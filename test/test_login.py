"""
Script de pruebas para sistema de autenticación
Ubicación: test/test_login.py
Versión: 2.1 - Con métodos de auditoría
"""

import sys
import os
from datetime import datetime

ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)

from controllers.auth_controller import AuthController
from utils.validadores import Validadores


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


def prueba_1_validaciones():
    """Prueba 1: Validadores"""
    print("\n" + "="*60)
    print("PRUEBA 1: Validaciones")
    print("="*60 + "\n")
    
    # Validar usuario correcto
    valido, msg = Validadores.validar_usuario("juan123")
    if valido:
        print("✅ Validación de usuario correcto: PASÓ")
        registrar_prueba("Validaciones", True, "Validación de usuario correcto: PASÓ")
    else:
        print(f"❌ FALLÓ: {msg}")
        registrar_prueba("Validaciones", False, f"Validación de usuario correcto falló: {msg}")
        return False
    
    # Validar usuario incorrecto
    valido, msg = Validadores.validar_usuario("ju")
    if not valido:
        print("✅ Rechazo de usuario corto: PASÓ")
        registrar_prueba("Validaciones", True, "Rechazo de usuario corto: PASÓ")
    else:
        print("❌ FALLÓ: Debió rechazar usuario corto")
        registrar_prueba("Validaciones", False, "Debió rechazar usuario corto")
        return False
    
    # Validar contraseña
    valido, msg = Validadores.validar_password("pass1234")
    if valido:
        print("✅ Validación de contraseña: PASÓ")
        registrar_prueba("Validaciones", True, "Validación de contraseña: PASÓ")
    else:
        print(f"❌ FALLÓ: {msg}")
        registrar_prueba("Validaciones", False, f"Validación de contraseña falló: {msg}")
        return False
    
    # Validar rol
    valido, msg = Validadores.validar_rol("admin")
    if valido:
        print("✅ Validación de rol: PASÓ")
        registrar_prueba("Validaciones", True, "Validación de rol: PASÓ")
    else:
        print(f"❌ FALLÓ: {msg}")
        registrar_prueba("Validaciones", False, f"Validación de rol falló: {msg}")
        return False
    
    print("\n✅ PRUEBA 1 COMPLETA\n")
    return True


def prueba_2_registro():
    """Prueba 2: Registro de usuario"""
    print("="*60)
    print("PRUEBA 2: Registro de Usuario")
    print("="*60 + "\n")
    
    auth = AuthController()
    
    # Registrar usuario de prueba (CORREGIDO: incluye apellido_paterno)
    exito, msg, id_usuario = auth.registrar_usuario(
        usuario="test_login",
        nombre="Usuario Test",
        apellido_paterno="Login",
        password="test1234",
        rol="empleado"
    )
    
    if exito and id_usuario:
        print(f"✅ Usuario registrado con ID: {id_usuario}")
        print(f"   Mensaje: {msg}\n")
        registrar_prueba("Registro de Usuario", True, f"Usuario registrado con ID: {id_usuario}")
        return True, id_usuario
    else:
        print(f"❌ FALLÓ: {msg}\n")
        registrar_prueba("Registro de Usuario", False, f"FALLÓ: {msg}")
        return False, None


def prueba_3_login_correcto(usuario: str, password: str):
    """Prueba 3: Login con credenciales correctas"""
    print("="*60)
    print("PRUEBA 3: Login Correcto")
    print("="*60 + "\n")
    
    auth = AuthController()
    
    exito, msg, usuario_obj = auth.iniciar_sesion(usuario, password)
    
    if exito and usuario_obj:
        print(f"✅ Login exitoso")
        print(f"   Usuario: {usuario_obj.usuario}")
        print(f"   Nombre completo: {usuario_obj.nombre_completo()}")
        print(f"   Rol: {usuario_obj.rol}")
        print(f"   Sesión activa: {auth.hay_sesion_activa()}\n")
        registrar_prueba("Login Correcto", True, f"Login exitoso para usuario: {usuario_obj.usuario}")
        return True, auth
    else:
        print(f"❌ FALLÓ: {msg}\n")
        registrar_prueba("Login Correcto", False, f"FALLÓ: {msg}")
        return False, None


def prueba_4_login_incorrecto():
    """Prueba 4: Login con credenciales incorrectas"""
    print("="*60)
    print("PRUEBA 4: Login Incorrecto")
    print("="*60 + "\n")
    
    auth = AuthController()
    
    # Intentar con contraseña incorrecta
    exito, msg, usuario_obj = auth.iniciar_sesion("test_login", "wrongpassword")
    
    if not exito and usuario_obj is None:
        print(f"✅ Login rechazado correctamente")
        print(f"   Mensaje: {msg}\n")
        registrar_prueba("Login Incorrecto", True, f"Login rechazado correctamente: {msg}")
        return True
    else:
        print(f"❌ FALLÓ: Debió rechazar credenciales incorrectas\n")
        registrar_prueba("Login Incorrecto", False, "Debió rechazar credenciales incorrectas")
        return False


def prueba_5_sesion(auth: AuthController):
    """Prueba 5: Gestión de sesión"""
    print("="*60)
    print("PRUEBA 5: Gestión de Sesión")
    print("="*60 + "\n")
    
    # Verificar que hay sesión
    if not auth.hay_sesion_activa():
        print("❌ FALLÓ: No hay sesión activa\n")
        registrar_prueba("Gestión de Sesión", False, "No hay sesión activa")
        return False
    
    # Obtener datos de sesión
    usuario = auth.obtener_sesion_activa()
    if usuario:
        print(f"✅ Sesión activa detectada")
        print(f"   Nombre completo: {usuario.nombre_completo()}")
        print(f"   Rol: {usuario.rol}")
        registrar_prueba("Gestión de Sesión", True, f"Sesión activa detectada para usuario: {usuario.usuario}")
    else:
        print("❌ FALLÓ: No se pudo obtener sesión\n")
        registrar_prueba("Gestión de Sesión", False, "No se pudo obtener sesión")
        return False
    
    # Cerrar sesión
    if auth.cerrar_sesion():
        print(f"✅ Sesión cerrada correctamente")
    else:
        print("❌ FALLÓ: Error al cerrar sesión\n")
        registrar_prueba("Gestión de Sesión", False, "Error al cerrar sesión")
        return False
    
    # Verificar que ya no hay sesión
    if not auth.hay_sesion_activa():
        print(f"✅ Verificación de cierre de sesión correcta\n")
        registrar_prueba("Gestión de Sesión", True, "Verificación de cierre de sesión correcta")
        return True
    else:
        print("❌ FALLÓ: Sesión no se cerró correctamente\n")
        registrar_prueba("Gestión de Sesión", False, "Sesión no se cerró correctamente")
        return False


def prueba_6_usuario_duplicado():
    """Prueba 6: Evitar usuarios duplicados"""
    print("="*60)
    print("PRUEBA 6: Usuario Duplicado")
    print("="*60 + "\n")
    
    auth = AuthController()
    
    # Intentar registrar usuario que ya existe
    exito, msg, id_usuario = auth.registrar_usuario(
        usuario="test_login",
        nombre="Otro",
        apellido_paterno="Usuario",
        password="otra1234",
        rol="empleado"
    )
    
    if not exito and "ya existe" in msg.lower():
        print(f"✅ Usuario duplicado rechazado correctamente")
        print(f"   Mensaje: {msg}\n")
        registrar_prueba("Usuario Duplicado", True, f"Usuario duplicado rechazado correctamente: {msg}")
        return True
    else:
        print(f"❌ FALLÓ: Debió rechazar usuario duplicado\n")
        registrar_prueba("Usuario Duplicado", False, "Debió rechazar usuario duplicado")
        return False


def prueba_7_listar_usuarios():
    """Prueba 7: Listar usuarios"""
    print("="*60)
    print("PRUEBA 7: Listar Usuarios")
    print("="*60 + "\n")
    
    auth = AuthController()
    usuarios = auth.listar_usuarios()
    
    if usuarios and len(usuarios) > 0:
        print(f"✅ Usuarios encontrados: {len(usuarios)}")
        for i, user in enumerate(usuarios[:3], 1):  # Mostrar solo primeros 3
            print(f"   {i}. {user.usuario} - {user.nombre_completo()} ({user.rol})")
        print()
        registrar_prueba("Listar Usuarios", True, f"Usuarios encontrados: {len(usuarios)}")
        return True
    else:
        print("❌ FALLÓ: No se encontraron usuarios\n")
        registrar_prueba("Listar Usuarios", False, "No se encontraron usuarios")
        return False


def limpiar_datos_prueba():
    """Limpia los datos de prueba creados"""
    print("="*60)
    print("LIMPIEZA: Eliminando datos de prueba")
    print("="*60 + "\n")
    
    from config.database import ConexionDB
    db = ConexionDB()
    db.conectar()
    
    query = "DELETE FROM USUARIOS WHERE Usuario = 'test_login'"
    filas = db.ejecutar_update(query)
    
    if filas:
        print(f"✅ Datos de prueba eliminados ({filas} filas)\n")
        print(f"📊 AUDITORÍA: Limpieza de datos - Resultado: Éxito - Mensaje: {filas} filas eliminadas")
    else:
        print("ℹ️ No había datos de prueba para eliminar\n")
        print(f"📊 AUDITORÍA: Limpieza de datos - Resultado: Éxito - Mensaje: No había datos de prueba para eliminar")


def ejecutar_todas():
    """Ejecuta todas las pruebas"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  PRUEBAS DE AUTENTICACIÓN - SISTEMA DISFRACES  ".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    resultados = []
    
    # Limpiar datos previos
    limpiar_datos_prueba()
    
    # Ejecutar pruebas
    resultados.append(prueba_1_validaciones())
    
    exito_registro, id_usuario = prueba_2_registro()
    resultados.append(exito_registro)
    
    if exito_registro:
        exito_login, auth = prueba_3_login_correcto("test_login", "test1234")
        resultados.append(exito_login)
        
        resultados.append(prueba_4_login_incorrecto())
        
        if exito_login and auth:
            resultados.append(prueba_5_sesion(auth))
        
        resultados.append(prueba_6_usuario_duplicado())
        resultados.append(prueba_7_listar_usuarios())
    
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
        print("✅ Sistema de autenticación funciona correctamente\n")
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