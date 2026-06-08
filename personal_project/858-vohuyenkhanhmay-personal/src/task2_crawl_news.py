"""
Task 2 — Crawl bài báo về nghệ sĩ liên quan tới ma tuý.

Crawl 11 bài từ VnExpress / Tuổi Trẻ / Thanh Niên / Dân Trí bằng Crawl4AI,
LỌC SẠCH theo css_selector của từng báo (chỉ lấy thân bài, bỏ nav/menu/footer).
Lưu mỗi bài 1 JSON vào data/landing/news/ (url, title, date_crawled, content_markdown).

Chạy:
    python -m src.task2_crawl_news

Lần đầu cần tải Chromium:  python -m playwright install chromium
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

# Danh sách bài báo, sắp xếp mới → cũ (article_01 = bài mới nhất).
ARTICLE_URLS = [
    "https://tuoitre.vn/bat-ca-si-long-nhat-va-ca-si-son-ngoc-minh-vi-lien-quan-ma-tuy-20260520082138943.htm",
    "https://tuoitre.vn/ca-si-miu-le-bi-bat-o-hai-phong-20260511172700149.htm",
    "https://vnexpress.net/hoai-dj-linh-an-tu-hinh-5071068.html",
    "https://vnexpress.net/co-tien-tu-thien-o-tp-hcm-vuong-lao-ly-sau-dem-tiec-sinh-nhat-ban-5058984.html",
    "https://dantri.com.vn/phap-luat/nguoi-mau-an-tay-ru-ban-va-tro-ly-cung-su-dung-ma-tuy-20260406152426197.htm",
    "https://tuoitre.vn/bat-nguoi-mau-an-tay-ca-si-chi-dan-co-tien-truc-phuong-do-lien-quan-ma-tuy-20241114114826655.htm",
    "https://vnexpress.net/nguoi-mau-nhikolai-dinh-bi-bat-vi-tang-tru-ma-tuy-4762598.html",
    "https://tuoitre.vn/cong-an-dua-ca-si-chu-bin-ve-tru-so-de-lam-ro-hanh-vi-nghi-lien-quan-ma-tuy-20240606194450472.htm",
    "https://thanhnien.vn/dien-vien-hai-huu-tin-lanh-7-nam-6-thang-tu-185230428134549434.htm",
    "https://thanhnien.vn/nu-dien-vien-le-hang-bi-bat-vi-di-buon-ma-tuy-185230423181213443.htm",
    "https://vnexpress.net/ca-si-chau-viet-cuong-nhan-13-nam-tu-vi-nhet-toi-hai-chet-co-gai-3891028.html",
]

# css_selector chứa thân bài cho từng báo (title + sapo + nội dung).
SITE_SELECTORS = {
    "vnexpress.net": ".title-detail, .description, .fck_detail",
    "tuoitre.vn": ".detail-title, .detail-sapo, .detail-content",
    "thanhnien.vn": ".detail-title, .detail-sapo, .detail-content",
    "dantri.com.vn": ".e-magazine__title, .singular-sapo, .singular-content, .dt-news__content",
}

# Tag rác bỏ đi (dùng cho cả primary lẫn fallback).
EXCLUDED_TAGS = ["script", "style", "nav", "header", "footer", "aside", "form"]
MIN_CHARS = 500  # body ngắn hơn coi như selector hụt → fallback


def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _selector_for(url: str):
    host = urlparse(url).netloc.replace("www.", "")
    for domain, selector in SITE_SELECTORS.items():
        if domain in host:
            return selector
    return None


async def crawl_article(url: str, crawler) -> dict:
    """Crawl 1 bài, ưu tiên css_selector của báo; nếu hụt thì fallback lọc tag."""
    from crawl4ai import CrawlerRunConfig, CacheMode

    selector = _selector_for(url)

    # Primary: chỉ lấy thân bài theo selector của báo.
    primary = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        css_selector=selector,
        excluded_tags=EXCLUDED_TAGS,
        exclude_external_links=True,
        word_count_threshold=10,
    )
    result = await crawler.arun(url=url, config=primary)
    body = str(result.markdown or "") if result.success else ""

    # Fallback: bỏ selector, lọc tag rác + bỏ block ngắn (drop menu/nav còn sót).
    if len(body) < MIN_CHARS:
        fallback = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            excluded_tags=EXCLUDED_TAGS,
            exclude_external_links=True,
            word_count_threshold=50,
        )
        result = await crawler.arun(url=url, config=fallback)
        body = str(result.markdown or "") if result.success else ""

    if not result.success:
        raise RuntimeError(result.error_message or "crawl failed")

    # Metadata title hay rỗng khi dùng css_selector → lấy từ heading đầu của body.
    title = (result.metadata or {}).get("title") or ""
    if not title or title == "Unknown":
        for line in body.splitlines():
            s = line.strip()
            if s.startswith("# "):
                title = s.lstrip("#").strip()
                break
        title = title or "Unknown"

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": body,
    }


async def crawl_all():
    """Crawl toàn bộ ARTICLE_URLS, lưu JSON. Trả số bài lưu thành công."""
    from crawl4ai import AsyncWebCrawler, BrowserConfig

    setup_directory()
    browser = BrowserConfig(headless=True, browser_type="chromium", ignore_https_errors=True)

    saved = 0
    async with AsyncWebCrawler(config=browser) as crawler:
        for i, url in enumerate(ARTICLE_URLS, 1):
            try:
                article = await crawl_article(url, crawler)
                if len(article["content_markdown"]) < MIN_CHARS:
                    print(f"  ✗ Bỏ qua {url}: nội dung quá ngắn")
                    continue
            except Exception as e:
                print(f"  ✗ {url}: {e}")
                continue

            out = DATA_DIR / f"article_{i:02d}.json"
            out.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
            saved += 1
            print(f"  ✓ {out.name} ({len(article['content_markdown']):,} ký tự) — {article['title'][:50]}")
            await asyncio.sleep(1)  # lịch sự với server

    print(f"\n✓ Lưu {saved}/{len(ARTICLE_URLS)} bài (yêu cầu tối thiểu 5).")
    return saved


if __name__ == "__main__":
    asyncio.run(crawl_all())
