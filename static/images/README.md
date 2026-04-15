# 🖼️ Imagens - Conversor de Arquivos AM

## 📁 Onde colocar as imagens de logo?

Coloque as imagens de logo do escritório nesta pasta: `static/images/`

## 📝 Nomes recomendados:

- `logo.png` - Logo principal (até 200x200px)
- `logo-white.png` - Logo versão branca (até 200x200px)
- `favicon.ico` - Ícone da abinha do navegador (32x32px)

## 🎨 Como usar no site?

### 1. Logo no topo do header:

Se quiser adicionar uma imagem logo, edite o arquivo `rotas/app_routes.py` e procure por:

```html
<div class="header">
    <h1>Conversor de Arquivos AM</h1>
```

Adicione antes:

```html
<img src="/static/images/logo.png" alt="Logo" style="height: 60px; margin-bottom: 20px;">
```

### 2. Favicon (ícone da abinha):

Na seção `<head>` do `rotas/app_routes.py`, adicione:

```html
<link rel="icon" type="image/x-icon" href="/static/images/favicon.ico">
```

---

## 📸 Formatos suportados:

- ✅ PNG (melhor para logos com fundo transparente)
- ✅ JPG/JPEG
- ✅ SVG (escalável)
- ✅ GIF
- ✅ ICO (para favicon)

## 📏 Tamanhos recomendados:

| Tipo | Dimensões | Peso máximo |
|------|-----------|------------|
| Logo | 200x200px | 50KB |
| Logo Branca | 200x200px | 50KB |
| Favicon | 32x32px | 10KB |

---

## 🚀 Após adicionar imagens:

1. Coloque as imagens nesta pasta
2. Edit o HTML conforme necessário
3. Faça git commit: `git add . && git commit -m "feat: add company logos"`
4. Faça git push: `git push origin develop`
5. Reinicie o container Docker (ou ele reconhecerá automaticamente)

---

**Dúvidas?** Consulte um desenvolvedor! 💬
