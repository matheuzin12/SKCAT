"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path

from jogo import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # API usada pelo jogo SKCAT para salvar o resultado da partida
    path('api/partidas/', views.registrar_partida, name='registrar_partida'),

    # API usada pela tela de selecao de jogador para listar jogadores
    path('api/jogadores/', views.listar_jogadores, name='listar_jogadores'),
]
