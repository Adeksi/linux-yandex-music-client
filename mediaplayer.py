from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from MainWindow import Ui_MainWindow
from auth import Ui_Dialog

from main import Ya_Client
import yandex_music

import os
import json
import time


def hhmmss(ms):
    # s = 1000
    # m = 60000
    # h = 360000
    # h, r = divmod(ms, 36000)
    m, r = divmod(ms, 60000)
    s, _ = divmod(r, 1000)
    return (("%d:%02d" % (m, s)))


class ViewerWindow(QMainWindow):
    state = pyqtSignal(bool)

    def closeEvent(self, e):
        # Emit the window state, to update the viewer toggle button.
        self.state.emit(False)


class PlaylistModel(QAbstractListModel):
    def __init__(self, playlist, *args, **kwargs):
        super(PlaylistModel, self).__init__(*args, **kwargs)
        self.playlist = playlist

    def data(self, index, role):
        if role == Qt.DisplayRole:
            media = self.playlist.media(index.row())
            return media.canonicalUrl().fileName()

    def rowCount(self, index):
        return self.playlist.mediaCount()


class AuthDialog(QDialog, Ui_Dialog):
    def __init__(self, *args, **kwargs):
        super(AuthDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)
        # self.dlg = Ui_Dialog()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.player = QMediaPlayer()

        self.player.error.connect(self.erroralert)
        self.player.play()

        # Setup the playlist.
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        # Add viewer for video playback, separate floating window.
        self.viewer = ViewerWindow(self)
        self.viewer.setWindowFlags(
            self.viewer.windowFlags() | Qt.WindowStaysOnTopHint)
        self.viewer.setMinimumSize(QSize(480, 360))

        videoWidget = QVideoWidget()
        self.viewer.setCentralWidget(videoWidget)
        self.player.setVideoOutput(videoWidget)

        # Connect control buttons/slides for media player.
        self.playButton.pressed.connect(self.player.play)
        self.pauseButton.pressed.connect(self.player.pause)
        self.stopButton.pressed.connect(self.player.stop)
        self.volumeSlider.valueChanged.connect(self.player.setVolume)

        self.viewButton.toggled.connect(self.toggle_viewer)
        self.viewer.state.connect(self.viewButton.setChecked)

        self.previousButton.pressed.connect(self.playlist.previous)
        self.nextButton.pressed.connect(self.playlist.next)

        self.model = PlaylistModel(self.playlist)
        self.playlistView.setModel(self.model)
        self.playlist.currentIndexChanged.connect(
            self.playlist_position_changed)
        selection_model = self.playlistView.selectionModel()
        selection_model.selectionChanged.connect(
            self.playlist_selection_changed)

        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)
        self.timeSlider.valueChanged.connect(self.player.setPosition)

        # self.open_file_action.triggered.connect(self.open_file)
        # self.fetch_from_Yandex_Music_action.triggered.connect(
        #     self.fetch_from_Yandex_Music)
        self.update_Tracks_List_action.triggered.connect(
            self.update_Tracks_List)
        self.actionLog_Out.triggered.connect(self.log_out)

        self.setAcceptDrops(True)

        self.show()

        self.auth_dialog = AuthDialog(self)

        self.Ya_music_logged_in = False
        self.client1 = None
        im = QPixmap(f"./images/image.png")
        self.trackCover.setPixmap(im)
        self.actionLog_Out.setText("Log In")
        self.log_in()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            self.playlist.addMedia(
                QMediaContent(url)
            )

        self.model.layoutChanged.emit()

        # If not playing, seeking to first of newly added + play.
        if self.player.state() != QMediaPlayer.PlayingState:
            i = self.playlist.mediaCount() - len(e.mimeData().urls())
            self.playlist.setCurrentIndex(i)
            self.player.play()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open file", "", "mp3 Audio (*.mp3);mp4 Video (*.mp4);Movie files (*.mov);All files (*.*)")

        if path:
            self.playlist.addMedia(
                QMediaContent(
                    QUrl.fromLocalFile(path)
                )
            )

        self.model.layoutChanged.emit()

    def log_in(self):
        # window = MainWindow()
        while self.Ya_music_logged_in is not True:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as fp:
                    main_TOKEN = json.load(fp)['TOKEN']
                # isLoggedIn = True
                self.client1 = Ya_Client(main_TOKEN)
                self.Ya_music_logged_in = True
                self.actionLog_Out.setText("Выйти из аккаунта")
            else:
                email, ok_email = QInputDialog.getText(
                    self, "Email", "Enter Email")
                password, ok_pass = QInputDialog.getText(
                    self, "Password", "Enter password", QLineEdit.Password)
                # self.Ya_music_logged_in = False
                if ok_email is True and ok_pass is True:
                    print(email, password)
                    # while self.Ya_music_logged_in is not True:
                    try:
                        main_TOKEN = Ya_Client.login_V2(email, password)
                    except yandex_music.exceptions.BadRequest as e:
                        QMessageBox.critical(
                            self, "Login Error", "Invalid email or password", defaultButton=QMessageBox.Ok)
                        continue
                    except yandex_music.exceptions.CaptchaRequired as e:
                        QMessageBox.critical(
                            self, "Login Error", "Invalid email or password", defaultButton=QMessageBox.Ok)
                        continue

                    # print(main_TOKEN)
                    self.client1 = Ya_Client(main_TOKEN)
                    self.Ya_music_logged_in = True
                self.actionLog_Out.setText("Выйти из аккаунта")
                print("You are in")

        # self.client1 = client1
        acc_info = self.client1.client.me
        print("Full Name:", acc_info.account.full_name)
        self.acc_name.setText(acc_info.account.full_name)
        self.fetch_from_Yandex_Music()

    def log_out(self):
        self.playlist.clear()
        print(os.getcwd())
        if os.path.exists("settings.json"):
            os.remove("settings.json")
            im = QPixmap(f"./images/image.png")
            self.trackCover.setPixmap(im)
            self.actionLog_Out.setText("Войти в аккаунт")
            self.acc_name.setText("")
            self.client1.delete_cached_tracks()
            self.client1 = None
            self.Ya_music_logged_in = False
        else:
            # QMessageBox.critical(
            #     self, "Update Error", "You are not logged in", defaultButton=QMessageBox.Ok)
            self.log_in()

    def update_Tracks_List(self):
        if self.client1 is None:
            QMessageBox.critical(
                self, "Update Error", "You are not logged in", defaultButton=QMessageBox.Ok)
        else:
            self.client1.update_liked_tracks()
            self.fetch_from_Yandex_Music()
            QMessageBox.critical(
                self, "Update Complete", "Track List Updated", defaultButton=QMessageBox.Ok)

    def fetch_from_Yandex_Music(self):
        path = os.getcwd()
        path = "file://" + path + "/music"
        self.playlist.clear()
        if self.Ya_music_logged_in:
            for key, track in self.client1.liked_tracks_dict.items():
                trackk = QMediaContent(QUrl(path + "/" + track + ".mp3"))
                self.playlist.addMedia(trackk)
        self.model.layoutChanged.emit()

    def update_duration(self, duration):
        print("!", duration)
        print("?", self.player.duration())

        self.timeSlider.setMaximum(duration)

        if duration >= 0:
            self.totalTimeLabel.setText(hhmmss(duration))

    def update_position(self, position):
        if position >= 0:
            self.currentTimeLabel.setText(hhmmss(position))

        # Disable the events to prevent updating triggering a setPosition event (can cause stuttering).
        self.timeSlider.blockSignals(True)
        self.timeSlider.setValue(position)
        self.timeSlider.blockSignals(False)

    def playlist_selection_changed(self, ix):
        # We receive a QItemSelection from selectionChanged.
        i = ix.indexes()[0].row()

        self.playlist.setCurrentIndex(i)

    def playlist_position_changed(self, i):
        self.client1.download_track(str(i))
        # self.trackCover.setp
        im = QPixmap(f"./covers/{self.client1.liked_tracks_dict[f'{i}']}.png")
        self.trackCover.setPixmap(im)
        self.song_title.setText(self.client1.liked_tracks_dict[f'{i}'])
        # time.sleep(2)
        print("OOL")
        if i > -1:
            ix = self.model.index(i)
            self.playlistView.setCurrentIndex(ix)

    def toggle_viewer(self, state):
        if state:
            self.viewer.show()
        else:
            self.viewer.hide()

    def erroralert(self, *args):
        print(args)


if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName("Yande-Music")
    app.setStyle("Fusion")

    # Fusion dark palette from https://gist.github.com/QuantumCD/6245215.
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    app.setStyleSheet(
        "QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    window = MainWindow()
    app.exec_()
