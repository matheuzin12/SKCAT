"""
moeda.py

Classe Moeda: coletaveis animados.
- Animacao de girando (assets/moeda/moeda-*.png)
- Animacao de coletada (assets/moeda/meodacoletada/moedacoletada-*.png)
"""

import pygame
import os
import glob
import random


# ============================================================
# CONFIGURACOES DAS MOEDAS (altere aqui)
# ============================================================

VELOCIDADE_MOEDA = 8
VELOCIDADE_ANIMACAO = 4

# Tamanho da moeda na tela (redimensiona todos os frames)
TAMANHO_MOEDA = 60

# Hitbox proporcional ao tamanho da moeda
HITBOX_OFFSET_X = 8
HITBOX_OFFSET_Y = 8
HITBOX_LARGURA = 34
HITBOX_ALTURA = 34

# ============================================================


def _carregar_animacao(pasta, tamanho):
    """Carrega frames .png, redimensiona todos para o mesmo tamanho."""
    frames = []
    if not os.path.exists(pasta):
        return frames
    arquivos = sorted(glob.glob(os.path.join(pasta, "*.png")))
    for arquivo in arquivos:
        img = pygame.image.load(arquivo).convert_alpha()
        img = pygame.transform.smoothscale(img, (tamanho, tamanho))
        frames.append(img)
    return frames


class Moeda:
    """Moeda coletavel com animacao de girar e de coleta."""

    def __init__(self, tela_largura, chao_y, obstaculos=None):
        self.tela_largura = tela_largura
        self.altura_do_chao = chao_y
        self.velocidade = VELOCIDADE_MOEDA
        self.obstaculos = obstaculos if obstaculos is not None else []

        # Carrega e redimensiona animacoes
        pasta_girar = os.path.join("assets", "moeda")
        self.frames_girar = _carregar_animacao(pasta_girar, TAMANHO_MOEDA)

        pasta_coletada = os.path.join("assets", "moeda", "meodacoletada")
        self.frames_coletada = _carregar_animacao(pasta_coletada, TAMANHO_MOEDA)

        if not self.frames_girar:
            self.frames_girar = [self._criar_fallback()]

        # Dimensoes
        self.largura_sprite = TAMANHO_MOEDA
        self.altura_sprite = TAMANHO_MOEDA

        # Animacao
        self.frame_atual = 0
        self.contador_frames = 0

        # Posicao
        self.x = tela_largura + random.randint(200, 800)
        self._definir_altura(chao_y)

        # Estado
        self.estado = "girando"

    def _longe_de_obstaculos(self, x):
        """Empurra a moeda para a frente se estiver em cima de um obstaculo."""
        for obs in self.obstaculos:
            obs_esq = obs.x
            obs_dir = obs.x + obs.largura_sprite
            if x < obs_dir + 120 and x + self.largura_sprite > obs_esq - 120:
                x = obs_dir + 200 + random.randint(0, 300)
        return x

    def _criar_fallback(self):
        surf = pygame.Surface((TAMANHO_MOEDA, TAMANHO_MOEDA), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 215, 0),
                           (TAMANHO_MOEDA // 2, TAMANHO_MOEDA // 2),
                           TAMANHO_MOEDA // 2)
        return surf

    def _definir_altura(self, chao_y):
        opcoes = [
            chao_y - self.altura_sprite - 10,
            chao_y - self.altura_sprite - 80,
            chao_y - self.altura_sprite - 140,
        ]
        self.y = random.choice(opcoes)

    def atualizar(self):
        if self.estado == "girando":
            self.x -= self.velocidade

        self.contador_frames += 1
        if self.contador_frames >= VELOCIDADE_ANIMACAO:
            self.contador_frames = 0
            self.frame_atual += 1

            if self.estado == "girando":
                if self.frame_atual >= len(self.frames_girar):
                    self.frame_atual = 0
            elif self.estado == "coletada":
                if self.frame_atual >= len(self.frames_coletada):
                    self.frame_atual = 0
                    self.estado = "girando"
                    self.x = self._longe_de_obstaculos(
                        self.tela_largura + random.randint(300, 800)
                    )
                    self._definir_altura(self.altura_do_chao)

    def desenhar(self, tela, debug_hitbox=False):
        if self.estado == "girando":
            frames = self.frames_girar
        else:
            frames = self.frames_coletada

        if frames:
            frame = frames[self.frame_atual % len(frames)]
            tela.blit(frame, (self.x, self.y))

        if debug_hitbox:
            pygame.draw.rect(tela, (255, 255, 0), self.get_hitbox(), 2)

    def get_hitbox(self):
        return pygame.Rect(
            self.x + HITBOX_OFFSET_X,
            self.y + HITBOX_OFFSET_Y,
            HITBOX_LARGURA,
            HITBOX_ALTURA,
        )

    def saiu_da_tela(self):
        return self.x + self.largura_sprite < 0

    def reposicionar(self, distancia):
        self.estado = "girando"
        self.frame_atual = 0
        self.x = self.tela_largura + distancia
        self._definir_altura(self.altura_do_chao)

    def detectar_coleta(self, jogador_hitbox):
        if self.estado == "coletada":
            return False
        if self.get_hitbox().colliderect(jogador_hitbox):
            self.estado = "coletada"
            self.frame_atual = 0
            return True
        return False
