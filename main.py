import tkinter as tk
from tkinter import filedialog
import re
import pyperclip  # 用于剪贴板操作


def process_question(question_text):
    """解析选择题的题目文本"""
    try:
        question_match = re.search(r"^(.*?)\n\n", question_text, re.DOTALL)  # 匹配题目文本部分
        options_match = re.findall(r"([A-Z]\.\s.*?)(?=\n[A-Z]\.|$)", question_text, re.DOTALL)  # 匹配选项

        if not question_match or not options_match:
            raise ValueError("无效的题目格式，必须包含题目和选项（A, B, C, D）。")

        question = question_match.group(1).strip()
        options = {}

        for i, option in enumerate(options_match):
            option_key = chr(65 + i)  # 转换为 A, B, C, D
            option_value = re.sub(r"^[A-Z]\.\s", "", option).strip()
            options[option_key] = option_value

        return "1", question, options
    except Exception as e:
        raise ValueError(f"解析失败: {e}")


class QuestionToSQLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("题目转SQL工具")

        # 题目类型选择框
        tk.Label(root, text="题目类型:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.type_var = tk.StringVar(value="选择题")  # 默认选择题
        self.type_mapping = {"选择题": "1", "判断题": "2", "主观题": "5"}  # 显示值和SQL值的映射
        self.type_menu = tk.OptionMenu(root, self.type_var, *self.type_mapping.keys(), command=self.update_answer_frame)
        self.type_menu.grid(row=0, column=1, padx=5, pady=5)

        # 题目文本输入框
        tk.Label(root, text="题目文本:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.question_text = tk.Text(root, height=10, width=60)
        self.question_text.grid(row=1, column=1, padx=5, pady=5)

        # 答案选择框
        tk.Label(root, text="答案:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.answer_frame = tk.Frame(root)
        self.answer_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.answer_vars = {key: tk.BooleanVar() for key in "ABCD"}
        self.judgment_var = tk.StringVar(value="")  # 用于“对/错”单选
        self.create_answer_frame("选择题")  # 默认创建选择题的答案框

        # 题目解析输入框
        tk.Label(root, text="题目解析:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.analysis_text = tk.Text(root, height=5, width=60)
        self.analysis_text.grid(row=3, column=1, padx=5, pady=5)

        # 按钮
        tk.Button(root, text="解析", command=self.parse_question).grid(row=4, column=0, padx=5, pady=5)
        tk.Button(root, text="插入", command=self.insert_sql).grid(row=4, column=1, padx=5, pady=5, sticky="w")
        tk.Button(root, text="清除", command=self.clear_inputs).grid(row=4, column=1, padx=5, pady=5, sticky="e")
        tk.Button(root, text="完成", command=self.save_sql).grid(row=4, column=2, padx=5, pady=5)
        tk.Button(root, text="复制", command=self.copy_to_clipboard).grid(row=4, column=3, padx=5, pady=5)

        # 解析结果显示框
        tk.Label(root, text="解析结果:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.result_text = tk.Text(root, height=10, width=60, state="disabled")
        self.result_text.grid(row=5, column=1, padx=5, pady=5)

        # 状态栏
        self.status_label = tk.Label(root, text="状态: 就绪", anchor="w", relief="sunken")
        self.status_label.grid(row=6, column=0, columnspan=2, sticky="we")

        self.sql_statements = []

    def set_status(self, message):
        """设置状态栏信息"""
        self.status_label.config(text=f"状态: {message}")

    def create_answer_frame(self, q_type_text):
        """根据题目类型更新答案选择框"""
        for widget in self.answer_frame.winfo_children():
            widget.destroy()

        if q_type_text == "选择题":
            self.answer_vars = {key: tk.BooleanVar() for key in "ABCD"}
            for key, var in self.answer_vars.items():
                tk.Checkbutton(self.answer_frame, text=key, variable=var).pack(side="left")
        elif q_type_text == "判断题":
            self.judgment_var.set("")  # 重置单选框
            tk.Radiobutton(self.answer_frame, text="对", variable=self.judgment_var, value="对").pack(side="left")
            tk.Radiobutton(self.answer_frame, text="错", variable=self.judgment_var, value="错").pack(side="left")

    def update_answer_frame(self, selected_type):
        """更新答案选择框"""
        self.create_answer_frame(selected_type)

    def parse_question(self):
        question_text = self.question_text.get("1.0", "end").strip()
        try:
            q_type_text = self.type_var.get()
            q_type = self.type_mapping[q_type_text]  # 根据文字获取对应SQL值

            if q_type == "1":  # 选择题
                q_type, question, options = process_question(question_text)
                answers = "".join([key for key, var in self.answer_vars.items() if var.get()])  # 拼接答案字符串
            elif q_type == "2":  # 判断题
                question = question_text
                options = None
                answers = self.judgment_var.get()  # 获取“对/错”单选答案
                if not answers:
                    raise ValueError("请选择“对”或“错”作为答案。")
            else:  # 主观题
                question = question_text
                options = None
                answers = ""  # 主观题没有明确答案

            analysis = self.analysis_text.get("1.0", "end").strip()

            result = f"题目类型: {q_type_text}\n题目: {question}\n"
            if options:
                result += f"选项: {options}\n"
            result += f"答案: {answers}\n解析: {analysis}"
            self.show_result(result)

            self.sql_data = (q_type, question, options, answers, analysis)
            self.set_status("题目解析成功！")
        except Exception as e:
            self.set_status(f"解析失败: {e}")

    def show_result(self, result):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", result)
        self.result_text.config(state="disabled")

    def insert_sql(self):
        if not hasattr(self, "sql_data"):
            self.set_status("请先解析题目！")
            return

        q_type, question, options, answers, analysis = self.sql_data

        # 判断题和主观题的选项为空
        if options:
            a, b, c, d = options.get("A", "NULL"), options.get("B", "NULL"), options.get("C", "NULL"), options.get("D", "NULL")
        else:
            a, b, c, d = "NULL", "NULL", "NULL", "NULL"

        # 构造SQL插入语句
        sql = (
            f"INSERT INTO questions (type, question, A, B, C, D, answer, analysis) "
            f"VALUES ('{q_type}', '{question}', "
            f"'{a}', '{b}', '{c}', '{d}', '{answers}', '{analysis}');"
        )
        self.sql_statements.append(sql)
        self.set_status("SQL语句插入成功！")

    def clear_inputs(self):
        self.question_text.delete("1.0", "end")
        self.analysis_text.delete("1.0", "end")
        for var in self.answer_vars.values():
            var.set(False)
        self.judgment_var.set("")  # 重置“对/错”单选框
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.config(state="disabled")
        self.set_status("输入已清空！")

    def save_sql(self):
        if not self.sql_statements:
            self.set_status("没有可保存的SQL语句！")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL文件", "*.sql")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(self.sql_statements))
            self.set_status("SQL语句已保存！")

    def copy_to_clipboard(self):
        if not self.sql_statements:
            self.set_status("没有可复制的SQL语句！")
            return

        sql_text = "\n".join(self.sql_statements)
        pyperclip.copy(sql_text)
        self.set_status("SQL语句已复制到剪贴板！")


if __name__ == "__main__":
    root = tk.Tk()
    app = QuestionToSQLApp(root)
    root.mainloop()
