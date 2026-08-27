"""
partida.py

Classe Partida: gerencia toda a gameplay do SKCAT.

Controla:
- Cenario
- Jogador
- Obstaculos
- Moedas
- Pontuacao
- Colisoes
- Animacao de queda
- Menu de pausa
- Game Over
"""

import pygame
import os
import random

from scripts.jogador import Jogador
from scripts.obstaculo import Obstaculo
from scripts.moeda import Moeda
from scripts.interfaces import Texto, Botao, FONTE_FRAKTUR


# ============================================================
# CONFIGURACOES DA PARTIDA
# ============================================================

# Quantidade de obstaculos
QTD_OBSTACULOS = 3

# Quantidade de moedas
QTD_MOEDAS = 5

# Velocidade do movimento do cenario
VELOCIDADE_CENARIO = 8

# Quantas telas cada cena fica na tela
# antes de passar para a proxima.
# 1 = cada cena aparece uma vez; so repete
# depois de passar por todas as cenas.
REPETICOES_CENA = 1

# ====================================================
# VELOCIDADE DO JOGO (aumenta com o tempo)
# ====================================================

# Velocidade no comeco (bem de vagar)
VELOCIDADE_INICIAL = 5

# Velocidade maxima (no final)
VELOCIDADE_MAXIMA = 15

# Quanto a velocidade aumenta por frame
# (0.004 = sobe devagar; quanto maior, mais rapido acelera)
AUMENTO_VELOCIDADE = 0.004

# Posicao vertical do chao
CHAO_Y = 620

# Distancia inicial entre os obstaculos
DISTANCIA_ENTRE_OBSTACULOS = 500

# ============================================================


def _carregar_cenario(largura, altura):
    """
    Procura e carrega as imagens do cenario.

    Pastas aceitas:
    - assets/cena
    - assets/cenas
    - assets/cenario
    - assets/cenarios
    """

    # Descobre automaticamente a pasta principal do projeto
    pasta_projeto = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    # Nomes possiveis para a pasta do cenario
    nomes_possiveis = [
        "cena",
        "cenas",
        "cenario",
        "cenarios"
    ]

    caminho = None

    # Procura uma das pastas
    for nome in nomes_possiveis:

        teste = os.path.join(
            pasta_projeto,
            "assets",
            nome
        )

        if os.path.isdir(teste):

            caminho = teste

            break


    # Se nenhuma pasta existir
    if caminho is None:

        print(
            "[ERRO] Nenhuma pasta de cenario encontrada!"
        )

        return []


    print(
        "[CENARIO] Pasta encontrada:",
        caminho
    )


    # ========================================================
    # PROCURA AS IMAGENS
    # ========================================================

    arquivos = []

    for nome in os.listdir(caminho):

        if nome.lower().endswith(
            (
                ".png",
                ".jpg",
                ".jpeg"
            )
        ):

            arquivos.append(
                os.path.join(
                    caminho,
                    nome
                )
            )


    # Ordena pelo nome
    arquivos = sorted(
        arquivos
    )


    print(
        "[CENARIO]",
        len(arquivos),
        "imagem(ns) encontrada(s)"
    )


    # ========================================================
    # CARREGA AS IMAGENS
    # ========================================================

    imagens = []

    for arquivo in arquivos:

        try:

            imagem = pygame.image.load(
                arquivo
            ).convert()

            # Ajusta o cenario para o tamanho da tela
            imagem = pygame.transform.scale(
                imagem,
                (
                    largura,
                    altura
                )
            )

            imagens.append(
                imagem
            )

        except pygame.error as erro:

            print(
                "[ERRO CENARIO]",
                arquivo,
                erro
            )


    return imagens


# ============================================================
# CLASSE PARTIDA
# ============================================================

class Partida:

    """
    Controla toda a gameplay do SKCAT.
    """

    def __init__(
        self,
        tela,
        largura,
        altura
    ):

        # ====================================================
        # TELA
        # ====================================================

        self.tela = tela

        self.largura = largura

        self.altura = altura


        # ====================================================
        # PASTA PRINCIPAL DO PROJETO
        # ====================================================

        self.pasta_projeto = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )


        # ====================================================
        # CENARIO
        # ====================================================

        self.cenario_lista = _carregar_cenario(
            largura,
            altura
        )


        # Guarda todas as cenas carregadas.
        # Para adicionar novas cenas, basta colocar
        # mais imagens na pasta assets/cenas (ou cenario).
        self.cenas = self.cenario_lista


        # Fallback caso nenhuma imagem seja encontrada
        if not self.cenas:

            print(
                "[ERRO] Nenhum cenario carregado!"
            )

            fundo = pygame.Surface(
                (
                    largura,
                    altura
                )
            )

            fundo.fill(
                (
                    150,
                    0,
                    0
                )
            )

            self.cenas = [fundo]


        # Cena que esta preenchendo a tela agora
        self.indice_cena_atual = 0

        # Quantas vezes a cena atual ainda aparece
        # (a primeira aparicao ja conta, entao comeca em -1)
        self.cenas_faltando = REPETICOES_CENA - 1

        # As duas imagens comecam na cena atual
        self.cenario_img1 = self.cenas[0]
        self.cenario_img2 = self.cenas[0]


        # Largura de uma tela do cenario
        self.cenario_largura = (
            self.cenas[0].get_width()
        )


        # Posicao da primeira imagem
        self.cenario1_x = 0


        # Segunda imagem fica logo depois
        self.cenario2_x = (
            self.cenario_largura
        )


        # ====================================================
        # JOGADOR
        # ====================================================

        self.jogador = Jogador(
            CHAO_Y
        )


        # ====================================================
        # OBSTACULOS
        # ====================================================

        self.obstaculos = []


        # ====================================================
        # MOEDAS
        # ====================================================

        self.moedas = []


        # ====================================================
        # PONTUACAO
        # ====================================================

        self.pontos = 0


        self.texto_pontos = Texto(
            f"Moedas: {self.pontos}",
            110,
            35,
            cor=(255, 255, 0),
            tamanho=32,
            nome_fonte=FONTE_FRAKTUR,
            caixa=True,
            cor_caixa=(0, 0, 0),
            opacidade_caixa=150
        )


        # ====================================================
        # ESTADOS DA PARTIDA
        # ====================================================

        # Velocidade atual do jogo (aumenta com o tempo)
        self.velocidade_jogo = VELOCIDADE_INICIAL

        # Indica se o jogo esta pausado
        self.pausado = False

        # Indica se o jogador perdeu
        self.game_over = False

        # Indica se esta executando a animacao de queda
        self.em_queda = False

        # Controla se o resultado da partida ja foi enviado
        # ao Django (evita enviar varias vezes na mesma partida)
        self.resultado_enviado = False

        # Recorde do jogador ANTES da partida (vindo do Django)
        self.recorde_inicio = 0

        # Marca anterior (para mostrar na mensagem de parabens)
        self.recorde_anterior = 0

        # True se o jogador bateu o recorde de moedas nesta partida
        self.bateu_recorde = False


        # ====================================================
        # DEBUG
        # ====================================================

        # Tecla H mostra/esconde as hitboxes
        self.debug_hitbox = False


        # ====================================================
        # MENU DE PAUSA
        # ====================================================

        # Titulo (fonte Fraktur)
        self.texto_pausa = Texto(
            "PAUSADO",
            largura // 2,
            altura // 2 - 160,
            cor=(255, 255, 255),
            tamanho=65,
            nome_fonte=FONTE_FRAKTUR
        )


        # Botao continuar (transparente)
        self.botao_continuar = Botao(
            "Continuar",
            largura // 2,
            altura // 2 - 60,
            largura=250,
            altura=55,
            cor_fundo=(50, 150, 50),
            cor_hover=(70, 190, 70),
            opacidade=120
        )


        # Botao reiniciar (transparente)
        self.botao_reiniciar_pausa = Botao(
            "Reiniciar",
            largura // 2,
            altura // 2 + 10,
            largura=250,
            altura=55,
            cor_fundo=(200, 150, 0),
            cor_hover=(230, 180, 20),
            opacidade=120
        )


        # Botao menu principal (transparente)
        self.botao_menu_pausa = Botao(
            "Menu principal",
            largura // 2,
            altura // 2 + 80,
            largura=250,
            altura=55,
            cor_fundo=(70, 100, 180),
            cor_hover=(90, 130, 220),
            opacidade=120
        )


        # Botao sair na pausa (transparente)
        self.botao_sair_pausa = Botao(
            "Sair",
            largura // 2,
            altura // 2 + 150,
            largura=250,
            altura=55,
            cor_fundo=(190, 50, 50),
            cor_hover=(230, 70, 70),
            opacidade=120
        )


        # ====================================================
        # GAME OVER
        # ====================================================

        # Caminho da imagem de fundo do game over
        caminho_telaperdeu = os.path.join(
            self.pasta_projeto,
            "assets",
            "telaperdeu.png"
        )

        if os.path.exists(caminho_telaperdeu):
            img_pd = pygame.image.load(
                caminho_telaperdeu
            ).convert()
            self.imagem_telaperdeu = pygame.transform.scale(
                img_pd, (largura, altura)
            )
        else:
            self.imagem_telaperdeu = None

        # Caminho da imagem perdeu.png (centralizada)
        caminho_perdeu = os.path.join(
            self.pasta_projeto,
            "assets",
            "perdeu.png"
        )

        # Som da moeda
        caminho_somoeda = os.path.join(
            self.pasta_projeto,
            "assets",
            "sons",
            "somoeda.mp3"
        )
        if os.path.exists(caminho_somoeda):
            self.som_moeda = pygame.mixer.Sound(caminho_somoeda)
        else:
            self.som_moeda = None


        # Tenta carregar a imagem
        if os.path.exists(
            caminho_perdeu
        ):

            self.imagem_perdeu = pygame.image.load(
                caminho_perdeu
            ).convert_alpha()

        else:

            self.imagem_perdeu = None


        # Texto da pontuacao final
        self.texto_pontuacao_final = Texto(
            "",
            largura // 2,
            altura // 2 - 10,
            cor=(255, 255, 0),
            tamanho=36,
            nome_fonte=FONTE_FRAKTUR,
            caixa=True,
            cor_caixa=(0, 0, 0),
            opacidade_caixa=150
        )


        # Botao tentar novamente (transparente)
        self.botao_tentar_novamente = Botao(
            "Tentar novamente",
            largura // 2,
            altura // 2 + 160,
            largura=270,
            altura=55,
            cor_fundo=(50, 150, 50),
            cor_hover=(70, 190, 70),
            opacidade=120
        )


        # Botao menu principal no Game Over (transparente)
        self.botao_menu_gameover = Botao(
            "Menu principal",
            largura // 2,
            altura // 2 + 225,
            largura=270,
            altura=55,
            cor_fundo=(70, 100, 180),
            cor_hover=(90, 130, 220),
            opacidade=120
        )


        # Botao sair no game over (transparente)
        self.botao_sair_gameover = Botao(
            "Sair",
            largura // 2,
            altura // 2 + 290,
            largura=270,
            altura=55,
            cor_fundo=(190, 50, 50),
            cor_hover=(230, 70, 70),
            opacidade=120
        )


        # ====================================================
        # MENSAGEM DE RECORDE (game over)
        # ====================================================

        # Linha 1: "PARABENS! Voce bateu seu recorde de moedas!"
        self.texto_recorde_parabens = Texto(
            "",
            largura // 2,
            altura // 2 + 45,
            cor=(255, 215, 0),
            tamanho=34,
            nome_fonte=FONTE_FRAKTUR
        )

        # Linha 2: mostra o tanto de moedas do novo recorde
        self.texto_recorde_novo = Texto(
            "",
            largura // 2,
            altura // 2 + 95,
            cor=(255, 255, 255),
            tamanho=28,
            nome_fonte=FONTE_FRAKTUR
        )


        # ====================================================
        # CRIA OBJETOS INICIAIS
        # ====================================================

        self._criar_obstaculos()

        self._criar_moedas()


    def _decidir_cena_reposicionar(self):
        """
        Decide qual cena colocar na imagem que acabou
        de sair da tela e foi levada para a direita.

        IMPORTANTE: so muda a imagem que esta SAINDO.
        A imagem que esta preenchendo a tela (a outra)
        nunca e trocada de repente, evitando a troca
        brusca de cena.

        Cada cena aparece REPETICOES_CENA vezes antes
        de passar para a proxima.
        """

        # Se ainda falta repetir a cena atual
        if self.cenas_faltando > 0:

            self.cenas_faltando -= 1

            return self.cenas[
                self.indice_cena_atual
            ]

        # Se ja repetiu o suficiente, vai para a proxima
        self.indice_cena_atual = (
            self.indice_cena_atual + 1
        ) % len(self.cenas)

        self.cenas_faltando = REPETICOES_CENA - 1

        return self.cenas[
            self.indice_cena_atual
        ]


    # ========================================================
    # CRIAR OBSTACULOS
    # ========================================================

    def _criar_obstaculos(self):
        """
        Cria os obstaculos da partida.
        """

        self.obstaculos = []


        for i in range(
            QTD_OBSTACULOS
        ):

            obstaculo = Obstaculo(
                self.largura,
                CHAO_Y
            )


            # Coloca cada obstaculo mais a frente
            obstaculo.x = (
                self.largura
                + 300
                + i * DISTANCIA_ENTRE_OBSTACULOS
                + random.randint(
                    0,
                    200
                )
            )


            self.obstaculos.append(
                obstaculo
            )


    # ========================================================
    # CRIAR MOEDAS
    # ========================================================

    def _x_moeda_livre(self, x):
        """
        Verifica se o x da moeda sobrepoe algum obstaculo.
        Se sobrepor, empurra a moeda para a frente.
        """
        moeda_largura = 60
        for obs in self.obstaculos:
            obs_esquerda = obs.x
            obs_direita = obs.x + obs.largura_sprite
            # Se a moeda estiver na faixa do obstaculo
            if (x < obs_direita + 120 and
                    x + moeda_largura > obs_esquerda - 120):
                x = obs_direita + 200
        return x

    def _criar_moedas(self):
        """
        Cria as moedas da partida, bem espacadas.
        """

        self.moedas = []

        for i in range(
            QTD_MOEDAS
        ):

            moeda = Moeda(
                self.largura,
                CHAO_Y,
                self.obstaculos
            )

            # Espalha as moedas pela frente (bem espacadas)
            x = (
                self.largura
                + 300
                + i * 500
                + random.randint(
                    100,
                    400
                )
            )

            # Evita que a moeda apareca em cima de um obstaculo
            x = self._x_moeda_livre(x)

            moeda.x = x

            self.moedas.append(
                moeda
            )


    # ========================================================
    # ATUALIZAR
    # ========================================================

    def atualizar(self):
        """
        Atualiza todos os objetos da partida.
        """


        # ====================================================
        # PAUSA
        # ====================================================

        # Se estiver pausado,
        # nao movimenta nada
        if self.pausado:

            return


        # ====================================================
        # GAME OVER
        # ====================================================

        if self.game_over:

            return


        # ====================================================
        # ANIMACAO DE QUEDA
        # ====================================================

        if self.em_queda:

            # Durante a queda,
            # atualiza somente o gato
            self.jogador.atualizar()


            # Quando a animacao terminar
            if self.jogador.queda_terminou:

                self.game_over = True

                # ============================================
                # VERIFICAR SE BATEU O RECORDE DE MOEDAS
                # ============================================

                # Marca ha quanto o jogador ja tinha antes
                # (para mostrar na mensagem de parabens)
                self.recorde_anterior = (
                    self.recorde_inicio
                )

                # Bateu o recorde se coletou MAIS moedas do
                # que a melhor marca anterior (e se ja existia
                # uma marca anterior para superar)
                if (
                    self.pontos > 0
                    and self.pontos > self.recorde_inicio
                    and self.recorde_inicio > 0
                ):

                    self.bateu_recorde = True

                # Atualiza a marca para a proxima jogada
                # ("Tentar novamente" compara com este novo valor)
                if self.pontos > self.recorde_inicio:
                    self.recorde_inicio = self.pontos


            return


        # ====================================================
        # AUMENTA A VELOCIDADE COM O TEMPO
        # ====================================================

        # Quanto mais tempo passa, mais rapido fica
        if self.velocidade_jogo < VELOCIDADE_MAXIMA:

            self.velocidade_jogo = min(
                VELOCIDADE_MAXIMA,
                self.velocidade_jogo
                + AUMENTO_VELOCIDADE
            )

        velocidade = self.velocidade_jogo


        # ====================================================
        # MOVIMENTO DO CENARIO
        # ====================================================

        self.cenario1_x -= velocidade

        self.cenario2_x -= velocidade


        # Quando a primeira imagem sair
        if (
            self.cenario1_x
            <= -self.cenario_largura
        ):

            self.cenario1_x = (
                self.cenario2_x
                + self.cenario_largura
            )

            # So a imagem que saiu recebe a proxima cena
            self.cenario_img1 = (
                self._decidir_cena_reposicionar()
            )


        # Quando a segunda imagem sair
        if (
            self.cenario2_x
            <= -self.cenario_largura
        ):

            self.cenario2_x = (
                self.cenario1_x
                + self.cenario_largura
            )

            # So a imagem que saiu recebe a proxima cena
            self.cenario_img2 = (
                self._decidir_cena_reposicionar()
            )


        # ====================================================
        # JOGADOR
        # ====================================================

        self.jogador.atualizar()


        # ====================================================
        # OBSTACULOS
        # ====================================================

        for obstaculo in self.obstaculos:

            # Usa a velocidade atual do jogo
            obstaculo.velocidade = velocidade

            # Move o obstaculo
            obstaculo.atualizar()


            # Se saiu da tela,
            # reposiciona
            if obstaculo.saiu_da_tela():

                obstaculo.reposicionar(
                    random.randint(
                        500,
                        900
                    )
                )


            # Verifica colisao com o gato
            if obstaculo.detectar_colisao(
                self.jogador.get_hitbox()
            ):

                self._iniciar_queda()

                return


        # ====================================================
        # MOEDAS
        # ====================================================

        for moeda in self.moedas:

            # Usa a velocidade atual do jogo
            moeda.velocidade = velocidade

            # Move a moeda
            moeda.atualizar()


            # Verifica se o gato coletou
            if moeda.detectar_coleta(
                self.jogador.get_hitbox()
            ):

                # Soma um ponto
                self.pontos += 1

                # Toca o som da moeda
                if self.som_moeda:
                    self.som_moeda.play()


                # Atualiza texto
                self.texto_pontos.atualizar_texto(
                    f"Moedas: {self.pontos}"
                )

                # A moeda se reposiciona sozinha
                # apos a animacao de coleta


            # Se passou pela tela (ou apos coleta)
            elif moeda.saiu_da_tela():

                moeda.reposicionar(
                    random.randint(
                        500,
                        1000
                    )
                )

                # Evita aparecer em cima de um obstaculo
                moeda.x = self._x_moeda_livre(
                    moeda.x
                )


    # ========================================================
    # QUEDA
    # ========================================================

    def _iniciar_queda(self):
        """
        Inicia a animacao de queda do gato.
        """

        # Evita iniciar duas vezes
        if self.em_queda:

            return


        self.em_queda = True


        # Chama a animacao do jogador
        self.jogador.iniciar_queda()


    # ========================================================
    # DESENHAR
    # ========================================================

    def desenhar(self):
        """
        Desenha todos os objetos na tela.
        """


        # ====================================================
        # CENARIO
        # ====================================================

        self.tela.blit(
            self.cenario_img1,
            (
                self.cenario1_x,
                0
            )
        )


        self.tela.blit(
            self.cenario_img2,
            (
                self.cenario2_x,
                0
            )
        )


        # ====================================================
        # MOEDAS
        # ====================================================

        for moeda in self.moedas:

            moeda.desenhar(
                self.tela,
                self.debug_hitbox
            )


        # ====================================================
        # OBSTACULOS
        # ====================================================

        for obstaculo in self.obstaculos:

            obstaculo.desenhar(
                self.tela,
                self.debug_hitbox
            )


        # ====================================================
        # JOGADOR
        # ====================================================

        self.jogador.desenhar(
            self.tela,
            self.debug_hitbox
        )


        # ====================================================
        # PONTUACAO
        # ====================================================

        self.texto_pontos.desenhar(
            self.tela
        )


        # ====================================================
        # MENU DE PAUSA
        # ====================================================

        # IMPORTANTE:
        # a pausa e desenhada por cima de tudo
        if self.pausado:

            self._desenhar_pausa()


        # ====================================================
        # GAME OVER
        # ====================================================

        if self.game_over:

            self._desenhar_game_over()


    # ========================================================
    # DESENHAR PAUSA
    # ========================================================

    def _desenhar_pausa(self):
        """
        Desenha o menu de pausa.
        """


        # ====================================================
        # FUNDO ESCURO TRANSPARENTE
        # ====================================================

        overlay = pygame.Surface(
            (
                self.largura,
                self.altura
            ),
            pygame.SRCALPHA
        )


        overlay.fill(
            (
                0,
                0,
                0,
                170
            )
        )


        self.tela.blit(
            overlay,
            (
                0,
                0
            )
        )


        # ====================================================
        # TITULO
        # ====================================================

        self.texto_pausa.desenhar(
            self.tela
        )


        # ====================================================
        # BOTOES
        # ====================================================

        # Continuar
        self.botao_continuar.desenhar(
            self.tela
        )


        # Reiniciar
        self.botao_reiniciar_pausa.desenhar(
            self.tela
        )


        # Menu principal
        self.botao_menu_pausa.desenhar(
            self.tela
        )


        # Sair
        self.botao_sair_pausa.desenhar(
            self.tela
        )


    # ========================================================
    # EVENTOS DA PAUSA
    # ========================================================

    def tratar_eventos_pausa(
        self,
        evento
    ):
        """
        Verifica os botoes do menu de pausa.

        Retorna:
        - continuar
        - reiniciar
        - menu
        - sair
        """


        # ====================================================
        # CONTINUAR
        # ====================================================

        if self.botao_continuar.clicou(
            evento
        ):

            return "continuar"


        # ====================================================
        # REINICIAR
        # ====================================================

        if self.botao_reiniciar_pausa.clicou(
            evento
        ):

            return "reiniciar"


        # ====================================================
        # MENU PRINCIPAL
        # ====================================================

        if self.botao_menu_pausa.clicou(
            evento
        ):

            return "menu"


        # ====================================================
        # SAIR
        # ====================================================

        if self.botao_sair_pausa.clicou(
            evento
        ):

            return "sair"


        return None


    # ========================================================
    # GAME OVER
    # ========================================================

    def _desenhar_game_over(self):
        """
        Desenha a tela de Game Over.
        """

        # ====================================================
        # FUNDO - telaperdeu.png ou overlay escuro
        # ====================================================

        if self.imagem_telaperdeu:
            self.tela.blit(self.imagem_telaperdeu, (0, 0))
        else:
            overlay = pygame.Surface(
                (self.largura, self.altura),
                pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 180))
            self.tela.blit(overlay, (0, 0))


        # ====================================================
        # IMAGEM PERDEU
        # ====================================================

        if self.imagem_perdeu:

            rect_perdeu = (
                self.imagem_perdeu.get_rect(
                    center=(
                        self.largura // 2,
                        self.altura // 2 - 150
                    )
                )
            )


            self.tela.blit(
                self.imagem_perdeu,
                rect_perdeu
            )


        # ====================================================
        # PONTUACAO FINAL
        # ====================================================

        self.texto_pontuacao_final.atualizar_texto(
            f"Voce coletou {self.pontos} moeda(s)"
        )


        self.texto_pontuacao_final.desenhar(
            self.tela
        )


        # ====================================================
        # PARABENS (quando bate o recorde de moedas)
        # ====================================================

        if self.bateu_recorde:

            self.texto_recorde_parabens.atualizar_texto(
                "PARABENS! Voce bateu seu recorde de moedas!"
            )

            self.texto_recorde_novo.atualizar_texto(
                f"Voce coletou {self.pontos} moeda(s) - "
                f"marca anterior: {self.recorde_anterior}"
            )

            self.texto_recorde_parabens.desenhar(
                self.tela
            )

            self.texto_recorde_novo.desenhar(
                self.tela
            )


        # ====================================================
        # BOTOES
        # ====================================================

        self.botao_tentar_novamente.desenhar(
            self.tela
        )


        self.botao_menu_gameover.desenhar(
            self.tela
        )


        self.botao_sair_gameover.desenhar(
            self.tela
        )


    # ========================================================
    # EVENTOS DO GAME OVER
    # ========================================================

    def tratar_eventos_gameover(
        self,
        evento
    ):
        """
        Verifica os botoes da tela de Game Over.
        """


        # Tentar novamente
        if self.botao_tentar_novamente.clicou(
            evento
        ):

            return "reiniciar"


        # Menu principal
        if self.botao_menu_gameover.clicou(
            evento
        ):

            return "menu"


        # Sair
        if self.botao_sair_gameover.clicou(
            evento
        ):

            return "sair"


        return None


    # ========================================================
    # DEFINIR RECORDE
    # ========================================================

    def definir_recorde(self, recorde):
        """
        Define a melhor marca que o jogador tinha antes
        da partida comecar (vinda do Django).

        Usada para saber no game over se o jogador
        bateu o recorde de moedas.
        """
        self.recorde_inicio = recorde
        self.recorde_anterior = recorde
        self.bateu_recorde = False


    # ========================================================
    # ALTERNAR PAUSA
    # ========================================================

    def alternar_pausa(self):
        """
        Liga ou desliga a pausa.
        """

        # Nao permite pausar depois que perdeu
        if self.game_over:

            return


        # Nao permite pausar durante a queda
        if self.em_queda:

            return


        self.pausado = (
            not self.pausado
        )


    # ========================================================
    # RESETAR PARTIDA
    # ========================================================

    def resetar(self):
        """
        Reinicia toda a partida.
        """


        # ====================================================
        # PONTUACAO
        # ====================================================

        self.pontos = 0


        self.texto_pontos.atualizar_texto(
            f"Moedas: {self.pontos}"
        )


        # ====================================================
        # ESTADOS
        # ====================================================

        self.pausado = False

        self.game_over = False

        self.em_queda = False

        # Nova partida: permite enviar o resultado de novo
        self.resultado_enviado = False

        # A mensagem de parabens e recalculada no fim da partida
        self.bateu_recorde = False

        # Volta a velocidade inicial (de vagar)
        self.velocidade_jogo = VELOCIDADE_INICIAL


        # ====================================================
        # JOGADOR
        # ====================================================

        self.jogador.resetar(
            CHAO_Y
        )


        # ====================================================
        # CENARIO
        # ====================================================

        self.indice_cena_atual = 0
        self.cenas_faltando = REPETICOES_CENA - 1
        self.cenario_img1 = self.cenas[0]
        self.cenario_img2 = self.cenas[0]

        self.cenario1_x = 0

        self.cenario2_x = (
            self.cenario_largura
        )


        # ====================================================
        # OBSTACULOS
        # ====================================================

        self._criar_obstaculos()


        # ====================================================
        # MOEDAS
        # ====================================================

        self._criar_moedas()