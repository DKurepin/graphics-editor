from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QComboBox, QLineEdit, QVBoxLayout, QPushButton, QGraphicsScene, QHBoxLayout, QDialog, QLabel

import scaling
from imageclasses import RGBImage

class ScalingImageView(QWidget):

    def __init__(self):
        super().__init__()
        self.current_pixels = []
        self.versions_of_images = []
        self.rgb_image = None
        self.scene = None
        self.graphics_view = None

        self.window = QWidget()
        self.width_line_edit = QLineEdit()
        self.height_line_edit = QLineEdit()
        self.bias_x_line_edit = QLineEdit()
        self.bias_y_line_edit = QLineEdit()
        self.scaling_options_combo_box = QComboBox()
        self.b_line_edit = QLineEdit()
        self.c_line_edit = QLineEdit()

        self.width = 0
        self.height = 0
        self.bias_x = 0
        self.bias_y = 0
        self.b = 0
        self.c = 0
        self.changed = False

        self.bc_spline_window = QDialog(self.window)
        self.bc_spline_window.setWindowTitle('BC-Spline Parameters')
        self.bc_spline_window.setGeometry(100, 100, 200, 200)

        self.bc_spline_layout = QVBoxLayout(self.bc_spline_window)
        self.bc_spline_b_label = QLabel('Parameter B:')
        self.bc_spline_c_label = QLabel('Parameter C:')
        self.bc_spline_b_line_edit = QLineEdit()
        self.bc_spline_c_line_edit = QLineEdit()
        self.bc_spline_apply_button = QPushButton('Apply')
        self.bc_spline_apply_button.clicked.connect(self.apply_bc_spline_parameters)

        self.bc_spline_layout.addWidget(self.bc_spline_b_label)
        self.bc_spline_layout.addWidget(self.bc_spline_b_line_edit)
        self.bc_spline_layout.addWidget(self.bc_spline_c_label)
        self.bc_spline_layout.addWidget(self.bc_spline_c_line_edit)
        self.bc_spline_layout.addWidget(self.bc_spline_apply_button)

    def set_window(self):
        self.window.setWindowTitle('Scaling Image')
        self.window.setGeometry(100, 100, 400, 200)
        self.changed = False

        main_layout = QVBoxLayout(self.window)
        input_layout = QHBoxLayout()
        bias_layout = QHBoxLayout()
        bc_spline_layout = QVBoxLayout()

        self.width_line_edit.setPlaceholderText('Width')
        self.height_line_edit.setPlaceholderText('Height')
        self.bias_x_line_edit.setPlaceholderText('Bias X')
        self.bias_y_line_edit.setPlaceholderText('Bias Y')
        self.scaling_options_combo_box.addItems(["Nearest Neighbor", "Bilinear", "Lanczos", "BC-Spline"])

        buttons_layout = QHBoxLayout()

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(
            lambda: self.apply_scaling(self.scaling_options_combo_box.currentText(), self.width_line_edit.text(),
                                       self.height_line_edit.text(), self.bias_x_line_edit.text(),
                                       self.bias_y_line_edit.text()))

        revert_button = QPushButton('Revert')
        revert_button.clicked.connect(self.revert)

        apply_crop_button = QPushButton('Apply Crop')
        apply_crop_button.clicked.connect(self.apply_crop)

        finish_button = QPushButton('Finish')
        finish_button.clicked.connect(self.finish)

        buttons_layout.addWidget(apply_button)
        buttons_layout.addWidget(revert_button)
        buttons_layout.addWidget(apply_crop_button)
        buttons_layout.addWidget(finish_button)

        input_layout.addWidget(self.width_line_edit)
        input_layout.addWidget(self.height_line_edit)
        bias_layout.addWidget(self.bias_x_line_edit)
        bias_layout.addWidget(self.bias_y_line_edit)

        main_layout.addLayout(input_layout)
        main_layout.addLayout(bias_layout)
        main_layout.addWidget(self.scaling_options_combo_box)
        main_layout.addLayout(bc_spline_layout)
        main_layout.addLayout(buttons_layout)

        self.scaling_options_combo_box.currentIndexChanged.connect(self.show_bc_spline_parameters)

    def show_bc_spline_parameters(self, index):
        if index == 3:
            self.bc_spline_window.show()
        else:
            self.bc_spline_window.hide()

    def apply_bc_spline_parameters(self):
        try:
            b = float(self.bc_spline_b_line_edit.text())
            c = float(self.bc_spline_c_line_edit.text())
            self.b = b
            self.c = c
            self.bc_spline_window.hide()
        except Exception as e:
            print(e)

    def show(self):
        self.window.show()

    def apply_scaling(self, option, width, height, bias_x=0, bias_y=0):
        try:
            print(f'Count of versions: {len(self.versions_of_images)}')
            if len(self.versions_of_images) == 0:
                new_rgb_image = RGBImage(self.rgb_image.width, self.rgb_image.height, self.current_pixels)
                print(f'first version: {new_rgb_image.width}, {new_rgb_image.height}')
                self.versions_of_images.append(new_rgb_image)
            else:
                new_rgb_image = RGBImage(self.width, self.height, self.current_pixels)
                print(f'new version: {new_rgb_image.width}, {new_rgb_image.height}')
                self.versions_of_images.append(new_rgb_image)
            self.width = int(width)
            self.height = int(height)
            self.bias_x = float(bias_x)
            self.bias_y = float(bias_y)
            self.changed = True
            self.scene.clear()
            if option == 'Nearest Neighbor':
                new_image = scaling.nearest_neighbor(self.rgb_image, self.width, self.height)
                self.current_pixels = new_image.pixels
                self.show_image_with_current_scaling()
            elif option == 'Bilinear':
                new_image = scaling.bilinear_scaling(self.rgb_image, self.width, self.height)
                self.current_pixels = new_image.pixels
                self.show_image_with_current_scaling()
            elif option == 'Lanczos':
                new_image = scaling.lanczos3(self.rgb_image, self.width, self.height)
                self.current_pixels = new_image.pixels
                self.show_image_with_current_scaling()
            elif option == 'BC-Spline':
                new_image = scaling.bc_splines(self.rgb_image, self.width, self.height, self.b, self.c)
                self.current_pixels = new_image.pixels
                self.show_image_with_current_scaling()

        except Exception as e:
            print(e)

    def revert(self):
        if len(self.versions_of_images) > 0:
            self.current_pixels = self.versions_of_images[-1].pixels
            self.width = self.versions_of_images[-1].width
            self.height = self.versions_of_images[-1].height
            self.versions_of_images.pop()
            pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.width, self.height,
                                                QImage.Format.Format_RGB888))
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.scene.setSceneRect(0, 0, self.width, self.height)


    def closeEvent(self, event):
        self.window.close()

    def close_window(self):
        self.window.close()

    def show_image_with_current_scaling(self):
        offset = 0
        if self.bias_x < 0:
            offset += abs(self.bias_x)
        if self.bias_y < 0:
            offset += abs(self.bias_y)

        center_x = self.bias_x + self.width // 2
        center_y = self.bias_y + self.height // 2
        if center_x < 0:
            center_x = 0
        if center_y < 0:
            center_y = 0

        window_width = self.graphics_view.width()
        window_height = self.graphics_view.height()
        if self.width < window_width:
            offset += (window_width - self.width) // 2
        if self.height < window_height:
            offset += (window_height - self.height) // 2

        print(f'offset: {offset} '
              f'center_x: {center_x}, center_y: {center_y} '
              f'window_width: {window_width}, window_height: {window_height} '
              f'width: {self.width}, height: {self.height} '
              f'bias_x: {self.bias_x}, bias_y: {self.bias_y}')

        pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.width, self.height,
                                            QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(0, 0, self.width, self.height)
        print(f'center_x: {center_x}, center_y: {center_y}')
        self.graphics_view.centerOn(center_x, center_y)

    def finish(self):
        if self.changed:
            self.rgb_image = RGBImage(self.width, self.height, self.current_pixels)
        self.versions_of_images = []
        self.close_window()

    def assign_value(self, rgb_image, scene, graphics_view):
        self.rgb_image = rgb_image
        self.scene = scene
        self.graphics_view = graphics_view
        self.current_pixels = list(self.rgb_image.pixels[:])

    def apply_crop(self):
        center_x = self.bias_x + self.width / 2
        center_y = self.bias_y + self.height / 2

        window_width = self.graphics_view.width()
        window_height = self.graphics_view.height()
        print(f'window_width: {window_width}, window_height: {window_height}')

        cropped_width = min(self.width, window_width)
        cropped_height = min(self.height, window_height)

        cropped_pixels = []

        for i in range(cropped_height):
            for j in range(cropped_width):
                x = center_x - cropped_width / 2 + j
                y = center_y - cropped_height / 2 + i
                pixel = self.bilinear_interpolation(x, y)
                cropped_pixels.extend(pixel)

        self.current_pixels = cropped_pixels
        self.width = cropped_width
        self.height = cropped_height

        pixmap = QPixmap.fromImage(
            QImage(bytes(self.current_pixels), self.width, self.height, QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(0, 0, self.width, self.height)
        print(f'image width: {self.width}, image height: {self.height}')
        self.changed = True

    def bilinear_interpolation(self, x, y):
        x0 = int(x)
        y0 = int(y)
        x1 = x0 + 1
        y1 = y0 + 1

        wx1 = x - x0
        wx0 = 1 - wx1
        wy1 = y - y0
        wy0 = 1 - wy1

        x0 = max(0, min(x0, self.width - 1))
        x1 = max(0, min(x1, self.width - 1))
        y0 = max(0, min(y0, self.height - 1))
        y1 = max(0, min(y1, self.height - 1))

        pixel00 = self.current_pixels[3 * (y0 * self.width + x0):3 * (y0 * self.width + x0 + 1)]
        pixel01 = self.current_pixels[3 * (y0 * self.width + x1):3 * (y0 * self.width + x1 + 1)]
        pixel10 = self.current_pixels[3 * (y1 * self.width + x0):3 * (y1 * self.width + x0 + 1)]
        pixel11 = self.current_pixels[3 * (y1 * self.width + x1):3 * (y1 * self.width + x1 + 1)]

        result = [
            int(wx0 * wy0 * pixel00[0] + wx1 * wy0 * pixel01[0] + wx0 * wy1 * pixel10[0] + wx1 * wy1 * pixel11[0]),
            int(wx0 * wy0 * pixel00[1] + wx1 * wy0 * pixel01[1] + wx0 * wy1 * pixel10[1] + wx1 * wy1 * pixel11[1]),
            int(wx0 * wy0 * pixel00[2] + wx1 * wy0 * pixel01[2] + wx0 * wy1 * pixel10[2] + wx1 * wy1 * pixel11[2])
        ]

        return result

    def get_current_pixels_rgb_image(self):
        return RGBImage(self.width, self.height, list(map(int, self.current_pixels)))

    def get_changed(self):
        return self.changed

    def set_changed(self, changed):
        self.changed = changed

    def get_current_pixels(self):
        return self.current_pixels

    def set_current_pixels(self, current_pixels):
        self.current_pixels = current_pixels