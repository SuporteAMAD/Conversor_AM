"""
Teste de Integração da Fila v2.2.0
Testa a integração completa entre Flask app e fila
"""

import os
import sys
import time
import tempfile
import requests
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(__file__))

def test_queue_integration():
    """Testa integração completa da fila."""
    print("\n=== Teste de Integração da Fila v2.2.0 ===")

    # Criar arquivo de teste
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as f:
        f.write("Arquivo de teste para conversão")
        test_file_path = f.name

    try:
        # 1. Testar se app está rodando
        print("1. Verificando se app Flask está rodando...")
        try:
            response = requests.get("http://localhost:5000/", timeout=5)
            if response.status_code != 200:
                print("❌ App Flask não está rodando em localhost:5000")
                return False
            print("✅ App Flask está rodando")
        except requests.exceptions.RequestException:
            print("❌ Não foi possível conectar ao app Flask")
            return False

        # 2. Testar API de stats da fila
        print("\n2. Testando API de estatísticas da fila...")
        try:
            response = requests.get("http://localhost:5000/api/queue/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ API de stats funcionando: {stats}")
            else:
                print(f"❌ API de stats falhou: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro na API de stats: {e}")
            return False

        # 3. Testar upload para fila (simular)
        print("\n3. Testando upload para fila...")
        try:
            with open(test_file_path, 'rb') as f:
                files = {'file': ('teste.txt', f, 'text/plain')}
                data = {'target_format': 'txt', 'use_queue': 'true'}
                response = requests.post(
                    "http://localhost:5000/convert",
                    files=files,
                    data=data,
                    timeout=10
                )

            if response.status_code == 201:
                result = response.json()
                if result.get('success') and result.get('task_id'):
                    task_id = result['task_id']
                    print(f"✅ Upload para fila funcionou: Task ID {task_id}")
                else:
                    print(f"❌ Resposta inválida: {result}")
                    return False
            else:
                print(f"❌ Upload falhou: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ Erro no upload: {e}")
            return False

        # 4. Testar status da tarefa
        print(f"\n4. Testando status da tarefa {task_id}...")
        try:
            response = requests.get(f"http://localhost:5000/api/queue/status/{task_id}", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Status da tarefa: {status}")
            else:
                print(f"❌ Status falhou: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro no status: {e}")
            return False

        # 5. Aguardar processamento (até 30 segundos)
        print("\n5. Aguardando processamento da tarefa...")
        max_wait = 30
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"http://localhost:5000/api/queue/status/{task_id}", timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    current_status = status.get('status')

                    if current_status == 'completed':
                        print(f"✅ Tarefa concluída em {time.time() - start_time:.1f}s")
                        break
                    elif current_status == 'error':
                        print(f"❌ Tarefa falhou: {status.get('error')}")
                        return False
                    else:
                        print(f"⏳ Status: {current_status} (esperando...)")
                        time.sleep(2)
                else:
                    print(f"❌ Erro ao verificar status: {response.status_code}")
                    time.sleep(2)

            except Exception as e:
                print(f"❌ Erro ao verificar status: {e}")
                time.sleep(2)

        else:
            print(f"❌ Timeout: tarefa não concluiu em {max_wait}s")
            return False

        print("\n✅ Todos os testes de integração passaram!")
        return True

    finally:
        # Cleanup
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE INTEGRAÇÃO DA FILA v2.2.0")
    print("=" * 60)
    print("Pré-requisitos:")
    print("1. App Flask rodando em localhost:5000")
    print("2. Worker da fila inicializado")
    print("3. Arquivos da fila criados")
    print("=" * 60)

    try:
        if test_queue_integration():
            print("\n" + "=" * 60)
            print("🎉 INTEGRAÇÃO BEM-SUCEDIDA!")
            print("Fila v2.2.0 está funcionando corretamente")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ FALHA NA INTEGRAÇÃO")
            print("Verifique os logs e tente novamente")
            print("=" * 60)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)