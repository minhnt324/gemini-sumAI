import os
from flask import Flask, request, render_template
import requests, fitz, io
from PIL import Image
import pytesseract
import google.generativeai as genai
from bs4 import BeautifulSoup

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    error = ""
    if request.method == "POST":
        url = request.form.get("url")
        file = request.files.get("file")

        try:
            if url:
                if url.lower().endswith(".pdf"):
                    text = extract_text_from_pdf_url(url)
                else:
                    text = extract_text_from_web(url)
            elif file and file.filename:
                image = Image.open(file.stream)
                text = pytesseract.image_to_string(image)
            else:
                error = "❌ Vui lòng nhập URL hoặc upload ảnh."
                return render_template("index.html", summary=summary, error=error)

            if not text.strip():
                error = "⚠️ Không tìm thấy nội dung trong nguồn."
                return render_template("index.html", summary=summary, error=error)

            summary = generate_summary(text)
        except Exception as e:
            error = f"❌ Đã xảy ra lỗi: {str(e)}"

    return render_template("index.html", summary=summary, error=error)

def extract_text_from_web(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    return "\n".join([p.get_text() for p in soup.find_all("p")])

def extract_text_from_pdf_url(url):
    response = requests.get(url)
    response.raise_for_status()
    pdf_data = fitz.open("pdf", response.content)
    return "\n".join([page.get_text() for page in pdf_data])

def generate_summary(text):
    prompt = f"Tóm tắt nội dung sau bằng tiếng Việt, trình bày dễ đọc:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
