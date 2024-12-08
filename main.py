# 该程序用于导入题目，然后识别ABCD选项，最终转换成数据库的形式

import tkinter as tk
from tkinter import ttk
import re
import pyperclip

def parse_question(question_text):
    # 解析题目文本，提取题目和选项
    question_match = re.search(r'^(.*?)\n\n', question_text, re.DOTALL)
    options_match = re.findall(r'([A-Z]\.\s.*?)(?=\n[A-Z]\.|$)', question_text, re.DOTALL)
    
    if not question_match or not options_match:
        raise ValueError("Invalid question format")
    
    question = question_match.group(1).strip()
    options = [option.strip() for option in options_match]
    
    return question, options

def add_question():
    # 获取输入框和选择框的值
    question_type = question_type_var.get()
    question_text = question_entry.get("1.0", "end-1c")
    
    # 解析题目文本
    try:
        question, options = parse_question(question_text)
    except ValueError as e:
        result_label.config(text=f"Error: {e}")
        return
    
    # 让用户选择答案
    answer = answer_var.get()
    
    # 根据题目类型生成 SQL 指令
    if question_type == "选择题":
        sql_instruction = f"INSERT INTO questions (question, type, answer, explain, A, B, C, D) VALUES ('{question}', 0, '{answer}', '', '{options[0]}', '{options[1]}', '{options[2]}', '{options[3]}');"
    elif question_type == "判断题":
        sql_instruction = f"INSERT INTO questions (question, type, answer, explain) VALUES ('{question}', 1, '{answer}', '');"
    elif question_type == "主观题":
        sql_instruction = f"INSERT INTO questions (question, type, answer, explain) VALUES ('{question}', 2, '', '');"
    else:
        result_label.config(text="Invalid question type")
        return
    
    # 显示结果
    result_label.config(text=sql_instruction)
    
    # 复制到剪贴板
    pyperclip.copy(sql_instruction)

def clear_entries():
    # 清除输入框和选择框的内容
    question_entry.delete("1.0", "end")
    answer_var.set("")
    question_type_var.set("")

def update_answer_options(*args):
    # 根据题目类型更新答案选择框的选项
    question_type = question_type_var.get()
    if question_type == "选择题":
        answer_combobox.config(values=["A", "B", "C", "D"])
    elif question_type == "判断题":
        answer_combobox.config(values=["对", "错"])
    else:
        answer_combobox.config(values=[])

# 切换是否复制到剪贴板的状态



# 创建主窗口
root = tk.Tk()
root.title("Question Importer")

# 创建输入框和选择框
question_label = ttk.Label(root, text="题目:")
question_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
question_entry = tk.Text(root, height=5, width=50)
question_entry.grid(row=0, column=1, padx=10, pady=10)

answer_label = ttk.Label(root, text="答案:")
answer_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
answer_var = tk.StringVar()
answer_combobox = ttk.Combobox(root, textvariable=answer_var, values=[])
answer_combobox.grid(row=2, column=1, padx=10, pady=10)

question_type_label = ttk.Label(root, text="题目类型:")
question_type_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
question_type_var = tk.StringVar()
question_type_combobox = ttk.Combobox(root, textvariable=question_type_var, values=["选择题", "判断题", "主观题"])
question_type_combobox.grid(row=1, column=1, padx=10, pady=10)


# 创建按钮
add_button = ttk.Button(root, text="添加", command=add_question)
add_button.grid(row=3, column=0, padx=10, pady=10)

clear_button = ttk.Button(root, text="清除", command=clear_entries)
clear_button.grid(row=3, column=1, padx=10, pady=10)

# 创建结果标签
result_label = ttk.Label(root, text="")
result_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# 绑定题目类型选择框的变化事件
question_type_var.trace_add("write", update_answer_options)


# 运行主循环
root.mainloop()
