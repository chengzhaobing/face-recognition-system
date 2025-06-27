# 人脸识别系统

基于Python OpenCV和PyQt5开发的人脸识别系统，支持人脸数据采集、模型训练和实时识别功能。

## 项目简介

本项目是一个完整的人脸识别解决方案，采用现代化的图形界面设计，提供了友好的用户交互体验。系统主要功能包括用户管理、人脸信息录入、训练分类器、人脸检测与识别等。

## 技术特点

### 核心算法

1. **Haar级联分类器**：用于人脸检测
   - 使用OpenCV提供的预训练模型
   - 快速准确的人脸区域定位

2. **LBPH (Local Binary Patterns Histograms) 算法**：用于人脸识别
   - 对光照变化有较强的鲁棒性
   - 能够处理一定程度的表情、姿态变化
   - 训练速度快，识别效率高

### 技术栈

- **前端界面**: PyQt5
- **计算机视觉**: OpenCV
- **图像处理**: PIL/Pillow
- **数据库**: MySQL
- **数值计算**: NumPy
- **开发语言**: Python 3.7+

## 系统功能

### 主要功能模块

1. **用户管理系统**
   - 用户注册与登录
   - 用户权限管理
   - 登录记录追踪

2. **人脸数据采集**
   - 实时摄像头人脸检测
   - 自动人脸区域提取
   - 批量人脸图像保存

3. **模型训练**
   - LBPH算法模型训练
   - 自动特征提取
   - 模型文件保存与管理

4. **人脸识别**
   - 实时人脸检测与识别
   - 置信度显示
   - 识别结果记录

5. **数据管理**
   - 识别记录存储
   - 用户活动日志
   - 数据统计分析

## 安装与配置

### 环境要求

- Python 3.7 或更高版本
- MySQL 5.7 或更高版本
- 摄像头设备

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/chengzhaobing/face-recognition-system.git
   cd face-recognition-system
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置数据库**
   - 安装MySQL数据库
   - 修改 `db_connection.py` 中的数据库连接参数
   - 系统会自动创建所需的数据库和表

4. **准备数据文件**
   ```bash
   mkdir -p data/classifiers
   ```
   - 下载 `haarcascade_frontalface_default.xml` 文件到 `data/` 目录

### 运行程序

```bash
python face_recognition_pyqt.py
```

## 使用说明

### 首次使用

1. **用户注册**
   - 点击"注册"按钮
   - 输入用户名和密码（密码至少8位）
   - 完成注册

2. **用户登录**
   - 输入注册的用户名和密码
   - 点击"登录"进入主界面

### 人脸识别流程

1. **数据采集**
   - 点击"人脸数据采集"
   - 输入要采集的人员姓名
   - 面对摄像头，系统会自动检测并保存人脸图像
   - 按 'q' 键结束采集

2. **模型训练**
   - 点击"训练识别模型"
   - 选择要训练的人员
   - 系统自动训练LBPH识别模型

3. **开始识别**
   - 点击"开始人脸识别"
   - 选择要识别的人员模型
   - 面对摄像头进行实时识别
   - 按 'q' 键退出识别

## 项目结构

```
face-recognition-system/
├── face_recognition_pyqt.py    # 主程序文件
├── Detector.py                  # 人脸检测与识别模块
├── create_dataset.py           # 人脸数据采集模块
├── create_classifier.py        # 模型训练模块
├── db_connection.py            # 数据库连接模块
├── requirements.txt            # 依赖包列表
├── .gitignore                 # Git忽略文件
├── README.md                  # 项目说明文档
└── data/                      # 数据目录
    ├── haarcascade_frontalface_default.xml  # 人脸检测模型
    ├── classifiers/           # 训练好的分类器
    └── [person_name]/         # 个人人脸数据目录
```

## 数据库设计

### 用户表 (users)
- `id`: 用户ID（主键）
- `username`: 用户名（唯一）
- `password`: 密码
- `created_at`: 创建时间

### 登录记录表 (login_records)
- `id`: 记录ID（主键）
- `user_id`: 用户ID（外键）
- `login_time`: 登录时间

### 识别记录表 (recognition_records)
- `id`: 记录ID（主键）
- `user_id`: 用户ID（外键）
- `person_name`: 识别的人员姓名
- `recognition_time`: 识别时间
- `confidence`: 识别置信度

## 注意事项

1. **摄像头权限**：确保程序有访问摄像头的权限
2. **光照条件**：在光线充足的环境下使用效果更佳
3. **人脸角度**：正面人脸识别效果最好
4. **数据安全**：请妥善保管数据库密码
5. **模型文件**：训练好的模型文件请及时备份

## 常见问题

### Q: 摄像头无法打开
A: 检查摄像头是否被其他程序占用，或尝试更改摄像头索引号

### Q: 识别准确率低
A: 增加训练样本数量，确保采集时光照充足且人脸清晰

### Q: 数据库连接失败
A: 检查MySQL服务是否启动，确认连接参数是否正确

## 开发计划

- [ ] 支持多人同时识别
- [ ] 添加人脸活体检测
- [ ] 优化识别算法性能
- [ ] 增加Web界面支持
- [ ] 添加人脸比对功能
- [ ] 支持更多数据库类型

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目采用MIT许可证，详情请查看LICENSE文件。

## 联系方式

如有问题或建议，请通过GitHub Issues联系。