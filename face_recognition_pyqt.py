import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
import mysql.connector
from mysql.connector import Error
from Detector import *
from create_classifier import *
from create_dataset import *
from db_connection import *

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # 打开视频文件
        cap = cv2.VideoCapture('videos/bg.mp4')
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
            else:
                # 视频播放完毕，重新开始
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("人脸识别系统 - 登录")
        self.setFixedSize(800, 600)
        self.setWindowIcon(QIcon('icon.ico'))
        
        # 设置背景
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
        """)
        
        self.init_ui()
        
        # 启动视频线程
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_background)
        self.thread.start()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建背景标签
        self.background_label = QLabel()
        self.background_label.setGeometry(0, 0, 800, 600)
        self.background_label.setScaledContents(True)
        
        # 创建登录框
        login_frame = QFrame()
        login_frame.setFixedSize(350, 400)
        login_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
        """)
        
        # 标题
        title_label = QLabel("人脸识别系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin: 20px 0;
            }
        """)
        
        # 用户名输入
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                margin: 5px 0;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        
        # 密码输入
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                margin: 5px 0;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        
        # 登录按钮
        login_btn = QPushButton("登录")
        login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd8, stop:1 #6a4190);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4e5bc6, stop:1 #5e377e);
            }
        """)
        login_btn.clicked.connect(self.login)
        
        # 注册按钮
        register_btn = QPushButton("注册")
        register_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #667eea;
                border: 2px solid #667eea;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin: 5px 0;
            }
            QPushButton:hover {
                background: #667eea;
                color: white;
            }
        """)
        register_btn.clicked.connect(self.show_register)
        
        # 布局
        login_layout = QVBoxLayout(login_frame)
        login_layout.addWidget(title_label)
        login_layout.addWidget(self.username_input)
        login_layout.addWidget(self.password_input)
        login_layout.addWidget(login_btn)
        login_layout.addWidget(register_btn)
        login_layout.setContentsMargins(30, 30, 30, 30)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.background_label)
        
        # 将登录框居中
        overlay_layout = QVBoxLayout()
        overlay_layout.addStretch()
        overlay_layout.addWidget(login_frame, alignment=Qt.AlignCenter)
        overlay_layout.addStretch()
        
        overlay_widget = QWidget()
        overlay_widget.setLayout(overlay_layout)
        overlay_widget.setStyleSheet("background: transparent;")
        
        main_layout.addWidget(overlay_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
    def update_background(self, cv_img):
        """更新背景视频"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(800, 600, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.background_label.setPixmap(QPixmap.fromImage(p))
        
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "请输入用户名和密码！")
            return
            
        if verify_user(username, password):
            user_id = get_user_id(username)
            record_login(user_id)
            QMessageBox.information(self, "成功", "登录成功！")
            self.thread.stop()
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误！")
            
    def show_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
        
    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("用户注册")
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon('icon.ico'))
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("用户注册")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        
        # 用户名
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                margin: 5px;
            }
        """)
        
        # 密码
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码（至少8位）")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                margin: 5px;
            }
        """)
        
        # 确认密码
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("请确认密码")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                margin: 5px;
            }
        """)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        register_btn = QPushButton("注册")
        register_btn.setStyleSheet("""
            QPushButton {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #5a6fd8;
            }
        """)
        register_btn.clicked.connect(self.register)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #ccc;
                color: #333;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #bbb;
            }
        """)
        cancel_btn.clicked.connect(self.close)
        
        button_layout.addWidget(register_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addWidget(title)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password_input)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "警告", "请填写所有字段！")
            return
            
        if len(password) < 8:
            QMessageBox.warning(self, "警告", "密码至少需要8位！")
            return
            
        if password != confirm_password:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致！")
            return
            
        if register_user(username, password):
            QMessageBox.information(self, "成功", "注册成功！")
            self.close()
        else:
            QMessageBox.warning(self, "错误", "用户名已存在或注册失败！")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("人脸识别系统")
        self.setFixedSize(1000, 700)
        self.setWindowIcon(QIcon('icon.ico'))
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel("人脸识别系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #2c3e50;
                margin: 20px 0;
                padding: 20px;
                background: white;
                border-radius: 15px;
                border: 2px solid #3498db;
            }
        """)
        
        # 功能按钮区域
        buttons_widget = QWidget()
        buttons_layout = QGridLayout(buttons_widget)
        buttons_layout.setSpacing(20)
        
        # 创建功能按钮
        self.create_function_buttons(buttons_layout)
        
        # 状态栏
        status_label = QLabel("系统就绪")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("""
            QLabel {
                background: #2c3e50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(buttons_widget)
        main_layout.addWidget(status_label)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
    def create_function_buttons(self, layout):
        # 按钮配置
        buttons_config = [
            ("人脸数据采集", "采集人脸图像数据", "#e74c3c", self.collect_data),
            ("训练识别模型", "训练人脸识别分类器", "#f39c12", self.train_model),
            ("开始人脸识别", "启动实时人脸识别", "#27ae60", self.start_recognition),
            ("查看识别记录", "查看历史识别记录", "#3498db", self.view_records)
        ]
        
        for i, (text, desc, color, callback) in enumerate(buttons_config):
            btn = self.create_styled_button(text, desc, color)
            btn.clicked.connect(callback)
            row = i // 2
            col = i % 2
            layout.addWidget(btn, row, col)
            
    def create_styled_button(self, text, description, color):
        btn = QPushButton()
        btn.setFixedSize(400, 120)
        
        # 创建按钮内容
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel(text)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: white;")
        
        desc = QLabel(description)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("font-size: 12px; color: rgba(255, 255, 255, 0.8);")
        
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 设置按钮样式
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                border: none;
                border-radius: 15px;
                color: white;
            }}
            QPushButton:hover {{
                background: {self.darken_color(color)};
                transform: scale(1.05);
            }}
            QPushButton:pressed {{
                background: {self.darken_color(color, 0.8)};
            }}
        """)
        
        # 将widget设置为按钮的布局
        btn_layout = QVBoxLayout(btn)
        btn_layout.addWidget(widget)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        return btn
        
    def darken_color(self, color, factor=0.9):
        """使颜色变暗"""
        # 简单的颜色变暗处理
        color_map = {
            "#e74c3c": "#c0392b",
            "#f39c12": "#d68910",
            "#27ae60": "#229954",
            "#3498db": "#2980b9"
        }
        return color_map.get(color, color)
        
    def collect_data(self):
        name, ok = QInputDialog.getText(self, '输入姓名', '请输入要采集人脸数据的人员姓名:')
        if ok and name:
            QMessageBox.information(self, "提示", f"开始采集 {name} 的人脸数据\n请面对摄像头，按 'q' 键结束采集")
            create_dataset(name)
            
    def train_model(self):
        # 获取可用的人员列表
        data_dir = "data"
        if not os.path.exists(data_dir):
            QMessageBox.warning(self, "错误", "数据目录不存在！")
            return
            
        persons = [d for d in os.listdir(data_dir) 
                  if os.path.isdir(os.path.join(data_dir, d)) and d != "classifiers"]
        
        if not persons:
            QMessageBox.warning(self, "错误", "没有找到人脸数据！请先采集数据。")
            return
            
        person, ok = QInputDialog.getItem(self, '选择人员', '请选择要训练的人员:', persons, 0, False)
        if ok and person:
            QMessageBox.information(self, "提示", f"开始训练 {person} 的识别模型...")
            create_classifier(person)
            QMessageBox.information(self, "完成", f"{person} 的识别模型训练完成！")
            
    def start_recognition(self):
        # 获取可用的分类器列表
        classifier_dir = "data/classifiers"
        if not os.path.exists(classifier_dir):
            QMessageBox.warning(self, "错误", "分类器目录不存在！")
            return
            
        classifiers = [f[:-4] for f in os.listdir(classifier_dir) 
                      if f.endswith('.xml')]
        
        if not classifiers:
            QMessageBox.warning(self, "错误", "没有找到训练好的模型！请先训练模型。")
            return
            
        person, ok = QInputDialog.getItem(self, '选择模型', '请选择要使用的识别模型:', classifiers, 0, False)
        if ok and person:
            QMessageBox.information(self, "提示", f"启动 {person} 的人脸识别\n按 'q' 键退出识别")
            detector = Detector()
            detector.recognize_face(person)
            
    def view_records(self):
        QMessageBox.information(self, "功能开发中", "识别记录查看功能正在开发中...")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 初始化数据库
    init_database()
    
    # 创建并显示登录窗口
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec_())