"""
Rotas Flask para o Conversor de Arquivos AM.
Estrutura modular similar ao I'AM.pdf.
"""

import os
from flask import request, send_file, render_template_string, redirect, url_for, flash
from werkzeug.exceptions import RequestEntityTooLarge

from main import (
    app,
    get_converter,
    save_converted_file_copy,
    save_upload_to_destination,
    save_upload_to_temp,
    validate_file_type,
    sanitize_filename,
    PER_FILE_LIMIT_MB,
)
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
            padding: 20px;
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
            font-size: 2em;
            font-weight: 700;
            margin-bottom: 5px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }
        .header p {
            font-size: 0.95em;
            opacity: 0.9;
            position: relative;
            z-index: 1;
            margin: 3px 0;
        }
        .main-content {
            padding: 25px;
        }
        .upload-section {
            background: #2a2a2a;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
            border: 1px solid #ff6b35;
        }
        .upload-section h2 {
            color: #ff6b35;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .form-group {
            margin-bottom: 12px;
        }
        .form-group label {
            display: block;
            margin-bottom: 6px;
            font-weight: 600;
            color: #ffffff;
            font-size: 0.9em;
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
            padding: 12px 15px;
            background: #3a3a3a;
            border: 2px dashed #ff6b35;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: #cccccc;
            font-size: 0.9em;
        }
        .file-input-label:hover {
            background: #4a4a4a;
            border-color: #ff8c42;
        }
        .file-name {
            margin-top: 8px;
            color: #ff6b35;
            font-weight: 500;
            font-size: 0.85em;
        }
        select, button {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
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
            margin-top: 15px;
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
        .checkbox-label {
            display: flex;
            align-items: center;
            cursor: pointer;
            font-size: 0.9em;
            color: #ffffff;
            margin-bottom: 10px;
        }
        .checkbox-label input[type="checkbox"] {
            margin-right: 10px;
            width: 18px;
            height: 18px;
            accent-color: #ff6b35;
        }
        .queue-info {
            font-size: 0.85em;
            color: #888;
            margin-top: 5px;
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
            margin-top: 30px;
        }
        .conversions h2 {
            color: #ff6b35;
            margin-bottom: 20px;
            text-align: center;
            font-size: 1.4em;
        }
        .conversions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
        }
        .conversion-category {
            background: #2a2a2a;
            border-radius: 12px;
            padding: 18px;
            border: 1px solid #ff6b35;
            transition: all 0.3s ease;
        }
        .conversion-category:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(255, 107, 53, 0.2);
        }
        .conversion-category h3 {
            color: #ff6b35;
            margin-bottom: 12px;
            font-size: 1.1em;
            display: flex;
            align-items: center;
        }
        .conversion-category h3::before {
            content: attr(data-icon);
            margin-right: 8px;
            font-size: 1.3em;
        }
        .conversion-item {
            background: #3a3a3a;
            padding: 10px;
            margin: 6px 0;
            border-radius: 6px;
            border-left: 3px solid #ff6b35;
            transition: all 0.2s ease;
            font-size: 0.85em;
        }
        .conversion-item:hover {
            background: #4a4a4a;
            transform: translateX(3px);
        }
        .conversion-item h4 {
            margin: 0 0 4px 0;
            color: #ffffff;
            font-size: 0.95em;
        }
        .conversion-item p {
            margin: 0;
            color: #cccccc;
            font-size: 0.8em;
        }
        .footer {
            text-align: center;
            padding: 20px;
            background: #1a1a1a;
            border-top: 1px solid #444;
            color: #888;
            font-size: 0.9em;
        }
        @media (max-width: 1024px) {
            .conversions-grid {
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            }
        }
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 8px;
            }
            .header {
                padding: 15px;
            }
            .header h1 {
                font-size: 1.5em;
            }
            .header p {
                font-size: 0.85em;
            }
            .main-content {
                padding: 15px;
            }
            .upload-section {
                padding: 15px;
            }
            .upload-section h2 {
                font-size: 1.1em;
            }
            .conversions h2 {
                font-size: 1.2em;
            }
            .conversions-grid {
                grid-template-columns: 1fr;
                gap: 12px;
            }
            .conversion-category {
                padding: 15px;
            }
            .conversion-category h3 {
                font-size: 1em;
            }
            select, button {
                padding: 10px;
                font-size: 13px;
            }
        }
        @media (max-width: 480px) {
            .container {
                margin: 5px;
            }
            .header {
                padding: 12px;
            }
            .header h1 {
                font-size: 1.3em;
            }
            .header p {
                font-size: 0.75em;
                margin: 2px 0;
            }
            .main-content {
                padding: 10px;
            }
            .upload-section {
                padding: 12px;
                margin-bottom: 15px;
            }
            .upload-section h2 {
                font-size: 1em;
                margin-bottom: 10px;
            }
            .conversions-grid {
                gap: 10px;
            }
            .conversion-category {
                padding: 12px;
            }
            .conversion-item {
                padding: 8px;
                margin: 4px 0;
            }
            .conversion-item h4 {
                font-size: 0.9em;
            }
            .conversion-item p {
                font-size: 0.75em;
            }
            button {
                padding: 10px;
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Conversor de Arquivos AM</h1>
            <p>Ferramenta profissional de conversÃ£o de arquivos</p>
            <p style="margin-top: 15px; font-size: 1.2em; font-weight: 600; letter-spacing: 1px;">âœ… Tudo local, tudo seguro.</p>
        </div>

        <div class="main-content">
            <div class="upload-section">
                <h2>ðŸ“¤ Fazer Upload e Converter</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="file">Selecione o arquivo:</label>
                        <div class="file-input-container">
                            <input type="file" id="file" name="file" class="file-input" required>
                            <label for="file" class="file-input-label">
                                <i>ðŸ“Ž</i> Clique para selecionar arquivo
                            </label>
                        </div>
                        <div id="fileName" class="file-name"></div>
                    </div>
                    <div class="form-group">
                        <label for="targetFormat">Formato de destino:</label>
                        <select id="targetFormat" name="target_format" required>
                            <option value="">Selecione...</option>
                            <optgroup label="ðŸŽµ Ãudio (20+ formatos)">
                                <option value="mp3">MP3 - MPEG Audio</option>
                                <option value="wav">WAV - Waveform Audio</option>
                                <option value="flac">FLAC - Free Lossless Audio</option>
                                <option value="aac">AAC - Advanced Audio Coding</option>
                                <option value="m4a">M4A - MPEG-4 Audio</option>
                                <option value="ogg">OGG - Ogg Vorbis</option>
                                <option value="opus">OPUS - Opus Audio</option>
                                <option value="aiff">AIFF - Audio Interchange</option>
                                <option value="weba">WebA - Web Audio</option>
                                <option value="ac3">AC3 - Dolby Digital</option>
                                <option value="dts">DTS - Digital Theater</option>
                                <option value="eac3">EAC3 - Enhanced AC-3</option>
                                <option value="wma">WMA - Windows Media Audio</option>
                            </optgroup>
                            <optgroup label="ðŸŽ¬ VÃ­deo (20+ formatos)">
                                <option value="mp4">MP4 - MPEG-4 Video</option>
                                <option value="avi">AVI - Audio Video Interleave</option>
                                <option value="mkv">MKV - Matroska Video</option>
                                <option value="mov">MOV - QuickTime Movie</option>
                                <option value="flv">FLV - Flash Video</option>
                                <option value="webm">WebM - Web Media</option>
                                <option value="3gp">3GP - 3rd Generation Partnership</option>
                                <option value="wmv">WMV - Windows Media Video</option>
                                <option value="asf">ASF - Advanced Systems Format</option>
                                <option value="mod">MOD - Camcorder Format</option>
                                <option value="mts">MTS - AVCHD Format</option>
                                <option value="ts">TS - Transport Stream</option>
                                <option value="vob">VOB - DVD Video Object</option>
                                <option value="m2ts">M2TS - Blu-ray Format</option>
                                <option value="ogv">OGV - Ogg Video</option>
                                <option value="m4v">M4V - MPEG-4 Video</option>
                                <option value="f4v">F4V - Flash Video</option>
                            </optgroup>
                            <optgroup label="ðŸ–¼ï¸ Imagem (20+ formatos)">
                                <option value="jpg">JPG - Joint Photographic</option>
                                <option value="jpeg">JPEG - JPEG Image</option>
                                <option value="png">PNG - Portable Network</option>
                                <option value="bmp">BMP - Bitmap Image</option>
                                <option value="gif">GIF - Graphics Interchange</option>
                                <option value="tiff">TIFF - Tagged Image Format</option>
                                <option value="ico">ICO - Icon Image</option>
                                <option value="webp">WebP - Web Picture Format</option>
                                <option value="tga">TGA - Truevision Graphics</option>
                                <option value="pnm">PNM - Portable Anymap</option>
                                <option value="ppm">PPM - Portable Pixmap</option>
                                <option value="xbm">XBM - X Bitmap</option>
                                <option value="xpm">XPM - X Pixmap</option>
                                <option value="svg">SVG - Scalable Vector</option>
                                <option value="cur">CUR - Cursor Image</option>
                                <option value="heic">HEIC - High Efficiency</option>
                                <option value="heif">HEIF - High Efficiency Image</option>
                                <option value="jfif">JFIF - JPEG File</option>
                                <option value="jp2">JP2 - JPEG 2000</option>
                                <option value="jp2k">JP2K - JPEG 2000</option>
                            </optgroup>
                            <optgroup label="ðŸ“„ Documentos">
                                <option value="pdf">PDF - Portable Document</option>
                                <option value="docx">DOCX - Word Document</option>
                                <option value="doc">DOC - Word 97-2003</option>
                                <option value="txt">TXT - Plain Text</option>
                                <option value="odt">ODT - OpenDocument Text</option>
                                <option value="rtf">RTF - Rich Text Format</option>
                            </optgroup>
                            <optgroup label="ðŸ“Š Planilhas">
                                <option value="csv">CSV - Comma Separated</option>
                                <option value="xlsx">XLSX - Excel Spreadsheet</option>
                                <option value="xls">XLS - Excel 97-2003</option>
                                <option value="ods">ODS - OpenDocument Sheet</option>
                                <option value="tsv">TSV - Tab Separated</option>
                            </optgroup>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="useQueue" name="use_queue" value="true">
                            <span class="checkmark"></span>
                            Usar fila de conversÃ£o (recomendado para arquivos grandes)
                        </label>
                        <div class="queue-info" style="font-size: 0.85em; color: #888; margin-top: 5px;">
                            ðŸ“‹ Processamento em fila evita timeouts e permite mÃºltiplas conversÃµes simultÃ¢neas
                        </div>
                    </div>
                    <button type="submit" id="convertBtn">
                        ðŸš€ Converter Arquivo
                    </button>
                </form>
            </div>

            <div class="progress-section" id="progressSection">
                <h3>ðŸ”„ Convertendo Arquivo...</h3>
                <div class="progress-container">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                <div class="progress-text" id="progressText">0%</div>
                <div class="status-text" id="statusText">Iniciando conversÃ£o...</div>
            </div>

            <div class="download-section" id="downloadSection">
                <h3 id="resultTitle">âœ… ConversÃ£o ConcluÃ­da!</h3>
                <p id="resultMessage">Seu arquivo foi convertido com sucesso.</p>
                <a href="#" id="downloadBtn" class="download-btn">
                    <i>ðŸ“¥</i> Baixar Arquivo Convertido
                </a>
            </div>

            <div class="conversions">
                <h2>ðŸ”§ ConversÃµes DisponÃ­veis</h2>

                <div class="conversions-grid">
                <div class="conversion-category" data-icon="ðŸŽµ">
                    <h3>Ãudio (20+)</h3>
                    <div class="conversion-item">
                        <h4>MP3 â†” WAV</h4>
                        <p>Converte entre MP3, WAV, FLAC, AAC, OGG, OPUS e muito mais.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>Formatos Suportados</h4>
                        <p>MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, AIFF, AC3, DTS, e mais...</p>
                    </div>
                </div>

                <div class="conversion-category" data-icon="ðŸŽ¬">
                    <h3>VÃ­deo (20+)</h3>
                    <div class="conversion-item">
                        <h4>MP4 â†” AVI/MKV</h4>
                        <p>Converte entre MP4, AVI, MKV, MOV, FLV, WebM e muitos mais.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>Formatos Suportados</h4>
                        <p>MP4, AVI, MKV, MOV, FLV, WebM, 3GP, WMV, VOB, TS e mais...</p>
                    </div>
                </div>

                <div class="conversion-category" data-icon="ðŸ–¼ï¸">
                    <h3>Imagem (20+)</h3>
                    <div class="conversion-item">
                        <h4>PNG â†” JPG/WebP</h4>
                        <p>Converte entre PNG, JPG, GIF, BMP, TIFF, HEIC e muito mais.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>Formatos Suportados</h4>
                        <p>PNG, JPG, BMP, GIF, TIFF, WEBP, ICO, SVG, TGA, HEIF e mais...</p>
                    </div>
                </div>

                <div class="conversion-category" data-icon="ðŸ“„">
                    <h3>Documentos</h3>
                    <div class="conversion-item">
                        <h4>DOCX â†” PDF/TXT</h4>
                        <p>Converte entre DOCX, PDF, TXT, ODT, RTF e Word 97-2003.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>Formatos Suportados</h4>
                        <p>PDF, DOCX, DOC, TXT, ODT, RTF - CompatÃ­vel com office.</p>
                    </div>
                </div>

                <div class="conversion-category" data-icon="ðŸ“Š">
                    <h3>Planilhas</h3>
                    <div class="conversion-item">
                        <h4>XLSX â†” CSV/ODS</h4>
                        <p>Converte entre XLSX, CSV, XLS, ODS, TSV e formatos legacy.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>Formatos Suportados</h4>
                        <p>XLSX, XLS, CSV, ODS, TSV - CompatÃ­vel com Excel/Calc.</p>
                    </div>
                </div>

                <div class="conversion-category" data-icon="âœ¨">
                    <h3>Recursos</h3>
                    <div class="conversion-item">
                        <h4>âœ… 100+ Formatos</h4>
                        <p>Suporte a mais de 100 formatos diferentes de arquivo.</p>
                    </div>
                    <div class="conversion-item">
                        <h4>âš¡ ConversÃ£o RÃ¡pida</h4>
                        <p>Processamento rÃ¡pido e sem perda de qualidade garantida.</p>
                    </div>
                </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>&copy; 2026 EscritÃ³rio Andrade Maia - Conversor de Arquivos AM v2.0.2 - 100+ Formatos</p>
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
        let queueStatusPoll = null;
        let queueDownloadBtn = null;
        let queueSocket = null;

        // Estados de progresso
        const progressSteps = [
            { percent: 10, text: 'Validando arquivo...' },
            { percent: 25, text: 'Preparando conversÃ£o...' },
            { percent: 50, text: 'Convertendo arquivo...' },
            { percent: 75, text: 'Finalizando...' },
            { percent: 90, text: 'Salvando arquivo...' },
            { percent: 100, text: 'ConversÃ£o concluÃ­da!' }
        ];

        // Mostrar nome do arquivo selecionado
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                fileName.textContent = `ðŸ“„ ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
            } else {
                fileName.textContent = '';
            }
        });

        // Manipular envio do formulÃ¡rio
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            if (!formData.get('file') || !formData.get('target_format')) {
                alert('Por favor, selecione um arquivo e formato de destino.');
                return;
            }

            // Mostrar seÃ§Ã£o de progresso
            if (queueStatusPoll) {
                clearInterval(queueStatusPoll);
                queueStatusPoll = null;
            }
            if (queueSocket) {
                queueSocket.close();
                queueSocket = null;
            }
            if (queueDownloadBtn) {
                queueDownloadBtn.remove();
                queueDownloadBtn = null;
            }
            progressSection.style.display = 'block';
            downloadSection.style.display = 'none';
            convertBtn.disabled = true;
            convertBtn.textContent = 'ðŸ”„ Convertendo...';

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
                    // Verificar se Ã© resposta de fila ou conversÃ£o imediata
                    if (result.task_id && result.status === 'queued') {
                        // ========== RESPOSTA DA FILA ==========
                        showQueueResponse(result);
                    } else if (result.download_url && result.filename) {
                        // ========== RESPOSTA IMEDIATA (LEGACY) ==========
                        // Mostrar seÃ§Ã£o de download
                        downloadSection.className = 'download-section success';
                        resultTitle.textContent = 'âœ… ConversÃ£o ConcluÃ­da!';
                        resultMessage.textContent = 'Seu arquivo foi convertido com sucesso.';
                        downloadBtn.href = result.download_url;
                        downloadBtn.target = '_blank';
                        downloadBtn.download = result.filename;
                        downloadBtn.textContent = `ðŸ“¥ Baixar ${result.filename}`;
                    } else {
                        showError('Resposta invÃ¡lida do servidor');
                    }

                } else {
                    // Erro
                    showError(result.error || 'Erro desconhecido na conversÃ£o');
                }

            } catch (error) {
                showError('Erro de conexÃ£o: ' + error.message);
            }

            // Resetar interface
            progressSection.style.display = 'none';
            downloadSection.style.display = 'block';
            convertBtn.disabled = false;
            convertBtn.textContent = 'ðŸš€ Converter Arquivo';
        });

        // Simular progresso da conversÃ£o
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

        function renderQueueStatus(taskId, data, fallbackFile) {
            const statusLabel = data.status || 'queued';
            const progressValue = Number.isFinite(data.progress) ? data.progress : 0;
            const etaLabel = data.eta_seconds ? `${data.eta_seconds}s` : 'calculando';
            const resultFilename = data.result_filename || 'aguardando processamento';

            resultMessage.innerHTML = `
                <div style="text-align: left; margin-bottom: 15px;">
                    <strong>Task ID:</strong> ${taskId}<br>
                    <strong>Arquivo:</strong> ${fallbackFile || data.filename || '-'}<br>
                    <strong>Status:</strong> ${statusLabel}<br>
                    <strong>Progresso:</strong> ${progressValue}%<br>
                    <strong>ETA:</strong> ${etaLabel}<br>
                    <strong>Resultado:</strong> ${resultFilename}
                </div>
            `;
        }

        async function pollQueueStatus(taskId, filename) {
            try {
                const response = await fetch(`/api/queue/status/${taskId}`);
                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.error || 'NÃ£o foi possÃ­vel consultar a fila.');
                }

                renderQueueStatus(taskId, data, filename);

                if (data.status === 'completed') {
                    clearInterval(queueStatusPoll);
                    queueStatusPoll = null;
                    if (queueSocket) {
                        queueSocket.close();
                        queueSocket = null;
                    }
                    downloadSection.className = 'download-section success';
                    resultTitle.textContent = 'âœ… ConversÃ£o ConcluÃ­da!';
                    downloadBtn.href = `/download/${taskId}`;
                    downloadBtn.target = '_blank';
                    downloadBtn.textContent = `ðŸ“¥ Baixar ${data.result_filename || filename}`;

                    if (queueDownloadBtn) {
                        queueDownloadBtn.remove();
                        queueDownloadBtn = null;
                    }
                    return;
                }

                if (data.status === 'error') {
                    clearInterval(queueStatusPoll);
                    queueStatusPoll = null;
                    if (queueSocket) {
                        queueSocket.close();
                        queueSocket = null;
                    }
                    showError(data.error || 'A conversÃ£o falhou.');
                }
            } catch (error) {
                clearInterval(queueStatusPoll);
                queueStatusPoll = null;
                showError('Erro ao acompanhar fila: ' + error.message);
            }
        }

        function startQueuePolling(taskId, filename) {
            if (queueStatusPoll) {
                clearInterval(queueStatusPoll);
            }
            pollQueueStatus(taskId, filename);
            queueStatusPoll = setInterval(() => pollQueueStatus(taskId, filename), 2000);
        }

        function connectQueueWebSocket(taskId, filename) {
            if (!window.WebSocket) {
                startQueuePolling(taskId, filename);
                return;
            }

            const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
            const socketUrl = `${protocol}://${window.location.host}/ws/queue/${taskId}`;
            let hasReceivedMessage = false;

            queueSocket = new WebSocket(socketUrl);

            queueSocket.onopen = () => {
                pollQueueStatus(taskId, filename);
            };

            queueSocket.onmessage = (event) => {
                hasReceivedMessage = true;
                try {
                    const message = JSON.parse(event.data);
                    if (message.type === 'progress' || message.type === 'completion' || message.type === 'status') {
                        pollQueueStatus(taskId, filename);
                    }
                } catch (error) {
                    startQueuePolling(taskId, filename);
                }
            };

            queueSocket.onerror = () => {
                if (!hasReceivedMessage) {
                    startQueuePolling(taskId, filename);
                }
            };

            queueSocket.onclose = () => {
                queueSocket = null;
                if (!hasReceivedMessage) {
                    startQueuePolling(taskId, filename);
                }
            };
        }

        // Mostrar resposta da fila
        function showQueueResponse(result) {
            downloadSection.className = 'download-section success';
            resultTitle.textContent = 'ðŸ“‹ Arquivo na Fila!';
            renderQueueStatus(result.task_id, {
                status: result.status,
                progress: 0,
                eta_seconds: null,
                filename: result.filename,
                result_filename: null
            }, result.filename);

            downloadBtn.href = `/api/queue/status/${result.task_id}`;
            downloadBtn.target = '_blank';
            downloadBtn.textContent = `ðŸ“Š Ver status bruto`;
            downloadBtn.style.background = '#4CAF50';

            queueDownloadBtn = document.createElement('a');
            queueDownloadBtn.href = '#';
            queueDownloadBtn.className = 'download-btn';
            queueDownloadBtn.textContent = 'â³ Aguardando conclusÃ£o';
            queueDownloadBtn.style.background = '#666';
            queueDownloadBtn.style.marginTop = '10px';
            queueDownloadBtn.onclick = function(e) {
                e.preventDefault();
            };

            downloadBtn.parentNode.insertBefore(queueDownloadBtn, downloadBtn.nextSibling);
            connectQueueWebSocket(result.task_id, result.filename);
            return;
        }

        // Mostrar erro
        function showError(message) {
            if (queueStatusPoll) {
                clearInterval(queueStatusPoll);
                queueStatusPoll = null;
            }
            if (queueSocket) {
                queueSocket.close();
                queueSocket = null;
            }
            downloadSection.className = 'download-section error';
            resultTitle.textContent = 'âŒ Erro na ConversÃ£o';
            resultMessage.textContent = message;
            downloadSection.style.display = 'block';
        }

        // AnimaÃ§Ã£o de entrada
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
    """PÃ¡gina inicial com formulÃ¡rio de upload."""
    return render_template_string(HOME_HTML)

@app.route("/convert", methods=["POST"])
def convert():
    """Processa a conversÃ£o do arquivo."""
    file = request.files.get("file")
    target_format = request.form.get("target_format")
    use_queue = request.form.get("use_queue", "false").lower() == "true"

    # Verificar se Ã© uma requisiÃ§Ã£o AJAX
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

    # ========== NOVO: SUPORTE Ã€ FILA v2.2.0 ==========
    if use_queue:
        return _convert_with_queue(file, target_format, is_ajax)

    # ========== LEGACY: CONVERSÃƒO IMEDIATA ==========
    return _convert_immediate(file, target_format, is_ajax)


def _convert_immediate(file, target_format: str, is_ajax: bool):
    """ConversÃ£o imediata (modo legacy)."""
    try:
        # Validar tipo do arquivo
        file_type, ext = validate_file_type(file.filename)

        # Salvar upload temporariamente
        input_path = save_upload_to_temp(file, per_file_limit_bytes=config.PER_FILE_LIMIT)

        try:
            # Obter conversor apropriado
            converter = get_converter(file_type, target_format, input_path)

            if not converter:
                error_msg = f"ConversÃ£o {file_type} â†’ {target_format} nÃ£o suportada."
                if is_ajax:
                    return {"success": False, "error": error_msg}, 400
                flash(error_msg)
                return redirect(url_for("home"))

            # Realizar conversÃ£o
            with converter:
                converted_path = converter.convert()
                converter.temp_files = []

            # Salvar cÃ³pia para auditoria
            output_filename = converter.get_output_filename(sanitize_filename(file.filename))
            export_path = save_converted_file_copy(output_filename, converted_path)
            if not export_path:
                raise RuntimeError("Falha ao persistir arquivo convertido")
            try:
                os.remove(converted_path)
            except OSError:
                pass

            if is_ajax:
                # Retornar URL de download para evitar payload binÃ¡rio em JSON
                return {
                    "success": True,
                    "filename": os.path.basename(export_path),
                    "download_url": url_for("download_exported_file", filename=os.path.basename(export_path))
                }
            else:
                # Retornar arquivo diretamente para download
                return send_file(
                    export_path,
                    mimetype=f"application/octet-stream",
                    as_attachment=True,
                    download_name=os.path.basename(export_path)
                )

        finally:
            # Limpar arquivo temporÃ¡rio de entrada
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
        error_msg = f"Erro durante a conversÃ£o: {str(e)}"
        if is_ajax:
            return {"success": False, "error": error_msg}, 500
        flash(error_msg)
        return redirect(url_for("home"))


def _convert_with_queue(file, target_format: str, is_ajax: bool):
    """ConversÃ£o via fila (modo novo v2.2.0)."""
    try:
        # Importar gerenciadores de fila
        from main import queue_manager

        # Salvar arquivo permanentemente na pasta uploads
        filename = sanitize_filename(file.filename)
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        save_upload_to_destination(file, file_path, per_file_limit_bytes=config.PER_FILE_LIMIT)

        # Obter tamanho em MB
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        # Obter IP do usuÃ¡rio
        user_ip = request.remote_addr

        # Adicionar Ã  fila
        task_id = queue_manager.add_task(
            filename=filename,
            target_format=target_format,
            user_ip=user_ip,
            file_size_mb=file_size_mb
        )

        # Obter posiÃ§Ã£o na fila
        stats = queue_manager.get_queue_stats()
        queue_position = stats['queued']

        # Resposta de sucesso
        response_data = {
            "success": True,
            "task_id": task_id,
            "status": "queued",
            "filename": filename,
            "queue_position": queue_position,
            "file_size_mb": round(file_size_mb, 2),
            "message": f"Arquivo adicionado Ã  fila. PosiÃ§Ã£o: {queue_position}"
        }

        if is_ajax:
            return response_data, 201
        else:
            flash(response_data["message"])
            return redirect(url_for("home"))

    except Exception as e:
        error_msg = f"Erro ao adicionar Ã  fila: {str(e)}"
        if is_ajax:
            return {"success": False, "error": error_msg}, 500
        flash(error_msg)
        return redirect(url_for("home"))

@app.route("/download/<task_id>", methods=["GET"])
def download_converted(task_id):
    """Download de arquivo convertido via fila."""
    try:
        from main import queue_manager

        # Obter status da tarefa
        task = queue_manager.get_status(task_id)
        if not task:
            flash("Tarefa nÃ£o encontrada.")
            return redirect(url_for("home"))

        if task['status'] != 'completed':
            flash(f"Tarefa ainda nÃ£o concluÃ­da. Status: {task['status']}")
            return redirect(url_for("home"))

        filename = task['filename_result']
        if not filename:
            flash("Arquivo convertido nÃ£o encontrado.")
            return redirect(url_for("home"))

        # Procurar arquivo nos exports
        full_path = os.path.join(config.EXPORTS_DIR, filename)
        if os.path.exists(full_path):
            return send_file(
                full_path,
                mimetype="application/octet-stream",
                as_attachment=True,
                download_name=filename
            )
        exports_dir = config.EXPORTS_DIR
        for file_path in os.listdir(exports_dir):
            if filename in file_path:
                full_path = os.path.join(exports_dir, file_path)
                return send_file(
                    full_path,
                    mimetype="application/octet-stream",
                    as_attachment=True,
                    download_name=filename
                )

        flash("Arquivo convertido nÃ£o encontrado no servidor.")
        return redirect(url_for("home"))

    except Exception as e:
        flash(f"Erro ao fazer download: {str(e)}")
        return redirect(url_for("home"))


@app.route("/download/export/<filename>", methods=["GET"])
def download_exported_file(filename):
    """Download de arquivo convertido no modo imediato."""
    safe_name = sanitize_filename(filename)
    full_path = os.path.join(config.EXPORTS_DIR, safe_name)

    if not os.path.exists(full_path):
        flash("Arquivo convertido nÃ£o encontrado.")
        return redirect(url_for("home"))

    return send_file(
        full_path,
        mimetype="application/octet-stream",
        as_attachment=True,
        download_name=safe_name
    )

