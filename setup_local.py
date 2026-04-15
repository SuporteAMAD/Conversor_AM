#!/usr/bin/env python3
"""
Setup e preparação do servidor local para Conversor de Arquivos AM v2.0.0
Detecta e instala dependências necessárias
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(msg):
    """Imprimir header com cores"""
    print(f"\n{'='*60}")
    print(f"🔧 {msg}")
    print(f"{'='*60}\n")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_info(msg):
    print(f"ℹ️  {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def check_python():
    """Verificar versão do Python"""
    print_header("Verificando Python")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.8+ necessário (você tem {version.major}.{version.minor})")
        return False

def check_ffmpeg():
    """Verificar se FFmpeg está instalado"""
    print_header("Verificando FFmpeg")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.decode().split('\n')[0]
            print_success(f"FFmpeg encontrado: {version_line}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print_error("FFmpeg NÃO encontrado!")
    print_ffmpeg_install_guide()
    return False

def print_ffmpeg_install_guide():
    """Exibir guia de instalação do FFmpeg"""
    print("\n📥 OPÇÕES DE INSTALAÇÃO:\n")
    
    print("1️⃣  FÁCIL - Instalar com Chocolatey (Windows):")
    print("   $ choco install ffmpeg")
    print("   Depois reinicie o PowerShell\n")
    
    print("2️⃣  MANUAL - Download direto:")
    print("   1. Ir para: https://ffmpeg.org/download.html")
    print("   2. Baixar 'Windows builds by BtbN'")
    print("   3. Extrair a pasta")
    print("   4. Adicionar ao PATH do Windows\n")
    
    print("3️⃣  VERIFICAÇÃO:")
    print("   Após instalação, execute:")
    print("   $ ffmpeg -version\n")

def check_pip_packages():
    """Verificar pacotes Python instalados"""
    print_header("Verificando Pacotes Python")
    
    required_packages = {
        'flask': 'Flask',
        'werkzeug': 'Werkzeug',
        'pillow': 'Pillow (imagens)',
        'reportlab': 'ReportLab (PDF)',
        'pdf2docx': 'pdf2docx (PDF→DOCX)',
        'docx': 'python-docx',
        'pandas': 'Pandas',
        'openpyxl': 'openpyxl (Excel)',
    }
    
    missing = []
    
    for package_import, package_name in required_packages.items():
        try:
            __import__(package_import)
            print_success(f"{package_name}")
        except ImportError:
            print_error(f"{package_name} FALTANDO")
            missing.append(package_import)
    
    if missing:
        print(f"\n❌ {len(missing)} pacote(s) faltando.\n")
        print("Instale com:")
        print(f"   pip install {' '.join(missing)}\n")
        return False
    
    return True

def check_directory_structure():
    """Verificar estrutura de diretórios"""
    print_header("Verificando Estrutura de Diretórios")
    
    required_dirs = ['uploads', 'exports', 'logs', 'rotas']
    base_dir = Path.cwd()
    
    all_ok = True
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print_success(f"{dir_name}/ existe")
        else:
            print_warning(f"{dir_name}/ CRIANDO")
            dir_path.mkdir(exist_ok=True, parents=True)
            all_ok = False
    
    # Verificar arquivos principais
    required_files = ['main.py', 'requirements.txt', 'config.py']
    for file_name in required_files:
        file_path = base_dir / file_name
        if file_path.exists():
            print_success(f"{file_name} encontrado")
        else:
            print_error(f"{file_name} NÃO ENCONTRADO")
            all_ok = False
    
    return all_ok

def test_application():
    """Testar aplicação localmente"""
    print_header("Testando Aplicação")
    
    try:
        from main import app
        print_success("main.py importado com sucesso")
        
        # Testar rota
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print_success("Página inicial respondendo (HTTP 200)")
            else:
                print_error(f"Página inicial erro: HTTP {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print_error(f"Erro ao testar: {e}")
        return False

def print_final_status(checks):
    """Exibir status final"""
    print_header("📊 RESUMO DA VERIFICAÇÃO")
    
    python_ok, ffmpeg_ok, packages_ok, dirs_ok, app_ok = checks
    
    statuses = [
        ("Python 3.8+", python_ok),
        ("FFmpeg instalado", ffmpeg_ok),
        ("Pacotes Python", packages_ok),
        ("Diretórios", dirs_ok),
        ("Aplicação testada", app_ok),
    ]
    
    for name, status in statuses:
        symbol = "✅" if status else "❌"
        print(f"{symbol} {name}")
    
    all_ok = all(checks)
    
    print(f"\n{'='*60}")
    if all_ok:
        print("🎉 TUDO PRONTO PARA RODAR!")
        print(f"\n   python main.py")
        print(f"   Depois acesse: http://localhost:5000")
    else:
        print("⚠️  PROBLEMAS ENCONTRADOS:")
        print("   Resolva os itens marcados com ❌ acima")
        print("   Depois execute novamente este script")
    
    print(f"{'='*60}\n")
    
    return all_ok

def main():
    """Executar verificações"""
    print("\n" + "="*60)
    print("🚀 SETUP - Conversor de Arquivos AM v2.0.0")
    print("="*60)
    
    # Executar verificações
    checks = (
        check_python(),
        check_ffmpeg(),
        check_pip_packages(),
        check_directory_structure(),
        test_application(),
    )
    
    # Exibir resultado final
    all_ok = print_final_status(checks)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
