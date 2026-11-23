# Software FJ – Sistema integral de gestión de Clientes, Servicios y Reservas

Proyecto de la **Fase 4 – Prácticas simuladas** del curso **Programación (213023)**, UNAD.
Aplicación orientada a objetos en Python, **sin base de datos**, con manejo avanzado de excepciones.

## Requisitos
- Python 3.9 o superior (solo librería estándar, no hay dependencias que instalar).

## Ejecución
```bash
python main.py
```
El programa simula 26 operaciones (válidas e inválidas) y escribe todos los eventos y errores en `logs/software_fj.log`.

## Estructura
| Archivo | Contenido |
|---|---|
| `entidades.py` | Clase abstracta `EntidadBase` (id único y `describir()`) |
| `cliente.py` | `Cliente` con encapsulación y validaciones estrictas |
| `servicios.py` | Clase abstracta `Servicio` + `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` |
| `reserva.py` | `Reserva` y `EstadoReserva` (confirmar, cancelar, procesar) |
| `excepciones.py` | Jerarquía de excepciones personalizadas |
| `gestor.py` | `GestorSistema`: listas internas y ejecución segura de operaciones |
| `logger_config.py` | Configuración del archivo de logs |
| `main.py` | Simulación de operaciones |

## Conceptos aplicados
- **Abstracción:** `EntidadBase` y `Servicio` (clases abstractas con `ABC`).
- **Herencia:** `Cliente`, `Servicio` y `Reserva` heredan de `EntidadBase`; tres servicios heredan de `Servicio`.
- **Polimorfismo:** `calcular_costo()`, `validar_parametros()` y `describir()` sobrescritos en cada servicio.
- **Encapsulación:** atributos privados y propiedades con validación.
- **Sobrecarga:** `calcular_costo_total()` con parámetros opcionales y `aplicar_descuento()` con `singledispatchmethod` (número o cupón).
- **Excepciones:** personalizadas, `try/except`, `try/except/else`, `try/except/finally` y encadenamiento con `raise ... from`.

## Integrantes
Completar con los nombres del grupo.
