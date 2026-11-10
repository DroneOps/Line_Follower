import time
import numpy as np
import cv2
from djitellopy import Tello
import CVisionLines
from O_Algo import create_ui
import pyvisual as pv
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

# Umbrales calibrados para ventana lookahead de 85x110 px
LOOKAHEAD_START_TURN_PIXELS = 220   # Si baja de esto, inicia maniobra de esquina
LOOKAHEAD_STOP_TURN_PIXELS = 320    # Píxeles necesarios en el frente para confirmar los 90°
MIN_TURN_DURATION = 0.45            # Segundos mínimos girando para no re-enganchar la línea vieja
MAX_TURN_DURATION = 2.40            # Tiempo máximo de seguridad para evitar giros de 180°


class dron:
    def __init__(self):
        self.tello = Tello()
        self.tello.connect()
        self.tello.streamon()
        print(f"Conectado, Batería: {self.tello.get_battery()}%")
        self.computerVision = CVisionLines.Computer_Vision()

        # Ganancias suaves para evitar sobreimpulso lateral
        self.kpx = 0.33
        self.kix = 0.20
        self.kdx = 0.30

        self.kp_yaw = 0.70
        self.kd_yaw = 0.10

        self.integral_x = 0.0
        self.prev_err_x = 0.0
        self.prev_err_yaw = 0.0
        self.last_time = time.time()
        self.limite = 20.0

        # Velocidad crucero reducida para dar tiempo de reacción en curvas
        self.velocidad = 40
        self.min_velocidad = 8
        self.deadband_pixels = 6
        self.deadband_angle = 4.0

        # Máquina de estados para curvas
        self.searching_for_line = False
        self.search_yaw = 0
        self.turn_Yaw_speed = 32
        self.last_turn_hint = 0      # -1: Izquierda, +1: Derecha
        self.brake_frames = 0        # Contador para pulso de frenado inverso
        self.turn_start_time = 0.0

        self.seen_frame = self.tello.get_frame_read()

    def scale_signal(self, val, min_power=8, max_power=35):
        if val == 0:
            return 0
        sign = 1 if val > 0 else -1
        magnitude = abs(val)
        if magnitude < min_power:
            return sign * min_power
        return sign * min(max_power, magnitude)

    def mirar(self):
        frame = self.seen_frame.frame
        if frame is None or frame.size == 0:
            return None

        vdd_frame = cv2.resize(frame, (480, 360))
        flip_frame = cv2.flip(vdd_frame, 0)

        # Recorte maestro de 300x360
        vrai_frame = flip_frame[0:360, 90:390]
        centro_x, centro_y, center, search_mask, width, _, vertical_error = self.computerVision.mask(vrai_frame)

        # Mitad superior (0:185) y ventana Lookahead frontal (0:85, 95:205 -> 85x110 px)
        half_mask = search_mask[0:185, :]
        lookahead_mask = search_mask[0:85, 95:205]
        lookahead_pixels = cv2.countNonZero(lookahead_mask)
        lookahead_min_green = 1100

        # Detectar hacia qué lado se carga la línea en la mitad superior (para anticipar la esquina)
        left_half_pixels = cv2.countNonZero(half_mask[:, 0:135])
        right_half_pixels = cv2.countNonZero(half_mask[:, 165:300])

        if left_half_pixels > right_half_pixels + 250 or (vertical_error is not None and vertical_error < -14):
            self.last_turn_hint = -1
        elif right_half_pixels > left_half_pixels + 250 or (vertical_error is not None and vertical_error > 14):
            self.last_turn_hint = 1

        M_half = cv2.moments(half_mask)
        if M_half["m00"] > 250:
            half_center = (M_half["m10"] / M_half["m00"], M_half["m01"] / M_half["m00"])
        else:
            half_center = None

        return (
            flip_frame, centro_x, centro_y, center, width, search_mask,
            half_mask, half_center, vertical_error, lookahead_mask,
            lookahead_pixels, lookahead_min_green, left_half_pixels, right_half_pixels
        )

    def controller(self, center, centro_x, vertical_error=0.0):
        now = time.time()
        dt = max(0.01, min(0.1, now - self.last_time))
        self.last_time = now

        if center is not None:
            error_x = float(center[0] - centro_x)

            if abs(error_x) <= self.deadband_pixels:
                error_x = 0.0
                self.integral_x = 0.0

            self.integral_x = float(np.clip(self.integral_x + error_x * dt, -self.limite, self.limite))
            deriv_x = (error_x - self.prev_err_x) / dt
            self.prev_err_x = error_x

            raw_roll = int((self.kpx * error_x) + (self.kix * self.integral_x) + (self.kdx * deriv_x))
            true_roll = self.scale_signal(raw_roll, min_power=7, max_power=25)

            true_yaw = 0
            if vertical_error is not None and abs(vertical_error) > self.deadband_angle:
                deriv_yaw = (vertical_error - self.prev_err_yaw) / dt
                self.prev_err_yaw = vertical_error
                raw_yaw = int((self.kp_yaw * vertical_error) + (self.kd_yaw * deriv_yaw))
                true_yaw = self.scale_signal(raw_yaw, min_power=6, max_power=25)
            else:
                self.prev_err_yaw = 0.0

            return true_roll, true_yaw, error_x

        self.prev_err_x = 0.0
        self.prev_err_yaw = 0.0
        return 0, 0, 0.0

    def takeoff(self):
        self.tello.takeoff()

    def land(self):
        try:
            self.tello.send_rc_control(0, 0, 0, 0)
            self.tello.land()
        except Exception as e:
            print(f"Error al aterrizar: {e}")

    def controlador(self, lr_speed, fb_speed, ud_speed, yaw_speed):
        lr = max(-100, min(100, int(lr_speed)))
        fb = max(-100, min(100, int(fb_speed)))
        ud = max(-100, min(100, int(ud_speed)))
        yaw = max(-100, min(100, int(yaw_speed)))
        self.tello.send_rc_control(lr, fb, ud, yaw)

    def reset_search(self):
        self.searching_for_line = False
        self.search_yaw = 0
        self.brake_frames = 0
        self.integral_x = 0.0
        self.prev_err_x = 0.0
        self.prev_err_yaw = 0.0

    def update_approach_speed(self, lookahead_pixels, lookahead_min_green, err_x):
        if lookahead_pixels < LOOKAHEAD_START_TURN_PIXELS:
            return 0
        coverage = max(0.0, min(1.0, lookahead_pixels / max(1, lookahead_min_green)))
        speed = self.min_velocidad + (self.velocidad - self.min_velocidad) * coverage
        # Reducir velocidad de avance si el dron está muy descentrado lateralmente
        if abs(err_x) > 35:
            speed = min(speed, float(self.min_velocidad))
        return int(round(speed))


def button_clicked(ui, obj, timer):
    timer.stop()
    try:
        obj.tello.send_rc_control(0, 0, 0, 0)
        obj.land()
    except Exception as e:
        print(f"Error al detener: {e}")
    finally:
        try:
            obj.tello.end()
        except Exception as e:
            print(f"Error al cerrar stream: {e}")
        ui["window"].close()
        app = QApplication.instance()
        if app is not None:
            app.quit()


def binding(timer, ui, obj):
    ui['page_0']['Button_2'].on_click = lambda *args: button_clicked(ui, obj, timer)


def UIimage(ui, frame, masc):
    ui['page_0']['OpencvImage_11'].image = masc
    ui['page_0']['OpencvImage_10'].image = frame


def update_camera(obj):
    result = obj.mirar()
    if result is None:
        return

    (
        flip_frame, centro_x, centro_y, center, width, mascara,
        half_masc, half_center, vertical_error, lookahead_mask,
        lookahead_pixels, lookahead_min_green, left_px, right_px
    ) = result

    true_roll, true_yaw, err_x = obj.controller(center, centro_x, vertical_error)

    # Renderizado de HUD
    img = cv2.cvtColor(flip_frame, cv2.COLOR_RGB2BGR)
    dir_txt = "IZQ" if obj.last_turn_hint < 0 else ("DER" if obj.last_turn_hint > 0 else "RECTO")
    cv2.putText(img, f"ErrX:{err_x:.0f} | Curva:{dir_txt}", (8, 122),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    display = cv2.cvtColor(mascara.copy(), cv2.COLOR_GRAY2BGR)
    cv2.rectangle(display, (50, 0), (249, 184), (0, 255, 255), 2)
    cv2.rectangle(display, (95, 0), (204, 84), (255, 255, 0), 2)
    cv2.putText(display, f"LOOK: {lookahead_pixels}", (98, 16),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 0), 1)
    cv2.line(display, (135, 0), (135, 184), (255, 0, 255), 1)
    cv2.line(display, (165, 0), (165, 184), (255, 0, 255), 1)

    UIimage(ui, img, display)

    # 1. DETECCIÓN DE ENTRADA A ESQUINA (Se acaba la línea en la ventana frontal)
    if not obj.searching_for_line and lookahead_pixels < LOOKAHEAD_START_TURN_PIXELS and center is not None:
        # Decidir sentido de giro usando los píxeles de los flancos o la memoria inmediata
        if left_px > right_px + 120:
            turn_dir = -1
        elif right_px > left_px + 120:
            turn_dir = 1
        elif obj.last_turn_hint != 0:
            turn_dir = obj.last_turn_hint
        else:
            turn_dir = -1 if center[0] < centro_x else 1

        obj.searching_for_line = True
        obj.search_yaw = turn_dir * obj.turn_Yaw_speed
        obj.brake_frames = 5  # ~0.16s de pulso inverso para frenar la inercia
        obj.turn_start_time = time.time()

    # 2. EJECUCIÓN DE LA VUELTA EN ESQUINA
    if obj.searching_for_line:
        # Paso A: Pulso corto de frenado en seco para no pasarse del vértice
        if obj.brake_frames > 0:
            obj.brake_frames -= 1
            obj.controlador(0, -12, 0, 0)
            return

        elapsed_turn = time.time() - obj.turn_start_time

        # Paso B: Después del tiempo mínimo de despeje (0.45s), buscar la nueva línea a 90°
        line_centered_ahead = (
            half_center is not None and 95 <= half_center[0] <= 205
        )
        if elapsed_turn >= MIN_TURN_DURATION:
            if (lookahead_pixels >= LOOKAHEAD_STOP_TURN_PIXELS and line_centered_ahead) or elapsed_turn > MAX_TURN_DURATION:
                obj.reset_search()
                obj.controlador(0, 0, 0, 0)
                return

        # Mantener giro puro sobre el eje sin retroceder
        obj.controlador(0, 0, 0, obj.search_yaw)
        return

    # 3. SEGUIMIENTO NORMAL EN RECTA / CURVA SUAVE
    forward_speed = obj.update_approach_speed(lookahead_pixels, lookahead_min_green, err_x)

    if center is not None:
        obj.controlador(true_roll, forward_speed, 0, true_yaw)
    else:
        obj.controlador(0, 0, 0, 0)


if __name__ == "__main__":
    nose = dron()
    nose.takeoff()
    app = pv.PvApp()
    ui = create_ui(nose.tello.get_battery())

    timer = QTimer()
    timer.timeout.connect(lambda: update_camera(nose))
    timer.start(33)
    binding(timer, ui, nose)

    ui["window"].show()
    app.run()