# 🧹 Cleanup - Arquivos Desnecessários para Produção

## Arquivos a Remover (Antes do GitHub)

Os seguintes arquivos podem ser removidos do repositório principal pois:
1. Ocupam espaço
2. Não são necessários em produção
3. Estão no `.gitignore` ou `.dockerignore`

### 🗑️ Remover Imediatamente

```bash
# Diretórios de FFmpeg (instalado no Docker)
rm -r ffmpeg/
rm -r ffmpeg-master-latest-win64-gpl/

# Arquivo de backup Docker (já está no Docker Hub)
rm conversor-am-v2.0.1.tar

# Diretórios de runtime (serão criados em tempo de execução)
rm -r uploads/*
rm -r exports/*
rm -r logs/*
```

### 📦 Manter (Documentação + Setup Local)

Estes arquivos devem ficar no repositório para referência:

```
✅ auto_install.py           # Setup local para desenvolvedores
✅ install_ffmpeg.py         # Instalação de FFmpeg no Windows
✅ test_app.py              # Testes da aplicação
✅ setup_local.py           # Setup desenvolvimento local
✅ deploy_rds.sh            # Script de deploy em RDS
✅ test_files/              # Arquivos de teste (útil para CI/CD)
✅ DEPLOY*.md               # Documentação de deploy
✅ GUIA_TESTE.md           # Guia de testes
✅ CONVERSOES_FUNCIONANDO.md # Status das conversões
✅ PUBLICAR.md             # Guia de publicação
✅ LIMPEZA.md              # Guia de cleanup
```

## 📊 Análise de Espaço

| Item | Tamanho | Remover? | Motivo |
|------|---------|----------|--------|
| `ffmpeg/` | ~200MB | ✅ Sim | No Docker |
| `ffmpeg-master-...` | ~500MB | ✅ Sim | No Docker |
| `conversor-am-v2.0.1.tar` | 2.6GB | ✅ Sim | Docker Hub |
| `uploads/*` | ~0MB | ✅ Sim | Runtime |
| `exports/*` | ~0MB | ✅ Sim | Runtime |
| `logs/*` | ~0MB | ✅ Sim | Runtime |
| `__pycache__/` | ~5MB | ✅ Sim | .gitignore |
| Documentação | ~5MB | ✅ Manter | Referência |

**Economia Total:** ~3.3GB removido! 🎉

## 📋 Checklist Pré-GitHub

- [ ] Remover diretórios `ffmpeg/`
- [ ] Remover arquivo `.tar`
- [ ] Limpar diretórios de runtime
- [ ] Verificar `.gitignore` covers tudo
- [ ] Verificar `.dockerignore` covers tudo
- [ ] Git log limpo: `git log --oneline`
- [ ] Nenhum arquivo sensível: `git ls-files | grep -i secret`
- [ ] Pronto para `git push` ✅

## 🔄 Script de Limpeza

```bash
#!/bin/bash
# cleanup.sh - Remover arquivos desnecessários

echo "🧹 Iniciando limpeza..."

# FFmpeg (instalado no Docker)
echo "Removendo ffmpeg..."
rm -rf ffmpeg/
rm -rf ffmpeg-master-latest-win64-gpl/

# Backup Docker
echo "Removendo arquivo tar..."
rm -f conversor-am-v2.0.1.tar

# Limpar caches Python
echo "Limpando cache Python..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Runtime directories (manter .gitkeep)
echo "Limpando diretórios de runtime..."
rm -f uploads/* exports/* logs/*
touch uploads/.gitkeep exports/.gitkeep logs/.gitkeep

# Limpeza concluída
echo "✅ Limpeza concluída!"
echo "📊 Espaço economizado: ~3.3GB"
echo ""
echo "Próximo passo: git push para GitHub"
```

## 💾 Comandos Git Finais

```bash
# Verificar o que será commited
git status

# Adicionar todos os arquivos
git add .

# Commit
git commit -m "Remove: FFmpeg e arquivos desnecessários para produção"

# Push
git push origin main

# Verificar tamanho do repositório
du -sh .git
```

## ⚠️ Nota Importante

**Depois que fizer push para GitHub, esses arquivos não podem mais ser removidos do histórico sem rewrite de commits.**

Se precisar depois:
1. Manter `.gitignore` atualizado
2. Usar `git lfs` para arquivos grandes
3. Ou fazer novo push com `--force` (cuidado!)

## 🎯 Benefícios

- ✅ Repositório ~3.3GB menor
- ✅ Clone mais rápido (de 3.3GB para ~50MB)
- ✅ Builds Docker mais rápidos
- ✅ Menos dados trafegando
- ✅ Mais profissional

**Resultado Final:**
- Repositório limpo e organizado
- Pronto para CI/CD
- Otimizado para produção
- Documentação completa
