import webbrowser

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from tinytag import TinyTag

from App.database import AudiofileDao
from App.resources.ui.PropertiesWidget import Ui_PropertiesWidget
from App.resources.ui.VolumeWidget import Ui_VolumeWidget
from App.resources.ui.AboutWidget import Ui_AboutWidget
from App.resources.ui.FavoriteWidget import Ui_FavoriteWidget
from App.__version__ import __version__


class PropertiesWidget(QWidget, Ui_PropertiesWidget):
    def __init__(self, x, y, height, file_path):
        super(PropertiesWidget, self).__init__()
        self.setupUi(self)

        self.setGeometry(x, y, self.width(), height)

        self.file_path = file_path
        self.load_properties()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(QRect(30, 30, self.width() - 60, self.height() - 60), 30.0, 30.0)
        painter.end()

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

        self.version_label.setText(__version__)
        self.github_button.clicked.connect(lambda: webbrowser.open('https://github.com/skosarex/AudioPlayer'))


class FavoriteWidget(QWidget, Ui_FavoriteWidget):
    def __init__(self, main_widget, user_id):
        super(FavoriteWidget, self).__init__()
        self.setupUi(self)

        self.dao = AudiofileDao()
        self.main_widget = main_widget
        self.user_id = user_id
        self.load_table()

        self.reload_button.clicked.connect(self.load_table)
        self.play_button.clicked.connect(self.play_favorites)
        self.delete_button.clicked.connect(self.delete_all)

    def get_data(self):
        return self.dao.get_all(self.user_id)

    def load_table(self):
        data = self.get_data()

        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['title', 'author'])
        self.table.setRowCount(len(data))
        for row in range(len(data)):
            for col in range(2):
                self.table.setItem(row, col, QTableWidgetItem(str(data[row][col + 1])))

    def play_favorites(self):
        new_playlist = []
        for song in self.get_data():
            new_playlist.append(song[3])
        if not new_playlist:
            self.main_widget.set_error('Error: No favorite music!')
        else:
            self.main_widget.playlist = new_playlist
            self.main_widget.cursor = 0
            self.main_widget.play()
            self.main_widget.update_metadata()

    def delete_all(self):
        for song in self.get_data():
            self.dao.delete(song[3])
        self.load_table()
