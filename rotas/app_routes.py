"""
Rotas Flask para o Conversor de Arquivos AM.
Estrutura modular similar ao I'AM.pdf.
"""

import os
import io
from flask import request, send_file, render_template_string, redirect, url_for, flash
from werkzeug.exceptions import RequestEntityTooLarge

from main import app, get_converter, save_upload_to_temp, save_converted_copy, validate_file_type, sanitize_filename, PER_FILE_LIMIT_MB
from config import get_config

config = get_config()

# ========== TEMPLATES HTML ==========

HOME_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conversor de Arquivos AM</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2c2c2c 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: #1a1a1a;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            overflow: hidden;
            border: 2px solid #ff6b35;
        }
        .header {
            background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%);
            padding: 30px;
            text-align: center;
            position: relative;
        }
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="%23ffffff" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="%23ffffff" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="%23ffffff" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.1;
        }
        .header h1 {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        .main-content {
            padding: 40px;
        }
        .upload-section {
            background: #2a2a2a;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid #ff6b35;
        }
        .upload-section h2 {
            color: #ff6b35;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #ffffff;
        }
        .file-input-container {
            position: relative;
            display: inline-block;
            width: 100%;
        }
        .file-input {
            display: none;
        }
        .file-input-label {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 15px 20px;
            background: #3a3a3a;
            border: 2px dashed #ff6b35;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: #cccccc;
        }
        .file-input-label:hover {
            background: #4a4a4a;
            border-color: #ff8c42;
        }
        .file-input-label i {
            margin-right: 10px;
            font-size: 1.2em;
        }
        .file-name {
            margin-top: 10px;
            color: #ff6b35;
            font-weight: 500;
        }
        select, button {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        select {
            background: #3a3a3a;
            color: #ffffff;
            border: 2px solid #555;
        }
        select:focus {
            border-color: #ff6b35;
            outline: none;
        }
        button {
            background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%);
            color: white;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
        }
        button:disabled {
            background: #555;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .progress-section {
            display: none;
            background: #2a2a2a;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid #ff6b35;
            text-align: center;
        }
        .progress-container {
            width: 100%;
            height: 20px;
            background: #3a3a3a;
            border-radius: 10px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #ff6b35 0%, #ff8c42 100%);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 10px;
        }
        .progress-text {
            color: #ff6b35;
            font-weight: 600;
            font-size: 1.1em;
        }
        .status-text {
            color: #cccccc;
            margin-top: 10px;
        }
        .download-section {
            display: none;
            background: #2a2a2a;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid #4CAF50;
            text-align: center;
        }
        .download-section.success {
            border-color: #4CAF50;
        }
        .download-section.error {
            border-color: #f44336;
        }
        .download-btn {
            display: inline-flex;
            align-items: center;
            padding: 15px 30px;
            background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin-top: 15px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        }
        .download-btn i {
            margin-right: 10px;
        }
        .conversions {
            margin-top: 40px;
        }
        .conversions h2 {
            color: #ff6b35;
            margin-bottom: 30px;
            text-align: center;
            font-size: 1.8em;
        }
        .conversion-category {
            margin-bottom: 30px;
            background: #2a2a2a;
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #444;
        }
        .conversion-category h3 {
            color: #ff6b35;
            margin-bottom: 20px;
            font-size: 1.4em;
            display: flex;
            align-items: center;
        }
        .conversion-category h3::before {
            content: attr(data-icon);
            margin-right: 10px;
            font-size: 1.2em;
        }
        .conversion-item {
            background: #3a3a3a;
            padding: 15px;
            margin: 8px 0;
            border-radius: 8px;
            border-left: 4px solid #ff6b35;
            transition: all 0.3s ease;
        }
        .conversion-item:hover {
            background: #4a4a4a;
            transform: translateX(5px);
        }
        .conversion-item h4 {
            margin: 0 0 8px 0;
            color: #ffffff;
            font-size: 1em;
        }
        .conversion-item p {
            margin: 5px 0;
            color: #cccccc;
            font-size: 0.9em;
        }
        .footer {
            text-align: center;
            padding: 20px;
            background: #1a1a1a;
            border-top: 1px solid #444;
            color: #888;
            font-size: 0.9em;
        }
        @media (max-width: 768px) {
            .container {
                margin: 10px;
            }
            .header {
                padding: 20px;
            }
            .header h1 {
                font-size: 2em;
            }
            .main-content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Conversor de Arquivos AM</h1>
            <p>Ferramenta profissional de conversão de arquivos</p>
        </div>

        <div class="main-content">
            <div class="upload-section">
                <h2>📤 Fazer Upload e Converter</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="file">Selecione o arquivo:</label>
                        <div class="file-input-container">
                            <input type="file" id="file" name="file" class="file-input" required>
                            <label for="file" class="file-input-label">
                                <i>📎</i> Clique para selecionar arquivo
                            </label>
                        </div>
                        <div id="fileName" class="file-name"></div>
                    </div>
                    <div class="form-group">
                        <label for="targetFormat">Formato de destino:</label>
                        <select id="targetFormat" name="target_format" required>
                            <option value="">Selecione...</option>
                            <optgroup label="🎵 Áudio">
                                <option value="mp3">MP3</option>
                                <option value="wav">WAV</option>
                            </optgroup>
                            <optgroup label="🎬 Vídeo">
                                <option value="wav">WAV (áudio)</option>
                                <option value="avi">AVI</option>
                                <option value="mp4">MP4</option>
                            </optgroup>
                            <optgroup label="🖼️ Imagem">
                                <option value="jpg">JPG</option>
                                <option value="webp">WebP</option>
                            </optgroup>
                            <optgroup label="📄 Documentos">
                                <option value="pdf">PDF</option>
                                <option value="docx">DOCX</option>
                                <option value="txt">TXT</option>
                            </optgroup>
                            <optgroup label="📊 Planilhas">
                                <option value="csv">CSV</option>
                                <option value="xlsx">XLSX</option>
                            </optgroup>
                        </select>
                    </div>
                    <button type="submit" id="convertBtn">
                        🚀 Converter Arquivo
                    </button>
                </form>
            </div>

            <div class="progress-section" id="progressSection">
                <h3>🔄 Convertendo Arquivo...</h3>
                <div class="progress-container">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                <div class="progress-text" id="progressText">0%</div>
                <div class="status-text" id="statusText">Iniciando conversão...</div>
            </div>

            <div class="download-section" id="downloadSection">
                <h3 id="resultTitle">✅ Conversão Concluída!</h3>
                <p id="resultMessage">Seu arquivo foi convertido com sucesso.</p>
                <a href="#" id="downloadBtn" class="download-btn">
                    <i>📥</i> Baixar Arquivo Convertido
                </a>
            </div>

            <div class="conversions">
                <h2>🔧 Conversões Disponíveis</h2>

                <div class="conversion-category" data-icon="🎵">
                    <h3>Áudio</h3>
                    <div class="conversion-item">
                        <h4>OGG → MP3</h4>
                        <p>Converte arquivos de áudio OGG para MP3 com qualidade 192kbps.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>MP3 → WAV</h4>
                        <p>Converte arquivos MP3 para formato WAV não comprimido.</p>
                    </div>
                </div>

                <div class="conversion-category" data-icon="🎬">
                    <h3>Vídeo</h3>
                    <div class="conversion-item">
                        <h4>MP4 → WAV</h4>
                        <p>Extrai áudio de vídeos MP4 e converte para formato WAV.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>MP4 → AVI</h4>
                        <p>Converte vídeos MP4 para formato AVI.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>M4V → MP4</h4>
                        <p>Converte vídeos M4V para formato MP4 compatível.</p>
                    </div>
                </div>

                <div class="conversion-category" data-icon="🖼️">
                    <h3>Imagem</h3>
                    <div class="conversion-item">
                        <h4>PNG → JPG</h4>
                        <p>Converte imagens PNG para JPG com otimização de qualidade.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>PNG/JPG → WebP</h4>
                        <p>Converte imagens para formato WebP moderno e comprimido.</p>
                    </div>
                </div>

                <div class="conversion-category" data-icon="📄">
                    <h3>Documentos</h3>
                    <div class="conversion-item">
                        <h4>DOCX → PDF</h4>
                        <p>Converte documentos Word para formato PDF.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>PDF → DOCX</h4>
                        <p>Converte arquivos PDF para documentos Word editáveis.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>DOCX → TXT</h4>
                        <p>Extrai texto puro de documentos Word.</p>
                    </div>
                </div>

                <div class="conversion-category" data-icon="📊">
                    <h3>Planilhas</h3>
                    <div class="conversion-item">
                        <h4>XLSX → CSV</h4>
                        <p>Converte planilhas Excel para formato CSV.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>CSV → XLSX</h4>
                        <p>Converte arquivos CSV para planilhas Excel.</p>
                    </div>
                </div>

                <div class="conversion-category" data-icon="📝">
                    <h3>Texto</h3>
                    <div class="conversion-item">
                        <h4>TXT → PDF</h4>
                        <p>Converte arquivos de texto para formato PDF.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>&copy; 2026 Escritório Andrade Maia - Conversor de Arquivos AM v2.0.0</p>
        </div>
    </div>

    <script>
        // Elementos DOM
        const uploadForm = document.getElementById('uploadForm');
        const fileInput = document.getElementById('file');
        const fileName = document.getElementById('fileName');
        const convertBtn = document.getElementById('convertBtn');
        const progressSection = document.getElementById('progressSection');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const statusText = document.getElementById('statusText');
        const downloadSection = document.getElementById('downloadSection');
        const downloadBtn = document.getElementById('downloadBtn');
        const resultTitle = document.getElementById('resultTitle');
        const resultMessage = document.getElementById('resultMessage');

        // Estados de progresso
        const progressSteps = [
            { percent: 10, text: 'Validando arquivo...' },
            { percent: 25, text: 'Preparando conversão...' },
            { percent: 50, text: 'Convertendo arquivo...' },
            { percent: 75, text: 'Finalizando...' },
            { percent: 90, text: 'Salvando arquivo...' },
            { percent: 100, text: 'Conversão concluída!' }
        ];

        // Mostrar nome do arquivo selecionado
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                fileName.textContent = `📄 ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
            } else {
                fileName.textContent = '';
            }
        });

        // Manipular envio do formulário
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            if (!formData.get('file') || !formData.get('target_format')) {
                alert('Por favor, selecione um arquivo e formato de destino.');
                return;
            }

            // Mostrar seção de progresso
            progressSection.style.display = 'block';
            downloadSection.style.display = 'none';
            convertBtn.disabled = true;
            convertBtn.textContent = '🔄 Convertendo...';

            // Simular progresso
            await simulateProgress();

            try {
                // Enviar arquivo
                const response = await fetch('/convert', {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    // Sucesso - converter dados hex para blob
                    const byteArray = new Uint8Array(result.data.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
                    const blob = new Blob([byteArray]);
                    const url = window.URL.createObjectURL(blob);

                    // Mostrar seção de download
                    downloadSection.className = 'download-section success';
                    resultTitle.textContent = '✅ Conversão Concluída!';
                    resultMessage.textContent = 'Seu arquivo foi convertido com sucesso.';
                    downloadBtn.href = url;
                    downloadBtn.download = result.filename;
                    downloadBtn.textContent = `📥 Baixar ${result.filename}`;

                } else {
                    // Erro
                    showError(result.error || 'Erro desconhecido na conversão');
                }

            } catch (error) {
                showError('Erro de conexão: ' + error.message);
            }

            // Resetar interface
            progressSection.style.display = 'none';
            downloadSection.style.display = 'block';
            convertBtn.disabled = false;
            convertBtn.textContent = '🚀 Converter Arquivo';
        });

        // Simular progresso da conversão
        async function simulateProgress() {
            for (let i = 0; i < progressSteps.length; i++) {
                const step = progressSteps[i];
                progressBar.style.width = step.percent + '%';
                progressText.textContent = step.percent + '%';
                statusText.textContent = step.text;

                // Delay entre etapas (mais realista)
                const delay = i === 0 ? 500 : i === progressSteps.length - 1 ? 1000 : 1500;
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }

        // Mostrar erro
        function showError(message) {
            downloadSection.className = 'download-section error';
            resultTitle.textContent = '❌ Erro na Conversão';
            resultMessage.textContent = message;
            downloadSection.style.display = 'block';
        }

        // Animação de entrada
        document.addEventListener('DOMContentLoaded', function() {
            const container = document.querySelector('.container');
            container.style.opacity = '0';
            container.style.transform = 'translateY(20px)';

            setTimeout(() => {
                container.style.transition = 'all 0.6s ease';
                container.style.opacity = '1';
                container.style.transform = 'translateY(0)';
            }, 100);
        });
    </script>
</body>
</html>
"""

# ========== ROTAS ==========

@app.route("/")
def home():
    """Página inicial com formulário de upload."""
    return render_template_string(HOME_HTML)

@app.route("/convert", methods=["POST"])
def convert():
    """Processa a conversão do arquivo."""
    file = request.files.get("file")
    target_format = request.form.get("target_format")

    # Verificar se é uma requisição AJAX
    is_ajax = request.headers.get('Content-Type', '').startswith('multipart/form-data') and request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not file or file.filename == "":
        if is_ajax:
            return {"success": False, "error": "Selecione um arquivo para converter."}, 400
        flash("Selecione um arquivo para converter.")
        return redirect(url_for("home"))

    if not target_format:
        if is_ajax:
            return {"success": False, "error": "Selecione o formato de destino."}, 400
        flash("Selecione o formato de destino.")
        return redirect(url_for("home"))

    try:
        # Validar tipo do arquivo
        file_type, ext = validate_file_type(file.filename)

        # Salvar upload temporariamente
        input_path = save_upload_to_temp(file, per_file_limit_bytes=config.PER_FILE_LIMIT)

        try:
            # Obter conversor apropriado
            converter = get_converter(file_type, target_format, input_path)

            if not converter:
                error_msg = f"Conversão {file_type} → {target_format} não suportada."
                if is_ajax:
                    return {"success": False, "error": error_msg}, 400
                flash(error_msg)
                return redirect(url_for("home"))

            # Realizar conversão
            with converter:
                converted_data = converter.convert()

            # Salvar cópia para auditoria
            output_filename = converter._get_output_filename(sanitize_filename(file.filename))
            save_converted_copy(output_filename, converted_data)

            if is_ajax:
                # Retornar dados para download via JavaScript
                return {
                    "success": True,
                    "filename": output_filename,
                    "data": converted_data.hex()  # Converter bytes para string hex para transmissão
                }
            else:
                # Retornar arquivo diretamente para download
                return send_file(
                    io.BytesIO(converted_data),
                    mimetype=f"application/octet-stream",
                    as_attachment=True,
                    download_name=output_filename
                )

        finally:
            # Limpar arquivo temporário de entrada
            try:
                os.remove(input_path)
            except:
                pass

    except ValueError as e:
        if is_ajax:
            return {"success": False, "error": str(e)}, 400
        flash(str(e))
        return redirect(url_for("home"))
    except Exception as e:
        error_msg = f"Erro durante a conversão: {str(e)}"
        if is_ajax:
            return {"success": False, "error": error_msg}, 500
        flash(error_msg)
        return redirect(url_for("home"))

@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(error):
    """Tratamento de arquivos muito grandes."""
    flash(f"Arquivo muito grande. Limite: {PER_FILE_LIMIT_MB} MB.")
    return redirect(url_for("home"))