from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from markdownify import markdownify as md

app = Flask(__name__)

@app.route('/api/convert', methods=['POST'])
def convert_pdf_to_md():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    pdf_file = request.files['file']
    try:
        # Extrair texto do PDF
        reader = PdfReader(pdf_file)
        text = "".join([page.extract_text() for page in reader.pages])

        # Converter para Markdown
        markdown_text = md(text)
        return jsonify({"markdown": markdown_text}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao processar o arquivo: {str(e)}"}), 500
