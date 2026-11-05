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
        self.VERDE_ALTO = np.array ([90,255,255])
    
    def mask(self, raw_frame, min_green_pixels=700):
        # VideoCapture already returns BGR. Keep the camera frame's native size
        # so mask/contour coordinates match the image being annotated.
        conversion_a_HSV = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2HSV)
        GaussianBlur = cv2.GaussianBlur(conversion_a_HSV, (5, 5), 0)

        mask = cv2.inRange(GaussianBlur, self.VERDE_BAJO, self.VERDE_ALTO)

        bg_closed_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        bg_closed_mask = cv2.morphologyEx(bg_closed_mask, cv2.MORPH_CLOSE, self.kernel)

        # raw_frame is already the requested ROI, so an all-white mask would
        # leave the threshold image unchanged.
        search_mask = bg_closed_mask
        verde_pixeles = cv2.countNonZero(search_mask)
        contours, _ = cv2.findContours(search_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        altura, ancho, _ = raw_frame.shape[:3]
        centro_x = ancho // 2
        centro_y = (altura // 2) - 20
        cv2.circle(raw_frame, (centro_x, centro_y), 5, (255, 0, 0), -1)
        if len(contours) > 0 and verde_pixeles >= min_green_pixels:
            Largest_contour = max(contours, key=cv2.contourArea)
            rectangle = cv2.minAreaRect(Largest_contour)
            center, (rect_width, rect_height), rect_angle = rectangle
            # Convert OpenCV's rectangle angle into the detected shape's long
            # axis angle, then express its signed error from vertical. The line
            # is considered vertical at either -90 or +90 degrees.
            long_axis_angle = rect_angle
            if rect_height > rect_width:
                long_axis_angle += 90
            long_axis_angle = (long_axis_angle + 90) % 180 - 90
            if long_axis_angle >= 0:
                vertical_error = long_axis_angle - 90
            else:
                vertical_error = long_axis_angle + 90
            cv2.drawContours(raw_frame, [Largest_contour], -1, (0, 255, 0), 2)
            line_width = min(rect_width, rect_height)
            cv2.circle(raw_frame, (int(center[0]), int(center[1])), 5, (0, 0, 255), -1)
            return centro_x, centro_y, center, search_mask, line_width, verde_pixeles, vertical_error
        else:
            center = None
            line_width = None
            vertical_error = None
        return centro_x, centro_y, center, search_mask, line_width, verde_pixeles, vertical_error

    
def button_clicked(instance):
    cap.release()
    cv2.destroyAllWindows()
    sys.exit()

def binding(ui):
    ui['page_0']['Button_2'].on_click = button_clicked

    ui['page_0']["TextInput_5"].text


def UIimage(ui, frame, mask):

    ui['page_0']['OpencvImage_11'].image = frame
    ui['page_0']['OpencvImage_10'].image = mask

def update_camera():
    ret, frame = cap.read()

    if not ret:
        return

    c_x, c_y, c_general, mascara, width, _, _ = coneccion.mask(frame)

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



