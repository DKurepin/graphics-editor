from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QComboBox, QLineEdit, QVBoxLayout, QPushButton, QGraphicsScene

import dithering
from imageclasses import RGBImage


class DitheringView(QWidget):

    def __init__(self):
        super().__init__()
        self.current_pixels = []
        self.rgb_image = None
        self.scene = None
        self.graphics_view = None
        self.changed = False
        self.window = QWidget()
        self.dithering_options_combo_box = QComboBox()
        self.bitness_line_edit = QLineEdit()
        self.gamma_correction_view = None

    def set_window(self):
        self.window.setWindowTitle('Dithering')
        self.window.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout(self.window)

        self.dithering_options_combo_box.addItems(["Floyd-Steinberg", "Atkinson", "Ordered", "Random"])

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(
            lambda: self.apply_dithering(self.dithering_options_combo_box.currentText(), self.bitness_line_edit.text()))

        layout.addWidget(self.dithering_options_combo_box)
        layout.addWidget(self.bitness_line_edit)
        layout.addWidget(apply_button)

    def show(self):
        self.window.show()

    def apply_dithering(self, option, bitness):
        if len(self.gamma_correction_view.current_pixels) != 0:
            image = RGBImage(self.gamma_correction_view.rgb_image.width,
                             self.gamma_correction_view.rgb_image.height,
                             self.gamma_correction_view.current_pixels)
        else:
            image = self.rgb_image
        try:
            bitness_value = int(bitness)
            if option == 'Floyd-Steinberg':
                new_image = dithering.floyd_steinberg_dithering(image, bitness_value)
                self.current_pixels = new_image.pixels
                self.show_image_with_current_dithering()
            elif option == 'Atkinson':
                new_image = dithering.atkinson_dithering(image, bitness_value)
                self.current_pixels = new_image.pixels
                self.show_image_with_current_dithering()
            elif option == 'Ordered':
                new_image = dithering.ordered_dithering(image, bitness_value)
                self.current_pixels = new_image.pixels
                self.show_image_with_current_dithering()
            elif option == 'Random':
                new_image = dithering.random_dithering(image, bitness_value)
                self.current_pixels = new_image.pixels
                self.show_image_with_current_dithering()
        except Exception as e:
            print(e)

    def assign_value(self, rgb_image, scene, graphics_view, gamma_correction_view):
        self.rgb_image = rgb_image
        self.scene = scene
        self.graphics_view = graphics_view
        self.current_pixels = list(self.rgb_image.pixels[:])
        self.gamma_correction_view = gamma_correction_view

    def show_image_with_current_dithering(self):
        self.changed = True
        pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.rgb_image.width, self.rgb_image.height,
                                          QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def closeEvent(self, a0, event=None):
        super().closeEvent(event)

    def close_window(self):
        self.window.close()





