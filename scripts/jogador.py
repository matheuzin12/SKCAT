"""
jogador.py

Classe Jogador: controla o gato skatista.

Posicao, animacoes, gravidade, pulo e hitbox.
"""

import pygame
import os
import glob


# ============================================================
# CONFIGURACOES DO JOGADOR
# ============================================================

# Velocidade inicial do pulo
VELOCIDADE_PULO = -23

# Quantidade maxima de pulos antes de tocar no chao
MAX_PULOS = 2

# Gravidade
GRAVIDADE = 0.9

# Quantos ticks esperar antes de trocar de frame
VELOCIDADE_ANIMACAO = 6

# Velocidade do gato para a FRENTE durante a queda
# (para ele cair andando em direcao ao jogo, sem sair do mapa)
VELOCIDADE_QUEDA_X = 2

# Posicao fixa do gato no eixo X
POSICAO_X = 150

# Tamanho desejado do personagem
LARGURA_JOGADOR = 140
ALTURA_JOGADOR = 140

# Hitbox do jogador
HITBOX_OFFSET_X = 30
HITBOX_OFFSET_Y = 20
HITBOX_LARGURA = 75
HITBOX_ALTURA = 105

# ============================================================


def _carregar_animacao(pasta):
    """
    Carrega automaticamente os frames da animacao.

    Primeiro procura em:
    assets/animacao gato/pasta/

    Se nao encontrar, procura em:
    assets/pasta/
    """

    frames = []

    # Primeiro caminho
    caminho = os.path.join(
        "assets",
        "animacao gato",
        pasta
    )

    # Se nao existir, tenta o segundo caminho
    if not os.path.exists(caminho):

        caminho = os.path.join(
            "assets",
            pasta
        )

    # Se ainda nao existir, mostra erro
    if not os.path.exists(caminho):

        print(
            f"[ERRO] Pasta nao encontrada: {pasta}"
        )

        return frames


    # Procura todos os arquivos PNG
    arquivos = sorted(
        glob.glob(
            os.path.join(
                caminho,
                "*.png"
            )
        )
    )


    print(
        f"[PASTA] {pasta}: {caminho}"
    )

    print(
        f"[FRAMES] {pasta}: {len(arquivos)} encontrados"
    )


    # Carrega as imagens
    for arquivo in arquivos:

        imagem = pygame.image.load(
            arquivo
        ).convert_alpha()


        # Ajusta o tamanho
        imagem = pygame.transform.scale(
            imagem,
            (
                LARGURA_JOGADOR,
                ALTURA_JOGADOR
            )
        )


        frames.append(
            imagem
        )


    return frames


class Jogador:
    """
    Representa o gato skatista.
    """

    def __init__(self, chao_y, limite_x=None):

        # Limite da tela no eixo X (para nao cair fora do mapa)
        self.limite_x = limite_x

        # ====================================================
        # CARREGA AS ANIMACOES
        # ====================================================

        self.animacao_normal = (
            _carregar_animacao("gato")
        )

        self.animacao_flip = (
            _carregar_animacao("flip")
        )

        self.animacao_caindo = (
            _carregar_animacao("caindo")
        )

        self.animacao_perdeu = (
            _carregar_animacao("perdeu")
        )


        # ====================================================
        # ANIMACAO
        # ====================================================

        self.frame_atual = 0

        self.contador_frames = 0

        self.estado_animacao = "normal"


        # ====================================================
        # POSICAO
        # ====================================================

        self.x = POSICAO_X

        self.chao_y = chao_y

        self.altura_sprite = ALTURA_JOGADOR

        self.y = (
            self.chao_y
            - self.altura_sprite
        )


        # ====================================================
        # FISICA
        # ====================================================

        self.velocidade_y = 0

        self.no_chao = True

        self.pulando = False

        # Conta quantos pulos foram feitos desde que saiu do chao
        self.pulos_realizados = 0


        # ====================================================
        # ESTADO DO JOGADOR
        # ====================================================

        self.vivo = True

        self.queda_terminou = False


    def pular(self):
        """
        Faz o gato pular.
        """

        # Pode pular ate MAX_PULOS vezes antes de tocar no chao
        if self.vivo and self.pulos_realizados < MAX_PULOS:

            self.velocidade_y = (
                VELOCIDADE_PULO
            )

            self.no_chao = False

            self.pulando = True

            self.pulos_realizados += 1

            self.estado_animacao = "flip"

            # Reinicia a animacao de flip a cada pulo
            self.frame_atual = 0

            self.contador_frames = 0


    def atualizar(self):
        """
        Atualiza fisica e animacao.
        """

        # ====================================================
        # QUEDA / PERDEU
        # ====================================================

        if self.estado_animacao in ("caindo", "perdeu"):

            # Usa a animacao do estado atual
            if self.estado_animacao == "perdeu":
                animacao = self.animacao_perdeu
            else:
                animacao = self.animacao_caindo

            # Aplica gravidade durante a queda
            self.velocidade_y += (
                GRAVIDADE
            )

            self.y += (
                self.velocidade_y
            )

            # O gato cai indo um pouco para a FRENTE
            # (na direcao que o jogo anda)
            self.x += VELOCIDADE_QUEDA_X

            # ================================================
            # NAO DEIXA O GATO SAIR DO MAPA DA TELA
            # ================================================

            # Limita o X: nao passa da borda direita da tela
            if self.limite_x:

                self.x = max(
                    0,
                    min(
                        self.x,
                        self.limite_x - self.altura_sprite
                    )
                )

            # Limita o Y: nao passa do chao (nao sai por baixo)
            self.y = max(
                0,
                min(
                    self.y,
                    self.chao_y - self.altura_sprite
                )
            )

            # Atualiza a animacao
            self.contador_frames += 1

            if (
                self.contador_frames
                >= VELOCIDADE_ANIMACAO
            ):

                self.contador_frames = 0

                self.frame_atual += 1


                # Verifica se terminou a animacao
                if animacao:

                    if (
                        self.frame_atual
                        >= len(
                            animacao
                        )
                    ):

                        self.frame_atual = (
                            len(
                                animacao
                            )
                            - 1
                        )

                        self.queda_terminou = True

                else:

                    self.queda_terminou = True

            return


        # ====================================================
        # PULO
        # ====================================================

        if not self.no_chao:

            # Aplica gravidade
            self.velocidade_y += (
                GRAVIDADE
            )

            # Move o jogador
            self.y += (
                self.velocidade_y
            )


            # Verifica se voltou ao chao
            if (
                self.y
                >= self.chao_y
                - self.altura_sprite
            ):

                self.y = (
                    self.chao_y
                    - self.altura_sprite
                )

                self.velocidade_y = 0

                self.no_chao = True

                self.pulando = False

                # Ao tocar no chao, libera novamente os dois pulos
                self.pulos_realizados = 0

                self.estado_animacao = (
                    "normal"
                )

                self.frame_atual = 0

                self.contador_frames = 0


        # ====================================================
        # ANIMACAO NORMAL / FLIP
        # ====================================================

        self.contador_frames += 1

        if (
            self.contador_frames
            >= VELOCIDADE_ANIMACAO
        ):

            self.contador_frames = 0

            self.frame_atual += 1


            # Animacao de pulo
            if self.estado_animacao == "flip":

                if self.animacao_flip:

                    if (
                        self.frame_atual
                        >= len(
                            self.animacao_flip
                        )
                    ):

                        # Mantem o flip em loop enquanto estiver no ar
                        self.frame_atual = 0


            # Animacao normal
            else:

                if self.animacao_normal:

                    if (
                        self.frame_atual
                        >= len(
                            self.animacao_normal
                        )
                    ):

                        self.frame_atual = 0


    def iniciar_queda(self):
        """
        Inicia a animacao de queda/perder.
        """

        self.vivo = False

        self.estado_animacao = (
            "perdeu"
        )

        self.frame_atual = 0

        self.contador_frames = 0

        # Comeca caindo suave (sem voar para cima)
        self.velocidade_y = 0

        self.queda_terminou = False


    def desenhar(
        self,
        tela,
        debug_hitbox=False
    ):
        """
        Desenha o jogador.
        """

        # Escolhe qual animacao usar
        if (
            self.estado_animacao
            == "caindo"
        ):

            frames = (
                self.animacao_caindo
            )

        elif (
            self.estado_animacao
            == "perdeu"
        ):

            frames = (
                self.animacao_perdeu
            )

        elif (
            self.estado_animacao
            == "flip"
        ):

            frames = (
                self.animacao_flip
            )

        else:

            frames = (
                self.animacao_normal
            )


        # Desenha o frame atual
        if frames:

            frame = frames[
                self.frame_atual
                % len(frames)
            ]

            tela.blit(
                frame,
                (
                    self.x,
                    self.y
                )
            )


        # Debug da hitbox
        if debug_hitbox:

            pygame.draw.rect(
                tela,
                (255, 0, 0),
                self.get_hitbox(),
                2
            )


    def get_hitbox(self):
        """
        Retorna a hitbox do jogador.
        """

        return pygame.Rect(

            self.x
            + HITBOX_OFFSET_X,

            self.y
            + HITBOX_OFFSET_Y,

            HITBOX_LARGURA,

            HITBOX_ALTURA
        )


    def resetar(self, chao_y):
        """
        Reseta o jogador.
        """

        self.x = POSICAO_X

        self.chao_y = chao_y

        self.altura_sprite = (
            ALTURA_JOGADOR
        )

        self.y = (
            self.chao_y
            - self.altura_sprite
        )

        self.velocidade_y = 0

        self.no_chao = True

        self.pulando = False

        self.pulos_realizados = 0

        self.estado_animacao = (
            "normal"
        )

        self.frame_atual = 0

        self.contador_frames = 0

        self.vivo = True

        self.queda_terminou = False