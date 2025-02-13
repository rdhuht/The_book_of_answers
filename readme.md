# 项目名称

一个基于 Tkinter 的桌面应用，叫做答案之书，来源于The Book Of Answers这本书籍，提供随机答案显示功能，并包含每天点击3次数限制等特性。

## 功能特性

- 采用 Tkinter 构建用户界面
- 随机选择答案并逐字显示
- 记录并限制每日点击次数
- 读取 JSON 数据文件作为答案库
- 记录应用运行日志
- 兼容 Windows 可执行文件（exe）运行

## 使用说明

### 1. 下载与解压

1. 访问 GitHub Releases 下载最新版本的 ZIP 文件。
2. 解压 ZIP 文件到任意目录。

### 2. 运行应用

- **Windows 用户**：
  - 进入解压后的文件夹，双击 `答案之书.exe` 运行。
- **源代码运行**（需要 Python 环境）：
  1. 确保已安装 Python 3。
  2. 运行以下命令安装依赖项（如有需要）：
     ```sh
     pip install -r requirements.txt
     ```
  3. 运行主程序：
     ```sh
     python main.py
     ```

### 3. 目录结构

```
|-- src/                  # 源代码文件夹
|   |-- answers.json      # 存储答案的 JSON 文件
|   |-- thoughts.txt      # 额外的文本数据
|   |-- logo.ico          # 应用图标文件
|-- requirements.txt      # 依赖库列表
|-- main.py               # 主程序
|-- README.md             # 本说明文档
```

## 依赖库

本项目依赖以下 Python 库（仅适用于源代码运行模式）：

```sh
pip install -r requirements.txt
```

## 打包
(.venv) 
```sh
pyinstaller 答案之书.spec
```

## 许可证

MIT License - 允许自由使用、修改和分发。详情请参阅 `LICENSE` 文件。

## 贡献指南

欢迎提交 Issue 或 Pull Request 以改进本项目！

## todo
Csv文件data/csv检查是否存在，开机时，不存在创建空csv文件 Mac上ico图标没显示出来


