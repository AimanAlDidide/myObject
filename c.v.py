import sys  
import cv2 
import numpy as np  
from PyQt6.QtWidgets import (QApplication, QLabel, QPushButton, QFileDialog, 
                             QComboBox, QGridLayout, QSizePolicy, QWidget)  
from PyQt6.QtGui import QPixmap, QImage, QPalette, QColor, QPainter, QPen 
from PyQt6.QtCore import Qt, QPoint 

class ImageEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Editor")  
        self.setGeometry(100, 100, 900, 600)

        # إعداد خلفية النافذة
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))  # خلفية رمادية
        self.setPalette(palette)

        # المتغيرات الرئيسية
        self.image = None  # الصورة المحملة
        self.original_image = None  # الاحتفاظ بنسخة من الصورة الأصلية
        self.drawing = False  # تتبع حالة الرسم
        self.last_point = QPoint()  # تخزين إحداثيات النقطة الأخيرة للرسم

        # عنصر لعرض الصورة
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background-color: white; border: 2px solid gray;")
        self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

       
        self.btn_open = QPushButton("Open Image")
        self.btn_save = QPushButton("Save Image")
        self.btn_grayscale = QPushButton("Grayscale")
        self.btn_mirror = QPushButton("Mirror")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Select Filter", "Blur", "Edge Detection", "Sharpen", "Sepia", "Original View"])

        # ربط الأزرار بالوظائف
        self.btn_open.clicked.connect(self.open_image)
        self.btn_save.clicked.connect(self.save_image)
        self.btn_grayscale.clicked.connect(self.convert_to_grayscale)
        self.btn_mirror.clicked.connect(self.mirror_image)
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)

        # تنسيق الأزرار
        button_style = "background-color: black; color: white; font-size: 14px; padding: 10px; border-radius: 5px;"
        for btn in [self.btn_open, self.btn_save, self.btn_grayscale, self.btn_mirror]:
            btn.setStyleSheet(button_style)
        self.filter_combo.setStyleSheet(button_style)

        # تصميم الواجهة
        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0, 6, 1)
        layout.addWidget(self.btn_open, 0, 1)
        layout.addWidget(self.btn_save, 1, 1)
        layout.addWidget(self.btn_grayscale, 2, 1)
        layout.addWidget(self.btn_mirror, 3, 1)
        layout.addWidget(self.filter_combo, 4, 1)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)
        self.setLayout(layout)

    # تحميل الصورة
    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.image = cv2.imread(file_path)
            if self.image is None:
                print("Error: Failed to load image.")
                return
            self.original_image = self.image.copy()  # حفظ النسخة الأصلية
            self.image = self.resize_to_fit(self.image)  # تعديل الحجم
            self.display_image()

    # حفظ الصورة
    def save_image(self):
        if self.image is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
            if file_path:
                cv2.imwrite(file_path, self.image)

    # تحويل الصورة إلى تدرج رمادي
    def convert_to_grayscale(self):
        if self.image is not None:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.display_image()

    # عكس الصورة أفقيًا
    def mirror_image(self):
        if self.image is not None:
            self.image = cv2.flip(self.image, 1)
            self.display_image()

    # تطبيق الفلاتر
    def apply_filter(self):
        if self.image is None:
            return

        filter_name = self.filter_combo.currentText()
        if filter_name == "Blur":
            self.image = cv2.GaussianBlur(self.image, (15, 15), 0)
        elif filter_name == "Edge Detection":
            self.image = cv2.Canny(self.image, 100, 200)
        elif filter_name == "Sharpen":
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            self.image = cv2.filter2D(self.image, -1, kernel)
        elif filter_name == "Sepia":
            kernel = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
            self.image = cv2.transform(self.image, kernel)
        elif filter_name == "Original View":
            self.image = self.original_image.copy()
        
        self.display_image()

    # وظيفة الرسم على الصورة
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.image is not None:
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing and self.image is not None:
            painter = QPainter(self.image)
            painter.setPen(QPen(Qt.GlobalColor.red, 3, Qt.PenStyle.SolidLine))
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.display_image()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    # تغيير حجم الصورة لتناسب العرض
    def resize_to_fit(self, image):
        height, width = image.shape[:2]
        aspect_ratio = width / height
        new_width = 500
        new_height = int(new_width / aspect_ratio)
        return cv2.resize(image, (new_width, new_height))

    # عرض الصورة في الواجهة
    def display_image(self):
        if self.image is None:
            return

        image = self.image.copy()
        if len(image.shape) == 2:
            qformat = QImage.Format.Format_Grayscale8
        else:
            qformat = QImage.Format.Format_RGB888
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        height, width = image.shape[:2]
        bytes_per_line = width * 3
        qimg = QImage(image.data, width, height, bytes_per_line, qformat)
        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

# تشغيل التطبيق
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageEditor()
    window.show()
    sys.exit(app.exec())
