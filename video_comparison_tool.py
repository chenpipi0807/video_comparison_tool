import sys
import os
import tempfile
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QSlider, QLabel, QFileDialog, QGridLayout, 
                            QSizePolicy, QComboBox, QStyle, QSpinBox)
from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtSignal, QSize, QThread, QProcess
from PyQt6.QtGui import QPalette, QColor, QIcon, QFont
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaDevices, QMediaFormat

class VideoPlayer(QWidget):    
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.5)  # 默认50%音量
        self.media_player.setAudioOutput(self.audio_output)
        self.video_widget = QVideoWidget()
        
        # 设置视频显示区域
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 视频标题栏
        self.title_bar = QLabel(f"视频 {index + 1}")
        self.title_bar.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                padding: 5px;
                background-color: #2a2a2a;
                border-radius: 3px;
                margin-bottom: 5px;
            }
        """)
        
        # 静音按钮
        self.mute_button = QPushButton("静音")
        self.mute_button.setCheckable(True)
        self.mute_button.setFixedSize(60, 25)
        self.mute_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 2px 5px;
            }
            QPushButton:checked {
                background-color: #ff4444;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        self.mute_button.clicked.connect(self.toggle_mute)
        
        # 时间标签
        self.time_label = QLabel("00:00:00 / 00:00:00")
        self.time_label.setStyleSheet("color: #aaaaaa;")
        
        # 进度条
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 5px;
                background: #3a3a3a;
                margin: 0px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid #5c5c5c;
                width: 12px;
                margin: -5px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #1e90ff;
                border-radius: 2px;
            }
        """)
        
        # 视频控件
        self.media_player.setVideoOutput(self.video_widget)
        
        # 标题栏布局
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_bar)
        title_layout.addStretch()
        title_layout.addWidget(self.mute_button)
        
        # 时间布局
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.time_label)
        
        # 主布局
        layout.addLayout(title_layout)
        layout.addWidget(self.video_widget, 1)
        layout.addLayout(time_layout)
        layout.addWidget(self.position_slider)
        
        self.setLayout(layout)
        
        # 连接信号
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.position_slider.sliderMoved.connect(self.set_position)
    
    def load_video(self, file_path):
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.title_bar.setText(os.path.basename(file_path))
    
    def toggle_mute(self, checked):
        self.audio_output.setMuted(checked)
    
    def set_muted(self, muted):
        self.audio_output.setMuted(muted)
        self.mute_button.setChecked(muted)
    
    def set_position(self, position):
        self.media_player.setPosition(position)
    
    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)
        self.update_duration_info(duration)
    
    def position_changed(self, position):
        self.position_slider.setValue(position)
        self.update_duration_info(position)
    
    def update_duration_info(self, position):
        duration = self.media_player.duration()
        if duration <= 0:
            return
            
        current_time = self.format_time(position)
        total_time = self.format_time(duration)
        self.time_label.setText(f"{current_time} / {total_time}")
    
    def format_time(self, ms):
        seconds = int(ms / 1000)
        minutes = int(seconds / 60)
        hours = int(minutes / 60)
        return f"{hours:02d}:{minutes % 60:02d}:{seconds % 60:02d}"

class VideoComparisonTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频对比工具")
        self.setMinimumSize(1000, 700)
        self.setAcceptDrops(True)  # 启用拖放支持
        
        # 主控件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # 视频网格区域
        self.video_grid = QWidget()
        self.grid_layout = QGridLayout(self.video_grid)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # 控制区域
        self.control_panel = QWidget()
        control_layout = QHBoxLayout(self.control_panel)
        control_layout.setContentsMargins(10, 5, 10, 10)
        
        # 添加视频按钮
        self.add_button = QPushButton("添加视频")
        self.add_button.setFixedSize(100, 30)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #1e90ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #1a80e6;
            }
        """)
        self.add_button.clicked.connect(self.add_videos)
        
        # 播放/暂停按钮
        self.play_button = QPushButton()
        self.play_button.setFixedSize(60, 30)
        self.play_button.setCheckable(True)
        self.play_button.setChecked(False)
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.toggle_playback)
        
        # 静音所有按钮
        self.mute_all_button = QPushButton("全部静音")
        self.mute_all_button.setCheckable(True)
        self.mute_all_button.setFixedSize(80, 30)
        self.mute_all_button.toggled.connect(self.toggle_mute_all)
        
        # 布局类型
        self.layout_type_label = QLabel("布局类型:")
        self.layout_type_combo = QComboBox()
        self.layout_type_combo.addItems(["Z字形布局", "普通网格"])
        self.layout_type_combo.setCurrentIndex(0)  # 默认使用Z字形布局
        self.layout_type_combo.currentIndexChanged.connect(self.update_grid_layout)
        
        # 每行视频数量
        self.videos_per_row_label = QLabel("每行视频数:")
        self.videos_per_row_spinbox = QSpinBox()
        self.videos_per_row_spinbox.setRange(1, 10)
        self.videos_per_row_spinbox.setValue(3)
        self.videos_per_row_spinbox.valueChanged.connect(self.update_grid_layout)
        
        # 导出视频按钮
        self.export_button = QPushButton("导出视频")
        self.export_button.setFixedSize(100, 30)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.export_button.clicked.connect(self.export_video)
        
        # 进度条
        self.master_slider = QSlider(Qt.Orientation.Horizontal)
        self.master_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #333333;
                margin: 0px;
                border-radius: 4px;
                border: 1px solid #444444;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid #777777;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #ff8c00;
                border-radius: 4px;
                border: 1px solid #ffa500;
            }
        """)
        self.master_slider.sliderMoved.connect(self.sync_players_position)
        
        # 时间标签
        self.master_time_label = QLabel("00:00:00 / 00:00:00")
        self.master_time_label.setStyleSheet("color: #cccccc; font-weight: bold;")
        
        # 主音量控制
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)  # 默认50%音量
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #3a3a3a;
                margin: 0px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid #5c5c5c;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #4caf50;
                border-radius: 2px;
            }
        """)
        self.volume_slider.valueChanged.connect(self.update_volume)
        
        # 音量标签
        self.volume_label = QLabel("音量:")
        self.volume_label.setStyleSheet("color: #cccccc;")
        
        # 添加到控制布局
        control_layout.addWidget(self.add_button)
        control_layout.addSpacing(10)
        control_layout.addWidget(self.play_button)
        control_layout.addSpacing(10)
        control_layout.addWidget(self.mute_all_button)
        control_layout.addSpacing(20)
        control_layout.addWidget(self.layout_type_label)
        control_layout.addWidget(self.layout_type_combo)
        control_layout.addSpacing(10)
        control_layout.addWidget(self.videos_per_row_label)
        control_layout.addWidget(self.videos_per_row_spinbox)
        control_layout.addSpacing(10)
        control_layout.addWidget(self.export_button)
        control_layout.addSpacing(20)
        control_layout.addWidget(self.volume_label)
        control_layout.addWidget(self.volume_slider)
        control_layout.addStretch()
        control_layout.addWidget(self.master_time_label)
        
        # 主布局
        self.main_layout.addWidget(self.video_grid, 1)
        self.main_layout.addWidget(self.master_slider)
        self.main_layout.addWidget(self.control_panel)
        
        # 视频播放器列表
        self.players = []
        self.current_grid_size = (2, 2)
        
        # 更新UI
        self.update_ui_style()
        
        # 初始化网格布局
        self.update_grid_layout()
    
    def update_ui_style(self):
        # 设置深色主题
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(60, 60, 60))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(30, 144, 255))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # 设置全局样式表
        self.setStyleSheet("""
            QMainWindow, QDialog, QWidget {
                background-color: #2d2d2d;
                color: #dcdcdc;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QComboBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 3px 5px;
                min-width: 60px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
            }
            QLabel {
                color: #dcdcdc;
            }
        """)
    
    def add_videos(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("视频文件 (*.mp4 *.avi *.mkv *.mov *.wmv *.flv)")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            for file_path in file_paths:
                player = VideoPlayer(len(self.players))
                player.load_video(file_path)
                self.players.append(player)
                
                # 连接主进度条更新
                player.media_player.durationChanged.connect(self.update_master_duration)
                player.media_player.positionChanged.connect(self.update_master_position)
                
                # 如果这是第一个视频，设置为主控制
                if len(self.players) == 1:
                    self.master_slider.setRange(0, player.media_player.duration())
            
            self.update_grid_layout()
    
    def update_grid_layout(self):
        # 清除现有布局
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        # 获取每行视频数量
        videos_per_row = self.videos_per_row_spinbox.value()
        
        # 如果没有播放器，直接返回
        if not self.players:
            return
            
        # 计算行数
        num_videos = len(self.players)
        rows = (num_videos + videos_per_row - 1) // videos_per_row  # 向上取整
        
        # 添加播放器到网格
        if self.layout_type_combo.currentIndex() == 0:  # Z字形布局
            for i, player in enumerate(self.players):
                row = i // videos_per_row
                
                # 如果是奇数行，则反向计算列位置
                if row % 2 == 0:  # 偶数行（第一行是0）
                    col = i % videos_per_row
                else:  # 奇数行
                    col = videos_per_row - 1 - (i % videos_per_row)
                
                self.grid_layout.addWidget(player, row, col)
                player.show()
        else:  # 普通网格布局
            for i, player in enumerate(self.players):
                row = i // videos_per_row
                col = i % videos_per_row
                self.grid_layout.addWidget(player, row, col)
                player.show()
    
    def toggle_playback(self):
        if not self.players:
            return
            
        if self.play_button.isChecked():
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            for player in self.players:
                player.media_player.play()
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            for player in self.players:
                player.media_player.pause()
    
    def toggle_mute_all(self, muted):
        for player in self.players:
            player.set_muted(muted)
        
        self.mute_all_button.setText("取消静音" if muted else "全部静音")
    
    def update_master_duration(self, duration):
        # 使用最长视频的时长作为主时长
        max_duration = max((p.media_player.duration() for p in self.players if p.media_player.duration() > 0), default=0)
        if max_duration > 0:
            self.master_slider.setRange(0, max_duration)
    
    def update_master_position(self, position):
        if not self.players:
            return
            
        # 检查是否有任何播放器正在播放
        if not any(p.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState for p in self.players):
            return
            
        # 更新主进度条位置
        self.master_slider.setValue(position)
        
        # 更新时间标签
        duration = self.master_slider.maximum()
        current_time = self.format_time(position)
        total_time = self.format_time(duration)
        self.master_time_label.setText(f"{current_time} / {total_time}")
    
    def sync_players_position(self, position):
        # 同步所有播放器的位置
        was_playing = any(p.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState for p in self.players)
        
        for player in self.players:
            if player.media_player.duration() > 0:
                # 按比例设置位置
                ratio = position / self.master_slider.maximum()
                player_pos = int(ratio * player.media_player.duration())
                player.media_player.setPosition(player_pos)
        
        # 如果之前有视频在播放，则继续播放
        if was_playing and not self.play_button.isChecked():
            self.play_button.setChecked(True)
            self.toggle_playback()
    
    def update_volume(self, value):
        # 更新所有播放器的音量
        volume = value / 100.0  # 转换为0.0-1.0范围
        for player in self.players:
            player.audio_output.setVolume(volume)
        
        # 如果当前是静音状态，取消静音
        if self.mute_all_button.isChecked() and value > 0:
            self.mute_all_button.setChecked(False)
            self.toggle_mute_all(False)
    
    def format_time(self, ms):
        seconds = int(ms / 1000)
        minutes = int(seconds / 60)
        hours = int(minutes / 60)
        return f"{hours:02d}:{minutes % 60:02d}:{seconds % 60:02d}"
    
    def dragEnterEvent(self, event):
        # 检查是否有视频文件被拖拽
        if event.mimeData().hasUrls():
            # 只接受本地文件
            for url in event.mimeData().urls():
                if url.isLocalFile() and self.is_video_file(url.toLocalFile()):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event):
        # 处理被拖拽的视频文件
        files = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile() and self.is_video_file(url.toLocalFile())]
        if files:
            # 为每个被拖拽的视频创建播放器
            for file_path in files:
                player = VideoPlayer(len(self.players))
                player.load_video(file_path)
                self.players.append(player)
                
                # 连接主进度条更新
                player.media_player.durationChanged.connect(self.update_master_duration)
                player.media_player.positionChanged.connect(self.update_master_position)
                
                # 如果这是第一个视频，设置为主控制
                if len(self.players) == 1:
                    self.master_slider.setRange(0, player.media_player.duration())
            
            self.update_grid_layout()
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        # 允许在窗口上拖动
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def is_video_file(self, file_path):
        # 检查文件是否为支持的视频格式
        video_extensions = [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"]
        return any(file_path.lower().endswith(ext) for ext in video_extensions)
        
    def closeEvent(self, event):
        # 清理资源
        for player in self.players:
            player.media_player.stop()
        event.accept()
    
    def export_video(self):
        # 如果没有视频，直接返回
        if not self.players:
            print("没有视频可以导出")
            return
            
        # 暂停所有视频
        for player in self.players:
            player.media_player.pause()
            
        # 选择保存路径
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            "保存导出视频", 
            os.path.expanduser("~") + "/output_video.mp4", 
            "视频文件 (*.mp4)"
        )
        
        if not output_path:
            return  # 用户取消了保存对话框
        
        # 获取所有视频路径
        video_paths = []
        for player in self.players:
            media_url = player.media_player.source().toLocalFile()
            if media_url:
                video_paths.append(media_url)
        
        # 获取当前的视频每行数量和布局类型
        videos_per_row = self.videos_per_row_spinbox.value()
        is_zigzag = self.layout_type_combo.currentIndex() == 0
        
        # 使用FFmpeg合并视频
        try:
            # 创建临时文件夹用于处理
            temp_dir = tempfile.mkdtemp()
            
            # 准备FFmpeg命令
            ffmpeg_cmd = ["ffmpeg", "-y"]
            
            # 为每个视频添加输入
            for i, video_path in enumerate(video_paths):
                ffmpeg_cmd.extend(["-i", video_path])
            
            # 计算行数
            num_videos = len(video_paths)
            rows = (num_videos + videos_per_row - 1) // videos_per_row
            
            # 构建FFmpeg网格布局的筛选器复杂命令
            filter_complex = []
            
            # 首先分析所有视频的尺寸以决定基准格式
            # 使用缩放比例而不是固定大小
            analyze_cmd = ["ffmpeg"]
            # 分析每个视频的原始尺寸
            aspect_ratios = []
            
            # 默认使用更小的padding和间距
            # 视频之间仅留小空间(设置为1)
            padding = 1
            
            # 添加xstack格式的视频网格
            row_stacks = []
            for row in range(rows):
                row_inputs = []
                for col in range(videos_per_row):
                    idx = row * videos_per_row + col
                    
                    # 如果使用Z字形布局且是奇数行，则反向排序
                    if is_zigzag and row % 2 == 1:
                        idx = row * videos_per_row + (videos_per_row - 1 - col)
                        
                    if idx < num_videos:
                        # 保持原始比例，使用缩放而不是填充
                        # 使用更高的分辨率提高清晰度（640x360而不是320x180）
                        # 使用简单的缩放命令，避免复杂的表达式
                        filter_complex.append(f"[{idx}:v]scale=640:-2,setsar=1[v{idx}]")
                        row_inputs.append(f"[v{idx}]")
                    else:
                        # 如果没有够的视频，添加适合分辨率的空白背景
                        # 使用正确的FFmpeg color滤镜格式：s=宽度x高度
                        filter_complex.append(f"color=black:s=640x360:d=999999[v{idx}]")
                        row_inputs.append(f"[v{idx}]")

                
                # 水平合并每一行的视频，不使用padding参数避免兼容性问题
                row_stacks.append(f"{''.join(row_inputs)}hstack=inputs={len(row_inputs)}[row{row}]")
            
            # 垂直合并所有行
            filter_complex.extend(row_stacks)
            rows_inputs = ''.join([f"[row{i}]" for i in range(rows)])
            filter_complex.append(f"{rows_inputs}vstack=inputs={rows}[v]")
            
            # 为整个视频添加统一小边距
            filter_complex.append(f"[v]pad=iw+10:ih+10:5:5:black[vout]")
            
            # 最终输出使用vout而不是v
            output_label = "vout"
            
            # 添加最终的复合筛选器到FFmpeg命令
            ffmpeg_cmd.extend(["-filter_complex", ';'.join(filter_complex)])
            
            # 添加输出参数，使用更高的质量和适当的编码设置以确保画质
            ffmpeg_cmd.extend([
                "-map", f"[{output_label}]", 
                "-c:v", "libx264", 
                "-preset", "slow",  # 使用更慢但质量更高的预设
                "-crf", "16",  # 质量设置更高，数值越小质量越高、8-28之间，16已非常高
                "-pix_fmt", "yuv420p",  # 确保在不同播放器中兼容
                "-tune", "film",  # 优化处理电影内容
                output_path
            ])
            
            # 执行FFmpeg命令
            subprocess.run(ffmpeg_cmd, check=True)
            
            # 清理临时目录
            for file in os.listdir(temp_dir):
                os.unlink(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
            
            print(f"导出成功: {output_path}")
            
        except Exception as e:
            print(f"导出错误: {str(e)}")
            import traceback
            traceback.print_exc()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序样式为Fusion以获得更好的跨平台外观
    app.setStyle("Fusion")
    
    # 设置应用程序字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    # 设置应用程序图标
    try:
        app_icon = QIcon(resource_path('logo.ico'))
        app.setWindowIcon(app_icon)
    except Exception as e:
        print(f"Warning: Could not set application icon: {e}")
    
    window = VideoComparisonTool()
    window.setWindowIcon(app_icon)
    window.show()
    sys.exit(app.exec())
