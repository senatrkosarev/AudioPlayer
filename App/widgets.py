import webbrowser

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget
from tinytag import TinyTag

from resources.ui.VolumeWidget import Ui_VolumeWidget
from resources.ui.PropertiesWidget import Ui_PropertiesWidget
from resources.ui.AboutWidget import Ui_AboutWidget


class PropertiesWidget(QWidget, Ui_PropertiesWidget):
    def __init__(self, x, y, height, file_path):
        super(PropertiesWidget, self).__init__()
        self.setupUi(self)
        self.setGeometry(x, y, self.width(), height)
        self.file_path = file_path
        self.load_properties()

    def load_properties(self):
        tag = TinyTag.get(self.file_path)

        title = tag.title
        authors = tag.artist
        album = tag.album
        genre = tag.genre
        year = tag.year
        length = str(f'{int(tag.duration / 60)}:{int(tag.duration % 60) + 1:02}')

        self.title_text.setText(title)
        try:
            self.author_text.setText(', '.join(authors.split('/')))
        except AttributeError:
            pass
        self.album_text.setText(album)
        self.genre_text.setText(genre)
        self.year_text.setText(year)
        self.length_text.setText(length)
        self.file_text.setText(self.file_path)


class VolumeWidget(QWidget, Ui_VolumeWidget):
    def __init__(self, player, x, y, width, color):
        super(VolumeWidget, self).__init__()
        self.setupUi(self)
        self.setGeometry(x, y, width, self.height())
        self.setStyleSheet(f'background-color: rgb({color.red()}, {color.green()}, {color.blue()});')

        self.player = player
        self.volume_slider.setValue(self.player.volume())
        self.volume_slider.valueChanged.connect(self.change_volume)
        QtCore.QTimer.singleShot(10000, self.close)

    def change_volume(self, value):
        self.player.setVolume(value)


class AboutWidget(QWidget, Ui_AboutWidget):
    def __init__(self):
        super(AboutWidget, self).__init__()
        self.setupUi(self)
        self.setFixedSize(430, 330)
        self.github_button.clicked.connect(lambda: webbrowser.open('https://github.com/skosarex/AudioPlayer'))