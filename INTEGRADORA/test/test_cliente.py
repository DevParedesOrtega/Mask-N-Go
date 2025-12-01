
"""
Script de pruebas para sistema de clientes
Ubicación: test/test_cliente.py
Versión: 2.1 - Corregido con parámetros reales del controller
"""


import sys
import os


ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)


from controllers.cliente_controller import ClienteController
from decimal import Decimal



# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

TELEFONO_PRUEBA_1 = "+52 618 000 0000"
TELEFONO_PRUEBA_2 = "+52 618 999 9999"
TELEFONO_INVALIDO_1 = "123"  # Muy corto
TELEFONO_INVALIDO_2 = "abcdefghijk"  # No es número
TELEFONO_INVALIDO_3 = ""  # Vacío


# ============================================================
# PRUEBAS BÁSICAS (HAPPY PATH)
# ============================================================

def prueba_1_buscar_duplicados_antes():
    """Prueba 1: Búsqueda inteligente de duplicados ANTES de agregar"""
    print("\n" + "="*60)
    print("PRUEBA 1: Búsqueda Inteligente de Duplicados (Antes)")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        duplicados = controller.buscar_duplicados("ClientePrueba", "Test", TELEFONO_PRUEBA_1)
        
        assert isinstance(duplicados, list), "Debe retornar una lista"
        print(f"✅ PASÓ: Búsqueda de duplicados funcional")
        print(f"   Clientes similares encontrados: {len(duplicados)}\n")
        return True
    except Exception as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False



def prueba_2_agregar_cliente_valido():
    """Prueba 2: Agregar cliente CON DATOS VÁLIDOS"""
    print("="*60)
    print("PRUEBA 2: Agregar Cliente Válido")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        exito, msg, id_cliente, duplicados = controller.agregar_cliente(
            nombre="ClientePrueba",
            apellido="Test",
            telefono=TELEFONO_PRUEBA_1
        )
        
        assert exito is True, f"Debe ser exitoso. Mensaje: {msg}"
        assert id_cliente is not None and id_cliente > 0, "ID debe ser válido"
        assert isinstance(id_cliente, int), "ID debe ser entero"
        
        print(f"✅ PASÓ: {msg}")
        print(f"   ID: {id_cliente}\n")
        return True, id_cliente
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False, None
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False, None



def prueba_3_telefono_duplicado_bloqueo():
    """Prueba 3: RECHAZAR teléfono duplicado"""
    print("="*60)
    print("PRUEBA 3: Teléfono Duplicado (Bloqueo)")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        exito, msg, id_cliente, duplicados = controller.agregar_cliente(
            nombre="OtroCliente",
            apellido="Diferente",
            telefono=TELEFONO_PRUEBA_1  # MISMO TELÉFONO
        )
        
        assert exito is False, "Debe fallar con teléfono duplicado"
        assert "ya está registrado" in msg.lower() or "duplicado" in msg.lower(), \
            f"Mensaje debe indicar duplicado. Recibido: {msg}"
        
        print(f"✅ PASÓ: Teléfono duplicado bloqueado correctamente")
        print(f"   Mensaje: {msg}\n")
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_4_buscar_por_id(id_cliente: int):
    """Prueba 4: Buscar cliente POR ID"""
    print("="*60)
    print("PRUEBA 4: Buscar por ID")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        cliente = controller.buscar_por_id(id_cliente)
        
        assert cliente is not None, "Cliente debe existir"
        assert cliente.id_cliente == id_cliente, "ID debe coincidir"
        assert cliente.nombre == "ClientePrueba", "Nombre debe coincidir"
        
        print(f"✅ PASÓ: Cliente encontrado")
        print(f"   Nombre: {cliente.nombre_completo()}")
        print(f"   Teléfono: {cliente.telefono_formateado()}\n")
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_5_buscar_por_telefono():
    """Prueba 5: Buscar cliente POR TELÉFONO"""
    print("="*60)
    print("PRUEBA 5: Buscar por Teléfono")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        cliente = controller.buscar_por_telefono(TELEFONO_PRUEBA_1)
        
        assert cliente is not None, "Cliente debe encontrarse"
        assert cliente.telefono == TELEFONO_PRUEBA_1, "Teléfono debe coincidir"
        assert cliente.nombre == "ClientePrueba", "Nombre debe coincidir"
        
        print(f"✅ PASÓ: Cliente encontrado")
        print(f"   ID: {cliente.id_cliente}")
        print(f"   Nombre: {cliente.nombre_completo()}\n")
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_6_buscar_por_nombre():
    """Prueba 6: Buscar cliente POR NOMBRE (LIKE)"""
    print("="*60)
    print("PRUEBA 6: Buscar por Nombre (LIKE)")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        clientes = controller.buscar_por_nombre("ClientePrueba")
        
        assert isinstance(clientes, list), "Debe retornar lista"
        assert len(clientes) > 0, "Debe encontrar al menos un cliente"
        
        # Verificar que al menos uno coincida
        encontrado = any(c.nombre.lower().find("clienteprueba".lower()) >= 0 for c in clientes)
        assert encontrado, "Debe contener cliente con ese nombre"
        
        print(f"✅ PASÓ: {len(clientes)} cliente(s) encontrado(s)")
        for c in clientes[:3]:
            print(f"   - {c.nombre_completo()} ({c.telefono})")
        print()
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_7_editar_cliente(id_cliente: int):
    """Prueba 7: EDITAR cliente (nombre)"""
    print("="*60)
    print("PRUEBA 7: Editar Cliente")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        print("Editando nombre...")
        exito, msg = controller.editar_cliente(
            id_cliente=id_cliente,
            nombre="ClienteEditado"
        )
        
        assert exito is True, f"Edición debe ser exitosa. Mensaje: {msg}"
        
        # Verificar cambio
        cliente = controller.buscar_por_id(id_cliente)
        assert cliente is not None, "Cliente debe existir"
        assert cliente.nombre == "ClienteEditado", "Nombre debe estar actualizado"
        
        print(f"✅ PASÓ: {msg}")
        print(f"   Nuevo nombre: {cliente.nombre_completo()}\n")
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_8_editar_telefono_critico(id_cliente: int):
    """Prueba 8: EDITAR TELÉFONO (operación crítica con validación)"""
    print("="*60)
    print("PRUEBA 8: Cambio de Teléfono (Crítico)")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        print("⚠️  Intentando cambiar teléfono (operación crítica)...")
        exito, msg = controller.editar_cliente(
            id_cliente=id_cliente,
            telefono=TELEFONO_PRUEBA_2
        )
        
        assert exito is True, f"Cambio debe ser exitoso. Mensaje: {msg}"
        
        # Verificar cambio
        cliente = controller.buscar_por_id(id_cliente)
        assert cliente is not None, "Cliente debe existir"
        assert cliente.telefono == TELEFONO_PRUEBA_2, "Teléfono debe estar actualizado"
        
        print(f"✅ PASÓ: {msg}")
        print(f"   Nuevo teléfono: {cliente.telefono_formateado()}\n")
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_9_eliminar_cliente(id_cliente: int):
    """Prueba 9: ELIMINAR cliente"""
    print("="*60)
    print("PRUEBA 9: Eliminar Cliente")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        print(f"Eliminando cliente ID {id_cliente}...")
        exito, msg = controller.eliminar_cliente(id_cliente)
        
        assert exito is True, f"Eliminación debe ser exitosa. Mensaje: {msg}"
        
        # Verificar que ya no existe
        cliente = controller.buscar_por_id(id_cliente)
        assert cliente is None, "Cliente NO debe existir después de eliminar"
        
        print(f"✅ PASÓ: {msg}")
        print(f"   Cliente eliminado correctamente\n")
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_10_listar_clientes():
    """Prueba 10: LISTAR todos los clientes"""
    print("="*60)
    print("PRUEBA 10: Listar Clientes")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        clientes = controller.listar_todos()
        
        assert isinstance(clientes, list), "Debe retornar una lista"
        # Nota: La lista puede estar vacía después de eliminar, eso es OK
        
        print(f"✅ PASÓ: {len(clientes)} cliente(s) registrado(s)")
        for i, c in enumerate(clientes[:5], 1):
            print(f"   {i}. {c.nombre_completo()} - {c.telefono_formateado()}")
        if len(clientes) > 5:
            print(f"   ... y {len(clientes) - 5} más")
        print()
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



# ============================================================
# PRUEBAS DE VALIDACIÓN (EDGE CASES - ERRORES)
# ============================================================

def prueba_11_agregar_nombre_vacio():
    """Prueba 11 (EDGE): Rechazar nombre VACÍO"""
    print("="*60)
    print("PRUEBA 11 (EDGE): Nombre Vacío - DEBE RECHAZAR")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        exito, msg, id_cliente, duplicados = controller.agregar_cliente(
            nombre="",  # VACÍO
            apellido="Test",
            telefono="+52 618 111 1111"
        )
        
        assert exito is False, "Debe RECHAZAR nombre vacío"
        assert "nombre" in msg.lower() or "vacío" in msg.lower(), \
            f"Mensaje debe indicar problema con nombre. Recibido: {msg}"
        
        print(f"✅ PASÓ: Nombre vacío rechazado correctamente")
        print(f"   Mensaje: {msg}\n")
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_12_agregar_apellido_vacio():
    """Prueba 12 (EDGE): Rechazar apellido VACÍO"""
    print("="*60)
    print("PRUEBA 12 (EDGE): Apellido Vacío - DEBE RECHAZAR")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        exito, msg, id_cliente, duplicados = controller.agregar_cliente(
            nombre="Cliente",
            apellido="",  # VACÍO
            telefono="+52 618 111 1111"
        )
        
        assert exito is False, "Debe RECHAZAR apellido vacío"
        assert "apellido" in msg.lower() or "vacío" in msg.lower(), \
            f"Mensaje debe indicar problema con apellido. Recibido: {msg}"
        
        print(f"✅ PASÓ: Apellido vacío rechazado correctamente")
        print(f"   Mensaje: {msg}\n")
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_13_agregar_telefono_invalido_corto():
    """Prueba 13 (EDGE): Rechazar teléfono MUY CORTO"""
    print("="*60)
    print("PRUEBA 13 (EDGE): Teléfono Muy Corto - DEBE RECHAZAR")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        exito, msg, id_cliente, duplicados = controller.agregar_cliente(
            nombre="Cliente",
            apellido="Test",
            telefono=TELEFONO_INVALIDO_1  # "123" - muy corto
        )
        
        assert exito is False, "Debe RECHAZAR teléfono muy corto"
        assert "teléfono" in msg.lower() or "inválido" in msg.lower() or "dígitos" in msg.lower(), \
            f"Mensaje debe indicar problema con teléfono. Recibido: {msg}"
        
        print(f"✅ PASÓ: Teléfono muy corto rechazado correctamente")
        print(f"   Mensaje: {msg}\n")
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_14_agregar_telefono_invalido_letras():
    """Prueba 14 (EDGE): Rechazar teléfono con LETRAS"""
    print("="*60)
    print("PRUEBA 14 (EDGE): Teléfono con Letras - DEBE RECHAZAR")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        exito, msg, id_cliente, duplicados = controller.agregar_cliente(
            nombre="Cliente",
            apellido="Test",
            telefono=TELEFONO_INVALIDO_2  # "abcdefghijk"
        )
        
        assert exito is False, "Debe RECHAZAR teléfono con letras"
        assert "teléfono" in msg.lower() or "inválido" in msg.lower() or "números" in msg.lower(), \
            f"Mensaje debe indicar problema con teléfono. Recibido: {msg}"
        
        print(f"✅ PASÓ: Teléfono con letras rechazado correctamente")
        print(f"   Mensaje: {msg}\n")
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_15_buscar_cliente_inexistente():
    """Prueba 15 (EDGE): Buscar cliente que NO EXISTE"""
    print("="*60)
    print("PRUEBA 15 (EDGE): Buscar Cliente Inexistente")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        # ID que no debe existir
        cliente = controller.buscar_por_id(999999)
        
        assert cliente is None, "Cliente NO debe encontrarse"
        
        print(f"✅ PASÓ: Búsqueda de cliente inexistente retorna None")
        print(f"   Resultado: {cliente}\n")
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_16_buscar_telefono_inexistente():
    """Prueba 16 (EDGE): Buscar teléfono que NO EXISTE"""
    print("="*60)
    print("PRUEBA 16 (EDGE): Buscar Teléfono Inexistente")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        cliente = controller.buscar_por_telefono("+52 999 999 9999")
        
        assert cliente is None, "Cliente NO debe encontrarse"
        
        print(f"✅ PASÓ: Búsqueda de teléfono inexistente retorna None")
        print(f"   Resultado: {cliente}\n")
        return True
    except AssertionError as e:
        print(f"❌ FALLÓ: {str(e)}\n")
        return False
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



def prueba_17_eliminar_cliente_inexistente():
    """Prueba 17 (EDGE): Eliminar cliente que NO EXISTE"""
    print("="*60)
    print("PRUEBA 17 (EDGE): Eliminar Cliente Inexistente")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        exito, msg = controller.eliminar_cliente(999999)
        
        # Puede ser False o True (depende de la lógica del controller)
        # Lo importante es que no lance excepción
        print(f"✅ PASÓ: Manejo correcto de cliente inexistente")
        print(f"   Resultado: {exito}")
        print(f"   Mensaje: {msg}\n")
        return True
    except Exception as e:
        print(f"❌ FALLÓ (Excepción no esperada): {str(e)}\n")
        return False



def prueba_18_buscar_nombre_vacio():
    """Prueba 18 (EDGE): Buscar con nombre VACÍO"""
    print("="*60)
    print("PRUEBA 18 (EDGE): Buscar con Nombre Vacío")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    try:
        clientes = controller.buscar_por_nombre("")
        
        # Debe retornar lista (posiblemente vacía o todos)
        assert isinstance(clientes, list), "Debe retornar lista"
        
        print(f"✅ PASÓ: Búsqueda con nombre vacío manejada correctamente")
        print(f"   Resultados: {len(clientes)} cliente(s)\n")
        return True
    except Exception as e:
        print(f"❌ FALLÓ (Excepción): {str(e)}\n")
        return False



# ============================================================
# LIMPIEZA Y RESUMEN
# ============================================================

def limpiar_datos_prueba():
    """Limpia datos de prueba de la BD"""
    print("="*60)
    print("LIMPIEZA: Eliminando datos de prueba")
    print("="*60 + "\n")
    
    try:
        from config.database import ConexionDB
        db = ConexionDB()
        db.conectar()
        
        # Eliminar clientes de prueba por teléfono
        query = f"DELETE FROM CLIENTES WHERE Telefono LIKE '%618 000 0000%' OR Telefono LIKE '%618 999 9999%' OR Telefono LIKE '%618 111 1111%'"
        filas = db.ejecutar_update(query)
        
        if filas:
            print(f"✅ Datos de prueba eliminados ({filas} filas)\n")
        else:
            print("ℹ️ No había datos de prueba para eliminar\n")
        
        db.desconectar()
        return True
    except Exception as e:
        print(f"⚠️ Error en limpieza: {str(e)}\n")
        return False



def ejecutar_todas():
    """Ejecuta TODAS las pruebas en orden"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  PRUEBAS DE CLIENTES v2.1 - CON EDGE CASES  ".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    resultados = []
    id_cliente = None
    
    # LIMPIEZA INICIAL
    limpiar_datos_prueba()
    
    # ============================================================
    # PRUEBAS BÁSICAS (HAPPY PATH)
    # ============================================================
    print("\n" + "▶"*30)
    print("SECCIÓN 1: PRUEBAS BÁSICAS (HAPPY PATH)")
    print("▶"*30)
    
    resultados.append(("Búsqueda de duplicados (antes)", prueba_1_buscar_duplicados_antes()))
    
    exito_agregar, id_cliente = prueba_2_agregar_cliente_valido()
    resultados.append(("Agregar cliente válido", exito_agregar))
    
    if exito_agregar and id_cliente:
        resultados.append(("Teléfono duplicado (bloqueo)", prueba_3_telefono_duplicado_bloqueo()))
        resultados.append(("Buscar por ID", prueba_4_buscar_por_id(id_cliente)))
        resultados.append(("Buscar por teléfono", prueba_5_buscar_por_telefono()))
        resultados.append(("Buscar por nombre (LIKE)", prueba_6_buscar_por_nombre()))
        resultados.append(("Editar cliente", prueba_7_editar_cliente(id_cliente)))
        resultados.append(("Cambio de teléfono", prueba_8_editar_telefono_critico(id_cliente)))
        resultados.append(("Eliminar cliente", prueba_9_eliminar_cliente(id_cliente)))
    
    resultados.append(("Listar clientes", prueba_10_listar_clientes()))
    
    # ============================================================
    # PRUEBAS DE VALIDACIÓN (EDGE CASES)
    # ============================================================
    print("\n" + "▶"*30)
    print("SECCIÓN 2: PRUEBAS DE VALIDACIÓN (EDGE CASES)")
    print("▶"*30)
    
    resultados.append(("Nombre vacío (EDGE)", prueba_11_agregar_nombre_vacio()))
    resultados.append(("Apellido vacío (EDGE)", prueba_12_agregar_apellido_vacio()))
    resultados.append(("Teléfono muy corto (EDGE)", prueba_13_agregar_telefono_invalido_corto()))
    resultados.append(("Teléfono con letras (EDGE)", prueba_14_agregar_telefono_invalido_letras()))
    resultados.append(("Cliente inexistente (EDGE)", prueba_15_buscar_cliente_inexistente()))
    resultados.append(("Teléfono inexistente (EDGE)", prueba_16_buscar_telefono_inexistente()))
    resultados.append(("Eliminar inexistente (EDGE)", prueba_17_eliminar_cliente_inexistente()))
    resultados.append(("Búsqueda nombre vacío (EDGE)", prueba_18_buscar_nombre_vacio()))
    
    # LIMPIEZA FINAL
    print("\n")
    limpiar_datos_prueba()
    
    # ============================================================
    # RESUMEN FINAL
    # ============================================================
    print("█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  RESUMEN FINAL  ".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60 + "\n")
    
    # Análisis
    total = len(resultados)
    exitosas = sum(1 for _, resultado in resultados if resultado is True)
    fallidas = total - exitosas
    
    # Mostrar tabla de resultados
    print(f"{'Prueba':<45} {'Resultado':<13}")
    print("-"*60)
    
    for nombre, resultado in resultados:
        status = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{nombre:<45} {status:<13}")
    
    print("-"*60)
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Total de pruebas: {total}")
    print(f"   ✅ Exitosas: {exitosas} ({(exitosas/total*100):.1f}%)")
    print(f"   ❌ Fallidas: {fallidas} ({(fallidas/total*100):.1f}%)\n")
    
    # Conclusión
    if exitosas == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ Sistema de clientes: FUNCIONANDO PERFECTAMENTE")
        print("✅ Validaciones: OK")
        print("✅ Edge cases: OK")
        print("✅ Manejo de errores: OK\n")
    elif fallidas <= 2:
        print("⚠️ LA MAYORÍA DE PRUEBAS PASARON")
        print(f"   Revisa los {fallidas} error(es) arriba\n")
    else:
        print("❌ MÚLTIPLES FALLOS")
        print("   Revisa todos los errores y valida la lógica\n")
    
    print("█"*60 + "\n")
    
    return exitosas, total



# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    try:
        exitosas, total = ejecutar_todas()
        
        # Exit code basado en resultados
        import sys
        sys.exit(0 if exitosas == total else 1)
        
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)