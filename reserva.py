"""
reserva.py
==========
Clase Reserva: integra cliente, servicio, duración y estado.
Implementa confirmación, cancelación y procesamiento con manejo de
excepciones (try/except/else/finally y encadenamiento con "raise ... from").
"""

from enum import Enum

from cliente import Cliente
from entidades import EntidadBase
from excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)
from logger_config import obtener_logger
from servicios import Servicio

logger = obtener_logger()


class EstadoReserva(Enum):
    """Estados posibles de una reserva."""
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    PROCESADA = "Procesada"


class Reserva(EntidadBase):
    """Reserva de un servicio por parte de un cliente."""

    PREFIJO = "RES"

    def __init__(self, cliente, servicio, horas):
        # 1) El cliente y el servicio deben ser del tipo correcto
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un servicio válido.")

        # 2) El servicio debe estar disponible
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible.")

        # 3) La duración se valida con las reglas propias del servicio.
        #    Si falla, se ENCADENA la excepción original con "from e":
        #    se conserva la causa raíz y se expone un error de más alto nivel.
        try:
            servicio.validar_parametros(horas)
        except ServicioInvalidoError as e:
            raise ReservaInvalidaError(
                f"No se pudo crear la reserva de '{servicio.nombre}': {e}"
            ) from e

        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = EstadoReserva.PENDIENTE
        self._costo_final = None
        super().__init__()

    # ------------------------ propiedades (encapsulación) --------------------
    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def horas(self) -> float:
        return self._horas

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_final(self):
        return self._costo_final

    # ------------------------------ operaciones ------------------------------
    def confirmar(self) -> None:
        """PENDIENTE -> CONFIRMADA."""
        if self._estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"{self.id}: solo se puede confirmar una reserva pendiente (estado actual: {self._estado.value})."
            )
        self._estado = EstadoReserva.CONFIRMADA
        logger.info("Reserva %s confirmada.", self.id)

    def cancelar(self) -> None:
        """PENDIENTE o CONFIRMADA -> CANCELADA."""
        if self._estado in (EstadoReserva.PROCESADA, EstadoReserva.CANCELADA):
            raise OperacionNoPermitidaError(
                f"{self.id}: no se puede cancelar una reserva en estado {self._estado.value}."
            )
        self._estado = EstadoReserva.CANCELADA
        logger.info("Reserva %s cancelada.", self.id)

    def procesar(self, impuesto=None, descuento=None) -> float:
        """CONFIRMADA -> PROCESADA, calculando el costo final.

        Usa try/except/else/finally:
          - try:     calcula el costo total del servicio.
          - except:  traduce errores de cálculo a ReservaInvalidaError (encadenada).
          - else:    solo si NO hubo error, actualiza el estado y guarda el costo.
          - finally: siempre deja constancia en el log del intento realizado.
        """
        if self._estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"{self.id}: solo se puede procesar una reserva confirmada (estado actual: {self._estado.value})."
            )
        try:
            costo = self._servicio.calcular_costo_total(self._horas, impuesto, descuento)
        except (ServicioInvalidoError, CalculoInconsistenteError) as e:
            raise ReservaInvalidaError(f"{self.id}: error al calcular el costo de la reserva: {e}") from e
        else:
            self._costo_final = costo
            self._estado = EstadoReserva.PROCESADA
            logger.info("Reserva %s procesada. Costo final: $%s", self.id, f"{costo:,.2f}")
            return costo
        finally:
            logger.debug("Intento de procesamiento de %s finalizado.", self.id)

    # ------------------------------ polimorfismo -----------------------------
    def describir(self) -> str:
        costo = f"${self._costo_final:,.2f}" if self._costo_final is not None else "sin calcular"
        return (f"[{self.id}] {self._cliente.nombre} -> {self._servicio.nombre} | "
                f"{self._horas} h | Estado: {self._estado.value} | Costo: {costo}")
