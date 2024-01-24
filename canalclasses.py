from GrayImage import GrayImage


class bytecanal:
    def __init__(self, width, height, pixels: bytearray):
        self.width = width
        self.height = height
        self.pixels = pixels

    def to_gray(self):
        return GrayImage(self.width, self.height, self.pixels)

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(f'{self.width} {self.height}\n'.encode())
            file.write(self.pixels)

    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'rb') as file:
            width, height = map(int, file.readline().decode().split())
            return bytecanal(width, height, bytearray(file.read()))


class zerotoonecanal:
    def __init__(self, width, height, pixels):
        self.width = width
        self.height = height
        self.pixels = pixels
        self.gray_pixels = None

    def to_gray(self):
        if self.gray_pixels is None:
            self.gray_pixels = bytearray(len(self.pixels))
            for i in range(0, len(self.pixels)):
                self.gray_pixels[i] = int(self.pixels[i] * 255)
        return GrayImage(self.width, self.height, self.gray_pixels)

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(f'{self.width} {self.height}\n'.encode())
            write_pixels = bytearray(len(self.pixels))
            for i in range(0, len(self.pixels)):
                write_pixels[i] = int(self.pixels[i] * 255)
            file.write(write_pixels)

    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'rb') as file:
            width, height = map(int, file.readline().decode().split())
            byte_pixels = bytearray(file.read())
            pixels = [0] * len(byte_pixels)
            for i in range(0, len(byte_pixels)):
                pixels[i] = byte_pixels[i] / 255
            return zerotoonecanal(width, height, pixels)


class huecanal:
    def __init__(self, width, height, pixels):
        self.width = width
        self.height = height
        self.pixels = pixels
        self.gray_pixels = None

    def to_gray(self):
        if self.gray_pixels is None:
            self.gray_pixels = bytearray(len(self.pixels))
            for i in range(0, len(self.pixels)):
                self.gray_pixels[i] = int(self.pixels[i] * 255 / 360)
        return GrayImage(self.width, self.height, self.gray_pixels)

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(f'{self.width} {self.height}\n'.encode())
            write_pixels = bytearray(len(self.pixels))
            for i in range(0, len(self.pixels)):
                write_pixels[i] = int(self.pixels[i] * 255 / 360)
            file.write(write_pixels)

    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'rb') as file:
            width, height = map(int, file.readline().decode().split())
            byte_pixels = bytearray(file.read())
            pixels = [0] * len(byte_pixels)
            for i in range(0, len(byte_pixels)):
                pixels[i] = byte_pixels[i] / 255 * 360
            return huecanal(width, height, pixels)


class halftohalfcanal:
    def __init__(self, width, height, pixels):
        self.width = width
        self.height = height
        self.pixels = pixels
        self.gray_pixels = None

    def to_gray(self):
        if self.gray_pixels is None:
            self.gray_pixels = bytearray(len(self.pixels))
            for i in range(0, len(self.pixels)):
                self.gray_pixels[i] = int((self.pixels[i] + 0.5) * 255)
        return GrayImage(self.width, self.height, self.gray_pixels)

    def write_to_file(self, file_path):
        with open(file_path, 'wb') as file:
            file.write(f'{self.width} {self.height}\n'.encode())
            write_pixels = bytearray(len(self.pixels))
            for i in range(0, len(self.pixels)):
                write_pixels[i] = int((self.pixels[i] + 0.5) * 255)
            file.write(write_pixels)

    @staticmethod
    def read_from_file(file_path):
        with open(file_path, 'rb') as file:
            width, height = map(int, file.readline().decode().split())
            byte_pixels = bytearray(file.read())
            pixels = [0] * len(byte_pixels)
            for i in range(0, len(byte_pixels)):
                pixels[i] = byte_pixels[i] / 255 - 0.5
            return halftohalfcanal(width, height, pixels)