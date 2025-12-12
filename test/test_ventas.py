"""
Script de pruebas para sistema de ventas
Ubicación: test/test_ventas.py
"""


import sys
import os


ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)


from controllers.venta_controller import VentaController
from controllers.inventario_controller import InventarioController
from controllers.cliente_controller import ClienteController
from controllers.auth_controller import AuthController



# Variables globales para IDs de prueba
id_cliente_test = None
id_usuario_test = None
id_venta_test = None
codigo_disfraz_test = "VENTEST001"



def setup_datos_prueba():
    """Crea o reutiliza datos necesarios para las pruebas"""
    global id_cliente_test, id_usuario_test
    
    print("\n" + "="*60)
    print("SETUP: Creando datos de prueba")
    print("="*60 + "\n")
    
    # ===================== CLIENTE =====================
    cliente_ctrl = ClienteController()
    exito, msg, id_cliente_test, _ = cliente_ctrl.agregar_cliente(
        nombre="ClienteVenta",
        apellido="Test",  # ✅ CORREGIDO: apellido (no apellido_paterno)
        telefono="+52 618 111 1111",
        forzar=True
    )
    
    if exito and id_cliente_test:
        print(f"Cliente: {msg} (ID: {id_cliente_test})")
    else:
        print(f"Cliente: {msg} (intentando reutilizar)\n")
        try:
            cliente = cliente_ctrl.buscar_por_telefono("+52 618 111 1111")
            if cliente:
                id_cliente_test = cliente.id_cliente
                print(f"ℹ️ Cliente reutilizado: ID {id_cliente_test}\n")
            else:
                print("⚠️ No se encontró cliente por teléfono\n")
        except Exception as e:
            print(f"❌ Error al buscar cliente: {e}\n")
    
    # ===================== USUARIO =====================
    auth_ctrl = AuthController()
    exito, msg, id_usuario_test = auth_ctrl.registrar_usuario(
        usuario="venta_test",
        nombre="Usuario",
        apellido_paterno="VentaTest",
        password="test1234",
        rol="admin"  # IMPORTANTE: admin para poder cancelar
    )
    
    if exito and id_usuario_test:
        print(f"Usuario: {msg} (ID: {id_usuario_test})")
    else:
        print(f"Usuario: {msg} (intentando reutilizar)\n")
        try:
            usuario_obj = auth_ctrl.obtener_usuario_por_nombre("venta_test")
            if usuario_obj:
                id_usuario_test = usuario_obj.id_usuario
                print(f"ℹ️ Usuario reutilizado: ID {id_usuario_test}\n")
            else:
                print("⚠️ No se encontró usuario 'venta_test'\n")
        except Exception as e:
            print(f"❌ Error al buscar usuario: {e}\n")
    
    # ===================== DISFRAZ =====================
    inv_ctrl = InventarioController()
    res_disfraz = inv_ctrl.agregar_disfraz(
        codigo_barras=codigo_disfraz_test,
        descripcion="Disfraz Test Ventas",
        talla="M",
        color="Azul",
        categoria="Test",
        precio_venta=500.00,
        precio_renta=100.00,
        stock=10
    )
    exito_disfraz = res_disfraz[0]
    msg_disfraz = res_disfraz[1] if len(res_disfraz) > 1 else ""
    print(f"Disfraz: {msg_disfraz}\n")



def prueba_1_generar_folio():
    """Prueba 1: Generar folio único"""
    print("="*60)
    print("PRUEBA 1: Generar Folio Único")
    print("="*60 + "\n")
    
    controller = VentaController()
    folio = controller.generar_folio()
    
    if folio and folio.startswith("VEN-"):
        print(f"✅ PASÓ: Folio generado correctamente")
        print(f"   Folio: {folio}\n")
        return True
    else:
        print("❌ FALLÓ: Error al generar folio\n")
        return False



def prueba_2_registrar_venta_simple():
    """Prueba 2: Registrar venta simple sin descuento"""
    global id_venta_test
    
    print("="*60)
    print("PRUEBA 2: Registrar Venta Simple")
    print("="*60 + "\n")
    
    controller = VentaController()
    
    detalles = [
        {'codigo_barras': codigo_disfraz_test, 'cantidad': 2}
    ]
    
    exito, msg, id_venta_test = controller.registrar_venta(
        id_cliente=id_cliente_test,
        id_usuario=id_usuario_test,
        detalles=detalles,
        metodo_pago='Efectivo'
    )
    
    if exito and id_venta_test:
        print(f"✅ PASÓ: {msg}")
        print(f"   ID Venta: {id_venta_test}\n")
        return True
    else:
        print(f"❌ FALLÓ: {msg}\n")
        return False



def prueba_3_verificar_stock_descontado():
    """Prueba 3: Verificar que el stock se descontó"""
    print("="*60)
    print("PRUEBA 3: Verificar Stock Descontado")
    print("="*60 + "\n")
    
    inv_ctrl = InventarioController()
    disfraz = inv_ctrl.buscar_por_codigo(codigo_disfraz_test)
    
    if disfraz and disfraz.disponible == 8:  # 10 - 2 = 8
        print(f"✅ PASÓ: Stock descontado correctamente")
        print(f"   Stock: {disfraz.stock}, Disponible: {disfraz.disponible}\n")
        return True
    else:
        print("❌ FALLÓ: El stock no se descontó correctamente\n")
        if disfraz:
            print(f"   Stock: {disfraz.stock}, Disponible: {disfraz.disponible}")
        return False



def prueba_4_venta_con_descuento():
    """Prueba 4: Venta con descuento y justificación"""
    print("="*60)
    print("PRUEBA 4: Venta con Descuento")
    print("="*60 + "\n")
    
    controller = VentaController()
    
    detalles = [
        {'codigo_barras': codigo_disfraz_test, 'cantidad': 1}
    ]
    
    exito, msg, id_venta = controller.registrar_venta(
        id_cliente=id_cliente_test,
        id_usuario=id_usuario_test,
        detalles=detalles,
        metodo_pago='tarjeta',
        descuento_porcentaje=20,
        motivo_descuento='Cliente VIP - Promoción especial',
        motivo_venta='Halloween'
    )
    
    if exito:
        print(f"✅ PASÓ: Venta con descuento registrada")
        
        # Verificar descuento
        venta = controller.obtener_venta_completa(id_venta)
        if venta and venta.descuento_porcentaje == 20:
            total_final = venta.obtener_total_final()
            print(f"   Descuento: {venta.descuento_porcentaje}%")
            print(f"   Total final: ${total_final:.2f}\n")
            return True
    
    print(f"❌ FALLÓ: {msg}\n")
    return False



def prueba_5_descuento_sin_justificacion():
    """Prueba 5: Rechazar descuento sin justificación"""
    print("="*60)
    print("PRUEBA 5: Descuento sin Justificación (Debe Fallar)")
    print("="*60 + "\n")
    
    controller = VentaController()
    
    detalles = [
        {'codigo_barras': codigo_disfraz_test, 'cantidad': 1}
    ]
    
    exito, msg, id_venta = controller.registrar_venta(
        id_cliente=id_cliente_test,
        id_usuario=id_usuario_test,
        detalles=detalles,
        metodo_pago='Efectivo',
        descuento_porcentaje=10
        # Sin motivo_descuento
    )
    
    if not exito and "justificación" in msg.lower():
        print(f"✅ PASÓ: Descuento sin justificación rechazado")
        print(f"   Mensaje: {msg}\n")
        return True
    else:
        print("❌ FALLÓ: Debió rechazar descuento sin justificación\n")
        return False



def prueba_6_stock_insuficiente():
    """Prueba 6: Rechazar venta con stock insuficiente"""
    print("="*60)
    print("PRUEBA 6: Stock Insuficiente (Debe Fallar)")
    print("="*60 + "\n")
    
    controller = VentaController()
    
    detalles = [
        {'codigo_barras': codigo_disfraz_test, 'cantidad': 100}  # Más de lo disponible
    ]
    
    exito, msg, id_venta = controller.registrar_venta(
        id_cliente=id_cliente_test,
        id_usuario=id_usuario_test,
        detalles=detalles,
        metodo_pago='Efectivo'
    )
    
    if not exito and "insuficiente" in msg.lower():
        print(f"✅ PASÓ: Stock insuficiente detectado")
        print(f"   Mensaje: {msg}\n")
        return True
    else:
        print("❌ FALLÓ: Debió rechazar por stock insuficiente\n")
        return False



def prueba_7_buscar_venta():
    """Prueba 7: Buscar venta por ID"""
    print("="*60)
    print("PRUEBA 7: Buscar Venta por ID")
    print("="*60 + "\n")
    
    controller = VentaController()
    venta = controller.obtener_venta_completa(id_venta_test)
    
    if venta:
        print(f"✅ PASÓ: Venta encontrada")
        print(f"\n{venta.resumen_estado()}\n")
        return True
    else:
        print("❌ FALLÓ: No se encontró la venta\n")
        return False



def prueba_8_total_ventas_dia():
    """Prueba 8: Calcular total del día"""
    print("="*60)
    print("PRUEBA 8: Total de Ventas del Día")
    print("="*60 + "\n")
    
    controller = VentaController()
    total = controller.total_ventas_dia()
    cantidad = controller.contar_ventas()
    
    if total >= 0 and cantidad >= 0:
        print(f"✅ PASÓ: Estadísticas calculadas")
        print(f"   Total del día: ${total:.2f}")
        print(f"   Cantidad de ventas: {cantidad}\n")
        return True
    else:
        print("❌ FALLÓ: Error al calcular estadísticas\n")
        return False



def prueba_9_cancelar_venta_no_admin():
    """Prueba 9: Intentar cancelar sin ser admin (debe fallar)"""
    print("="*60)
    print("PRUEBA 9: Cancelar Venta sin ser Admin (Debe Fallar)")
    print("="*60 + "\n")
    
    # Crear usuario empleado
    auth_ctrl = AuthController()
    exito, msg, id_empleado = auth_ctrl.registrar_usuario(
        usuario="empleado_test",
        nombre="Empleado",
        apellido_paterno="Test",
        password="test1234",
        rol="empleado"
    )
    
    controller = VentaController()
    exito, msg = controller.cancelar_venta(
        id_venta=id_venta_test,
        id_usuario_admin=id_empleado,
        motivo_cancelacion="Motivo de prueba"
    )
    
    # Limpiar empleado
    from config.database import ConexionDB
    db = ConexionDB()
    db.conectar()
    db.ejecutar_update("DELETE FROM USUARIOS WHERE Id_usuario = %s", (id_empleado,))
    
    if not exito and "administrador" in msg.lower():
        print(f"✅ PASÓ: Empleado no puede cancelar")
        print(f"   Mensaje: {msg}\n")
        return True
    else:
        print("❌ FALLÓ: Debió rechazar cancelación de empleado\n")
        return False



def prueba_10_cancelar_venta_admin():
    """Prueba 10: Cancelar venta como admin"""
    print("="*60)
    print("PRUEBA 10: Cancelar Venta como Admin")
    print("="*60 + "\n")
    
    controller = VentaController()
    inv_ctrl = InventarioController()
    
    # Stock antes de cancelar
    disfraz_antes = inv_ctrl.buscar_por_codigo(codigo_disfraz_test)
    stock_antes = disfraz_antes.disponible if disfraz_antes else 0
    print(f"   Stock antes de cancelar: {stock_antes}")
    
    # Cancelar
    exito, msg = controller.cancelar_venta(
        id_venta=id_venta_test,
        id_usuario_admin=id_usuario_test,
        motivo_cancelacion="Cancelación de prueba - Cliente desistió de la compra"
    )
    
    if exito:
        # Forzar nueva consulta
        import time
        time.sleep(0.1)
        
        inv_ctrl_nuevo = InventarioController()
        disfraz_despues = inv_ctrl_nuevo.buscar_por_codigo(codigo_disfraz_test)
        stock_despues = disfraz_despues.disponible if disfraz_despues else 0
        print(f"   Stock después de cancelar: {stock_despues}")
        
        # La venta tenía 2 productos, así que debió aumentar en 2
        if stock_despues > stock_antes:
            print(f"✅ PASÓ: Venta cancelada y stock devuelto correctamente")
            print(f"   Stock aumentó de {stock_antes} a {stock_despues}\n")
            return True
        else:
            print(f"❌ FALLÓ: Stock no se devolvió (antes: {stock_antes}, después: {stock_despues})\n")
            return False
    else:
        print(f"❌ FALLÓ: {msg}\n")
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
        "DELETE FROM DETALLE_VENTAS WHERE Id_Venta IN (SELECT Id_Venta FROM VENTAS WHERE Id_cliente = %s)",
        (id_cliente_test,)
    )
    db.ejecutar_update("DELETE FROM VENTAS WHERE Id_cliente = %s", (id_cliente_test,))
    db.ejecutar_update("DELETE FROM INVENTARIO WHERE Codigo_Barras = %s", (codigo_disfraz_test,))
    db.ejecutar_update("DELETE FROM CLIENTES WHERE Id_cliente = %s", (id_cliente_test,))
    db.ejecutar_update("DELETE FROM USUARIOS WHERE Id_usuario = %s OR Usuario = 'empleado_test'", (id_usuario_test,))
    
    print("✅ Datos de prueba eliminados\n")



def ejecutar_todas():
    """Ejecuta todas las pruebas"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  PRUEBAS DE VENTAS - SISTEMA DISFRACES  ".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    # Setup
    setup_datos_prueba()
    
    resultados = []
    
    # Ejecutar pruebas
    resultados.append(prueba_1_generar_folio())
    resultados.append(prueba_2_registrar_venta_simple())
    resultados.append(prueba_3_verificar_stock_descontado())
    resultados.append(prueba_4_venta_con_descuento())
    resultados.append(prueba_5_descuento_sin_justificacion())
    resultados.append(prueba_6_stock_insuficiente())
    resultados.append(prueba_7_buscar_venta())
    resultados.append(prueba_8_total_ventas_dia())
    resultados.append(prueba_9_cancelar_venta_no_admin())
    resultados.append(prueba_10_cancelar_venta_admin())
    
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
        print("✅ Sistema de ventas funciona perfectamente")
        print("✅ Folios automáticos: OK")
        print("✅ Descuentos con justificación: OK")
        print("✅ Validaciones: OK")
        print("✅ Cancelación admin: OK\n")
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
