from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel

from canalclasses import bytecanal
from imageclasses import RGBImage


class ContrastCorrectionView(QWidget):
    def __init__(self):
        super().__init__()
        self.current_pixels = []
        self.image = None
        self.scene = None
        self.graphics_view = None
        self.window = QWidget()
        self.changed = False
        self.channel = None
        self.color_space = None
        self.ignored_pixels_part = 0

    def set_window(self):
        self.window.setWindowTitle('Contrast Correction')
        self.window.setGeometry(100, 100, 150, 150)

        layout = QVBoxLayout(self.window)

        ignored_pixels_part = QLabel("Part to ignore")
        layout.addWidget(ignored_pixels_part)

        contrast_line_edit = QLineEdit()
        layout.addWidget(contrast_line_edit)

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(lambda: self.change_pixels_depends_on_image_format(contrast_line_edit.text()))

        layout.addWidget(apply_button)

    def show(self):
        self.window.show()

    def assign_value(self, image, scene, graphics_view, channel, color_space):
        self.image = image
        self.scene = scene
        self.graphics_view = graphics_view
        self.channel = channel
        self.color_space = color_space

    def apply_contrast_correction(self, ignored_pixels_part):
        self.changed = True
        self.ignored_pixels_part = float(ignored_pixels_part)

        rgb_image = self.image.to_rgb()
        channel_pixels = self.get_channels_pixels(rgb_image, self.channel)

        brightness_changed_channel_pixels = {}

        for channel in channel_pixels.keys():
            pixels = channel_pixels[channel]
            brightness_changed_pixels = self.change_brightness(pixels)
            brightness_changed_channel_pixels[channel] = brightness_changed_pixels

        channels_count = len(brightness_changed_channel_pixels)

        if channels_count == 1:
            self.current_pixels = brightness_changed_channel_pixels[self.channel]
            channel = bytecanal(self.image.width, self.image.height, bytearray(self.current_pixels))
            pixmap = channel.to_gray().to_qpixmap()
        else:
            channel1_pixels = brightness_changed_channel_pixels['1']
            channel2_pixels = brightness_changed_channel_pixels['2']
            channel3_pixels = brightness_changed_channel_pixels['3']
            self.current_pixels = self.form_rgb_image_pixels(channel1_pixels, channel2_pixels, channel3_pixels)
            pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.image.width, self.image.height,
                                              QImage.Format.Format_RGB888))
        self.draw_image(pixmap)

    def get_channels_pixels(self, rgb_image, channel):
        channels = {}
        pixels = rgb_image.pixels
        if channel == 'all':
            channels['1'] = [pixels[i] for i in range(0, len(pixels), 3)]
            channels['2'] = [pixels[i] for i in range(1, len(pixels), 3)]
            channels['3'] = [pixels[i] for i in range(2, len(pixels), 3)]
        else:
            channels[channel] = [pixels[i] for i in range((ord(channel) - ord('1')), len(pixels), 3)]
        return channels

    def draw_image(self, pixmap):
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def change_brightness(self, pixels, min_val, max_val):
        changed_pixels = []
        for x in pixels:
            changed_val = int((x - min_val) / (max_val - min_val) * 255)
            saturated_changed_val = 0 if changed_val < 0 else 255 if changed_val > 255 else changed_val
            changed_pixels.append(saturated_changed_val)
        return changed_pixels

    def form_rgb_image_pixels(self, channel1_pixels, channel2_pixels, channel3_pixels):
        channel_size = len(channel1_pixels)
        rgb_image_pixels = [0] * channel_size * 3
        for i in range(channel_size):
            rgb_image_pixels[i * 3] = channel1_pixels[i]
            rgb_image_pixels[i * 3 + 1] = channel2_pixels[i]
            rgb_image_pixels[i * 3 + 2] = channel3_pixels[i]
        return rgb_image_pixels

    def change_pixels_depends_on_image_format(self, ignored_pixels_part):
        self.changed = True
        self.ignored_pixels_part = float(ignored_pixels_part)
        if self.color_space == 'CMY' or self.color_space == 'RGB':
            channel1 = self.image.canal(0).to_gray().pixels
            channel2 = self.image.canal(1).to_gray().pixels
            channel3 = self.image.canal(2).to_gray().pixels

            size = len(channel1)

            sorted_channel1 = sorted(channel1)
            sorted_channel2 = sorted(channel2)
            sorted_channel3 = sorted(channel3)

            amount_of_pixels_to_ignore = int((size / 2) * self.ignored_pixels_part)

            min_val1 = sorted_channel1[amount_of_pixels_to_ignore]
            min_val2 = sorted_channel2[amount_of_pixels_to_ignore]
            min_val3 = sorted_channel3[amount_of_pixels_to_ignore]

            max_val1 = sorted_channel1[size - amount_of_pixels_to_ignore - 1]
            max_val2 = sorted_channel2[size - amount_of_pixels_to_ignore - 1]
            max_val3 = sorted_channel3[size - amount_of_pixels_to_ignore - 1]

            min_val = min(min_val1, min_val2, min_val3)
            max_val = max(max_val1, max_val2, max_val3)

            ch1 = self.change_brightness(channel1, min_val, max_val)
            ch2 = self.change_brightness(channel2, min_val, max_val)
            ch3 = self.change_brightness(channel3, min_val, max_val)

            self.current_pixels = self.form_rgb_image_pixels(ch1, ch2, ch3)
            rgb_image = RGBImage(bytes(self.current_pixels), self.image.width, self.image.height)
            if self.channel == '1':
                pixmap = rgb_image.canal(0).to_gray().to_qpixmap()
            elif self.channel == '2':
                pixmap = rgb_image.canal(1).to_gray().to_qpixmap()
            elif self.channel == '3':
                pixmap = rgb_image.canal(2).to_gray().to_qpixmap()
            else:
                pixmap = QPixmap.fromImage(QImage(rgb_image.pixels, self.image.width, self.image.height,
                                                  QImage.Format.Format_RGB888))

            self.draw_image(pixmap)

        elif self.color_space == 'YCbCr601' or self.color_space == 'YCbCr709' or self.color_space == 'YCoCg':

            channel1 = self.image.canal(0).to_gray().pixels
            channel2 = self.image.canal(1).to_gray().pixels
            channel3 = self.image.canal(2).to_gray().pixels

            size = len(channel1)

            sorted_channel1 = sorted(channel1)

            amount_of_pixels_to_ignore = int((size / 2) * self.ignored_pixels_part)

            min_val = sorted_channel1[amount_of_pixels_to_ignore]

            max_val = sorted_channel1[size - amount_of_pixels_to_ignore - 1]

            ch1 = self.change_brightness(channel1, min_val, max_val)

            self.current_pixels = self.form_rgb_image_pixels(ch1, channel2, channel3)
            rgb_image = RGBImage(bytes(self.current_pixels), self.image.width, self.image.height)
            if self.channel == '1':
                pixmap = rgb_image.canal(0).to_gray().to_qpixmap()
            elif self.channel == '2':
                pixmap = rgb_image.canal(1).to_gray().to_qpixmap()
            elif self.channel == '3':
                pixmap = rgb_image.canal(2).to_gray().to_qpixmap()
            else:
                pixmap = QPixmap.fromImage(QImage(rgb_image.pixels, self.image.width, self.image.height,
                                                  QImage.Format.Format_RGB888))
            self.draw_image(pixmap)
