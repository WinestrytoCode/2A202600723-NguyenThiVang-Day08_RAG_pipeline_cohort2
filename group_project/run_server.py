#!/usr/bin/env python3
"""
Khởi động DrugLaw Search Engine backend.
Chạy từ thư mục gốc của project:
  python group_project/run_server.py
"""
import sys
from pathlib import Path

# Thêm project root vào path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("  ⚖️  DrugLaw Search Engine — Backend API")
    print("=" * 60)
    print("  API:      http://localhost:8000")
    print("  Frontend: http://localhost:8000")
    print("  Docs:     http://localhost:8000/docs")
    print("=" * 60)
    print()

    uvicorn.run(
        "group_project.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
    )
