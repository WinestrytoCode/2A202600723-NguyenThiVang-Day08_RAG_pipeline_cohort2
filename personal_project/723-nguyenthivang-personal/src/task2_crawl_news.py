"""
Task 2 — Crawl bài báo về nghệ sĩ liên quan tới ma tuý.

Hướng dẫn:
    1. Crawl tối thiểu 5 bài báo từ các trang tin tức Việt Nam.
    2. Sử dụng Crawl4AI hoặc thư viện crawling tương tự.
    3. Lưu output vào data/landing/news/
    4. Mỗi bài lưu 1 file JSON với metadata (url, title, date_crawled, content).

Cài đặt:
    pip install crawl4ai
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"


def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# TODO: Điền danh sách URL bài báo cần crawl
ARTICLE_URLS = [
    "https://tuoitre.vn/nghe-si-va-ma-tuy-danh-doi-ca-su-nghiep-20241110091216503.htm",
    "https://tuoitre.vn/ca-si-chi-dan-nguoi-mau-an-tay-bi-dieu-tra-vi-lien-quan-ma-tuy-20241110084535359.htm",
    "https://tuoitre.vn/nguoi-mau-an-tay-bi-khoi-to-toi-to-chuc-su-dung-va-tang-tru-ma-tuy-20241114175653556.htm",
    "https://tuoitre.vn/ca-si-chi-dan-bi-khoi-to-toi-to-chuc-su-dung-trai-phep-chat-ma-tuy-20241114172551525.htm",
    "https://tuoitre.vn/kham-xet-noi-o-cua-ca-si-chi-dan-nguoi-mau-an-tay-20241110121124701.htm",
    "https://tuoitre.vn/dien-vien-huu-tin-linh-7-nam-6-thang-tu-vi-to-chuc-su-dung-ma-tuy-20230428135851493.htm",
    "https://tuoitre.vn/ca-si-chau-viet-cuong-linh-13-nam-tu-giam-20190307130545935.htm",
    "https://tuoitre.vn/bat-giam-ca-si-chu-bin-to-chuc-su-dung-ma-tuy-tai-quan-10-20240606132717326.htm",
    "https://vnexpress.net/ma-tuy-trong-loi-song-showbiz-5074606.html",
    "https://vnexpress.net/long-nhat-duoc-biet-den-ra-sao-truoc-khi-bi-bat-lien-quan-ma-tuy-5076279.html",
    "https://vnexpress.net/anh-em-ca-si-chi-dan-ru-nhieu-nguoi-choi-ma-tuy-nhu-the-nao-4929804.html",
    "https://vnexpress.net/nguoi-mau-andrea-aybar-va-ca-si-chi-dan-bi-bat-4814295.html",
    "https://vnexpress.net/227-nguoi-bi-truy-to-trong-vu-4-tiep-vien-hang-khong-xach-ma-tuy-5057648.html",
    "https://vnexpress.net/trum-ma-tuy-dung-sau-duong-day-lien-quan-4-tiep-vien-hang-khong-5059153.html",
    "https://tuoitre.vn/hot-girl-dieu-hanh-duong-day-cung-cap-nuoc-vui-thuoc-lac-cho-nguoi-nuoc-ngoai-20260602145446559.htm",
    "https://tuoitre.vn/nha-trang-tang-cuong-ra-soat-xet-nghiem-ma-tuy-gom-ca-nguoi-nuoc-ngoai-20260607143603699.htm"
]


async def crawl_article(url: str) -> dict:
    """
    Crawl một bài báo và trả về dict chứa metadata + content.
    Sử dụng requests và BeautifulSoup thay vì Playwright để tránh lỗi môi trường.
    """
    import requests
    from bs4 import BeautifulSoup
    from markdownify import markdownify as md
    
    # Run requests in thread to avoid blocking asyncio
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None, 
        lambda: requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    )
    
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "Unknown"
    
    # Extract main content
    article_body = soup.find("div", class_="detail-content") or soup.find("article") or soup.body
    markdown_content = md(str(article_body)) if article_body else ""
    
    return {
        "url": url,
        "title": title.strip(),
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": markdown_content.strip(),
    }


async def crawl_all():
    """Crawl toàn bộ bài báo trong ARTICLE_URLS."""
    setup_directory()

    for i, url in enumerate(ARTICLE_URLS, 1):
        print(f"[{i}/{len(ARTICLE_URLS)}] Crawling: {url}")
        article = await crawl_article(url)

        # Lưu file JSON
        filename = f"article_{i:02d}.json"
        filepath = DATA_DIR / filename
        filepath.write_text(json.dumps(article, ensure_ascii=False, indent=2))
        print(f"  ✓ Saved: {filepath}")


if __name__ == "__main__":
    if not ARTICLE_URLS:
        print("⚠ Hãy điền ARTICLE_URLS trước khi chạy!")
        print("Gợi ý: tìm bài báo trên VnExpress, Tuổi Trẻ, Thanh Niên, ...")
    else:
        asyncio.run(crawl_all())
