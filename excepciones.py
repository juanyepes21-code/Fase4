"""
excepciones.py
==============
Jerarquía de excepciones personalizadas del sistema Software FJ.

Todas las excepciones heredan de SoftwareFJError, de modo que el sistema
puede capturar cualquier error propio con un único "except SoftwareFJError"
y, al mismo tiempo, distinguir cada caso con excepciones más específicas.
"""


class SoftwareFJError(Exception):
    """Excepción base de la aplicación: de ella heredan todas las demás."""


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando falta un parámetro obligatorio (None, vacío o ausente)."""


class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos de un cliente no cumplen las validaciones."""


class ServicioInvalidoError(SoftwareFJError):
    """Se lanza cuando los parámetros de un servicio (o su creación) son inválidos."""


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta reservar un servicio marcado como no disponible."""


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando una reserva no puede crearse o procesarse correctamente."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta una transición de estado no permitida
    (por ejemplo, cancelar una reserva que ya fue procesada)."""


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos produce valores incoherentes
    (costos negativos, descuentos excesivos, impuestos fuera de rango, etc.)."""
