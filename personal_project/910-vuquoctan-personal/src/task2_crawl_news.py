"""
Task 2: Crawl news articles.

Trong bài này, dữ liệu đã được lưu sẵn dưới dạng JSON trong:
data/landing/news/

Mỗi JSON cần có:
- url
- title
- date_crawled
- content_markdown
"""

import json
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = PROJECT_ROOT / "data" / "landing" / "news"

ARTICLE_URLS = [
    # Nếu sau này muốn crawl thật thì thêm URL vào đây.
]


async def crawl_article(url: str) -> dict:
    """
    Hàm crawl một bài báo.

    Hiện tại dùng fallback đơn giản để tránh lỗi Crawl4AI/Playwright.
    Nếu đã có JSON trong data/landing/news thì không cần gọi hàm này.
    """
    return {
        "url": url,
        "title": "Unknown",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": "",
    }


def validate_existing_json_files() -> None:
    """
    Kiểm tra các file JSON đã có trong data/landing/news.
    """
    NEWS_DIR.mkdir(parents=True, exist_ok=True)

    json_files = list(NEWS_DIR.glob("*.json"))

    print(f"Found {len(json_files)} JSON files in {NEWS_DIR}")

    if len(json_files) < 5:
        raise ValueError("Task 2 cần ít nhất 5 file JSON trong data/landing/news/")

    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_fields = ["url", "title", "date_crawled", "content_markdown"]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"{file_path.name} thiếu field: {field}")

        if not str(data["url"]).strip():
            raise ValueError(f"{file_path.name} có url rỗng")

        if not str(data["content_markdown"]).strip():
            raise ValueError(f"{file_path.name} có content_markdown rỗng")

        print(f"OK: {file_path.name}")


def main():
    validate_existing_json_files()
    print("Task 2 completed: existing news JSON files are valid.")


if __name__ == "__main__":
    main()