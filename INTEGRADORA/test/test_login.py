"""
Script de pruebas para sistema de autenticación
Ubicación: test/test_login.py
"""

import sys
import os

ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)

from controllers.auth_controller import AuthController
from utils.validadores import Validadores


def prueba_1_validaciones():
    """Prueba 1: Validadores"""
    print("\n" + "="*60)
    print("PRUEBA 1: Validaciones")
    print("="*60 + "\n")
    
    # Validar usuario correcto
    valido, msg = Validadores.validar_usuario("juan123")
    if valido:
        print("✅ Validación de usuario correcto: PASÓ")
    else:
        print(f"❌ FALLÓ: {msg}")
        return False
    
    # Validar usuario incorrecto
    valido, msg = Validadores.validar_usuario("ju")
    if not valido:
        print("✅ Rechazo de usuario corto: PASÓ")
    else:
        print("❌ FALLÓ: Debió rechazar usuario corto")
        return False
    
    # Validar contraseña
    valido, msg = Validadores.validar_password("pass1234")
    if valido:
        print("✅ Validación de contraseña: PASÓ")
    else:
        print(f"❌ FALLÓ: {msg}")
        return False
    
    # Validar rol
    valido, msg = Validadores.validar_rol("admin")
    if valido:
        print("✅ Validación de rol: PASÓ")
    else:
        print(f"❌ FALLÓ: {msg}")
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
        return True, id_usuario
    else:
        print(f"❌ FALLÓ: {msg}\n")
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
        return True, auth
    else:
        print(f"❌ FALLÓ: {msg}\n")
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
        return True
    else:
        print(f"❌ FALLÓ: Debió rechazar credenciales incorrectas\n")
        return False


def prueba_5_sesion(auth: AuthController):
    """Prueba 5: Gestión de sesión"""
    print("="*60)
    print("PRUEBA 5: Gestión de Sesión")
    print("="*60 + "\n")
    
    # Verificar que hay sesión
    if not auth.hay_sesion_activa():
        print("❌ FALLÓ: No hay sesión activa\n")
        return False
    
    # Obtener datos de sesión
    usuario = auth.obtener_sesion_activa()
    if usuario:
        print(f"✅ Sesión activa detectada")
        print(f"   Nombre completo: {usuario.nombre_completo()}")
        print(f"   Rol: {usuario.rol}")
    else:
        print("❌ FALLÓ: No se pudo obtener sesión\n")
        return False
    
    # Cerrar sesión
    if auth.cerrar_sesion():
        print(f"✅ Sesión cerrada correctamente")
    else:
        print("❌ FALLÓ: Error al cerrar sesión\n")
        return False
    
    # Verificar que ya no hay sesión
    if not auth.hay_sesion_activa():
        print(f"✅ Verificación de cierre de sesión correcta\n")
        return True
    else:
        print("❌ FALLÓ: Sesión no se cerró correctamente\n")
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
        return True
    else:
        print(f"❌ FALLÓ: Debió rechazar usuario duplicado\n")
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
        return True
    else:
        print("❌ FALLÓ: No se encontraron usuarios\n")
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
    else:
        print("ℹ️ No había datos de prueba para eliminar\n")


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