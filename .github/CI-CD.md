# 🔄 GitHub Actions - CI/CD Pipeline

Este projeto inclui pipelines automatizados com GitHub Actions para Build, Testes e Deploy.

## 📋 Workflows Disponíveis

### 1. 🐳 Build e Push Docker (`docker-build-push.yml`)

**Disparado por:**
- Push em `main` ou `develop`
- Tags semânticas (`v*`)
- Pull requests em `main`

**O que faz:**
- ✅ Build da imagem Docker
- ✅ Push automático para Docker Hub
- ✅ Tagging semântico (latest, v2.0.1, etc)
- ✅ Cache de layers para otimização

**Secrets necessários:**
```
DOCKER_USERNAME    # Seu username Docker Hub
DOCKER_PASSWORD    # Token de acesso Docker Hub
```

### 2. 🧪 Testes Automatizados (`tests.yml`)

**Disparado por:**
- Push em `main` ou `develop`
- Pull requests em `main`

**O que faz:**
- ✅ Compila código Python
- ✅ Verifica sintaxe
- ✅ Valida imports principais
- ✅ Executa testes (se existirem)
- ✅ Lint com Pylint e Flake8

### 3. 🚀 Deploy Automático (`deploy.yml`)

**Disparado por:**
- Conclusão bem-sucedida do build Docker (em `main`)

**O que faz:**
- ✅ Notifica deploy bem-sucedido
- ✅ Gera relatório de deploy
- ✅ Aguarda configuração manual em servidor

## 🔐 Configurar Secrets

### No GitHub:
1. Vá para **Settings → Secrets and variables → Actions**
2. Clique em **New repository secret**
3. Adicione:

```
DOCKER_USERNAME=seu_username_docker_hub
DOCKER_PASSWORD=seu_personal_access_token_docker_hub
```

### Para Deploy Real:
```
DEPLOY_HOST=seu-servidor.com
DEPLOY_USER=usuario
DEPLOY_KEY=sua-chave-privada-ssh
```

## 📦 Versioning Semântico

Use tags para versioning automático:

```bash
# Versão minor (2.0.1)
git tag v2.0.1
git push origin v2.0.1

# Versão major (3.0.0)
git tag v3.0.0
git push origin v3.0.0
```

Isso automaticamente:
- ✅ Faz build da imagem
- ✅ Push com tag semântica
- ✅ Atualiza `latest`

## 🎯 Fluxo Recomendado

```
1. Develop local
   ↓
2. Commit e Push para develop
   ✓ Testes executados automaticamente
   ↓
3. Pull Request para main
   ✓ Testes executados novamente
   ✓ Docker build (sem push)
   ↓
4. Merge em main
   ✓ Testes finais
   ✓ Build Docker
   ✓ Push para Docker Hub
   ✓ Deploy automático
```

## 🔄 Configurar Deploy Real

Para deploy automático em servidor:

### Opção 1: SSH + Webhook
```bash
# No servidor:
mkdir -p /opt/conversor-am
cd /opt/conversor-am
git clone https://seu-repo.git .

# Criar script de deploy
cat > deploy.sh << 'EOF'
#!/bin/bash
docker pull gabrielwaschburger/conversor-am:latest
docker-compose down
docker-compose up -d
EOF

chmod +x deploy.sh
```

### Opção 2: Railway/Render
1. Conecte seu repositório GitHub
2. Selecione branch `main`
3. Railway/Render faz deploy automático a cada push

## 📊 Monitorar Workflows

No GitHub:
1. Vá para **Actions**
2. Veja status de cada workflow
3. Clique em workflow para detalhes
4. Veja logs em tempo real

## ✅ Checklist Inicial

- [ ] Criar conta Docker Hub (se não tiver)
- [ ] Gerar Personal Access Token no Docker Hub
- [ ] Adicionar secrets no GitHub
- [ ] Fazer primeiro push para testar workflows
- [ ] Verificar build em Docker Hub
- [ ] Configurar deploy real no servidor
- [ ] Testar pull da imagem em produção

## 🐛 Troubleshooting

### Workflow não dispara
```
- Verificar branch (main/develop)
- Verificar permissions em Settings
- Verificar se yml está em .github/workflows/
```

### Build Docker falha
```
- Verificar Dockerfile
- Ver logs completos em Actions
- Testar build local: docker build -t test .
```

### Push não funciona
```
- Verificar secrets (DOCKER_USERNAME, DOCKER_PASSWORD)
- Verificar credenciais Docker Hub
- Gerar novo token se expirou
```

## 📚 Referências

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Semantic Versioning](https://semver.org/)

## 🎯 Próximos Passos

1. ✅ Push para GitHub
2. ✅ Observar workflows executando
3. ✅ Configurar secrets
4. ✅ Testar build Docker
5. ⏳ Configurar deploy automático real
