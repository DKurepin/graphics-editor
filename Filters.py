from abc import ABC, abstractmethod, ABCMeta

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from scipy.ndimage.filters import gaussian_filter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
import math
import numpy as np
import random
from PNMImage import PNMImage
from conversions import rgb_to_hsv, hsv_to_rgb
from imageclasses import RGBImage


class Filter(QWidget):

    def __init__(self):
        super().__init__()
        self.image = None
        self.scene = None
        self.graphics_view = None
        self.layout = None
        self.apply_filter_button = None
        self.window = QWidget()
        self.current_pixels = []

    def assign_values(self, image, scene, graphics_view):
        self.image = image
        self.scene = scene
        self.graphics_view = graphics_view

    @abstractmethod
    def set_window(self):
        pass

    @abstractmethod
    def show(self):
        pass


class ThresholdFilter(Filter):

    def __init__(self):
        super().__init__()
        self.threshold_amount = None

    def set_window(self):
        self.window.setWindowTitle('Threshold Filter')
        self.window.setGeometry(100, 100, 150, 150)

        self.layout = QVBoxLayout(self.window)

        label = QLabel('Choose amount of threshold:')
        self.layout.addWidget(label)

        self.threshold_amount = QComboBox()
        self.threshold_amount.addItems(["0", "1", "2"])
        self.threshold_amount.currentIndexChanged.connect(self.set_threshold_amount)

        self.layout.addWidget(self.threshold_amount)

    def show(self):
        self.window.show()

    def clear_filter(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            widget.setParent(None)

        label = QLabel('Choose amount of threshold:')
        self.layout.addWidget(label)

        self.layout.addWidget(self.threshold_amount)

    def set_threshold_amount(self):
        threshold_num = int(self.threshold_amount.currentText())

        if threshold_num == 0:
            return

        if threshold_num < 0 or threshold_num > 2:
            print("Invalid thresholds amount!")
            return

        self.clear_filter()
        self.apply_filter_button = QPushButton("Apply Filter")

        if threshold_num == 1:
            threshold_label = QLabel("Threshold:")
            self.layout.addWidget(threshold_label)

            threshold_value = QLineEdit()
            self.layout.addWidget(threshold_value)

            self.apply_filter_button.clicked.connect(
                lambda: self.apply_1_threshold_filter(threshold_value.text()))
        elif threshold_num == 2:
            threshold1_label = QLabel("Threshold 1:")
            self.layout.addWidget(threshold1_label)

            threshold1_value = QLineEdit()
            self.layout.addWidget(threshold1_value)

            threshold2_label = QLabel("Threshold 2:")
            self.layout.addWidget(threshold2_label)

            threshold2_value = QLineEdit()
            self.layout.addWidget(threshold2_value)

            self.apply_filter_button.clicked.connect(
                lambda: self.apply_2_threshold_filter(threshold1_value.text(), threshold2_value.text()))

        self.layout.addWidget(self.apply_filter_button)

    def show_image(self):
        pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.image.width, self.image.height,
                                          QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def apply_1_threshold_filter(self, filter_value):
        threshold_value = int(filter_value)

        if not self.check_threshold_value(threshold_value):
            print("Invalid threshold value!")
            return

        if len(self.current_pixels) == 0:
            rgb_image = self.image.to_rgb()
            self.current_pixels = list(map(int, rgb_image.pixels))

        for i in range(0, len(self.current_pixels), 3):
            pixel_value = (self.current_pixels[i] + self.current_pixels[i + 1] + self.current_pixels[i + 2]) / 3
            value = 255 if pixel_value > threshold_value else 0
            self.current_pixels[i] = value
            self.current_pixels[i + 1] = value
            self.current_pixels[i + 2] = value

        print(set(self.current_pixels))
        self.show_image()

    def apply_2_threshold_filter(self, filter1_value, filter2_value):
        threshold1_value = int(filter1_value)
        threshold2_value = int(filter2_value)

        if not (self.check_threshold_value(threshold1_value) and
                self.check_threshold_value(threshold2_value)):
            print("Invalid threshold values!")
            return

        if threshold1_value > threshold2_value:
            threshold1_value, threshold2_value = threshold2_value, threshold1_value

        if len(self.current_pixels) == 0:
            rgb_image = self.image.to_rgb()
            self.current_pixels = list(map(int, rgb_image.pixels))

        for i in range(0, len(self.current_pixels), 3):
            pixel_value = (self.current_pixels[i] + self.current_pixels[i + 1] + self.current_pixels[i + 2]) / 3
            if pixel_value > threshold2_value:
                value = 255
            elif pixel_value < threshold1_value:
                value = 0
            else:
                value = 128
            self.current_pixels[i] = value
            self.current_pixels[i + 1] = value
            self.current_pixels[i + 2] = value

        self.show_image()

    def check_threshold_value(self, value):
        return 0 <= value <= 255


class OtsuThresholdFilter(Filter):
    def __init__(self):
        super().__init__()

    def set_window(self):
        self.window.setWindowTitle('Otsu Threshold Filter')
        self.window.setGeometry(100, 100, 150, 150)

        self.layout = QVBoxLayout(self.window)

        label = QLabel('Choose amount of threshold:')
        self.layout.addWidget(label)

        threshold_amount = QComboBox()
        threshold_amount.addItems(["0", "1", "2"])
        self.layout.addWidget(threshold_amount)

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(lambda: self.apply_filter(threshold_amount.currentText()))
        self.layout.addWidget(apply_button)

    def show_image(self):
        pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.image.width, self.image.height,
                                          QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def apply_filter(self, threshold_amount):
        threshold_amount = int(threshold_amount)

        if len(self.current_pixels) == 0:
            rgb_image = self.image.to_rgb()
            self.current_pixels = list(map(int, rgb_image.pixels))

        if threshold_amount == 1:
            self.apply_1_threshold()
        elif threshold_amount == 2:
            self.apply_2_threshold()

        self.show_image()

    def apply_1_threshold(self):
        threshold = 0
        dispersion = 0
        p = self.get_brightness_probabilities()
        u = sum([i * p[i] for i in range(len(p))])
        q1, q2, u1, u2 = p[0], 1 - p[0], 0, u
        for i in range(1, len(p)):
            q1_prev = q1
            q1 += p[i]
            if q1 != 0:
                u1 = (q1_prev * u1 + i * p[i]) / q1
                u2 = (u - q1 * u1) / (1 - q1)
                q2 = 1 - q1
                d = q1 * q2 * ((u1 - u2) ** 2)
                if dispersion < d:
                    threshold = i
                    dispersion = d

        for i in range(0, len(self.current_pixels), 3):
            value = (self.current_pixels[i] + self.current_pixels[i + 1] + self.current_pixels[i + 2]) // 3
            new_value = 0 if value <= threshold else 255
            self.current_pixels[i] = new_value
            self.current_pixels[i + 1] = new_value
            self.current_pixels[i + 2] = new_value

    def apply_2_threshold(self):
        threshold1 = 0
        threshold2 = 0
        dispersion = 0
        p = self.get_brightness_probabilities()
        u = sum([i * p[i] for i in range(len(p))])
        q1, q2, q3, u1, u2, u3 = 0, 0, 0, 0, 0, 0
        for i in range(1, len(p) - 1):
            q1_prev = q1
            q1 += p[i]
            if q1 == 0:
                u1 = 0
            else:
                u1 = (u1 * q1_prev + i * p[i]) / q1
            q2, q3, u2, u3 = 0, 0, 0, 0
            for j in range(2, len(p)):
                q2_prev = q2
                q2 += p[j]
                if q2 == 0:
                    u2 = 0
                else:
                    u2 = (u2 * q2_prev + j * p[j]) / q2
                q3 = 1 - q2 - q1
                if q3 == 0:
                    u3 = 0
                else:
                    u3 = (u - u1 * q1 - u2 * q2) / q3

                d = q1 * (u1 ** 2) + q2 * (u2 ** 2) + q3 * (u3 ** 2)
                if dispersion < d:
                    print(f"i = {i}, j = {j}, d = {d}")
                    dispersion = d
                    threshold1 = i
                    threshold2 = j

        if threshold1 > threshold2:
            threshold1, threshold2 = threshold2, threshold1

        print(threshold1)
        print(threshold2)

        for i in range(0, len(self.current_pixels), 3):
            value = (self.current_pixels[i] + self.current_pixels[i + 1] + self.current_pixels[i + 2]) // 3
            if value <= threshold1:
                new_value = 0
            elif threshold1 < value <= threshold2:
                new_value = 128
            else:
                new_value = 255
            self.current_pixels[i] = new_value
            self.current_pixels[i + 1] = new_value
            self.current_pixels[i + 2] = new_value

    def get_brightness_probabilities(self):
        size = 256
        brightness_count = [0] * size
        for i in range(0, len(self.current_pixels), 3):
            brightness = (self.current_pixels[i] + self.current_pixels[i + 1] + self.current_pixels[i + 2]) // 3
            brightness_count[brightness] += 1
        N = len(self.current_pixels) / 3
        p = [0] * size
        for i in range(size):
            count = brightness_count[i]
            p[i] = count / N
        return p

    def show(self):
        self.window.show()


class MedianFilter(Filter):
    def __init__(self):
        super().__init__()

    def set_window(self):
        self.window.setWindowTitle('Median Filter')
        self.window.setGeometry(100, 100, 150, 150)

        self.layout = QVBoxLayout(self.window)

        label = QLabel('Choose radius:')
        self.layout.addWidget(label)

        contrast_line_edit = QLineEdit()
        self.layout.addWidget(contrast_line_edit)

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(lambda: self.apply_filter(contrast_line_edit.text()))
        self.layout.addWidget(apply_button)

    def show_image(self):
        pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.image.width, self.image.height,
                                          QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def show(self):
        self.window.show()

    def apply_filter(self, radius):
        radius = int(radius)

        if len(self.current_pixels) == 0:
            rgb_image = self.image.to_rgb()
            self.current_pixels = list(map(int, rgb_image.pixels))

        pixels = self.get_brightness_matrix()
        medians = self.get_medians(pixels, radius)

        for i in range(len(medians)):
            self.current_pixels[3 * i] = medians[i]
            self.current_pixels[3 * i + 1] = medians[i]
            self.current_pixels[3 * i + 2] = medians[i]

        self.show_image()

    def get_brightness_matrix(self):
        pixels = [[0] * self.image.width for _ in range(self.image.height)]
        count = 0
        for i in range(self.image.height):
            for j in range(self.image.width):
                p1 = self.current_pixels[count]
                p2 = self.current_pixels[count + 1]
                p3 = self.current_pixels[count + 2]
                pixels[i][j] = (p1 + p2 + p3) // 3
                count += 3
        return pixels

    def get_medians(self, pixels, radius):
        medians = []
        for i in range(self.image.height):
            for j in range(self.image.width):
                medians.append(self.get_median(pixels, j, i, radius))
        return medians

    def get_median(self, pixels, x, y, r):
        values = []
        for i in range(y - r, y + r + 1):
            for j in range(x - r, x + r + 1):
                c1 = (0 if i < 0 else self.image.height - 1 if i >= self.image.height else i)
                c2 = (0 if j < 0 else self.image.width - 1 if j >= self.image.width else j)
                values.append(pixels[c1][c2])

        sorted_values = self.count_sort_matrix(values)
        return sorted_values[(((2 * r + 1) ** 2) + 1) // 2]

    def count_sort_matrix(self, values):
        counts = [0] * 256
        for value in values:
            counts[value] += 1
        current_value = 0
        for i in range(len(counts)):
            count = counts[i]
            counts[i] = current_value
            current_value += count
        sorted_values = [0] * len(values)
        for value in values:
            sorted_values[counts[value]] = value
            counts[value] += 1

        return sorted_values


class GaussFilter(Filter):
    def __init__(self):
        super().__init__()

    def set_window(self):
        self.window.setWindowTitle('Gauss Filter')
        self.window.setGeometry(100, 100, 150, 150)

        self.layout = QVBoxLayout(self.window)

        label = QLabel('Choose sigma:')
        self.layout.addWidget(label)

        sigma_value_edit = QLineEdit()
        self.layout.addWidget(sigma_value_edit)

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(lambda: self.apply_filter(sigma_value_edit.text()))
        self.layout.addWidget(apply_button)

    def show_image(self):
        pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.image.width, self.image.height,
                                          QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def show(self):
        self.window.show()

    def apply_filter(self, sigma):
        sigma = float(sigma)

        if len(self.current_pixels) == 0:
            rgb_image = self.image.to_rgb()
            self.current_pixels = list(map(int, rgb_image.pixels))

        pixels = self.get_brightness_matrix()

        pixels_gauss_values = list(map(int, self.get_pixels_gauss_values(pixels, sigma)))

        for i in range(len(pixels_gauss_values)):
            self.current_pixels[3 * i] = pixels_gauss_values[i]
            self.current_pixels[3 * i + 1] = pixels_gauss_values[i]
            self.current_pixels[3 * i + 2] = pixels_gauss_values[i]

        self.show_image()

    def get_pixels_gauss_values(self, pixels, sigma):
        r = int(max(3 * sigma, 1))

        pixels_gauss_values = []

        for i in range(self.image.height):
            for j in range(self.image.width):
                brightness_matrix = self.form_brightness_matrix(pixels, j, i, r)
                gauss_matrix = self.form_gauss_matrix(sigma)
                result = np.sum(np.multiply(brightness_matrix, gauss_matrix))
                pixels_gauss_values.append(result)

        return pixels_gauss_values

    def form_brightness_matrix(self, pixels, x, y, r):
        values = np.zeros((2 * r + 1, 2 * r + 1))

        for i in range(y - r, y + r + 1):
            for j in range(x - r, x + r + 1):
                c1 = (0 if i < 0 else self.image.height - 1 if i >= self.image.height else i)
                c2 = (0 if j < 0 else self.image.width - 1 if j >= self.image.width else j)
                values[i - (y - r)][j - (x - r)] = pixels[c1][c2]

        return values

    def form_gauss_matrix(self, sigma):
        r = int(max(3 * sigma, 1))
        x, y = np.meshgrid(np.arange(-r, r + 1), np.arange(-r, r + 1))
        gauss_matrix = np.exp(-(x ** 2 + y ** 2) / (2 * sigma ** 2)) / (2 * np.pi * sigma ** 2)
        gauss_matrix /= np.sum(gauss_matrix)
        return gauss_matrix

    def get_brightness_matrix(self):
        pixels = np.array(self.current_pixels, dtype=float).reshape(self.image.height, self.image.width, 3)
        return np.mean(pixels, axis=2).astype(int)


class BoxBlurFilter(Filter):

    def __init__(self):
        super().__init__()

    def set_window(self):
        self.window.setWindowTitle('Box Blur Filter')
        self.window.setGeometry(100, 100, 150, 150)

        self.layout = QVBoxLayout(self.window)

        label = QLabel('Choose radius:')
        self.layout.addWidget(label)

        radius_line_edit = QLineEdit()
        self.layout.addWidget(radius_line_edit)

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(lambda: self.apply_filter(radius_line_edit.text()))
        self.layout.addWidget(apply_button)

    def show_image(self):
        pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.image.width, self.image.height,
                                          QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def show(self):
        self.window.show()

    def apply_filter(self, radius):
        radius = int(radius)

        if len(self.current_pixels) == 0:
            rgb_image = self.image.to_rgb()
            self.current_pixels = list(map(int, rgb_image.pixels))

        pixels = self.get_brightness_matrix()
        box_blur_pixels = list(self.get_box_blur_pixels(pixels, radius).astype(int))

        for i in range(len(box_blur_pixels)):
            self.current_pixels[3 * i] = box_blur_pixels[i]
            self.current_pixels[3 * i + 1] = box_blur_pixels[i]
            self.current_pixels[3 * i + 2] = box_blur_pixels[i]

        self.show_image()

    def get_brightness_matrix(self):
        pixels = np.array(self.current_pixels, dtype=float).reshape(self.image.height, self.image.width, 3)
        return np.mean(pixels, axis=2).astype(int)

    def get_box_blur_pixels(self, pixels, radius):
        values = np.zeros(self.image.height * self.image.width)
        count = 0

        for i in range(self.image.height):
            for j in range(self.image.width):
                values[count] = self.get_box_blur_value(pixels, j, i, radius)
                count += 1

        return values

    def get_box_blur_value(self, pixels, x, y, r):
        box_blur_sum = 0
        for i in range(y - r, y + r + 1):
            for j in range(x - r, x + r + 1):
                c1 = (0 if i < 0 else self.image.height - 1 if i >= self.image.height else i)
                c2 = (0 if j < 0 else self.image.width - 1 if j >= self.image.width else j)
                box_blur_sum += pixels[c1][c2]
        return box_blur_sum / ((2 * r + 1) ** 2)


class UnsharpMaskingFilter(Filter):
    def __init__(self):
        super().__init__()

    def set_window(self):
        self.window.setWindowTitle('Unsharp Masking Filter')
        self.window.setGeometry(100, 100, 150, 150)

        self.layout = QVBoxLayout(self.window)

        amount_label = QLabel('Choose amount:')
        self.layout.addWidget(amount_label)

        amount_line_edit = QLineEdit()
        self.layout.addWidget(amount_line_edit)

        sigma_label = QLabel('Choose sigma:')
        self.layout.addWidget(sigma_label)

        sigma_line_edit = QLineEdit()
        self.layout.addWidget(sigma_line_edit)

        threshold_label = QLabel('Choose threshold:')
        self.layout.addWidget(threshold_label)

        threshold_line_edit = QLineEdit()
        self.layout.addWidget(threshold_line_edit)

        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(lambda: self.apply_filter(amount_line_edit.text(),
                                                               sigma_line_edit.text(),
                                                               threshold_line_edit.text()))
        self.layout.addWidget(apply_button)

    def show_image(self):
        rgb_pixels = hsv_to_rgb(self.current_pixels)
        pixmap = QPixmap.fromImage(QImage(bytes(rgb_pixels), self.image.width, self.image.height,
                                          QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def apply_filter(self, amount, sigma, threshold):
        sigma = float(sigma)
        amount = float(amount)
        threshold = int(threshold)

        if len(self.current_pixels) == 0:
            hsv_image = self.image.to_rgb().to_hsv()
            self.current_pixels = hsv_image.pixels
            v_channel = np.array(hsv_image.pixels)[2::3] * 255
        else:
            v_channel = np.array(self.current_pixels)[2::3] * 255

        v_channel = v_channel.reshape((self.image.height, self.image.width))
        v_channel = self.apply_unsharp_masking_filter(amount, sigma, threshold, v_channel) / 255

        for i in range(len(v_channel)):
            self.current_pixels[3 * i + 2] = v_channel[i]

        self.show_image()

    def show(self):
        self.window.show()

    def apply_unsharp_masking_filter(self, amount, sigma, threshold, pixels):
        pixels_gauss_values = self.get_pixels_gauss_values(pixels, sigma)

        difference_pixels = pixels.flatten() - pixels_gauss_values

        print(list(difference_pixels))

        difference_pixels = self.apply_threshold_filter(threshold, difference_pixels)

        result_pixels = (pixels.flatten() + difference_pixels * amount).astype(int)

        self.normalize_pixels(result_pixels)

        return result_pixels

    def apply_threshold_filter(self, threshold, pixels):
        size = len(pixels)
        binary_mask = np.zeros(size)
        for i in range(size):
            binary_mask[i] = 0 if pixels[i] <= threshold else pixels[i]
        return binary_mask


    def normalize_pixels(self, pixels):
        for i in range(len(pixels)):
            pixels[i] = 0 if pixels[i] < 0 else 255 if pixels[i] > 255 else pixels[i]

    def get_brightness_matrix(self):
        pixels = np.array(self.current_pixels, dtype=float).reshape(self.image.height, self.image.width, 3)
        return np.mean(pixels, axis=2).astype(int)

    def get_pixels_gauss_values(self, pixels, sigma):
        r = int(max(3 * sigma, 1))

        pixels_gauss_values = np.zeros(self.image.height * self.image.width)
        count = 0

        for i in range(self.image.height):
            for j in range(self.image.width):
                brightness_matrix = self.form_brightness_matrix(pixels, j, i, r)
                gauss_matrix = self.form_gauss_matrix(sigma)
                result = np.sum(np.multiply(brightness_matrix, gauss_matrix))
                pixels_gauss_values[count] = result
                count += 1

        return pixels_gauss_values

    def form_brightness_matrix(self, pixels, x, y, r):
        values = np.zeros((2 * r + 1, 2 * r + 1))

        for i in range(y - r, y + r + 1):
            for j in range(x - r, x + r + 1):
                c1 = (0 if i < 0 else self.image.height - 1 if i >= self.image.height else i)
                c2 = (0 if j < 0 else self.image.width - 1 if j >= self.image.width else j)
                values[i - (y - r)][j - (x - r)] = pixels[c1][c2]

        return values

    def form_gauss_matrix(self, sigma):
        r = int(max(3 * sigma, 1))
        x, y = np.meshgrid(np.arange(-r, r + 1), np.arange(-r, r + 1))
        gauss_matrix = np.exp(-(x ** 2 + y ** 2) / (2 * sigma ** 2)) / (2 * np.pi * sigma ** 2)
        gauss_matrix /= np.sum(gauss_matrix)
        return gauss_matrix


# class CASFilter(Filter):
#
#     def __init__(self):
#         super().__init__()
#
#     def set_window(self):
#         self.window.setWindowTitle('CAS Filter')
#         self.window.setGeometry(100, 100, 150, 150)
#
#         self.layout = QVBoxLayout(self.window)
#
#         label = QLabel('Input sharpness value (0.0 - 1.0):')
#         self.layout.addWidget(label)
#
#         sharpness_value = QLineEdit()
#         self.layout.addWidget(sharpness_value)
#
#         self.apply_filter_button = QPushButton("Apply CAS Filter")
#         self.apply_filter_button.clicked.connect(lambda: self.apply_cas_filter(sharpness_value.text()))
#
#         self.layout.addWidget(self.apply_filter_button)
#
#     def show(self):
#         self.window.show()
#
#     def show_image(self):
#         pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.image.width, self.image.height,
#                                           QImage.Format.Format_RGB888))
#         self.scene.clear()
#         self.scene.addPixmap(pixmap)
#         self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
#
#     def apply_cas_filter(self, sharpness_value):
#         sharpness_value = float(sharpness_value)
#         if sharpness_value < 0 or sharpness_value > 1:
#             print("Invalid sharpness value!")
#             return
#         if len(self.current_pixels) == 0:
#             rgb_image = self.image.to_rgb()
#             self.current_pixels = list(map(int, rgb_image.pixels))
#
#         pixels_array = np.array(self.current_pixels, dtype=np.uint8).reshape((self.image.height, self.image.width, 3))
#
#         gray_pixels = np.dot(pixels_array[..., :3], [0.2989, 0.5870, 0.1140])
#
#         blurred_img = self.gaussian_blur(gray_pixels, radius=2)
#
#         sharpened_img = 1.5 * gray_pixels - 0.5 * blurred_img
#
#         sharpened_img = self.apply_better_diagonals(sharpened_img)
#
#         cas_sharpened_img = sharpness_value * gray_pixels + (1 - sharpness_value) * sharpened_img
#
#         cas_sharpened_img = np.stack([cas_sharpened_img] * 3, axis=-1).astype(np.uint8)
#
#         self.current_pixels = cas_sharpened_img.flatten().tolist()
#
#         self.show_image()
#
#     def gaussian_blur(self, img, radius=2):
#         kernel_size = 2 * radius + 1
#         kernel = np.fromfunction(
#             lambda x, y: (1 / (2 * np.pi * radius ** 2)) * np.exp(
#                 -((x - radius) ** 2 + (y - radius) ** 2) / (2 * radius ** 2)),
#             (kernel_size, kernel_size)
#         )
#         kernel /= np.sum(kernel)
#
#         result = np.zeros_like(img)
#
#         for i in range(radius, img.shape[0] - radius):
#             for j in range(radius, img.shape[1] - radius):
#                 result[i, j] = np.sum(img[i - radius:i + radius + 1, j - radius:j + radius + 1] * kernel)
#
#         return result
#
#     def apply_better_diagonals(self, img):
#         kernel = np.array([[-1, 0, -1],
#                            [0, 5, 0],
#                            [-1, 0, -1]])
#
#         result = np.zeros_like(img)
#
#         for i in range(1, img.shape[0] - 1):
#             for j in range(1, img.shape[1] - 1):
#                 result[i, j] = np.sum(img[i - 1:i + 2, j - 1:j + 2] * kernel)
#
#         return np.clip(result, 0, 255)


class CASFilter(Filter):
    def init(self):
        super().init()

    def set_window(self):
        self.window.setWindowTitle('CAS Filter')
        self.window.setGeometry(100, 100, 150, 150)

        self.layout = QVBoxLayout(self.window)

        label = QLabel('Input sharpness value (0.0 - 1.0):')
        self.layout.addWidget(label)

        self.sharpness_value = QLineEdit()
        self.layout.addWidget(self.sharpness_value)

        self.apply_filter_button = QPushButton("Apply CAS Filter")
        self.apply_filter_button.clicked.connect(self.apply_cas_filter)

        self.layout.addWidget(self.apply_filter_button)

    def show(self):
        self.window.show()

    def show_image(self):
        pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.image.width, self.image.height,
                                          QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def apply_cas_filter(self):
        sharpness_value = float(self.sharpness_value.text())
        if sharpness_value < 0 or sharpness_value > 1:
            print("Invalid sharpness value!")
            return
        if len(self.current_pixels) == 0:
            rgb_image = self.image.to_rgb()
            self.current_pixels = list(map(int, rgb_image.pixels))

        pixels_array = np.array(self.current_pixels, dtype=np.uint8).reshape((self.image.height, self.image.width, 3))

        filtered_pixels = np.zeros((self.image.height, self.image.width, 3), dtype=np.float32)
        temp_pixels = pixels_array / 255.0

        for y in range(1, self.image.height - 1):
            for x in range(1, self.image.width - 1):
                a, b, c = temp_pixels[y - 1, x - 1:x + 2].flatten()[:3]
                d, e, f = temp_pixels[y, x - 1:x + 2].flatten()[:3]
                g, h, i = temp_pixels[y + 1, x - 1:x + 2].flatten()[:3]

                a, b, c, d, e, f, g, h, i = self.better_diagonals(a, b, c, d, e, f, g, h, i)

                mnL = min(d, e, f, b, h)
                mxL = max(d, e, f, b, h)
                mnL2 = min([mnL, min(a, c), min(g, i)])
                mnL += mnL2
                mxL2 = max([mxL, max(a, c), max(g, i)])
                mxL += mxL2

                tol = max(mnL, 2.0 - mxL) / mxL
                ampL = math.sqrt(math.sqrt(tol))
                peak = -(8.0 + 5.0 * max(min(sharpness_value, 1.0), 0.0))
                wL = ampL / peak
                weights = 1.0 + wL * 4.0

                filtered_pixels[y, x] = ((b + d + f + h) * wL + e) / weights

        filtered_normalized = filtered_pixels.clip(0.0, 1.0) * 255.0

        self.current_pixels = filtered_normalized.astype(np.uint8).flatten()

        self.show_image()

    def better_diagonals(self, a, b, c, d, e, f, g, h, i):
        EPSILON = 1e-8
        a = a
        b = b
        c = c
        d = d
        e = e
        f = f
        g = g
        h = h
        i = i

        cross = np.array([b, d, e, f, h])
        mn = np.min(cross)
        mx = np.max(cross)

        inv_mx = 1.0 / (mx + EPSILON)
        amp = inv_mx * min(mn, (2 - mx))

        amp = math.sqrt(math.sqrt(amp))

        return a, b, c, d, e, f, g, h, i


class SobelFilter(Filter):

    def __init__(self):
        super().__init__()

    def set_window(self):
        self.window.setWindowTitle('Sobel Filter')
        self.window.setGeometry(100, 100, 150, 150)

        self.layout = QVBoxLayout(self.window)

        self.apply_filter_button = QPushButton("Apply Sobel Filter")
        self.apply_filter_button.clicked.connect(self.apply_sobel_filter)

        self.layout.addWidget(self.apply_filter_button)

    def show(self):
        self.window.show()

    def show_image(self):
        pixmap = QPixmap.fromImage(QImage(bytes(self.current_pixels), self.image.width, self.image.height,
                                          QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def apply_sobel_filter(self):
        if len(self.current_pixels) == 0:
            rgb_image = self.image.to_rgb()
            self.current_pixels = list(map(int, rgb_image.pixels))

        for i in range(0, len(self.current_pixels), 3):
            val = (self.current_pixels[i] + self.current_pixels[i + 1] + self.current_pixels[i + 2]) // 3
            self.current_pixels[i] = val
            self.current_pixels[i + 1] = val
            self.current_pixels[i + 2] = val

        gradient_magnitude = self.calculate_sobel_gradients(self.current_pixels)
        # gradient_magnitude = np.clip(gradient_magnitude, 0, 255)
        # gradient_magnitude = gradient_magnitude
        self.current_pixels = gradient_magnitude
        self.show_image()

    def calculate_sobel_gradients(self, pixels):
        width, height = self.image.width, self.image.height
        pixels = []
        for i in range(0, len(self.current_pixels), 3):
            pixels.append((self.current_pixels[i] + self.current_pixels[i + 1] + self.current_pixels[i + 2]) // 3)
        pixels = np.array(pixels).reshape((height, width))
        new_pixels = np.empty((height, width) + (3,), dtype=np.uint8)

        Gx = np.array([[1.0, 0.0, -1.0], [2.0, 0.0, -2.0], [1.0, 0.0, -1.0]])
        Gy = np.array([[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]])

        for i in range(1, height - 1):
            for j in range(1, width - 1):
                gx = np.sum(Gx * pixels[i - 1: i + 2, j - 1: j + 2])
                gy = np.sum(Gy * pixels[i - 1: i + 2, j - 1: j + 2])
                gradient_magnitude = np.sqrt(gx * gx + gy * gy)
                new_pixels[i, j] = gradient_magnitude

        return new_pixels


class CannyEdgeDetector(Filter):

    def __init__(self):
        super().__init__()

    def set_window(self):
        self.window.setWindowTitle('Canny Edge Detector')
        self.window.setGeometry(100, 100, 150, 150)

        self.layout = QVBoxLayout(self.window)

        self.apply_filter_button = QPushButton("Apply Canny Edge Detector")
        self.apply_filter_button.clicked.connect(self.apply_canny_edge_detector)

        self.layout.addWidget(self.apply_filter_button)

    def show(self):
        self.window.show()

    def show_image(self):
        if len(self.current_pixels) == 0:
            return

        normalized_pixels = np.clip(self.current_pixels, 0, 255)
        normalized_pixels = normalized_pixels.astype(np.uint8)

        pixmap = QPixmap.fromImage(QImage(bytes(normalized_pixels), self.image.width, self.image.height,
                                          QImage.Format.Format_RGB888))
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def apply_canny_edge_detector(self):
        if len(self.current_pixels) == 0:
            rgb_image = self.image.to_rgb()
            self.current_pixels = list(map(int, rgb_image.pixels))

        self.current_pixels = self.gaussian_smoothing(self.current_pixels)

        for i in range(0, len(self.current_pixels), 3):
            val = (self.current_pixels[i] + self.current_pixels[i + 1] + self.current_pixels[i + 2]) // 3
            self.current_pixels[i] = val
            self.current_pixels[i + 1] = val
            self.current_pixels[i + 2] = val

        gradient_magnitude, gradient_direction = self.calculate_gradients(self.current_pixels)
        # Non-maximum suppression
        gradient_magnitude = self.non_maximum_suppression(gradient_magnitude, gradient_direction)
        # Double threshold
        high_threshold, low_threshold = 50, 5
        gradient_magnitude = self.double_threshold(gradient_magnitude, high_threshold, low_threshold)
        # # Edge tracking by hysteresis
        gradient_magnitude = self.edge_tracking_by_hysteresis(gradient_magnitude, high_threshold, low_threshold)

        self.current_pixels = gradient_magnitude
        self.show_image()


    def gaussian_smoothing(self, pixels):
        width, height = self.image.width, self.image.height

        pixels_array = np.array(pixels).reshape((height, width, 3))

        blurred_image = gaussian_filter(pixels_array, sigma=3)

        return blurred_image.flatten().tolist()


    def calculate_gradients(self, pixels):
        width, height = self.image.width, self.image.height
        pixels = []
        for i in range(0, len(self.current_pixels), 3):
            pixels.append((self.current_pixels[i] + self.current_pixels[i + 1] + self.current_pixels[i + 2]) // 3)
        pixels = np.array(pixels).reshape((height, width))
        gradient_mag = np.zeros((height, width), dtype=np.uint8)
        gradient_dir = np.zeros((height, width), dtype=np.uint8)
        Gx = np.array([[1.0, 0.0, -1.0], [2.0, 0.0, -2.0], [1.0, 0.0, -1.0]])
        Gy = np.array([[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]])

        for i in range(1, height - 1):
            for j in range(1, width - 1):
                gx = np.sum(Gx * pixels[i - 1: i + 2, j - 1: j + 2])
                gy = np.sum(Gy * pixels[i - 1: i + 2, j - 1: j + 2])
                gradient_magnitude = np.sqrt(gx * gx + gy * gy)
                gradient_direction = np.arctan2(gy, gx)
                gradient_mag[i, j] = gradient_magnitude
                gradient_dir[i, j] = gradient_direction

        return gradient_mag, gradient_dir

    def non_maximum_suppression(self, gradient_magnitude, gradient_direction):
        width, height = self.image.width, self.image.height
        new_pixels = np.zeros((height, width), dtype=np.uint8)
        angle = gradient_direction * 180. / np.pi
        angle[angle < 0] += 180

        for i in range(1, height - 1):
            for j in range(1, width - 1):
                q = 255
                r = 255

                # angle 0
                if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180):
                    q = gradient_magnitude[i, j + 1]
                    r = gradient_magnitude[i, j - 1]
                # angle 45
                elif 22.5 <= angle[i, j] < 67.5:
                    q = gradient_magnitude[i + 1, j - 1]
                    r = gradient_magnitude[i - 1, j + 1]
                # angle 90
                elif 67.5 <= angle[i, j] < 112.5:
                    q = gradient_magnitude[i + 1, j]
                    r = gradient_magnitude[i - 1, j]
                # angle 135
                elif 112.5 <= angle[i, j] < 157.5:
                    q = gradient_magnitude[i - 1, j - 1]
                    r = gradient_magnitude[i + 1, j + 1]

                if (gradient_magnitude[i, j] >= q) and (gradient_magnitude[i, j] >= r):
                    new_pixels[i, j] = gradient_magnitude[i, j]
                else:
                    new_pixels[i, j] = 0

        return new_pixels

    def double_threshold(self, gradient_magnitude, high_threshold, low_threshold):
        width, height = self.image.width, self.image.height
        new_pixels = np.zeros((height, width), dtype=np.uint8)
        weak = np.int32(25)
        strong = np.int32(255)

        strong_i, strong_j = np.where(gradient_magnitude >= high_threshold)
        zeros_i, zeros_j = np.where(gradient_magnitude < low_threshold)

        weak_i, weak_j = np.where((gradient_magnitude <= high_threshold) & (gradient_magnitude >= low_threshold))
        new_pixels[strong_i, strong_j] = strong
        new_pixels[weak_i, weak_j] = weak
        return new_pixels

    def edge_tracking_by_hysteresis(self, gradient_magnitude, high_threshold, low_threshold):
        width, height = self.image.width, self.image.height
        weak = np.int32(25)
        strong = np.int32(255)

        result_pixels = np.zeros((height, width) + (3,), dtype=np.uint8)
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                if gradient_magnitude[i, j] == weak:
                    if ((gradient_magnitude[i + 1, j - 1] == strong) or (gradient_magnitude[i + 1, j] == strong) or (gradient_magnitude[i + 1, j + 1] == strong)
                            or (gradient_magnitude[i, j - 1] == strong) or (gradient_magnitude[i, j + 1] == strong)
                            or (gradient_magnitude[i - 1, j - 1] == strong) or (gradient_magnitude[i - 1, j] == strong) or (gradient_magnitude[i - 1, j + 1] == strong)):
                        result_pixels[i, j] = strong
                    else:
                        result_pixels[i, j] = 0
                else:
                    result_pixels[i, j] = gradient_magnitude[i, j]
        return result_pixels


