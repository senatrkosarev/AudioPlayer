import sys

from PyQt5 import uic, QtCore
from PyQt5.QtCore import QUrl, QDirIterator
from PyQt5.QtGui import QPixmap, QImage, QIcon, QPalette
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget
from tinytag import TinyTag

from image import find_average_color, save_audio_image
from database import AudiofileDao, UserDao


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi('resources\\ui\\MainWindow.ui', self)
        self.setMinimumSize(420, 540)
        self.title_label.hide()
        self.author_label.hide()
        self.image.setPixmap(QPixmap.fromImage(QImage('resources\\default.png')))

        self.playlist = []
        self.current_audio_index = 0
        self.player = QMediaPlayer()
        self.audio_dao = AudiofileDao()

        self.volume_widget = None
        self.main_button.clicked.connect(self.invoke_play_function)
        self.like_button.clicked.connect(self.like)
        self.dislike_button.clicked.connect(self.dislike)
        self.volume_button.clicked.connect(self.open_volume_widget)
        self.open_file_action.triggered.connect(self.open_file)
        self.open_folder_action.triggered.connect(self.open_folder)
        self.next_button.clicked.connect(self.next)
        self.prev_button.clicked.connect(self.previous)
        self.song_slider.sliderReleased.connect(self.slider_released)
        self.error_label.hide()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_slider)
        self.timer.start(1000)
    def update_slider(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.song_slider.setMinimum(0)
            self.song_slider.setMaximum(self.player.duration())
            self.song_slider.setValue(self.song_slider.value() + 1000)
            self.update_time()

    def update_time(self):
        pos = self.player.position()
        current_time = str(f'{int(pos / 60000)}:{int((pos / 1000) % 60):02}')
        self.time_current.setText(current_time)
        print(pos)

    def slider_released(self):
        self.player.setPosition(self.song_slider.value())
        self.update_time()

    def like(self):
        try:
            self.audio_dao.save(1, self.title_label.text(), self.playlist[self.current_audio_index])
        except IndexError:
            pass

    def dislike(self):
        try:
            self.audio_dao.delete(self.playlist[self.current_audio_index])
        except IndexError:
            pass

    def next(self):
        if len(self.playlist) > 1:
            self.song_slider.setSliderPosition(0)
            self.update_time()
            self.current_audio_index += 1
            self.current_audio_index %= len(self.playlist)
            self.load_metadata()
            self.play()

    def previous(self):
        if len(self.playlist) > 1:
            self.song_slider.setSliderPosition(0)
            self.update_time()
            self.current_audio_index -= 1
            self.current_audio_index %= len(self.playlist)
            self.load_metadata()
            self.play()

    def invoke_play_function(self):
        print(self.player.state())
        if not self.playlist:
            self.error_label.show()
        else:
            self.error_label.hide()
            state = self.player.state()
            if state == QMediaPlayer.StoppedState:
                self.play()
            elif state == QMediaPlayer.PlayingState:
                self.pause()
            elif state == QMediaPlayer.PausedState:
                self.resume()

    def sizes(self):
        # TODO delete this func later
        w = self.frameGeometry().width()
        h = self.frameGeometry().height()
        self.setWindowTitle(f'{w}, {h}')

    def print_playlist(self):
        # TODO delete this func later
        print(self.playlist)

    def play(self):
        url = QUrl.fromLocalFile(self.playlist[self.current_audio_index])
        self.player.setMedia(QMediaContent(url))
        self.main_button.setIcon(QIcon('resources\\icons\\pause.svg'))
        self.player.play()
        self.song_slider.setSliderPosition(0)
        self.image.show()

    def pause(self):
        self.player.pause()
        self.main_button.setIcon(QIcon('resources\\icons\\play.svg'))

    def resume(self):
        self.player.play()
        self.main_button.setIcon(QIcon('resources\\icons\\pause.svg'))

    def stop(self):
        self.player.stop()
        self.playlist.clear()
        self.main_button.setIcon(QIcon('resources\\icons\\play.svg'))

    def open_file(self):
        file_path = \
            QFileDialog.getOpenFileName(self, 'Select audio file', '', 'Audio (*.mp3 *.wav);;All files (*)')[0]
        if file_path == '':
            return

        self.stop()
        self.playlist.append(file_path)
        self.error_label.hide()
        self.load_metadata()

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select folder')
        if folder_path == '':
            return
        self.stop()
        iterator = QDirIterator(folder_path, ['*.mp3', '*.wav', '*.ogg'])
        while iterator.hasNext():
            self.playlist.append(iterator.next())
        if len(self.playlist) != 0:
            self.load_metadata()
            self.update_slider()
        else:
            self.image.hide()
            self.title_label.setText('')
            self.author_label.setText('')

    def load_metadata(self):
        file_path = self.playlist[self.current_audio_index]
        tag = TinyTag.get(file_path, image=True)

        title = tag.title
        if title is None:
            self.title_label.setText(file_path[file_path.rfind('/') + 1:])
        else:
            self.title_label.setText(title)
        self.title_label.show()

        authors = tag.artist
        self.author_label.setText(', '.join(authors.split('/')) if authors else 'Unknown author')
        self.author_label.show()

        image = tag.get_image()
        if image is None:
            self.image.setPixmap(QPixmap.fromImage(QImage('resources\\default.png')))
        else:
            save_audio_image(image)
            self.image.setPixmap(QPixmap.fromImage(QImage('resources\\temp.png')))

        # current_time = str(f'{int(pos / 60000)}:{int((pos / 1000) % 60):02}')
        print('AAAAAAAAAA', tag.duration)
        duration = str(f'{int(tag.duration / 60)}:{int(tag.duration % 60):02}')
        self.time_end.setText(str(duration))

        self.image.pixmap().toImage().save('resources\\temp.png')
        colors = find_average_color('resources\\temp.png')
        self.setStyleSheet(f'background-color: rgb({colors[0]}, {colors[1]}, {colors[2]});')

    def open_volume_widget(self):
        x = self.x()
        y = self.y() + self.height() + 40
        color = self.palette().color(QPalette.Background)
        self.volume_widget = VolumeWidget(self.player, x, y, color)
        self.volume_widget.show()


class VolumeWidget(QWidget):
    def __init__(self, player, x, y, color):
        super(VolumeWidget, self).__init__()
        uic.loadUi('resources\\ui\\Volume.ui', self)
        self.move(x, y)
        self.setStyleSheet(f'background-color: rgb({color.red()}, {color.green()}, {color.blue()});')

        self.player = player
        self.volume_slider.setValue(self.player.volume())
        self.volume_slider.valueChanged.connect(self.change_volume)
        QtCore.QTimer.singleShot(10000, self.close)

    def change_volume(self, value):
        self.player.setVolume(value)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
