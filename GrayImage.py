import importlib

from PyQt6.QtGui import QPixmap, QImage


class GrayImage:
    def __init__(self, width, height, pixels):
        self.width = width
        self.height = height
        self.pixels = pixels

    def to_qpixmap(self):
        return QPixmap.fromImage(QImage(self.pixels, self.width, self.height, QImage.Format.Format_Indexed8))

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write('P5\n'.encode())
            file.write(f'{self.width} {self.height}\n'.encode())
            file.write('255\n'.encode())
            file.write(self.pixels)

    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'rb') as file:
            magic_number = file.readline().decode().rstrip('\n')
            width, height = map(int, file.readline().decode().split())
            max_val = file.readline().decode().rstrip('\n')
            return GrayImage(width, height, bytearray(file.read()))

    def to_rgb(self):
        pixel_data_p6 = bytearray(len(self.pixels) * 3)
        for i in range(0, len(self.pixels)):
            val = self.pixels[i]
            pixel_data_p6[3 * i] = val
            pixel_data_p6[3 * i + 1] = val
            pixel_data_p6[3 * i + 2] = val
        return importlib.import_module('imageclasses').RGBImage(self.width, self.height, pixel_data_p6)
