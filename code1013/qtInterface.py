# -*- coding: utf-8 -*-
# @Time    : 2024/10/13 16:16
# @Author  : zwj, lyf, lhl
# @File    : qtInterface.py
import os
import sys
import time
import psutil
import qtawesome as qta
import PyQt5
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QUrl, QDateTime
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QDesktopWidget, \
    QFileDialog, QGridLayout, QHBoxLayout, QSplitter, QSlider
from langchain.chains import LLMChain

from TitleBar import *
from bubble_message import BubbleMessage, ChatWidget, MessageType, Notice
from cykj.zhipu import *
from cykj.zlsjy import *
from cykj.video2srt import *
from qss import qss
from PyQt5.QtCore import QThread, pyqtSignal
from qt_material import apply_stylesheet
import cykj.prompts as pt

from cykj.processer import runC, runT

# 获取当前运行时目录
current_directory = os.getcwd()
# 构造 ffmpeg 的完整路径
ffmpeg_path = os.path.join(current_directory, "ffmpeg", "ffmpeg")
# 将该路径添加到 PATH 环境变量的开头
os.environ["PATH"] = os.path.dirname(ffmpeg_path) + ":" + os.environ["PATH"]
# 全局文件监视器
Funclisten = Worker()

'''
#1、使用以下代码中的文件拖拽功能，只需将文件或文件夹拖拽到文本编辑框中即可。如果文件是本地文件，它们将以文件路径的形式显示在文本编辑框中。
#2、如果你想要进一步处理这些文件路径，比如复制、移动、读取或执行其他操作，你可以在 processFiles 方法中添加你的自定义代码，该方法在用户点击提交按钮后被调用。在该方法中，你可以访问文本编辑框的内容，将其拆分成文件路径，并执行相应的操作。
'''




class VideoProcessThread(QThread):
    finished = pyqtSignal()

    def __init__(self, cykj, file_paths, output_dir, textName):
        super().__init__()
        self.file_paths = file_paths
        self.output_dir = output_dir
        self.textName = textName
        #lan
        self.cykj = cykj


    def run(self):
        if not os.path.exists(self.textName):
            video_process(self.cykj, self.file_paths, self.output_dir, Funclisten)
            # video_process(self.file_paths, self.output_dir)
        # print("VideoProcessThread")
        self.finished.emit()



class VideoProcessUsercutThread(QThread):
    finished = pyqtSignal()

    def __init__(self, cykj, file_paths, output_dir, user_keywords):
        super().__init__()
        self.file_paths = file_paths
        self.output_dir = output_dir
        self.user_keywords = user_keywords
        #lan
        self.cykj = cykj

    def run(self):
        video_process_usercut(self.cykj, self.file_paths, self.output_dir, self.user_keywords, Funclisten)
        self.finished.emit()

class Video2SrtThread(QThread):
    finished = pyqtSignal()

    def __init__(self, file_paths, textName):
        super().__init__()
        self.file_paths = file_paths
        self.textName = textName

    def run(self):
        if  not os.path.exists(self.textName):
            # os.system("python3 ./cykj/__main__.py -t " + self.file_paths)
            # os.system("autocut -t " + self.file_paths)
            runT(self.file_paths)
        else :
            time.sleep(5)  # 暂停 20 秒
        self.finished.emit()

class CutVideoThread(QThread):
    finished = pyqtSignal()

    def __init__(self, file_paths, srt_cut_path , output_path, cut_way):
        super().__init__()
        self.file_paths = file_paths
        self.srt_cut_path = srt_cut_path
        self.output_path = output_path
        self.cut_way = cut_way

    def run(self):
        output_path_srt = self.output_path.split('.')[0]+"_srt."+self.output_path.split('.')[1]
        if not os.path.exists(output_path_srt) or self.cut_way == 2:          
            # os.system("python3 ./cykj/__main__.py -c " + self.file_paths + ' ' + self.srt_cut_path)
            # os.system("autocut -c " + self.file_paths + ' ' + self.srt_cut_path)
            runC(self.file_paths, self.srt_cut_path)
            # 使用 f-string 来构建命令字符串
            command = (
                f"ffmpeg -i \"{self.output_path}\" "
                f"-vf \"subtitles='{self.srt_cut_path}':force_style='Fontsize=30'\" "
                f"-c:v libx264 -crf 18 -preset slow -c:a copy \"{output_path_srt}\""
            )
            # 执行命令
            # os.system(command)

            print("裁剪结束", self.file_paths)
        else:
            time.sleep(5)  # 暂停 20 秒

        self.finished.emit()

class SimpleQAThread(QThread):
    finished = pyqtSignal(str)  # 修改这里，使信号能够接受一个字符串参数

    def __init__(self, text, cykj, path):
        super().__init__()
        self.text = text
        # self.model = model
        self.response = ''
        self.cykj = cykj
        self.flag = True
        self.filepath = path
        # self.conversation = LLMChain(
        #     llm=cykj.llm,
        #     prompt=ChatPromptTemplate(
        #     messages=[
        #         SystemMessagePromptTemplate.from_template(
        #             pt.user_qa_promt
        #         ),
        #         HumanMessagePromptTemplate.from_template("{question}")
        #     ]
        # ),
        #     verbose=True,
        #     memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
        # )

    def run(self):
        if self.flag:
            self.conversation = self.cykj.simpleQA_init(self.filepath)
            self.flag = False

        self.response =  self.cykj.simpleQA(self.text, self.conversation)
        # self.response = "hello"
        self.finished.emit(self.response)


class ChangeModelThread(QThread):
    finished = pyqtSignal()  # 修改这里，使信号能够接受一个字符串参数

    def __init__(self, cykj, model):
        super().__init__()
        self.model = model
        self.cykj = cykj

    def run(self):
        self.cykj.changeModel(self.model)


class EmptyThread(QThread):
    finished = pyqtSignal()  # 修改这里，使信号能够接受一个字符串参数

    def __init__(self):
        super().__init__()


    def run(self):
        time.sleep(10)  # 暂停 20 秒
        self.finished.emit()





# 选择大模型的按钮
class OvalButton(QPushButton):
    def __init__(self, text, shape_id, parent=None):
        super().__init__(parent)
        self.shape_id = shape_id
        self.selected = False
        self.setText(text)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {

                color: white;  /* 设置文本颜色为白色 */
                min-width: 80px;
                min-height: 40px; /* 固定高度为30像素 */
                border-bottom: 2px solid white;           
            }
            QPushButton:checked {
                border-bottom: 2px solid #F06242;
                color: #F06242;
            }
        """)
        def setChecked(self, a0):
            super().setChecked()

# 底部的开关，终止等按钮
class CircularButton(QPushButton):
    def __init__(self, icon=None, default_icon=None, hover_icon=None, pressed_icon=None,parent=None):
        super().__init__(parent)
        self.setFixedSize(QSize(70, 70))  # 设置按钮的大小为正方形
        self.defaultIcon = QIcon(default_icon)
        self.hoverIcon = QIcon(hover_icon) if hover_icon else self.defaultIcon # 鼠标经过时的图标
        self.pressed = QIcon(pressed_icon) if pressed_icon else self.defaultIcon
        self.setIcon(self.defaultIcon)
        self.setIconSize(QSize(68, 68))

    # 鼠标进入按钮区域
    def enterEvent(self, event):
        self.setIcon(self.hoverIcon)  # 设置鼠标经过时的图标
        super(CircularButton, self).enterEvent(event)

    # 鼠标离开按钮区域
    def leaveEvent(self, event):
        self.setIcon(self.defaultIcon)  # 恢复原始图标
        super(CircularButton, self).leaveEvent(event)

    # # 重写鼠标按下事件
    # def mousePressEvent(self, event):
    #     self.setIcon(self.pressedIcon)  # 改变图标为按下时的图标
    #     # 调用QPushButton的默认行为
    #     QPushButton.mousePressEvent(self, event)

    # # 重写鼠标释放事件
    # def mouseReleaseEvent(self, event):
    #     self.setIcon(self.defaultIcon)  # 鼠标释放后恢复为默认图标
    #      # 调用QPushButton的默认行为以确保clicked事件触发
    #     QPushButton.mouseReleaseEvent(self, event)



class MainApp(QMainWindow):  #创建实例化类
    def __init__(self):
        super().__init__()
        self.file_paths = "#"
        # self.model = 0
        self.cut_way = 1

        self.initUI()

        # lan
        self.cykj = CYKJ()
    def initUI(self):

        self.setWindowFlags(Qt.FramelessWindowHint)



        self.titleBar = TitleBar(self)
        TitleBarWidth = self.titleBar.width()
        TitleBarHeight = self.titleBar.height()
        # self.titleBar.setStyleSheet("background-color: #101010; padding-bottom:3px;font-size:16pt; color:#FAE100")
        self.titleBarOut = QWidget()
        self.titleBarOut.setFixedHeight(TitleBarHeight)
        self.titleBarOut.setStyleSheet("background-color: #101010; border:0px; color:#FAE100")
        self.titleBarLay = QVBoxLayout(self)       
        self.titleBarLay.addWidget(self.titleBar)
        self.titleBarLay.setSpacing(0)
        self.titleBarLay.setContentsMargins(0, 0, 0, 0) 
        self.titleBarOut.setLayout(self.titleBarLay)


        self.client = QWidget(self)
        self.center = QWidget(self)

        self.setCentralWidget(self.center)

        self.lay = QVBoxLayout(self)
        self.center.setLayout(self.lay)

        self.lay.addWidget(self.titleBarOut)
        self.lay.addWidget(self.client)
        self.lay.setStretch(1, 100)
        self.lay.setSpacing(0)
        self.lay.setContentsMargins(0, 0, 0, 0)


        # self.titleBar.SetTitle("畅意快剪")
        # 获取屏幕的宽度和高度
        screen = QDesktopWidget().screenGeometry()
        screenWidth = screen.width()
        screenHeight = screen.height()

        # 计算窗口居中的坐标
        x = (screenWidth - self.width()) // 2
        y = (screenHeight - self.height()) // 2
        print(x)
        print(y)
        # 设置窗口大小已经出现在屏幕的什么位置
        self.setGeometry(x, y, 2160, 1128)  #设置主窗口的初始位置和大小。 (x, y)是设置窗口出现的位置。窗口的宽度为 600 像素，高度为 400 像素。

        # 初始化窗口排版模式
        central = QWidget(self)    #创建一个名为 central 的 QWidget（窗口中央部件），用于将其他小部件添加到主窗口的中央区域。
        self.setCentralWidget(central) #将 central 部件设置为主窗口的中央部分。这意味着所有其他小部件将放置在 central 部件中，以确保它们在窗口中间显示。

        # 功能进度
        
        Funclisten.naviBarValue.connect(self.updateFileSlide)

        # 左侧布局
        # 空title
        self.titleText = QLabel(self)
        self.titleText.setText("无标题")
        self.titleText.setFixedHeight(64)
        self.titleText.setAlignment(Qt.AlignCenter)
        self.titleText.setFrameShadow(QFrame.Sunken)
        self.titleText.setStyleSheet("margin-bottom: 5px; font-size: 24px; color: rgba(255, 255, 255, 230);")


        # 文件加载进度条
        self.fileSlide = QLabel("视频处理： <font color=#FAE100>0%</font>")
        self.fileSlide.setStyleSheet("font-size: 24px; padding: 10px; background-color:#272727; margin:10px; border-radius: 4px; margin-left:5px")

        # self.fileSlide.setOrientation(Qt.Horizontal)
        # self.fileSlide.setValue(0)
        # self.fileSlide.setMinimum(0)
        # self.fileSlide.setMaximum(10)
        # self.fileSlide.hide()


        
        # 显示处理过程的标签
        self.processingText = QLabel("请上传视频文件!")
        self.processingText.setStyleSheet(" font-size: 24px; padding: 10px; background-color:#272727; margin:10px; border-radius: 4px; margin-right:0px")
        self.processingText.setFixedWidth(760)
        # self.processingText.adjustSize()
        # self.processingText.hide()

        

        

        # 提交按钮
        # submBton = qta.icon('ri.folder-upload-line', color='white')
        self.submit_Button = CircularButton(
            default_icon="ui/畅意快剪/切图/上传1@3x.png",
            hover_icon="ui/畅意快剪/切图/上传2@3x.png",
            pressed_icon="ui/畅意快剪/切图/上传3@3x.png"
        )
        self.submit_Button.setStyleSheet("border-left:2px solid #000000")
        self.submit_Button.clicked.connect(self.selectFiles)  # 给提交按钮绑定事件函数processFiles
        # self.submit_Button.setIcon(submBton)
        # self.blackButton.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMaxButton))

        # 文件加载
        # fileBton = qta.icon('fa.cut', color='white')
        self.file_Button = CircularButton(
            default_icon="ui/畅意快剪/切图/视频裁剪1@3x.png",
            hover_icon="ui/畅意快剪/切图/视频裁剪2@3x.png",
            pressed_icon="ui/畅意快剪/切图/视频裁剪3@3x.png"
        )
        self.file_Button.setStyleSheet("border-left:2px solid #000000")
        self.file_Button.clicked.connect(lambda :self.processFiles(1))
        # self.file_Button.setIcon(fileBton)


        # 进一步处理剪切
        # submBton2 = qta.icon('fa.film', color='white')
        self.submit_Button2 = CircularButton(
            default_icon="ui/畅意快剪/切图/视频裁剪1@3x.png",
            hover_icon="ui/畅意快剪/切图/视频裁剪2@3x.png",
            pressed_icon="ui/畅意快剪/切图/视频裁剪3@3x.png"
        )
        self.submit_Button2.clicked.connect(self.clip)
        # self.submit_Button2.setIcon(submBton2)

        # 视频的布局
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()
        self.videoWidgetOut = QWidget()
        self.videoWidgetOut.setStyleSheet("background-color:#000000;")
        videoLayout = QVBoxLayout()
        videoLayout.setSpacing(0)
        videoLayout.setContentsMargins(0, 0, 0, 0)
        videoLayout.addWidget(self.videoWidget)
        self.videoWidgetOut.setLayout(videoLayout)



        # # 在视频小部件上叠加文本标签
        # self.textOverlay = QLabel("", self.videoWidget)
        # self.textOverlay.setStyleSheet("color: white; font-size: 20px; background-color:#000000;")
        # self.textOverlay.adjustSize()
        # self.textOverlay.move(0,0)  # 调整位置
        # # self.textOverlay.hide()  # 初始隐藏文本标签


        # 视频开始
        playBton = qta.icon('ri.play-fill', color='white')
        self.playButton = CircularButton(
            default_icon="ui/畅意快剪/切图/播放1@3x.png",
            hover_icon="ui/畅意快剪/切图/播放2@3x.png",
            pressed_icon="ui/畅意快剪/切图/播放3@3x.png"
        )
        # self.playButton.setIcon(QIcon("ui/畅意快剪/切图/播放1@3x.png"))
        self.playButton.setIconSize(QSize(68, 68))
        self.playButton.setStyleSheet("border-right:2px solid #000000")
        self.playButton.clicked.connect(self.playClicked)


        # 暂停
        pauseBton = qta.icon('ri.pause-fill', color='white')
        self.pauseButton = CircularButton(
            default_icon="ui/畅意快剪/切图/暂停1@3x.png",
            hover_icon="ui/畅意快剪/切图/暂停2@3x.png",
            pressed_icon="ui/畅意快剪/切图/暂停3@3x.png"
        )
        self.pauseButton.setIconSize(QSize(68, 68))
        self.pauseButton.setStyleSheet("border-right:2px solid #000000")
        self.pauseButton.clicked.connect(self.pauseClicked)
        self.pauseButton.hide()

        # 停止
        stopBton = qta.icon('ri.stop-fill', color='white')
        self.stopButton = CircularButton(
            default_icon="ui/畅意快剪/切图/停止1@3x.png",
            hover_icon="ui/畅意快剪/切图/停止2@3x.png",
            pressed_icon="ui/畅意快剪/切图/停止3@3x.png"
        )
        # self.stopButton.setIcon(QIcon("ui/畅意快剪/切图/停止1@3x.png"))
        self.stopButton.setIconSize(QSize(68, 68))
        self.stopButton.setStyleSheet("border-right:2px solid #000000")
        self.stopButton.clicked.connect(self.stopClicked)

        # 显示播放时长
        self.labelDuration = QLabel()
        self.labelDuration.setStyleSheet("font-size: 20px; padding: 10px; padding-left: 20px ")
        # self.labelDuration.setText(f'00:00:00   /   00:00:00')
        self.labelDuration.setText('00:00:00\t'+'<font color=#A5A5A5>/\t00:00:00</font>')

        self.totalTime = QTime(0, 0, 0, 0)
        self.currentTime = QTime(0, 0, 0, 0)

        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)





        # 当前播放的进度，显示调整视频进度条
        self.timeSlider = QSlider(self)
        # self.timeSlider.set
        self.timeSlider.setOrientation(Qt.Horizontal)
        self.timeSlider.setValue(0)
        self.timeSlider.setMinimum(0)
        self.mediaPlayer.positionChanged.connect(self.get_time)
        self.timeSlider.sliderPressed.connect(self.pauseClicked)
        self.timeSlider.sliderMoved.connect(self.change_time)
        self.timeSlider.sliderReleased.connect(self.playClicked)
        # 修改进度条的样式表
        self.timeSlider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                height: 3px; /* 设置进度条的高度 */
                background: #000000; /* 设置进度条的背景色 */
            }

            QSlider::handle:horizontal {
                background: #D9D9D9; /* 设置滑块的背景色 */
                border: none; /* 去掉滑块的边框 */
                width: 12px; /* 设置滑块的宽度 */
                height: 10px; /* 设置滑块的高度 */
                margin: -5px 0; /* 调整滑块位置使其居中 */
                border-radius: 6px; /* 设置滑块的圆角使其成为圆形 */
            }

            QSlider::sub-page:horizontal {
                background: #FAE100; /* 设置已填充部分的颜色（播放进度的颜色） */
            }

            QSlider{
                border:0px;
            }

            """
        )
        self.timeSliderOut = QWidget()
        self.timeSliderOut.setFixedHeight(36)
        self.timeSliderOut.setStyleSheet("border-top:2px solid #000000; border-bottom:2px solid #000000; padding-left:5px")

        timeSliderOutLay = QHBoxLayout()
        timeSliderOutLay.addWidget(self.timeSlider)
        timeSliderOutLay.setSpacing(0)
        timeSliderOutLay.setContentsMargins(0, 0, 0, 0)
        self.timeSliderOut.setLayout(timeSliderOutLay)



        # button的布局
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.playButton)
        buttonLayout.addWidget(self.pauseButton)
        buttonLayout.addWidget(self.stopButton)
        buttonLayout.addWidget(self.labelDuration)
        buttonLayout.addStretch(1)

        buttonLayout.addWidget(self.processingText)
        buttonLayout.addWidget(self.fileSlide)
        buttonLayout.addWidget(self.submit_Button)
        buttonLayout.addWidget(self.file_Button)
        # buttonLayout.addWidget(self.submit_Button2)
        # buttonLayout.setContentsMargins(5, 5, 5, 5)  # 上、右、下、左的边距都设置为20像素


        leftWidget = QWidget()
        leftLayout = QVBoxLayout(leftWidget)
        leftLayout.addWidget(self.titleText)
        leftLayout.addWidget(self.videoWidgetOut)
        leftLayout.addWidget(self.timeSliderOut)
        leftLayout.addLayout(buttonLayout)
        leftLayout.setSpacing(0)
        leftLayout.setContentsMargins(0, 0, 0, 0)




        # 右侧布局
        # # 产生两个窗口
        # grid_layout = QGridLayout()
        rightWidget = QWidget()
        rightWidget.setStyleSheet(" background-color: black;")
        display = QVBoxLayout(rightWidget) #创建一个垂直布局管理器 display，它将用于管理 central 部件中的小部件的位置和大小。垂直布局意味着小部件将按垂直方向排列。
        
        # 窗口
        self.chatLayout = QVBoxLayout()
        self.textEdit = ChatWidget()
        self.chatLayout.addWidget(self.textEdit)

        bubble_message_re = BubbleMessage("欢迎来到畅意快剪！请先上传视频文件，点击视频框下方剪辑按钮，或在输入简单描述后点击输入框下方快剪按钮，开启一场轻松的剪辑之旅吧！", 'ui/畅意快剪/切图/小人@3x.png', Type=MessageType.Text, is_send=False)
        self.textEdit.add_message_item(bubble_message_re)

        # 输入框
        self.inputEdit = QTextEdit()
        self.inputEdit.setFixedHeight(208)
        self.inputEdit.setStyleSheet("color:rgba(255, 255, 255, 0.6); padding:20px")
        self.inputEdit.setPlaceholderText("写下你的创意试试吧。")
        self.inputEditOut = QWidget()
        self.inputEditOut.setFixedHeight(208)
        self.inputEditOutLay = QHBoxLayout()
        self.inputEditOutLay.setSpacing(0)
        self.inputEditOutLay.setContentsMargins(0, 0, 0, 0)
        self.inputEditOutLay.addWidget(self.inputEdit)
        self.inputEditOut.setStyleSheet("background-color:#141517; color:rgba(255, 255, 255, 0.6); border:2px solid #4B4B4E; border-radius:16px ;margin:0px 28px; padding:20px")
        self.inputEditOut.setLayout(self.inputEditOutLay)

        # 提交输入
        self.rightCommitLayout = QHBoxLayout()
        # 设置布局的 margin（左、上、右、下分别为 10 像素）
        self.rightCommitLayout.setContentsMargins(15, 15, 15, 15)
        # 添加一个伸缩空间到水平布局中，将按钮推到右侧
        # self.rightCommitLayout.addStretch(1)

        # # 提交关键词剪辑
        # # cutCommitBton = qta.icon('fa.cut', color='white')
        # self.cutCommitButton = CircularButton(
        #     default_icon="ui/畅意快剪/切图/剪辑@3x.png",
        # )
        # # self.cutCommitButton.setText("剪辑")
        # self.cutCommitButton.clicked.connect(self.commitQuestionCut)
        # # self.cutCommitButton.setIcon(cutCommitBton)
        # # self.commitButton.setIconSize(QSize(32, 32))

        # 创建 QPushButton
        self.cutCommitBton = QPushButton()
        self.cutCommitBton.setFixedSize(240,70)
        # 设置按钮的文字
        self.cutCommitBton.setText("剪辑")
        # 设置按钮的图标
        self.cutCommitBton.setIcon(QIcon("ui/畅意快剪/切图/剪辑@3x.png"))  # 替换为你的图标路径
        # 设置图标在文字前的位置
        self.cutCommitBton.setIconSize(QSize(32, 32))  # 可根据需要调整图标大小
        self.cutCommitBton.setStyleSheet("border-radius:8px; background-color:#FAE100;color:black;")
        self.cutCommitBton.clicked.connect(self.commitQuestionCut)
        self.rightCommitLayout.addWidget(self.cutCommitBton)

        # 提交对话
        self.commitButton = QPushButton()
        self.commitButton.clicked.connect(self.commitQuestion)
        self.commitButton.setFixedSize(240,70)
        # 设置按钮的文字
        self.commitButton.setText("发送")
        # 设置按钮的图标
        self.commitButton.setIcon(QIcon("ui/畅意快剪/切图/发送@3x.png"))  # 替换为你的图标路径
        # 设置图标在文字前的位置
        self.commitButton.setIconSize(QSize(32, 32))  # 可根据需要调整图标大小
        self.commitButton.setStyleSheet("border-radius:8px; background-color:#4B4B4E;color:#FAE100;")

        self.rightCommitLayout.addWidget(self.commitButton)
        # self.rightCommitLayout.addStretch(1)



        # 大模型下拉菜单
        self.comboBox = QComboBox(self)
        # self.comboBox.setFixedSize(574,64)
        self.comboBox.setFixedHeight(64)
        # self.comboBox.setStyleSheet("background-color:#3A3C40; margin:0px; padding-left:20px; border:0px")
        # 创建 QListView 并设置为 comboBox 的视图
        self.comboBox.setStyleSheet("""
            QComboBox {
                background-color:#3A3C40; 
                margin:0px; 
                padding-left:20px; 
                border:0px；
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right; /* 位置 */
                width: 64px;
                border:0px;

            }
            QComboBox::down-arrow {
                image: url("ui/畅意快剪/切图/下拉1@2x.png"); /* 下拉箭头图片 */
                width: 56px;
                height: 56px;
            }
            QComboBox QAbstractItemView {
                # selection-background-color: #1E1E1E;
                # selection-color: black;
                # background: white;
                # outline: 0px; /* 移除高亮边框 */
            }
        """)

        self.comboBox.addItem("GPT")
        self.comboBox.addItem("GPT(备用)")
        self.comboBox.addItem("Claude")
        self.comboBox.addItem("智谱")
        self.comboBox.addItem("通义千问")
        self.comboBox.addItem("零一万物")
        # 可以设置默认选中的项
        self.comboBox.setCurrentIndex(0)  # 默认选择第一个选项
        # 绑定 currentIndexChanged 信号到一个槽函数
        self.comboBox.currentIndexChanged.connect(self.on_combobox_changed)

        display.addWidget(self.comboBox)



        display.addLayout(self.chatLayout)
        # display.addLayout(self.rightCommitLayout)
        display.addWidget(self.inputEditOut)
        display.addLayout(self.rightCommitLayout)
        display.setSpacing(0)
        display.setContentsMargins(0, 0, 0, 0)




        splitter = QSplitter()
        splitter.addWidget(leftWidget)
        splitter.addWidget(rightWidget)
        splitter.setSizes([1576,574])
        splitter.setStyleSheet("""
            QSplitter {
                border: 2px solid black;  /* 设置 QSplitter 的整体边框 */
            }
        """)                       

        mainLayout = QVBoxLayout(central)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(self.titleBarOut)
        mainLayout.addWidget(splitter)

    def on_combobox_changed(self, index):
        # 获取当前选中的文本
        selected_item = self.comboBox.itemText(index)

        # 根据选项修改 self.model 的值
        if selected_item == "GPT":
            self.model = 0
        elif selected_item == "GPT（备用）":
            self.model = 1
        elif selected_item == "Claude":
            self.model = 2
        elif selected_item == "智谱":
            self.model = 3
        elif selected_item == "通义千问":
            self.model = 4
        elif selected_item == "零一万物":
            self.model = 5

        # 打印新的 model 值以进行调试
        print(f"Model changed to: {self.model}")


    def updateFileSlide(self, i):
        self.fileSlide.setText("视频处理： <font color=#FAE100>" + str(i) + "%</font>")
    
    def playClicked(self):
        self.mediaPlayer.play()
        self.playButton.hide()
        self.pauseButton.show()

        # 获取获得进度条进度
    def get_time(self, num):
        self.timeSlider.setMaximum(self.mediaPlayer.duration())
        self.timeSlider.setValue(num)

    def change_time(self, num):
        self.mediaPlayer.setPosition(num)

    def commitQuestion(self):
        text = self.inputEdit.toPlainText()

        bubble_message = BubbleMessage(text, '', Type=MessageType.Text, is_send=True)
        self.textEdit.add_message_item(bubble_message)
        self.inputEdit.clear()
        QCoreApplication.processEvents()  # 强制更新GUI



        def QA_finished(response):
            bubble_message_re = BubbleMessage(response, 'ui/畅意快剪/切图/小人@3x.png', Type=MessageType.Text, is_send=False)
            self.textEdit.add_message_item(bubble_message_re)


        self.thread = SimpleQAThread(text, self.cykj, self.file_paths)
        self.thread.finished.connect(QA_finished)  # 任务完成后的回调函数
        self.thread.start()






    def pauseClicked(self):
        self.mediaPlayer.pause()
        self.playButton.show()
        self.pauseButton.hide()

    def stopClicked(self):
        self.mediaPlayer.stop()

    def selectFiles(self):
        file_dialog = QFileDialog(self)
        self.file_paths, _ = file_dialog.getOpenFileName(self, "选择文件")
        a = self.file_paths
        b = a.split('/')
        L = len(b)
        c = b[L - 1].split('.')[0]

        video_extensions = {'mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'webm'}
        if not b[L - 1].split('.')[1] in video_extensions:
            self.processingText.setText("非视频文件无法上传！")
            self.processingText.show()
            self.file_paths = "#"
            return


        self.titleText.setText(c)
        self.processingText.setText(a)
        self.processingText.show()
        
        

    def processFiles(self, cut_way):
        a = self.file_paths
        b = a.split('/')
        L = len(b)
        c = b[L - 1].split('.')[0]
        self.cut_way = cut_way
        srt_cut_path = '/'.join(b[:-2]) + '/video/' + c + "_cut.srt"

        if a == "#":
            self.processingText.setText("请先选择视频文件！")
            self.processingText.show()
            return


        self.processingText.setText("正在提取字幕...")
        self.processingText.show()
        startTime = time.time()
        Funclisten.setIndex(0)
        Funclisten.start()




        def process3_finished():
            # self.videoFile = QUrl("file:"+a.split('.')[0]+"_cut_srt."+a.split('.')[1])
            self.videoFile = QUrl("file:"+a.split('.')[0]+"_cut."+a.split('.')[1])
            mediaContent = QMediaContent(self.videoFile)
            self.mediaPlayer.setMedia(mediaContent)
            self.mediaPlayer.setVideoOutput(self.videoWidget)
            self.processingText.setText("剪辑完成！")
            endTime = time.time()
            print(startTime-endTime)
            Funclisten.setIndex(100)
            Funclisten.start()
            self.processingText.show()



        def process2_finished():
            if self.cut_way == 1:
                textName = '/'.join(b[:-2]) + '/video/' + c + "_summary.txt"
                with open(textName, 'r', encoding='utf-8') as file:
                    content = file.read()
                    bubble_message = BubbleMessage(content, 'ui/畅意快剪/切图/小人@3x.png', Type=MessageType.Text, is_send=False)
                    self.textEdit.add_message_item(bubble_message)
            else:
                textName = '/'.join(b[:-2]) + '/video/' + c + "_top.txt"
                # with open(textName, 'r', encoding='utf-8') as file:
                #     content = file.read()
                #     bubble_message = BubbleMessage(content, 'ui/畅意快剪/切图/小人@3x.png', Type=MessageType.Text, is_send=False)
                #     self.textEdit.add_message_item(bubble_message)
                content = "好的，视频已剪辑完成。"
                bubble_message = BubbleMessage(content, 'ui/畅意快剪/切图/小人@3x.png', Type=MessageType.Text, is_send=False)
                self.textEdit.add_message_item(bubble_message)
            # print("初始化完成")
            self.processingText.setText("初始化完成!")

            if not os.path.exists(srt_cut_path):
                self.processingText.setText("请先进行视频处理！")
                self.processingText.show()
                return
            
            if a == "#":
                self.processingText.setText("请先选择视频文件！")
                self.processingText.show()
                return

            output_path = a.split('.')[0]+"_cut."+a.split('.')[1]

            self.processingText.setText("正在剪辑...")
            self.processingText.show()
            self.thread = CutVideoThread(self.file_paths, srt_cut_path, output_path, self.cut_way)
            self.thread.finished.connect(process3_finished)  # 任务完成后的回调函数
            self.thread.start()




        def process1_finished():
            self.processingText.setText("字幕提取完成")
            self.processingText.show()

            # 暂时注释
            textName = '/'.join(b[:-2]) + '/video/' + c + "_summary.txt"
            if self.cut_way == 1: 
                self.processingText.setText("正在处理视频...")
                self.processingText.show()
                QCoreApplication.processEvents()  # 强制更新GUI
                #lan
                Funclisten.setIndex(10)
                Funclisten.start()
                self.thread = VideoProcessThread(self.cykj, self.file_paths, "./clip_tmp", textName)
                self.thread.finished.connect(process2_finished)  # 任务完成后的回调函数
                self.thread.start()
            else:
                self.processingText.setText("正在处理视频...")
                self.processingText.show()
                QCoreApplication.processEvents()  # 强制更新GUI
                # video_process_usercut(self.file_paths, "./clip_tmp", self.user_keywords)
                # lan
                self.thread = VideoProcessUsercutThread(self.cykj, self.file_paths, "./clip_tmp", self.user_keywords)
                self.thread.finished.connect(process2_finished)  # 任务完成后的回调函数
                self.thread.start()

            # # 空线程
            # self.processingText.setText("正在处理视频...")
            # self.processingText.show()
            # self.thread = EmptyThread()
            # self.thread.finished.connect(process2_finished)  # 任务完成后的回调函数
            # self.thread.start()



        textName = '/'.join(b[:-2]) + '/media/' + c + ".srt"
        # 创建线程并启动
        self.thread = Video2SrtThread(self.file_paths, textName)
        self.thread.finished.connect(process1_finished)  # 任务完成后的回调函数
        self.thread.start()


    

    def clip(self):
        a = self.file_paths
        b = a.split('/')
        L = len(b)
        c = b[L - 1].split('.')[0]
        srt_cut_path = '/'.join(b[:-2]) + '/video/' + c + "_cut.srt"
        
        if not os.path.exists(srt_cut_path):
            self.processingText.setText("请先进行视频处理！")
            self.processingText.show()
            return
        
        if a == "#":
            self.processingText.setText("请先选择视频文件！")
            self.processingText.show()
            return

        output_path = a.split('.')[0]+"_cut."+a.split('.')[1]



        def process3_finished():
            # self.videoFile = QUrl("file:"+a.split('.')[0]+"_cut_srt."+a.split('.')[1])
            self.videoFile = QUrl("file:"+a.split('.')[0]+"_cut."+a.split('.')[1])
            mediaContent = QMediaContent(self.videoFile)
            self.mediaPlayer.setMedia(mediaContent)
            self.mediaPlayer.setVideoOutput(self.videoWidget)
            self.processingText.setText("剪辑完成！")
            self.processingText.show()


        self.processingText.setText("正在剪辑...")
        self.processingText.show()
        self.thread = CutVideoThread(self.file_paths, srt_cut_path, output_path, self.cut_way)
        self.thread.finished.connect(process3_finished)  # 任务完成后的回调函数
        self.thread.start()



    def button_clicked(self, shape_id):
        # 处理按钮点击事件，确保互斥
        if shape_id == 1:
            self.Ovalbutton2.selected = False
            self.Ovalbutton2.setChecked(False)
            self.model = 1
        elif shape_id == 2:
            self.Ovalbutton1.selected = False
            self.Ovalbutton1.setChecked(False)
            self.model = 2
        status1 = shape_id
        if status1 == 1:
            print(f"Shape 1 selected")
        else:
            print(f"Shape 2 selected")

    # 显示播放时长
    def durationChanged(self, duration):
        self.timeSlider.setRange(0, duration)
        self.totalTime = QTime(0, 0, 0, 0)
        self.totalTime = self.totalTime.addMSecs(duration)
        self.labelDuration.setText(f'00:00:00 / {self.totalTime.toString("hh:mm:ss")}')

    def positionChanged(self, position):
        self.timeSlider.setValue(position)
        self.currentTime = QTime(0, 0, 0, 0)
        self.currentTime = self.currentTime.addMSecs(position)
        self.labelDuration.setText(f'{self.currentTime.toString("hh:mm:ss")} / {self.totalTime.toString("hh:mm:ss")}')

    
    def commitQuestionCut(self):
        text = self.inputEdit.toPlainText()
        self.user_keywords = text

        bubble_message = BubbleMessage(text, '', Type=MessageType.Text, is_send=True)
        self.textEdit.add_message_item(bubble_message)
        self.inputEdit.clear()
      
        bubble_message_re = BubbleMessage("好的，正在根据您的个性化剪辑方案为您处理视频...", 'ui/畅意快剪/切图/小人@3x.png', Type=MessageType.Text, is_send=False)
        self.textEdit.add_message_item(bubble_message_re)
        QCoreApplication.processEvents()  # 强制更新GUI

        self.processFiles(cut_way=2)


def check_port_in_use(port):
    """
    Check if any process is using the specified port.
    """
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
            return True
    return False



def main():
    # #启动服务器
    # port_to_check = 45679
    # if check_port_in_use(port_to_check):
    #     print(f"Port {port_to_check} is in use.")
    # else:
    #     print(f"Port {port_to_check} is not in use.")
    #     # 启动 app.py 进程
    #     # 创建线程并启动
    #     thread = serverThread()
    #     thread.start()

    Qss=qss # 直接将qss这个字符串给QSS即可
    app = QApplication(sys.argv)

    app.setStyleSheet(Qss)

    ex = MainApp()
    # 设置窗口标志，确保窗口可以移动
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
