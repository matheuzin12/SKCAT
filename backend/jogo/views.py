import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Jogador, Partida


def listar_jogadores(request):
    """
    API usada pela tela de selecao de jogador do SKCAT.

    Quando o jogo abre a tela "Escolha seu jogador",
    ele faz um GET aqui e recebe a lista de jogadores
    cadastrados, para escolher um deles ou digitar
    um nome novo.

    Resposta:
        {
            "jogadores": [
                {"id": 1, "nome": "Matheus", "moedas": 100,
                 "recorde": 123, "partidas_jogadas": 3},
                ...
            ]
        }
    """

    if request.method != 'GET':
        return JsonResponse(
            {'erro': 'Metodo nao permitido. Use GET.'},
            status=405
        )

    registros = Jogador.objects.order_by('-recorde', 'nome')

    dados = [
        {
            'id': registro.id,
            'nome': registro.nome,
            'moedas': registro.moedas,
            'recorde': registro.recorde,
            'partidas_jogadas': registro.partidas_jogadas,
        }
        for registro in registros
    ]

    return JsonResponse({'jogadores': dados})


@csrf_exempt
def registrar_partida(request):
    """
    API usada pelo jogo SKCAT.

    Quando o jogador perde (Game Over), o Pygame envia um POST:

        {
            "jogador": "Matheus",
            "pontuacao": 5230,
            "moedas_coletadas": 37
        }

    Este serviço:
        1. localiza (ou cria) o Jogador pelo nome;
        2. registra a Partida;
        3. aumenta partidas_jogadas += 1;
        4. soma as moedas ao total do jogador;
        5. atualiza o recorde se a pontuacao for maior;
        6. salva tudo e responde se deu certo.

    csrf_exempt: aceita o POST vindo do Pygame sem token CSRF.
    (Ok apenas para servidor local / trabalho escolar.)
    """

    # Somente aceita POST
    if request.method != 'POST':
        return JsonResponse(
            {'erro': 'Metodo nao permitido. Use POST.'},
            status=405
        )

    try:
        # Le o JSON que o jogo enviou
        dados = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse(
            {'erro': 'JSON invalido.'},
            status=400
        )

    nome = dados.get('jogador')
    pontuacao = int(dados.get('pontuacao', 0))
    moedas = int(dados.get('moedas_coletadas', 0))

    if not nome:
        return JsonResponse(
            {'erro': 'Campo "jogador" nao informado.'},
            status=400
        )

    # ====================================================
    # 1. Localiza (ou cria) o Jogador pelo nome
    # ====================================================

    jogador, criado = Jogador.objects.get_or_create(
        nome=nome
    )

    # ====================================================
    # 2. Registra a Partida
    # ====================================================

    Partida.objects.create(
        jogador=jogador,
        pontuacao=pontuacao,
        moedas_coletadas=moedas
    )

    # ====================================================
    # 3. Aumenta partidas_jogadas
    # ====================================================

    jogador.partidas_jogadas += 1

    # ====================================================
    # 4. Soma as moedas da partida ao total
    # ====================================================

    jogador.moedas += moedas

    # ====================================================
    # 5. Atualiza o recorde somente se for maior
    # ====================================================

    if pontuacao > jogador.recorde:
        jogador.recorde = pontuacao

    # ====================================================
    # 6. Salva tudo no banco
    # ====================================================

    jogador.save()

    # ====================================================
    # 7. Resposta para o jogo
    # ====================================================

    return JsonResponse({
        'ok': True,
        'jogador': jogador.nome,
        'pontuacao': pontuacao,
        'moedas_coletadas': moedas,
    })