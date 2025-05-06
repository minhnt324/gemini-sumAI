import os
import requests
import fitz  # PyMuPDF
from flask import Flask, request, render_template
from google.generativeai import configure, GenerativeModel

app = Flask(__name__)

# Cấu hình API Gemini
configure(api_key=os.getenv("GEMINI_API_KEY"))
model = GenerativeModel("gemini-2.0-flash")

def summarize_text(text):
    prompt = f"Tóm tắt nội dung sau bằng tiếng Việt, trình bày dễ đọc:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text.strip()

def extract_text_from_pdf_url(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code != 200:
        return None, f"Lỗi tải PDF: {response.status_code}"
    pdf_data = response.content
    doc = fitz.open("pdf", pdf_data)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip(), None

def extract_text_from_web(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None, f"Lỗi truy cập trang web: {response.status_code}"
        return response.text.strip(), None
    except Exception as e:
        return None, f"Lỗi: {str(e)}"

def is_pdf_url(url):
    return url.lower().endswith(".pdf")

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    error = None

    if request.method == 'POST':
        url = request.form.get('url')

        if not url:
            error = "Vui lòng nhập URL."
        else:
            if is_pdf_url(url):
                text, error = extract_text_from_pdf_url(url)
            else:
                text, error = extract_text_from_web(url)

            if text:
                summary = summarize_text(text)

    return render_template("index.html", summary=summary, error=error)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
