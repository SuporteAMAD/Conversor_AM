# ⚡ INÍCIO RÁPIDO - Conversor de Arquivos AM v2.0.0

## 🚀 Começar em 2 Minutos (Local)

```bash
# 1. Entrar no diretório
cd "c:\Users\gabriel.waschburger\Documents\Conversor de Arquivos AM"

# 2. Iniciar (apenas isso!)
python main.py

# 3. Abrir no navegador
http://localhost:5000
```

✅ Pronto! Você pode converter arquivos agora.

---

## 🐳 Com Docker (5 minutos)

```bash
# 1. Build
docker build -t conversor-am .

# 2. Executar
docker run -p 5000:5000 conversor-am

# 3. Abrir
http://localhost:5000
```

Ou com Docker Compose:
```bash
docker-compose up -d
```

---

## 🌐 Deploy em Heroku (10 minutos)

```bash
# 1. Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Commands
heroku login
heroku create seu-app-name
git push heroku main
heroku open
```

---

## 📁 Estrutura de Pastas Importante

```
uploads/      ← Arquivos enviados pelo usuário
exports/      ← Arquivos convertidos (cópias)
logs/         ← Logs da aplicação
conversores/  ← Lógica de conversão
rotas/        ← Endpoints Flask
static/       ← CSS, JS, imagens
templates/    ← HTML
```

---

## 🔧 Configurações Básicas

### Variáveis de Ambiente

Criar arquivo `.env`:
```
FLASK_ENV=development
FLASK_SECRET=sua-chave-aqui
PORT=5000
```

### Limites de Arquivo

Em `config.py`:
```python
PER_FILE_LIMIT_MB = 50  # Aumentar conforme necessário
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
```

---

## ✅ Checklist de Verificação

- [ ] Python 3.10+ instalado: `python --version`
- [ ] FFmpeg funciona: `ffmpeg -version`
- [ ] Dependências: `pip install -r requirements.txt`
- [ ] Servidor roda: `python main.py`
- [ ] Acesso: `http://localhost:5000`
- [ ] Upload funciona
- [ ] Download funciona

---

## 🔗 Próximos Passos

1. **Testar** - Fazer upload de alguns arquivos
2. **Documentação Completa** - Ver `PUBLICAR.md`
3. **Deploy** - Escolher plataforma em `PUBLICAR.md`
4. **Monitoramento** - Configurar logs

---

## 🆘 Problemas Rápidos

| Problema | Solução |
|----------|---------|
| "FFmpeg not found" | `apt install ffmpeg` (Linux) ou `choco install ffmpeg` (Windows) |
| "Porta 5000 em uso" | Mudar em `main.py`: `python main.py --port 8000` |
| "Arquivo muito grande" | Aumentar `PER_FILE_LIMIT_MB` em `config.py` |
| "Permissão negada" | `chmod 755 uploads/ exports/ logs/` (Linux) |

---

## 📚 Documentação

- **Detalhado:** `PUBLICAR.md` - Todas as opções de deploy
- **Conversões:** `CONVERSOES_FUNCIONANDO.md` - Status das conversões
- **Limpeza:** `LIMPEZA.md` - Arquivos removidos
- **Testes:** `GUIA_TESTE.md` - Como testar
- **Deployment Avançado:** `DEPLOY.md` - Deploy em produção

---

**Pronto para usar! 🎉**

Dúvidas? Consulte `PUBLICAR.md` para o guia completo.
