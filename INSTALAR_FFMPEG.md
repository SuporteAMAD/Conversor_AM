# ⚡ Instalação Rápida - FFmpeg

## Por que FFmpeg é necessário?

FFmpeg é **obrigatório** para converter áudio e vídeo. Sem ele, conversões como:
- MP3 → WAV ❌
- MP4 → AVI ❌
- Qualquer áudio/vídeo ❌

## 🚀 Instalação Rápida (3 passos)

### Opção 1: Instalar via PowerShell (RECOMENDADO)

#### Se você TEM Chocolatey:
```powershell
# Abrir PowerShell como Administrador
choco install ffmpeg

# Reiniciar PowerShell
# Verificar
ffmpeg -version
```

#### Se você NÃO tem Chocolatey:

1. **Instalar Chocolatey** (executar como Admin):
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

2. **Fechar e reabrir PowerShell como Admin**

3. **Instalar FFmpeg**:
```powershell
choco install ffmpeg
```

4. **Verificar**:
```powershell
ffmpeg -version
```

### Opção 2: Instalação Manual

1. **Download**:
   - Acesse: https://ffmpeg.org/download.html
   - Clique em "Windows builds by BtbN"
   - Baixe o arquivo `ffmpeg-master-latest-win64-gpl.zip` (ou similar)

2. **Descompactar**:
   - Extraia em qualquer lugar (ex: `C:\ffmpeg`)

3. **Adicionar ao PATH**:
   - Windows Key + R → `sysdm.cpl` → Enter
   - Aba: `Avançado`
   - Botão: `Variáveis de Ambiente`
   - Selecione `PATH` na lista
   - Clique em `Editar`
   - Clique em `Novo`
   - Digite: `C:\ffmpeg\bin` (ajuste se extraiu em outro lugar)
   - OK, OK, OK
   - **Reinicie o PowerShell**

4. **Verificar**:
```powershell
ffmpeg -version
```

## ✅ Validar Instalação

Após instalação, execute:

```powershell
cd "C:\Users\gabriel.waschburger\Documents\Conversor de Arquivos AM"
python setup_local.py
```

Deve aparecer:
```
✅ FFmpeg instalado
✅ Pacotes Python
✅ Diretórios
✅ Aplicação testada
🎉 TUDO PRONTO PARA RODAR!
```

## 🚨 Se com Erro "ffmpeg not recognized"

Significa que FFmpeg NÃO foi adicionado ao PATH ou PowerShell não foi reiniciado.

**Solução**:
1. Feche TODOS os PowerShells abertos
2. Abra um PowerShell NOVO
3. Tente: `ffmpeg -version`

## 🎯 Próximos Passos

Após FFmpeg Instalado:

```powershell
# Rodar a aplicação
cd "C:\Users\gabriel.waschburger\Documents\Conversor de Arquivos AM"
python main.py

# Em outro PowerShell, testar
python test_app.py

# Abrir no navegador
# http://localhost:5000
```

## 📝 Notas

- FFmpeg + FFprobe devem estar no PATH global do Windows
- Após instalar, o PowerShell precisa ser reiniciado
- Teste com: `ffmpeg -version` e `ffprobe -version`
