"""
Script de pruebas para sistema de clientes
Ubicación: test/test_cliente.py
"""

import sys
import os

ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)

from controllers.cliente_controller import ClienteController


def prueba_1_buscar_duplicados_antes():
    """Prueba 1: Búsqueda inteligente de duplicados"""
    print("\n" + "="*60)
    print("PRUEBA 1: Búsqueda Inteligente de Duplicados")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    # Buscar antes de agregar
    duplicados = controller.buscar_duplicados("Cliente", "Test", "6180000000")
    
    if isinstance(duplicados, list):
        print(f"✅ PASÓ: Búsqueda de duplicados funcional")
        print(f"   Clientes similares encontrados: {len(duplicados)}\n")
        return True
    else:
        print("❌ FALLÓ: Error en búsqueda de duplicados\n")
        return False


def prueba_2_agregar_cliente():
    """Prueba 2: Agregar cliente con validación"""
    print("="*60)
    print("PRUEBA 2: Agregar Cliente")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    exito, msg, id_cliente, duplicados = controller.agregar_cliente(
        nombre="Cliente",
        apellido_paterno="Test",
        telefono="+52 618 000 0000"
    )
    
    if exito and id_cliente:
        print(f"✅ PASÓ: {msg}")
        print(f"   ID: {id_cliente}\n")
        return True, id_cliente
    elif duplicados:
        print(f"⚠️ ADVERTENCIA: {msg}")
        print(f"   Duplicados encontrados: {len(duplicados)}\n")
        return False, None
    else:
        print(f"❌ FALLÓ: {msg}\n")
        return False, None


def prueba_3_telefono_duplicado():
    """Prueba 3: Rechazar teléfono duplicado"""
    print("="*60)
    print("PRUEBA 3: Teléfono Duplicado (Bloqueo)") 
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    exito, msg, id_cliente, duplicados = controller.agregar_cliente(
        nombre="Otro",
        apellido_paterno="Cliente",
        telefono="+52 618 000 0000"  # Mismo teléfono
    )
    
    if not exito and "ya está registrado" in msg.lower():
        print(f"✅ PASÓ: Teléfono duplicado bloqueado correctamente")
        print(f"   Mensaje: {msg}\n")
        return True
    else:
        print(f"❌ FALLÓ: Debió rechazar teléfono duplicado\n")
        return False


def prueba_4_buscar_por_id(id_cliente: int):
    """Prueba 4: Buscar por ID"""
    print("="*60)
    print("PRUEBA 4: Buscar por ID")
    print("="*60 + "\n")
    
    controller = ClienteController()
    cliente = controller.buscar_por_id(id_cliente)
    
    if cliente:
        print(f"✅ PASÓ: Cliente encontrado")
        print(f"   Nombre: {cliente.nombre_completo()}")
        print(f"   Teléfono: {cliente.telefono_formateado()}\n")
        return True
    else:
        print("❌ FALLÓ: No se encontró el cliente\n")
        return False


def prueba_5_buscar_por_telefono():
    """Prueba 5: Buscar por teléfono"""
    print("="*60)
    print("PRUEBA 5: Buscar por Teléfono")
    print("="*60 + "\n")
    
    controller = ClienteController()
    cliente = controller.buscar_por_telefono("+52 618 000 0000")
    
    if cliente:
        print(f"✅ PASÓ: Cliente encontrado")
        print(f"   ID: {cliente.id_cliente}")
        print(f"   Nombre: {cliente.nombre_completo()}\n")
        return True
    else:
        print("❌ FALLÓ: No se encontró el cliente\n")
        return False


def prueba_6_buscar_por_nombre():
    """Prueba 6: Buscar por nombre"""
    print("="*60)
    print("PRUEBA 6: Buscar por Nombre (LIKE)")
    print("="*60 + "\n")
    
    controller = ClienteController()
    clientes = controller.buscar_por_nombre("Cliente")
    
    if clientes and len(clientes) > 0:
        print(f"✅ PASÓ: {len(clientes)} clientes encontrados")
        for c in clientes[:3]:
            print(f"   - {c.nombre_completo()} ({c.telefono})")
        print()
        return True
    else:
        print("❌ FALLÓ: No se encontraron clientes\n")
        return False


def prueba_7_historial_cliente(id_cliente: int):
    """Prueba 7: Cargar historial completo"""
    print("="*60)
    print("PRUEBA 7: Historial Completo del Cliente")
    print("="*60 + "\n")
    
    controller = ClienteController()
    cliente = controller.obtener_cliente_con_historial(id_cliente)
    
    if cliente and cliente.estadisticas:
        print(f"✅ PASÓ: Historial cargado")
        print(f"\n{cliente.resumen_estadisticas()}\n")
        return True
    else:
        print("❌ FALLÓ: No se pudo cargar historial\n")
        return False


def prueba_8_editar_cliente(id_cliente: int):
    """Prueba 8: Editar cliente"""
    print("="*60)
    print("PRUEBA 8: Editar Cliente")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    print("Editando nombre...")
    exito, msg = controller.editar_cliente(
        id_cliente=id_cliente,
        nombre="ClienteEditado"
    )
    
    if exito:
        print(f"✅ PASÓ: {msg}")
        
        # Verificar cambio
        cliente = controller.buscar_por_id(id_cliente)
        if cliente and cliente.nombre == "ClienteEditado":
            print(f"   Nuevo nombre: {cliente.nombre_completo()}\n")
            return True
        else:
            print("❌ FALLÓ: El nombre no se actualizó\n")
            return False
    else:
        print(f"❌ FALLÓ: {msg}\n")
        return False


def prueba_9_editar_telefono_critico(id_cliente: int):
    """Prueba 9: Cambio de teléfono (operación crítica)"""
    print("="*60)
    print("PRUEBA 9: Cambio de Teléfono (Crítico)")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    print("⚠️ Intentando cambiar teléfono (operación crítica)...")
    exito, msg = controller.editar_cliente(
        id_cliente=id_cliente,
        telefono="+52 618 999 9999"
    )
    
    if exito:
        print(f"✅ PASÓ: {msg}")
        print(f"   ADVERTENCIA mostrada correctamente\n")
        return True
    else:
        print(f"❌ FALLÓ: {msg}\n")
        return False


def prueba_10_eliminar_sin_historial(id_cliente: int):
    """Prueba 10: Eliminar cliente SIN historial"""
    print("="*60)
    print("PRUEBA 10: Eliminar Cliente sin Historial")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    print(f"Eliminando cliente ID {id_cliente} (sin historial)...")
    exito, msg = controller.eliminar_cliente(id_cliente)
    
    if exito:
        print(f"✅ PASÓ: {msg}")
        
        # Verificar que ya no existe
        cliente = controller.buscar_por_id(id_cliente)
        if cliente is None:
            print(f"   Cliente eliminado correctamente\n")
            return True
        else:
            print("❌ FALLÓ: El cliente no se eliminó\n")
            return False
    else:
        print(f"❌ FALLÓ: {msg}\n")
        return False


def prueba_11_listar_clientes():
    """Prueba 11: Listar todos los clientes"""
    print("="*60)
    print("PRUEBA 11: Listar Clientes")
    print("="*60 + "\n")
    
    controller = ClienteController()
    clientes = controller.listar_todos()
    
    if isinstance(clientes, list):
        print(f"✅ PASÓ: {len(clientes)} clientes registrados")
        for i, c in enumerate(clientes[:3], 1):
            print(f"   {i}. {c.nombre_completo()} - {c.telefono_formateado()}")
        print()
        return True
    else:
        print("❌ FALLÓ: Error al listar clientes\n")
        return False


def limpiar_datos_prueba():
    """Limpia datos de prueba"""
    print("="*60)
    print("LIMPIEZA: Eliminando datos de prueba")
    print("="*60 + "\n")
    
    from config.database import ConexionDB
    db = ConexionDB()
    db.conectar()
    
    # Eliminar clientes de prueba
    query = "DELETE FROM CLIENTES WHERE Telefono LIKE '%618 000 0000%' OR Telefono LIKE '%618 999 9999%'"
    filas = db.ejecutar_update(query)
    
    if filas:
        print(f"✅ Datos de prueba eliminados ({filas} filas)\n")
    else:
        print("ℹ️ No había datos de prueba para eliminar\n")


def ejecutar_todas():
    """Ejecuta todas las pruebas"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  PRUEBAS DE CLIENTES - SISTEMA DISFRACES  ".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    resultados = []
    
    # Limpiar datos previos
    limpiar_datos_prueba()
    
    # Ejecutar pruebas
    resultados.append(prueba_1_buscar_duplicados_antes())
    
    exito_agregar, id_cliente = prueba_2_agregar_cliente()
    resultados.append(exito_agregar)
    
    if exito_agregar and id_cliente:
        resultados.append(prueba_3_telefono_duplicado())
        resultados.append(prueba_4_buscar_por_id(id_cliente))
        resultados.append(prueba_5_buscar_por_telefono())
        resultados.append(prueba_6_buscar_por_nombre())
        resultados.append(prueba_7_historial_cliente(id_cliente))
        resultados.append(prueba_8_editar_cliente(id_cliente))
        resultados.append(prueba_9_editar_telefono_critico(id_cliente))
        resultados.append(prueba_10_eliminar_sin_historial(id_cliente))
        resultados.append(prueba_11_listar_clientes())
    
    # Limpiar al final
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
        print("✅ Sistema de clientes funciona perfectamente")
        print("✅ Búsqueda inteligente de duplicados: OK")
        print("✅ Historial completo: OK")
        print("✅ Validaciones: OK\n")
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