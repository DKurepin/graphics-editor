from PyQt6.QtGui import QImage, QPixmap
import os
from ColorSpaces import ColorSpace
from imageclasses import RGBImage



class Pixmap:
    def __init__(self, width, height, pixel_width, pixels: bytearray):
        self.width = width
        self.height = height
        self.pixel_width = pixel_width
        self.pixels = pixels

    def __getitem__(self, indexes):
        if isinstance(indexes, int):
            return self.pixels[self.pixel_width * indexes * self.width: self.pixel_width * self.width * (indexes + 1)]

        if len(indexes) > 2:
            raise IndexError("Invalid number of indexes. Expected 1 or 2.")

        row, col = indexes
        index = self.pixel_width * ((row * self.width) + col)
        return self.pixels[index:index + self.pixel_width]


class PNMImage:
    def __init__(self, image_type, width, height, max_value, pixels):
        self.image_type = image_type
        self.width = width
        self.height = height
        self.max_value = max_value
        self.pixmap = Pixmap(width, height, 3 if image_type == 'P6' else 1, pixels)

    @staticmethod
    def read_from_file(file_path):
        if not os.path.isfile(file_path):
            print(f"File {file_path} does not exist!")
            return
        with open(file_path, 'rb') as file:

            magic_number = file.readline().decode().rstrip('\n')
            width, height = map(int, file.readline().decode().split())
            max_value = int(file.readline().decode().rstrip('\n'))

            if width < 0 or height < 0:
                raise Exception('Width and height values must be positive!')

            if magic_number != 'P6' and magic_number != 'P5':
                raise Exception('Invalid PNM image format')

            pixels = file.read()

            if len(pixels) != width * height * (3 if magic_number == 'P6' else 1):
                raise Exception('Invalid size')

            return PNMImage(magic_number, width, height, max_value, pixels)

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(f'{self.image_type}\n'.encode())
            file.write(f'{self.width} {self.height}\n'.encode())
            file.write(f'{self.max_value}\n'.encode())
            file.write(self.pixmap.pixels)

    def to_qimage(self):
        image_format = QImage.Format.Format_RGB888 if self.image_type == 'P6' else QImage.Format.Format_Indexed8
        qimage = QImage(self.pixmap.pixels, self.width, self.height, image_format)
        return qimage

    def to_qpixmap(self):
        qimage = self.to_qimage()
        qpixmap = QPixmap.fromImage(qimage)
        return qpixmap

    def p6_to_p5(self):
        if self.image_type != 'P6':
            raise RuntimeError('Image is not PNM P6')

        pixels = bytearray(self.width * self.height)
        for i in range(self.height):
            row = self.pixmap[i]
            for j in range(self.width):
                rgb_pixel = row[3 * j: 3 * j + 3]
                pixels[i * self.width + j] = (rgb_pixel[0] + rgb_pixel[1] + rgb_pixel[2]) // 3

        return PNMImage('P5', self.width, self.height, self.max_value, pixels)

    def to_rgb(self):
        return RGBImage(self.width, self.height, self.pixmap.pixels)
