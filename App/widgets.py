import webbrowser

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from tinytag import TinyTag

from App.database import AudiofileDao
from resources.ui.VolumeWidget import Ui_VolumeWidget
from resources.ui.PropertiesWidget import Ui_PropertiesWidget
from resources.ui.AboutWidget import Ui_AboutWidget
from resources.ui.FavoriteWidget import Ui_FavoriteWidget


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


class FavoriteWidget(QWidget, Ui_FavoriteWidget):
    def __init__(self, main_widget, user_id):
        super(FavoriteWidget, self).__init__()
        self.setupUi(self)
        self.dao = AudiofileDao()
        self.main_widget = main_widget
        self.user_id = user_id
        self.load_table()

        self.reload_button.clicked.connect(self.load_table)
        self.play_button.clicked.connect(self.play)
        self.delete_button.clicked.connect(self.delete_all)

    def get_data(self):
        return self.dao.get_all(self.user_id)

    def load_table(self):
        dao = AudiofileDao()
        data = dao.get_all(self.user_id)

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['id', 'title', 'author', 'path'])
        self.table.setRowCount(len(data))

        for row in range(len(data)):
            for col in range(len(data[0])):
                self.table.setItem(row, col, QTableWidgetItem(str(data[row][col])))

    def play(self):
        new_playlist = []
        for song in self.get_data():
            new_playlist.append(song[3])
        if not new_playlist:
            self.main_widget.set_error('Error: No favorite music!')
            self.error_timer = QtCore.QTimer()
            self.error_timer.start(5000)
            self.error_timer.timeout.connect(lambda: self.main_widget.set_error(None))
        else:
            self.main_widget.playlist = new_playlist
            self.main_widget.play()
            self.main_widget.load_metadata()  # TODO delete this line??

    def delete_all(self):
        for song in self.get_data():
            self.dao.delete(song[3])
