import cv2
import numpy as np
import os
from datetime import datetime
from db_connection import record_recognition

class Detector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
        
    def recognize_face(self, person_name):
        """人脸识别主函数"""
        # 加载训练好的分类器
        classifier_path = f'data/classifiers/{person_name}.xml'
        if not os.path.exists(classifier_path):
            print(f"错误：找不到 {person_name} 的分类器文件")
            return
            
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(classifier_path)
        
        # 打开摄像头
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("错误：无法打开摄像头")
            return
            
        print(f"开始识别 {person_name}，按 'q' 键退出")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 检测人脸
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            for (x, y, w, h) in faces:
                # 提取人脸区域
                face_roi = gray[y:y+h, x:x+w]
                
                # 进行人脸识别
                label, confidence = recognizer.predict(face_roi)
                
                # 绘制矩形框
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # 显示识别结果
                if confidence < 100:  # 置信度阈值
                    result_text = f"{person_name}: {confidence:.1f}%"
                    color = (0, 255, 0)  # 绿色
                    
                    # 记录识别结果到数据库
                    record_recognition(1, person_name, confidence)  # 假设用户ID为1
                    
                    # 保存识别结果图片
                    self.save_recognition_result(frame, person_name, confidence)
                else:
                    result_text = "Unknown"
                    color = (0, 0, 255)  # 红色
                
                # 在图像上显示文本
                cv2.putText(frame, result_text, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            # 显示图像
            cv2.imshow('Face Recognition', frame)
            
            # 按 'q' 键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # 释放资源
        cap.release()
        cv2.destroyAllWindows()
        
    def save_recognition_result(self, frame, person_name, confidence):
        """保存识别结果图片"""
        # 创建保存目录
        save_dir = "recognition_results"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{save_dir}/{person_name}_{confidence:.1f}_{timestamp}.jpg"
        
        # 保存图片
        cv2.imwrite(filename, frame)
        print(f"识别结果已保存: {filename}")
        
    def detect_faces(self, image_path):
        """检测图片中的人脸"""
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            print(f"错误：无法读取图片 {image_path}")
            return []
            
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return faces
        
    def extract_face_features(self, image_path):
        """提取人脸特征"""
        faces = self.detect_faces(image_path)
        
        if len(faces) == 0:
            return None
            
        # 读取图片并转换为灰度图
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 提取第一个检测到的人脸
        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        
        # 调整大小为统一尺寸
        face_roi = cv2.resize(face_roi, (100, 100))
        
        return face_roi

if __name__ == "__main__":
    detector = Detector()
    
    # 示例：识别特定人员
    person_name = input("请输入要识别的人员姓名: ")
    detector.recognize_face(person_name)