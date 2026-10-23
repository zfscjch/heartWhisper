import os
import time
from flask import Flask, send_from_directory, jsonify, url_for
from gen_word import generate_word

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.join(BASE_DIR, "doc")
os.makedirs(DOC_DIR, exist_ok=True)

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
                try:
                    os.remove(f)
                except OSError:
                    pass
        else:
            now = time.time()
            for f in files:
                if now - os.path.getmtime(f) > MAX_FILE_AGE:
                    try:
                        os.remove(f)
                    except OSError:
                        pass
    except Exception as e:
        app.logger.warning(f"清理旧文件失败: {e}")

@app.route('/doc/<filename>')
def download_file(filename):
    # send_from_directory 内部自带了路径安全检查，防止路径穿越
    return send_from_directory(DOC_DIR, filename, as_attachment=True)

@app.route('/genWord')
def generate():
    try:
        cleanup_old_files()
        
        path = generate_word()
        
        download_url = url_for('download_file', filename=path, _external=True)
        
        return jsonify({"status": "success", "url": download_url})
        
    except Exception as e:
        app.logger.exception("生成问卷时发生内部错误")
        return jsonify({
            "status": "error", 
            "message": "问卷生成失败，请稍后重试或联系管理员。"
        }), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)