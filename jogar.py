"""
jogar.py

Lancador do SKCAT: inicia o servidor Django e abre o jogo
automaticamente, com apenas UM comando.

Uso:
    .venv\Scripts\python.exe jogar.py
    (ou: python jogar.py)

O servidor Django fica rodando em segundo plano enquanto
o jogo estiver aberto e e desligado automaticamente
quando o jogo fechar.
"""

import os
import subprocess
import sys
import time

# ============================================================
# DESCOBRE O PYTHON DO VENV
# ============================================================

# O .venv fica em backend/.venv e ja tem tudo (Django + pygame).
# Usamos o python dele sempre, para funcionar em qualquer PC.
raiz = os.path.dirname(os.path.abspath(__file__))
python_venv = os.path.join(raiz, "backend", ".venv", "Scripts", "python.exe")

if not os.path.exists(python_venv):
    print("[jogar.py] ERRO: backend\\.venv\\Scripts\\python.exe nao encontrado.")
    print("[jogar.py] Crie o ambiente com: python -m venv backend\\.venv")
    sys.exit(1)

# ============================================================
# 1. INICIAR O SERVIDOR DJANGO
# ============================================================

print("Iniciando o servidor Django...", flush=True)

# O manage.py da raiz sabe onde fica o projeto (pasta backend/).
# Com cwd na raiz, o servidor usa o banco backend/config/db.sqlite3.
devnull = open(os.devnull, "w")

servidor = subprocess.Popen(
    [
        python_venv,
        "manage.py",
        "runserver",
        "127.0.0.1:8000",
    ],
    cwd=raiz,
    stdout=devnull,
    stderr=devnull,
)

# ============================================================
# 2. AGUARDAR O SERVIDOR FICAR PRONTO
# ============================================================

# Damos alguns segundos para o Django subir antes do jogo,
# senao o primeiro envio poderia falhar.
time.sleep(4)

# ============================================================
# 3. INICIAR O JOGO (fica aberto ate o jogador sair)
# ============================================================

print("Abrindo o SKCAT...", flush=True)
print("Jogando... feche o jogo para desligar o servidor.", flush=True)

try:
    subprocess.call([python_venv, "main.py"])
finally:
    # ========================================================
    # 4. DESLIGAR O SERVIDOR QUANDO O JOGO FECHAR
    # ========================================================

    print("Fechando o servidor Django...", flush=True)
    servidor.terminate()

    devnull.close()

    print(
        "Encerrado. As partidas salvas estao no banco "
        "backend/config/db.sqlite3",
        flush=True,
    )