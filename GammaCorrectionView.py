from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QComboBox, QLineEdit, QVBoxLayout, QPushButton, QGraphicsScene
from imageclasses import *


class GammaCorrectionView(QWidget):

    def __init__(self):
        super().__init__()
        self.current_pixels = []
        self.rgb_image = None
        self.scene = None
        self.graphics_view = None
        self.window = QWidget()
        self.gamma_options_combo_box = QComboBox()
        self.gamma_line_edit = QLineEdit()
        self.changed = False

    def set_window(self):
        self.window.setWindowTitle('Gamma Correction')
        self.window.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout(self.window)

        self.gamma_options_combo_box.addItems(["Convert Gamma", "Assign Gamma"])

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(
            lambda: self.apply_gamma_correction(self.gamma_options_combo_box.currentText(),
                                                self.gamma_line_edit.text()))

        layout.addWidget(self.gamma_options_combo_box)
        layout.addWidget(self.gamma_line_edit)
        layout.addWidget(apply_button)

    def show(self):
        self.window.show()

    def apply_gamma_correction(self, option, gamma):
        try:
            gamma_value = float(gamma)
            if option == 'Convert Gamma':
                self.convert_gamma(gamma_value)
            elif option == 'Assign Gamma':
                self.assign_gamma(gamma_value)
        except Exception as e:
            print(e)

    def assign_value(self, rgb_image, scene, graphics_view):
        self.rgb_image = rgb_image
        self.scene = scene
        self.graphics_view = graphics_view
        self.current_pixels = list(self.rgb_image.pixels[:])

    def show_image_with_current_gamma(self, pixels, gamma):
        new_pixels = list(map(int, self.apply_new_gamma(pixels, gamma)))
        pixmap = QPixmap.fromImage(QImage(bytes(new_pixels), self.rgb_image.width, self.rgb_image.height,
                                          QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def get_current_pixels_rgb_image(self):
        return RGBImage(self.width(), self.height(), list(map(int, self.current_pixels)))

    def assign_gamma(self, gamma):
        if gamma < 0:
            print("Gamma value must be positive!")
            return
        self.show_image_with_current_gamma(self.current_pixels, gamma)

    def convert_gamma(self, gamma):
        if gamma < 0:
            print("Gamma value must be positive!")
            return
        self.current_pixels = self.apply_new_gamma(self.current_pixels, gamma)
        if gamma == 0:
            cur_gamma = -1
        else:
            cur_gamma = 1 / gamma
        self.show_image_with_current_gamma(self.current_pixels, cur_gamma)
        self.changed = True

    def from_srgb_to_linear(self, pixels):
        pixels_copy = pixels.copy()
        for i in range(len(pixels_copy)):
            if pixels_copy[i] / 255 <= 0.04045:
                pixels_copy[i] = pixels_copy[i] / 12.92
            else:
                pixels_copy[i] = 255 * (((pixels_copy[i] / 255 + 0.055) / 1.055) ** 2.4)
        return pixels_copy

    def from_linear_to_srgb(self, pixels):
        pixels_copy = pixels.copy()
        for i in range(len(pixels_copy)):
            if pixels_copy[i] / 255 <= 0.0031308:
                pixels_copy[i] = pixels_copy[i] * 12.92
            else:
                pixels_copy[i] = 255 * (1.055 * ((pixels_copy[i] / 255) ** (1 / 2.4)) - 0.055)
        return pixels_copy

    def apply_new_gamma(self, pixels, gamma):
        if gamma == 0:
            return self.from_srgb_to_linear(pixels)
        elif gamma == -1:
            return self.from_linear_to_srgb(pixels)
        return self.change_gamma(pixels, gamma)

    def change_gamma(self, pixels, gamma):
        pixels_copy = pixels.copy()
        for i in range(len(pixels_copy)):
            pixels_copy[i] = 255 * ((pixels_copy[i] / 255) ** gamma)
        return pixels_copy

    def closeEvent(self, a0, event=None):
        super().closeEvent(event)

    def close_window(self):
        self.window.close()
