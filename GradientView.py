from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QComboBox, QLineEdit, QVBoxLayout, QPushButton, QGraphicsScene

import gradient

class GradientView(QWidget):

    def __init__(self):
        super().__init__()
        self.current_pixels = []
        self.rgb_image = None
        self.scene = None
        self.graphics_view = None
        self.window = QWidget()
        self.width_line_edit = QLineEdit()
        self.height_line_edit = QLineEdit()
        self.width = 0
        self.height = 0
        self.changed = False;


    def set_window(self):
        self.window.setWindowTitle('Gradient')
        self.window.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout(self.window)
        self.width_line_edit.setPlaceholderText('Width')
        self.height_line_edit.setPlaceholderText('Height')

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(
            lambda: self.apply_gradient(self.width_line_edit.text(), self.height_line_edit.text()))
        finish_button = QPushButton('Finish')
        finish_button.clicked.connect(self.finish)

        layout.addWidget(self.width_line_edit)
        layout.addWidget(self.height_line_edit)
        layout.addWidget(apply_button)
        layout.addWidget(finish_button)

    def show(self):
        self.window.show()

    def apply_gradient(self, width, height):
        try:
            self.width = int(width)
            self.height = int(height)
            new_image = gradient.gradient(self.width, self.height)
            self.current_pixels = new_image.pixels
            self.show_image_with_current_gradient()
        except Exception as e:
            print(e)

    def assign_value(self,  scene, graphics_view):
        self.scene = scene
        self.graphics_view = graphics_view

    def show_image_with_current_gradient(self):
        self.changed = True
        pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.width, self.height,
                                          QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def finish(self):
        if self.changed:
            self.rgb_image = gradient.RGBImage(self.width, self.height, self.current_pixels)
        self.close_window()

    def closeEvent(self, event):
        self.window.close()

    def close_window(self):
        self.window.close()

    def get_changed(self):
        return self.changed

    def get_current_pixels_rgb_image(self):
        return gradient.RGBImage(self.width, self.height, self.current_pixels)

