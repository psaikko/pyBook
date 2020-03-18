from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator
import book
import sys
import io
import PyPDF2

class MainWindow(QWidget):

    def select_open_file(self):
        (path, _) = QFileDialog.getOpenFileName(self, caption="Open Document", directory=".", filter="*.pdf")
        if path:
            self.input_file = path
            self.open_txt.setText(path)
            self.save_btn.setEnabled(True)

    def select_save_file(self):
        (path, _) = QFileDialog.getSaveFileName(self, caption="Save As", directory=".", filter="*.pdf")
        if path:
            if not path.endswith(".pdf"): 
                path += ".pdf"

            infile = open(self.input_file, "rb")
            outfile = open(path, "wb")
            section_size = int(self.section_size_txt.text())

            reader = PyPDF2.PdfFileReader(infile)
            n_content_pages = reader.getNumPages()
            order = book.page_order(n_content_pages, section_size)

            padded_stream = io.BytesIO()
            ordered_stream = io.BytesIO()

            book.apply_padding(infile, padded_stream, len(order))
            book.reorder_pages(padded_stream, ordered_stream, order)
            book.merge_sheets(ordered_stream, outfile)

            self.close()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.section_size = 4
        self.input_file = None

        self.setWindowTitle("pyBook")
        
        self.open_btn = QPushButton("Open")
        self.open_btn.clicked.connect(self.select_open_file)

        self.open_txt = QLineEdit("")
        self.open_txt.setReadOnly(True)
        self.open_txt.setDisabled(True)

        open_row = QHBoxLayout()
        open_row.addWidget(self.open_btn)
        open_row.addWidget(self.open_txt)

        self.section_size_lbl = QLabel("Sheets per section:")
        self.section_size_txt = QLineEdit(str(self.section_size))
        self.section_size_validator = QIntValidator()
        self.section_size_validator.setBottom(1)
        self.section_size_txt.setValidator(self.section_size_validator)

        section_size_row = QHBoxLayout()
        section_size_row.addWidget(self.section_size_lbl)
        section_size_row.addWidget(self.section_size_txt)

        self.save_btn = QPushButton("Create")
        self.save_btn.clicked.connect(self.select_save_file)
        self.save_btn.setEnabled(False)

        layout = QVBoxLayout()
        layout.addLayout(open_row)
        layout.addLayout(section_size_row)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
