"""
api.py

Comunicacao entre o SKCAT (Pygame) e o servidor Django.

Este arquivo nao usa Django internamente: ele envia os
resultados da partida via HTTP (POST) para a API do Django.

Se o servidor estiver desligado ou acontecer algum erro,
o jogo NUNCA trava: a funcao apenas mostra o erro no
terminal e deixa o jogo continuar normalmente.
"""

import json
import urllib.request
import urllib.error

# ============================================================
# CONFIGURACOES
# ============================================================

# Endereco do servidor Django (rodando em outro terminal)
URL_API = "http://127.0.0.1:8000/api/partidas/"

# Endereco que lista os jogadores cadastrados
URL_JOGADORES = "http://127.0.0.1:8000/api/jogadores/"

# Nome do jogador enviado ao banco.
# Altere aqui o nome que voce quer usar.
NOME_JOGADOR = "Matheus"

# Quanto tempo esperar a resposta do servidor (segundos).
# Evita que o jogo fique travado se o servidor sumir.
TEMPO_ESPERA = 3

# ============================================================


def verificar_servidor():
    """
    Verifica se o servidor Django esta respondendo.

    Mostra no terminal se o servidor esta ligado ou desligado,
    para voce saber se as partidas estao sendo salvas.

    Retorna True se o servidor esta ativo, False se nao.
    """

    try:
        requisicao = urllib.request.Request(URL_API)
        urllib.request.urlopen(requisicao, timeout=TEMPO_ESPERA)

    except urllib.error.HTTPError:
        # O servidor respondeu (mesmo com erro tipo 405),
        # entao ele esta LIGADO.
        print("[API] Servidor Django ENCONTRADO. Partidas serao salvas.")
        return True

    except Exception as erro:
        # Nao conseguiu nem conectar -> servidor DESLIGADO
        print(
            "[API] ATENCAO: servidor Django NAO esta rodando.\n"
            "[API] Para salvar as partidas, rode o jogo pelo lancador:\n"
            "[API]   python jogar.py\n"
            "[API] (ou inicie o servidor separado: python manage.py runserver)\n"
            f"[API] Detalhes do erro: {erro}"
        )
        return False

    # Sem erro e sem HTTPError nao deve acontecer, mas por seguranca
    return True


def listar_jogadores():
    """
    Busca no Django os jogadores cadastrados.

    Usada pela tela de selecao de jogador do SKCAT.

    Retorna uma lista de dicionarios:
        [
            {"id": 1, "nome": "Matheus", "moedas": 100,
             "recorde": 123, "partidas_jogadas": 3},
            ...
        ]

    Se o servidor estiver desligado ou der erro,
    retorna [] (lista vazia) e o jogo continua normal.
    """

    try:
        with urllib.request.urlopen(
            URL_JOGADORES,
            timeout=TEMPO_ESPERA
        ) as resposta:

            dados = json.loads(
                resposta.read().decode("utf-8")
            )

            return dados.get("jogadores", [])

    except Exception as erro:
        print(
            "[API] NAO foi possivel buscar os jogadores.\n"
            "[API] Confira se o servidor Django esta rodando "
            "(python jogar.py ou python manage.py runserver).\n"
            f"[API] Erro: {erro}"
        )
        return []


def salvar_resultado(pontuacao, moedas, nome=None):
    """
    Envia o resultado de uma partida para o Django.

    Parametros:
        pontuacao: pontuacao final da partida
        moedas: quantidade de moedas coletadas na partida
        nome: nome do jogador (padrao: NOME_JOGADOR)

    Se der qualquer erro (servidor desligado, sem internet, etc.),
    apenas imprime o erro no terminal e termina
    sem atrapalhar o jogo.
    """

    # Se nao informarem um nome, usa o escolhido na tela
    if nome is None:
        nome = NOME_JOGADOR

    # Monta o JSON que o Django espera receber
    dados = {
        "jogador": nome,
        "pontuacao": pontuacao,
        "moedas_coletadas": moedas,
    }

    corpo = json.dumps(dados).encode("utf-8")

    # Cria a requisicao POST
    requisicao = urllib.request.Request(
        URL_API,
        data=corpo,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        # Envia a requisicao e espera a resposta do servidor.
        # TEMPO_ESPERA = limite de segundos para nao travar o jogo.
        with urllib.request.urlopen(
            requisicao,
            timeout=TEMPO_ESPERA
        ) as resposta:

            texto = resposta.read().decode("utf-8")
            print(f"[API] Partida salva! Resposta: {texto}")

    except urllib.error.HTTPError as erro:

        # Servidor respondeu, mas com erro (ex.: 400, 500)
        print(f"[API] Servidor respondeu com erro {erro.code}: {erro.read().decode('utf-8')}")

    except Exception as erro:

        # Qualquer outro erro (servidor desligado, conexao recusada...)
        print(
            "[API] NAO foi possivel salvar a partida.\n"
            "[API] Confira se o servidor Django esta rodando:\n"
            "[API]   python jogar.py\n"
            "[API] (ou inicie o servidor separado: python manage.py runserver)\n"
            f"[API] Erro: {erro}"
        )