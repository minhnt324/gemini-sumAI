FROM python:3.10-slim

# Tạo thư mục làm việc
WORKDIR /app

# Copy file requirements.txt trước để cài dependencies
COPY requirements.txt /app/

# Cài đặt các package cần thiết và thư viện Python
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 libsm6 libxrender1 libxext6 poppler-utils && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /app/uploads

# Copy toàn bộ mã nguồn còn lại
COPY . /app

# Mở port Flask app
EXPOSE 10000

# Chạy ứng dụng Flask
CMD ["python", "app.py"]
