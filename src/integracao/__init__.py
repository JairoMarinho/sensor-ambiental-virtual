"""Componentes compartilhados pela coleta MQTT e pelo dashboard."""

from .leituras import RepositorioLeituras, normalizar_leitura

__all__ = ["RepositorioLeituras", "normalizar_leitura"]
