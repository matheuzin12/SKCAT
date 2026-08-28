"""
menu.py

Classe Menu: tela inicial do jogo.
Exibe a imagem de fundo e botoes Jogar/Sair.
"""

import os
import pygame

from scripts.interfaces import Botao, _caminho_tela


class Menu:
    """Tela inicial do SKCAT."""

    def __init__(self, tela, largura, altura):
        self.tela = tela
        self.largura = largura
        self.altura = altura

        # Carrega a imagem de tela inicial como fundo
        caminho = _caminho_tela("telaincial.png")
        if caminho:
            img = pygame.image.load(caminho).convert()
            self.imagem_fundo = pygame.transform.scale(img, (largura, altura))
        else:
            self.imagem_fundo = None

        # Botao Jogar (transparente)
        self.botao_jogar = Botao(
            "Jogar",
            largura // 2,
            altura // 2 + 120,
            largura=220,
            altura=55,
            cor_fundo=(50, 150, 50),
            tamanho_fonte=34,
            opacidade=120
        )

        # Botao Sair (transparente)
        self.botao_sair = Botao(
            "Sair",
            largura // 2,
            altura // 2 + 200,
            largura=220,
            altura=55,
            cor_fundo=(200, 50, 50),
            tamanho_fonte=34,
            opacidade=120
        )

    def desenhar(self):
        """Desenha o menu na tela."""
        if self.imagem_fundo:
            self.tela.blit(self.imagem_fundo, (0, 0))
        else:
            self.tela.fill((30, 30, 50))

        self.botao_jogar.desenhar(self.tela)
        self.botao_sair.desenhar(self.tela)

    def tratar_eventos(self, evento):
        """Verifica cliques nos botoes. Retorna 'jogar', 'sair' ou None."""
        if self.botao_jogar.clicou(evento):
            return "jogar"
        if self.botao_sair.clicou(evento):
            return "sair"
        return None
