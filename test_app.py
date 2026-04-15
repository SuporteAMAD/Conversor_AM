#!/usr/bin/env python3
"""
Script de Teste Automatizado - Conversor de Arquivos AM
Testa todas as funcionalidades da aplicação Convertio-like
"""

import os
import sys
import requests
import time
from pathlib import Path

# Configurações
BASE_URL = "http://localhost:5000"
TEST_DIR = Path(__file__).parent / "test_files"

def test_homepage():
    """Testa se a página inicial está funcionando"""
    print("🧪 Testando página inicial...")
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Página inicial OK")
            return True
        else:
            print(f"❌ Página inicial falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar página inicial: {e}")
        return False

def test_file_validation():
    """Testa validação de tipos de arquivo"""
    print("\n🧪 Testando validação de tipos...")

    from main import validate_file_type

    test_cases = [
        ("teste.ogg", "audio"),
        ("teste.mp3", "audio"),
        ("teste.mp4", "video"),
        ("teste.png", "image"),
        ("teste.docx", "document"),
        ("teste.pdf", "document"),
        ("teste.txt", "text"),
        ("teste.xlsx", "spreadsheet"),
        ("teste.csv", "spreadsheet"),
        ("teste.invalid", None)  # Deve falhar
    ]

    passed = 0
    for filename, expected in test_cases:
        try:
            if expected is None:
                # Deve lançar erro
                validate_file_type(filename)
                print(f"❌ {filename}: deveria ter falhado")
            else:
                file_type, ext = validate_file_type(filename)
                if file_type == expected:
                    print(f"✅ {filename}: {file_type}")
                    passed += 1
                else:
                    print(f"❌ {filename}: esperado {expected}, recebeu {file_type}")
        except ValueError:
            if expected is None:
                print(f"✅ {filename}: corretamente rejeitado")
                passed += 1
            else:
                print(f"❌ {filename}: erro inesperado")
        except Exception as e:
            print(f"❌ {filename}: erro {e}")

    print(f"Validação: {passed}/{len(test_cases)} testes passaram")
    return passed == len(test_cases)

def test_converters():
    """Testa instanciação de conversores"""
    print("\n🧪 Testando conversores...")

    from main import get_converter

    conversions = [
        ("audio", "mp3"),
        ("audio", "wav"),
        ("video", "wav"),
        ("video", "avi"),
        ("image", "jpg"),
        ("image", "webp"),
        ("document", "pdf"),
        ("document", "docx"),
        ("document", "txt"),
        ("text", "pdf"),
        ("spreadsheet", "csv"),
        ("spreadsheet", "xlsx")
    ]

    passed = 0
    for file_type, target_format in conversions:
        try:
            converter = get_converter(file_type, target_format, "dummy_path")
            if converter:
                print(f"✅ {file_type} → {target_format}: {type(converter).__name__}")
                passed += 1
            else:
                print(f"❌ {file_type} → {target_format}: conversor não encontrado")
        except Exception as e:
            print(f"❌ {file_type} → {target_format}: erro {e}")

    print(f"Conversores: {passed}/{len(conversions)} testes passaram")
    return passed == len(conversions)

def test_file_operations():
    """Testa operações básicas de arquivo"""
    print("\n🧪 Testando operações de arquivo...")

    from main import file_sha1, sanitize_filename

    # Testar sanitização
    test_names = [
        ("teste normal.txt", "teste_normal.txt"),
        ("teste@#$%.txt", "teste_.txt"),
        ("", "arquivo"),
        ("teste com espaços.txt", "teste_com_espa_os.txt")
    ]

    passed = 0
    for input_name, expected in test_names:
        result = sanitize_filename(input_name)
        if result == expected:
            print(f"✅ Sanitização: '{input_name}' → '{result}'")
            passed += 1
        else:
            print(f"❌ Sanitização: '{input_name}' → '{result}' (esperado '{expected}')")

    # Testar SHA1 se arquivo existe
    txt_file = TEST_DIR / "teste.txt"
    if txt_file.exists():
        try:
            sha1 = file_sha1(str(txt_file))
            if len(sha1) == 40 and sha1.isalnum():
                print(f"✅ SHA1: {sha1[:16]}...")
                passed += 1
            else:
                print(f"❌ SHA1 inválido: {sha1}")
        except Exception as e:
            print(f"❌ Erro no SHA1: {e}")
    else:
        print("⚠️ Arquivo teste.txt não encontrado para teste SHA1")

    print(f"Operações: {passed} testes passaram")
    return passed > 0

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes do Conversor de Arquivos AM v2.0.0")
    print("=" * 60)

    # Verificar se aplicação está rodando
    if not test_homepage():
        print("\n❌ Aplicação não está rodando!")
        print("Execute: python main.py")
        sys.exit(1)

    # Executar testes
    tests = [
        test_file_validation,
        test_converters,
        test_file_operations
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 Todos os testes passaram! ({passed}/{total})")
        print("\n📋 Próximos passos:")
        print("1. Abra http://localhost:5000 no navegador")
        print("2. Teste upload de arquivos dos tipos suportados")
        print("3. Verifique as conversões na interface web")
        print("4. Teste com arquivos reais (áudio, vídeo, documentos)")
    else:
        print(f"⚠️ Alguns testes falharam: {passed}/{total}")
        print("Verifique os erros acima e corrija antes de usar em produção")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)