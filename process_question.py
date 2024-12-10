import re

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
