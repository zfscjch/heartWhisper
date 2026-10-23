<<<<<<< HEAD
import json
import random
import uuid
import os
from docx import Document


def load_data() -> dict[str, str | list]:
    """加载测试数据。

    从 ``paper_example.txt`` 中读取问卷的开头提示与结尾提示
    （以 ``---\\n`` 分隔），并从 ``titles.json`` 中读取题目列表。

    Returns:
        dict[str, str | list]: 包含以下键的字典：

        - ``"head"`` (str): 问卷开头的提示文本。
        - ``"end"`` (str): 问卷结尾的提示文本。
        - ``"problems"`` (list): 题目列表。

    Raises:
        FileNotFoundError: 当 ``paper_example.txt`` 或 ``titles.json`` 不存在时。
        ValueError: 当 ``paper_example.txt`` 中不包含 ``---\\n`` 分隔符时。
        json.JSONDecodeError: 当 ``titles.json`` 不是合法的 JSON 时。

    Examples:
        >>> res = load_data()
        >>> res["head"]
        '...'
    """
    with open("./paper_example.txt", "r", encoding="utf-8") as rf:
        paper_hint = rf.read()

    head_hint, finish_hint = paper_hint.split("---\n")

    with open("titles.json", "r", encoding="utf-8") as jf:
        questions = json.load(jf)

    res = {
        "head": head_hint,
        "end": finish_hint,
        "problems": questions
    }

    return res


def generate_word() -> str:
    """生成一份随机的心理调查问卷 Word 文档。

    从 :func:`load_data` 加载数据，随机抽取题目（每组最多 2 道，
    最多 5 组），将题目连同开头、结尾提示写入 docx 文档，
    并保存到 ``doc/`` 目录下（目录不存在时自动创建）。
    文件名为随机生成的 8 位十六进制字符串加 ``.docx`` 后缀。

    Returns:
        str: 生成的文件名（不含目录路径），例如 ``"a1b2c3d4.docx"``。

    Raises:
        FileNotFoundError: 当所需数据文件不存在时（由 :func:`load_data` 抛出）。
        ValueError: 当数据文件格式不正确时（由 :func:`load_data` 抛出）。

    Examples:
        >>> file_name = generate_word()
        >>> file_name.endswith(".docx")
        True
    """
    doc = Document()
    doc.add_heading("心理调查问卷", level=1)

    data = load_data()
    doc.add_paragraph(data["head"])

    problems = data["problems"]
    os.makedirs("doc", exist_ok=True)

    question_num = 1

    for i in range(5):
        num_to_pick = min(2, len(problems[i]))
        selected_problems = random.sample(problems[i], num_to_pick)

        for problem in selected_problems:
            text = f"{question_num}. "
            if problem["is_reverse_scored"]:
                text += "【本题需要反向评分】"
            text += problem["question_text"]
            doc.add_paragraph(text)
            question_num += 1

    doc.add_paragraph(data["end"])

    file_name = str(uuid.uuid4())[:8] + ".docx"
    file_path = os.path.join("doc", file_name)
    doc.save(file_path)

=======
import json
import random
import uuid
import os
from docx import Document


def load_data() -> dict[str, str | list]:
    """加载测试数据。

    从 ``paper_example.txt`` 中读取问卷的开头提示与结尾提示
    （以 ``---\\n`` 分隔），并从 ``titles.json`` 中读取题目列表。

    Returns:
        dict[str, str | list]: 包含以下键的字典：

        - ``"head"`` (str): 问卷开头的提示文本。
        - ``"end"`` (str): 问卷结尾的提示文本。
        - ``"problems"`` (list): 题目列表。

    Raises:
        FileNotFoundError: 当 ``paper_example.txt`` 或 ``titles.json`` 不存在时。
        ValueError: 当 ``paper_example.txt`` 中不包含 ``---\\n`` 分隔符时。
        json.JSONDecodeError: 当 ``titles.json`` 不是合法的 JSON 时。

    Examples:
        >>> res = load_data()
        >>> res["head"]
        '...'
    """
    with open("./paper_example.txt", "r", encoding="utf-8") as rf:
        paper_hint = rf.read()

    head_hint, finish_hint = paper_hint.split("---\n")

    with open("titles.json", "r", encoding="utf-8") as jf:
        questions = json.load(jf)

    res = {
        "head": head_hint,
        "end": finish_hint,
        "problems": questions
    }

    return res


def generate_word() -> str:
    """生成一份随机的心理调查问卷 Word 文档。

    从 :func:`load_data` 加载数据，随机抽取题目（每组最多 2 道，
    最多 5 组），将题目连同开头、结尾提示写入 docx 文档，
    并保存到 ``doc/`` 目录下（目录不存在时自动创建）。
    文件名为随机生成的 8 位十六进制字符串加 ``.docx`` 后缀。

    Returns:
        str: 生成的文件名（不含目录路径），例如 ``"a1b2c3d4.docx"``。

    Raises:
        FileNotFoundError: 当所需数据文件不存在时（由 :func:`load_data` 抛出）。
        ValueError: 当数据文件格式不正确时（由 :func:`load_data` 抛出）。

    Examples:
        >>> file_name = generate_word()
        >>> file_name.endswith(".docx")
        True
    """
    doc = Document()
    doc.add_heading("心理调查问卷", level=1)

    data = load_data()
    doc.add_paragraph(data["head"])

    problems = data["problems"]
    os.makedirs("doc", exist_ok=True)

    question_num = 1

    for i in range(5):
        num_to_pick = min(2, len(problems[i]))
        selected_problems = random.sample(problems[i], num_to_pick)

        for problem in selected_problems:
            text = f"{question_num}. "
            if problem["is_reverse_scored"]:
                text += "【本题需要反向评分】"
            text += problem["question_text"]
            doc.add_paragraph(text)
            question_num += 1

    doc.add_paragraph(data["end"])

    file_name = str(uuid.uuid4())[:8] + ".docx"
    file_path = os.path.join("doc", file_name)
    doc.save(file_path)

>>>>>>> 550ddc05bb1e893b4a2965411c77932763787ec1
    return file_name