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


# 开始倒计时的函数
def start_countdown():
    logging.info("用户点击了 '获取答案' 按钮") # 记录用户点击行为
    answer_label.config(text="")
    countdown_label.config(text="10", foreground='#e74c3c') #  <--- 设置倒计时标签文本为 "15" (显示)
    start_button.config(state=tk.DISABLED)
    countdown_label.after(1000, countdown, 9)


# 倒计时函数
def countdown(seconds):
    if seconds > 0:
        countdown_label.config(text=str(seconds))
        countdown_label.after(1000, countdown, seconds - 1)
    else:
        countdown_label.config(text="0")
        show_answer()
        start_button.config(state=tk.NORMAL)


# 显示随机答案的函数
def show_answer():
    logging.info("显示答案")
    r_num = random.randint(1, len(answers))
    answer_text = next((item for item in answers if item["page_number"] == r_num), None)
    if answer_text:
        cn_text = answer_text["CN"]
        en_text = answer_text["EN"]
        answer_label.config(text=f'"{en_text}"\n\n—— {cn_text}', foreground='#2c3e50')
        countdown_label.config(text="") #  <---  答案显示后清空倒计时标签文本 (隐藏)
        logging.info(f"本轮 r_num: {r_num}, 显示的答案: EN='{en_text}', CN='{cn_text}'") # 记录 r_num 和答案
    logging.info("答案显示完成")

def view_log_file():
    log_file_path = 'app.log'
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
# root.geometry("450x350")  # 移除固定窗口尺寸设置
root.resizable(False, False) # 宽度和高度都不允许手动调整
root.configure(bg='#f9f9f9')

# 菜单栏
menubar = tk.Menu(root)
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="查看日志", command=view_log_file)
menubar.add_cascade(label="帮助", menu=helpmenu)
root.config(menu=menubar)

# 样式配置
style = ttk.Style(root)
style.configure("TLabel", background='#f9f9f9', font=('Microsoft YaHei UI', 10))
style.configure("TButton", font=('Microsoft YaHei UI', 10, 'bold'), padding=8, relief="raised")

# 标题标签
title_label = ttk.Label(root, text="答案之书", font=('Microsoft YaHei UI', 18, 'bold'))
title_label.pack(pady=(15, 5), padx=20)

# 说明标签
instructions_label = ttk.Label(
    root,
    text="心中想一个封闭式问题，点击按钮获取答案。\n比如，“我这个周末应该去旅行吗？”",
    wraplength=400,
    justify="center"
)
instructions_label.pack(pady=(0, 10), padx=20)

# 倒计时标签
countdown_label = ttk.Label(root, text="", font=("Helvetica", 24, "bold")) #  <--- 初始状态设置文本为空 (隐藏)
countdown_label.pack(pady=(5, 10), padx=20)

# 准备好了按钮
start_button = ttk.Button(root, text="获取答案", command=start_countdown, style="TButton")
start_button.pack(pady=(10, 15), padx=20)

# 答案显示标签
answer_label = ttk.Label(
    root,
    text="",
    font=('Microsoft YaHei UI', 14, 'bold'),
    justify="center",
    wraplength=400
)
answer_label.pack(pady=(10, 20), padx=20)

# 运行应用
root.mainloop()
logging.info("应用退出")