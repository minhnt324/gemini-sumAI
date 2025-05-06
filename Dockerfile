FROM python:3.10-slim

# Cài đặt các package cần thiết
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 libsm6 libxrender1 libxext6 poppler-utils

# Chỉ định thư mục làm việc
WORKDIR /app

# Sao chép tệp requirements.txt vào container
COPY requirements.txt .

# Cài đặt các thư viện từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . /app

# Expose port mà Flask sẽ sử dụng
EXPOSE 10000

# Đảm bảo biến môi trường FLASK_APP được thiết lập
ENV FLASK_APP=app.py

# Chạy ứng dụng Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=10000"]
