#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # Esta pasta (backend/) ja vem no caminho do Python
    # (onde fica o app "jogo").
    #
    # Falta adicionar a subpasta config/ para o Django achar
    # o modulo config.settings.
    pasta_backend = os.path.dirname(os.path.abspath(__file__))
    pasta_config = os.path.join(pasta_backend, 'config')

    if pasta_config not in sys.path:
        sys.path.insert(0, pasta_config)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()