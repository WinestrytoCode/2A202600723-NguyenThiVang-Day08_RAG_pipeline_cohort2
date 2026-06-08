"""
Task 3 — Convert toàn bộ file trong data/landing/ thành Markdown.

- legal/: PDF/DOCX → markdown bằng MarkItDown (Microsoft).
- news/:  JSON đã crawl (đã có 'content_markdown') → markdown + header metadata.

Output lưu vào data/standardized/ giữ nguyên cấu trúc thư mục con (legal/, news/).

Chạy:
    python -m src.task3_convert_markdown
"""

import json
from pathlib import Path

from markitdown import MarkItDown

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> int:
    """Convert PDF/DOCX trong data/landing/legal/ sang markdown. Trả số file OK."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    md = MarkItDown()
    count = 0
    for filepath in sorted(legal_dir.iterdir()):
        if filepath.suffix.lower() not in (".pdf", ".docx", ".doc"):
            continue
        print(f"Converting: {filepath.name}")
        output_path = output_dir / f"{filepath.stem}.md"
        try:
            text = md.convert(str(filepath)).text_content
        except Exception as e:
            print(f"  ✗ Lỗi convert {filepath.name}: {e}")
            continue
        # PDF scan (ký số) không có lớp text → trích rỗng. Bỏ qua + xoá output cũ.
        if len(text.strip()) < 200:
            print(f"  ⚠ Bỏ qua {filepath.name}: chỉ trích được {len(text.strip())} ký tự "
                  f"(có thể là PDF scan, cần nguồn text).")
            if output_path.exists():
                output_path.unlink()
            continue
        output_path.write_text(text, encoding="utf-8")
        print(f"  ✓ {output_path.name} ({len(text):,} ký tự)")
        count += 1
    return count


def convert_news_articles() -> int:
    """Convert JSON bài báo trong data/landing/news/ sang markdown. Trả số file OK."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for filepath in sorted(news_dir.iterdir()):
        if filepath.suffix.lower() != ".json":
            continue
        print(f"Converting: {filepath.name}")
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ✗ Lỗi đọc {filepath.name}: {e}")
            continue

        header = (
            f"# {data.get('title', 'Unknown')}\n\n"
            f"**Nguồn:** {data.get('url', 'N/A')}\n"
            f"**Ngày crawl:** {data.get('date_crawled', 'N/A')}\n\n"
            "---\n\n"
        )
        content = header + data.get("content_markdown", "")
        output_path = output_dir / f"{filepath.stem}.md"
        output_path.write_text(content, encoding="utf-8")
        print(f"  ✓ {output_path.name} ({len(content):,} ký tự)")
        count += 1
    return count


def convert_all():
    """Convert toàn bộ legal + news."""
    print("=" * 50)
    print("Task 3: Convert to Markdown (MarkItDown)")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    n_legal = convert_legal_docs()

    print("\n--- News Articles ---")
    n_news = convert_news_articles()

    print(f"\n✓ Done! legal={n_legal}, news={n_news} → {OUTPUT_DIR}")
    return n_legal, n_news


if __name__ == "__main__":
    convert_all()
