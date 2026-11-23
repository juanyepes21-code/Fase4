"""
servicios.py
============
Clase abstracta Servicio y tres servicios especializados:
  - ReservaSala
  - AlquilerEquipo
  - AsesoriaEspecializada

Demuestra abstracción, herencia, polimorfismo (métodos sobrescritos) y
sobrecarga de métodos (por parámetros opcionales y por tipo de argumento).
"""

from abc import ABC, abstractmethod
from functools import singledispatchmethod

from entidades import EntidadBase
from excepciones import (
    CalculoInconsistenteError,
    ParametroFaltanteError,
    ServicioInvalidoError,
)


class Servicio(EntidadBase, ABC):
    """Clase abstracta de la que heredan todos los servicios de Software FJ."""

    PREFIJO = "SRV"
    IVA = 0.19            # impuesto por defecto (19 %)
    HORAS_MAX = 12        # duración máxima por reserva (se sobrescribe en hijas)
    DESCUENTO_MAX = 50.0  # descuento máximo permitido (en %)
    # Cupones de descuento disponibles (porcentaje)
    CUPONES = {"FJ10": 10.0, "FJ20": 20.0}

    def __init__(self, nombre=None, tarifa_hora=None, disponible: bool = True):
        # Validaciones comunes a todos los servicios
        if nombre is None or not str(nombre).strip():
            raise ParametroFaltanteError("Falta el parámetro obligatorio: 'nombre' del servicio.")
        if tarifa_hora is None:
            raise ParametroFaltanteError("Falta el parámetro obligatorio: 'tarifa_hora'.")
        if isinstance(tarifa_hora, bool) or not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise ServicioInvalidoError(f"Tarifa por hora inválida: {tarifa_hora!r} (debe ser un número > 0).")
        self._nombre = str(nombre).strip()
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = bool(disponible)
        super().__init__()

    # ------------------------ propiedades (encapsulación) --------------------
    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        self._disponible = bool(valor)

    # --------------------- métodos abstractos (polimorfismo) -----------------
    @abstractmethod
    def calcular_costo(self, horas: float) -> float:
        """Costo base del servicio (sin impuestos ni descuentos)."""

    @abstractmethod
    def validar_parametros(self, horas: float) -> None:
        """Valida los parámetros de la reserva; lanza ServicioInvalidoError si fallan."""

    # describir() se hereda como abstracto de EntidadBase y cada hija lo implementa.

    # ---------------- validación compartida de la duración -------------------
    def _validar_horas_base(self, horas) -> None:
        """Validación común de la duración (la reutilizan las clases hijas)."""
        if horas is None:
            raise ParametroFaltanteError("Falta el parámetro obligatorio: 'horas'.")
        if isinstance(horas, bool) or not isinstance(horas, (int, float)):
            raise ServicioInvalidoError(f"La duración debe ser numérica, se recibió {horas!r}.")
        if horas <= 0:
            raise ServicioInvalidoError(f"La duración debe ser mayor que 0 (recibido: {horas}).")
        if horas > self.HORAS_MAX:
            raise ServicioInvalidoError(
                f"La duración {horas} h supera el máximo permitido de {self.HORAS_MAX} h para '{self._nombre}'."
            )

    # ------------------------- SOBRECARGA DE MÉTODOS ------------------------
    # 1) Sobrecarga por parámetros opcionales: impuesto y descuento son opcionales
    #    y producen distintas variantes de cálculo:
    #       calcular_costo_total(3)                      -> con IVA por defecto
    #       calcular_costo_total(3, impuesto=0)          -> sin impuesto
    #       calcular_costo_total(3, 0.05, 10)            -> IVA 5 % y 10 % de descuento
    #       calcular_costo_total(3, descuento="FJ20")    -> con cupón
    def calcular_costo_total(self, horas, impuesto=None, descuento=None) -> float:
        """Costo final = (costo base - descuento) + impuesto."""
        self.validar_parametros(horas)               # puede lanzar ServicioInvalidoError
        subtotal = self.calcular_costo(horas)
        if subtotal <= 0:
            raise CalculoInconsistenteError(f"El costo base calculado no es válido: {subtotal}.")
        if descuento is not None:
            subtotal = self.aplicar_descuento(descuento, subtotal)
        tasa = self.IVA if impuesto is None else impuesto
        if isinstance(tasa, bool) or not isinstance(tasa, (int, float)) or not 0 <= tasa <= 1:
            raise CalculoInconsistenteError(f"Tasa de impuesto fuera de rango (0 a 1): {tasa!r}.")
        return round(subtotal * (1 + tasa), 2)

    # 2) Sobrecarga por TIPO de argumento (singledispatchmethod):
    #    aplicar_descuento(10, valor)     -> porcentaje numérico
    #    aplicar_descuento(12.5, valor)   -> porcentaje numérico decimal
    #    aplicar_descuento("FJ10", valor) -> código de cupón
    @singledispatchmethod
    def aplicar_descuento(self, descuento, subtotal: float) -> float:
        raise CalculoInconsistenteError(
            f"Tipo de descuento no soportado: {type(descuento).__name__}."
        )

    @aplicar_descuento.register(int)
    @aplicar_descuento.register(float)
    def _descuento_porcentual(self, descuento, subtotal: float) -> float:
        if isinstance(descuento, bool) or not 0 <= descuento <= self.DESCUENTO_MAX:
            raise CalculoInconsistenteError(
                f"Descuento {descuento}% inválido (permitido: 0 a {self.DESCUENTO_MAX}%)."
            )
        return subtotal * (1 - descuento / 100)

    @aplicar_descuento.register(str)
    def _descuento_cupon(self, descuento, subtotal: float) -> float:
        codigo = descuento.strip().upper()
        if codigo not in self.CUPONES:
            raise CalculoInconsistenteError(f"Cupón de descuento inexistente: '{descuento}'.")
        return subtotal * (1 - self.CUPONES[codigo] / 100)


# =============================================================================
# Servicio especializado 1: reserva de salas
# =============================================================================
class ReservaSala(Servicio):
    """Reserva de salas de reuniones por hora."""

    HORAS_MAX = 10

    def __init__(self, nombre=None, tarifa_hora=None, capacidad=None, disponible: bool = True):
        if capacidad is None:
            raise ParametroFaltanteError("Falta el parámetro obligatorio: 'capacidad' de la sala.")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r} (entero > 0).")
        self._capacidad = capacidad
        super().__init__(nombre, tarifa_hora, disponible)

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def validar_parametros(self, horas) -> None:
        self._validar_horas_base(horas)

    def calcular_costo(self, horas: float) -> float:
        base = self._tarifa_hora * horas
        # Las salas grandes (más de 20 personas) tienen un recargo del 10 %
        return base * 1.10 if self._capacidad > 20 else base

    def describir(self) -> str:
        return (f"[{self.id}] Sala '{self._nombre}' | Capacidad: {self._capacidad} personas | "
                f"${self._tarifa_hora:,.0f}/h")


# =============================================================================
# Servicio especializado 2: alquiler de equipos
# =============================================================================
class AlquilerEquipo(Servicio):
    """Alquiler de equipos tecnológicos (portátiles, proyectores, etc.)."""

    HORAS_MAX = 72

    def __init__(self, nombre=None, tarifa_hora=None, tipo_equipo=None,
                 incluye_seguro: bool = False, disponible: bool = True):
        if tipo_equipo is None or not str(tipo_equipo).strip():
            raise ParametroFaltanteError("Falta el parámetro obligatorio: 'tipo_equipo'.")
        self._tipo_equipo = str(tipo_equipo).strip()
        self._incluye_seguro = bool(incluye_seguro)
        super().__init__(nombre, tarifa_hora, disponible)

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    def validar_parametros(self, horas) -> None:
        self._validar_horas_base(horas)

    def calcular_costo(self, horas: float) -> float:
        base = self._tarifa_hora * horas
        # El seguro opcional es un valor fijo de $15.000
        return base + 15000 if self._incluye_seguro else base

    def describir(self) -> str:
        seguro = "con seguro" if self._incluye_seguro else "sin seguro"
        return (f"[{self.id}] Equipo '{self._nombre}' ({self._tipo_equipo}) | {seguro} | "
                f"${self._tarifa_hora:,.0f}/h")


# =============================================================================
# Servicio especializado 3: asesorías especializadas
# =============================================================================
class AsesoriaEspecializada(Servicio):
    """Asesoría con un especialista; la tarifa depende del nivel."""

    HORAS_MAX = 8
    # Multiplicador de tarifa por nivel del asesor
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre=None, tarifa_hora=None, especialidad=None,
                 nivel: str = "junior", disponible: bool = True):
        if especialidad is None or not str(especialidad).strip():
            raise ParametroFaltanteError("Falta el parámetro obligatorio: 'especialidad'.")
        nivel_normalizado = str(nivel).strip().lower()
        if nivel_normalizado not in self.NIVELES:
            raise ServicioInvalidoError(
                f"Nivel de asesor inválido '{nivel}'. Opciones: {', '.join(self.NIVELES)}."
            )
        self._especialidad = str(especialidad).strip()
        self._nivel = nivel_normalizado
        super().__init__(nombre, tarifa_hora, disponible)

    @property
    def especialidad(self) -> str:
        return self._especialidad

    @property
    def nivel(self) -> str:
        return self._nivel

    def validar_parametros(self, horas) -> None:
        self._validar_horas_base(horas)
        # Las asesorías se agendan en bloques de media hora
        if (horas * 2) % 1 != 0:
            raise ServicioInvalidoError(
                f"Las asesorías se reservan en múltiplos de 0.5 h (recibido: {horas})."
            )

    def calcular_costo(self, horas: float) -> float:
        return self._tarifa_hora * self.NIVELES[self._nivel] * horas

    def describir(self) -> str:
        return (f"[{self.id}] Asesoría '{self._nombre}' ({self._especialidad}, nivel {self._nivel}) | "
                f"${self._tarifa_hora:,.0f}/h base")
