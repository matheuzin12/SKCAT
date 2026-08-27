"""
main.py

Arquivo principal do SKCAT.
Controla inicializacao, estados, eventos, musicas e transicoes.
"""

import pygame
import sys
import os
import threading

import scripts.api as api

from scripts.menu import Menu
from scripts.partida import Partida
from scripts.selecao import SelecaoJogador
from scripts.api import salvar_resultado, verificar_servidor


# ============================================================
# CONFIGURACOES GERAIS
# ============================================================

LARGURA = 1280
ALTURA = 720
FPS = 60

TITULO = "SKCAT - Gato Skatista"

# Velocidade do fade (0-255 por frame, 4 = 64 frames = ~1 segundo)
FADE_VELOCIDADE = 4

# ============================================================


def main():
    """Funcao principal do jogo."""

    pygame.init()
    pygame.mixer.init()

    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption(TITULO)
    relogio = pygame.time.Clock()

    # ========================================================
    # CARREGAR MUSICAS E SONS
    # ========================================================

    pasta_sons = os.path.join("assets", "sons")

    caminho_menu = os.path.join(pasta_sons, "musicacomecojogo.mp3")
    tem_musica_menu = os.path.exists(caminho_menu)

    caminho_trilha = os.path.join(pasta_sons, "trilha sonora.mp3")
    tem_trilha = os.path.exists(caminho_trilha)

    caminho_perdeu_som = os.path.join(pasta_sons, "perdeu.mp3")
    if os.path.exists(caminho_perdeu_som):
        som_perdeu = pygame.mixer.Sound(caminho_perdeu_som)
    else:
        som_perdeu = None

    # ========================================================
    # ESTADO E OBJETOS
    # ========================================================

    estado = "menu"
    estado_anterior = None

    menu = Menu(tela, LARGURA, ALTURA)
    partida = Partida(tela, LARGURA, ALTURA)
    selecao = SelecaoJogador(tela, LARGURA, ALTURA)

    # Verifica no terminal se o servidor Django esta ativo
    # (sempre em segundo plano, sem travar o jogo)
    threading.Thread(
        target=verificar_servidor,
        daemon=True
    ).start()

    # Toca a musica do menu ao iniciar
    if tem_musica_menu:
        pygame.mixer.music.load(caminho_menu)
        pygame.mixer.music.play(-1)

    # ========================================================
    # SISTEMA DE FADE (transicao entre telas)
    # ========================================================

    fade_alpha = 0
    fade_estado = "nenhum"
    fade_destino = None

    def iniciar_fade(destino):
        """Inicia uma transicao de fade para o estado destino."""
        nonlocal fade_estado, fade_destino
        fade_estado = "escurecendo"
        fade_destino = destino

    # Surface preta para o fade
    fade_surface = pygame.Surface((LARGURA, ALTURA))
    fade_surface.fill((0, 0, 0))

    # ========================================================
    # LOOP PRINCIPAL
    # ========================================================

    rodando = True

    while rodando:

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                rodando = False

            # So processa botoes se nao estiver no meio de um fade
            if fade_estado != "nenhum":
                continue

            # --- MENU ---
            if estado == "menu":
                resultado = menu.tratar_eventos(evento)
                if resultado == "jogar":
                    selecao.carregar_jogadores()
                    iniciar_fade("selecionar")
                elif resultado == "sair":
                    rodando = False

            # --- SELECAO DE JOGADOR ---
            elif estado == "selecionar":
                resultado = selecao.tratar_eventos(evento)
                if resultado == "jogar":
                    api.NOME_JOGADOR = selecao.nome.strip()
                    partida.definir_recorde(selecao.obter_recorde())
                    partida.resetar()
                    iniciar_fade("partida")
                elif resultado == "voltar":
                    iniciar_fade("menu")

            # --- PARTIDA ---
            elif estado == "partida":
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        partida.jogador.pular()
                    elif evento.key == pygame.K_ESCAPE:
                        partida.pausado = True
                        estado = "pausa"
                    elif evento.key == pygame.K_h:
                        partida.debug_hitbox = not partida.debug_hitbox

            # --- PAUSA ---
            elif estado == "pausa":
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        partida.pausado = False
                        estado = "partida"

                resultado = partida.tratar_eventos_pausa(evento)
                if resultado == "continuar":
                    partida.pausado = False
                    estado = "partida"
                elif resultado == "reiniciar":
                    partida.resetar()
                    estado = "partida"
                elif resultado == "menu":
                    partida.pausado = False
                    estado = "menu"
                elif resultado == "sair":
                    rodando = False

            # --- GAME OVER ---
            elif estado == "gameover":
                resultado = partida.tratar_eventos_gameover(evento)
                if resultado == "reiniciar":
                    partida.resetar()
                    iniciar_fade("partida")
                elif resultado == "menu":
                    partida.pausado = False
                    iniciar_fade("menu")
                elif resultado == "sair":
                    rodando = False

        # ====================================================
        # ATUALIZACAO
        # ====================================================

        if estado == "partida":
            partida.atualizar()
            if partida.game_over:
                estado = "gameover"

                # ================================================
                # SALVAR RESULTADO NO DJANGO (uma unica vez)
                # ================================================

                # Envia so quando ainda nao foi enviado nesta partida.
                # Os valores sao os mesmos do jogo (partida.pontos
                # guarda as moedas coletadas).
                if not partida.resultado_enviado:
                    partida.resultado_enviado = True

                    # Executa o envio em segundo plano (thread)
                    # para o jogo nao travar se o servidor
                    # demorar ou estiver desligado.
                    threading.Thread(
                        target=salvar_resultado,
                        args=(
                            partida.pontos,
                            partida.pontos,
                        ),
                        kwargs={
                            "nome": api.NOME_JOGADOR,
                        },
                        daemon=True
                    ).start()

        # ====================================================
        # ATUALIZAR FADE
        # ====================================================

        if fade_estado == "escurecendo":
            fade_alpha = min(255, fade_alpha + FADE_VELOCIDADE)
            if fade_alpha >= 255:
                estado = fade_destino
                fade_estado = "clareando"

        elif fade_estado == "clareando":
            fade_alpha = max(0, fade_alpha - FADE_VELOCIDADE)
            if fade_alpha <= 0:
                fade_estado = "nenhum"
                fade_destino = None

        # ====================================================
        # CONTROLE DE MUSICAS
        # ====================================================

        if estado != estado_anterior:

            if estado == "menu":

                # Voltou da tela de selecao de jogador:
                # deixa a musica continuar tocando.
                if estado_anterior == "selecionar":

                    if not pygame.mixer.music.get_busy():

                        pygame.mixer.music.load(caminho_menu)
                        pygame.mixer.music.play(-1)

                else:

                    pygame.mixer.music.stop()
                    if tem_musica_menu:
                        pygame.mixer.music.load(caminho_menu)
                        pygame.mixer.music.play(-1)

            elif estado == "selecionar":

                # A musica do menu continua tocando sem recomecar.
                # So carrega do zero caso por algum motivo
                # nao esteja tocando.
                if not pygame.mixer.music.get_busy():

                    pygame.mixer.music.load(caminho_menu)
                    pygame.mixer.music.play(-1)

            elif estado == "partida":
                if estado_anterior == "pausa":
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.stop()
                    if tem_trilha:
                        pygame.mixer.music.load(caminho_trilha)
                        pygame.mixer.music.play(-1)

            elif estado == "pausa":
                pygame.mixer.music.pause()

            elif estado == "gameover":
                pygame.mixer.music.stop()
                if som_perdeu:
                    som_perdeu.play()

            estado_anterior = estado

        # ====================================================
        # DESENHO
        # ====================================================

        if estado == "menu":
            menu.desenhar()
        elif estado == "selecionar":
            selecao.desenhar()
        elif estado in ("partida", "pausa", "gameover"):
            partida.desenhar()

        # Desenha o fade por cima de tudo
        if fade_alpha > 0:
            fade_surface.set_alpha(fade_alpha)
            tela.blit(fade_surface, (0, 0))

        pygame.display.flip()
        relogio.tick(FPS)

    # ========================================================
    # FINALIZACAO
    # ========================================================

    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
