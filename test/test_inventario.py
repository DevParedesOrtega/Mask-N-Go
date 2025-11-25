"""
Script de pruebas para sistema de inventario
Ubicación: test/test_inventario.py
"""

import sys
import os

ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)

from controllers.inventario_controller import InventarioController


def prueba_1_agregar_disfraz():
    """Prueba 1: Agregar disfraz"""
    print("\n" + "="*60)
    print("PRUEBA 1: Agregar Disfraz")
    print("="*60 + "\n")
    
    inv = InventarioController()
    
    exito, msg = inv.agregar_disfraz(
        codigo_barras="TEST001",
        descripcion="Spider-Man Test",
        talla="M",
        color="Rojo/Azul",
        categoria="Superheroes",
        precio_venta=850.00,
        precio_renta=150.00,
        stock=10
    )
    
    if exito:
        print(f"✅ PASÓ: {msg}\n")
        return True
    else:
        print(f"❌ FALLÓ: {msg}\n")
        return False


def prueba_2_buscar_por_codigo():
    """Prueba 2: Buscar por código"""
    print("="*60)
    print("PRUEBA 2: Buscar por Código")
    print("="*60 + "\n")
    
    inv = InventarioController()
    disfraz = inv.buscar_por_codigo("TEST001")
    
    if disfraz:
        print(f"✅ PASÓ: Disfraz encontrado")
        print(f"   Código: {disfraz.codigo_barras}")
        print(f"   Descripción: {disfraz.descripcion}")
        print(f"   Stock: {disfraz.stock}")
        print(f"   Disponible: {disfraz.disponible}\n")
        return True
    else:
        print("❌ FALLÓ: No se encontró el disfraz\n")
        return False


def prueba_3_buscar_por_categoria():
    """Prueba 3: Buscar por categoría"""
    print("="*60)
    print("PRUEBA 3: Buscar por Categoría")
    print("="*60 + "\n")
    
    inv = InventarioController()
    disfraces = inv.buscar_por_categoria("Superheroes")
    
    if disfraces and len(disfraces) > 0:
        print(f"✅ PASÓ: {len(disfraces)} disfraces encontrados")
        for d in disfraces[:3]:
            print(f"   - {d.descripcion}")
        print()
        return True
    else:
        print("❌ FALLÓ: No se encontraron disfraces de esa categoría\n")
        return False


def prueba_4_buscar_por_nombre():
    """Prueba 4: Buscar por nombre"""
    print("="*60)
    print("PRUEBA 4: Buscar por Nombre (LIKE)")
    print("="*60 + "\n")
    
    inv = InventarioController()
    disfraces = inv.buscar_por_nombre("Spider")
    
    if disfraces and len(disfraces) > 0:
        print(f"✅ PASÓ: {len(disfraces)} disfraces encontrados")
        for d in disfraces:
            print(f"   - {d.descripcion}")
        print()
        return True
    else:
        print("❌ FALLÓ: No se encontraron disfraces con ese nombre\n")
        return False


def prueba_5_control_stock_estricto():
    """Prueba 5: Control estricto de stock"""
    print("="*60)
    print("PRUEBA 5: Control Estricto de Stock")
    print("="*60 + "\n")
    
    inv = InventarioController()
    
    # Intentar descontar más de lo disponible (debe fallar)
    print("Intentando descontar 15 unidades (solo hay 10)...")
    exito, msg = inv.descontar_stock("TEST001", 15)
    
    if not exito and "insuficiente" in msg.lower():
        print(f"✅ PASÓ: Control estricto funcionó")
        print(f"   Mensaje: {msg}\n")
        return True
    else:
        print(f"❌ FALLÓ: Debió rechazar por stock insuficiente\n")
        return False


def prueba_6_descontar_stock():
    """Prueba 6: Descontar stock válido"""
    print("="*60)
    print("PRUEBA 6: Descontar Stock Válido")
    print("="*60 + "\n")
    
    inv = InventarioController()
    
    print("Descontando 3 unidades...")
    exito, msg = inv.descontar_stock("TEST001", 3)
    
    if exito:
        print(f"✅ PASÓ: {msg}")
        
        # Verificar que se descontó
        disfraz = inv.buscar_por_codigo("TEST001")
        if disfraz and disfraz.disponible == 7:
            print(f"   Nuevo disponible: {disfraz.disponible}/10\n")
            return True
        else:
            print("❌ FALLÓ: El stock no se actualizó correctamente\n")
            return False
    else:
        print(f"❌ FALLÓ: {msg}\n")
        return False


def prueba_7_aumentar_stock():
    """Prueba 7: Aumentar stock (devolución)"""
    print("="*60)
    print("PRUEBA 7: Aumentar Stock (Devolución)")
    print("="*60 + "\n")
    
    inv = InventarioController()
    
    print("Aumentando 3 unidades (devolución)...")
    exito, msg = inv.aumentar_stock("TEST001", 3)
    
    if exito:
        print(f"✅ PASÓ: {msg}")
        
        # Verificar que se aumentó
        disfraz = inv.buscar_por_codigo("TEST001")
        if disfraz and disfraz.disponible == 10:
            print(f"   Nuevo disponible: {disfraz.disponible}/10\n")
            return True
        else:
            print("❌ FALLÓ: El stock no se actualizó correctamente\n")
            return False
    else:
        print(f"❌ FALLÓ: {msg}\n")
        return False


def prueba_8_editar_disfraz():
    """Prueba 8: Editar disfraz"""
    print("="*60)
    print("PRUEBA 8: Editar Disfraz")
    print("="*60 + "\n")
    
    inv = InventarioController()
    
    print("Editando precio de venta...")
    exito, msg = inv.editar_disfraz(
        codigo_barras="TEST001",
        precio_venta=900.00
    )
    
    if exito:
        print(f"✅ PASÓ: {msg}")
        
        # Verificar cambio
        disfraz = inv.buscar_por_codigo("TEST001")
        if disfraz and disfraz.precio_venta == 900.00:
            print(f"   Nuevo precio: ${disfraz.precio_venta}\n")
            return True
        else:
            print("❌ FALLÓ: El precio no se actualizó\n")
            return False
    else:
        print(f"❌ FALLÓ: {msg}\n")
        return False


def prueba_9_listar_disponibles():
    """Prueba 9: Listar solo disponibles"""
    print("="*60)
    print("PRUEBA 9: Listar Disfraces Disponibles")
    print("="*60 + "\n")
    
    inv = InventarioController()
    disfraces = inv.listar_disponibles()
    
    if disfraces and len(disfraces) > 0:
        print(f"✅ PASÓ: {len(disfraces)} disfraces disponibles")
        for i, d in enumerate(disfraces[:5], 1):
            print(f"   {i}. {d.descripcion} - Disponible: {d.disponible}")
        print()
        return True
    else:
        print("❌ FALLÓ: No se encontraron disfraces disponibles\n")
        return False


def prueba_10_eliminar_disfraz():
    """Prueba 10: Eliminar (marcar inactivo)"""
    print("="*60)
    print("PRUEBA 10: Eliminar Disfraz (Lógico)")
    print("="*60 + "\n")
    
    inv = InventarioController()
    
    print("Eliminando disfraz TEST001 (marcando como Inactivo)...")
    exito, msg = inv.eliminar_disfraz("TEST001")
    
    if exito:
        print(f"✅ PASÓ: {msg}")
        
        # Verificar que está inactivo
        disfraz = inv.buscar_por_codigo("TEST001")
        if disfraz and not disfraz.esta_activo():
            print(f"   Estado: {disfraz.estado}\n")
            return True
        else:
            print("❌ FALLÓ: El disfraz no está inactivo\n")
            return False
    else:
        print(f"❌ FALLÓ: {msg}\n")
        return False


def limpiar_datos_prueba():
    """Limpia datos de prueba"""
    print("="*60)
    print("LIMPIEZA: Eliminando datos de prueba")
    print("="*60 + "\n")
    
    from config.database import ConexionDB
    db = ConexionDB()
    db.conectar()
    
    query = "DELETE FROM INVENTARIO WHERE Codigo_Barras = 'TEST001'"
    filas = db.ejecutar_update(query)
    
    if filas:
        print(f"✅ Datos de prueba eliminados ({filas} filas)\n")
    else:
        print("ℹ️ No había datos de prueba para eliminar\n")


def ejecutar_todas():
    """Ejecuta todas las pruebas"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  PRUEBAS DE INVENTARIO - SISTEMA DISFRACES  ".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    # Limpiar datos previos
    limpiar_datos_prueba()
    
    resultados = []
    
    # Ejecutar pruebas
    resultados.append(prueba_1_agregar_disfraz())
    resultados.append(prueba_2_buscar_por_codigo())
    resultados.append(prueba_3_buscar_por_categoria())
    resultados.append(prueba_4_buscar_por_nombre())
    resultados.append(prueba_5_control_stock_estricto())
    resultados.append(prueba_6_descontar_stock())
    resultados.append(prueba_7_aumentar_stock())
    resultados.append(prueba_8_editar_disfraz())
    resultados.append(prueba_9_listar_disponibles())
    resultados.append(prueba_10_eliminar_disfraz())
    
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
        print("✅ Sistema de inventario funciona perfectamente\n")
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