"""
entidades.py
============
Clase abstracta base que representa las entidades generales del sistema
(clientes, servicios y reservas).
"""

from abc import ABC, abstractmethod


class EntidadBase(ABC):
    """Entidad general del sistema.

    Aporta un identificador único con prefijo (CLI-001, SRV-001, RES-001...)
    y obliga a las clases hijas a implementar el método describir().
    """

    # Prefijo del identificador; cada clase hija lo sobrescribe
    PREFIJO = "ENT"
    # Contadores por prefijo, compartidos por todas las entidades
    _contadores: dict = {}

    def __init__(self) -> None:
        # Se incrementa el contador correspondiente al prefijo de la clase hija
        numero = EntidadBase._contadores.get(self.PREFIJO, 0) + 1
        EntidadBase._contadores[self.PREFIJO] = numero
        # Atributo "privado" por convención (encapsulación)
        self._id = f"{self.PREFIJO}-{numero:03d}"

    @property
    def id(self) -> str:
        """Identificador único de solo lectura."""
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad (polimórfico)."""

    def __str__(self) -> str:
        # Por defecto, imprimir una entidad muestra su descripción
        return self.describir()
