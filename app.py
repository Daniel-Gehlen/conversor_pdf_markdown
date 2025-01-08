from flask import Flask, render_template, request, send_file, jsonify
from PyPDF2 import PdfReader
from markdownify import markdownify as md
import os
import tempfile
import shutil

# Configuração do Flask
app = Flask(__name__, template_folder=".", static_folder=".")

# Função para extrair texto do PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Função para salvar o texto extraído como Markdown
def save_as_markdown(text, md_path):
    markdown_text = md(text)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)

# Rota principal
@app.route("/")
def index():
    return render_template("index.html")

# Rota para servir arquivos estáticos (CSS e JS)
@app.route("/<filename>")
def static_files(filename):
    return app.send_static_file(filename)

# Rota para conversão
@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    # Cria um diretório temporário
    tmpdir = tempfile.mkdtemp()
    try:
        pdf_path = os.path.join(tmpdir, file.filename)
        md_filename = f"{os.path.splitext(file.filename)[0]}.md"
        md_path = os.path.join(tmpdir, md_filename)

        # Salva o PDF no diretório temporário
        file.save(pdf_path)

        # Extrai o texto do PDF e converte para Markdown
        text = extract_text_from_pdf(pdf_path)
        save_as_markdown(text, md_path)

        # Envia o arquivo Markdown como download
        response = send_file(
            md_path,
            as_attachment=True,
            download_name=md_filename,
            mimetype="text/markdown"
        )

        # Fecha o arquivo explicitamente após o envio
        response.call_on_close(lambda: shutil.rmtree(tmpdir, ignore_errors=True))
        return response

    except Exception as e:
        # Remove o diretório temporário em caso de erro
        shutil.rmtree(tmpdir, ignore_errors=True)
        return jsonify({"error": f"Erro durante a conversão: {str(e)}"}), 500

# Inicia o servidor Flask
if __name__ == "__main__":
    # Configurações para produção
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['DEBUG'] = False
    app.run(host='0.0.0.0', port=5000)