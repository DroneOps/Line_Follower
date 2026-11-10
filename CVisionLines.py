import numpy as np
import cv2
from O_Algo import create_ui
import pyvisual as pv
import sys
from PySide6.QtCore import QTimer


class Computer_Vision:
    def __init__(self):
        self.kernel = np.ones((5, 5), np.uint8)
        self.VERDE_BAJO = np.array([30, 50, 40])
        self.VERDE_ALTO = np.array([90, 255, 255])

    def mask(self, raw_frame, min_green_pixels=500):
        altura, ancho = raw_frame.shape[:2]
        centro_x = ancho // 2
        centro_y = (altura // 2) + 20  # Referencia en la mitad inferior (bajo el dron)

        conversion_a_HSV = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2HSV)
        blur = cv2.GaussianBlur(conversion_a_HSV, (5, 5), 0)
        raw_mask = cv2.inRange(blur, self.VERDE_BAJO, self.VERDE_ALTO)

        search_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, self.kernel)
        search_mask = cv2.morphologyEx(search_mask, cv2.MORPH_CLOSE, self.kernel)

        verde_pixeles = cv2.countNonZero(search_mask)
        cv2.circle(raw_frame, (centro_x, centro_y), 5, (255, 0, 0), -1)

        contours, _ = cv2.findContours(search_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0 and verde_pixeles >= min_green_pixels:
            largest_contour = max(contours, key=cv2.contourArea)
            cv2.drawContours(raw_frame, [largest_contour], -1, (0, 255, 0), 2)

            # Crear máscara exclusiva del contorno principal para evitar ruido externo
            clean_mask = np.zeros_like(search_mask)
            cv2.drawContours(clean_mask, [largest_contour], -1, 255, -1)

            # 1. Centro de seguimiento lateral (franja inferior/media: y de 150 a 340)
            y_low_start = max(0, centro_y - 50)
            y_low_end = min(altura, centro_y + 90)
            lower_slice = clean_mask[y_low_start:y_low_end, :]
            M_low = cv2.moments(lower_slice)

            if M_low["m00"] > 100:
                cx_low = float(M_low["m10"] / M_low["m00"])
                cy_low = float(M_low["m01"] / M_low["m00"]) + y_low_start
            else:
                M_all = cv2.moments(largest_contour)
                if M_all["m00"] > 0:
                    cx_low = float(M_all["m10"] / M_all["m00"])
                    cy_low = float(M_all["m01"] / M_all["m00"])
                else:
                    cx_low, cy_low = float(centro_x), float(centro_y)

            center = (cx_low, cy_low)

            # 2. Centro de la franja superior (y de 30 a 150) para medir hacia dónde dobla la línea
            upper_slice = clean_mask[30:y_low_start, :]
            M_up = cv2.moments(upper_slice)

            if M_up["m00"] > 100:
                cx_up = float(M_up["m10"] / M_up["m00"])
                cy_up = float(M_up["m01"] / M_up["m00"]) + 30
                dy = max(15.0, cy_low - cy_up)
                dx = cx_up - cx_low
                # Positivo = se inclina a la derecha; Negativo = se inclina a la izquierda
                vertical_error = float(np.degrees(np.arctan2(dx, dy)))
                cv2.line(raw_frame, (int(cx_low), int(cy_low)), (int(cx_up), int(cy_up)), (255, 255, 0), 2)
                cv2.circle(raw_frame, (int(cx_up), int(cy_up)), 4, (0, 255, 255), -1)
            else:
                vertical_error = 0.0

            cv2.circle(raw_frame, (int(center[0]), int(center[1])), 6, (0, 0, 255), -1)
            _, (rect_w, rect_h), _ = cv2.minAreaRect(largest_contour)
            line_width = min(rect_w, rect_h)

            return centro_x, centro_y, center, search_mask, line_width, verde_pixeles, vertical_error

        return centro_x, centro_y, None, search_mask, None, verde_pixeles, None


def button_clicked(instance):
    cap.release()
    cv2.destroyAllWindows()
    sys.exit()


def binding(ui):
    ui['page_0']['Button_2'].on_click = button_clicked


def UIimage(ui, frame, mask):
    ui['page_0']['OpencvImage_11'].image = frame
    ui['page_0']['OpencvImage_10'].image = mask


def update_camera():
    ret, frame = cap.read()
    if not ret:
        return
    _, _, _, mascara, _, _, _ = coneccion.mask(frame)
    if mascara is not None:
        UIimage(ui, frame, mascara)


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    coneccion = Computer_Vision()
    app = pv.PvApp()
    ui = create_ui(8)
    binding(ui)

    timer = QTimer()
    timer.timeout.connect(update_camera)
    timer.start(33)

    ui["window"].show()
    app.run()