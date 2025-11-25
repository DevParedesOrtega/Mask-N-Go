"""
Módulo: auth_controller.py
Ubicación: controllers/auth_controller.py
Descripción: Controlador para autenticación de usuarios
Sistema: Renta y Venta de Disfraces
Versión: 2.0 - Con métodos de actualización y eliminación
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
from models.usuario import Usuario
from utils.validadores import Validadores
from typing import Optional, Tuple, List
from datetime import datetime


class AuthController:
    """
    Controlador para manejar autenticación de usuarios.
    
    Gestiona:
    - Registro de nuevos usuarios
    - Inicio de sesión
    - Validación de credenciales
    - Gestión de sesión activa
    - Actualización de usuarios
    - Eliminación de usuarios
    """
    
    def __init__(self):
        """Inicializa el controlador con conexión a BD."""
        self.db = ConexionDB()
        self.sesion_activa = None  # Usuario actualmente logueado
    
    def registrar_usuario(
        self,
        usuario: str,
        nombre: str,
        apellido_paterno: str,
        password: str,
        rol: str = 'empleado'
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Registra un nuevo usuario en el sistema.
        
        Args:
            usuario: Nombre de usuario para login
            nombre: Nombre del usuario
            apellido_paterno: Apellido paterno
            password: Contraseña en texto plano
            rol: Rol del usuario (default: 'empleado')
        
        Returns:
            Tuple[bool, str, Optional[int]]: (éxito, mensaje, id_usuario)
        
        Example:
            >>> auth = AuthController()
            >>> exito, msg, id = auth.registrar_usuario('juan123', 'Juan', 'Pérez', 'pass1234', 'empleado')
        """
        try:
            # 1. Validar usuario
            valido, mensaje = Validadores.validar_usuario(usuario)
            if not valido:
                return False, mensaje, None
            
            # 2. Validar nombre
            valido, mensaje = Validadores.validar_nombre(nombre)
            if not valido:
                return False, mensaje, None
            
            # 3. Validar apellido
            valido, mensaje = Validadores.validar_nombre(apellido_paterno)
            if not valido:
                return False, f"Apellido: {mensaje}", None
            
            # 4. Validar contraseña
            valido, mensaje = Validadores.validar_password(password)
            if not valido:
                return False, mensaje, None
            
            # 5. Validar rol
            valido, mensaje = Validadores.validar_rol(rol)
            if not valido:
                return False, mensaje, None
            
            # 6. Verificar que el usuario no exista
            if self.usuario_existe(usuario):
                return False, f"El usuario '{usuario}' ya existe", None
            
            # 7. Insertar en base de datos
            self.db.conectar()
            query = """
                INSERT INTO USUARIOS (Usuario, Nombre, Apellido_Paterno, Password, Rol)
                VALUES (%s, %s, %s, %s, %s)
            """
            nuevo_id = self.db.ejecutar_insert(
                query,
                (usuario, nombre, apellido_paterno, password, rol)
            )
            
            if nuevo_id:
                print(f"✅ Usuario '{usuario}' registrado exitosamente con ID {nuevo_id}")
                return True, "Usuario registrado exitosamente", nuevo_id
            else:
                return False, "Error al registrar usuario en la base de datos", None
        
        except Exception as e:
            print(f"❌ Error en registrar_usuario: {e}")
            return False, f"Error inesperado: {str(e)}", None
    
    def actualizar_usuario(
        self,
        id_usuario: int,
        nombre: str,
        apellido_paterno: str,
        rol: str,
        password: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Actualiza los datos de un usuario existente.
        
        Args:
            id_usuario: ID del usuario a actualizar
            nombre: Nuevo nombre
            apellido_paterno: Nuevo apellido paterno
            rol: Nuevo rol
            password: Nueva contraseña (opcional, None si no se cambia)
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        
        Example:
            >>> auth = AuthController()
            >>> exito, msg = auth.actualizar_usuario(1, 'Juan', 'Pérez', 'admin', 'nueva_pass123')
        """
        try:
            # 1. Verificar que el usuario existe
            usuario_actual = self.obtener_usuario_por_id(id_usuario)
            if not usuario_actual:
                return False, f"No existe un usuario con ID {id_usuario}"
            
            # 2. Validar nombre
            valido, mensaje = Validadores.validar_nombre(nombre)
            if not valido:
                return False, f"Nombre inválido: {mensaje}"
            
            # 3. Validar apellido
            valido, mensaje = Validadores.validar_nombre(apellido_paterno)
            if not valido:
                return False, f"Apellido inválido: {mensaje}"
            
            # 4. Validar rol
            valido, mensaje = Validadores.validar_rol(rol)
            if not valido:
                return False, f"Rol inválido: {mensaje}"
            
            # 5. Validar contraseña si se proporciona
            if password:
                valido, mensaje = Validadores.validar_password(password)
                if not valido:
                    return False, f"Contraseña inválida: {mensaje}"
            
            # 6. Actualizar en base de datos
            self.db.conectar()
            
            if password:
                # Actualizar con nueva contraseña
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
                # Actualizar sin cambiar contraseña
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
                print(f"✅ Usuario ID {id_usuario} actualizado exitosamente")
                return True, "Usuario actualizado exitosamente"
            else:
                return False, "No se realizaron cambios en la base de datos"
        
        except Exception as e:
            print(f"❌ Error en actualizar_usuario: {e}")
            return False, f"Error inesperado: {str(e)}"
    
    def eliminar_usuario(self, id_usuario: int) -> Tuple[bool, str]:
        """
        Elimina un usuario del sistema.
        
        Args:
            id_usuario: ID del usuario a eliminar
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        
        Example:
            >>> auth = AuthController()
            >>> exito, msg = auth.eliminar_usuario(5)
        """
        try:
            # 1. Verificar que el usuario existe
            usuario = self.obtener_usuario_por_id(id_usuario)
            if not usuario:
                return False, f"No existe un usuario con ID {id_usuario}"
            
            # 2. Verificar que no es el usuario de la sesión activa
            if self.sesion_activa and self.sesion_activa.id_usuario == id_usuario:
                return False, "No puedes eliminar tu propia cuenta mientras está activa"
            
            # 3. Eliminar de la base de datos
            self.db.conectar()
            query = "DELETE FROM USUARIOS WHERE Id_usuario = %s"
            filas = self.db.ejecutar_update(query, (id_usuario,))
            
            if filas and filas > 0:
                print(f"✅ Usuario '{usuario.usuario}' (ID {id_usuario}) eliminado exitosamente")
                return True, f"Usuario '{usuario.usuario}' eliminado exitosamente"
            else:
                return False, "No se pudo eliminar el usuario"
        
        except Exception as e:
            print(f"❌ Error en eliminar_usuario: {e}")
            return False, f"Error inesperado: {str(e)}"
    
    def iniciar_sesion(self, usuario: str, password: str) -> Tuple[bool, str, Optional[Usuario]]:
        """
        Inicia sesión validando credenciales.
        
        Args:
            usuario: Nombre de usuario
            password: Contraseña
        
        Returns:
            Tuple[bool, str, Optional[Usuario]]: (éxito, mensaje, objeto_usuario)
        
        Example:
            >>> auth = AuthController()
            >>> exito, msg, usuario = auth.iniciar_sesion('admin', 'admin123')
            >>> if exito:
            >>>     print(f"Bienvenido {usuario.nombre_completo()}")
        """
        try:
            # 1. Validar que no estén vacíos
            if not usuario or not password:
                return False, "Usuario y contraseña son requeridos", None
            
            # 2. Buscar usuario en la BD
            self.db.conectar()
            query = "SELECT * FROM USUARIOS WHERE Usuario = %s"
            resultados = self.db.ejecutar_query(query, (usuario,))
            
            if not resultados or len(resultados) == 0:
                return False, "Usuario o contraseña incorrectos", None
            
            # 3. Verificar contraseña
            usuario_db = Usuario.from_db_row(resultados[0])
            
            if usuario_db.password != password:
                return False, "Usuario o contraseña incorrectos", None
            
            # 4. Crear sesión activa
            self.sesion_activa = usuario_db
            
            print(f"✅ Sesión iniciada: {usuario_db.nombre_completo()} ({usuario_db.rol})")
            return True, "Inicio de sesión exitoso", usuario_db
        
        except Exception as e:
            print(f"❌ Error en iniciar_sesion: {e}")
            return False, f"Error inesperado: {str(e)}", None
    
    def cerrar_sesion(self) -> bool:
        """
        Cierra la sesión activa.
        
        Returns:
            bool: True si había sesión activa, False si no
        """
        if self.sesion_activa:
            print(f"🔌 Sesión cerrada: {self.sesion_activa.nombre_completo()}")
            self.sesion_activa = None
            return True
        else:
            print("ℹ️ No hay sesión activa")
            return False
    
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
    
    def usuario_existe(self, usuario: str) -> bool:
        """
        Verifica si un usuario ya existe en la BD.
        
        Args:
            usuario: Nombre de usuario a verificar
        
        Returns:
            bool: True si existe, False si no
        """
        try:
            self.db.conectar()
            query = "SELECT COUNT(*) FROM USUARIOS WHERE Usuario = %s"
            resultados = self.db.ejecutar_query(query, (usuario,))
            
            if resultados and resultados[0][0] > 0:
                return True
            return False
        
        except Exception as e:
            print(f"❌ Error en usuario_existe: {e}")
            return False
    
    def obtener_usuario_por_id(self, id_usuario: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            id_usuario: ID del usuario
        
        Returns:
            Optional[Usuario]: Objeto Usuario o None si no existe
        """
        try:
            self.db.conectar()
            query = "SELECT * FROM USUARIOS WHERE Id_usuario = %s"
            resultados = self.db.ejecutar_query(query, (id_usuario,))
            
            if resultados and len(resultados) > 0:
                return Usuario.from_db_row(resultados[0])
            return None
        
        except Exception as e:
            print(f"❌ Error en obtener_usuario_por_id: {e}")
            return None
    
    def obtener_usuario_por_nombre(self, usuario: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su nombre de usuario.
        
        Args:
            usuario: Nombre de usuario
        
        Returns:
            Optional[Usuario]: Objeto Usuario o None si no existe
        """
        try:
            self.db.conectar()
            query = "SELECT * FROM USUARIOS WHERE Usuario = %s"
            resultados = self.db.ejecutar_query(query, (usuario,))
            
            if resultados and len(resultados) > 0:
                return Usuario.from_db_row(resultados[0])
            return None
        
        except Exception as e:
            print(f"❌ Error en obtener_usuario_por_nombre: {e}")
            return None
    
    def listar_usuarios(self, rol: Optional[str] = None) -> List[Usuario]:
        """
        Lista todos los usuarios del sistema.
        
        Args:
            rol: Filtrar por rol (opcional)
        
        Returns:
            list: Lista de objetos Usuario
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
                return [Usuario.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en listar_usuarios: {e}")
            return []
    
    def contar_usuarios(self, rol: Optional[str] = None) -> int:
        """
        Cuenta el número de usuarios en el sistema.
        
        Args:
            rol: Filtrar por rol (opcional)
        
        Returns:
            int: Cantidad de usuarios
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
                return resultados[0][0]
            return 0
        
        except Exception as e:
            print(f"❌ Error en contar_usuarios: {e}")
            return 0
    
    def cambiar_password(self, usuario: str, password_actual: str, password_nueva: str) -> Tuple[bool, str]:
        """
        Cambia la contraseña de un usuario.
        
        Args:
            usuario: Nombre de usuario
            password_actual: Contraseña actual
            password_nueva: Nueva contraseña
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # 1. Validar nueva contraseña
            valido, mensaje = Validadores.validar_password(password_nueva)
            if not valido:
                return False, mensaje
            
            # 2. Verificar contraseña actual
            exito, msg, usuario_obj = self.iniciar_sesion(usuario, password_actual)
            if not exito:
                return False, "Contraseña actual incorrecta"
            
            # 3. Actualizar contraseña
            self.db.conectar()
            query = "UPDATE USUARIOS SET Password = %s WHERE Usuario = %s"
            filas = self.db.ejecutar_update(query, (password_nueva, usuario))
            
            if filas and filas > 0:
                print(f"✅ Contraseña actualizada para usuario '{usuario}'")
                return True, "Contraseña actualizada exitosamente"
            else:
                return False, "Error al actualizar contraseña"
        
        except Exception as e:
            print(f"❌ Error en cambiar_password: {e}")
            return False, f"Error inesperado: {str(e)}"
    
    def cambiar_rol(self, id_usuario: int, nuevo_rol: str) -> Tuple[bool, str]:
        """
        Cambia el rol de un usuario.
        
        Args:
            id_usuario: ID del usuario
            nuevo_rol: Nuevo rol ('admin' o 'empleado')
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # 1. Validar rol
            valido, mensaje = Validadores.validar_rol(nuevo_rol)
            if not valido:
                return False, mensaje
            
            # 2. Verificar que el usuario existe
            usuario = self.obtener_usuario_por_id(id_usuario)
            if not usuario:
                return False, f"No existe un usuario con ID {id_usuario}"
            
            # 3. Actualizar rol
            self.db.conectar()
            query = "UPDATE USUARIOS SET Rol = %s WHERE Id_usuario = %s"
            filas = self.db.ejecutar_update(query, (nuevo_rol, id_usuario))
            
            if filas and filas > 0:
                print(f"✅ Rol actualizado para usuario '{usuario.usuario}': {nuevo_rol}")
                return True, f"Rol actualizado a '{nuevo_rol}' exitosamente"
            else:
                return False, "Error al actualizar rol"
        
        except Exception as e:
            print(f"❌ Error en cambiar_rol: {e}")
            return False, f"Error inesperado: {str(e)}"


# ==================== EJEMPLO DE USO ====================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJEMPLO DE USO - AuthController v2.0")
    print("="*60 + "\n")
    
    auth = AuthController()
    
    # Ejemplo 1: Registrar usuario
    print("1️⃣ Registrando usuario...")
    exito, msg, id = auth.registrar_usuario(
        usuario="test_actualizado",
        nombre="Usuario",
        apellido_paterno="De Prueba",
        password="test1234",
        rol="empleado"
    )
    print(f"   {msg}\n")
    
    if exito and id:
        # Ejemplo 2: Actualizar usuario
        print("2️⃣ Actualizando usuario...")
        exito_act, msg_act = auth.actualizar_usuario(
            id_usuario=id,
            nombre="Usuario Actualizado",
            apellido_paterno="Modificado",
            rol="admin",
            password="nueva_pass123"
        )
        print(f"   {msg_act}\n")
        
        # Ejemplo 3: Listar usuarios
        print("3️⃣ Listando usuarios...")
        usuarios = auth.listar_usuarios()
        print(f"   Total usuarios: {len(usuarios)}")
        for u in usuarios[:3]:
            print(f"   - {u.usuario} ({u.rol})")
        print()
        
        # Ejemplo 4: Eliminar usuario
        print("4️⃣ Eliminando usuario de prueba...")
        exito_del, msg_del = auth.eliminar_usuario(id)
        print(f"   {msg_del}\n")
    
    print("="*60 + "\n")