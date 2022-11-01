import sys

from PyQt5 import uic
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi('resources\\ui\\MainWindow.ui', self)
        self.setMinimumSize(420, 540)
        self.title_label.hide()
        self.author_label.hide()
        self.image.setPixmap(QPixmap.fromImage(QImage('resources\\default.png')))

        self.file_path = None
        self.player = QMediaPlayer()

        self.main_button.clicked.connect(self.invoke_play_function)
        self.like_button.clicked.connect(self.sizes)
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.open_file_action.triggered.connect(self.open_file)
        self.error_label.hide()

    def invoke_play_function(self):
        if self.file_path is None:
            self.error_label.show()
        else:
            self.error_label.hide()
            state = self.player.state()
            if state == QMediaPlayer.StoppedState:
                self.play()
                self.load_metadata()
                self.load_metadata()
                print('try 2 times')
            elif state == QMediaPlayer.PlayingState:
                self.pause()
                self.load_metadata()
            elif state == QMediaPlayer.PausedState:
                self.resume()

    def end_of_media(self):
        self.main_button.setIcon(QIcon('resources\\icons\\play.svg'))
        self.file_path = None

    def sizes(self):
        # TODO delete this func later
        w = self.frameGeometry().width()
        h = self.frameGeometry().height()
        self.setWindowTitle(f'{w}, {h}')

    def play(self):
        url = QUrl.fromLocalFile(self.file_path)
        self.player.setMedia(QMediaContent(url))
        self.main_button.setIcon(QIcon('resources\\icons\\pause.svg'))
        self.player.play()

    def pause(self):
        self.player.pause()
        self.main_button.setIcon(QIcon('resources\\icons\\play.svg'))

    def resume(self):
        self.player.play()
        self.main_button.setIcon(QIcon('resources\\icons\\pause.svg'))

    def change_volume(self, value):
        # TODO delete 'print'
        print(value)
        self.player.setVolume(value)

    def open_file(self):
        self.file_path = \
            QFileDialog.getOpenFileName(self, 'Select audio file', '', 'Audio (*.mp3 *.wav);;All files (*)')[0]
        if self.file_path == '':
            self.file_path = None
        self.player.stop()
        self.main_button.setIcon(QIcon('resources\\icons\\play.svg'))

    def load_metadata(self):
        if not self.player.isMetaDataAvailable():
            return

        title = self.player.metaData('Title')
        authors = self.player.metaData('Author')
        image = self.player.metaData('ThumbnailImage')

        if title is None:
            self.title_label.setText(self.file_path[self.file_path.rfind('/') + 1:])
        else:
            self.title_label.setText(title)
        self.title_label.show()

        self.author_label.setText(', '.join(authors) if authors else 'Unknown author')
        self.author_label.show()

        if image is None:
            self.image.setPixmap(QPixmap.fromImage(QImage('resources\\default.png')))
        else:
            self.image.setPixmap(QPixmap.fromImage(image.scaled(420, 420)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
