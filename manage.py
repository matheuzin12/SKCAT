#!/usr/bin/env python
"""
manage.py (raiz do projeto)

Ponto de entrada do Django na pasta raiz do SKCAT,
para que TODOS os comandos funcionem direto daqui:

    python manage.py runserver
    python manage.py createsuperuser
    python manage.py migrate
    python manage.py shell

O projeto Django fica na pasta backend/, e este arquivo
apenas aponta para ele.
"""

import os
import sys

if __name__ == '__main__':
    # Pasta atual (raiz do SKCAT)
    raiz = os.path.dirname(os.path.abspath(__file__))

    # Pasta backend/ (onde fica o app "jogo")
    pasta_backend = os.path.join(raiz, 'backend')

    # Pasta backend/config (onde fica o modulo config.settings)
    pasta_config = os.path.join(pasta_backend, 'config')

    # Adiciona os caminhos ao Python
    for caminho in (raiz, pasta_backend, pasta_config):
        if caminho not in sys.path:
            sys.path.insert(0, caminho)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)