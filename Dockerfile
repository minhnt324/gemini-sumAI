FROM python:3.10-slim

# Cài đặt các package cần thiết
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 libsm6 libxrender1 libxext6 poppler-utils && \
    pip install --no-cache-dir -r requirements.txt

# Chỉ định thư mục làm việc
WORKDIR /app

# Sao chép mã nguồn vào container
COPY . /app

# Expose port mà Flask sẽ sử dụng
EXPOSE 10000

# Chạy ứng dụng Flask
CMD ["python", "app.py"]
