import typing

from IPython.external.qt_for_kernel import QtGui
from PyQt6.QtWidgets import QGraphicsView, QLabel, QGraphicsEllipseItem, QGraphicsPixmapItem, QHBoxLayout
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QComboBox, QLineEdit, QVBoxLayout, QPushButton, QGraphicsScene

from GammaCorrectionView import GammaCorrectionView
from math import tan, sqrt, ceil
import math
import numpy as np

from conversions import hsv_to_rgb


class MyGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)


class MyGraphicsScene(QGraphicsScene):

    def __init__(self):
        super().__init__()
        self.line_drawing_view = None

    def mousePressEvent(self, event):
        if self.line_drawing_view is None:
            return
        if self.line_drawing_view.clicking_enabled:
            pos = event.scenePos()
            self.line_drawing_view.init_point(pos)
            print(f"X: {pos.x()}, Y: {pos.y()}")
            # ellipse = QGraphicsEllipseItem(pos.x() - 5, pos.y() - 5, 100, 100)
            # ellipse.setBrush(Qt.GlobalColor.red)
            # self.addItem(ellipse)

    def set_line_drawing_view(self, line_drawing_view):
        self.line_drawing_view = line_drawing_view

    def addPixmap(self, pixmap: QtGui.QPixmap) -> typing.Optional[QGraphicsPixmapItem]:
        return super().addPixmap(pixmap)


class Line:
    def __init__(self, x1=None, x2=None, y1=None, y2=None):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2


def get_pixel_brightness(pixel):
    return 0.3 * pixel[0] + 0.59 * pixel[1] + 0.11 * pixel[2]


class LineDrawingView(QWidget):

    def __init__(self):
        super().__init__()
        self.current_pixels = []
        self.rgb_image = None
        self.scene = None
        self.graphics_view = None
        self.window = QWidget()
        self.color = None
        self.thickness = None
        self.transparency = None
        self.clicking_enabled = False
        self.lines = []
        self.current_point = 1
        self.current_line = Line()
        self.buttons = []
        self.gamma_correction_view = None
        self.changed = False

    def set_window(self):
        self.window.setWindowTitle('Line Setting')
        self.window.setGeometry(100, 100, 300, 200)

        thickness_line_edit = QLineEdit()
        transparency_line_edit = QLineEdit()

        layout = QVBoxLayout(self.window)
        rgb_components_names_horizontal_layout = QHBoxLayout()
        rgb_components_horizontal_layout = QHBoxLayout()

        r_component_label = QLabel("R")
        g_component_label = QLabel("G")
        b_component_label = QLabel("B")

        rgb_components_names_horizontal_layout.addWidget(r_component_label)
        rgb_components_names_horizontal_layout.addWidget(g_component_label)
        rgb_components_names_horizontal_layout.addWidget(b_component_label)

        r_component = QLineEdit()
        g_component = QLineEdit()
        b_component = QLineEdit()

        rgb_components_horizontal_layout.addWidget(r_component)
        rgb_components_horizontal_layout.addWidget(g_component)
        rgb_components_horizontal_layout.addWidget(b_component)

        apply_button = QPushButton('Apply')
        start_drawing_button = QPushButton('Start drawing')
        end_drawing_button = QPushButton('End drawing')
        apply_button.clicked.connect(
            lambda: self.apply_line_characteristics(r_component.text(),
                                                    g_component.text(),
                                                    b_component.text(),
                                                    thickness_line_edit.text(),
                                                    transparency_line_edit.text()))
        start_drawing_button.clicked.connect(self.start_drawing)
        end_drawing_button.clicked.connect(self.end_drawing)

        transparency_label = QLabel("Transparency")
        layout.addWidget(transparency_label)
        layout.addWidget(transparency_line_edit)
        thickness_label = QLabel("Thickness")
        layout.addWidget(thickness_label)
        layout.addWidget(thickness_line_edit)
        layout.addLayout(rgb_components_names_horizontal_layout)
        layout.addLayout(rgb_components_horizontal_layout)
        layout.addWidget(apply_button)
        layout.addWidget(start_drawing_button)
        layout.addWidget(end_drawing_button)

    def show(self):
        self.window.show()

    def apply_line_characteristics(self, r, g, b, thickness, transparency):
        if not self.check_parameters:
            print("Invalid parameters format!")
            return
        self.color = (int(r), int(g), int(b))
        self.thickness = int(thickness)
        self.transparency = float(transparency)

    def check_parameters(self, r, g, b, thickness, transparency):
        parameters = (r, g, b, thickness, transparency)
        if any(math.isnan(x) for x in parameters):
            return False
        return 0 <= g <= 255 and 0 <= r <= 255 and 0 <= b <= 255 and thickness > 0 and 0 <= transparency <= 1

    def start_drawing(self):
        self.clicking_enabled = True
        for button in self.buttons:
            if button.objectName() != 'Draw Line':
                button.setEnabled(False)

    def end_drawing(self):
        self.clicking_enabled = False
        for button in self.buttons:
            if button.objectName() == 'Gamma Correction' and type(self.image).__name__ == "GrayImage":
                continue
            button.setEnabled(True)

    def assign_value(self, rgb_image, scene, graphics_view, buttons,
                               gamma_correction_view: GammaCorrectionView):
        self.rgb_image = rgb_image
        self.scene = scene
        self.graphics_view = graphics_view
        self.current_pixels = []
        self.buttons = buttons
        self.color = None
        self.thickness = None
        self.transparency = None
        self.clicking_enabled = False
        self.lines = []
        self.current_point = 1
        self.current_line = Line()
        self.gamma_correction_view = gamma_correction_view

    def draw_line(self):
        if self.rgb_image is None:
            return
        if self.gamma_correction_view.changed:
            self.current_pixels = list(self.gamma_correction_view.get_current_pixels_rgb_image().pixels[:])
            self.gamma_correction_view.changed = False
        elif len(self.current_pixels) == 0:
            if len(self.gamma_correction_view.current_pixels) != 0:
                self.current_pixels = list(self.gamma_correction_view.get_current_pixels_rgb_image().pixels[:])
            else:
                self.current_pixels = list(self.rgb_image.pixels)
        self.changed = True
        start_point = (self.current_line.x1, self.current_line.y1)
        end_point = (self.current_line.x2, self.current_line.y2)

        self.draw_line_algorithm(start_point, end_point)
        pixmap = QPixmap.fromImage(
            QImage(bytes(list(map(int, self.current_pixels))), self.rgb_image.width, self.rgb_image.height,
                   QImage.Format.Format_RGB888))

        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def get_points_offsets(self, point, k, x_offset, y_offset):
        if k < 0:
            start_offset_points = (point[0] - x_offset, point[1] - y_offset,
                                   point[0] + x_offset, point[1] + y_offset)
        else:
            start_offset_points = (point[0] + x_offset, point[1] - y_offset,
                                   point[0] - x_offset, point[1] + y_offset)
        return start_offset_points

    def clear_lines(self):
        self.lines = []

    def clear_last_line(self):
        if self.current_point == 2:
            self.current_point = 1
            self.current_line = Line()
        else:
            if len(self.lines) != 0:
                self.lines.pop()

    def check_coordinates(self, x, y):
        return self.rgb_image.width >= x >= 0 and self.rgb_image.height >= y >= 0

    def get_pixel_index_by_coordinates(self, x, y):
        if not self.check_coordinates(x, y):
            return

        # print(f'x = {x}')
        # print(f'y = {y}')

        width = self.rgb_image.width
        y = ceil(y) - 1
        x = ceil(x) - 1

        byte_offset = (y * width * 3) + (x * 3)

        return byte_offset

    def get_transparency(self, pixel):
        avg_val = ((pixel[0] + pixel[1] + pixel[2]) / 255) / 3
        return avg_val

    def get_length(self, a, b):
        return sqrt(a ** 2 + b ** 2)

    def define_new_brightness(self, brightness):
        new_r = self.color[0] * brightness / 255
        new_g = self.color[1] * brightness / 255
        new_b = self.color[2] * brightness / 255
        new_r = new_r if 0 <= new_r <= 255 else (0 if new_r < 0 else 255)
        new_g = new_g if 0 <= new_g <= 255 else (0 if new_g < 0 else 255)
        new_b = new_b if 0 <= new_b <= 255 else (0 if new_b < 0 else 255)
        return new_r, new_g, new_b

    def plot_pixel(self, x, y, c=float('nan')):
        pixel_index = self.get_pixel_index_by_coordinates(x, y)
        rgb = [self.color[0], self.color[1], self.color[2]]
        if not np.isnan(c):
            brightness = c * 255
            rgb = self.define_new_brightness(brightness)
        new_color_alpha = self.transparency
        current_pixel_alpha = self.get_transparency((self.current_pixels[pixel_index],
                                                     self.current_pixels[pixel_index + 1],
                                                     self.current_pixels[pixel_index + 2]))
        result_transparency = new_color_alpha + current_pixel_alpha * (1 - new_color_alpha)
        new_r = (rgb[0] * new_color_alpha + self.current_pixels[pixel_index] * current_pixel_alpha * (
                1 - new_color_alpha)) / result_transparency
        new_g = (rgb[1] * new_color_alpha + self.current_pixels[pixel_index + 1] * current_pixel_alpha * (
                1 - new_color_alpha)) / result_transparency
        new_b = (rgb[2] * new_color_alpha + self.current_pixels[pixel_index + 2] * current_pixel_alpha * (
                1 - new_color_alpha)) / result_transparency

        self.current_pixels[pixel_index] = new_r
        self.current_pixels[pixel_index + 1] = new_g
        self.current_pixels[pixel_index + 2] = new_b

    def draw_line_algorithm(self, start_point, end_point):
        x0 = start_point[0]
        y0 = start_point[1]
        x1 = end_point[0]
        y1 = end_point[1]
        thickness = self.thickness // 2

        if int(x0) == int(x1):
            self.draw_vertical_line(start_point, end_point)
            return
        if int(y0) == int(y1):
            self.draw_horizontal_line(start_point, end_point)
            return

        tan = -(y1 - y0) / (x1 - x0)
        x = thickness / math.sqrt(1 + (1 / tan) ** 2)
        y = abs(x / tan)

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        start_p1 = ()
        start_p2 = ()
        if tan > 0:
            start_p1 = (int(x0 - x), int(y0 - y))
            start_p2 = (int(x0 + x), int(y0 + y))
        elif tan < 0:
            start_p1 = (int(x0 + x), int(y0 - y))
            start_p2 = (int(x0 - x), int(y0 + y))
        end_p1 = (start_p1[0] + int(x1 - x0), start_p1[1] + int(y1 - y0))
        end_p2 = (start_p2[0] + int(x1 - x0), start_p2[1] + int(y1 - y0))
        self.draw_line_by_fulfilling(start_p1, end_p1, end_p2, start_p2)

    def draw_line_by_fulfilling(self, p1, p2, p3, p4):

        used_pixels = set()
        used_pixels = self.draw_line_between_pixels_wu_algorithm(p1[0], p1[1], p2[0], p2[1], used_pixels)
        used_pixels = self.draw_line_between_pixels_wu_algorithm(p2[0], p2[1], p3[0], p3[1], used_pixels)
        used_pixels = self.draw_line_between_pixels_wu_algorithm(p3[0], p3[1], p4[0], p4[1], used_pixels)
        used_pixels = self.draw_line_between_pixels_wu_algorithm(p4[0], p4[1], p1[0], p1[1], used_pixels)
        tan1 = (p2[1] - p1[1]) / (p2[0] - p1[0])
        tan2 = (p3[1] - p2[1]) / (p3[0] - p2[0])
        tan3 = (p4[1] - p3[1]) / (p4[0] - p3[0])
        tan4 = (p1[1] - p4[1]) / (p1[0] - p4[0])
        coef1 = p1[1] - p1[0] * tan1
        coef2 = p2[1] - p2[0] * tan2
        coef3 = p3[1] - p3[0] * tan3
        coef4 = p4[1] - p4[0] * tan4

        for y in range(min(int(p1[1]), int(p2[1]), int(p3[1]), int(p4[1])),
                       max(int(p1[1]), int(p2[1]), int(p3[1]), int(p4[1])) + 1):
            x = min(int(p1[0]), int(p2[0]), int(p3[0]), int(p4[0]))
            while x <= max(int(p1[0]), int(p2[0]), int(p3[0]), int(p4[0])):
                ind = self.get_pixel_index_by_coordinates(x, y)
                if (
                        (tan1 < 0 and int(tan1 * x + coef1) <= y < int(tan3 * x + coef3) and
                         int(tan2 * x + coef2) < y <= math.ceil(tan4 * x + coef4)) or
                        (tan1 > 0 and int(tan1 * x + coef1) < y <= int(tan3 * x + coef3) and
                         int(tan4 * x + coef4) < y <= math.ceil(tan2 * x + coef2))
                ) and ind not in used_pixels and self.check_coordinates(x, y):
                    used_pixels.add(ind)
                    self.plot_pixel(x, y)
                x += 1
            if y == int(p1[1]) or y == int(p2[1]) or y == int(p3[1]) or y == int(p4[1]):
                continue
            x = max(int(p1[0]), int(p2[0]), int(p3[0]), int(p4[0])) + 1
            while x <= min(int(p1[0]), int(p2[0]), int(p3[0]), int(p4[0])):
                ind = self.get_pixel_index_by_coordinates(x, y)
                if (
                        (tan1 < 0 and int(tan1 * x + coef1) <= y < int(tan3 * x + coef3) and
                         int(tan2 * x + coef2) < y <= math.ceil(tan4 * x + coef4)) or
                        (tan1 > 0 and int(tan1 * x + coef1) < y <= int(tan3 * x + coef3) and
                         int(tan4 * x + coef4) < y <= math.ceil(tan2 * x + coef2))
                ) and ind not in used_pixels and self.check_coordinates(x, y):
                    used_pixels.add(ind)
                    self.plot_pixel(x, y)
                x += 1

    def draw_horizontal_line(self, start_point, end_point):
        x0 = int(start_point[0])
        y0 = int(start_point[1])
        x1 = int(end_point[0])
        if x0 > x1:
            x0, x1 = x1, x0
        thickness = self.thickness // 2
        while x0 != x1:
            for i in range(-thickness, thickness + 1):
                if self.check_coordinates(x0, y0 + i):
                    self.plot_pixel(x0, y0 + i)
            x0 += 1

    def draw_vertical_line(self, start_point, end_point):
        x0 = int(start_point[0])
        y0 = int(start_point[1])
        y1 = int(end_point[1])
        if y0 > y1:
            y0, y1 = y1, y0
        thickness = self.thickness // 2
        while y0 != y1:
            for i in range(-thickness, thickness + 1):
                if self.check_coordinates(x0 + i, y0 + i):
                    self.plot_pixel(x0 + i, y0)
            y0 += 1

    def change_coordinates(self, x0, y0, x1, y1):
        tan = (y1 - y0) / (x1 - x0)
        coef = y0 - tan * x0
        if x0 < 0:
            x0 = 0
            y0 = coef
        elif x0 > self.rgb_image.width:
            x0 = self.rgb_image.width
            y0 = tan * x0 + coef
        if y0 < 0:
            y0 = 0
            x0 = - coef / tan
        elif y0 > self.rgb_image.height:
            y0 = self.rgb_image.height
            x0 = (y0 - coef) / tan
        if x1 < 0:
            x1 = 0
            y1 = coef
        elif x1 > self.rgb_image.width:
            x1 = self.rgb_image.width
            y1 = tan * x1 + coef
        if y1 < 0:
            y1 = 0
            x1 = - coef / tan
        elif y1 > self.rgb_image.height:
            y1 = self.rgb_image.height
            x1 = (y1 - coef) / tan
        return int(x0), int(y0), int(x1), int(y1)

    def draw_line_between_pixels_wu_algorithm(self, x0, y0, x1, y1, used_pixels):
        x0, y0, x1, y1 = self.change_coordinates(x0, y0, x1, y1)
        steep = (abs(y1 - y0) > abs(x1 - x0))
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1, = y1, y0

        dx = x1 - x0
        dy = y1 - y0

        if int(dx) == 0:
            gradient = 1
        else:
            gradient = dy / dx

        x_end = int(x0 + 0.5)
        y_end = y0 + gradient * (x_end - x0)
        x_gap = 1 - (x0 + 0.5 - int(x0 + 0.5))
        x_pxl1 = x_end
        y_pxl1 = int(y_end)
        if steep:
            ind1 = self.get_pixel_index_by_coordinates(y_pxl1, x_pxl1)
            ind2 = self.get_pixel_index_by_coordinates(y_pxl1 + 1, x_pxl1)
            if self.check_coordinates(y_pxl1, x_pxl1) and ind1 not in used_pixels:
                self.plot_pixel(y_pxl1, x_pxl1, (1 - (y_end - int(y_end))) * x_gap)
                used_pixels.add((y_pxl1, x_pxl1))
            if self.check_coordinates(y_pxl1 + 1, x_pxl1) and ind2 not in used_pixels:
                self.plot_pixel(y_pxl1 + 1, x_pxl1, (y_end - int(y_end)) * x_gap)
                used_pixels.add((y_pxl1 + 1, x_pxl1))
        else:
            ind1 = self.get_pixel_index_by_coordinates(x_pxl1, y_pxl1)
            ind2 = self.get_pixel_index_by_coordinates(x_pxl1, y_pxl1 + 1)
            if self.check_coordinates(x_pxl1, y_pxl1) and ind1 not in used_pixels:
                self.plot_pixel(x_pxl1, y_pxl1, (1 - (y_end - int(y_end))) * x_gap)
                used_pixels.add((x_pxl1, y_pxl1))
            if self.check_coordinates(x_pxl1, y_pxl1 + 1) and ind2 not in used_pixels:
                self.plot_pixel(x_pxl1, y_pxl1 + 1, (y_end - int(y_end)) * x_gap)
                used_pixels.add((x_pxl1, y_pxl1 + 1))

        intery = y_end + gradient
        x_end = int(x1 + 0.5)
        y_end = y1 + gradient * (x_end - x1)
        x_gap = (x1 + 0.5 - int(x1 + 0.5))
        x_pxl2 = x_end
        y_pxl2 = int(y_end)
        if steep:
            ind1 = self.get_pixel_index_by_coordinates(y_pxl2, x_pxl2)
            ind2 = self.get_pixel_index_by_coordinates(y_pxl2 + 1, x_pxl2)
            if self.check_coordinates(y_pxl2, x_pxl2) and ind1 not in used_pixels:
                self.plot_pixel(y_pxl2, x_pxl2, (1 - (y_end - int(y_end))) * x_gap)
                used_pixels.add((y_pxl2, x_pxl2))
            if self.check_coordinates(y_pxl2 + 1, x_pxl2) and ind2 not in used_pixels:
                self.plot_pixel(y_pxl2 + 1, x_pxl2, (y_end - int(y_end)) * x_gap)
                used_pixels.add((y_pxl2 + 1, x_pxl2))
        else:
            ind1 = self.get_pixel_index_by_coordinates(x_pxl2, y_pxl2)
            ind2 = self.get_pixel_index_by_coordinates(x_pxl2, y_pxl2 + 1)
            if self.check_coordinates(x_pxl2, y_pxl2) and ind1 not in used_pixels:
                self.plot_pixel(x_pxl2, y_pxl2, (1 - (y_end - int(y_end))) * x_gap)
                used_pixels.add((x_pxl2, y_pxl2))
            if self.check_coordinates(x_pxl2, y_pxl2 + 1) and ind2 not in used_pixels:
                self.plot_pixel(x_pxl2, y_pxl2 + 1, (y_end - int(y_end)) * x_gap)
                used_pixels.add((x_pxl2, y_pxl2 + 1))

        for x in range(x_pxl1 - 1, x_pxl2 + 1):
            if self.check_coordinates(x, intery):
                if steep:
                    ind1 = self.get_pixel_index_by_coordinates(intery, x)
                    ind2 = self.get_pixel_index_by_coordinates(intery + 1, x)
                    if self.check_coordinates(intery, x) and ind1 not in used_pixels:
                        self.plot_pixel(intery, x, 1 - (intery - int(intery)))
                        used_pixels.add((intery, x))
                    if self.check_coordinates(intery + 1, x) and ind2 not in used_pixels:
                        self.plot_pixel(intery + 1, x, (intery - int(intery)))
                        used_pixels.add((intery + 1, x))
                else:
                    ind1 = self.get_pixel_index_by_coordinates(x, intery)
                    ind2 = self.get_pixel_index_by_coordinates(x, intery + 1)
                    if self.check_coordinates(x, intery) and ind1 not in used_pixels:
                        self.plot_pixel(x, intery, 1 - (intery - int(intery)))
                        used_pixels.add((x, intery))
                    if self.check_coordinates(x, intery + 1) and ind2 not in used_pixels:
                        self.plot_pixel(x, intery + 1, (intery - int(intery)))
                        used_pixels.add((x, intery + 1))
                intery = intery + gradient
        return used_pixels

    def init_point(self, pos):
        if self.current_point == 1:
            self.current_line.x1 = pos.x()
            self.current_line.y1 = pos.y()
            self.current_point += 1
        else:
            self.current_line.x2 = pos.x()
            self.current_line.y2 = pos.y()
            self.draw_line()
            self.lines.append(self.current_line)
            self.current_line = Line()
            self.current_point = 1

    def closeEvent(self, a0, event=None):
        super().closeEvent(event)

    def close_window(self):
        self.window.close()
