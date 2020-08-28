from ctypes import windll
import os
from PIL import Image
from pickle import dump, load
from PyQt5 import QtCore, QtGui, QtWidgets
from pytube import YouTube
import pytube.exceptions
import subprocess
import sys
from threading import Thread
from time import strftime, gmtime, sleep
from urllib import request
from uuid import getnode


class UiMainWindow(object):
    def __init__(self):
        # Initialize Widgets
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.linkInput = QtWidgets.QLineEdit(self.centralwidget)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.bannerOverlayLabel = QtWidgets.QLabel(self.centralwidget)
        self.checkLink = QtWidgets.QPushButton(self.centralwidget)
        self.videoQualityDropdown = QtWidgets.QComboBox(self.centralwidget)
        self.audioQualityDropdown = QtWidgets.QComboBox(self.centralwidget)
        self.videoOnlyCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.audioOnlyCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.saveAsLabel = QtWidgets.QLabel(self.centralwidget)
        self.saveFilenameBar = QtWidgets.QLineEdit(self.centralwidget)
        self.browseButton = QtWidgets.QToolButton(self.centralwidget)
        self.encoderPresetDropdown = QtWidgets.QComboBox(self.centralwidget)
        self.downloadButton = QtWidgets.QPushButton(self.centralwidget)
        # self.cancelDownloadButton = QtWidgets.QPushButton(self.centralwidget)
        self.loselessEncodingCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.keepSeparatedCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.thumbnailLabel = QtWidgets.QLabel(self.centralwidget)
        self.videoTitleLabel = QtWidgets.QLabel(self.centralwidget)
        self.videoLengthLabel = QtWidgets.QLabel(self.centralwidget)
        self.downloadSizeLabel = QtWidgets.QLabel(self.centralwidget)
        self.downloadProgress = QtWidgets.QProgressBar(self.centralwidget)
        self.progressStateLabel = QtWidgets.QLabel(self.centralwidget)
        self.creditsLabel = QtWidgets.QLabel(self.centralwidget)

        # Initialize Message Box
        self.msgbox = QtWidgets.QMessageBox()

        # Config Info
        try:
            self.config_file = load(open('config', 'rb'))
        except FileNotFoundError:
            self.config_file = dict()

        # Temp Info
        self.temp_info = dict()

        # Encoder presets
        self.available_encoder_presets = {0: "ultrafast", 1: "veryfast", 2: "fast", 3: "medium",
                                          4: "slow", 5: "slower", 6: "veryslow"}

        # Class-Level Variables
        self.yt_link = ''
        self.videoTitle = ''
        self.videoLength = ''
        self.downloadSize = 0

        self.file_size = 0
        self.video_file_size = 0
        self.audio_file_size = 0

        self.combinedState = True
        self.videoOnlyState = False
        self.audioOnlyState = False
        self.approxFileSize = False

        self.default_file_name = ''
        self.output_path = ''
        self.file_extension = ''
        self.file_name = ''
        self.file_path = ''
        self.file_video_save_path = ''
        self.file_audio_save_path = ''
        self.size_check_path = ''
        self.encoder_preset = ''
        self.loseless_encoding = ''

        # Pytube Objects
        self.yt = None
        self.videoStreamTags = list()
        self.audioStreamTags = list()
        self.videoStream = None
        self.audioStream = None

    def setupUi(self, MainWindow):
        # Setup Main Window
        MainWindow.setWindowTitle('Light Youtube Downloader')
        MainWindow.resize(461, 465)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(461, 465))
        MainWindow.setMaximumSize(QtCore.QSize(461, 465))

        # Global Font Settings
        font = QtGui.QFont()
        font.setPointSize(9)

        # Set Widget Properties
        # bannerOverlayLabel
        self.bannerOverlayLabel.setGeometry(QtCore.QRect(30, 10, 401, 131))
        self.bannerOverlayLabel.setText("")
        self.bannerOverlayLabel.setPixmap(QtGui.QPixmap("imgs/banner_overlay.png"))
        self.bannerOverlayLabel.setObjectName("bannerOverlayLabel")

        # linkInput
        self.linkInput.setGeometry(QtCore.QRect(9, 152, 348, 20))
        self.linkInput.setPlaceholderText("https://www.youtube.com/watch?v=GU3AoFaJ3jc")
        self.linkInput.setMaxLength(32767)
        self.linkInput.setFrame(True)

        # checkLink
        self.checkLink.setGeometry(QtCore.QRect(359, 151, 92, 22))
        self.checkLink.setFont(font)
        self.checkLink.setText("Continue")
        self.checkLink.clicked.connect(self.get_video_info_handler)

        # videoQualityDropdown
        self.videoQualityDropdown.setEnabled(False)
        self.videoQualityDropdown.setGeometry(QtCore.QRect(269, 182, 91, 23))
        self.videoQualityDropdown.setFont(font)

        # audioQualityDropdown
        self.audioQualityDropdown.setEnabled(False)
        self.audioQualityDropdown.setGeometry(QtCore.QRect(369, 182, 81, 23))
        self.audioQualityDropdown.setSizePolicy(sizePolicy)
        self.audioQualityDropdown.setFont(font)

        # videoOnlyCheckbox
        self.videoOnlyCheckbox.setEnabled(False)
        self.videoOnlyCheckbox.setGeometry(QtCore.QRect(269, 212, 81, 16))
        self.videoOnlyCheckbox.setFont(font)
        self.videoOnlyCheckbox.setText("Video Only")
        self.videoOnlyCheckbox.stateChanged.connect(self.video_checkbox_handler)

        # audioOnlyCheckbox
        self.audioOnlyCheckbox.setEnabled(False)
        self.audioOnlyCheckbox.setGeometry(QtCore.QRect(369, 212, 81, 16))
        self.audioOnlyCheckbox.setFont(font)
        self.audioOnlyCheckbox.setText("Audio Only")
        self.audioOnlyCheckbox.stateChanged.connect(self.audio_checkbox_handler)

        # saveAsLabel
        self.saveAsLabel.setGeometry(QtCore.QRect(270, 232, 47, 13))
        self.saveAsLabel.setFont(font)
        self.saveAsLabel.setText("Save as:")

        # saveFilenameBar
        self.saveFilenameBar.setEnabled(False)
        self.saveFilenameBar.setGeometry(QtCore.QRect(269, 250, 154, 20))

        # browseButton
        self.browseButton.setEnabled(False)
        self.browseButton.setGeometry(QtCore.QRect(425, 249, 25, 22))
        self.browseButton.setText("...")
        self.browseButton.clicked.connect(self.browse_save)

        # thumbnailLabel
        self.thumbnailLabel.setGeometry(QtCore.QRect(10, 182, 251, 156))
        self.thumbnailLabel.setText("")
        self.thumbnailLabel.setPixmap(QtGui.QPixmap('imgs/blank.jpg'))

        # videoTitleLabel
        self.videoTitleLabel.setGeometry(QtCore.QRect(9, 362, 251, 16))
        self.videoTitleLabel.setFont(font)
        self.videoTitleLabel.setText("Title: -")

        # videoLengthLabel
        self.videoLengthLabel.setGeometry(QtCore.QRect(10, 342, 150, 16))
        self.videoLengthLabel.setFont(font)
        self.videoLengthLabel.setText("Length: - ")

        # downloadSizeLabel
        self.downloadSizeLabel.setGeometry(QtCore.QRect(166, 343, 93, 16))
        self.downloadSizeLabel.setFont(font)
        self.downloadSizeLabel.setText("Size: - ")

        # encoderPresetDropdown
        self.encoderPresetDropdown.setGeometry(QtCore.QRect(269, 278, 180, 24))
        self.encoderPresetDropdown.setFont(font)
        self.encoderPresetDropdown.setToolTip("Faster presets will result in decreased quality with slightly\n"
                                              "faster encoding speeds, while slower presets will result\n"
                                              "in better quality at the expense of significantly slower\n"
                                              "encoding speeds. Slower presets will also increase file size.\n\n"
                                              "Note: Longer videos take longer to encode.")
        self.encoderPresetDropdown.addItems(["Select Encoder Preset:", "Ultrafast Preset", "Veryfast Preset",
                                             "Fast Preset", "Balanced Preset", "Slow Preset", "Slower Preset",
                                             "Very Slow Preset"])

        self.encoderPresetDropdown.activated.connect(self.preset_dropdown_handler)

        # downloadButton
        self.downloadButton.setEnabled(False)
        self.downloadButton.setGeometry(QtCore.QRect(269, 310, 182, 27))
        self.downloadButton.setFont(font)
        self.downloadButton.setText("Download")
        self.downloadButton.clicked.connect(self.download_handler)

        # cancelDownloadButton
        """
        self.cancelDownloadButton.setVisible(False)
        self.cancelDownloadButton.setGeometry(QtCore.QRect(269, 310, 182, 27))
        self.cancelDownloadButton.setFont(font)
        self.cancelDownloadButton.clicked.connect(self.cancel_download_handler)
        """

        # loselessEncodingCheckbox
        self.loselessEncodingCheckbox.setGeometry(QtCore.QRect(270, 341, 181, 17))
        self.loselessEncodingCheckbox.setToolTip("Encodes the final video with no additional loss of quality\n"
                                                 "due to compression, with respect to the encoder preset. Will"
                                                 "increase encoding times.")
        self.loselessEncodingCheckbox.setText("Use Loseless Encoding")

        # keepSeparatedCheckbox
        self.keepSeparatedCheckbox.setGeometry(QtCore.QRect(270, 362, 181, 17))
        self.keepSeparatedCheckbox.setToolTip("Retains downloaded video and audio streams after encoding.\n"
                                              "This setting does not apply to video only or audio only modes.")
        self.keepSeparatedCheckbox.setText("Keep Separate Streams")

        # downloadProgress
        self.downloadProgress.setGeometry(QtCore.QRect(9, 384, 441, 23))
        self.downloadProgress.setProperty("value", 0)

        # progressStateLabel
        self.progressStateLabel.setGeometry(QtCore.QRect(10, 410, 441, 16))
        self.progressStateLabel.setText("State: Please enter a YouTube link")

        # creditsLabel
        self.creditsLabel.setGeometry(QtCore.QRect(10, 430, 401, 16))
        self.creditsLabel.setText("by Bryan Soong (version 0.1.1) (UNSTABLE)|"
                                  "<a href='https://pastebin.com/M4B7MCdx'>Read known issues</a>")
        self.creditsLabel.setOpenExternalLinks(True)

        # Final Initialization
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def app_exit_handler(self):  # Triggered by onWindowClose event
        dump(self.config_file, open('config', 'wb'))

    def alert(self, title, text, info_text):
        self.msgbox.setIcon(QtWidgets.QMessageBox.Warning)
        self.msgbox.setWindowTitle(title)
        self.msgbox.resize(100, 5000)
        self.msgbox.setText(text)
        self.msgbox.setInformativeText(info_text)
        self.msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)

        self.msgbox.exec_()

    def get_video_info_handler(self):
        self.temp_info = dict()
        self.yt_link = self.linkInput.text()
        if self.yt_link != '':
            try:
                self.yt = YouTube(self.yt_link)
                self.get_video_info()

            except pytube.exceptions.HTMLParseError:
                self.alert('Error', 'Error: Failed to parse HTML request!' + ' ' * 30,
                           'Failed to retrieve video. Please try again.')
            except pytube.exceptions.VideoUnavailable:
                self.alert('Error', 'Error: Video Unavailable!' + ' ' * 30,
                           'Please choose another video and try again.')
            except pytube.exceptions.LiveStreamError:
                self.alert('Error', 'Error: Video is a live stream!' + ' ' * 30,
                           'Please choose another video and try again.')
            except pytube.exceptions.PytubeError:
                self.alert('Error', 'Error: Video link is invalid!' + ' ' * 30,
                           'Failed to retrieve video. Please try again.')
            except Exception as e:
                if str(e) == "'formats'":
                    #  TODO FIX THIS
                    self.alert('Error', 'Error: Video is a live stream!', 'Please choose another video and try again.')
                else:
                    self.alert('Error', 'Unknown Error:' + str(e), 'Please try again!')

    def get_video_info(self):
        # Check if is repeated, if yes, cleared
        if self.videoQualityDropdown.count() > 0: self.videoQualityDropdown.clear()
        if self.audioQualityDropdown.count() > 0: self.audioQualityDropdown.clear()

        # Retrieve stream objects, update dropdown items, sort stream itags into lists for later use
        for s in self.yt.streams.filter(subtype='webm', only_video=True):
            video_stream_item = s.resolution + str(s.fps)
            self.videoQualityDropdown.addItem(video_stream_item)
            self.videoStreamTags.append(s.itag)

        audio_abr = list()
        for s in self.yt.streams.filter(only_audio=True).order_by('abr'):
            audio_abr.append(s.abr)
            self.audioStreamTags.append(s.itag)

        audio_abr.reverse()
        self.audioStreamTags.reverse()
        self.audioQualityDropdown.addItems(audio_abr)

        # Connect currentIndexChanged event to function
        self.videoQualityDropdown.currentIndexChanged.connect(self.select_video_quality)
        self.audioQualityDropdown.currentIndexChanged.connect(self.select_audio_quality)

        # Set default highest quality for video, audio stream objects
        self.videoStream = self.yt.streams.get_by_itag(self.videoStreamTags[0])
        self.audioStream = self.yt.streams.get_by_itag(self.audioStreamTags[0])

        # Start thread to retrieve remaining video info
        Thread(target=self.get_video_info_thread, daemon=True).start()

        self.default_file_name = os.path.splitext(self.videoStream.default_filename)[0]

        # Update thumbnail
        Thread(target=self.update_thumbnail, daemon=True).start()

    def get_video_info_thread(self):
        # For less important tasks so that main thread is not overwhelmed
        # Retrieve remaining video info
        self.videoTitle = self.yt.title
        self.videoLength = strftime("%H:%M:%S", gmtime(self.yt.length))

        # Update labels
        self.videoTitleLabel.setText("Title: %s" % self.videoTitle)
        self.videoLengthLabel.setText("Length: %s" % self.videoLength)

        # Retrieve and update download size
        self.update_file_size()

        # Update file save name and location, browse save button state
        self.progressStateLabel.setText("State: Please select save location")

        self.videoQualityDropdown.setEnabled(True)
        self.audioQualityDropdown.setEnabled(True)
        self.videoOnlyCheckbox.setEnabled(True)
        self.audioOnlyCheckbox.setEnabled(True)
        self.browseButton.setEnabled(True)
        self.downloadButton.setEnabled(False)
        self.checkLink.setEnabled(True)

    def update_thumbnail(self):
        # Retrieve video thumbnail
        request.urlretrieve(self.yt.thumbnail_url, 'light_temp.jpg')

        Image.open('light_temp.jpg').resize((251, 156)).save('light_temp_resize.jpg')

        self.thumbnailLabel.setPixmap(QtGui.QPixmap('light_temp_resize.jpg'))

        os.remove('light_temp.jpg')
        os.remove('light_temp_resize.jpg')

    def update_file_size(self):
        try:
            if self.videoOnlyState:
                self.downloadSize = self.videoStream.filesize
            elif self.audioOnlyState:
                self.downloadSize = self.audioStream.filesize
            else:
                self.downloadSize = self.videoStream.filesize + self.audioStream.filesize

        except request.HTTPError:
            self.approxFileSize = True

            if self.videoOnlyState:
                self.downloadSize = self.videoStream.filesize_approx
            elif self.audioOnlyState:
                self.downloadSize = self.audioStream.filesize_approx
            else:
                self.downloadSize = self.videoStream.filesize_approx + self.audioStream.filesize_approx

        if self.downloadSize > 1073741824:
            self.downloadSize = round(float(self.downloadSize) / float(1073741824), 2)
            self.downloadSizeLabel.setText('Size: %.2f GB' % self.downloadSize)
        else:
            self.downloadSize = round(float(self.downloadSize) / float(1048576), 1)
            self.downloadSizeLabel.setText('Size: %.1f MB' % self.downloadSize)

    def select_video_quality(self):
        self.videoStream = self.yt.streams.get_by_itag(self.videoStreamTags[self.videoQualityDropdown.currentIndex()])
        self.update_file_size()

    def select_audio_quality(self):
        self.audioStream = self.yt.streams.get_by_itag(self.audioStreamTags[self.audioQualityDropdown.currentIndex()])
        self.update_file_size()

    def preset_dropdown_handler(self):
        if self.encoderPresetDropdown.count() == 8:
            selected_preset_index = self.encoderPresetDropdown.currentIndex()
            if selected_preset_index != 0:
                self.encoderPresetDropdown.removeItem(0)
                selected_preset_index -= 1
                self.encoderPresetDropdown.setCurrentIndex(selected_preset_index)
                self.encoder_preset = self.available_encoder_presets[selected_preset_index]
        else:
            selected_preset_index = self.encoderPresetDropdown.currentIndex()
            self.encoder_preset = self.available_encoder_presets[selected_preset_index]

    def video_checkbox_handler(self):
        if self.videoOnlyCheckbox.isChecked():  # Video only checkbox is checked
            self.audioOnlyCheckbox.setChecked(False)
            self.audioQualityDropdown.setEnabled(False)
            self.videoQualityDropdown.setEnabled(True)
            self.videoOnlyState = True
            self.combinedState = False

            if self.output_path != '':
                try:
                    self.output_path = self.temp_info["last_video_output_path"]
                except KeyError:
                    self.progressStateLabel.setText("State: Please select download location")
                    self.downloadButton.setEnabled(False)

        elif not self.videoOnlyCheckbox.isChecked():  # Video only checkbox is unchecked
            self.audioQualityDropdown.setEnabled(True)
            self.videoQualityDropdown.setEnabled(True)
            self.videoOnlyState = False
            self.combinedState = True

        self.update_file_size()

    def audio_checkbox_handler(self):
        if self.audioOnlyCheckbox.isChecked():  # Audio only checkbox is checked
            self.videoOnlyCheckbox.setChecked(False)
            self.videoQualityDropdown.setEnabled(False)
            self.audioQualityDropdown.setEnabled(True)
            self.audioOnlyState = True
            self.combinedState = False

            if self.output_path != '':
                try:
                    self.output_path = self.temp_info["last_audio_output_path"]
                except KeyError:
                    self.progressStateLabel.setText("State: Please select download location")
                    self.downloadButton.setEnabled(False)

        elif not self.audioOnlyCheckbox.isChecked():  # Audio only checkbox is unchecked
            self.audioQualityDropdown.setEnabled(True)
            self.videoQualityDropdown.setEnabled(True)
            self.audioOnlyState = False
            self.combinedState = True

        self.update_file_size()

    def browse_save(self):
        try:
            last_file_path = self.config_file["last_file_path"]

        except KeyError:
            last_file_path = os.getcwd()

        if self.combinedState or self.videoOnlyState:
            try:
                file_path = self.temp_info["last_video_output_path"]
            except KeyError:
                file_path = os.path.join(last_file_path, self.default_file_name)

            self.output_path = QtWidgets.QFileDialog.getSaveFileName(None, 'Choose Output File', file_path,
                                                                     'MP4 (*.mp4)')[0]
        elif self.audioOnlyState:
            try:
                file_path = self.temp_info["last_audio_output_path"]
            except KeyError:
                file_path = os.path.join(last_file_path, self.default_file_name)

            self.output_path = QtWidgets.QFileDialog.getSaveFileName(None, 'Choose Output File', file_path,
                                                                     'MP3 (*.mp3)')[0]

        self.saveFilenameBar.setPlaceholderText(self.output_path)

        if self.output_path != '':
            if self.combinedState or self.audioOnlyState or self.videoOnlyState:
                last_file_path = self.output_path.split('/')
                last_file_path.pop()
                last_file_path = '/'.join(last_file_path)
                self.config_file["last_file_path"] = last_file_path
                self.file_path = last_file_path

            # Save to temp, Prepare for download
            if self.videoOnlyState:
                self.temp_info["last_video_output_path"] = self.output_path
                self.file_name, self.file_extension = os.path.splitext(os.path.basename(self.output_path))

            elif self.audioOnlyState:
                self.temp_info["last_audio_output_path"] = self.output_path
                self.file_name, self.file_extension = os.path.splitext(os.path.basename(self.output_path))

            elif self.combinedState:
                self.temp_info["last_video_output_path"] = self.output_path

            # Allow download
            self.downloadButton.setEnabled(True)
            self.progressStateLabel.setText("State: Ready to download")

    def progress_bar_helper(self):
        if self.combinedState:
            self.file_size = (self.videoStream.filesize_approx + self.audioStream.filesize_approx) if \
                self.approxFileSize else (self.videoStream.filesize + self.audioStream.filesize)

            self.video_file_size = self.videoStream.filesize_approx if self.approxFileSize\
                else self.videoStream.filesize
            self.audio_file_size = self.audioStream.filesize_approx if self.approxFileSize\
                else self.audioStream.filesize

            self.file_video_save_path = os.path.join(self.file_path + '/', ('(Video)' + self.videoStream.default_filename))
            self.file_audio_save_path = os.path.join(self.file_path + '/', ('(Audio)' + self.audioStream.default_filename))

        elif self.videoOnlyState:
            self.file_size = self.videoStream.filesize_approx if self.approxFileSize else self.videoStream.filesize
            self.size_check_path = os.path.join(self.file_path + '/', self.videoStream.default_filename)

        elif self.audioOnlyState:
            self.file_size = self.audioStream.filesize_approx if self.approxFileSize else self.audioStream.filesize
            self.size_check_path = os.path.join(self.file_path + '/', self.audioStream.default_filename)

    def update_progress_bar(self):
        downloaded_size = 0
        if self.combinedState:
            while downloaded_size < self.file_size:
                while downloaded_size < self.video_file_size:
                    try:
                        downloaded_size = os.stat(self.file_video_save_path).st_size
                        progress = round((downloaded_size / self.file_size) * 100, 0)
                        self.downloadProgress.setProperty("value", progress)
                        sleep(0.3)
                    except FileNotFoundError:
                        sleep(0.3)
                    except ZeroDivisionError:
                        break

                try:
                    downloaded_size = self.video_file_size + os.stat(self.file_audio_save_path).st_size
                    progress = round((downloaded_size / self.file_size) * 100, 0)
                    self.downloadProgress.setProperty("value", progress)
                    sleep(0.3)
                except FileNotFoundError:
                    sleep(0.3)
                except ZeroDivisionError:
                    break

        elif self.videoOnlyState or self.audioOnlyState:
            while downloaded_size < self.file_size:
                try:
                    downloaded_size = os.stat(self.size_check_path).st_size
                    progress = round((downloaded_size / self.file_size) * 100, 0)
                    self.downloadProgress.setProperty("value", progress)
                    sleep(0.3)
                except FileNotFoundError:
                    sleep(0.3)
                except ZeroDivisionError:
                    break

    def run_ffmpeg_function(self):
        cmd = ''
        if self.combinedState:
            if os.path.exists(self.output_path):
                os.remove(self.output_path)

            cmd = 'ffmpeg -y -i "%s" -i "%s" -c:v copy -preset %s %s"%s"' \
                  % (self.file_video_save_path, self.file_audio_save_path, self.encoder_preset, self.loseless_encoding,
                     self.output_path)
        else:
            if self.videoOnlyState:
                cmd = 'ffmpeg -y -i "%s" -c:v copy -preset %s %s"%s"'\
                      % (self.size_check_path, self.encoder_preset, self.loseless_encoding, self.output_path)
            elif self.audioOnlyState:
                cmd = 'ffmpeg -y -i "%s" -preset %s %s"%s"' \
                      % (self.size_check_path, self.encoder_preset, self.loseless_encoding, self.output_path)
                print(cmd)

        subprocess.Popen(cmd, shell=True).wait()

    def download(self):
        if os.path.exists(self.file_video_save_path):
            os.remove(self.file_video_save_path)

        if os.path.exists(self.file_audio_save_path):
            os.remove(self.file_audio_save_path)

        self.progressStateLabel.setText("State: Downloading video")
        try:
            self.videoStream.download(output_path=self.file_path, filename_prefix='(VIDEO)')
            self.progressStateLabel.setText("State: Downloading audio")
            self.audioStream.download(output_path=self.file_path, filename_prefix='(AUDIO)')

            if self.combinedState:
                self.progressStateLabel.setText("State: Encoding video and audio files. Please wait.")
                self.run_ffmpeg_function()
                self.progressStateLabel.setText("State: Done!")

                if not self.keepSeparatedCheckbox.isChecked():
                    os.remove(self.file_video_save_path)
                    os.remove(self.file_audio_save_path)

        except Exception:
            self.file_video_save_path = os.path.join(self.file_path + '/', self.yt.streams.first().default_filename)

            try:
                self.file_size = self.yt.streams.first().filesize + self.audioStream.filesize
            except request.HTTPError:
                self.file_size = self.yt.streams.first().filesize_approx + self.audioStream.filesize_approx

            try:
                self.yt.streams.first().download(output_path=self.file_path)
                self.file_size = 0

            except Exception:
                self.progressStateLabel.setText("State: Error. No compatible downloadable video streams could be found.")

            self.progressStateLabel.setText("State: Error downloading selected video stream. "
                                            "Most compatible format downloaded.")

            self.downloadProgress.setProperty("value", 100)

        # Reset progress bar
        self.downloadProgress.setProperty("value", 100)
        sleep(0.4)
        self.downloadProgress.setProperty("value", 0)

        self.toggle_features(True)

    def download_video(self):
        check_exist_path = os.path.join(self.file_path + '/',  self.videoStream.default_filename)
        if os.path.exists(check_exist_path):
            os.remove(check_exist_path)

        self.progressStateLabel.setText("State: Downloading video")
        try:
            self.videoStream.download(output_path=self.file_path)

            if os.path.splitext(self.videoStream.default_filename)[1] != self.file_extension:
                self.run_ffmpeg_function()
                os.remove(self.size_check_path)

            self.progressStateLabel.setText("State: Done!")

        except Exception:
            self.size_check_path = os.path.join(self.file_path + '/', self.yt.streams.first().default_filename)

            try:
                self.file_size = self.yt.streams.first().filesize
            except request.HTTPError:
                self.file_size = self.yt.streams.first().filesize()

            self.yt.streams.first().download(output_path=self.file_path)

            self.progressStateLabel.setText("State: Error downloading selected video stream. "
                                            "Most compatible format downloaded.")

        # Reset progress bar
        self.downloadProgress.setProperty("value", 100)
        sleep(0.4)
        self.downloadProgress.setProperty("value", 0)

        self.toggle_features(True)
        self.audioQualityDropdown.setEnabled(False)

    def download_audio(self):
        try:
            check_exist_path = os.path.join(self.file_path + '/', self.audioStream.default_filename)
            if os.path.exists(check_exist_path):
                os.remove(check_exist_path)

            self.progressStateLabel.setText("State: Downloading audio")
            self.audioStream.download(output_path=self.file_path)
            sleep(0.2)

            if os.path.splitext(self.audioStream.default_filename)[1] != self.file_extension:
                self.run_ffmpeg_function()
                os.remove(self.size_check_path)

            self.progressStateLabel.setText("State: Done!")

            # Reset progress bar
            self.downloadProgress.setProperty("value", 100)
            sleep(0.4)
            self.downloadProgress.setProperty("value", 0)

        except pytube.exceptions.PytubeError:
            self.progressStateLabel.setText("State: Audio download error!")

        self.toggle_features(True)
        self.videoQualityDropdown.setEnabled(False)

    def download_handler(self):
        if len(self.output_path.split('/')) == 2:
            self.alert('Error', 'Saving file to root directory of drive is currently unsupported',
                       'Please choose a subfolder')

        self.loseless_encoding = '-crf 0 ' if self.loselessEncodingCheckbox.isChecked() else ''

        if self.encoder_preset != '':
            self.progress_bar_helper()  # Get file sizes for progress bar
            self.toggle_features(False)
            if self.videoOnlyState:
                Thread(target=self.download_video, daemon=True).start()
                Thread(target=self.update_progress_bar, daemon=True).start()

            if self.audioOnlyState:
                Thread(target=self.download_audio, daemon=True).start()
                Thread(target=self.update_progress_bar, daemon=True).start()

            if self.combinedState:
                Thread(target=self.download, daemon=True).start()
                Thread(target=self.update_progress_bar, daemon=True).start()
        else:
            self.alert('Error', 'Please select an encoding preset.' + ' ' * 30, '')

    def toggle_features(self, state: bool):
        self.checkLink.setEnabled(state)

        self.videoQualityDropdown.setEnabled(state)
        self.audioQualityDropdown.setEnabled(state)

        self.videoOnlyCheckbox.setEnabled(state)
        self.audioOnlyCheckbox.setEnabled(state)

        self.browseButton.setEnabled(state)

        self.encoderPresetDropdown.setEnabled(state)

        self.loselessEncodingCheckbox.setEnabled(state)
        self.keepSeparatedCheckbox.setEnabled(state)

        self.downloadButton.setEnabled(state)


def identifier():
    unique_address = hex(getnode())

    if not os.path.exists('uniden.dll'):
        dump(unique_address, open('uniden.dll', 'wb'))
        return True
    else:
        try:
            uniden = load(open('uniden.dll', 'rb'))
            if unique_address == uniden:
                return True
            else:
                return False

        except Exception:
            return False


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    if identifier():
        MainWindow = QtWidgets.QMainWindow()
        ui = UiMainWindow()
        ui.setupUi(MainWindow)
        app.aboutToQuit.connect(ui.app_exit_handler)
        MainWindow.show()
        sys.exit(app.exec_())
    else:
        windll.user32.MessageBoxW(0, u"This is an unregistered copy. Please obtain a "
                                     u"registered copy from the author", u"Error", 0)
