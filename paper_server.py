import os
import time
import json
from flask import Flask, send_from_directory, jsonify, url_for, request
from gen_word import generate_word

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.join(BASE_DIR, "doc")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DOC_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

MAX_FILES = 100
MAX_FILE_AGE = 3600

def cleanup_old_files():
    """清理旧的生成文件，防止磁盘溢出导致服务崩溃"""
    try:
        files = [os.path.join(DOC_DIR, f) for f in os.listdir(DOC_DIR) if f.endswith(".docx")]
        if len(files) > MAX_FILES:
            files.sort(key=os.path.getmtime)
            num_to_delete = len(files) - MAX_FILES + 10
            for f in files[:num_to_delete]:
                try: os.remove(f)
                except OSError: pass
        else:
            now = time.time()
            for f in files:
                if now - os.path.getmtime(f) > MAX_FILE_AGE:
                    try: os.remove(f)
                    except OSError: pass
    except Exception as e:
        app.logger.warning(f"清理旧文件失败: {e}")

@app.route('/doc/<filename>')
def download_file(filename):
    return send_from_directory(DOC_DIR, filename, as_attachment=True)

@app.route('/check', methods=['GET'])
def check_cache():
    """检查该类型试卷题库是否已缓存"""
    q_type = request.args.get("type", "抗抑郁型")
    # 安全检查，防止路径穿越
    if not q_type or "/" in q_type or "\\" in q_type:
        return jsonify({"message": "no cache", "status": "error"})
        
    question_file = os.path.join(DATA_DIR, f"{q_type}.json")
    if os.path.exists(question_file):
        return jsonify({"message": "cache hit", "status": "success"})
    else:
        return jsonify({"message": "no cache", "status": "success"})

@app.route('/create_new', methods=['POST'])
def create_new():
    try:
        q_type = request.args.get("type", "未知类型")
        data = request.get_json(force=True, silent=True)
        
        if not data or "questions" not in data:
            return jsonify({"status": "error", "message": "缺少 questions 字段"}), 400

        questions = data["questions"]
        paper_text = data.get("paper_text", "")

        # 1. 保存题库
        question_file = os.path.join(DATA_DIR, f"{q_type}.json")
        with open(question_file, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=4)

        # 2. 保存专属的卷首语和卷尾语
        if paper_text and "---\n" in paper_text:
            paper_file = os.path.join(DATA_DIR, f"{q_type}_paper.txt")
            with open(paper_file, "w", encoding="utf-8") as f:
                f.write(paper_text)

        return jsonify({"status": "success", "message": f"{q_type}题库及首尾语创建成功"})
    except Exception as e:
        app.logger.exception("创建题库时发生错误")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/genWord', methods=['GET'])
def generate():
    try:
        cleanup_old_files()
        q_type = request.args.get("type", "抗抑郁型")
        
        # 调用生成逻辑，传入类型
        path = generate_word(q_type)
        download_url = url_for('download_file', filename=path, _external=True)
        
        return jsonify({"status": "success", "url": download_url})
    except Exception as e:
        app.logger.exception("生成问卷时发生内部错误")
        return jsonify({"status": "error", "message": "问卷生成失败，请稍后重试或联系管理员。"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)