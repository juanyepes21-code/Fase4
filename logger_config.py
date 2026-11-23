"""
logger_config.py
================
Configuración centralizada del archivo de logs.

Todos los errores y eventos relevantes del sistema se escriben en
logs/software_fj.log. Es el ÚNICO uso de archivos que hace la aplicación
(no se utiliza ninguna base de datos).
"""

import logging
import os

# Carpeta donde se guardará el archivo de logs (junto a este módulo)
CARPETA_LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
# Ruta completa del archivo de logs
ARCHIVO_LOG = os.path.join(CARPETA_LOGS, "software_fj.log")


def obtener_logger(nombre: str = "software_fj") -> logging.Logger:
    """Devuelve un logger configurado para escribir en el archivo de logs.

    Si el logger ya fue configurado se reutiliza, evitando mensajes duplicados.
    """
    logger = logging.getLogger(nombre)
    if logger.handlers:  # ya estaba configurado: se reutiliza
        return logger

    logger.setLevel(logging.DEBUG)  # se registra todo, desde DEBUG hacia arriba
    logger.propagate = False  # evita duplicar mensajes en el logger raíz

    # Se crea la carpeta de logs si todavía no existe
    os.makedirs(CARPETA_LOGS, exist_ok=True)

    # Formato: fecha-hora | nivel | módulo | mensaje
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Manejador que escribe en el archivo (modo "a": agrega al final)
    manejador = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
    manejador.setFormatter(formato)
    logger.addHandler(manejador)
    return logger
