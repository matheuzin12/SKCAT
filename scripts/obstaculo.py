"""

obstaculo.py

Classe Obstaculo:

objetos que aparecem pela direita

e se movem para a esquerda.

"""

import pygame
import os
import glob
import random


# ============================================================
# CONFIGURACOES DOS OBSTACULOS
# ============================================================

# Velocidade dos obstaculos
VELOCIDADE_OBSTACULO = 8

# Altura padrao de cada obstaculo na tela.
# A largura e calculada automaticamente para
# preservar o formato (proporcao) da imagem.
ALTURA_OBSTACULO = 90

# Altura um pouco maior para os obstaculos
# que NAO sao o "obstaculo-1".
ALTURA_OBSTACULO_MAIOR = 115

# Altura maior so para o "obstaculo-2"
ALTURA_OBSTACULO_2 = 135

# Nomes (sem diferenciar maiuscula/minuscula)
# que ficam com o tamanho padrao menor.
OBSTACULOS_MENORES = [
    "obstaculo-1",
    "caixa"
]

# ============================================================


def _carregar_obstaculos():
    """
    Carrega automaticamente todas
    as imagens PNG da pasta:

    assets/obstaculos/
    """

    caminho = os.path.join(
        "assets",
        "obstaculos"
    )

    if not os.path.exists(caminho):

        print(
            f"[ERRO] Pasta nao encontrada: {caminho}"
        )

        return []

    arquivos = sorted(
        glob.glob(
            os.path.join(
                caminho,
                "*.png"
            )
        )
    )

    imagens = []

    for arquivo in arquivos:

        imagem = pygame.image.load(
            arquivo
        ).convert_alpha()

        # ====================================================
        # REDIMENSIONA PRESERVANDO O FORMATO
        # ====================================================

        # Descobre o nome do arquivo (sem caso)
        nome = os.path.basename(
            arquivo
        ).lower()

        # Altura depende do tipo do obstaculo
        if "obstaculo-2" in nome:

            altura_desejada = ALTURA_OBSTACULO_2

        elif any(
            marcador in nome
            for marcador in OBSTACULOS_MENORES
        ):

            altura_desejada = ALTURA_OBSTACULO

        else:

            altura_desejada = ALTURA_OBSTACULO_MAIOR

        # Pega o tamanho original da imagem
        largura_original = imagem.get_width()
        altura_original = imagem.get_height()

        # Calcula a largura proporcional a altura desejada
        largura = int(
            largura_original
            * (altura_desejada / altura_original)
        )
        altura = altura_desejada

        # Redimensiona a imagem
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

    print(
        f"[OBSTACULOS] {len(imagens)} imagem(ns) encontrada(s)"
    )

    return imagens


class Obstaculo:
    """
    Representa um obstaculo do jogo.
    """

    def __init__(
        self,
        tela_largura,
        chao_y
    ):

        # ====================================================
        # CARREGA IMAGENS
        # ====================================================

        self.imagens = (
            _carregar_obstaculos()
        )

        if not self.imagens:

            # Fallback se nao encontrar imagens
            self.imagens = [
                self._criar_fallback()
            ]

        # Escolhe um obstaculo aleatorio
        self.imagem = random.choice(
            self.imagens
        )

        # ====================================================
        # TAMANHO
        # ====================================================

        self.largura_sprite = (
            self.imagem.get_width()
        )

        self.altura_sprite = (
            self.imagem.get_height()
        )

        # ====================================================
        # POSICAO
        # ====================================================

        self.tela_largura = (
            tela_largura
        )

        self.chao_y = (
            chao_y
        )

        self.x = (
            tela_largura
            + random.randint(
                200,
                500
            )
        )

        # Mantem o obstaculo apoiado no chao,
        # mesmo tendo alturas diferentes.
        self.y = (
            chao_y
            - self.altura_sprite
        )

        # ====================================================
        # VELOCIDADE
        # ====================================================

        self.velocidade = (
            VELOCIDADE_OBSTACULO
        )


    def _criar_fallback(self):
        """
        Cria um quadrado vermelho
        se nenhuma imagem for encontrada.
        """

        superficie = pygame.Surface(
            (
                ALTURA_OBSTACULO,
                ALTURA_OBSTACULO
            ),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            superficie,
            (255, 0, 0),
            (
                0,
                0,
                ALTURA_OBSTACULO,
                ALTURA_OBSTACULO
            )
        )

        return superficie


    def atualizar(self):
        """
        Move o obstaculo da direita
        para a esquerda.
        """

        self.x -= (
            self.velocidade
        )


    def desenhar(
        self,
        tela,
        debug_hitbox=False
    ):
        """
        Desenha o obstaculo.
        """

        tela.blit(
            self.imagem,
            (
                self.x,
                self.y
            )
        )

        # Mostra hitbox
        if debug_hitbox:

            pygame.draw.rect(
                tela,
                (255, 0, 0),
                self.get_hitbox(),
                2
            )


    def get_hitbox(self):
        """
        Retorna a hitbox do obstaculo.

        A hitbox fica um pouco menor
        que a imagem para evitar colisao injusta.
        """

        margem_x = int(
            self.largura_sprite
            * 0.15
        )

        margem_y = int(
            self.altura_sprite
            * 0.10
        )

        return pygame.Rect(
            self.x
            + margem_x,

            self.y
            + margem_y,

            self.largura_sprite
            - margem_x * 2,

            self.altura_sprite
            - margem_y * 2
        )


    def saiu_da_tela(self):
        """
        Verifica se saiu completamente
        pela esquerda.
        """

        return (
            self.x
            + self.largura_sprite
            < 0
        )


    def reposicionar(
        self,
        distancia
    ):
        """
        Reposiciona o obstaculo
        na direita da tela.
        """

        # Escolhe uma nova imagem
        self.imagem = random.choice(
            self.imagens
        )

        # Atualiza o tamanho porque
        # caixa e cone possuem tamanhos diferentes.
        self.largura_sprite = (
            self.imagem.get_width()
        )

        self.altura_sprite = (
            self.imagem.get_height()
        )

        # Coloca novamente na direita
        self.x = (
            self.tela_largura
            + distancia
        )

        # Posiciona corretamente no chao
        self.y = (
            self.chao_y
            - self.altura_sprite
        )


    def detectar_colisao(
        self,
        outro_rect
    ):
        """
        Verifica colisao com o jogador.
        """

        return (
            self.get_hitbox()
            .colliderect(
                outro_rect
            )
        )