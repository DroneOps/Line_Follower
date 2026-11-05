import CVisionLines
from djitellopy import Tello
import cv2
from O_Algo import create_ui
import pyvisual as pv
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
ancho_linea = 10
LOOKAHEAD_YAW_STOP_PIXELS = 80

class dron:
    def __init__(self):
        self.tello = Tello()
        self.tello.connect()
        self.tello.streamon()
        print(f"conectado, 电池: {self.tello.get_battery()}%")
        self.computerVision = CVisionLines.Computer_Vision()

        self.integral_x = 0.0
        self.limite = 30.0

        self.velocidad = 18

        self.kpx = 0.65
        self.kix = 0.3
        self.dt = 0.1

        self.deadband_pixels = 4
        self.searching_for_line = False
        self.search_yaw = 0
        self.search_yaw_stopped = False
        self.deceleration_kp = 100.0
        self.approach_stop_latched = False
        self.gap_search_speed = 8

        self.seen_frame = self.tello.get_frame_read()

    def scale_signal(self, val):
        return max(-100, min(100, int(val)))

    def mirar(self):
        frame = self.seen_frame.frame
        if frame is None or frame.size == 0:
            return None
        vdd_frame = cv2.resize(frame, (480, 360))
        flip_frame = cv2.flip(vdd_frame, 0)
        vrai_frame = flip_frame[0:360, 90:390]
        half_frame = flip_frame[0:165, 140:340]
        lookahead_frame = half_frame[0:30, :]
        half_frame_area = half_frame.shape[0] * half_frame.shape[1]
        lookahead_area = lookahead_frame.shape[0] * lookahead_frame.shape[1]
        lookahead_min_green = max(1, round(700 * lookahead_area / half_frame_area))
        centro_x, centro_y, center, search_mask, width, _, _ = self.computerVision.mask(vrai_frame)
        _, _, half_center, half_mask = self.computerVision.mask(half_frame)
        _, _, _, lookahead_mask, _, lookahead_pixels, _ = self.computerVision.mask(
            lookahead_frame, min_green_pixels=lookahead_min_green
        )
        return (
            vrai_frame, centro_x, centro_y, center, width, search_mask,
            half_mask, half_center, lookahead_mask,
            lookahead_pixels, lookahead_min_green,
        )


    def controller(self, center, centro_x, width):
        if center is not None and width is not None and width > 0:
            error_x_pixels = center[0] - centro_x

            error_x = error_x_pixels * (ancho_linea / width)
            if abs(error_x_pixels) <= self.deadband_pixels:
                error_x = 0.0
                self.integral_x = 0.0

            self.integral_x += error_x * self.dt

            self.integral_x = max(min(self.integral_x, self.limite), - self.limite)
            
            raw_roll = int((self.kpx * error_x) + (self.kix * self.integral_x))

            true_roll = self.scale_signal(raw_roll)

            return true_roll, error_x
        else:
            return 0, 0
    def takeoff(self):
        self.tello.takeoff()

    def land(self):
        try:
            self.tello.send_rc_control(0, 0, 0, 0)
            self.tello.land()
        except Exception as e:
            print(f"no se pudo bajar ff gg papa :{e}")

    def controlador(self, lr_speed, fb_speed, ud_speed, yaw_speed):
        lr = max(-100, min(100, int(lr_speed)))
        fb = max(-100, min(100, int(fb_speed)))
        ud = max(-100, min(100, int(ud_speed)))
        yaw = max(-100, min(100, int(yaw_speed)))
        self.tello.send_rc_control(lr, fb, ud, yaw)



    def reset_search(self):
        self.searching_for_line = False
        self.search_yaw = 0
        self.search_yaw_stopped = False

    def update_approach_speed(self, lookahead_pixels, lookahead_min_green, half_frame_visible):
        if not half_frame_visible:
            self.approach_stop_latched = False
            return 0

        if self.approach_stop_latched:
            return 0

        coverage = max(0.0, min(1.0, lookahead_pixels / max(1, lookahead_min_green)))
        missing_fraction = 1.0 - coverage
        desired_speed = max(
            0.0,
            min(
                float(self.velocidad),
                float(self.velocidad) - max(0.0, self.deceleration_kp) * missing_fraction,
            ),
        )
        command = int(round(desired_speed))
        if command == 0:
            self.approach_stop_latched = True

        return command




def button_clicked(ui, obj, timer):
    timer.stop()
    try:
        obj.tello.send_rc_control(0, 0, 0, 0)
        obj.land()
    except Exception as e:
        print(f"no se pudo gg ff papa {e}")
    finally:
        try:
            obj.tello.end()
        except Exception as e:
            print(f"no se pudo cerrar el stream: {e}")
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
        half_masc, half_center, lookahead_mask,
        lookahead_pixels, lookahead_min_green,
    ) = result
    true_roll, err_x = obj.controller(center, centro_x, width)
    img = cv2.cvtColor(flip_frame, cv2.COLOR_RGB2BGR)
    cv2.putText(img, f"Error X: {err_x:.1f}", (8, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    display = cv2.cvtColor(mascara.copy(), cv2.COLOR_GRAY2BGR)
    x0 = 140 - 90
    x1 = 340 - 90
    y0, y1 = 0, 165

    cv2.rectangle(display, (x0, y0), (x1 - 1, y1 - 1), (0, 255, 255), 2)

    lookahead_height, lookahead_width = lookahead_mask.shape[:2]
    display[y0:y0 + lookahead_height, x0:x0 + lookahead_width] = cv2.cvtColor(
        lookahead_mask, cv2.COLOR_GRAY2BGR
    )
    cv2.rectangle(
        display,
        (x0, y0),
        (x0 + lookahead_width - 1, y0 + lookahead_height - 1),
        (255, 255, 0),
        2,
    )
    cv2.putText(
        display,
        f"LOOKAHEAD: {lookahead_pixels}",
        (x0 + 4, y0 + 14),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        (255, 255, 0),
        1,
    )

    x_first_divider = x0 + round((x1 - x0) / 3)
    x_second_divider = x0 + round(2 * (x1 - x0) / 3)
    cv2.line(display, (x_first_divider, y0), (x_first_divider, y1 - 1), (255, 0, 255), 1)
    cv2.line(display, (x_second_divider, y0), (x_second_divider, y1 - 1), (255, 0, 255), 1)

    y_mid = y0 + (y1 - y0) // 2
    cv2.line(display, (x0, y_mid), (x1 - 1, y_mid), (255, 0, 255), 1)
    UIimage(ui, img, display)

    forward_speed = obj.update_approach_speed(
        lookahead_pixels,
        lookahead_min_green,
        half_center is not None,
    )

    if obj.searching_for_line and obj.search_yaw != 0:
        if lookahead_pixels >= LOOKAHEAD_YAW_STOP_PIXELS:
            obj.search_yaw = 0
            obj.search_yaw_stopped = True
        else:
            obj.controlador(0, 0, 0, obj.search_yaw)
            return

    if obj.search_yaw_stopped:
        if half_center is not None:
            obj.reset_search()
            obj.approach_stop_latched = False
            obj.controlador(true_roll, obj.gap_search_speed, 0, 0)
        else:
            obj.controlador(0, 0, 0, 0)
        return

    if half_center is not None:
        obj.reset_search()
        obj.controlador(true_roll, forward_speed, 1, 0)
        return

    left_zone_end = x0 + round((x1 - x0) / 3)
    right_zone_start = x0 + round(2 * (x1 - x0) / 3)

    if not obj.searching_for_line:
        obj.searching_for_line = True
        obj.search_yaw = 0
        obj.search_yaw_stopped = False
        if center is not None:
            if center[0] < left_zone_end:
                obj.search_yaw = -20
            elif center[0] > right_zone_start:
                obj.search_yaw = 20

    if obj.search_yaw != 0:
        obj.controlador(0, 0, 0, obj.search_yaw)
    elif center is not None:
        obj.controlador(true_roll, obj.gap_search_speed, 0, 0)
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
