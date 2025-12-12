"""
Módulo: auth_controller.py
Ubicación: controllers/auth_controller.py
Descripción: Controlador para autenticación de usuarios
Sistema: Renta y Venta de Disfraces
Versión: 2.5 - Con gestión completa de pregunta/respuesta de seguridad
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
from models.usuario import Usuario
from utils.validadores import Validadores
from utils.logger_config import setup_logger
from typing import Optional, Tuple, List
import mysql.connector
import logging


# Configurar logging
logger = setup_logger('auth_controller', 'logs/auth.log')


class AuthController:
    """
    Controlador para manejar autenticación de usuarios.
    
    Gestiona:
    - Registro de nuevos usuarios (con pregunta/respuesta de seguridad opcional)
    - Inicio de sesión
    - Recuperación de contraseña mediante pregunta de seguridad
    - Actualización completa de usuarios (incluyendo pregunta/respuesta)
    - Eliminación de usuarios (SOLO ADMIN)
    - Cambio de roles (SOLO ADMIN)
    - Gestión de sesión activa
    """
    
    def __init__(self):
        """Inicializa el controlador con conexión a BD."""
        self.db = ConexionDB()
        self.sesion_activa: Optional[Usuario] = None  # Usuario actualmente logueado
    
    # ============================================================
    # MÉTODOS PRIVADOS - VALIDACIÓN DE PERMISOS
    # ============================================================
    
    def _validar_admin(self) -> bool:
        """
        Verifica que hay sesión activa y el usuario es ADMIN.
        
        Returns:
            bool: True si es admin, False si no
        """
        return self.sesion_activa is not None and self.sesion_activa.rol == 'admin'
    
    def _validar_sesion(self) -> bool:
        """
        Verifica que hay sesión activa.
        
        Returns:
            bool: True si hay sesión, False si no
        """
        return self.sesion_activa is not None

    # ============================================================
    # REGISTRO Y AUTENTICACIÓN
    # ============================================================

    def registrar_usuario(
        self,
        usuario: str,
        nombre: str,
        apellido_paterno: str,
        password: str,
        rol: str = 'empleado',
        pregunta_seguridad: Optional[str] = None,
        respuesta_seguridad: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Registra un nuevo usuario en el sistema.
        
        Args:
            usuario: Nombre de usuario para login
            nombre: Nombre del usuario
            apellido_paterno: Apellido paterno
            password: Contraseña en texto plano
            rol: Rol del usuario (default: 'empleado')
            pregunta_seguridad: Pregunta de seguridad (opcional)
            respuesta_seguridad: Respuesta de seguridad (opcional, en texto plano)
        
        Returns:
            Tuple[bool, str, Optional[int]]: (éxito, mensaje, id_usuario)
        """
        try:
            # 1. Validar usuario
            valido, mensaje = Validadores.validar_usuario(usuario)
            if not valido:
                logger.warning(f"Intento de registro fallido: {mensaje}")
                return False, mensaje, None
            
            # 2. Validar nombre
            valido, mensaje = Validadores.validar_nombre(nombre)
            if not valido:
                logger.warning(f"Intento de registro fallido: {mensaje}")
                return False, mensaje, None
            
            # 3. Validar apellido
            valido, mensaje = Validadores.validar_nombre(apellido_paterno)
            if not valido:
                logger.warning(f"Intento de registro fallido: Apellido: {mensaje}")
                return False, f"Apellido: {mensaje}", None
            
            # 4. Validar contraseña
            valido, mensaje = Validadores.validar_password(password)
            if not valido:
                logger.warning(f"Intento de registro fallido: {mensaje}")
                return False, mensaje, None
            
            # 5. Validar rol
            valido, mensaje = Validadores.validar_rol(rol)
            if not valido:
                logger.warning(f"Intento de registro fallido: {mensaje}")
                return False, mensaje, None
            
            # 6. Verificar que el usuario no exista
            if self.usuario_existe(usuario):
                logger.warning(f"Intento de registro duplicado: {usuario}")
                return False, f"El usuario '{usuario}' ya existe", None
            
            # 7. Insertar en base de datos
            self.db.conectar()
            query = """
                INSERT INTO USUARIOS (Usuario, Nombre, Apellido_Paterno, Password, Pregunta_Seguridad, Respuesta_Seguridad, Rol)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            nuevo_id = self.db.ejecutar_insert(
                query,
                (usuario, nombre, apellido_paterno, password, pregunta_seguridad, respuesta_seguridad, rol)
            )
            
            if nuevo_id:
                logger.info(f"Usuario '{usuario}' registrado exitosamente en USUARIOS (ID={nuevo_id})")
                return True, "Usuario registrado exitosamente", nuevo_id
            else:
                logger.error(f"Fallo al registrar usuario '{usuario}' en la base de datos")
                return False, "Error al registrar usuario en la base de datos", None

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en registrar_usuario: {e}")
            return False, f"Error de base de datos: {str(e)}", None
        except Exception as e:
            logger.error(f"Error inesperado en registrar_usuario: {e}")
            return False, f"Error inesperado: {str(e)}", None

    def iniciar_sesion(self, usuario: str, password: str) -> Tuple[bool, str, Optional[Usuario]]:
        """
        Inicia sesión validando credenciales.
        
        Args:
            usuario: Nombre de usuario
            password: Contraseña
        
        Returns:
            Tuple[bool, str, Optional[Usuario]]: (éxito, mensaje, objeto_usuario)
        """
        try:
            # 1. Validar que no estén vacíos
            if not usuario or not password:
                logger.warning("Intento de inicio de sesión sin usuario o contraseña")
                return False, "Usuario y contraseña son requeridos", None
            
            # 2. Buscar usuario en la BD
            self.db.conectar()
            query = "SELECT * FROM USUARIOS WHERE Usuario = %s"
            resultados = self.db.ejecutar_query(query, (usuario,))
            
            if not resultados or len(resultados) == 0:
                logger.warning(f"Intento de inicio de sesión fallido: usuario '{usuario}' no encontrado")
                return False, "Usuario o contraseña incorrectos", None
            
            # 3. Verificar contraseña
            usuario_db = Usuario.from_db_row(resultados[0])
            
            if usuario_db.password != password:
                logger.warning(f"Intento de inicio de sesión fallido: contraseña incorrecta para '{usuario}'")
                return False, "Usuario o contraseña incorrectos", None
            
            # 4. Crear sesión activa
            self.sesion_activa = usuario_db
            
            logger.info(f"Sesión iniciada: {usuario_db.nombre_completo()} ({usuario_db.rol})")
            return True, "Inicio de sesión exitoso", usuario_db

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en iniciar_sesion: {e}")
            return False, f"Error de base de datos: {str(e)}", None
        except Exception as e:
            logger.error(f"Error inesperado en iniciar_sesion: {e}")
            return False, f"Error inesperado: {str(e)}", None

    def cerrar_sesion(self) -> bool:
        """
        Cierra la sesión activa.
        
        Returns:
            bool: True si había sesión activa, False si no
        """
        if self.sesion_activa:
            logger.info(f"Sesión cerrada: {self.sesion_activa.nombre_completo()}")
            self.sesion_activa = None
            return True
        else:
            logger.info("Intento de cerrar sesión, pero no había sesión activa")
            return False

    # ============================================================
    # GESTIÓN DE SESIÓN
    # ============================================================
    
    def obtener_sesion_activa(self) -> Optional[Usuario]:
        """
        Obtiene el usuario de la sesión activa.
        
        Returns:
            Optional[Usuario]: Usuario logueado o None si no hay sesión
        """
        return self.sesion_activa
    
    def hay_sesion_activa(self) -> bool:
        """
        Verifica si hay una sesión activa.
        
        Returns:
            bool: True si hay sesión, False si no
        """
        return self.sesion_activa is not None

    # ============================================================
    # OPERACIONES CRUD - SIN VALIDACIÓN DE PERMISOS EN ESTE MÉTODO
    # ============================================================
    
    def actualizar_usuario(
        self,
        id_usuario: int,
        nombre: str,
        apellido_paterno: str,
        rol: str,
        password: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Actualiza los datos de un usuario existente (sin pregunta/respuesta).
        
        NOTA: Este método NO valida permisos. La validación debe hacerse
        en la capa de presentación (formulario) antes de llamarlo.
        """
        try:
            # 1. Verificar que el usuario existe
            usuario_actual = self.obtener_usuario_por_id(id_usuario)
            if not usuario_actual:
                logger.warning(f"Intento de actualizar usuario inexistente: ID {id_usuario}")
                return False, f"No existe un usuario con ID {id_usuario}"
            
            # 2. Validar nombre
            valido, mensaje = Validadores.validar_nombre(nombre)
            if not valido:
                logger.warning(f"Intento de actualizar usuario {id_usuario} con nombre inválido: {mensaje}")
                return False, f"Nombre inválido: {mensaje}"
            
            # 3. Validar apellido
            valido, mensaje = Validadores.validar_nombre(apellido_paterno)
            if not valido:
                logger.warning(f"Intento de actualizar usuario {id_usuario} con apellido inválido: {mensaje}")
                return False, f"Apellido inválido: {mensaje}"
            
            # 4. Validar rol
            valido, mensaje = Validadores.validar_rol(rol)
            if not valido:
                logger.warning(f"Intento de actualizar usuario {id_usuario} con rol inválido: {mensaje}")
                return False, f"Rol inválido: {mensaje}"
            
            # 5. Validar contraseña si se proporciona
            if password:
                valido, mensaje = Validadores.validar_password(password)
                if not valido:
                    logger.warning(f"Intento de actualizar usuario {id_usuario} con contraseña inválida: {mensaje}")
                    return False, f"Contraseña inválida: {mensaje}"
            
            # 6. Actualizar en base de datos
            self.db.conectar()
            
            if password:
                query = """
                    UPDATE USUARIOS 
                    SET Nombre = %s, 
                        Apellido_Paterno = %s, 
                        Password = %s, 
                        Rol = %s
                    WHERE Id_usuario = %s
                """
                params = (nombre, apellido_paterno, password, rol, id_usuario)
            else:
                query = """
                    UPDATE USUARIOS 
                    SET Nombre = %s, 
                        Apellido_Paterno = %s, 
                        Rol = %s
                    WHERE Id_usuario = %s
                """
                params = (nombre, apellido_paterno, rol, id_usuario)
            
            filas = self.db.ejecutar_update(query, params)
            
            if filas and filas > 0:
                logger.info(f"Usuario ID {id_usuario} actualizado exitosamente")
                return True, "Usuario actualizado exitosamente"
            else:
                logger.warning(f"No se realizaron cambios al actualizar usuario ID {id_usuario}")
                return False, "No se realizaron cambios en la base de datos"

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en actualizar_usuario: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en actualizar_usuario: {e}")
            return False, f"Error inesperado: {str(e)}"

    def actualizar_usuario_completo(
        self,
        id_usuario: int,
        nombre: str,
        apellido_paterno: str,
        rol: str,
        password: Optional[str] = None,
        pregunta_seguridad: Optional[str] = None,
        respuesta_seguridad: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Actualiza todos los datos de un usuario, incluyendo pregunta y respuesta de seguridad.
        
        Args:
            id_usuario: ID del usuario a actualizar
            nombre: Nuevo nombre
            apellido_paterno: Nuevo apellido paterno
            rol: Nuevo rol
            password: Nueva contraseña (opcional)
            pregunta_seguridad: Nueva pregunta de seguridad (opcional)
            respuesta_seguridad: Nueva respuesta de seguridad (opcional)
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # 1. Verificar que el usuario existe
            usuario_actual = self.obtener_usuario_por_id(id_usuario)
            if not usuario_actual:
                logger.warning(f"Intento de actualizar usuario inexistente: ID {id_usuario}")
                return False, f"No existe un usuario con ID {id_usuario}"
            
            # 2. Validar datos
            valido, mensaje = Validadores.validar_nombre(nombre)
            if not valido:
                logger.warning(f"Intento de actualizar usuario {id_usuario} con nombre inválido: {mensaje}")
                return False, f"Nombre inválido: {mensaje}"
            
            valido, mensaje = Validadores.validar_nombre(apellido_paterno)
            if not valido:
                logger.warning(f"Intento de actualizar usuario {id_usuario} con apellido inválido: {mensaje}")
                return False, f"Apellido inválido: {mensaje}"
            
            valido, mensaje = Validadores.validar_rol(rol)
            if not valido:
                logger.warning(f"Intento de actualizar usuario {id_usuario} con rol inválido: {mensaje}")
                return False, f"Rol inválido: {mensaje}"
            
            if password:
                valido, mensaje = Validadores.validar_password(password)
                if not valido:
                    logger.warning(f"Intento de actualizar usuario {id_usuario} con contraseña inválida: {mensaje}")
                    return False, f"Contraseña inválida: {mensaje}"
            
            # 3. Construir la consulta
            self.db.conectar()
            
            query = "UPDATE USUARIOS SET Nombre = %s, Apellido_Paterno = %s, Rol = %s"
            params = [nombre, apellido_paterno, rol]
            
            if password:
                query += ", Password = %s"
                params.append(password)
            
            query += ", Pregunta_Seguridad = %s, Respuesta_Seguridad = %s"
            params.extend([pregunta_seguridad, respuesta_seguridad])
            
            query += " WHERE Id_usuario = %s"
            params.append(id_usuario)
            
            filas = self.db.ejecutar_update(query, tuple(params))
            
            if filas and filas > 0:
                logger.info(f"Usuario ID {id_usuario} actualizado exitosamente (con pregunta de seguridad)")
                return True, "Usuario actualizado exitosamente."
            else:
                logger.warning(f"No se realizaron cambios al actualizar usuario ID {id_usuario}")
                return False, "No se realizaron cambios en la base de datos"

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en actualizar_usuario_completo: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en actualizar_usuario_completo: {e}")
            return False, f"Error inesperado: {str(e)}"

    def eliminar_usuario(self, id_usuario: int) -> Tuple[bool, str]:
        """
        Elimina un usuario del sistema.
        
        PERMISOS:
        - Solo ADMIN puede eliminar usuarios
        """
        try:
            if not self._validar_admin():
                logger.warning(f"Usuario {self.sesion_activa.usuario if self.sesion_activa else 'Desconocido'} intentó eliminar usuario sin permisos")
                return False, "Solo administradores pueden eliminar usuarios"
            
            usuario = self.obtener_usuario_por_id(id_usuario)
            if not usuario:
                logger.warning(f"Intento de eliminar usuario inexistente: ID {id_usuario}")
                return False, f"No existe un usuario con ID {id_usuario}"
            
            if self.sesion_activa and self.sesion_activa.id_usuario == id_usuario:
                logger.warning(f"Usuario {self.sesion_activa.usuario} intentó eliminarse a sí mismo")
                return False, "No puedes eliminar tu propia cuenta mientras está activa"
            
            self.db.conectar()
            query = "DELETE FROM USUARIOS WHERE Id_usuario = %s"
            filas = self.db.ejecutar_update(query, (id_usuario,))
            
            if filas and filas > 0:
                logger.info(f"Usuario '{usuario.usuario}' (ID {id_usuario}) eliminado exitosamente")
                return True, f"Usuario '{usuario.usuario}' eliminado exitosamente"
            else:
                logger.warning(f"No se pudo eliminar el usuario ID {id_usuario}")
                return False, "No se pudo eliminar el usuario"

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en eliminar_usuario: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en eliminar_usuario: {e}")
            return False, f"Error inesperado: {str(e)}"

    # ============================================================
    # RECUPERACIÓN DE CONTRASEÑA
    # ============================================================
    
    def verificar_respuesta_seguridad(self, id_usuario: int, respuesta: str) -> bool:
        """
        Verifica si la respuesta de seguridad es correcta.
        La comparación se hace en texto plano (para proyecto académico).
        
        Returns:
            bool: True si es correcta, False si no
        """
        try:
            usuario = self.obtener_usuario_por_id(id_usuario)
            if not usuario:
                return False
            if not usuario.respuesta_seguridad:
                return False
            return respuesta == usuario.respuesta_seguridad
        except Exception as e:
            logger.error(f"Error al verificar respuesta de seguridad: {e}")
            return False

    def actualizar_password_por_id(self, id_usuario: int, nueva_password: str) -> Tuple[bool, str]:
        """
        Actualiza la contraseña de un usuario por su ID.
        
        Args:
            id_usuario: ID del usuario
            nueva_password: Nueva contraseña en texto plano
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Validar contraseña
            valido, mensaje = Validadores.validar_password(nueva_password)
            if not valido:
                return False, mensaje

            self.db.conectar()
            query = "UPDATE USUARIOS SET Password = %s WHERE Id_usuario = %s"
            filas = self.db.ejecutar_update(query, (nueva_password, id_usuario))
            
            if filas and filas > 0:
                logger.info(f"Contraseña actualizada para usuario ID: {id_usuario}")
                return True, "Contraseña actualizada exitosamente."
            else:
                return False, "No se pudo actualizar la contraseña."
        except Exception as e:
            logger.error(f"Error al actualizar contraseña: {e}")
            return False, f"Error: {str(e)}"

    # ============================================================
    # CAMBIOS DE CONFIGURACIÓN - SOLO ADMIN
    # ============================================================
    
    def cambiar_password(self, usuario: str, password_actual: str, password_nueva: str) -> Tuple[bool, str]:
        """
        Cambia la contraseña de un usuario (método clásico con contraseña actual).
        """
        try:
            valido, mensaje = Validadores.validar_password(password_nueva)
            if not valido:
                logger.warning(f"Intento de cambio de contraseña con nueva contraseña inválida: {mensaje}")
                return False, mensaje
            
            exito, msg, usuario_obj = self.iniciar_sesion(usuario, password_actual)
            if not exito:
                logger.warning(f"Intento de cambio de contraseña fallido: contraseña actual incorrecta para '{usuario}'")
                return False, "Contraseña actual incorrecta"
            
            self.db.conectar()
            query = "UPDATE USUARIOS SET Password = %s WHERE Usuario = %s"
            filas = self.db.ejecutar_update(query, (password_nueva, usuario))
            
            if filas and filas > 0:
                logger.info(f"Contraseña actualizada para usuario '{usuario}'")
                return True, "Contraseña actualizada exitosamente"
            else:
                logger.warning(f"Error al actualizar contraseña para usuario '{usuario}'")
                return False, "Error al actualizar contraseña"

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en cambiar_password: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en cambiar_password: {e}")
            return False, f"Error inesperado: {str(e)}"

    def cambiar_rol(self, id_usuario: int, nuevo_rol: str) -> Tuple[bool, str]:
        """
        Cambia el rol de un usuario.
        
        PERMISOS:
        - Solo ADMIN puede cambiar roles
        """
        try:
            if not self._validar_admin():
                logger.warning(f"Usuario {self.sesion_activa.usuario if self.sesion_activa else 'Desconocido'} intentó cambiar rol sin permisos")
                return False, "❌ Solo administradores pueden cambiar roles"
            
            valido, mensaje = Validadores.validar_rol(nuevo_rol)
            if not valido:
                logger.warning(f"Intento de cambio de rol inválido para ID {id_usuario}: {mensaje}")
                return False, f"Rol inválido: {mensaje}"
            
            usuario = self.obtener_usuario_por_id(id_usuario)
            if not usuario:
                logger.warning(f"Intento de cambiar rol de usuario inexistente: ID {id_usuario}")
                return False, f"No existe un usuario con ID {id_usuario}"
            
            self.db.conectar()
            query = "UPDATE USUARIOS SET Rol = %s WHERE Id_usuario = %s"
            filas = self.db.ejecutar_update(query, (nuevo_rol, id_usuario))
            
            if filas and filas > 0:
                logger.info(f"Rol actualizado para usuario '{usuario.usuario}': {nuevo_rol}")
                return True, f"Rol actualizado a '{nuevo_rol}' exitosamente"
            else:
                logger.warning(f"Error al actualizar rol para usuario ID {id_usuario}")
                return False, "Error al actualizar rol"

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en cambiar_rol: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en cambiar_rol: {e}")
            return False, f"Error inesperado: {str(e)}"

    # ============================================================
    # BÚSQUEDAS Y CONSULTAS
    # ============================================================
    
    def usuario_existe(self, usuario: str) -> bool:
        """
        Verifica si un usuario ya existe en la BD.
        """
        try:
            self.db.conectar()
            query = "SELECT COUNT(*) FROM USUARIOS WHERE Usuario = %s"
            resultados = self.db.ejecutar_query(query, (usuario,))
            
            if resultados and resultados[0][0] > 0:
                return True
            return False

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en usuario_existe: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado en usuario_existe: {e}")
            return False

    def obtener_usuario_por_id(self, id_usuario: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID.
        """
        try:
            self.db.conectar()
            query = "SELECT * FROM USUARIOS WHERE Id_usuario = %s"
            resultados = self.db.ejecutar_query(query, (id_usuario,))
            
            if resultados and len(resultados) > 0:
                return Usuario.from_db_row(resultados[0])
            return None

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en obtener_usuario_por_id: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en obtener_usuario_por_id: {e}")
            return None

    def obtener_usuario_por_nombre(self, usuario: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su nombre de usuario.
        """
        try:
            self.db.conectar()
            query = "SELECT * FROM USUARIOS WHERE Usuario = %s"
            resultados = self.db.ejecutar_query(query, (usuario,))
            
            if resultados and len(resultados) > 0:
                return Usuario.from_db_row(resultados[0])
            return None

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en obtener_usuario_por_nombre: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en obtener_usuario_por_nombre: {e}")
            return None

    def listar_usuarios(self, rol: Optional[str] = None) -> List[Usuario]:
        """
        Lista todos los usuarios del sistema.
        """
        try:
            self.db.conectar()
            
            if rol:
                query = "SELECT * FROM USUARIOS WHERE Rol = %s ORDER BY Fecha_Registro DESC"
                resultados = self.db.ejecutar_query(query, (rol,))
            else:
                query = "SELECT * FROM USUARIOS ORDER BY Fecha_Registro DESC"
                resultados = self.db.ejecutar_query(query)
            
            if resultados:
                usuarios = [Usuario.from_db_row(row) for row in resultados]
                logger.info(f"Listado de usuarios: {len(usuarios)} encontrados")
                return usuarios
            return []

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en listar_usuarios: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en listar_usuarios: {e}")
            return []

    def contar_usuarios(self, rol: Optional[str] = None) -> int:
        """
        Cuenta el número de usuarios en el sistema.
        """
        try:
            self.db.conectar()
            
            if rol:
                query = "SELECT COUNT(*) FROM USUARIOS WHERE Rol = %s"
                resultados = self.db.ejecutar_query(query, (rol,))
            else:
                query = "SELECT COUNT(*) FROM USUARIOS"
                resultados = self.db.ejecutar_query(query)
            
            if resultados:
                count = resultados[0][0]
                logger.info(f"Conteo de usuarios: {count} en total")
                return count
            return 0

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en contar_usuarios: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error inesperado en contar_usuarios: {e}")
            return 0


# ==================== EJEMPLO DE USO ====================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJEMPLO DE USO - AuthController v2.5")
    print("CON GESTIÓN COMPLETA DE PREGUNTA/RESPUESTA DE SEGURIDAD")
    print("="*60 + "\n")
    
    auth = AuthController()
    
    # Ejemplo 1: Registrar usuario con pregunta de seguridad
    print("1️⃣ Registrando usuario con pregunta de seguridad...")
    exito, msg, id_usr = auth.registrar_usuario(
        usuario="test_user",
        nombre="Test",
        apellido_paterno="User",
        password="test1234",
        rol="empleado",
        pregunta_seguridad="¿Cuál es el nombre de tu primera mascota?",
        respuesta_seguridad="Firulais"
    )
    print(f"   {msg}\n")
    
    if exito and id_usr:
        # Ejemplo 2: Verificar respuesta de seguridad
        print("2️⃣ Verificando respuesta de seguridad...")
        es_correcta = auth.verificar_respuesta_seguridad(id_usr, "Firulais")
        print(f"   Respuesta correcta: {es_correcta}\n")
        
        if es_correcta:
            # Ejemplo 3: Restablecer contraseña
            print("3️⃣ Restableciendo contraseña...")
            exito, msg = auth.actualizar_password_por_id(id_usr, "nueva1234")
            print(f"   {msg}\n")
            
            # Ejemplo 4: Actualizar todo el usuario
            print("4️⃣ Actualizando usuario completo...")
            exito, msg = auth.actualizar_usuario_completo(
                id_usuario=id_usr,
                nombre="Test Actualizado",
                apellido_paterno="User",
                rol="empleado",
                pregunta_seguridad="¿Cuál es tu color favorito?",
                respuesta_seguridad="Azul"
            )
            print(f"   {msg}\n")
    
    print("="*60 + "\n")