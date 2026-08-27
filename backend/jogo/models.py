from django.db import models


class Jogador(models.Model):
    """
    Modelo de um jogador do SKCAT.

    Guarda as informacoes acumuladas do jogador:
    nome, total de moedas, recorde, partidas jogadas
    e a data de criacao do cadastro.
    """

    # Nome do jogador (ex.: "Matheus")
    nome = models.CharField(max_length=100)

    # Total de moedas acumuladas em todas as partidas
    moedas = models.IntegerField(default=0)

    # Maior pontuacao ja alcancada
    recorde = models.IntegerField(default=0)

    # Quantidade de partidas que o jogador ja jogou
    partidas_jogadas = models.IntegerField(default=0)

    # Data em que o cadastro foi criado (preenchida sozinha)
    data_criacao = models.DateTimeField(auto_now_add=True)

    # O que aparece no Admin quando listamos os jogadores
    def __str__(self):
        return self.nome


class Partida(models.Model):
    """
    Modelo de uma partida do SKCAT.

    Uma partida pertence a UM jogador (ForeignKey),
    ou seja: 1 Jogador pode ter varias Partidas,
    mas cada Partida tem somente 1 Jogador.
    """

    # Chave estrangeira: aponta para o Jogador dono da partida.
    # on_delete=CASCADE -> se o jogador for apagado,
    # as partidas dele tambem sao apagadas.
    jogador = models.ForeignKey(
        Jogador,
        on_delete=models.CASCADE,
        related_name='partidas'
    )

    # Pontuacao final da partida
    pontuacao = models.IntegerField(default=0)

    # Moedas coletadas naquela partida
    moedas_coletadas = models.IntegerField(default=0)

    # Data da partida (preenchida sozinha)
    data = models.DateTimeField(auto_now_add=True)

    # O que aparece no Admin quando listamos as partidas
    def __str__(self):
        return f"{self.jogador.nome} - {self.pontuacao} pts"