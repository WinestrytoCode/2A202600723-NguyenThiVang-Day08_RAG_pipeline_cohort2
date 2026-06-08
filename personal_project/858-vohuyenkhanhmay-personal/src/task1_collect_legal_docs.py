"""
Task 1 — Thu thập văn bản pháp luật về ma tuý và các chất cấm.

Tải các văn bản pháp luật (PDF) từ Cổng Thông tin điện tử Chính phủ
(datafiles.chinhphu.vn) về data/landing/legal/. Nguồn chính thống, tải
trực tiếp, không cần đăng nhập.

Chạy:
    python -m src.task1_collect_legal_docs
"""

from pathlib import Path

import requests

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

# (filename không dấu, url tải trực tiếp). Đã xác minh trả về application/pdf.
LEGAL_DOCS = [
    ("luat-phong-chong-ma-tuy-2021.pdf",
     "https://datafiles.chinhphu.vn/cpp/files/vbpq/2022/01/73luat.pdf"),
    ("bo-luat-hinh-su-2015.pdf",  # Chương XX: tội phạm về ma tuý (Điều 247–259)
     "https://datafiles.chinhphu.vn/cpp/files/vbpq/2025/9/135-vbhn-vpqh.pdf"),
    ("nghi-dinh-105-2021-nd-cp.pdf",  # hướng dẫn Luật Phòng chống ma tuý
     "https://datafiles.chinhphu.vn/cpp/files/vbpq/2021/12/105.signed_02.pdf"),
    ("nghi-dinh-57-2022-nd-cp.pdf",  # danh mục chất ma tuý và tiền chất
     "https://datafiles.chinhphu.vn/cpp/files/vbpq/2022/08/57-cp.signed.pdf"),
    ("nghi-dinh-90-2024-nd-cp.pdf",  # sửa đổi danh mục chất ma tuý/tiền chất
     "https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/7/90nd.signed.pdf"),
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def setup_directory():
    """Tạo thư mục data/landing/legal/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_file(filename: str, url: str) -> bool:
    """Tải 1 file về DATA_DIR; kiểm tra là PDF hợp lệ (>1KB). Trả True nếu OK."""
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=120)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ✗ {filename}: lỗi tải ({e})")
        return False

    content = resp.content
    if not content.startswith(b"%PDF"):
        print(f"  ✗ {filename}: không phải PDF (có thể là trang login/redirect)")
        return False
    if len(content) < 1024:
        print(f"  ✗ {filename}: file quá nhỏ ({len(content)} bytes)")
        return False

    (DATA_DIR / filename).write_bytes(content)
    print(f"  ✓ {filename} ({len(content):,} bytes)")
    return True


def collect_all() -> int:
    """Tải toàn bộ văn bản trong LEGAL_DOCS. Trả số file tải thành công."""
    setup_directory()
    print(f"Tải văn bản pháp luật → {DATA_DIR}")
    ok = sum(download_file(name, url) for name, url in LEGAL_DOCS)
    print(f"\n✓ Tải thành công {ok}/{len(LEGAL_DOCS)} file (yêu cầu tối thiểu 3).")
    return ok


if __name__ == "__main__":
    collect_all()
