#!/usr/bin/env python3
"""
Instalador de FFmpeg para Windows - Sem necessidade de Admin
Faz download e configura automaticamente
"""

import os
import sys
import zipfile
import urllib.request
import subprocess
from pathlib import Path

def print_header(msg):
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

def check_ffmpeg():
    """Verificar se FFmpeg está em PATH"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.decode().split('\n')[0]
            return True, version
    except:
        pass
    return False, None

def download_ffmpeg():
    """Download FFmpeg já compilado"""
    print_header("Baixando FFmpeg")
    
    # URL do FFmpeg pré-compilado
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    ffmpeg_zip = "ffmpeg-latest.zip"
    ffmpeg_dir = Path("ffmpeg")
    
    # Verificar se já existe
    if ffmpeg_dir.exists() and (ffmpeg_dir / "bin" / "ffmpeg.exe").exists():
        print_success("FFmpeg já existe localmente")
        return True
    
    try:
        print_info(f"Fazendo download de FFmpeg (pode levar alguns minutos)...")
        
        # Download com barra de progresso simples
        def download_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, int(100.0 * downloaded / total_size))
                print(f"\r📥 {percent}% - {downloaded/(1024*1024):.1f}MB / {total_size/(1024*1024):.1f}MB", end='', flush=True)
        
        urllib.request.urlretrieve(url, ffmpeg_zip, download_progress)
        print("\n")
        print_success("Download concluído")
        
        # Criar diretório
        ffmpeg_dir.mkdir(exist_ok=True)
        
        # Extrair
        print_info("Descompactando...")
        with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
            # Extrair e remover diretório raiz se necessário
            items = zip_ref.namelist()
            prefix = items[0].split('/')[0] + '/'
            
            for item in items:
                if item.startswith(prefix):
                    target_path = ffmpeg_dir / item[len(prefix):]
                else:
                    target_path = ffmpeg_dir / item
                
                if item.endswith('/'):
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    extracted_path = zip_ref.extract(item)
                    os.replace(extracted_path, target_path)
        
        # Limpar arquivo ZIP
        os.remove(ffmpeg_zip)
        
        print_success("FFmpeg descompactado")
        return True
        
    except Exception as e:
        print_error(f"Erro no download: {e}")
        return False

def add_to_path():
    """Adicionar FFmpeg ao PATH"""
    print_header("Configurando PATH")
    
    ffmpeg_bin = Path.cwd() / "ffmpeg" / "bin"
    
    if not ffmpeg_bin.exists():
        print_error("Diretório ffmpeg/bin não encontrado")
        return False
    
    # Adicionar ao PATH do usuário (não requer admin)
    import subprocess
    
    try:
        # Verificar PATH current
        current_path = os.environ.get('PATH', '')
        ffmpeg_path = str(ffmpeg_bin)
        
        if ffmpeg_path in current_path:
            print_success("FFmpeg já está no PATH")
            return True
        
        # Tentar adicionar via setx (user PATH)
        print_info(f"Adicionando {ffmpeg_path} ao PATH do usuário...")
        
        # Este comando pode pedir confirmação
        result = subprocess.run(
            ['setx', 'PATH', f'{current_path};{ffmpeg_path}'],
            capture_output=True
        )
        
        if result.returncode == 0:
            print_success("Adicionado ao PATH do usuário")
            print_warning("⚠️  Reinicie o PowerShell/CMD para aplicar as mudanças")
            return True
        else:
            print_warning("Não foi possível usar setx, mas FFmpeg foi instalado localmente")
            print_info("Você pode usar: .\\ffmpeg\\bin\\ffmpeg.exe")
            return True
            
    except Exception as e:
        print_warning(f"Não foi possível adicionar ao PATH global: {e}")
        print_info("FFmpeg foi instalado e pode ser usado como: .\\ffmpeg\\bin\\ffmpeg.exe")
        return True

def test_ffmpeg():
    """Testar FFmpeg"""
    print_header("Testando FFmpeg")
    
    # Tenta encontrar FFmpeg
    ffmpeg_exe = None
    
    # Primeiro tenta no PATH
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            ffmpeg_exe = 'ffmpeg'
    except:
        pass
    
    # Se não achou, tenta localmente
    if not ffmpeg_exe:
        local_ffmpeg = Path.cwd() / "ffmpeg" / "bin" / "ffmpeg.exe"
        if local_ffmpeg.exists():
            ffmpeg_exe = str(local_ffmpeg)
    
    if ffmpeg_exe:
        result = subprocess.run([ffmpeg_exe, '-version'], 
                              capture_output=True, timeout=5)
        version = result.stdout.decode().split('\n')[0]
        print_success(f"FFmpeg funcionando: {version}")
        
        # Testar ffprobe
        ffprobe_exe = ffmpeg_exe.replace('ffmpeg', 'ffprobe')
        try:
            result = subprocess.run([ffprobe_exe, '-version'], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                print_success("FFprobe também disponível")
        except:
            print_warning("FFprobe não encontrado (opcional)")
        
        return True
    else:
        print_error("FFmpeg não encontrado")
        return False

def run_setup():
    """Executar setup_local.py"""
    print_header("Validando ambiente completo")
    
    try:
        result = subprocess.run([sys.executable, 'setup_local.py'], 
                              capture_output=False, timeout=60)
        return result.returncode == 0
    except Exception as e:
        print_error(f"Erro ao executar setup: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🚀 Instalador de Dependências - Conversor de Arquivos AM")
    print("="*60)
    
    # Verificar se já tem FFmpeg
    is_installed, version = check_ffmpeg()
    if is_installed:
        print_success(f"FFmpeg já instalado: {version}")
    else:
        # Download e instala
        if not download_ffmpeg():
            print_error("Falha ao baixar FFmpeg")
            return 1
        
        # Configura PATH
        if not add_to_path():
            print_warning("PATH não foi configurado, mas FFmpeg instalado localmente")
    
    # Testa
    if not test_ffmpeg():
        print_warning("FFmpeg não está no PATH")
        print_info("Tente reiniciar o PowerShell/CMD")
        print_info("Ou use: .\\ffmpeg\\bin\\ffmpeg.exe")
    
    # Executar validação
    if not run_setup():
        print_error("Setup incompleto")
        return 1
    
    print("\n" + "="*60)
    print("✅ TUDO PRONTO!")
    print("="*60)
    print("""
🎯 PRÓXIMOS PASSOS:

1. Feche todos os PowerShells abertos
2. Abra um NOVO PowerShell
3. Vá para o diretório:
   cd "C:\\Users\\gabriel.waschburger\\Documents\\Conversor de Arquivos AM"

4. Rode a aplicação:
   python main.py

5. Em outro PowerShell, testar:
   python test_app.py

6. Abra no navegador:
   http://localhost:5000
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
