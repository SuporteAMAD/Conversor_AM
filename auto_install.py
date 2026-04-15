#!/usr/bin/env python3
"""
Instalador Automático de FFmpeg e Dependências
Conversor de Arquivos AM v2.0.0
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path

def print_header(msg):
    print(f"\n{'='*70}")
    print(f"🔧 {msg}")
    print(f"{'='*70}\n")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_info(msg):
    print(f"ℹ️  {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def is_admin():
    """Verificar se está rodando como admin (Windows)"""
    if platform.system() != "Windows":
        return True
    
    try:
        from ctypes import windll
        return windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def check_ffmpeg():
    """Verificar se FFmpeg está instalado"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, timeout=5, text=True)
        return result.returncode == 0
    except:
        return False

def install_ffmpeg_chocolatey():
    """Instalar FFmpeg via Chocolatey"""
    print_header("Tentando instalar FFmpeg via Chocolatey")
    
    if not is_admin():
        print_error("PowerShell NÃO está como Administrador")
        print("   Feche isto e execute como Admin\n")
        return False
    
    try:
        # Verificar se Chocolatey existe
        result = subprocess.run(['choco', '--version'], 
                              capture_output=True, timeout=5, text=True)
        
        if result.returncode != 0:
            print_warning("Chocolatey não encontrado")
            print("   Instalando Chocolatey primeiro...\n")
            
            # Instalar Chocolatey
            ps_cmd = (
                "[System.Net.ServicePointManager]::SecurityProtocol = "
                "[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
                "iex ((New-Object System.Net.WebClient).DownloadString"
                "('https://community.chocolatey.org/install.ps1'))"
            )
            
            subprocess.run(['powershell', '-Command', ps_cmd], check=True)
            print_success("Chocolatey instalado")
        
        print_info("Instalando FFmpeg via Chocolatey...")
        result = subprocess.run(['choco', 'install', 'ffmpeg', '-y'], 
                              capture_output=False, timeout=300)
        
        if result.returncode == 0:
            print_success("FFmpeg instalado via Chocolatey")
            return True
        else:
            print_error("Falha ao instalar via Chocolatey")
            return False
            
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

def install_ffmpeg_manual():
    """Instalar FFmpeg manualmente do source"""
    print_header("Instalação Manual de FFmpeg")
    
    try:
        # URL do FFmpeg
        if platform.machine() in ('AMD64', 'x86_64'):
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z"
            print_info("Baixando FFmpeg (build full)...")
        else:
            print_error("Arquitetura não suportada")
            return False
        
        # Diretório de instalação
        install_dir = Path("ffmpeg")
        bin_dir = install_dir / "bin"
        
        # Download
        output_file = "ffmpeg-release.7z"
        
        print_info(f"Fazendo download (pode levar alguns minutos)...")
        urllib.request.urlretrieve(url, output_file)
        print_success(f"Download completo: {output_file}")
        
        # Tentar extrair com 7z (se disponível) ou zipfile
        print_info("Descompactando...")
        
        try:
            subprocess.run(['7z', 'x', output_file, f'-o{install_dir}'], 
                         check=True, capture_output=True)
        except:
            print_warning("7z não encontrado, tentando com Python...")
            print_error("Arquivo .7z requer 7-Zip para extrair")
            print("\nAlternativa: Baixe manualmente")
            print("1. https://www.ffmpeg.org/download.html")
            print("2. Escolha 'Windows builds by BtbN'")
            print("3. Extraia como: C:\\ffmpeg")
            return False
        
        # Criar diretório bin se não existir
        if not bin_dir.exists():
            bin_dir.mkdir(parents=True, exist_ok=True)
        
        # Adicionar ao PATH (variável de ambiente)
        print_info("Adicionando ao PATH do Windows...")
        
        env_path = os.environ.get('PATH', '')
        new_path = str(bin_dir.absolute()) + os.pathsep + env_path
        
        subprocess.run(['setx', 'PATH', new_path], 
                      capture_output=True, shell=True)
        
        # Atualizar PATH atual
        os.environ['PATH'] = new_path
        
        print_success("FFmpeg instalado em: " + str(install_dir.absolute()))
        print_info("PATH atualizado")
        
        # Limpar arquivo de download
        try:
            os.remove(output_file)
        except:
            pass
        
        return True
        
    except Exception as e:
        print_error(f"Erro na instalação manual: {e}")
        return False

def install_ffmpeg_windows():
    """Instalar FFmpeg no Windows"""
    print_header("Terminal de Instalação - FFmpeg (Windows)")
    
    # Tentar Chocolatey primeiro
    if install_ffmpeg_chocolatey():
        print_success("FFmpeg pronto!")
        return True
    
    # Se falhar, tentar manual
    print_warning("Chocolatey não funcionou, tentando download manual...")
    
    if install_ffmpeg_manual():
        print_success("FFmpeg pronto!")
        return True
    
    # Se ainda falhar, instruções finais
    print_error("Instalação automática falhou")
    print_ffmpeg_manual_instructions()
    return False

def print_ffmpeg_manual_instructions():
    """Imprimir instruções para instalação manual"""
    print("\n" + "="*70)
    print("📥 INSTALAÇÃO MANUAL - FFmpeg")
    print("="*70 + "\n")
    
    print("1. Acesse: https://ffmpeg.org/download.html")
    print("2. Escolha: 'Windows builds by BtbN'")
    print("3. Baixe o arquivo .zip (completo)")
    print("4. Extraia a pasta para: C:\\ffmpeg")
    print("5. Adicione C:\\ffmpeg\\bin ao PATH do Windows")
    print("6. Reinicie o computador")
    print("7. Abra PowerShell e teste:\n")
    print("   ffmpeg -version\n")
    print("="*70)

def install_ffmpeg_linux():
    """Instalar FFmpeg no Linux"""
    print_header("Terminal de Instalação - FFmpeg (Linux)")
    
    try:
        print_info("Atualizando repositórios...")
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        
        print_info("Instalando FFmpeg...")
        subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'], check=True)
        
        print_success("FFmpeg instalado!")
        return True
        
    except Exception as e:
        print_error(f"Erro: {e}")
        print("Instale manualmente: sudo apt install ffmpeg")
        return False

def install_ffmpeg_mac():
    """Instalar FFmpeg no Mac"""
    print_header("Terminal de Instalação - FFmpeg (macOS)")
    
    try:
        print_info("Verificando Homebrew...")
        subprocess.run(['brew', '--version'], check=True, capture_output=True)
        
        print_info("Instalando FFmpeg...")
        subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
        
        print_success("FFmpeg instalado!")
        return True
        
    except:
        print_error("Homebrew não encontrado")
        print("Instale em: https://brew.sh/")
        return False

def install_python_packages():
    """Instalar pacotes Python necessários"""
    print_header("Instalando Pacotes Python")
    
    packages = [
        'flask',
        'werkzeug',
        'pillow',
        'reportlab',
        'pdf2docx',
        'python-docx',
        'pandas',
        'openpyxl',
    ]
    
    print_info(f"Instalando {len(packages)} pacotes...")
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade'] + packages,
            check=True
        )
        print_success("Todos os pacotes instalados!")
        return True
    except Exception as e:
        print_error(f"Erro ao instalar pacotes: {e}")
        return False

def verify_installation():
    """Verificar se tudo foi instalado"""
    print_header("Verificando Instalação")
    
    # Verificar FFmpeg
    if check_ffmpeg():
        print_success("FFmpeg ✓")
    else:
        print_error("FFmpeg NÃO encontrado")
        return False
    
    # Verificar pacotes Python
    packages = ['flask', 'pillow', 'reportlab', 'pdf2docx', 'pandas']
    all_ok = True
    
    for pkg in packages:
        try:
            __import__(pkg)
            print_success(f"{pkg} ✓")
        except ImportError:
            print_error(f"{pkg} NÃO encontrado")
            all_ok = False
    
    return all_ok

def main():
    """Executar instalação"""
    print("\n" + "="*70)
    print("🚀 INSTALADOR - Conversor de Arquivos AM v2.0.0")
    print("="*70)
    
    system = platform.system()
    print(f"\nSistema Operacional: {system}")
    
    # Instalar FFmpeg conforme SO
    if system == "Windows":
        ffmpeg_ok = install_ffmpeg_windows()
    elif system == "Darwin":  # macOS
        ffmpeg_ok = install_ffmpeg_mac()
    elif system == "Linux":
        ffmpeg_ok = install_ffmpeg_linux()
    else:
        print_error(f"Sistema operacional não suportado: {system}")
        return 1
    
    if not ffmpeg_ok:
        print_warning("Continuando mesmo sem FFmpeg...")
    
    # Instalar pacotes Python
    python_ok = install_python_packages()
    
    # Verificar
    print("\n")
    if verify_installation():
        print("\n" + "="*70)
        print("🎉 INSTALAÇÃO COMPLETA!")
        print("="*70)
        print("\nPróximos passos:")
        print("  1. python main.py")
        print("  2. Abra http://localhost:5000")
        print("  3. Teste as conversões")
        return 0
    else:
        print("\n" + "="*70)
        print("⚠️  ALGUNS ITENS NÃO COMPLETARAM")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
