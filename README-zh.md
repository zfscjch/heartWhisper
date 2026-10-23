# 心语 AI 插件：心理测试卷生成器

[English Version](./README.md)

版本：`0.0.1`

---

一个为 [Coze](https://www.coze.cn/) 提供服务的心理调查问卷生成接口。调用后随机从题库中抽取题目，生成一份 Word 格式（`.docx`）的心理调查问卷，并返回可下载的文件链接。

## 功能简介

- **随机组卷**：题库共 5 组，每组随机抽取至多 2 道题目，最多生成 10 道题。
- **正反向计分**：题目可标记为反向计分，生成时会自动附上「【本题需要反向评分】」提示。
- **固定首尾**：问卷自动包含卷首语（含评分标准）与卷尾语（含结果评估参考）。
- **自动清理**：服务端会定期清理过期或超量的生成文件，防止磁盘溢出。
- **无需参数**：接口为无参 GET 请求，方便 Coze 插件直接调用。

# 项目结构

核心文件：

`paper_server.py`（Flask 入口）

`gen_word.py`（生成逻辑）

`paper_example.txt`（首尾语）

`titles.json`（题库）

`requirements.txt`（依赖）

生产部署使用 `run.py`。

## 环境要求

- Python 3.9+（`gen_word.py` 使用了 `dict[str, ...]` 类型注解，建议 3.9 及以上）
- 依赖见 `requirements.txt`：

```txt
flask>=3.1.3
python-docx>=1.2.0
gevent>=26.8.0
```

安装依赖：

```bash
pip install -r requirements.txt
```

## 快速开始

### 开发模式（Flask 内置服务器）

```bash
python paper_server.py
```

服务将监听 `http://0.0.0.0:5000`，并开启 `debug=True`。

> Windows 用户也可直接双击 `start.bat`。

### 生产模式（gevent + HTTPS）

1. 将 `run.example.py` 复制为 `run.py`；
2. 修改其中的 `CERT_FILE` 与 `KEY_FILE` 为你的 SSL 证书与私钥路径；
3. 启动：

```bash
python run.py
```

服务将监听 `https://0.0.0.0:5000`。

> Windows 用户也可直接双击 `start_run.bat`。

## 请求参数

无需参数。

| 项目 | 说明 |
| --- | --- |
| 方法 | `GET` |
| 路径 | `/genWord` |
| 参数 | 无 |

## 返回数据

成功时返回 HTTP 200：

```json
{
    "status": "success",
    "url": "https://your-domain/doc/a1b2c3d4.docx"
}
```

失败时返回 HTTP 500：

```json
{
    "status": "error",
    "message": "问卷生成失败，请稍后重试或联系管理员。"
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `status` | string | `success` 或 `error` |
| `url` | string | 生成文档的下载链接（仅成功时返回） |
| `message` | string | 错误描述（仅失败时返回） |

## 接口说明

### `GET /genWord`

生成一份随机心理调查问卷，返回下载链接。调用前会先执行旧文件清理。

### `GET /doc/<filename>`

下载已生成的问卷文件。内部使用 `send_from_directory`，自带路径安全检查，防止路径穿越攻击。文件以附件形式（`as_attachment=True`）返回。

## 示例调用

### JavaScript (fetch)

```js
fetch('/genWord', {
    method: "GET",
    headers: {
        "User-Agent": "...",
    },
})
    .then((res) => { return res.json(); })
    .then((data) => {
        if (data.status === "success") {
            const url = data.url;
            console.log("下载地址：", url);
        } else {
            console.error("生成失败：", data.message);
        }
    })
    .catch((err) => {
        console.error(err);
    });
```

### curl

```bash
curl -X GET http://127.0.0.1:5000/genWord
```

### Python (requests)

```python
import requests

resp = requests.get("http://127.0.0.1:5000/genWord")
data = resp.json()
if data["status"] == "success":
    print("下载地址：", data["url"])
else:
    print("生成失败：", data["message"])
```

## 数据文件说明

### `paper_example.txt`

包含卷首语与卷尾语，二者以单独一行 `---` 分隔。**必须包含该分隔符**，否则 `load_data()` 会抛出 `ValueError`。

### `titles.json`

题库，结构为二维数组：外层数组代表 5 个题目分组，内层数组为该组的题目列表。每道题包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `question_text` | string | 题干文本 |
| `is_reverse_scored` | bool | 是否为反向计分题 |

> 注意：当前题目分组固定为 5 组（`gen_word.py` 中循环 `range(5)`），若题库组数少于 5 会抛出 `IndexError`。

## 文件清理策略

服务端在每次生成前调用 `cleanup_old_files()`：

- 当 `doc/` 中 `.docx` 文件数超过 `MAX_FILES`（默认 100）时，按修改时间从旧到新删除，直至降至阈值以下（额外多删 10 个作为缓冲）。
- 当文件数未超限时，删除修改时间超过 `MAX_FILE_AGE`（默认 3600 秒，即 1 小时）的文件。
- 清理过程中的删除异常会被忽略，不会影响主流程。

## 注意事项

- `paper_server.py` 中 `debug=True` 仅用于开发，**生产环境请使用 `run.py`**（gevent + HTTPS）。
- 生成的文件名由 `uuid4` 前 8 位十六进制字符组成，理论上有极小概率重复。
- 本问卷仅用于心理健康状况的初步筛查与自我了解，**不能作为临床医学诊断的依据**。

## 版本

`0.0.1`