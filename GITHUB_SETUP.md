# 🚀 Inicializar Repositório GitHub

## Passo 1: Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name**: `conversor-am`
   - **Description**: `Ferramenta de conversão de arquivos - Andrade Maia`
   - **Visibility**: `Public` (ou Private se preferir)
   - **Initialize**: Deixe vazio (vamos fazer push do existente)
3. Clique em **Create repository**

## Passo 2: Configurar Localmente

No terminal da pasta do projeto:

```bash
# Navegar para a pasta
cd "C:\Users\gabriel.waschburger\Documents\Conversor de Arquivos AM"

# Inicializar repositório Git (se ainda não fez)
git init

# Adicionar todos os arquivos
git add .

# Primeiro commit
git commit -m "Initial commit: Conversor de Arquivos AM v2.0.2"

# Adicionar remote do GitHub (substitua YOUR_USERNAME)
git remote add origin https://github.com/gabrielwaschburger/conversor-am.git

# Renomear branch para main (se necessário)
git branch -M main

# Push inicial
git push -u origin main
```

## Passo 3: Configurar Secrets (CI/CD)

1. No GitHub: **Settings → Secrets and variables → Actions**
2. Clique em **New repository secret**
3. Adicione:

### Secret 1: DOCKER_USERNAME
```
gabrielwaschburger
```

### Secret 2: DOCKER_PASSWORD
```
# Gerar em https://hub.docker.com/settings/security
# Personal Access Token com permissão para read/write
```

Exemplo de como gerar no Docker Hub:
1. Acesse: https://hub.docker.com/settings/security
2. Clique em **New Access Token**
3. Nomeie: `github-actions`
4. Selecione permissões: `Read, Write`
5. Copie o token e cole no secret

## Passo 4: Ativar GitHub Actions

1. No GitHub: **Settings → Actions → General**
2. Selecione: **Allow all actions and reusable workflows**
3. Clique em **Save**

## Passo 5: Testar Pipeline

```bash
# Fazer um commit para disparar workflow
git add .
git commit -m "Ativar GitHub Actions"
git push origin main
```

Então:
1. Vá para: **Actions** no GitHub
2. Veja os workflows executando
3. Aguarde conclusão

## ✅ Workflow Esperado

### Primeiro Push
1. ✅ Tests.yml executado
2. ✅ Docker-build-push.yml executado
3. ✅ Deploy.yml executado (notificação)

### Resultados
- 🟢 Testes passando
- 🟢 Build Docker bem-sucedido
- 🟢 Push para Docker Hub completado
- 🟢 Imagem disponível em: `docker.io/gabrielwaschburger/conversor-am:latest`

## 📝 Commits com Tags (Versioning)

Para criar uma nova versão:

```bash
# Fazer commit
git add .
git commit -m "feat: Adicionar nova funcionalidade"

# Criar tag semântica
git tag v2.0.3

# Push commits e tags
git push origin main
git push origin v2.0.3
```

**Resultado automático:**
- ✅ Build Docker com tag `v2.0.3`
- ✅ Push para Docker Hub com multiple tags:
  - `latest`
  - `v2.0.3`
  - `v2.0`
  - `2`

## 🔍 Monitorar Workflows

1. GitHub → **Actions**
2. Clique no workflow
3. Veja:
   - ✅ Status de cada step
   - 📊 Tempo de execução
   - 📋 Logs detalhados
   - 🖼️ Artifacts (se gerados)

## 🐛 Troubleshooting

### Actions não aparece
```
1. Settings → Actions → General
2. Selecione "Allow all actions"
3. Salve e aguarde
```

### Docker push falha
```
1. Verificar secrets (DOCKER_USERNAME, DOCKER_PASSWORD)
2. Verificar credenciais no Docker Hub
3. Gerar novo token se expirou
```

### Teste falha
```
1. Ver logs completos em Actions
2. Executar localmente: python -m pytest test_app.py
3. Verificar imports: python -c "from main import app"
```

## 🎯 Checklist

- [ ] Repositório criado no GitHub
- [ ] Código feito push
- [ ] Secrets adicionados
- [ ] GitHub Actions ativado
- [ ] Primeiro workflow executado com sucesso
- [ ] Docker Hub atualizado com imagem
- [ ] Testes passando
- [ ] Badges no README funcionando

## 📚 Referências

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Hub](https://hub.docker.com/)
- [Como gerar Personal Access Token](https://docs.docker.com/docker-hub/access-tokens/)

## 🚀 Próximas Etapas

1. ✅ GitHub configurado
2. ✅ CI/CD automático
3. ⏳ Deploy em Railway/Render/VPS
4. ⏳ Configurar domínio próprio
5. ⏳ Monitoramento e backups

**Pronto para publicar!** 🎉
