import cv2
import os

def create_dataset(person_name):
    """创建人脸数据集"""
    # 创建数据目录
    data_dir = f"data/{person_name}"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # 加载人脸检测器
    face_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("错误：无法打开摄像头")
        return
    
    print(f"开始采集 {person_name} 的人脸数据")
    print("请面对摄像头，按 's' 键保存图片，按 'q' 键退出")
    
    count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 转换为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # 绘制人脸框
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # 提取人脸区域
            face_roi = gray[y:y+h, x:x+w]
            
            # 自动保存（也可以手动按's'保存）
            if len(faces) > 0:
                count += 1
                filename = f"{data_dir}/{count}{person_name}.jpg"
                cv2.imwrite(filename, face_roi)
                print(f"保存图片: {filename}")
                
                # 限制采集数量
                if count >= 300:
                    print(f"已采集 {count} 张图片，采集完成")
                    break
        
        # 显示图像
        cv2.imshow('Data Collection', frame)
        
        # 按键处理
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s') and len(faces) > 0:
            # 手动保存
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                count += 1
                filename = f"{data_dir}/{count}{person_name}.jpg"
                cv2.imwrite(filename, face_roi)
                print(f"手动保存图片: {filename}")
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"数据采集完成，共采集 {count} 张图片")
    
    # 更新姓名列表文件
    update_names_list(person_name)

def update_names_list(person_name):
    """更新姓名列表文件"""
    names_file = "nameslist.txt"
    
    # 读取现有姓名
    existing_names = []
    if os.path.exists(names_file):
        with open(names_file, 'r', encoding='utf-8') as f:
            existing_names = [line.strip() for line in f.readlines()]
    
    # 添加新姓名（如果不存在）
    if person_name not in existing_names:
        existing_names.append(person_name)
        
        # 写回文件
        with open(names_file, 'w', encoding='utf-8') as f:
            for name in existing_names:
                f.write(f"{name}\n")
        
        print(f"已将 {person_name} 添加到姓名列表")

def batch_create_dataset():
    """批量创建数据集"""
    print("批量数据采集模式")
    
    while True:
        person_name = input("请输入人员姓名（输入 'quit' 退出）: ").strip()
        
        if person_name.lower() == 'quit':
            break
            
        if not person_name:
            print("姓名不能为空")
            continue
            
        create_dataset(person_name)
        
        continue_choice = input("是否继续采集下一个人员的数据？(y/n): ").strip().lower()
        if continue_choice != 'y':
            break
    
    print("批量数据采集完成")

if __name__ == "__main__":
    choice = input("选择模式：1-单个采集，2-批量采集: ").strip()
    
    if choice == '1':
        person_name = input("请输入人员姓名: ").strip()
        if person_name:
            create_dataset(person_name)
        else:
            print("姓名不能为空")
    elif choice == '2':
        batch_create_dataset()
    else:
        print("无效选择")