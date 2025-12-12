"""
Módulo: usuario.py
Ubicación: models/usuario.py
Descripción: Modelo de datos para usuarios del sistema
Sistema: MaskNGO - Renta y Venta de Disfraces
Versión: 2.2 - Con soporte para pregunta de seguridad
"""

from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import logging
from utils.logger_config import setup_logger


# Configurar logging
logger = setup_logger('usuario_model', 'logs/usuarios_model.log')


class Usuario:
    """
    Clase que representa un usuario del sistema MaskNGO.
    
    Attributes:
        id_usuario (int): ID único del usuario (PK)
        usuario (str): Nombre de usuario para login (UNIQUE)
        nombre (str): Nombre del usuario
        apellido_paterno (str): Apellido paterno
        password (str): Contraseña (texto plano)
        rol (str): Rol del usuario (admin, empleado)
        fecha_registro (datetime): Fecha de creación de la cuenta
        pregunta_seguridad (str, opcional): Pregunta de seguridad para recuperación
        respuesta_seguridad (str, opcional): Respuesta de seguridad (texto plano)
        historial_estados (list): Historial de cambios de estado
    
    BD Campos (tabla USUARIOS):
        - Id_usuario (PK, int, auto_increment)
        - Usuario (varchar 255, UNIQUE)
        - Nombre (text)
        - Apellido_Paterno (text)
        - Password (varchar 255)
        - Pregunta_Seguridad (varchar 255, NULL)
        - Respuesta_Seguridad (varchar 255, NULL)
        - Rol (enum empleado/admin, default empleado)
        - Fecha_Registro (datetime, default CURRENT_TIMESTAMP)
    """
    
    # Roles válidos
    ROLES_VALIDOS: Tuple[str, ...] = ('admin', 'empleado')
    
    def __init__(
        self,
        usuario: str,
        nombre: str,
        apellido_paterno: str,
        password: str,
        id_usuario: Optional[int] = None,
        rol: str = 'empleado',
        fecha_registro: Optional[datetime] = None,
        pregunta_seguridad: Optional[str] = None,     # ← NUEVO
        respuesta_seguridad: Optional[str] = None     # ← NUEVO
    ) -> None:
        """
        Constructor de Usuario.
        
        Args:
            usuario: Nombre de usuario para login (UNIQUE)
            nombre: Nombre del usuario
            apellido_paterno: Apellido paterno
            password: Contraseña en texto plano
            id_usuario: ID del usuario (generado por BD)
            rol: Rol del usuario (default: 'empleado')
            fecha_registro: Fecha de registro (default: ahora)
            pregunta_seguridad: Pregunta de seguridad (opcional)
            respuesta_seguridad: Respuesta de seguridad (opcional)
        """
        # Validaciones
        if rol not in self.ROLES_VALIDOS:
            raise ValueError(f"Rol '{rol}' no es válido. Roles válidos: {', '.join(self.ROLES_VALIDOS)}")
        
        if not usuario or len(usuario.strip()) == 0:
            raise ValueError("El usuario no puede estar vacío")
        
        if len(usuario) < 3:
            raise ValueError("El usuario debe tener al menos 3 caracteres")
        
        if len(usuario) > 255:
            raise ValueError("El usuario no puede exceder 255 caracteres")
        
        if not nombre or len(nombre.strip()) == 0:
            raise ValueError("El nombre no puede estar vacío")
        
        if not apellido_paterno or len(apellido_paterno.strip()) == 0:
            raise ValueError("El apellido paterno no puede estar vacío")
        
        if not password or len(password.strip()) == 0:
            raise ValueError("La contraseña no puede estar vacía")
        
        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")

        self.id_usuario: Optional[int] = id_usuario
        self.usuario: str = usuario
        self.nombre: str = nombre
        self.apellido_paterno: str = apellido_paterno
        self.password: str = password
        self.rol: str = rol
        self.fecha_registro: datetime = fecha_registro or datetime.now()
        self.pregunta_seguridad: Optional[str] = pregunta_seguridad      # ← NUEVO
        self.respuesta_seguridad: Optional[str] = respuesta_seguridad    # ← NUEVO
        self.historial_estados: list = []

        logger.info(f"Usuario creado: {self.usuario} ({self.nombre_completo()})")

    # ============================================================
    # REPRESENTACIÓN Y COMPARACIÓN
    # ============================================================
    
    def __str__(self) -> str:
        """Representación legible del usuario."""
        return f"Usuario({self.usuario}, {self.nombre_completo()}, Rol: {self.rol})"
    
    def __repr__(self) -> str:
        """Representación técnica del objeto."""
        return self.__str__()
    
    def __eq__(self, other: Any) -> bool:
        """Compara si dos usuarios son el mismo por ID."""
        if not isinstance(other, Usuario):
            return False
        return self.id_usuario == other.id_usuario
    
    def __hash__(self) -> int:
        """Hash para usar en sets/dicts."""
        return hash(self.id_usuario) if self.id_usuario else hash(id(self))
    
    def __lt__(self, other: 'Usuario') -> bool:
        """Compara usuarios por nombre de usuario (para ordenamiento)."""
        if not isinstance(other, Usuario):
            return NotImplemented
        return self.usuario.lower() < other.usuario.lower()
    
    def __le__(self, other: 'Usuario') -> bool:
        """Menor o igual que."""
        return self == other or self < other
    
    def __gt__(self, other: 'Usuario') -> bool:
        """Mayor que."""
        return not self <= other
    
    def __ge__(self, other: 'Usuario') -> bool:
        """Mayor o igual que."""
        return not self < other

    # ============================================================
    # CONVERSIÓN A DICCIONARIO
    # ============================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el objeto Usuario a diccionario.
        
        Returns:
            Dict: Diccionario con los datos del usuario
        """
        return {
            'id_usuario': self.id_usuario,
            'usuario': self.usuario,
            'nombre': self.nombre,
            'apellido_paterno': self.apellido_paterno,
            'password': self.password,
            'pregunta_seguridad': self.pregunta_seguridad,      # ← NUEVO
            'respuesta_seguridad': self.respuesta_seguridad,    # ← NUEVO
            'rol': self.rol,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'historial_estados': self.historial_estados
        }

    # ============================================================
    # MÉTODOS DE INFORMACIÓN BÁSICA
    # ============================================================
    
    def nombre_completo(self) -> str:
        """
        Obtiene el nombre completo del usuario.
        
        Returns:
            str: Nombre completo (Nombre + Apellido)
        """
        return f"{self.nombre} {self.apellido_paterno}".strip()
    
    def dias_desde_registro(self) -> int:
        """
        Calcula cuántos días lleva el usuario en el sistema.
        
        Returns:
            int: Número de días desde registro
        """
        if not self.fecha_registro:
            return 0
        
        delta = datetime.now() - self.fecha_registro
        return delta.days

    # ============================================================
    # MÉTODOS DE ROL Y PERMISOS
    # ============================================================
    
    def es_admin(self) -> bool:
        """
        Verifica si el usuario es administrador.
        
        Returns:
            bool: True si es admin, False si no
        """
        return self.rol == 'admin'
    
    def es_empleado(self) -> bool:
        """
        Verifica si el usuario es empleado.
        
        Returns:
            bool: True si es empleado, False si no
        """
        return self.rol == 'empleado'
    
    def puede_ver_reportes(self) -> bool:
        """
        Verifica si el usuario puede ver reportes.
        
        Permiso: Solo administradores
        
        Returns:
            bool: True si puede ver reportes, False si no
        """
        return self.es_admin()
    
    def puede_eliminar_datos(self) -> bool:
        """
        Verifica si el usuario puede eliminar datos.
        
        Permiso: Solo administradores
        
        Returns:
            bool: True si puede eliminar, False si no
        """
        return self.es_admin()
    
    def puede_crear_usuarios(self) -> bool:
        """
        Verifica si el usuario puede crear nuevos usuarios.
        
        Permiso: Solo administradores
        
        Returns:
            bool: True si puede crear usuarios, False si no
        """
        return self.es_admin()
    
    def puede_modificar_usuarios(self) -> bool:
        """
        Verifica si el usuario puede modificar usuarios.
        
        Permiso: Solo administradores
        
        Returns:
            bool: True si puede modificar usuarios, False si no
        """
        return self.es_admin()
    
    def puede_registrar_rentas(self) -> bool:
        """
        Verifica si el usuario puede registrar rentas.
        
        Permiso: Todos los usuarios
        
        Returns:
            bool: True siempre (todos pueden registrar rentas)
        """
        return True
    
    def puede_registrar_ventas(self) -> bool:
        """
        Verifica si el usuario puede registrar ventas.
        
        Permiso: Todos los usuarios
        
        Returns:
            bool: True siempre (todos pueden registrar ventas)
        """
        return True

    # ============================================================
    # MÉTODOS DE AUDITORÍA
    # ============================================================

    def cambiar_rol(self, nuevo_rol: str, usuario: Optional[str] = None, motivo: Optional[str] = None) -> bool:
        """
        Cambia el rol del usuario y registra el cambio en el historial.

        Args:
            nuevo_rol: Nuevo rol del usuario
            usuario: Usuario que realiza el cambio (opcional)
            motivo: Motivo del cambio (opcional)

        Returns:
            bool: True si se cambió, False si no
        """
        if self.rol == nuevo_rol:
            logger.info(f"Rol no cambiado: {self.usuario} ya está en rol '{nuevo_rol}'")
            return False

        if nuevo_rol not in self.ROLES_VALIDOS:
            logger.warning(f"Intento de cambiar rol a valor inválido: {nuevo_rol}")
            return False

        antiguo_rol = self.rol
        self.rol = nuevo_rol

        # Registrar en historial
        registro = {
            'fecha': self._get_current_datetime(),
            'antiguo_rol': antiguo_rol,
            'nuevo_rol': nuevo_rol,
            'usuario': usuario,
            'motivo': motivo
        }
        self.historial_estados.append(registro)

        logger.info(f"Rol cambiado para {self.usuario}: '{antiguo_rol}' → '{nuevo_rol}' (por {usuario or 'sistema'}, motivo: {motivo or 'sin especificar'})")
        return True

    def obtener_historial_estados(self) -> list:
        """
        Obtiene el historial de cambios de rol del usuario.

        Returns:
            list: Lista de diccionarios con cambios de rol
        """
        return self.historial_estados

    def ultimo_cambio_rol(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el último cambio de rol del usuario.

        Returns:
            dict o None: Último registro de cambio de rol
        """
        if self.historial_estados:
            return self.historial_estados[-1]
        return None

    def _get_current_datetime(self):
        """Obtiene la fecha/hora actual. Aislado para facilitar pruebas."""
        return datetime.now()

    # ============================================================
    # MÉTODOS DE AUTENTICACIÓN
    # ============================================================

    def verificar_contrasena(self, contrasena: str) -> bool:
        """
        Verifica si la contraseña proporcionada coincide con la del usuario.

        Args:
            contrasena: Contraseña a verificar

        Returns:
            bool: True si coincide, False si no
        """
        if not contrasena:
            logger.warning(f"Intento de autenticación con contraseña vacía para usuario {self.usuario}")
            return False

        if self.password == contrasena:
            logger.debug(f"Autenticación exitosa para usuario {self.usuario}")
            return True
        else:
            logger.warning(f"Autenticación fallida para usuario {self.usuario}")
            return False

    # ============================================================
    # MÉTODOS DE VALIDACIÓN
    # ============================================================
    
    def validar_rol(self) -> bool:
        """
        Valida que el rol sea uno de los válidos.
        
        Returns:
            bool: True si es válido, False si no
        """
        return self.rol in self.ROLES_VALIDOS
    
    def validar_usuario(self) -> Tuple[bool, str]:
        """
        Valida que el usuario tenga datos correctos.
        
        Returns:
            Tuple[bool, str]: (es_válido, mensaje)
        """
        if not self.usuario or len(self.usuario.strip()) == 0:
            return False, "El usuario no puede estar vacío"
        
        if len(self.usuario) < 3:
            return False, "El usuario debe tener al menos 3 caracteres"
        
        if len(self.usuario) > 255:
            return False, "El usuario no puede exceder 255 caracteres"
        
        if not self.nombre or len(self.nombre.strip()) == 0:
            return False, "El nombre no puede estar vacío"
        
        if not self.apellido_paterno or len(self.apellido_paterno.strip()) == 0:
            return False, "El apellido paterno no puede estar vacío"
        
        if not self.password or len(self.password.strip()) == 0:
            return False, "La contraseña no puede estar vacía"
        
        if len(self.password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        if not self.validar_rol():
            return False, f"Rol '{self.rol}' no es válido. Roles válidos: {', '.join(self.ROLES_VALIDOS)}"
        
        return True, "Usuario válido"

    # ============================================================
    # MÉTODOS DE REPORTE
    # ============================================================
    
    def resumen_estado(self) -> str:
        """
        Genera un resumen legible del estado del usuario.
        
        Returns:
            str: Resumen en formato texto
        """
        rol_emoji: str = "👑" if self.es_admin() else "👤"
        
        lineas: list = [
            f"{rol_emoji} USUARIO: {self.usuario}",
            f"├─ 👤 Nombre: {self.nombre_completo()}",
            f"├─ 🔐 Rol: {self.rol.upper()}",
            f"├─ 📅 Registrado hace: {self.dias_desde_registro()} días",
            f"├─ 📆 Fecha registro: {self.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')}",
            f"├─ ✓ Puede registrar rentas: {'Sí' if self.puede_registrar_rentas() else 'No'}",
            f"├─ ✓ Puede registrar ventas: {'Sí' if self.puede_registrar_ventas() else 'No'}",
            f"├─ 📊 Puede ver reportes: {'Sí' if self.puede_ver_reportes() else 'No'}",
            f"└─ 🗑️  Puede eliminar datos: {'Sí' if self.puede_eliminar_datos() else 'No'}"
        ]
        
        logger.debug(f"Resumen de estado generado para usuario {self.usuario}")
        return "\n".join(lineas)
    
    def resumen_corto(self) -> str:
        """
        Genera un resumen corto en una línea.
        
        Returns:
            str: Resumen corto
        """
        rol_emoji = "👑" if self.es_admin() else "👤"
        resumen = f"{rol_emoji} {self.usuario} ({self.nombre_completo()}) - {self.rol.upper()}"
        logger.debug(f"Resumen corto generado para usuario {self.usuario}")
        return resumen
    
    def debug_info(self) -> str:
        """
        Genera información de debugging del usuario.
        
        Returns:
            str: Información técnica del objeto
        """
        valido, msg_validacion = self.validar_usuario()
        
        info_lines: list = [
            "🔧 DEBUG INFO - Usuario",
            f"├─ ID: {self.id_usuario}",
            f"├─ Usuario: '{self.usuario}' (tipo: {type(self.usuario).__name__})",
            f"├─ Nombre: '{self.nombre}' (tipo: {type(self.nombre).__name__})",
            f"├─ Apellido: '{self.apellido_paterno}' (tipo: {type(self.apellido_paterno).__name__})",
            f"├─ Password: '***' (tipo: {type(self.password).__name__})",
            f"├─ Pregunta de Seguridad: {'Sí' if self.pregunta_seguridad else 'No'}",
            f"├─ Rol: {self.rol} (válido: {self.validar_rol()})",
            f"├─ Fecha Registro: {self.fecha_registro} (tipo: {type(self.fecha_registro).__name__})",
            f"├─ Hash: {hash(self)}",
            f"├─ Es Admin: {self.es_admin()}",
            f"├─ Es Empleado: {self.es_empleado()}",
            f"├─ Días desde registro: {self.dias_desde_registro()}",
            f"├─ Validación: {'✓ Válido' if valido else '✗ Inválido'}",
            f"├─ Mensaje: {msg_validacion}",
            f"├─ Historial Estados: {len(self.historial_estados)} cambios registrados",
            f"└─ Último Cambio Rol: {self.ultimo_cambio_rol() or 'Ninguno'}"
        ]
        
        logger.debug(f"Debug info generado para usuario {self.usuario}")
        return "\n".join(info_lines)

    # ============================================================
    # CREACIÓN DESDE BD
    # ============================================================
    
    @staticmethod
    def from_db_row(row: tuple) -> 'Usuario':
        """
        Crea un objeto Usuario desde fila de BD.
        
        Orden de columnas en USUARIOS:
        0. Id_usuario
        1. Usuario
        2. Nombre
        3. Apellido_Paterno
        4. Password
        5. Pregunta_Seguridad
        6. Respuesta_Seguridad
        7. Rol
        8. Fecha_Registro
        
        Args:
            row: Tupla con los datos de la BD
        
        Returns:
            Usuario: Objeto Usuario creado
        
        Raises:
            IndexError: Si la tupla no tiene los campos requeridos
            TypeError: Si los tipos de datos no coinciden
            ValueError: Si los valores no son válidos
        """
        try:
            usuario = Usuario(
                id_usuario=int(row[0]),
                usuario=str(row[1]),
                nombre=str(row[2]),
                apellido_paterno=str(row[3]),
                password=str(row[4]),
                pregunta_seguridad=row[5] if row[5] else None,      # ← NUEVO
                respuesta_seguridad=row[6] if row[6] else None,      # ← NUEVO
                rol=str(row[7]) if row[7] else 'empleado',
                fecha_registro=row[8] if isinstance(row[8], datetime) else datetime.fromisoformat(str(row[8])) if row[8] else None
            )
            logger.debug(f"Usuario creado desde BD: {usuario.usuario} ({usuario.nombre_completo()})")
            return usuario
        except (IndexError, TypeError, ValueError) as e:
            logger.error(f"Error al crear Usuario desde BD: {e}")
            logger.error(f"   Row recibida: {row}")
            logger.error(f"   Tipos: {[type(x).__name__ for x in row]}")
            raise



# ============================================================
# EJEMPLO DE USO
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*80)
    print("EJEMPLO DE USO - Clase Usuario v2.2")
    print("CON SOPORTE PARA PREGUNTA DE SEGURIDAD")
    print("="*80 + "\n")
    
    # 1️⃣ Crear usuario admin con pregunta de seguridad
    print("1️⃣ Creando usuario admin con pregunta de seguridad...")
    admin = Usuario(
        usuario="admin",
        nombre="Juan",
        apellido_paterno="Pérez",
        password="admin123",
        rol="admin",
        pregunta_seguridad="¿Cuál es el nombre de tu primera mascota?",
        respuesta_seguridad="Firulais"
    )
    print()
    
    # 2️⃣ Información básica
    print("2️⃣ Información básica...")
    print(f"   Nombre completo: {admin.nombre_completo()}")
    print(f"   Tiene pregunta de seguridad: {'Sí' if admin.pregunta_seguridad else 'No'}")
    print(f"   Días registrado: {admin.dias_desde_registro()}")
    print(f"   Es admin: {admin.es_admin()}")
    print()
    
    # 3️⃣ Validación
    print("3️⃣ Validación de usuario...")
    valido, msg = admin.validar_usuario()
    print(f"   Válido: {valido} ({msg})")
    print()
    
    # 4️⃣ Autenticación
    print("4️⃣ Autenticación...")
    print(f"   Contraseña correcta: {admin.verificar_contrasena('admin123')}")
    print(f"   Contraseña incorrecta: {admin.verificar_contrasena('incorrecta')}")
    print()
    
    # 5️⃣ Resumen
    print("5️⃣ Resumen del admin...")
    print(admin.resumen_estado())
    print()
    
    # 6️⃣ Debug info
    print("6️⃣ Información de debugging...")
    print(admin.debug_info())
    print()
    
    print("="*80 + "\n")