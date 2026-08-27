"""
selecao.py

Tela de selecao do jogador do SKCAT.

Busca no Django (via scripts.api) os jogadores cadastrados
e permite:
- clicar em um jogador existente;
- digitar um nome novo no campo de texto.

O nome escolhido vira o NOME_JOGADOR das proximas partidas.
"""

import os
import threading

import pygame

from scripts.interfaces import Botao, FONTE_FRAKTUR, Texto
from scripts.api import listar_jogadores


class SelecaoJogador:
    """Tela para escolher o jogador antes de jogar."""

    # Quantos jogadores aparecem na lista (de cada vez)
    QUANTOS_VISIVEIS = 5

    def __init__(self, tela, largura, altura):
        self.tela = tela
        self.largura = largura
        self.altura = altura

        # Nome atualmente digitado/escolhido
        self.nome = ""

        # Jogadores vindos do Django
        self.jogadores = []

        # Rolagem da lista de jogadores
        self.deslocamento = 0

        # Campo de texto comeca focado (pode digitar na hora)
        self.campo_focado = True

        # Indica se esta buscando os jogadores no servidor
        self.carregando = False

        # Mensagem de aviso (nome vazio, etc.)
        self.mensagem = ""

        # ====================================================
        # FUNDO
        # ====================================================

        # Pasta principal do projeto (pai de scripts/)
        pasta_projeto = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        caminho_fundo = os.path.join(
            pasta_projeto,
            "assets",
            "telaincial.png"
        )

        if os.path.exists(caminho_fundo):
            self.imagem_fundo = pygame.transform.scale(
                pygame.image.load(caminho_fundo).convert(),
                (largura, altura)
            )
        else:
            self.imagem_fundo = None

        # ====================================================
        # TEXTOS
        # ====================================================

        self.texto_titulo = Texto(
            "ESCOLHA SEU JOGADOR",
            largura // 2,
            90,
            cor=(255, 255, 0),
            tamanho=55,
            nome_fonte=FONTE_FRAKTUR
        )

        self.texto_subtitulo = Texto(
            "Clique em um jogador ou digite um nome novo",
            largura // 2,
            150,
            cor=(255, 255, 255),
            tamanho=26
        )

        self.texto_carregando = Texto(
            "Carregando jogadores...",
            largura // 2,
            250,
            cor=(255, 255, 255),
            tamanho=28
        )

        self.texto_vazio = Texto(
            "(nenhum jogador cadastrado ainda)",
            largura // 2,
            250,
            cor=(200, 200, 200),
            tamanho=28
        )

        self.texto_rotulo_campo = Texto(
            "Nome do jogador:",
            largura // 2,
            462,
            cor=(255, 255, 255),
            tamanho=26
        )

        # ====================================================
        # BOTOES
        # ====================================================

        self.botao_jogar = Botao(
            "Jogar",
            largura // 2 - 130,
            615,
            largura=200,
            altura=55,
            cor_fundo=(50, 150, 50),
            cor_hover=(70, 190, 70),
            opacidade=120
        )

        self.botao_voltar = Botao(
            "Voltar",
            largura // 2 + 130,
            615,
            largura=200,
            altura=55,
            cor_fundo=(70, 100, 180),
            cor_hover=(90, 130, 220),
            opacidade=120
        )

        self.botao_atualizar = Botao(
            "Atualizar",
            largura - 110,
            60,
            largura=150,
            altura=45,
            cor_fundo=(120, 120, 120),
            cor_hover=(150, 150, 150),
            opacidade=120
        )

        # Fontes usadas para desenhar as linhas da lista
        # e o texto digitado (variaveis de um frame para outro)
        self.fonte_linha = pygame.font.SysFont(None, 26)
        self.fonte_campo = pygame.font.SysFont(None, 30)
        self.fonte_mensagem = pygame.font.SysFont(None, 26)

    # ========================================================
    # LISTA DE JOGADORES
    # ========================================================

    def carregar_jogadores(self):
        """
        Busca os jogadores cadastrados no Django.

        Executa a busca em segundo plano (thread) para
        nao travar a tela se o servidor estiver desligado.
        """
        if self.carregando:
            return

        self.carregando = True
        self.mensagem = ""

        threading.Thread(
            target=self._carregar,
            daemon=True
        ).start()

    def _carregar(self):
        """Executa a busca e guarda o resultado."""
        lista = listar_jogadores()
        self.jogadores = lista
        self.carregando = False
        self.deslocamento = 0

    def _areas_jogadores(self):
        """
        Regioes clicaveis da lista de jogadores visiveis.

        Retorna uma lista de (rect, jogador).
        """
        areas = []

        inicio = self.deslocamento
        fim = min(
            inicio + self.QUANTOS_VISIVEIS,
            len(self.jogadores)
        )

        largura_linha = 560
        topo = 210
        espaco = 46

        for i in range(inicio, fim):

            rect = pygame.Rect(
                self.largura // 2 - largura_linha // 2,
                topo + (i - inicio) * espaco,
                largura_linha,
                40
            )

            areas.append(
                (rect, self.jogadores[i])
            )

        return areas

    def _campo_rect(self):
        """Regiao clicavel do campo de texto."""
        return pygame.Rect(
            self.largura // 2 - 180,
            483,
            360,
            45
        )

    def _clicou_jogador(self, posicao):
        """Se clicou em um jogador da lista, devolve o nome dele."""
        for rect, jogador in self._areas_jogadores():
            if rect.collidepoint(posicao):
                return jogador["nome"]
        return None

    def _mostrar_mensagem(self, texto, cor):
        """Guarda um aviso para desenhar na tela."""
        self.mensagem = (texto, cor)

    def obter_recorde(self):
        """
        Melhor marca (recorde) do jogador escolhido.

        Se o nome digitado ainda nao existe no banco,
        devolve 0 (jogador novo - ainda nao tem recorde).
        """
        for jogador in self.jogadores:
            if jogador["nome"] == self.nome:
                return jogador["recorde"]
        return 0

    # ========================================================
    # EVENTOS
    # ========================================================

    def tratar_eventos(self, evento):
        """
        Trata cliques e teclas da tela de selecao.

        Retorna:
        - jogar: comeca a partida com o jogador escolhido
        - voltar: volta para o menu principal
        - None: continua na tela
        """

        # ====================================================
        # MOUSE
        # ====================================================

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:

            if self.botao_jogar.clicou(evento):

                if self.nome.strip():
                    return "jogar"

                self._mostrar_mensagem(
                    "Digite ou escolha um nome primeiro.",
                    (255, 150, 150)
                )

            elif self.botao_voltar.clicou(evento):

                return "voltar"

            elif self.botao_atualizar.clicou(evento):

                self.carregar_jogadores()

            else:

                # Clicou em algum jogador da lista
                nome_clicado = self._clicou_jogador(evento.pos)

                if nome_clicado:
                    self.nome = nome_clicado
                    self.campo_focado = True
                    self.mensagem = ""

                # Clicou no campo de texto
                elif self._campo_rect().collidepoint(evento.pos):
                    self.campo_focado = True

        # ====================================================
        # ROLAGEM DA LISTA (rodinha do mouse)
        # ====================================================

        elif evento.type == pygame.MOUSEWHEEL:

            self.deslocamento -= evento.y

            maximo = max(
                0,
                len(self.jogadores) - self.QUANTOS_VISIVEIS
            )

            self.deslocamento = max(
                0,
                min(maximo, self.deslocamento)
            )

        # ====================================================
        # TECLADO
        # ====================================================

        elif evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_RETURN:

                if self.nome.strip():
                    return "jogar"

                self._mostrar_mensagem(
                    "Digite ou escolha um nome primeiro.",
                    (255, 150, 150)
                )

            elif evento.key == pygame.K_ESCAPE:

                return "voltar"

            elif evento.key == pygame.K_BACKSPACE:

                self.nome = self.nome[:-1]

            elif evento.key == pygame.K_UP:

                self.deslocamento = max(
                    0,
                    self.deslocamento - 1
                )

            elif evento.key == pygame.K_DOWN:

                maximo = max(
                    0,
                    len(self.jogadores) - self.QUANTOS_VISIVEIS
                )

                self.deslocamento = min(
                    maximo,
                    self.deslocamento + 1
                )

            elif self.campo_focado and evento.unicode:

                # Aceita somente caracteres visiveis (letras, numeros)
                if evento.unicode.isprintable():

                    if len(self.nome) < 30:
                        self.nome += evento.unicode

        return None

    # ========================================================
    # DESENHAR
    # ========================================================

    def desenhar(self):
        """Desenha a tela de selecao de jogador."""

        # ====================================================
        # FUNDO
        # ====================================================

        if self.imagem_fundo:
            self.tela.blit(self.imagem_fundo, (0, 0))
        else:
            self.tela.fill((30, 20, 45))

        # Escurece um pouco para os textos destacarem
        overlay = pygame.Surface(
            (self.largura, self.altura),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 130))
        self.tela.blit(overlay, (0, 0))

        # ====================================================
        # TITULO
        # ====================================================

        self.texto_titulo.desenhar(self.tela)
        self.texto_subtitulo.desenhar(self.tela)

        # ====================================================
        # LISTA DE JOGADORES
        # ====================================================

        if self.carregando and not self.jogadores:

            self.texto_carregando.desenhar(self.tela)

        elif not self.jogadores:

            self.texto_vazio.desenhar(self.tela)

        else:

            for rect, jogador in self._areas_jogadores():

                selecionado = (jogador["nome"] == self.nome)

                cor_fundo = (
                    (50, 120, 70)
                    if selecionado
                    else (0, 0, 0)
                )

                fundo = pygame.Surface(
                    rect.size,
                    pygame.SRCALPHA
                )
                fundo.fill((*cor_fundo, 160))
                pygame.draw.rect(
                    fundo, (255, 255, 255, 190),
                    fundo.get_rect(),
                    2,
                    border_radius=8
                )
                self.tela.blit(fundo, rect)

                texto_linha = (
                    f"{jogador['nome']}   |   recorde "
                    f"{jogador['recorde']}   |   moedas "
                    f"{jogador['moedas']}   |   partidas "
                    f"{jogador['partidas_jogadas']}"
                )

                linha = self.fonte_linha.render(
                    texto_linha,
                    True,
                    (255, 255, 255)
                )

                self.tela.blit(
                    linha,
                    linha.get_rect(
                        midleft=(rect.x + 12, rect.centery)
                    )
                )

        # ====================================================
        # CAMPO DE TEXTO
        # ====================================================

        self.texto_rotulo_campo.desenhar(self.tela)

        campo_rect = self._campo_rect()

        cor_borda = (
            (80, 220, 120)
            if self.campo_focado
            else (255, 255, 255)
        )

        fundo_campo = pygame.Surface(
            campo_rect.size,
            pygame.SRCALPHA
        )
        fundo_campo.fill((*cor_borda, 90))
        pygame.draw.rect(
            fundo_campo, (*cor_borda, 255),
            fundo_campo.get_rect(),
            2,
            border_radius=8
        )
        self.tela.blit(fundo_campo, campo_rect)

        # Texto digitado (com cursor "|" quando focado)
        texto_campo = self.nome + ("|" if self.campo_focado else "")

        superficie_campo = self.fonte_campo.render(
            texto_campo,
            True,
            (255, 255, 255)
        )

        # Reduz o texto se passar da largura do campo
        while (
            superficie_campo.get_width() > campo_rect.width - 20
            and texto_campo
        ):
            texto_campo = texto_campo[1:]
            superficie_campo = self.fonte_campo.render(
                texto_campo,
                True,
                (255, 255, 255)
            )

        self.tela.blit(
            superficie_campo,
            superficie_campo.get_rect(
                midleft=(campo_rect.x + 12, campo_rect.centery)
            )
        )

        # ====================================================
        # AVISO
        # ====================================================

        if self.mensagem:

            texto_aviso, cor_aviso = self.mensagem

            superficie_aviso = self.fonte_mensagem.render(
                texto_aviso,
                True,
                cor_aviso
            )

            self.tela.blit(
                superficie_aviso,
                superficie_aviso.get_rect(
                    center=(self.largura // 2, 560)
                )
            )

        # ====================================================
        # BOTOES
        # ====================================================

        self.botao_jogar.desenhar(self.tela)
        self.botao_voltar.desenhar(self.tela)
        self.botao_atualizar.desenhar(self.tela)