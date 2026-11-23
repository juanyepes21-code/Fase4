"""
gestor.py
=========
GestorSistema: administra las listas internas de clientes, servicios y
reservas (sin base de datos) y garantiza que NINGÚN error detenga la
aplicación: cada operación captura sus excepciones, las registra en el
log y devuelve el control al programa.
"""

from cliente import Cliente
from excepciones import (
    ClienteInvalidoError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    SoftwareFJError,
)
from logger_config import obtener_logger
from reserva import Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala

logger = obtener_logger()


class GestorSistema:
    """Fachada del sistema: registra, reserva y consulta."""

    # Fábrica de servicios: asocia el tipo de servicio con su clase
    TIPOS_SERVICIO = {
        "sala": ReservaSala,
        "equipo": AlquilerEquipo,
        "asesoria": AsesoriaEspecializada,
    }

    def __init__(self) -> None:
        # Listas internas: reemplazan a una base de datos
        self._clientes: list = []
        self._servicios: list = []
        self._reservas: list = []
        self.exitos = 0
        self.errores = 0

    # ------------------------------------------------------------------
    # Ejecutor central: try/except/else/finally para toda operación
    # ------------------------------------------------------------------
    def _ejecutar(self, descripcion: str, funcion, *args, **kwargs):
        """Ejecuta una operación de forma segura y devuelve (ok, resultado).

        - except SoftwareFJError: error controlado propio del dominio.
        - except Exception:       error inesperado; también se registra y NO detiene el programa.
        - else:                   la operación terminó bien.
        - finally:                se deja registro del fin de la operación.
        """
        try:
            resultado = funcion(*args, **kwargs)
        except SoftwareFJError as e:
            self.errores += 1
            # Si el error fue encadenado se registra también su causa raíz
            causa = f" | causa: {type(e.__cause__).__name__}: {e.__cause__}" if e.__cause__ else ""
            logger.error("%s FALLÓ -> %s: %s%s", descripcion, type(e).__name__, e, causa)
            return False, e
        except Exception as e:  # último recurso: errores no previstos
            self.errores += 1
            logger.exception("%s FALLÓ con error inesperado: %s", descripcion, e)
            return False, e
        else:
            self.exitos += 1
            logger.info("%s OK.", descripcion)
            return True, resultado
        finally:
            logger.debug("Fin de la operación: %s", descripcion)

    # ------------------------------ búsquedas -------------------------------
    @staticmethod
    def _buscar(lista: list, identificador: str, nombre_entidad: str):
        for elemento in lista:
            if elemento.id == identificador:
                return elemento
        raise ReservaInvalidaError(f"{nombre_entidad} '{identificador}' no existe.")

    # ------------------------------ clientes --------------------------------
    def registrar_cliente(self, **datos):
        def _registrar():
            cliente = Cliente(**datos)
            # No se permiten documentos duplicados
            if any(c.documento == cliente.documento for c in self._clientes):
                raise ClienteInvalidoError(
                    f"Ya existe un cliente con el documento {cliente.documento}."
                )
            self._clientes.append(cliente)
            return cliente
        return self._ejecutar(f"Registro de cliente {datos.get('nombre')!r}", _registrar)

    # ------------------------------ servicios -------------------------------
    def crear_servicio(self, tipo: str, **parametros):
        def _crear():
            clase = self.TIPOS_SERVICIO.get(str(tipo).lower())
            if clase is None:
                raise ServicioInvalidoError(
                    f"Tipo de servicio desconocido '{tipo}'. Opciones: {', '.join(self.TIPOS_SERVICIO)}."
                )
            try:
                servicio = clase(**parametros)
            except TypeError as e:
                # Parámetro desconocido en la creación: se encadena el error original
                raise ServicioInvalidoError(f"Parámetros incorrectos para el servicio '{tipo}': {e}") from e
            self._servicios.append(servicio)
            return servicio
        return self._ejecutar(f"Creación de servicio tipo '{tipo}'", _crear)

    # ------------------------------ reservas --------------------------------
    def crear_reserva(self, id_cliente: str, id_servicio: str, horas):
        def _crear():
            cliente = self._buscar(self._clientes, id_cliente, "Cliente")
            servicio = self._buscar(self._servicios, id_servicio, "Servicio")
            reserva = Reserva(cliente, servicio, horas)
            self._reservas.append(reserva)
            return reserva
        return self._ejecutar(f"Creación de reserva ({id_cliente}, {id_servicio}, {horas} h)", _crear)

    def confirmar_reserva(self, id_reserva: str):
        return self._ejecutar(
            f"Confirmación de {id_reserva}",
            lambda: self._buscar(self._reservas, id_reserva, "Reserva").confirmar(),
        )

    def cancelar_reserva(self, id_reserva: str):
        return self._ejecutar(
            f"Cancelación de {id_reserva}",
            lambda: self._buscar(self._reservas, id_reserva, "Reserva").cancelar(),
        )

    def procesar_reserva(self, id_reserva: str, impuesto=None, descuento=None):
        return self._ejecutar(
            f"Procesamiento de {id_reserva}",
            lambda: self._buscar(self._reservas, id_reserva, "Reserva").procesar(impuesto, descuento),
        )

    # ------------------------------ consultas -------------------------------
    @property
    def clientes(self) -> list:
        return list(self._clientes)  # copia: protege la lista interna

    @property
    def servicios(self) -> list:
        return list(self._servicios)

    @property
    def reservas(self) -> list:
        return list(self._reservas)
