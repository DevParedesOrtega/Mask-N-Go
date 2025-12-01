"""
Script de pruebas para ConexionDB
Ubicación: test/test_conexion.py
Versión: 2.1 - Ajustado a estructura actual de CLIENTES
"""

import sys
import os

# Agregar directorio raíz al path
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)

from config.database import ConexionDB


def prueba_1_conexion():
    """Prueba 1: Conexión básica"""
    print("\n" + "="*60)
    print("PRUEBA 1: Conexión Básica")
    print("="*60 + "\n")
    
    db = ConexionDB()
    
    if db.conectar():
        print("\n✅ PASÓ: Conexión exitosa")
        db.desconectar()
        return True
    else:
        print("\n❌ FALLÓ: No se pudo conectar")
        return False


def prueba_2_listar_tablas():
    """Prueba 2: Listar tablas"""
    print("\n" + "="*60)
    print("PRUEBA 2: Listar Tablas")
    print("="*60 + "\n")
    
    db = ConexionDB()
    db.conectar()
    
    tablas = db.ejecutar_query("SHOW TABLES")
    
    if tablas:
        print(f"\n📊 Tablas encontradas:")
        for i, tabla in enumerate(tablas, 1):
            print(f"   {i}. {tabla[0]}")
        print(f"\n✅ PASÓ: {len(tablas)} tablas")
        db.desconectar()
        return True
    else:
        print("\n❌ FALLÓ: No se encontraron tablas")
        db.desconectar()
        return False


def prueba_3_insert():
    """Prueba 3: INSERT en CLIENTES (respeta Estado)"""
    print("\n" + "="*60)
    print("PRUEBA 3: INSERT")
    print("="*60 + "\n")
    
    db = ConexionDB()
    db.conectar()
    
    # CLIENTES ahora tiene: Id_cliente, Nombre, Apellido_Paterno, Telefono, Estado, Fecha_Registro
    query = "INSERT INTO CLIENTES (Nombre, Apellido_Paterno, Telefono, Estado) VALUES (%s, %s, %s, %s)"
    nuevo_id = db.ejecutar_insert(query, ('Test Cliente', 'Prueba', '6180000000', 'Activo'))
    
    if nuevo_id:
        print(f"\n✅ PASÓ: Cliente insertado ID {nuevo_id}")
        
        # Limpiar: eliminar el registro de prueba
        db.ejecutar_update("DELETE FROM CLIENTES WHERE Id_cliente = %s", (nuevo_id,))
        
        db.desconectar()
        return True
    else:
        print("\n❌ FALLÓ: Error en INSERT")
        db.desconectar()
        return False


def prueba_4_select():
    """Prueba 4: SELECT desde CLIENTES (con columnas actuales)"""
    print("\n" + "="*60)
    print("PRUEBA 4: SELECT")
    print("="*60 + "\n")
    
    db = ConexionDB()
    db.conectar()
    
    # Insertar dato de prueba con todas las columnas requeridas
    query_insert = "INSERT INTO CLIENTES (Nombre, Apellido_Paterno, Telefono, Estado) VALUES (%s, %s, %s, %s)"
    test_id = db.ejecutar_insert(query_insert, ('Select Test', 'Apellido', '6180000001', 'Activo'))
    
    if not test_id:
        print("\n❌ FALLÓ: No se pudo insertar dato de prueba")
        db.desconectar()
        return False
    
    # Ahora hacer SELECT (todas las columnas)
    query_select = "SELECT Id_cliente, Nombre, Apellido_Paterno, Telefono, Estado, Fecha_Registro FROM CLIENTES WHERE Id_cliente = %s"
    resultados = db.ejecutar_query(query_select, (test_id,))
    
    if resultados and len(resultados) > 0:
        fila = resultados[0]
        print(f"\n📋 Cliente encontrado:")
        print(f"   ID: {fila[0]}")
        print(f"   Nombre: {fila[1]}")
        print(f"   Apellido: {fila[2]}")
        print(f"   Teléfono: {fila[3]}")
        print(f"   Estado: {fila[4]}")
        print(f"   Fecha_Registro: {fila[5]}")
        print("\n✅ PASÓ: SELECT exitoso")
        
        # Limpiar
        db.ejecutar_update("DELETE FROM CLIENTES WHERE Id_cliente = %s", (test_id,))
        
        db.desconectar()
        return True
    else:
        print("\n❌ FALLÓ: No se encontró el registro")
        db.desconectar()
        return False


def ejecutar_todas():
    """Ejecuta todas las pruebas"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  PRUEBAS CONEXIONDB - SISTEMA DISFRACES  ".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    resultados = []
    resultados.append(prueba_1_conexion())
    resultados.append(prueba_2_listar_tablas())
    resultados.append(prueba_3_insert())
    resultados.append(prueba_4_select())
    
    # Resumen
    total = len(resultados)
    exitosas = sum(resultados)
    
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  RESUMEN  ".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    print(f"\n✅ Pruebas exitosas: {exitosas}/{total}")
    print(f"❌ Pruebas fallidas: {total - exitosas}/{total}\n")
    
    if exitosas == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ ConexionDB funciona perfectamente\n")
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
