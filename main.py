import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  # 导入 messagebox 模块，用于显示消息框
import random
import json
import logging
import os
import subprocess
import sys
import datetime
import csv
import time


# ----- 文件路径定义 -----
# 定义 JSON 答案文件、想法文件、图标文件和点击次数限制数据文件的相对路径
json_file = "./src/answers.json"  # JSON 答案文件路径
thoughts_file = "./src/thoughts.txt"  # 想法文件路径
ico_logo_file = "./src/logo.ico"  # 图标文件路径
log_file_path = './data/log.log'  # 定义日志文件路径
click_limit_file = "./data/click_limit.csv"  # 点击次数限制数据文件路径 (CSV 文件)

def get_base_path():
    """
    获取应用的基础路径。

    根据程序是否被打包为可执行文件（exe）来决定基础路径。
    如果是打包后的 exe，则基础路径为 exe 所在的目录；
    否则，为当前脚本运行的目录。

    Returns:
        str: 应用的基础路径。
    """
    if getattr(sys, 'frozen', False):
        # 如果 sys.frozen 为 True，说明程序是被打包为 exe 运行的
        base_path = os.path.dirname(sys.executable)  # 获取 exe 文件所在的目录
    else:
        base_path = os.path.abspath(".")  # 否则，返回当前工作目录的绝对路径

    data_path = os.path.join(base_path, 'data')
    if not os.path.exists(data_path):
        os.makedirs(data_path, exist_ok=True)
    return base_path


base_path = get_base_path()


# ----- 日志配置 -----
# 配置日志记录，将日志信息写入 'log.log' 文件
log_file_path = os.path.join(base_path, 'data', 'log.log')  # 日志文件存储在 data 目录
print(log_file_path)
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8')

logging.info("应用启动")  # 记录应用启动事件
logging.info(f"当前执行文件所在目录: {base_path}")  # 记录基础路径信息


def ensure_data_directory():
    """
    确保数据目录存在，如果不存在则创建。
    """
    data_path = os.path.join(base_path, 'data')
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        logging.info(f"Creating data directory: {data_path}")
    else:
        logging.info(f"Data directory already exists: {data_path}")


ensure_data_directory()


def file_path_processor(file_path):
    """
    处理文件路径，适配打包后的应用。

    当程序打包为 exe 后，文件路径可能需要从打包路径中获取。
    此函数检查程序是否在打包环境下运行，并据此调整文件路径。

    Args:
        file_path (str): 原始文件路径。

    Returns:
        str: 处理后的文件路径。
    """
    # 检查是否存在 _MEIPASS 属性，该属性在使用 PyInstaller 打包时会被设置
    if hasattr(sys, '_MEIPASS'):
        # 如果存在 _MEIPASS 属性，说明程序是被打包运行的
        file_path = os.path.join(sys._MEIPASS, file_path)  # 将文件路径拼接为打包环境下的路径
    else:
        file_path = file_path  # 否则，保持原始路径不变
    return file_path


# 使用 file_path_processor 函数处理各个文件路径，以适配打包环境
json_file = file_path_processor(json_file)
thoughts_file = file_path_processor(thoughts_file)
ico_logo_file = file_path_processor(ico_logo_file)

logging.info(f"JSON 文件路径: {json_file}")  # 记录处理后的 JSON 文件路径
logging.info(f"想法文件路径: {thoughts_file}")  # 记录处理后的想法文件路径
logging.info(f"图标文件路径: {ico_logo_file}")  # 记录处理后的图标文件路径
logging.info(f"点击次数限制数据文件路径: {click_limit_file}")  # 记录的点击次数限制数据文件路径
logging.info(f"日志文件路径: {log_file_path}")  # 记录的日志文件路径


# ----- 加载答案数据 -----
# 检查 JSON 答案文件是否存在
if os.path.exists(json_file):
    # 如果 JSON 文件存在，则尝试加载答案数据
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            answers = json.load(f)  # 从 JSON 文件中加载答案数据
        logging.info("答案文件加载完成")  # 记录答案文件加载成功事件
    except json.JSONDecodeError as e:
        # JSON 文件格式错误处理
        logging.error(f"JSON 文件格式错误: {e}")
        messagebox.showerror("错误", f"答案文件 JSON 格式错误: {json_file}\n请检查文件内容是否为有效的 JSON 格式。")
        answers = []  # 初始化答案列表以避免后续错误
    except Exception as e:
        # 其他文件读取错误处理
        logging.error(f"加载答案文件时发生错误: {e}")
        messagebox.showerror("错误", f"加载答案文件时发生未知错误: {json_file}\n错误信息: {e}")
        answers = []  # 初始化答案列表以避免后续错误
else:
    # 如果 JSON 文件不存在，则记录错误并显示错误消息框
    logging.error(f"{json_file}文件未找到")
    messagebox.showerror("错误", f"答案文件未找到: {json_file}\n请确保 '{json_file}' 文件与程序在同一目录下")
    answers = []  # 初始化答案列表以避免后续错误，但应用可能无法正常功能


def save_click_count_data(count, date_str):
    """
    保存点击次数和日期到 CSV 文件中。
    CSV 文件包含列头 'Count' 和 'Date'，并写入一行数据。

    Args:
        count (int): 当前的点击次数。
        date_str (str): 当前日期字符串 (YYYY-MM-DD 格式)。
    """
    logging.info(f"Attempting to save click count data to: {click_limit_file}, Count: {count}, Date: {date_str}")  # <-- ADDED LOGGING
    try:
        with open(click_limit_file, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Count', 'Date'])  # 写入 CSV 文件头
            csv_writer.writerow([count, date_str])  # 写入点击次数和日期数据
        logging.info(f"Successfully saved click count data to CSV file, Count: {count}, 日期: {date_str}")
    except Exception as e:
        print(f"Error saving click count data: {e}")  # <--- ADDED PRINT STATEMENT for immediate console output
        logging.error(f"Error saving click count data to CSV file: {e}")


def load_click_count_data():
    """
    从 CSV 文件中加载点击次数限制数据 (点击次数和最后点击日期)。
    CSV 文件应包含列头 'Count' 和 'Date'，并期望只有一行数据。
    如果文件不存在或内容不符合预期，则返回默认值：count=0, last_date=None。

    Returns:
        tuple: 包含点击次数 (int) 和最后点击日期 (str, YYYY-MM-DD 格式) 的元组。
               如果文件不存在或读取失败，则返回 (0, None)。
    """
    try:
        if os.path.exists(click_limit_file):
            with open(click_limit_file, 'r', newline='', encoding='utf-8') as csvfile:
                csv_reader = csv.reader(csvfile)
                header = next(csv_reader, None)  # 读取并忽略 CSV 文件头
                if header is None:  # 文件为空
                    logging.warning("点击次数 CSV 文件为空，使用默认值。")
                    return 0, None
                row = next(csv_reader, None)  # 尝试读取数据行
                if row:
                    try:
                        count = int(row[0]) if row[0] else 0  # 读取并转换点击次数
                        last_date = row[1] if len(row) > 1 else None  # 读取日期
                        logging.info(f"成功从 CSV 文件加载点击次数数据，次数: {count}, 日期: {last_date}")
                        return count, last_date
                    except ValueError:
                        logging.error("CSV 文件中点击次数数据格式错误，使用默认值。")
                        return 0, None  # 数据格式错误，返回默认值
                else:
                    logging.warning("点击次数 CSV 文件数据行缺失，使用默认值。")
                    return 0, None  # 没有数据行, 返回默认值
        else:
            logging.info("点击次数 CSV 数据文件不存在，使用默认值。")
            return 0, None  # 文件不存在，返回默认值
    except FileNotFoundError:
        logging.info("点击次数 CSV 数据文件未找到，使用默认值。")  # 更加明确的日志
        return 0, None  # 文件未找到，返回默认值
    except Exception as e:
        logging.error(f"加载点击次数 CSV 数据失败: {e}")
        return 0, None  # 加载 CSV 数据失败，返回默认值

# 点击次数限制
DAILY_CLICK_LIMIT = 3  # 每天允许点击的最大次数

# 开始显示答案的函数 (限制点击次数)
def start_show_answer():
    """
    响应“获取答案”按钮点击事件，开始获取并逐渐显示答案，并实现每日点击次数限制。
    """
    logging.info("用户点击了 '获取答案' 按钮 - 尝试获取答案 (带点击次数限制)")  # 记录用户点击行为

    current_date = datetime.datetime.now().strftime('%Y-%m-%d')  # 获取当前日期
    click_count, last_click_date = load_click_count_data()  # 加载点击次数数据

    if last_click_date != current_date:  # 如果上次点击日期不是今天，说明是新的一天，重置点击次数
        click_count = 0  # 重置点击次数为 0
        logging.info("新的一天，重置点击次数为 0。")  # 记录重置事件

    if click_count < DAILY_CLICK_LIMIT:  # 检查点击次数是否小于限制
        logging.info("start_show_answer function CALLED") # <--- ADDED LOGGING
        logging.info(f"Current click count before increment: {click_count}") # <--- ADDED LOGGING
        click_count += 1  # 点击次数加 1
        save_click_count_data(click_count, current_date)  # 保存更新后的点击次数和日期
        logging.info(f"本轮点击次数: {click_count}/{DAILY_CLICK_LIMIT}")  # 记录本轮点击次数

        answer_label.config(text="")  # 清空答案 Label 的文本
        start_button.config(state=tk.DISABLED)  # 禁用开始按钮
        full_answer_text = show_answer()  # 获取答案文本
        if full_answer_text:
            gradually_show_answer(full_answer_text)  # 逐渐显示答案
        else:
            start_button.config(state=tk.NORMAL)  # 重新启用开始按钮
            answer_label.config(text="未能获取答案，请重试。")
            logging.error("未能从答案列表中获取有效答案。")
    else:
        logging.warning("已达到每日点击次数限制。")  # 记录达到限制警告
        messagebox.showinfo("提示", f"今日获取答案次数已达上限 ({DAILY_CLICK_LIMIT}次)，请明日再来。")  # 弹出提示消息框


# 显示随机答案的函数
def show_answer():
    """
    从答案列表中随机选择一个答案并格式化文本。

    Returns:
        str: 格式化后的答案文本，包含英文和中文，如果获取失败则返回 None。
    """
    logging.info("显示答案 - 准备答案文本")  # 记录准备答案文本事件
    r_num = random.randint(1, len(answers))  # 生成一个 1 到答案列表长度之间的随机数，作为页码
    answer_text = next((item for item in answers if item["page_number"] == r_num), None)  # 从答案列表中查找页码与随机数匹配的答案项
    if answer_text:
        # 如果找到了对应的答案项
        cn_text = answer_text["CN"]  # 获取中文答案
        en_text = answer_text["EN"]  # 获取英文答案
        full_answer_text = f'{en_text}\n{cn_text}'  # 将英文和中文答案合并，用换行符分隔
        logging.info(f"本轮 r_num: {r_num}, 准备显示的答案: EN='{en_text}', CN='{cn_text}'")  # 记录本轮随机数和准备显示的答案
        return full_answer_text  # 返回完整的答案文本
    return None  # 如果未找到答案，则返回 None


# 逐渐显示文本的通用函数
def gradually_show_text(label, full_text, index=0, duration_ms=100):
    """
    逐渐在指定的 Label 组件上显示文本，实现文字逐字出现的效果。

    Args:
        label (tk.Label 或 ttk.Label): 要显示文本的 Label 组件。
        full_text (str): 要完整显示的文本内容。
        index (int): 当前已显示的文本索引，默认为 0。
        duration_ms (int): 每次更新文本显示的时间间隔（毫秒），默认为 100 毫秒。
    """
    if not full_text:
        logging.warning("没有文本可以显示。")  # 记录警告：没有文本可以显示
        return

    if index <= len(full_text):
        # 如果当前索引小于等于文本长度，继续更新 Label 文本
        current_text = full_text[:index]  # 截取从开始到当前索引的文本
        label.config(text=current_text)  # 更新 Label 组件的文本
        label.after(duration_ms, gradually_show_text, label, full_text, index + 1, duration_ms)  # duration_ms 毫秒后，递归调用自身，索引加 1
    else:
        # 文本显示完成后执行的操作
        if label == answer_label:
            # 如果是答案 Label 显示完成，则启用开始按钮
            start_button.config(state=tk.NORMAL)  # 启用开始按钮
            logging.info("答案显示完成")  # 记录答案显示完成事件
        elif label == instructions_label:
            # 如果是用户提示 Label 显示完成
            logging.info("用户提示显示完成")  # 记录用户提示显示完成事件


# 逐渐显示答案的函数 (使用通用函数 gradually_show_text)
def gradually_show_answer(full_answer_text, index=0):
    """
    调用通用函数 gradually_show_text 逐渐显示答案文本。

    Args:
        full_answer_text (str): 要完整显示的答案文本。
        index (int): 当前已显示的文本索引，默认为 0。
    """
    gradually_show_text(answer_label, full_answer_text, index)  # 调用通用函数，目标 Label 为答案 Label，使用默认 duration_ms


# 逐渐显示用户提示的函数
def gradually_show_instructions(full_instructions_text, index=0):
    """
    调用通用函数 gradually_show_text 逐渐显示用户提示文本，并设置特定的显示速度。

    Args:
        full_instructions_text (str): 要完整显示的用户提示文本。
        index (int): 当前已显示的文本索引，默认为 0。
    """
    gradually_show_text(instructions_label, full_instructions_text, index, duration_ms=60)  # 调用通用函数，目标 Label 为提示 Label，设置 duration_ms 为 60 毫秒


# 查看日志文件的函数
def view_log_file():
    """
    打开日志文件 'log.log' 以供查看。

    根据操作系统类型选择不同的打开方式：
    Windows 使用 os.startfile，macOS 和 Linux 使用 subprocess.Popen 和 'open' 或 'xdg-open' 命令。
    如果日志文件不存在，则显示提示信息。
    """
    if os.path.exists(log_file_path):
        # 如果日志文件存在
        logging.info(f"打开日志文件: {log_file_path}")  # 记录打开日志文件事件
        try:
            if os.name == 'nt':  # Windows 系统
                os.startfile(log_file_path)  # 使用 Windows 默认方式打开文件
            else:  # macOS, Linux 系统
                subprocess.Popen(['open', log_file_path])  # 使用 'open' 命令 (macOS) 或 'xdg-open' (Linux) 打开文件
        except Exception as e:
            # 打开日志文件失败处理
            logging.error(f"打开日志文件失败: {e}")
            tk.messagebox.showerror("错误", "无法打开日志文件。")  # 显示错误消息框
    else:
        # 如果日志文件不存在
        logging.warning("日志文件不存在，但尝试打开日志查看。")  # 记录警告：日志文件不存在
        tk.messagebox.showinfo("提示", "日志文件不存在。")  # 显示提示消息框


# 读取想法文件的函数
def read_thoughts_file(path=None):
    """
    读取想法文件 'thoughts.txt' 的内容。

    根据程序是否打包，确定想法文件的路径。
    如果打包，从打包路径中读取；否则，从相对路径读取。
    处理文件未找到和读取错误等异常情况。

    Args:
        path (str, optional): 想法文件的路径，默认为 None。

    Returns:
        str: 想法文件的内容，如果读取失败则返回 None。
    """
    if hasattr(sys, '_MEIPASS'):
        # 如果程序已打包，从 _MEIPASS 中获取想法文件路径
        thoughts_file_path = os.path.join(sys._MEIPASS, thoughts_file)
        logging.info(f"Running as bundled executable, using _MEIPASS for thoughts file path: {thoughts_file_path}")  # 记录使用 _MEIPASS 路径
    else:
        # 否则，使用相对路径
        thoughts_file_path = thoughts_file
        logging.info(f"Running as script, using relative path for thoughts file path: {thoughts_file_path}")  # 记录使用相对路径

    try:
        with open(thoughts_file_path, 'r', encoding='utf-8') as file:
            thoughts_content = file.read()  # 读取想法文件内容
        return thoughts_content  # 返回读取到的内容
    except FileNotFoundError:
        # 文件未找到错误处理
        logging.error(f"{thoughts_file_path} 文件未找到")
        messagebox.showerror("错误", f"想法文件未找到: {thoughts_file_path}")  # 显示文件未找到错误消息框
        return None
    except Exception as e:  # 添加其他异常处理，例如编码错误等
        # 其他读取文件错误处理
        logging.error(f"读取想法文件出错: {e}")
        messagebox.showerror("错误", f"读取想法文件出错: {e}")  # 显示读取文件错误消息框
        return None


# 显示想法的函数
def show_thoughts():
    """
    创建一个新的顶级窗口显示想法文件的内容。

    读取想法文件的内容，并在新的顶级窗口的文本框中显示。
    窗口标题为 "Thoughts"，背景色与主窗口一致，文本框内容只读。
    窗口居中显示在屏幕上。
    """
    thoughts_content = read_thoughts_file()  # 读取想法文件内容
    if thoughts_content:
        # 如果成功读取到想法内容
        thoughts_window = tk.Toplevel(root)  # 创建一个新的顶级窗口，父窗口为主窗口 root
        thoughts_window.title("Thoughts")  # 设置新窗口标题为 "Thoughts"

        thoughts_text = tk.Text(thoughts_window, wrap=tk.WORD)  # 创建文本框组件，设置背景色和前景色
        thoughts_text.insert(tk.END, thoughts_content)  # 将想法内容插入到文本框中
        thoughts_text.config(state=tk.DISABLED)  # 设置文本框为只读状态
        thoughts_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # 文本框填充窗口，并设置内外边距

        # ----- 窗口居中显示代码 -----
        thoughts_window.update_idletasks()  # 更新窗口状态，确保可以获取正确的窗口尺寸
        screen_width = thoughts_window.winfo_screenwidth()  # 获取屏幕宽度
        screen_height = thoughts_window.winfo_screenheight()  # 获取屏幕高度
        window_width = thoughts_window.winfo_reqwidth()  # 获取窗口请求宽度
        window_height = thoughts_window.winfo_reqheight()  # 获取窗口请求高度
        x_coordinate = int((screen_width - window_width) / 2)  # 计算窗口居中显示的 x 坐标
        y_coordinate = int((screen_height - window_height) / 2)  # 计算窗口居中显示的 y 坐标
        thoughts_window.geometry(f"+{x_coordinate}+{y_coordinate}")  # 设置窗口位置，使其居中显示


# ----- 创建主窗口 -----
root = tk.Tk()
root.title("The Book of Answers")  # 设置窗口标题
root.iconbitmap(ico_logo_file)  # 设置窗口图标
root.resizable(False, False)  # 禁止窗口大小调整

# ----- 菜单栏 -----
menubar = tk.Menu(root)  # 创建菜单栏，设置背景色和前景色
helpmenu = tk.Menu(menubar, tearoff=0)  # 创建 "Help" 菜单，不显示虚线，设置背景色和前景色
helpmenu.add_command(label="Log", command=view_log_file)  # 添加 "Log" 子菜单项，关联查看日志文件函数
menubar.add_cascade(label="Help", menu=helpmenu)  # 将 "Help" 菜单添加到菜单栏

# ----- "关于" 菜单 -----
aboutmenu = tk.Menu(menubar, tearoff=0)  # 创建 "关于" 菜单
aboutmenu.add_command(label="Thoughts", command=show_thoughts)  # 添加 "Thoughts" 子菜单项，关联显示想法函数
menubar.add_cascade(label="About", menu=aboutmenu)  # 将 "关于" 菜单添加到菜单栏

root.config(menu=menubar)  # 将菜单栏配置到主窗口，并确保菜单栏背景与主窗口一致


# ----- 样式配置 -----
style = ttk.Style(root)  # 创建样式对象
style.configure("TLabel", font=('Microsoft YaHei UI', 10))  # 配置 Label 样式：背景色、前景色、字体
style.configure("TButton", font=('Microsoft YaHei UI', 10, 'bold'), padding=8, relief="raised",
                borderwidth=2,  # 设置边框宽度
                )

# ----- 标题标签 -----
title_label = ttk.Label(root, text="答案之书", font=('Microsoft YaHei UI', 18, 'bold'))  # 创建标题 Label，设置文本、字体和前景色
title_label.pack(pady=(15, 5), padx=20)  # 使用 pack 布局管理器，设置垂直和水平方向的外边距

# ----- 说明标签 (初始文本为空) -----
instructions_label = ttk.Label(
    root,
    text="",  # 初始文本设置为空
    font=('Microsoft YaHei UI', 10),  # 恢复原始字体大小
    wraplength=400,  # 设置文本自动换行长度
    justify="center",  # 文本居中对齐
)
instructions_label.pack(pady=(0, 10), padx=20)  # 设置垂直和水平方向的外边距

# ----- "获取答案" 按钮 -----
start_button = ttk.Button(root, text="获取答案", command=start_show_answer, style="TButton")  # 创建按钮，设置文本、点击命令和样式
start_button.pack(pady=(10, 15), padx=20)  # 设置垂直和水平方向的外边距

# ----- 答案显示标签 -----
answer_label = ttk.Label(
    root,
    text="",  # 初始文本为空
    font=('Microsoft YaHei UI', 14, 'bold'),  # 设置字体
    justify="center",  # 文本居中对齐
    wraplength=400,  # 设置文本自动换行长度
)
answer_label.pack(pady=(10, 20), padx=20)  # 设置垂直和水平方向的外边距

# ----- 初始完整提示文本 -----
full_instructions = "聚焦在你心心念念、亟待求解的事儿上，想一个封闭式问题，点击按钮获取答案。比如，“我这个周末应该去旅行吗？”"

# ----- 延时启动时逐渐显示用户提示 -----
root.after(500, gradually_show_instructions, full_instructions)  # 延时 500 毫秒后启动逐渐显示用户提示

# ----- 窗口居中显示代码 -----
root.update_idletasks()  # 更新窗口状态，获取正确的窗口尺寸
screen_width = root.winfo_screenwidth()  # 获取屏幕宽度
screen_height = root.winfo_screenheight()  # 获取屏幕高度
window_width = root.winfo_reqwidth()  # 获取窗口请求宽度
window_height = root.winfo_reqheight()  # 获取窗口请求高度
x_coordinate = int((screen_width - window_width) / 2)  # 计算窗口居中 x 坐标
y_coordinate = int((screen_height - window_height) / 2)  # 计算窗口居中 y 坐标
root.geometry(f"+{x_coordinate}+{y_coordinate}")  # 设置窗口位置，使其居中显示

# ----- 运行应用主循环 -----
root.mainloop()  # 启动 tkinter 应用的主循环，监听事件
logging.info("应用退出")  # 记录应用退出事件
# ----- 日志分隔符 -----
logging.info("-----")  # 添加分隔符，分隔每次的应用运行日志