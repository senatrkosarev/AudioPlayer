import sys

from PyQt5 import QtCore, uic
from PyQt5.QtGui import QPixmap, QImage, QIcon, QPalette
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog
from tinytag import TinyTag

from image import find_average_color, save_audio_image
from database import AudiofileDao, UserDao
from resources.ui.MainWindow import Ui_MainWindow
from widgets import VolumeWidget, PropertiesWidget, AboutWidget, FavoriteWidget

PLAY_ICON = QIcon('resources\\icons\\play.svg')
PAUSE_ICON = QIcon('resources\\icons\\pause.svg')
DEFAULT_IMAGE = QImage('resources\\default.png')
NO_FILE_ERROR = 'Error: file not selected!'


class Player(QMainWindow, Ui_MainWindow):
    def __init__(self, user_id):
        super(Player, self).__init__()
        self.setupUi(self)

        self.user_id = user_id
        self.playlist = []
        self.cursor = 0  # current audio index in playlist
        self.player = QMediaPlayer()
        self.audio_dao = AudiofileDao()
        self.timer = QtCore.QTimer(self)
        self.timer.start(1000)

        self.timer.timeout.connect(self.update_slider)
        self.timer.timeout.connect(self.update_time)
        self.player.mediaStatusChanged.connect(self.end_of_media)
        self.main_button.clicked.connect(self.select_func)
        self.like_button.clicked.connect(self.like)
        self.dislike_button.clicked.connect(self.dislike)
        self.volume_button.clicked.connect(self.open_volume_widget)
        self.playlist_button.clicked.connect(self.open_favorites)
        self.open_file_action.triggered.connect(self.open_file)
        self.open_folder_action.triggered.connect(self.open_folder)
        self.properties_action.triggered.connect(self.open_properties_widget)
        self.about_action.triggered.connect(self.open_about_widget)
        self.next_button.clicked.connect(self.next)
        self.prev_button.clicked.connect(self.previous)
        self.song_slider.sliderReleased.connect(self.slider_released)

    def update_slider(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.song_slider.setMinimum(0)
            self.song_slider.setMaximum(self.player.duration())
            self.song_slider.setValue(self.song_slider.value() + 1000)

    def update_time(self):
        pos = self.player.position()
        current_time = str(f'{int(pos / 60000)}:{int((pos / 1000) % 60):02}')
        self.current_time_label.setText(current_time)

    def slider_released(self):
        self.player.setPosition(self.song_slider.value())
        self.update_time()

    def like(self):
        try:
            self.audio_dao.save(self.user_id, self.title_label.text(), self.author_label.text(),
                                self.playlist[self.cursor])
        except IndexError:
            pass

    def dislike(self):
        try:
            self.audio_dao.delete(self.playlist[self.cursor])
        except IndexError:
            pass

    def next(self):
        self.cursor = (self.cursor + 1) % len(self.playlist)
        self.load_metadata()
        self.play()

    def previous(self):
        self.cursor = (self.cursor - 1) % len(self.playlist)
        self.load_metadata()
        self.play()

    def end_of_media(self):
        current_time = self.current_time_label.text()
        end_time = self.end_time_label.text()
        if self.player.state() == QMediaPlayer.StoppedState and current_time[:-1] == end_time[:-1]:
            if len(self.playlist) > 1:
                self.next()
            else:
                self.play()

    def select_func(self):
        """Selects the desired function: play, pause or resume"""
        if not self.playlist:
            self.set_error(NO_FILE_ERROR)
            return
        self.set_error(None)
        state = self.player.state()
        if state == QMediaPlayer.StoppedState:
            self.play()
        elif state == QMediaPlayer.PlayingState:
            self.pause()
        elif state == QMediaPlayer.PausedState:
            self.resume()

    def set_error(self, msg):
        if msg is None:
            self.error_label.hide()
        else:
            self.error_label.setText(msg)
            self.error_label.show()

    def play(self):
        url = QtCore.QUrl(self.playlist[self.cursor])
        self.player.setMedia(QMediaContent(url))
        self.main_button.setIcon(PAUSE_ICON)
        self.player.play()
        self.current_time_label.setText('0:00')
        self.song_slider.setSliderPosition(0)

    def pause(self):
        self.player.pause()
        self.main_button.setIcon(PLAY_ICON)

    def resume(self):
        self.player.play()
        self.main_button.setIcon(PAUSE_ICON)

    def stop(self):
        self.player.stop()
        self.playlist.clear()
        self.main_button.setIcon(PLAY_ICON)

    def open_file(self):
        file_path = \
            QFileDialog.getOpenFileName(self, 'Select audio file', '', 'Audio (*.mp3 *.wav);;All files (*)')[0]
        if file_path == '':
            return

        self.stop()
        self.playlist.append(file_path)
        self.set_error(None)
        self.cursor = 0
        self.load_metadata()

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select folder')
        if folder_path == '':
            return
        self.stop()

        iterator = QtCore.QDirIterator(folder_path, ['*.mp3', '*.wav', '*.ogg'])
        while iterator.hasNext():
            self.playlist.append(iterator.next())

        self.load_metadata()

    def load_metadata(self):
        if len(self.playlist) == 0:
            self.image.setPixmap(QPixmap.fromImage(DEFAULT_IMAGE))
            self.title_label.setText('')
            self.author_label.setText('')
            return

        self.update_slider()
        self.update_time()
        file_path = self.playlist[self.cursor]
        tag = TinyTag.get(file_path, image=True)

        title = tag.title
        if title is None:
            title = file_path[file_path.rfind('/') + 1:]
        if len(title) > 35:
            title = title[0:35] + '...'
        self.title_label.setText(title)
        self.title_label.show()

        authors = tag.artist
        if authors:
            authors = ', '.join(authors.split('/'))
            if len(authors) > 35:
                authors = authors[0:35] + '...'
        self.author_label.setText(authors if authors else 'Unknown author')
        self.author_label.show()

        image = tag.get_image()
        if image is None:
            self.image.setPixmap(QPixmap.fromImage(DEFAULT_IMAGE))
        else:
            save_audio_image(image)
            self.image.setPixmap(QPixmap.fromImage(QImage('resources\\temp.png')))

        duration = str(f'{int(tag.duration / 60)}:{int(tag.duration % 60) + 1:02}')
        self.end_time_label.setText(str(duration))

        self.image.pixmap().toImage().save('resources\\temp.png')
        colors = find_average_color('resources\\temp.png')
        self.setStyleSheet(f'background-color: rgb({colors[0]}, {colors[1]}, {colors[2]});')

    def open_volume_widget(self):
        x = self.x()
        y = self.y() + self.height() + 80
        width = self.width()
        color = self.palette().color(QPalette.Background)
        self.volume_widget = VolumeWidget(self.player, x, y, width, color)
        self.volume_widget.show()

    def open_properties_widget(self):
        if len(self.playlist) == 0:
            self.set_error(NO_FILE_ERROR)
        else:
            self.set_error(None)
            x = self.x() + self.width() + 10
            y = self.y() + 37
            height = self.height()
            file_path = self.playlist[self.cursor]
            self.properties_widget = PropertiesWidget(x, y, height, file_path)
            self.properties_widget.show()

    def open_about_widget(self):
        self.about_widget = AboutWidget()
        self.about_widget.show()

    def open_favorites(self):
        self.favorite_widget = FavoriteWidget(self, self.user_id)
        self.favorite_widget.show()


class LogInDialog(QDialog):
    def __init__(self):
        super(LogInDialog, self).__init__()
        uic.loadUi('resources\\ui\\LogInDialog.ui', self)
        self.dao = UserDao()
        self.error_label.hide()
        self.log_in_button.clicked.connect(self.log_in)

    def log_in(self):
        login = self.login_input.text()
        password = self.pass_input.text()
        id = self.is_user_valid(login, password)
        if id > 0:
            print(id)
            self.player = Player(id)
            self.hide()
            self.player.show()
        else:
            self.error_label.show()

    def is_user_valid(self, login, password):
        user = self.dao.get(login)
        print(user)
        if user is not None and user[3] == password:
            return user[0]
        else:
            return -1


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogInDialog()
    window.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
