"""
Script de pruebas para sistema de rentas
Ubicación: test/test_rentas.py
Versión: 2.6 - Corregido: Prueba 6 ahora simula devolución con retraso sin vencer
"""

import sys
import os
from datetime import datetime, timedelta


ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)


from controllers.renta_controller import RentaController
from controllers.inventario_controller import InventarioController
from controllers.cliente_controller import ClienteController
from controllers.auth_controller import AuthController


# ============================================================
# MÉTODOS DE AUDITORÍA
# ============================================================

def registrar_prueba(nombre_prueba: str, resultado: bool, mensaje: str = ""):
    """
    Registra la ejecución de una prueba en el historial de auditoría.

    Args:
        nombre_prueba: Nombre de la prueba ejecutada
        resultado: True si pasó, False si falló
        mensaje: Mensaje adicional
    """
    auditoria = {
        'fecha': datetime.now(),
        'prueba': nombre_prueba,
        'resultado': 'PASÓ' if resultado else 'FALLÓ',
        'mensaje': mensaje
    }
    print(f"📊 AUDITORÍA: Prueba: {nombre_prueba} - Resultado: {'PASÓ' if resultado else 'FALLÓ'} - Mensaje: {mensaje}")
    return auditoria


# Variables globales para IDs de prueba
id_cliente_test = None
id_usuario_test = None
id_renta_test = None
codigo_disfraz_test = "RENTEST001"


def setup_datos_prueba():
    """Crea o reutiliza datos necesarios para las pruebas"""
    global id_cliente_test, id_usuario_test
   
    print("\n" + "="*60)
    print("SETUP: Creando datos de prueba")
    print("="*60 + "\n")
   
    # ===================== CLIENTE =====================
    cliente_ctrl = ClienteController()
    exito, msg, id_cliente_test, _ = cliente_ctrl.agregar_cliente(
        nombre="ClienteRenta",
        apellido="Test",
        telefono="+52 618 222 2222",
        forzar=True
    )
   
    if exito and id_cliente_test:
        print(f"Cliente: {msg} (ID: {id_cliente_test})")
        registrar_prueba("Setup - Cliente", True, f"Cliente creado con ID: {id_cliente_test}")
    else:
        # Si no se pudo crear (teléfono duplicado, etc.), intentar reutilizar
        print(f"Cliente: {msg} (intentando reutilizar)\n")
        try:
            cliente = cliente_ctrl.buscar_por_telefono("+52 618 222 2222")
            if cliente:
                id_cliente_test = cliente.id_cliente
                print(f"ℹ️ Cliente reutilizado: ID {id_cliente_test}\n")
                registrar_prueba("Setup - Cliente", True, f"Cliente reutilizado con ID: {id_cliente_test}")
            else:
                print("⚠️ No se encontró cliente por teléfono, id_cliente_test seguirá en None\n")
                registrar_prueba("Setup - Cliente", False, "No se encontró cliente por teléfono")
        except Exception as e:
            print(f"❌ Error al buscar cliente por teléfono: {e}\n")
            registrar_prueba("Setup - Cliente", False, f"Error al buscar cliente por teléfono: {e}")
   
    # ===================== USUARIO =====================
    auth_ctrl = AuthController()
    exito, msg, id_usuario_test = auth_ctrl.registrar_usuario(
        usuario="renta_test",
        nombre="Usuario",
        apellido_paterno="RentaTest",
        password="test1234",
        rol="empleado"
    )
   
    if exito and id_usuario_test:
        print(f"Usuario: {msg} (ID: {id_usuario_test})")
        registrar_prueba("Setup - Usuario", True, f"Usuario creado con ID: {id_usuario_test}")
    else:
        # Si ya existe el usuario, reutilizarlo
        print(f"Usuario: {msg} (intentando reutilizar)\n")
        try:
            usuario_obj = auth_ctrl.obtener_usuario_por_nombre("renta_test")
            if usuario_obj:
                id_usuario_test = usuario_obj.id_usuario
                print(f"ℹ️ Usuario reutilizado: ID {id_usuario_test}\n")
                registrar_prueba("Setup - Usuario", True, f"Usuario reutilizado con ID: {id_usuario_test}")
            else:
                print("⚠️ No se encontró usuario 'renta_test', id_usuario_test seguirá en None\n")
                registrar_prueba("Setup - Usuario", False, "No se encontró usuario 'renta_test'")
        except Exception as e:
            print(f"❌ Error al buscar usuario por nombre: {e}\n")
            registrar_prueba("Setup - Usuario", False, f"Error al buscar usuario por nombre: {e}")
   
    # ===================== DISFRAZ =====================
    inv_ctrl = InventarioController()
    res_disfraz = inv_ctrl.agregar_disfraz(
        codigo_barras=codigo_disfraz_test,
        descripcion="Disfraz Test Rentas",
        talla="M",
        color="Verde",
        categoria="Test",
        precio_venta=800.00,  # Depósito por unidad
        precio_renta=150.00,  # Por día
        stock=10
    )
    # Soporta (exito, msg) o (exito, msg, obj, ...)
    exito_disfraz = res_disfraz[0]
    msg_disfraz = res_disfraz[1] if len(res_disfraz) > 1 else ""
    print(f"Disfraz: {msg_disfraz}\n")
    if exito_disfraz:
        registrar_prueba("Setup - Disfraz", True, f"Disfraz creado: {codigo_disfraz_test}")
    else:
        registrar_prueba("Setup - Disfraz", False, f"Error al crear disfraz: {msg_disfraz}")


def prueba_1_registrar_renta():
    """Prueba 1: Registrar renta simple"""
    global id_renta_test
   
    print("="*60)
    print("PRUEBA 1: Registrar Renta")
    print("="*60 + "\n")
   
    controller = RentaController()
   
    detalles = [
        {'codigo_barras': codigo_disfraz_test, 'cantidad': 2}
    ]
   
    exito, msg, id_renta_test = controller.registrar_renta(
        id_cliente=id_cliente_test,
        id_usuario=id_usuario_test,
        detalles=detalles,
        dias_renta=3
    )
   
    if exito and id_renta_test:
        print(f"✅ PASÓ: {msg}")
        print(f"   ID Renta: {id_renta_test}\n")
        registrar_prueba("Registrar Renta", True, f"Renta registrada con ID: {id_renta_test}")
        return True
    else:
        print(f"❌ FALLÓ: {msg}\n")
        registrar_prueba("Registrar Renta", False, f"FALLÓ: {msg}")
        return False


def prueba_2_verificar_deposito():
    """Prueba 2: Verificar cálculo de depósito"""
    print("="*60)
    print("PRUEBA 2: Verificar Depósito")
    print("="*60 + "\n")
   
    controller = RentaController()
    renta = controller.obtener_renta_completa(id_renta_test)
   
    # Depósito debe ser precio_venta × cantidad = 800 × 2 = 1600
    if renta and renta.deposito == 1600.00:
        print(f"✅ PASÓ: Depósito calculado correctamente")
        print(f"   Depósito: ${renta.deposito:.2f}")
        print(f"   Total renta (3 días): ${renta.total:.2f}\n")
        registrar_prueba("Verificar Depósito", True, f"Depósito calculado correctamente: ${renta.deposito:.2f}")
        return True
    else:
        print(f"❌ FALLÓ: Depósito incorrecto\n")
        if renta:
            print(f"   Depósito: ${renta.deposito:.2f}")
        registrar_prueba("Verificar Depósito", False, f"Depósito incorrecto: {renta.deposito if renta else 'N/A'}")
        return False


def prueba_3_verificar_stock_descontado():
    """Prueba 3: Verificar que solo bajó disponible, NO stock"""
    print("="*60)
    print("PRUEBA 3: Stock en Rentas (Solo Disponible)")
    print("="*60 + "\n")
   
    inv_ctrl = InventarioController()
    disfraz = inv_ctrl.buscar_por_codigo(codigo_disfraz_test)
   
    # Stock debe seguir en 10, disponible debe ser 8 (10 - 2)
    if disfraz and disfraz.stock == 10 and disfraz.disponible == 8:
        print(f"✅ PASÓ: Solo disponible se descontó")
        print(f"   Stock: {disfraz.stock} (sin cambio)")
        print(f"   Disponible: {disfraz.disponible} (10 - 2 = 8)\n")
        registrar_prueba("Stock en Rentas", True, f"Stock: {disfraz.stock}, Disponible: {disfraz.disponible}")
        return True
    else:
        print(f"❌ FALLÓ: Stock incorrecto\n")
        if disfraz:
            print(f"   Stock: {disfraz.stock}, Disponible: {disfraz.disponible}")
        registrar_prueba("Stock en Rentas", False, f"Stock incorrecto - Stock: {disfraz.stock if disfraz else 'N/A'}, Disponible: {disfraz.disponible if disfraz else 'N/A'}")
        return False


def prueba_4_renta_con_dias_invalidos():
    """Prueba 4: Rechazar días inválidos"""
    print("="*60)
    print("PRUEBA 4: Días Inválidos (Debe Fallar)")
    print("="*60 + "\n")
   
    controller = RentaController()
   
    detalles = [
        {'codigo_barras': codigo_disfraz_test, 'cantidad': 1}
    ]
   
    # Intentar con 0 días
    exito, msg, _ = controller.registrar_renta(
        id_cliente=id_cliente_test,
        id_usuario=id_usuario_test,
        detalles=detalles,
        dias_renta=0
    )
   
    if not exito and "mayor a 0" in msg.lower():
        print(f"✅ PASÓ: Días inválidos rechazados")
        print(f"   Mensaje: {msg}\n")
        registrar_prueba("Días Inválidos", True, f"Días inválidos rechazados: {msg}")
        return True
    else:
        print(f"❌ FALLÓ: Debió rechazar días inválidos\n")
        registrar_prueba("Días Inválidos", False, f"Debió rechazar días inválidos - Mensaje: {msg}")
        return False


def prueba_5_devolver_renta():
    """Prueba 5: Devolver renta a tiempo"""
    print("="*60)
    print("PRUEBA 5: Devolver Renta a Tiempo")
    print("="*60 + "\n")
   
    controller = RentaController()
    inv_ctrl = InventarioController()
   
    # Stock antes
    disfraz_antes = inv_ctrl.buscar_por_codigo(codigo_disfraz_test)
    disponible_antes = disfraz_antes.disponible if disfraz_antes else 0
   
    # Devolver
    exito, msg, info = controller.devolver_renta(
        id_renta=id_renta_test,
        id_usuario=id_usuario_test
    )
   
    if exito and info:
        # Verificar que devolvió disponible
        disfraz_despues = inv_ctrl.buscar_por_codigo(codigo_disfraz_test)
        disponible_despues = disfraz_despues.disponible if disfraz_despues else 0
       
        print(f"✅ PASÓ: Renta devuelta")
        print(f"   Días retraso: {info['dias_retraso']}")
        print(f"   Penalización: ${info['penalizacion']:.2f}")
        print(f"   Depósito devuelto: ${info['deposito_devuelto']:.2f}")
        print(f"   Disponible: {disponible_antes} → {disponible_despues}\n")
        registrar_prueba("Devolver Renta a Tiempo", True, f"Días retraso: {info['dias_retraso']}, Penalización: ${info['penalizacion']:.2f}")
        return True
    else:
        print(f"❌ FALLÓ: {msg}\n")
        registrar_prueba("Devolver Renta a Tiempo", False, f"FALLÓ: {msg}")
        return False


def prueba_6_renta_con_retraso():
    """Prueba 6: Renta con retraso y penalización"""
    print("="*60)
    print("PRUEBA 6: Renta con Retraso")
    print("="*60 + "\n")
   
    controller = RentaController()
   
    # Crear una NUEVA renta exclusiva para esta prueba
    detalles = [
        {'codigo_barras': codigo_disfraz_test, 'cantidad': 1}
    ]
   
    exito, msg, id_renta_retraso = controller.registrar_renta(
        id_cliente=id_cliente_test,
        id_usuario=id_usuario_test,
        detalles=detalles,
        dias_renta=1  # 1 día
    )
   
    if not exito:
        print(f"❌ FALLÓ: No se pudo crear renta: {msg}\n")
        registrar_prueba("Renta con Retraso", False, f"No se pudo crear renta: {msg}")
        return False
   
    # Simular retraso modificando fecha en BD (ponerla 3 días atrás)
    from config.database import ConexionDB
    db = ConexionDB()
    db.conectar()
   
    # Poner fecha de devolución 3 días atrás
    fecha_pasada = datetime.now() - timedelta(days=3)
    query_simular = "UPDATE RENTAS SET Fecha_Devolucion = %s WHERE Id_Renta = %s"
    db.ejecutar_update(query_simular, (fecha_pasada, id_renta_retraso))
   
    # Devolver con retraso
    exito, msg, info = controller.devolver_renta(
        id_renta=id_renta_retraso,  # Usar la nueva renta
        id_usuario=id_usuario_test
    )
   
    if exito and info:
        # Verificar que se haya calculado penalización
        dias_retraso = info.get('dias_retraso', 0)
        penalizacion = info.get('penalizacion', 0)
        if dias_retraso > 0 and penalizacion > 0:
            print(f"✅ PASÓ: Penalización calculada")
            print(f"   Días retraso: {dias_retraso}")
            print(f"   Penalización: ${penalizacion:.2f}")
            print(f"   (${controller.penalizacion_dia:.2f} × {dias_retraso} días)\n")
            registrar_prueba("Renta con Retraso", True, f"Penalización calculada: ${penalizacion:.2f}")
            return True
        else:
            print(f"❌ FALLÓ: No se calculó penalización\n")
            print(f"   Días retraso: {dias_retraso}")
            print(f"   Penalización: ${penalizacion:.2f}")
            registrar_prueba("Renta con Retraso", False, f"No se calculó penalización - Días: {dias_retraso}, Penalización: ${penalizacion:.2f}")
            return False
    else:
        print(f"❌ FALLÓ: {msg}\n")
        print(f"   Info devuelto: {info}")
        registrar_prueba("Renta con Retraso", False, f"Falló devolución con retraso - Mensaje: {msg}, Info: {info}")
        return False


def prueba_7_marcar_vencidas():
    """Prueba 7: Marcar automáticamente rentas vencidas"""
    print("="*60)
    print("PRUEBA 7: Marcar Rentas Vencidas")
    print("="*60 + "\n")
   
    controller = RentaController()
   
    # Crear renta vencida
    detalles = [
        {'codigo_barras': codigo_disfraz_test, 'cantidad': 1}
    ]
   
    exito, msg, id_renta3 = controller.registrar_renta(
        id_cliente=id_cliente_test,
        id_usuario=id_usuario_test,
        detalles=detalles,
        dias_renta=1
    )
   
    if not exito:
        print(f"⚠️ No se pudo crear renta de prueba: {msg}\n")
        registrar_prueba("Marcar Rentas Vencidas", False, f"No se pudo crear renta de prueba: {msg}")
        return False
   
    # Simular que ya pasó la fecha
    from config.database import ConexionDB
    db = ConexionDB()
    db.conectar()
    fecha_pasada = datetime.now() - timedelta(days=1)
    db.ejecutar_update(
        "UPDATE RENTAS SET Fecha_Devolucion = %s WHERE Id_Renta = %s",
        (fecha_pasada, id_renta3)
    )
   
    # Marcar vencidas
    cantidad = controller.marcar_rentas_vencidas()
   
    if cantidad >= 1:
        print(f"✅ PASÓ: Rentas marcadas como vencidas")
        print(f"   Cantidad: {cantidad}\n")
        registrar_prueba("Marcar Rentas Vencidas", True, f"Rentas marcadas como vencidas: {cantidad}")
        return True
    else:
        print(f"❌ FALLÓ: No se marcaron rentas vencidas\n")
        registrar_prueba("Marcar Rentas Vencidas", False, "No se marcaron rentas vencidas")
        return False


def prueba_8_listar_activas():
    """Prueba 8: Listar rentas activas"""
    print("="*60)
    print("PRUEBA 8: Listar Rentas Activas")
    print("="*60 + "\n")
   
    controller = RentaController()
    rentas = controller.listar_rentas_activas()
   
    if isinstance(rentas, list):
        print(f"✅ PASÓ: Lista obtenida")
        print(f"   Rentas activas: {len(rentas)}\n")
        registrar_prueba("Listar Rentas Activas", True, f"Rentas activas: {len(rentas)}")
        return True
    else:
        print(f"❌ FALLÓ: Error al listar\n")
        registrar_prueba("Listar Rentas Activas", False, "Error al listar")
        return False


def prueba_9_actualizar_penalizacion():
    """Prueba 9: Actualizar configuración de penalización"""
    print("="*60)
    print("PRUEBA 9: Actualizar Penalización")
    print("="*60 + "\n")
   
    controller = RentaController()
   
    # Cambiar a $75/día
    exito, msg = controller.actualizar_penalizacion_dia(75.00)
   
    if exito and controller.penalizacion_dia == 75.00:
        print(f"✅ PASÓ: {msg}\n")
       
        # Regresar a $50
        controller.actualizar_penalizacion_dia(50.00)
        registrar_prueba("Actualizar Penalización", True, f"Penalización actualizada a $75/día")
        return True
    else:
        print(f"❌ FALLÓ: {msg}\n")
        registrar_prueba("Actualizar Penalización", False, f"FALLÓ: {msg}")
        return False


def prueba_10_contar_activas():
    """Prueba 10: Contar rentas activas"""
    print("="*60)
    print("PRUEBA 10: Contar Rentas Activas")
    print("="*60 + "\n")
   
    controller = RentaController()
    cantidad = controller.contar_rentas_activas()
   
    if cantidad >= 0:
        print(f"✅ PASÓ: Contador funcional")
        print(f"   Rentas activas: {cantidad}\n")
        registrar_prueba("Contar Rentas Activas", True, f"Rentas activas: {cantidad}")
        return True
    else:
        print(f"❌ FALLÓ: Error al contar\n")
        registrar_prueba("Contar Rentas Activas", False, "Error al contar")
        return False


def limpiar_datos_prueba():
    """Limpia todos los datos de prueba"""
    print("="*60)
    print("LIMPIEZA: Eliminando datos de prueba")
    print("="*60 + "\n")
   
    from config.database import ConexionDB
    db = ConexionDB()
    db.conectar()
   
    # Eliminar en orden (respetando FKs)
    db.ejecutar_update(
        "DELETE FROM DETALLE_RENTAS WHERE Id_Renta IN (SELECT Id_Renta FROM RENTAS WHERE Id_Cliente = %s)",
        (id_cliente_test,)
    )
    db.ejecutar_update("DELETE FROM RENTAS WHERE Id_Cliente = %s", (id_cliente_test,))
    db.ejecutar_update("DELETE FROM INVENTARIO WHERE Codigo_Barras = %s", (codigo_disfraz_test,))
    db.ejecutar_update("DELETE FROM CLIENTES WHERE Id_cliente = %s", (id_cliente_test,))
    db.ejecutar_update("DELETE FROM USUARIOS WHERE Id_usuario = %s", (id_usuario_test,))
   
    print("✅ Datos de prueba eliminados\n")
    print(f"📊 AUDITORÍA: Limpieza de datos - Resultado: Éxito - Mensaje: Datos de prueba eliminados")


def ejecutar_todas():
    """Ejecuta todas las pruebas"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  PRUEBAS DE RENTAS - SISTEMA DISFRACES  ".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
   
    # Setup
    setup_datos_prueba()
   
    resultados = []
   
    # Ejecutar pruebas
    resultados.append(prueba_1_registrar_renta())
    resultados.append(prueba_2_verificar_deposito())
    resultados.append(prueba_3_verificar_stock_descontado())
    resultados.append(prueba_4_renta_con_dias_invalidos())
    resultados.append(prueba_5_devolver_renta())
    resultados.append(prueba_6_renta_con_retraso())
    resultados.append(prueba_7_marcar_vencidas())
    resultados.append(prueba_8_listar_activas())
    resultados.append(prueba_9_actualizar_penalizacion())
    resultados.append(prueba_10_contar_activas())
   
    # Limpiar
    limpiar_datos_prueba()
   
    # Resumen
    total = len(resultados)
    exitosas = sum(resultados)
   
    print("█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  RESUMEN  ".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    print(f"\n✅ Pruebas exitosas: {exitosas}/{total}")
    print(f"❌ Pruebas fallidas: {total - exitosas}/{total}\n")
   
    if exitosas == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ Sistema de rentas funciona perfectamente")
        print("✅ Depósitos automáticos: OK")
        print("✅ Stock solo disponible: OK")
        print("✅ Penalizaciones: OK")
        print("✅ Marcado automático: OK\n")
    else:
        print("⚠️ Revisa los errores arriba\n")
   
    print("█"*60 + "\n")


if __name__ == "__main__":
    try:
        ejecutar_todas()
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}\n")
        import traceback
        traceback.print_exc()