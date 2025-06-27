import cv2
import numpy as np
import os
from PIL import Image

def create_classifier(person_name):
    """创建人脸分类器"""
    # 数据路径
    data_path = f"data/{person_name}"
    
    if not os.path.exists(data_path):
        print(f"错误：找不到 {person_name} 的数据目录")
        return False
    
    # 创建分类器保存目录
    classifier_dir = "data/classifiers"
    if not os.path.exists(classifier_dir):
        os.makedirs(classifier_dir)
    
    # 准备训练数据
    faces = []
    labels = []
    
    print(f"正在加载 {person_name} 的训练数据...")
    
    # 遍历数据目录中的所有图片
    for filename in os.listdir(data_path):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image_path = os.path.join(data_path, filename)
            
            # 读取图片并转换为灰度图
            image = Image.open(image_path).convert('L')
            image_np = np.array(image, 'uint8')
            
            # 从文件名中提取ID（假设文件名格式为：数字+姓名.jpg）
            try:
                # 提取文件名中的数字部分作为ID
                file_id = int(''.join(filter(str.isdigit, filename.split('.')[0])))
            except:
                file_id = 1  # 默认ID
            
            faces.append(image_np)
            labels.append(file_id)
    
    if len(faces) == 0:
        print(f"错误：在 {data_path} 中没有找到有效的图片文件")
        return False
    
    print(f"加载了 {len(faces)} 张训练图片")
    
    # 创建LBPH人脸识别器
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    print("开始训练分类器...")
    
    # 训练分类器
    recognizer.train(faces, np.array(labels))
    
    # 保存分类器
    classifier_path = f"{classifier_dir}/{person_name}.xml"
    recognizer.save(classifier_path)
    
    print(f"分类器训练完成，已保存到: {classifier_path}")
    
    # 更新分类器列表
    update_classifier_list(person_name)
    
    return True

def update_classifier_list(person_name):
    """更新分类器列表文件"""
    classifier_file = "classifiers_list.txt"
    
    # 读取现有分类器列表
    existing_classifiers = []
    if os.path.exists(classifier_file):
        with open(classifier_file, 'r', encoding='utf-8') as f:
            existing_classifiers = [line.strip() for line in f.readlines()]
    
    # 添加新分类器（如果不存在）
    if person_name not in existing_classifiers:
        existing_classifiers.append(person_name)
        
        # 写回文件
        with open(classifier_file, 'w', encoding='utf-8') as f:
            for classifier in existing_classifiers:
                f.write(f"{classifier}\n")
        
        print(f"已将 {person_name} 添加到分类器列表")

def batch_create_classifiers():
    """批量创建分类器"""
    data_dir = "data"
    
    if not os.path.exists(data_dir):
        print("错误：数据目录不存在")
        return
    
    # 获取所有人员目录
    persons = [d for d in os.listdir(data_dir) 
              if os.path.isdir(os.path.join(data_dir, d)) and d != "classifiers"]
    
    if not persons:
        print("没有找到人员数据目录")
        return
    
    print(f"找到 {len(persons)} 个人员数据目录")
    
    for person in persons:
        print(f"\n正在为 {person} 创建分类器...")
        success = create_classifier(person)
        
        if success:
            print(f"{person} 的分类器创建成功")
        else:
            print(f"{person} 的分类器创建失败")
    
    print("\n批量分类器创建完成")

def test_classifier(person_name):
    """测试分类器"""
    classifier_path = f"data/classifiers/{person_name}.xml"
    
    if not os.path.exists(classifier_path):
        print(f"错误：找不到 {person_name} 的分类器文件")
        return
    
    # 加载分类器
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(classifier_path)
    
    # 加载测试图片
    test_data_path = f"data/{person_name}"
    
    if not os.path.exists(test_data_path):
        print(f"错误：找不到 {person_name} 的测试数据")
        return
    
    print(f"测试 {person_name} 的分类器...")
    
    correct_predictions = 0
    total_predictions = 0
    
    for filename in os.listdir(test_data_path):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image_path = os.path.join(test_data_path, filename)
            
            # 读取并预处理图片
            image = Image.open(image_path).convert('L')
            image_np = np.array(image, 'uint8')
            
            # 进行预测
            label, confidence = recognizer.predict(image_np)
            
            total_predictions += 1
            
            # 判断预测是否正确（这里简化处理）
            if confidence < 100:  # 置信度阈值
                correct_predictions += 1
                print(f"✓ {filename}: 置信度 {confidence:.2f}")
            else:
                print(f"✗ {filename}: 置信度 {confidence:.2f} (未识别)")
    
    if total_predictions > 0:
        accuracy = (correct_predictions / total_predictions) * 100
        print(f"\n测试结果：")
        print(f"总测试图片: {total_predictions}")
        print(f"正确识别: {correct_predictions}")
        print(f"准确率: {accuracy:.2f}%")
    else:
        print("没有找到测试图片")

if __name__ == "__main__":
    print("人脸分类器训练工具")
    print("1. 训练单个分类器")
    print("2. 批量训练分类器")
    print("3. 测试分类器")
    
    choice = input("请选择操作 (1-3): ").strip()
    
    if choice == '1':
        person_name = input("请输入人员姓名: ").strip()
        if person_name:
            create_classifier(person_name)
        else:
            print("姓名不能为空")
    
    elif choice == '2':
        batch_create_classifiers()
    
    elif choice == '3':
        person_name = input("请输入要测试的人员姓名: ").strip()
        if person_name:
            test_classifier(person_name)
        else:
            print("姓名不能为空")
    
    else:
        print("无效选择")