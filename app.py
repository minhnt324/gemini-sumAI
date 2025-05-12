import os
from flask import Flask, request, render_template
import requests, fitz, io
from PIL import Image
import pytesseract
import google.generativeai as genai
from bs4 import BeautifulSoup
from docx import Document  # ✅ xử lý file Word

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'docx'}  # ✅ cho phép file Word

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    error = ""

    if request.method == "POST":
        input_type = request.form.get("input_type")
        url = request.form.get("url")
        file = request.files.get("file")
        raw_text = request.form.get("raw_text")

        try:
            text = ""

            if input_type == "url" and url:
                if url.lower().endswith(".pdf"):
                    text = extract_text_from_pdf_url(url)
                else:
                    text = extract_text_from_web(url)

            elif input_type == "file" and file and file.filename:
                ext = file.filename.rsplit(".", 1)[1].lower()

                if ext == "pdf":
                    text = extract_text_from_pdf(file)
                elif ext == "docx":
                    text = extract_text_from_docx(file)
                else:
                    image = Image.open(file.stream)
                    text = pytesseract.image_to_string(image)

            elif input_type == "text" and raw_text:
                text = raw_text

            else:
                error = "❌ Vui lòng nhập đúng loại dữ liệu tương ứng."
                return render_template("index.html", summary=summary, error=error)

            if not text.strip():
                error = "⚠️ Không tìm thấy nội dung trong nguồn."
                return render_template("index.html", summary=summary, error=error)

            summary = generate_summary(text)

        except Exception as e:
            error = f"❌ Đã xảy ra lỗi: {str(e)}"

    return render_template("index.html", summary=summary, error=error)

def extract_text_from_docx(file):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    os.remove(file_path)
    return text

def extract_text_from_pdf(file):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    with fitz.open(file_path) as doc:
        first_page_text = doc[0].get_text().strip()

        if len(first_page_text) > 20:
            text = "\n".join([page.get_text() for page in doc])
        else:
            text = ""
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_bytes))
                page_text = pytesseract.image_to_string(image)
                text += page_text + "\n"

    os.remove(file_path)
    return text

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
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host="0.0.0.0", port=10000)
