"""
main.py
=======
Simulación de Software FJ: ejecuta más de 10 operaciones completas
(válidas e inválidas) para demostrar que el sistema NO se detiene ante
errores y que todos quedan registrados en logs/software_fj.log.

Ejecución:  python main.py
"""

from gestor import GestorSistema
from logger_config import ARCHIVO_LOG, obtener_logger

logger = obtener_logger()


def mostrar(numero: int, titulo: str, resultado) -> None:
    """Imprime el resultado de una operación de la simulación."""
    ok, valor = resultado
    if ok:
        detalle = valor.describir() if hasattr(valor, "describir") else (valor if valor is not None else "")
        print(f"{numero:02d}. [OK]    {titulo}  {detalle}")
    else:
        print(f"{numero:02d}. [ERROR] {titulo}  ->  {type(valor).__name__}: {valor}")


def main() -> None:
    logger.info("=== INICIO DE LA SIMULACIÓN DE SOFTWARE FJ ===")
    sistema = GestorSistema()
    print("=" * 78)
    print(" SOFTWARE FJ - Sistema integral de clientes, servicios y reservas")
    print("=" * 78)

    # ------------------------------- CLIENTES -------------------------------
    r1 = sistema.registrar_cliente(nombre="ana maría gómez", documento="1037456123",
                                   correo="ana.gomez@correo.com", telefono="3105551234")
    mostrar(1, "Cliente válido (Ana)", r1)

    mostrar(2, "Cliente con correo inválido", sistema.registrar_cliente(
        nombre="Pedro Ruiz", documento="98765432", correo="pedro-correo.com", telefono="3001112233"))

    mostrar(3, "Cliente sin documento (parámetro faltante)", sistema.registrar_cliente(
        nombre="Luisa Torres", correo="luisa@correo.com", telefono="3201112233"))

    r4 = sistema.registrar_cliente(nombre="Carlos Mejía", documento="71654321",
                                   correo="carlos.mejia@correo.com", telefono="3159998877")
    mostrar(4, "Cliente válido (Carlos)", r4)

    # ------------------------------- SERVICIOS ------------------------------
    r5 = sistema.crear_servicio("sala", nombre="Sala Innovación", tarifa_hora=50000, capacidad=25)
    mostrar(5, "Servicio válido: sala", r5)

    r6 = sistema.crear_servicio("equipo", nombre="Portátil Pro", tarifa_hora=8000,
                                tipo_equipo="Portátil", incluye_seguro=True)
    mostrar(6, "Servicio válido: equipo", r6)

    mostrar(7, "Asesoría con nivel inválido", sistema.crear_servicio(
        "asesoria", nombre="Asesoría Cloud", tarifa_hora=70000, especialidad="Cloud", nivel="maestro"))

    r8 = sistema.crear_servicio("asesoria", nombre="Asesoría Seguridad", tarifa_hora=70000,
                                especialidad="Ciberseguridad", nivel="senior")
    mostrar(8, "Servicio válido: asesoría", r8)

    mostrar(9, "Tipo de servicio inexistente", sistema.crear_servicio("catering", nombre="Café", tarifa_hora=1000))

    r10 = sistema.crear_servicio("equipo", nombre="Proyector 4K", tarifa_hora=12000,
                                 tipo_equipo="Proyector", disponible=False)
    mostrar(10, "Servicio válido pero NO disponible", r10)

    # ---------------------- OBTENCIÓN DE IDS CREADOS ------------------------
    ana, carlos = r1[1], r4[1]
    sala, equipo, asesoria, proyector = r5[1], r6[1], r8[1], r10[1]

    # -------------------------------- RESERVAS ------------------------------
    rr1 = sistema.crear_reserva(ana.id, sala.id, 3)
    mostrar(11, "Reserva exitosa Ana -> Sala (3 h)", rr1)

    mostrar(12, "Reserva con duración excesiva (20 h)", sistema.crear_reserva(ana.id, sala.id, 20))
    mostrar(13, "Reserva con cliente inexistente", sistema.crear_reserva("CLI-999", sala.id, 2))
    mostrar(14, "Reserva de servicio no disponible", sistema.crear_reserva(carlos.id, proyector.id, 4))
    mostrar(15, "Reserva de asesoría con 2.3 h (no múltiplo de 0.5)", sistema.crear_reserva(carlos.id, asesoria.id, 2.3))

    rr2 = sistema.crear_reserva(carlos.id, asesoria.id, 2.5)
    mostrar(16, "Reserva exitosa Carlos -> Asesoría (2.5 h)", rr2)

    rr3 = sistema.crear_reserva(carlos.id, equipo.id, 24)
    mostrar(17, "Reserva exitosa Carlos -> Equipo (24 h)", rr3)

    # ---------------- CONFIRMACIÓN, PROCESAMIENTO Y CANCELACIÓN ---------------
    id1, id2, id3 = rr1[1].id, rr2[1].id, rr3[1].id

    mostrar(18, "Procesar reserva SIN confirmar (no permitido)", sistema.procesar_reserva(id1))
    mostrar(19, "Confirmar reserva de Ana", sistema.confirmar_reserva(id1))
    mostrar(20, "Procesar con IVA 19 % y cupón FJ10", sistema.procesar_reserva(id1, descuento="FJ10"))
    mostrar(21, "Cancelar reserva ya procesada (no permitido)", sistema.cancelar_reserva(id1))

    mostrar(22, "Confirmar reserva de asesoría", sistema.confirmar_reserva(id2))
    mostrar(23, "Procesar con descuento excesivo (80 %)", sistema.procesar_reserva(id2, descuento=80))
    mostrar(24, "Procesar con IVA 5 % y 10 % de descuento", sistema.procesar_reserva(id2, impuesto=0.05, descuento=10))

    mostrar(25, "Cancelar reserva de equipo (pendiente)", sistema.cancelar_reserva(id3))
    mostrar(26, "Confirmar reserva ya cancelada (no permitido)", sistema.confirmar_reserva(id3))

    # --------------------------------- RESUMEN ------------------------------
    print("\n" + "-" * 78)
    print(" ESTADO FINAL DEL SISTEMA")
    print("-" * 78)
    print(f" Clientes registrados : {len(sistema.clientes)}")
    for c in sistema.clientes:
        print("   ", c.describir())
    print(f" Servicios creados    : {len(sistema.servicios)}")
    for s in sistema.servicios:
        print("   ", s.describir())
    print(f" Reservas             : {len(sistema.reservas)}")
    for r in sistema.reservas:
        print("   ", r.describir())
    print(f"\n Operaciones exitosas : {sistema.exitos}")
    print(f" Operaciones con error: {sistema.errores} (todas registradas en el log)")
    print(f" Archivo de logs      : {ARCHIVO_LOG}")
    print("\n El sistema terminó SIN interrupciones pese a los errores simulados.")

    logger.info("=== FIN DE LA SIMULACIÓN: %s éxitos, %s errores ===", sistema.exitos, sistema.errores)


if __name__ == "__main__":
    main()
