"""
interfaces.py

Classes de interface do jogo.
- Texto
- Botao (com transparencia, fonte Fraktur e som de clique)
"""

import pygame
import os


# Caminho da fonte Fraktur
_pasta_assets = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets"
)
FONTE_FRAKTUR = os.path.join(_pasta_assets, "UnifrakturCook-Bold.ttf")

# Som de clicar botao
_som_clique = None


def _carregar_som_clique():
    """Carrega o som de clique uma unica vez."""
    global _som_clique
    if _som_clique is None:
        caminho = os.path.join(_pasta_assets, "sons", "clicarbotao.mp3")
        if os.path.exists(caminho):
            _som_clique = pygame.mixer.Sound(caminho)


def _tocar_som_clique():
    """Toca o som de clique se disponivel."""
    _carregar_som_clique()
    if _som_clique:
        _som_clique.play()


def _carregar_fonte(tamanho, caminho_fonte=None):
    """Carrega uma fonte .ttf ou usa a padrao do pygame."""
    if caminho_fonte and os.path.exists(caminho_fonte):
        return pygame.font.Font(caminho_fonte, tamanho)
    return pygame.font.SysFont(None, tamanho)


# ============================================================
# CAMINHO DE IMAGENS DE TELA
# ============================================================

def _caminho_tela(nome_arquivo):
    """
    Encontra uma imagem de tela independente da pasta.

    Procura primeiro em:
        assets/telas/<nome_arquivo>

    Se nao achar, procura em:
        assets/<nome_arquivo>

    Retorna o caminho completo, ou None se nao existir.
    """
    pasta_projeto = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    # Primeira opcao: assets/telas/
    caminho = os.path.join(
        pasta_projeto,
        "assets",
        "telas",
        nome_arquivo
    )

    if os.path.exists(caminho):
        return caminho

    # Segunda opcao: assets/
    caminho = os.path.join(
        pasta_projeto,
        "assets",
        nome_arquivo
    )

    if os.path.exists(caminho):
        return caminho

    return None


# ============================================================
# ICONE
# ============================================================

def _carregar_icone(tamanho):
    """
    Carrega assets/icone.png redimensionado,
    mantendo a proporcao (imagem quadrada).

    Retorna uma Surface, ou None se o arquivo nao existir.
    """
    caminho = os.path.join(_pasta_assets, "icone.png")

    if not os.path.exists(caminho):
        return None

    imagem = pygame.image.load(caminho).convert_alpha()

    return pygame.transform.smoothscale(
        imagem,
        (tamanho, tamanho)
    )


# ============================================================
# TEXTO
# ============================================================

class Texto:
    """Classe para exibir textos na tela, com opcional caixa de fundo."""

    def __init__(self, texto, x, y, cor=(255, 255, 255),
                 tamanho=36, nome_fonte=None,
                 caixa=False, cor_caixa=(0, 0, 0),
                 opacidade_caixa=180, margem=20):
        self.texto = texto
        self.x = x
        self.y = y
        self.cor = cor
        self.tamanho = tamanho
        self.caixa = caixa
        self.cor_caixa = cor_caixa
        self.opacidade_caixa = opacidade_caixa
        self.margem = margem
        self.fonte = _carregar_fonte(tamanho, nome_fonte)
        self._atualizar_imagem()

    def _atualizar_imagem(self):
        self.imagem = self.fonte.render(self.texto, True, self.cor)
        self.rect = self.imagem.get_rect(center=(self.x, self.y))

    def atualizar_texto(self, novo_texto):
        self.texto = novo_texto
        self._atualizar_imagem()

    def desenhar(self, tela):
        if self.caixa:
            # Cria uma surface semitransparente para a caixa
            caixa_largura = self.imagem.get_width() + self.margem * 2
            caixa_altura = self.imagem.get_height() + self.margem * 2
            caixa_rect = pygame.Rect(
                self.rect.centerx - caixa_largura // 2,
                self.rect.centery - caixa_altura // 2,
                caixa_largura,
                caixa_altura
            )
            fundo = pygame.Surface(
                (caixa_largura, caixa_altura),
                pygame.SRCALPHA
            )
            cor = (*self.cor_caixa, self.opacidade_caixa)
            pygame.draw.rect(
                fundo, cor,
                (0, 0, caixa_largura, caixa_altura),
                border_radius=8
            )
            pygame.draw.rect(
                fundo, (255, 255, 255, self.opacidade_caixa),
                (0, 0, caixa_largura, caixa_altura),
                2, border_radius=8
            )
            tela.blit(fundo, caixa_rect)

        tela.blit(self.imagem, self.rect)


# ============================================================
# BOTAO
# ============================================================

class Botao:
    """Botao clicavel com fundo semitransparente, estilo Fraktur e som."""

    def __init__(self, texto, x, y, largura=200, altura=50,
                 cor_fundo=(70, 70, 200), cor_texto=(255, 255, 255),
                 cor_hover=(100, 100, 255), tamanho_fonte=30,
                 opacidade=150, caminho_fonte=None):
        self.texto = texto
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.cor_fundo = cor_fundo
        self.cor_texto = cor_texto
        self.cor_hover = cor_hover
        self.opacidade = opacidade

        self.rect = pygame.Rect(
            x - largura // 2,
            y - altura // 2,
            largura,
            altura
        )

        fonte_caminho = caminho_fonte if caminho_fonte else FONTE_FRAKTUR
        self.fonte = _carregar_fonte(tamanho_fonte, fonte_caminho)

        self.imagem_texto = self.fonte.render(texto, True, cor_texto)
        self.rect_texto = self.imagem_texto.get_rect(
            center=self.rect.center
        )

    def desenhar(self, tela):
        """Desenha o botao com fundo semitransparente."""
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            cor = self.cor_hover
        else:
            cor = self.cor_fundo

        fundo = pygame.Surface(
            (self.largura, self.altura),
            pygame.SRCALPHA
        )
        cor_com_alpha = (*cor, self.opacidade)
        pygame.draw.rect(
            fundo, cor_com_alpha,
            (0, 0, self.largura, self.altura),
            border_radius=8
        )
        pygame.draw.rect(
            fundo, (255, 255, 255, self.opacidade),
            (0, 0, self.largura, self.altura),
            2, border_radius=8
        )

        tela.blit(fundo, self.rect)
        tela.blit(self.imagem_texto, self.rect_texto)

    def clicou(self, evento):
        """Verifica se o botao foi clicado. Toca som ao clicar."""
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if self.rect.collidepoint(evento.pos):
                    _tocar_som_clique()
                    return True
        return False
