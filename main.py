import sys

from PyQt5 import uic
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setMinimumSize(300, 150)
        uic.loadUi('D:\\dev\\Python\\Projects\\Audioplayer\\resources\\ui\\MainWindow.ui', self)
        self.file_path = None
        self.player = QMediaPlayer()
        self.play_button.clicked.connect(self.play)
        self.prev_button.clicked.connect(self.pause)
        self.next_button.clicked.connect(self.resume)
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.open_file_action.triggered.connect(self.open_file)
        self.error_label.hide()

    def play(self):
        if self.file_path is None:
            self.error_label.show()
        else:
            self.error_label.hide()
            url = QUrl.fromLocalFile(self.file_path)
            self.player.setMedia(QMediaContent(url))
            self.player.play()

    def pause(self):
        self.player.pause()

    def resume(self):
        self.player.play()

    def change_volume(self, value):
        print(value)
        self.player.setVolume(value)

    def open_file(self):
        self.file_path = \
            QFileDialog.getOpenFileName(self, 'Select audio file', '', 'Audio (*.mp3 *.wav);;All files (*)')[0]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
