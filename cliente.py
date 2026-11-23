"""
cliente.py
==========
Clase Cliente con encapsulación de datos personales y validaciones estrictas.
"""

import re

from entidades import EntidadBase
from excepciones import ClienteInvalidoError, ParametroFaltanteError

# Solo letras (con tildes y ñ) y espacios
_PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$")
# Estructura básica de un correo: usuario@dominio.ext
_PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


class Cliente(EntidadBase):
    """Cliente de Software FJ.

    Los datos personales se guardan en atributos privados y solo se
    modifican mediante propiedades que validan cada valor.
    """

    PREFIJO = "CLI"

    def __init__(self, nombre=None, documento=None, correo=None, telefono=None):
        # Se validan todos los datos ANTES de generar el identificador,
        # así un cliente inválido nunca consume un número de ID.
        self._nombre = self._validar_nombre(nombre)
        self._documento = self._validar_documento(documento)
        self._correo = self._validar_correo(correo)
        self._telefono = self._validar_telefono(telefono)
        super().__init__()

    # ----------------------------- validaciones -----------------------------
    @staticmethod
    def _requerido(valor, campo: str):
        """Verifica que el parámetro exista y no sea una cadena vacía."""
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(f"Falta el parámetro obligatorio: '{campo}'.")
        return valor

    @classmethod
    def _validar_nombre(cls, nombre) -> str:
        nombre = cls._requerido(nombre, "nombre")
        if not isinstance(nombre, str):
            raise ClienteInvalidoError("El nombre debe ser texto.")
        nombre = " ".join(nombre.split())  # limpia espacios repetidos
        if len(nombre) < 3 or not _PATRON_NOMBRE.match(nombre):
            raise ClienteInvalidoError(
                f"Nombre inválido '{nombre}': mínimo 3 letras, sin números ni símbolos."
            )
        return nombre.title()

    @classmethod
    def _validar_documento(cls, documento) -> str:
        documento = str(cls._requerido(documento, "documento")).strip()
        if not documento.isdigit() or not 5 <= len(documento) <= 12:
            raise ClienteInvalidoError(
                f"Documento inválido '{documento}': solo dígitos, entre 5 y 12."
            )
        return documento

    @classmethod
    def _validar_correo(cls, correo) -> str:
        correo = str(cls._requerido(correo, "correo")).strip().lower()
        if not _PATRON_CORREO.match(correo):
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{correo}'.")
        return correo

    @classmethod
    def _validar_telefono(cls, telefono) -> str:
        telefono = str(cls._requerido(telefono, "telefono")).strip()
        if not telefono.isdigit() or not 7 <= len(telefono) <= 10:
            raise ClienteInvalidoError(
                f"Teléfono inválido '{telefono}': solo dígitos, entre 7 y 10."
            )
        return telefono

    # ------------------------ propiedades (encapsulación) --------------------
    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def documento(self) -> str:
        return self._documento

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, nuevo: str) -> None:
        # Al cambiar el correo se vuelve a validar
        self._correo = self._validar_correo(nuevo)

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, nuevo: str) -> None:
        self._telefono = self._validar_telefono(nuevo)

    # ------------------------------ polimorfismo -----------------------------
    def describir(self) -> str:
        return f"[{self.id}] {self._nombre} | Doc: {self._documento} | {self._correo} | Tel: {self._telefono}"
