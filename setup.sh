#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# ANSI escape codes for colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}          DrugLaw Search Engine — Setup Project             ${NC}"
echo -e "${BLUE}============================================================${NC}"

# Step 1: Check Python
echo -e "\n${YELLOW}[Step 1] Kiểm tra Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Lỗi: Python 3 chưa được cài đặt trên hệ thống.${NC}"
    exit 1
fi
python3 --version

# Step 2: Create virtual environment (venv)
echo -e "\n${YELLOW}[Step 2] Khởi tạo môi trường ảo (venv)...${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✓ Đã tạo thư mục .venv${NC}"
else
    echo -e "${GREEN}✓ Môi trường ảo .venv đã tồn tại${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

# Step 3: Install dependencies
echo -e "\n${YELLOW}[Step 3] Cài đặt các thư viện từ requirements.txt...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Cài đặt thư viện thành công${NC}"

# Step 4: Verify directory structure
echo -e "\n${YELLOW}[Step 4] Khởi tạo các thư mục lưu trữ dữ liệu...${NC}"
mkdir -p data/landing/legal
mkdir -p data/landing/news
mkdir -p data/standardized/legal
mkdir -p data/standardized/news
echo -e "${GREEN}✓ Cấu trúc thư mục dữ liệu đã sẵn sàng${NC}"

# Step 5: Crawl news articles
echo -e "\n${YELLOW}[Step 5] Crawl dữ liệu tin tức báo chí...${NC}"
python3 src/task2_crawl_news.py
echo -e "${GREEN}✓ Hoàn thành crawl tin tức${NC}"

# Step 6: Convert legal documents (Markdown conversion)
echo -e "\n${YELLOW}[Step 6] Chuyển đổi văn bản pháp luật sang Markdown...${NC}"
python3 src/task3_convert_markdown.py
echo -e "${GREEN}✓ Hoàn thành chuyển đổi Markdown${NC}"

# Step 7: Chunking & Indexing into Vector Database
echo -e "\n${YELLOW}[Step 7] Phân đoạn và lập chỉ mục vào database ChromaDB...${NC}"
python3 src/task4_chunking_indexing.py
echo -e "${GREEN}✓ Hoàn thành tạo database chỉ mục${NC}"

echo -e "\n${GREEN}============================================================${NC}"
echo -e "${GREEN}          Setup thành công! Sẵn sàng khởi chạy project.      ${NC}"
echo -e "${GREEN}============================================================${NC}"

echo -e "\n${YELLOW}Hướng dẫn chạy hệ thống:${NC}"
echo -e "Kích hoạt môi trường ảo: ${BLUE}source .venv/bin/activate${NC}"
echo -e "1. Chạy Backend API (FastAPI & Web UI):"
echo -e "   ${BLUE}python3 group_project/run_server.py${NC}"
echo -e "   -> Truy cập Web UI tại: ${BLUE}http://localhost:8000${NC}"
echo -e "2. Chạy Streamlit Search App (Giao diện thay thế):"
echo -e "   ${BLUE}streamlit run group_project/search_app.py${NC}"
echo -e "   -> Truy cập Streamlit UI tại: ${BLUE}http://localhost:8501${NC}"
echo -e "\n"
