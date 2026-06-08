"""
Crawl HTML fallback cho văn bản pháp luật KHÔNG convert được từ PDF
(PDF scan ký số → markitdown trích 0 ký tự).

Lấy toàn văn từ thuvienphapluat.vn (selector nội dung: .cldivContentDocVn),
chuyển sang markdown, lưu vào data/standardized/legal/.

Chạy:
    python -m src.crawl_legal_html
"""

import asyncio
from datetime import datetime
from pathlib import Path

OUT_DIR = Path(__file__).parent.parent / "data" / "standardized" / "legal"

# (filename .md, url HTML toàn văn). Các văn bản PDF scan không trích được text.
LEGAL_HTML = [
    ("nghi-dinh-105-2021-nd-cp.md",
     "https://thuvienphapluat.vn/van-ban/Van-hoa-Xa-hoi/Nghi-dinh-105-2021-ND-CP-huong-dan-Luat-Phong-chong-ma-tuy-496664.aspx"),
    ("nghi-dinh-57-2022-nd-cp.md",
     "https://thuvienphapluat.vn/van-ban/Van-hoa-Xa-hoi/Nghi-dinh-57-2022-ND-CP-danh-muc-chat-ma-tuy-va-tien-chat-527507.aspx"),
    ("nghi-dinh-90-2024-nd-cp.md",
     "https://thuvienphapluat.vn/van-ban/Van-hoa-Xa-hoi/Nghi-dinh-90-2024-ND-CP-sua-doi-Danh-muc-chat-ma-tuy-tien-chat-theo-Nghi-dinh-57-2022-ND-CP-607161.aspx"),
]

# Selector chứa toàn văn văn bản trên thuvienphapluat.vn
CONTENT_SELECTOR = ".cldivContentDocVn"
MIN_CHARS = 500


async def crawl_legal():
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    browser = BrowserConfig(headless=True, browser_type="chromium", ignore_https_errors=True)
    run = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        css_selector=CONTENT_SELECTOR,   # chỉ lấy phần thân văn bản, bỏ nav/footer
        word_count_threshold=5,
    )

    saved = 0
    async with AsyncWebCrawler(config=browser) as crawler:
        for name, url in LEGAL_HTML:
            result = await crawler.arun(url=url, config=run)
            if not result.success:
                print(f"  ✗ {name}: {result.error_message}")
                continue
            body = str(result.markdown or "")
            flag = "✓" if len(body) >= MIN_CHARS else "⚠"
            print(f"  {flag} {name} ({len(body):,} ký tự body)")
            if len(body) < MIN_CHARS:
                continue
            title = (result.metadata or {}).get("title", name)
            header = (
                f"# {title}\n\n"
                f"**Nguồn:** {url}\n"
                f"**Crawled:** {datetime.now().isoformat()}\n\n"
                "---\n\n"
            )
            (OUT_DIR / name).write_text(header + body, encoding="utf-8")
            saved += 1
            await asyncio.sleep(1)

    print(f"\n✓ Crawl HTML: lưu {saved}/{len(LEGAL_HTML)} văn bản.")
    return saved


if __name__ == "__main__":
    asyncio.run(crawl_legal())
