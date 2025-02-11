import tkinter as tk
from tkinter import ttk
import random
import json
import logging
import os
import subprocess

# 配置日志记录
logging.basicConfig(filename='log.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8')

logging.info("应用启动")

# 从JSON文件加载答案
with open('The_Book_of_Answers_Full.json', 'r', encoding='utf-8') as f:
    answers = json.load(f)
logging.info("答案文件加载完成")

# 显示随机答案的函数
def show_answer():
    logging.info("显示答案 - 准备答案文本")
    r_num = random.randint(1, len(answers))
    answer_text = next((item for item in answers if item["page_number"] == r_num), None)
    if answer_text:
        cn_text = answer_text["CN"]
        en_text = answer_text["EN"]
        full_answer_text = f'{en_text}\n{cn_text}'
        logging.info(f"本轮 r_num: {r_num}, 准备显示的答案: EN='{en_text}', CN='{cn_text}'") # 记录 r_num 和答案
        return full_answer_text
    return None

# 逐渐显示文本的通用函数
def gradually_show_text(label, full_text, index=0, duration_ms=100): #  <---  调整默认 duration_ms 为 80 毫秒 (答案)
    if not full_text:
        logging.warning("没有文本可以显示。")
        return

    if index <= len(full_text):
        current_text = full_text[:index]
        label.config(text=current_text) #  <---  使用传入的 label
        label.after(duration_ms, gradually_show_text, label, full_text, index + 1, duration_ms) #  <---  label 也传入
    else:
        if label == answer_label: #  <---  仅当答案显示完成时启用按钮
            start_button.config(state=tk.NORMAL)
            logging.info("答案显示完成")
        elif label == instructions_label:
            logging.info("用户提示显示完成")


# 逐渐显示答案的函数 (使用通用函数)
def gradually_show_answer(full_answer_text, index=0):
    gradually_show_text(answer_label, full_answer_text, index) #  <---  使用默认 duration_ms = 80

# 逐渐显示用户提示的函数
def gradually_show_instructions(full_instructions_text, index=0):
    gradually_show_text(instructions_label, full_instructions_text, index, duration_ms=60) #  <---  调整提示文本 duration_ms 为 60 毫秒


# 开始显示答案的函数 (不再倒计时)
def start_show_answer():
    logging.info("用户点击了 '获取答案' 按钮 - 开始逐渐显示答案") # 记录用户点击行为
    answer_label.config(text="")
    start_button.config(state=tk.DISABLED)
    full_answer_text = show_answer()
    if full_answer_text:
        gradually_show_answer(full_answer_text)
    else:
        start_button.config(state=tk.NORMAL)
        answer_label.config(text="未能获取答案，请重试。", foreground='#e74c3c') #  保持错误信息颜色不变
        logging.error("未能从答案列表中获取有效答案。")


def view_log_file():
    log_file_path = 'log.log'
    if os.path.exists(log_file_path):
        logging.info(f"打开日志文件: {log_file_path}")
        try:
            if os.name == 'nt': # Windows
                os.startfile(log_file_path)
            else: # macOS, Linux
                subprocess.Popen(['open', log_file_path]) # For macOS, consider 'xdg-open' for Linux
        except Exception as e:
            logging.error(f"打开日志文件失败: {e}")
            tk.messagebox.showerror("错误", "无法打开日志文件。")
    else:
        logging.warning("日志文件不存在，但尝试打开日志查看。")
        tk.messagebox.showinfo("提示", "日志文件不存在。")


# 创建主窗口
root = tk.Tk()
root.title("答案之书")
root.resizable(False, False)
root.configure(bg='#082032') #  深蓝色背景

# 菜单栏
menubar = tk.Menu(root, background='#2e0249', foreground='#f0f0f0') # 深紫色菜单栏背景，浅灰色文字
helpmenu = tk.Menu(menubar, tearoff=0, background='#2e0249', foreground='#f0f0f0') # 深紫色菜单背景，浅灰色文字
helpmenu.add_command(label="查看日志", command=view_log_file, foreground='#f0f0f0', background='#2e0249') # 浅灰色文字，深紫色背景
menubar.add_cascade(label="帮助", menu=helpmenu, foreground='#f0f0f0') # 浅灰色文字
root.config(menu=menubar, background='#082032') #  确保菜单栏背景与主窗口一致

# 样式配置
style = ttk.Style(root)
style.configure("TLabel", background='#082032', foreground='#f0f0f0', font=('Microsoft YaHei UI', 10)) #  浅灰色文本
style.configure("TButton", font=('Microsoft YaHei UI', 10, 'bold'), padding=8, relief="raised",
                background='#f0f0f0', foreground='#2e0249',  # 深紫色按钮背景，浅灰色文字
                borderwidth=2,  # 可选：稍微增加边框宽度
                )

# 标题标签
title_label = ttk.Label(root, text="答案之书", font=('Microsoft YaHei UI', 18, 'bold'), foreground='#f0f0f0') # 浅灰色标题
title_label.pack(pady=(15, 5), padx=20)

# 说明标签 (初始文本为空)
instructions_label = ttk.Label(
    root,
    text="", #  <---  初始文本设置为空
    font=('Microsoft YaHei UI', 10), #  <---  恢复原始字体大小
    wraplength=400,
    justify="center",
    foreground='#f0f0f0' # 浅灰色说明文字
)
instructions_label.pack(pady=(0, 10), padx=20)

# 准备好了按钮
start_button = ttk.Button(root, text="获取答案", command=start_show_answer, style="TButton")
start_button.pack(pady=(10, 15), padx=20)

# 答案显示标签
answer_label = ttk.Label(
    root,
    text="",
    font=('Microsoft YaHei UI', 14, 'bold'),
    justify="center",
    wraplength=400,
    foreground='#f0f0f0' # 浅灰色答案文字
)
answer_label.pack(pady=(10, 20), padx=20)

# 初始完整提示文本
full_instructions = "心中想一个封闭式问题，点击按钮获取答案。\n比如，“我这个周末应该去旅行吗？”"

# 延时启动时逐渐显示用户提示  <---  添加延时
root.after(500, gradually_show_instructions, full_instructions) #  <---  延时 500 毫秒后启动


#  -----  窗口居中显示代码  -----
root.update_idletasks() #  确保窗口布局完成
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = root.winfo_reqwidth()
window_height = root.winfo_reqheight()
x_coordinate = int((screen_width - window_width) / 2)
y_coordinate = int((screen_height - window_height) / 2)
root.geometry(f"+{x_coordinate}+{y_coordinate}") #  设置窗口位置


# 运行应用
root.mainloop()
logging.info("应用退出")