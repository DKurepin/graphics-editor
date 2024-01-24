import sys

from ColorSpaces import ColorSpace
from PyQt6.QtWidgets import *

from ContrastCorrectionView import ContrastCorrectionView
from Filters import ThresholdFilter, OtsuThresholdFilter, MedianFilter, GaussFilter, BoxBlurFilter, \
    UnsharpMaskingFilter, CASFilter, SobelFilter, CannyEdgeDetector
from HistogramView import HistogramView
from PNMImage import PNMImage
from imageclasses import *
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt
from GammaCorrectionView import GammaCorrectionView
from LineDrawingView import *
from DitheringView import *
from GradientView import *
from ScalingImageView import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image = None
        self.setWindowTitle("Graphic Editor")
        self.layout = QVBoxLayout()

        self.filter = None
        self.filters_button = QPushButton("Filters")
        self.filters_button.clicked.connect(self.show_filters)
        self.filters_button.setEnabled(False)
        self.filters_options = QComboBox()
        self.filters_options.addItems(
            ["None", "Threshold filter", "Otsu Threshold filter", "Median filter",
             "Gauss filter", "Box Blur filter", "Unsharp Masking filter",
             "CAS filter", "Sobel filter", "Canny Edge detector"])
        self.filters_options.currentIndexChanged.connect(self.handle_filter_change)
        self.filters_options.hide()
        self.filters_options.setObjectName("Apply filters")
        self.layout.addWidget(self.filters_button)
        self.layout.addWidget(self.filters_options)

        self.contrast_correction_button = QPushButton("Correct contrast")
        self.contrast_correction_view = ContrastCorrectionView()
        self.contrast_correction_button.clicked.connect(self.apply_contrast_correction)
        self.contrast_correction_button.setEnabled(False)

        self.draw_histogram_button = QPushButton("Draw histogram")
        self.histogram_view = HistogramView()
        self.draw_histogram_button.clicked.connect(self.show_histogram_view)
        self.draw_histogram_button.setEnabled(False)

        self.draw_line_button = QPushButton("Draw Line")
        self.line_drawing_view = LineDrawingView()
        self.line_drawing_view.set_window()
        self.draw_line_button.clicked.connect(self.show_line_drawing_view)
        self.draw_line_button.setEnabled(False)
        self.draw_line_button.setObjectName("Draw Line")

        self.scene = MyGraphicsScene()
        self.scene.set_line_drawing_view(self.line_drawing_view)
        self.graphics_view = MyGraphicsView(self.scene)
        self.setCentralWidget(self.graphics_view)

        self.toolbar = QToolBar("Main toolbar")

        self.save_button = QPushButton("Save image")
        self.save_button.clicked.connect(self.save_image_file_dialog)
        self.save_button.setEnabled(False)
        self.save_button.setObjectName("Save image")

        self.open_custom_format_button = QPushButton("Open image")
        self.open_custom_format_button.clicked.connect(self.load_image_file_dialog)
        self.open_custom_format_button.setObjectName("Open image")

        self.change_color_space = QPushButton("Change color space")
        self.change_color_space.clicked.connect(self.show_color_space_options)
        self.color_space_options = QComboBox()
        self.color_space_options.addItems(["RGB", "HSL", "HSV", "YCbCr601", "YCbCr709", "YCoCg", "CMY"])
        self.color_space_mode = 'RGB'
        self.color_space_options.currentIndexChanged.connect(self.handle_color_space_change)
        self.color_space_options.hide()
        self.change_color_space.setObjectName("Change color space")
        self.layout.addWidget(self.change_color_space)
        self.layout.addWidget(self.color_space_options)

        self.change_canals_button = QPushButton("Change channels")
        self.change_canals_button.clicked.connect(self.show_canals_options)
        self.canals_options = QComboBox()
        self.canals_options.addItems(["all", "1", "2", "3"])
        self.canals_mode = 'all'
        self.canals_options.currentIndexChanged.connect(self.handle_canals_change)
        self.canals_options.hide()
        self.change_canals_button.setObjectName("Change canals")
        self.layout.addWidget(self.change_canals_button)
        self.layout.addWidget(self.canals_options)
        self.setLayout(self.layout)

        self.gamma_correction_view = GammaCorrectionView()
        self.gamma_correction_view.set_window()
        self.gamma_correction_button = QPushButton("Gamma Correction")
        self.gamma_correction_button.clicked.connect(self.show_gamma_correction_options)
        self.gamma_correction_view.setObjectName("Gamma Correction")
        self.gamma_correction_button.setEnabled(False)

        self.dithering_view = DitheringView()
        self.dithering_view.set_window()
        self.dithering_button = QPushButton("Dithering")
        self.dithering_button.clicked.connect(self.show_dithering_options)
        self.dithering_view.setObjectName("Dithering")
        self.dithering_button.setEnabled(False)

        self.gradient_view = GradientView()
        self.gradient_view.set_window()
        self.gradient_view.assign_value(self.scene, self.graphics_view)
        self.gradient_button = QPushButton("Gradient")
        self.gradient_button.clicked.connect(self.show_gradient_options)
        self.gradient_view.setObjectName("Gradient")

        self.scaling_image_view = ScalingImageView()
        self.scaling_image_view.set_window()
        self.scaling_button = QPushButton("Scaling")
        self.scaling_button.clicked.connect(self.show_scaling_image_view)
        self.scaling_image_view.setObjectName("Scaling")

        self.toolbar.addWidget(self.filters_button)
        self.toolbar.addWidget(self.open_custom_format_button)
        self.toolbar.addWidget(self.save_button)
        self.toolbar.addWidget(self.change_color_space)
        self.toolbar.addWidget(self.change_canals_button)
        self.toolbar.addWidget(self.scaling_button)
        self.toolbar.addWidget(self.gamma_correction_button)
        self.toolbar.addWidget(self.draw_line_button)
        self.toolbar.addWidget(self.dithering_button)
        self.toolbar.addWidget(self.gradient_button)
        self.toolbar.addWidget(self.draw_histogram_button)
        self.toolbar.addWidget(self.contrast_correction_button)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.setMinimumSize(600, 400)

    def load_image_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.fileSelected.connect(self.load_image)
        file_dialog.exec()

    def load_image(self, file_path):
        self.color_space_options.setEnabled(True)
        try:
            self.image = type(ColorSpace[f'{self.color_space_mode}'].value[0]).read_from_file(file_path)
        except Exception as e:
            print(e)
            return

        self.enable_gray_mode(type(self.image).__name__ == "GrayImage")
        self.draw()
        self.save_button.setEnabled(True)
        if type(self.image).__name__ != "GrayImage":
            self.set_buttons_state(True)
        else:
            if self.gamma_correction_view.isEnabled():
                self.gamma_correction_view.close_window()
            self.set_buttons_state(False)
        self.filters_button.setEnabled(True)
        self.set_views_state(False)
        self.draw_histogram_button.setEnabled(True)

    def draw(self):
        if self.image is None:
            return
        if self.canals_options.currentText() != "all":
            if self.gamma_correction_view.isEnabled():
                self.gamma_correction_view.close_window()
            self.gamma_correction_button.setEnabled(False)
            self.line_drawing_view.setEnabled(False)
            self.current_canal = self.image.canal(int(self.canals_options.currentText()) - 1)
            self.draw_canal()
        else:
            self.draw_image()
            self.set_buttons_state(True)

    def enable_gray_mode(self, flag=True):
        self.color_space_options.setEnabled(not flag)
        self.canals_options.setEnabled(not flag)
        self.canals_options.setCurrentText("all")
        self.draw()

    def draw_image(self):
        self.scene = MyGraphicsScene()
        self.scene.set_line_drawing_view(self.line_drawing_view)
        self.graphics_view.setScene(self.scene)
        self.scene.addPixmap(self.image.to_qpixmap())
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def save_image_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_name, _ = file_dialog.getSaveFileName(self, "Save File", "", "All files (*)")
        if file_name:
            self.save_image(file_name)

    def save_image(self, file_path):
        if self.canals_options.currentText() != "all":
            self.current_canal.to_gray().write_to_file(file_path)
        else:
            image = self.get_current_image()
            image.write_to_file(file_path)

    def get_current_image(self):
        if self.image is None:
            return
        if self.scaling_image_view.changed:
            image = RGBImage(self.scaling_image_view.width, self.scaling_image_view.height,
                             bytes(self.scaling_image_view.current_pixels))
        elif self.contrast_correction_view.changed:
            image = RGBImage(self.image.width, self.image.height, bytes(self.contrast_correction_view.current_pixels))
        elif self.line_drawing_view.changed:
            image = RGBImage(self.image.width, self.image.height, bytes(self.line_drawing_view.current_pixels))
        elif self.gamma_correction_view.changed:
            image = RGBImage(self.image.width, self.image.height, bytes(self.gamma_correction_view.current_pixels))
        elif self.gradient_view.changed:
            image = RGBImage(self.gradient_view.width, self.gradient_view.height,
                             bytes(self.gradient_view.current_pixels))
        elif self.dithering_view.changed:
            image = RGBImage(self.image.width, self.image.height, bytes(self.dithering_view.current_pixels))
        else:
            image = self.image
        return image

    def handle_filter_change(self):
        self.filters_options.hide()
        selected_option = self.filters_options.currentText()
        print(selected_option)
        if selected_option == "Threshold filter":
            self.filter = ThresholdFilter()
        elif selected_option == "Otsu Threshold filter":
            self.filter = OtsuThresholdFilter()
        elif selected_option == "Median filter":
            self.filter = MedianFilter()
        elif selected_option == "Gauss filter":
            self.filter = GaussFilter()
        elif selected_option == "Box Blur filter":
            self.filter = BoxBlurFilter()
        elif selected_option == "Unsharp Masking filter":
            self.filter = UnsharpMaskingFilter()
        elif selected_option == "CAS filter":
            self.filter = CASFilter()
        elif selected_option == "Sobel filter":
            self.filter = SobelFilter()
        elif selected_option == "Canny Edge detector":
            self.filter = CannyEdgeDetector()
        else:
            return
        self.filter.assign_values(self.get_current_image(), self.scene, self.graphics_view)
        self.filter.set_window()
        self.filter.show()

    def show_filters(self):
        self.filters_options.show() if not self.filters_options.isVisible() else self.filters_options.hide()
    def set_views_state(self, state):
        self.contrast_correction_view.changed = state
        self.line_drawing_view.changed = state
        self.gamma_correction_view.changed = state
        self.gradient_view.changed = state
        self.dithering_view.changed = state

    def set_buttons_state(self, state):
        self.contrast_correction_button.setEnabled(state)
        self.draw_line_button.setEnabled(state)
        self.gamma_correction_button.setEnabled(state)
        self.gradient_button.setEnabled(state)
        self.dithering_button.setEnabled(state)

    def resizeEvent(self, event):
        if self.scene is not None:
            self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def show_color_space_options(self):
        self.color_space_options.show() if not self.color_space_options.isVisible() else self.color_space_options.hide()

    def handle_color_space_change(self):
        self.color_space_options.hide()
        selected_option = self.color_space_options.currentText()
        self.color_space_mode = selected_option
        if self.image is None:
            return
        name = self.image.__class__.__name__[:-5]
        if name == 'PNM' and self.image_type == 'P5':
            return
        self.image = self.image.to_rgb().convert_to(selected_option)
        self.draw()
        self.save_button.setEnabled(True)

    def show_canals_options(self):
        self.canals_options.show() if not self.canals_options.isVisible() else self.canals_options.hide()

    def show_dithering_options(self):
        image = self.get_current_image()
        if image is None:
            return
        image = image.to_rgb()
        self.dithering_view.assign_value(image, self.scene, self.graphics_view,
                                         self.gamma_correction_view)
        self.dithering_view.show()

    def show_line_drawing_view(self):
        image = self.get_current_image()
        if image is None:
            return
        image = image.to_rgb()
        self.line_drawing_view.assign_value(image, self.scene, self.graphics_view,
                                            self.findChildren(QPushButton), self.gamma_correction_view)
        self.scene.set_line_drawing_view(self.line_drawing_view)
        self.line_drawing_view.show()

    def show_scaling_image_view(self):
        image = self.get_current_image()
        if image is None:
            return
        self.scaling_image_view.assign_value(self.image.to_rgb(), self.scene, self.graphics_view)
        self.scaling_image_view.show()

    def show_histogram_view(self):
        image = self.get_current_image()
        if image is None:
            return
        self.histogram_view.assign_value(self.canals_mode, image, self.scene, self.graphics_view)
        self.histogram_view.initUi()
        self.histogram_view.draw_histograms()

    def apply_contrast_correction(self):
        image = self.get_current_image()
        self.contrast_correction_view.assign_value(image, self.scene, self.graphics_view, self.canals_mode, self.color_space_mode)
        self.contrast_correction_view.set_window()
        self.contrast_correction_view.show()

    def handle_canals_change(self):
        self.canals_options.hide()
        selected_option = self.canals_options.currentText()
        self.canals_mode = selected_option
        if self.image is None:
            return
        name = self.image.__class__.__name__[:-5]
        if name == 'PNM' and self.image_type == 'P5':
            return
        self.draw()

    def show_gamma_correction_options(self):
        self.gamma_correction_view.show()

    def show_gradient_options(self):
        self.gradient_view.show()
        self.save_button.setEnabled(True)
        self.draw_histogram_button.setEnabled(True)

    def draw_canal(self):
        self.graphics_view.setScene(self.scene)
        self.scene.addPixmap(self.current_canal.to_gray().to_qpixmap())
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def closeEvent(self, event):
        self.color_space_options.hide()
        self.canals_options.hide()
        self.gamma_correction_view.close_window()
        self.line_drawing_view.close()
        super().closeEvent(event)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
