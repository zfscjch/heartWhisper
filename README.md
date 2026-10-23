# Xinyu AI Plugin: Psychological Questionnaire Generator

[中文版](./README-zh.md)

Version: `0.0.1`

---

An API that generates psychological survey questionnaires for [Coze](https://www.coze.com/). On each call, questions are randomly drawn from a question bank, a Word document (`.docx`) is generated, and a download link is returned.

## Features

- **Random selection**: The question bank is organized into 5 groups; up to 2 questions are drawn from each group, for a maximum of 10 questions per questionnaire.
- **Reverse scoring support**: Questions can be flagged for reverse scoring; a `【本题需要反向评分】` hint is automatically appended when generated.
- **Fixed header & footer**: Every questionnaire automatically includes the opening remarks (with scoring criteria) and closing remarks (with result interpretation guidance).
- **Automatic cleanup**: The server periodically removes expired or excess generated files to prevent disk overflow.
- **No parameters**: The endpoint is a parameterless GET request, making it easy for Coze plugins to call directly.

# Project Structure

Core files:

`paper_server.py` (Flask entry point)

`gen_word.py` (generation logic)

`paper_example.txt` (opening & closing remarks)

`titles.json` (question bank)

`requirements.txt` (dependencies)

Production deployment uses `run.py`.

## Requirements

- Python 3.9+ (`gen_word.py` uses `dict[str, ...]` type hints; 3.9 or newer recommended)
- Dependencies (see `requirements.txt`):

```txt
flask>=3.1.3
python-docx>=1.2.0
gevent>=26.8.0
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Development mode (Flask built-in server)

```bash
python paper_server.py
```

The service listens on `http://0.0.0.0:5000` with `debug=True` enabled.

> On Windows, you can also double-click `start.bat`.

### Production mode (gevent + HTTPS)

1. Copy `run.example.py` to `run.py`;
2. Set `CERT_FILE` and `KEY_FILE` in it to your SSL certificate and private key paths;
3. Start the server:

```bash
python run.py
```

The service listens on `https://0.0.0.0:5000`.

> On Windows, you can also double-click `start_run.bat`.

## Request

No parameters required.

| Item | Description |
| --- | --- |
| Method | `GET` |
| Path | `/genWord` |
| Parameters | None |

## Response

On success, returns HTTP 200:

```json
{
    "status": "success",
    "url": "https://your-domain/doc/a1b2c3d4.docx"
}
```

On failure, returns HTTP 500:

```json
{
    "status": "error",
    "message": "Questionnaire generation failed. Please try again later or contact the administrator."
}
```

| Field | Type | Description |
| --- | --- | --- |
| `status` | string | `success` or `error` |
| `url` | string | Download URL of the generated document (only on success) |
| `message` | string | Error description (only on failure) |

## Endpoints

### `GET /genWord`

Generates a random psychological questionnaire and returns a download link. Old files are cleaned up before generation.

### `GET /doc/<filename>`

Downloads a previously generated questionnaire. Internally uses `send_from_directory`, which includes path traversal protection. The file is returned as an attachment (`as_attachment=True`).

## Example Usage

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
            console.log("Download URL:", url);
        } else {
            console.error("Generation failed:", data.message);
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
    print("Download URL:", data["url"])
else:
    print("Generation failed:", data["message"])
```

## Data Files

### `paper_example.txt`

Contains the opening and closing remarks, separated by a line containing only `---`. **This separator is required**; otherwise `load_data()` raises `ValueError`.

### `titles.json`

The question bank, structured as a 2D array: the outer array represents 5 question groups, and each inner array is the list of questions in that group. Each question contains:

| Field | Type | Description |
| --- | --- | --- |
| `question_text` | string | The question text |
| `is_reverse_scored` | bool | Whether the question is reverse-scored |

> Note: The number of question groups is fixed at 5 (`range(5)` in `gen_word.py`); fewer than 5 groups will raise `IndexError`.

## File Cleanup Policy

The server calls `cleanup_old_files()` before each generation:

- When the number of `.docx` files in `doc/` exceeds `MAX_FILES` (default 100), files are deleted oldest-first by modification time until the count drops below the threshold (with an extra 10-file buffer).
- When the count is within the limit, files older than `MAX_FILE_AGE` (default 3600 seconds, i.e. 1 hour) are deleted.
- Deletion errors during cleanup are silently ignored and do not affect the main flow.

## Notes

- `debug=True` in `paper_server.py` is for development only. **Use `run.py` (gevent + HTTPS) in production.**
- Generated filenames are the first 8 hex characters of a `uuid4`, with a negligible chance of collision.
- This questionnaire is intended only for preliminary screening and self-understanding of mental health status, and **must not be used as a basis for clinical diagnosis**.

## Version

`0.0.1`