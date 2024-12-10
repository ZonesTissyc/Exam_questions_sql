import re

def process_question(question_text):
    # 解析题目文本，提取题目和选项
    question_match = re.search(r'^(.*?)\n\n', question_text, re.DOTALL)  # 匹配第一个空行之前的内容作为题目
    options_match = re.findall(r'([A-Z]\.\s.*?)(?=\n[A-Z]\.|$)', question_text, re.DOTALL)  # 匹配选项部分
    
    if not question_match or not options_match:  # 如果没有题目或选项，抛出异常
        raise ValueError("Invalid question format: Question must include text and options (A, B, C, D).")
    
    question = question_match.group(1).strip()  # 提取题目内容，去掉首尾空格
    options = {}
    
    # 提取选项内容并存入字典
    for i, option in enumerate(options_match):
        option_key = chr(65 + i)  # 转换为 A, B, C, D
        option_value = re.sub(r'^[A-Z]\.\s', '', option).strip()  # 去掉 "A. " 等前缀
        options[option_key] = option_value
    
    # 确定题目类型为选择题
    question_type = "0"
    
    return question_type, question, options
