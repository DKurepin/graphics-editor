import matplotlib.pyplot as plt
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QComboBox, QLineEdit, QVBoxLayout, QPushButton, QGraphicsScene, QGraphicsView, \
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class HistogramView(QWidget):

    def __init__(self):
        super().__init__()
        self.channel = None
        self.image = None
        self.scene = None
        self.graphics_view = None
        self.layout = None
        self.figure = None
        self.histogram_scene = None
        self.histogram_view = None
        self.histogram_window = None
        self.canvas = None
        self.channels_colors = {'all': 'black', '1': 'red', '2': 'green', '3': 'blue'}
        self.channels_titles = {'all': 'Channel RGB', '1': 'Channel Red', '2': 'Channel Green', '3': 'Channel Blue'}

    def initUi(self):
        self.histogram_window = QWidget()
        self.histogram_window.setWindowTitle('Histogram')
        self.histogram_scene = QGraphicsScene()
        self.histogram_view = QGraphicsView(self.histogram_scene)

    def assign_value(self, chanel, image, scene, graphics_view):
        self.channel = chanel
        self.image = image
        self.scene = scene
        self.graphics_view = graphics_view

    def draw_histograms(self):
        channels = self.get_channels()

        x = 0
        y = 0
        bar_width = 2
        bar_spacing = 0

        max_count = self.get_max_count(channels)

        for channel in channels.keys():
            if channel == 'all':
                pixels_brightness = self.get_pixels_brightness_values(channels[channel])
                pixels_brightness_count = self.get_pixels_count(pixels_brightness)
                self.add_histogram(pixels_brightness_count, "Brightness", (x, y), bar_width, 'grey', bar_spacing)
                y += 100

                r_count = self.get_pixels_count(channels['1'])
                g_count = self.get_pixels_count(channels['2'])
                b_count = self.get_pixels_count(channels['3'])

                size = len(r_count)

                pixels_count = [(r_count[i] + g_count[i] + b_count[i]) // 3 for i in range(size)]
            else:
                pixels_count = self.get_pixels_count(channels[channel])

            self.add_histogram(pixels_count, self.channels_titles[channel], (x, y), bar_width,
                               self.channels_colors[channel], bar_spacing, max_count)

            y += 100

        bottom_line = QGraphicsLineItem(x, y - 100, x + bar_width * 256, y - 100)
        self.histogram_scene.addItem(bottom_line)

        row_count = len(channels) + 1 if len(channels) == 4 else 1
        self.histogram_scene.setSceneRect(-51, -150, bar_width * 256 + 102, 100 * row_count + 100)

        histogram_layout = QVBoxLayout(self.histogram_window)
        histogram_layout.addWidget(self.histogram_view)

        self.histogram_window.show()

    def add_histogram(self, pixels_numbers, histogram_title, pos, bar_width, color, bar_spacing, max_count=-1):
        x, y = pos[0], pos[1]

        top_line = QGraphicsLineItem(x - 1, y - 100, x + bar_width * 256 + 1, y - 100)
        left_line = QGraphicsLineItem(x - 1, y, x - 1, y - 100)
        right_line = QGraphicsLineItem(x + bar_width * 256 + 1, y, x + bar_width * 256 + 1, y - 100)
        self.histogram_scene.addItem(top_line)
        self.histogram_scene.addItem(left_line)
        self.histogram_scene.addItem(right_line)

        max_count_value = max_count if max_count != -1 else max(pixels_numbers)

        title = QGraphicsTextItem(histogram_title)
        title.setPos(x, y - 100)
        self.histogram_scene.addItem(title)

        for value in pixels_numbers:
            bar_height = (value / max_count_value) * 75
            rect_item = QGraphicsRectItem(x, y, bar_width, -bar_height)
            rect_item.setBrush(QColor(color))
            self.histogram_scene.addItem(rect_item)
            x += bar_width + bar_spacing

    def get_pixels_brightness_values(self, pixels):
        pixels_brightness = []
        for i in range(0, len(pixels), 3):
            r = pixels[i]
            g = pixels[i + 1]
            b = pixels[i + 2]
            brightness = int((0.2126 * r) + (0.7152 * g) + (0.0722 * b))
            pixels_brightness.append(brightness)
        return pixels_brightness

    def get_channels(self):
        channels = {}
        if self.channel == 'all':
            channels['all'] = self.image.pixels
            channels['1'] = self.image.canal(0).to_gray().pixels
            channels['2'] = self.image.canal(1).to_gray().pixels
            channels['3'] = self.image.canal(2).to_gray().pixels
        else:
            channels[self.channel] = self.image.canal(int(ord(self.channel) - ord('1'))).to_gray().pixels
        return channels

    def get_pixels_count(self, pixels):
        pixels_count = {}
        for i in range(0, 256):
            pixels_count[i] = 0
        for pixel in pixels:
            pixels_count[pixel] += 1
        sorted_keys = sorted(pixels_count.keys())
        sorted_values = [pixels_count[el] for el in sorted_keys]
        return sorted_values

    def get_max_count(self, channels):
        if 'all' in channels.keys():
            r_count = self.get_pixels_count(channels['1'])
            g_count = self.get_pixels_count(channels['2'])
            b_count = self.get_pixels_count(channels['3'])
            max_r, max_g, max_b = max(r_count), max(g_count), max(b_count)
            return max(max_r, max_g, max_b)

        count = self.get_pixels_count(channels[self.channel])
        return max(count)
