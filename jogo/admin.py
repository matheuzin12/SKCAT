from django.contrib import admin

from .models import Jogador, Partida


# ============================================================
# JOGADOR
# ============================================================

@admin.register(Jogador)
class JogadorAdmin(admin.ModelAdmin):
    """
    Configuracao da listagem de Jogadores no Django Admin.
    """

    # Colunas visiveis na listagem
    list_display = (
        'id',
        'nome',
        'moedas',
        'recorde',
        'partidas_jogadas',
        'data_criacao',
    )

    # Permite buscar jogadores pelo nome
    search_fields = ('nome',)

    # Ordena pelo maior recorde primeiro (- = decrescente)
    ordering = ('-recorde',)


# ============================================================
# PARTIDA
# ============================================================

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    """
    Configuracao da listagem de Partidas no Django Admin.
    """

    # Colunas visiveis na listagem
    list_display = (
        'jogador',
        'pontuacao',
        'moedas_coletadas',
        'data',
    )

    # Ordena pelas partidas mais recentes primeiro
    ordering = ('-data',)