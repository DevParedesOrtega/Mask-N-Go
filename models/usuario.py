"""
Módulo: usuario.py
Ubicación: models/usuario.py
Descripción: Modelo de datos para usuarios del sistema
Sistema: Renta y Venta de Disfraces
"""

from datetime import datetime
from typing import Optional


class Usuario:
    """
    Clase que representa un usuario del sistema.
    
    Attributes:
        id_usuario (int): ID único del usuario
        usuario (str): Nombre de usuario (login)
        nombre (str): Nombre del usuario
        apellido_paterno (str): Apellido paterno
        password (str): Contraseña (texto plano)
        rol (str): Rol del usuario ('admin' o 'empleado')
        fecha_registro (datetime): Fecha de creación
    """
    
    def __init__(
        self,
        usuario: str,
        nombre: str,
        apellido_paterno: str,
        password: str,
        rol: str = 'empleado',
        id_usuario: Optional[int] = None,
        fecha_registro: Optional[datetime] = None
    ):
        """
        Constructor de la clase Usuario.
        
        Args:
            usuario: Nombre de usuario para login
            nombre: Nombre del usuario
            apellido_paterno: Apellido paterno
            password: Contraseña en texto plano
            rol: Rol del usuario (default: 'empleado')
            id_usuario: ID del usuario (opcional, lo genera la BD)
            fecha_registro: Fecha de registro (opcional)
        """
        self.id_usuario = id_usuario
        self.usuario = usuario
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.password = password
        self.rol = rol
        self.fecha_registro = fecha_registro or datetime.now()
    
    def __str__(self) -> str:
        """
        Representación en texto del usuario.
        
        Returns:
            str: Descripción del usuario
        """
        return f"Usuario({self.usuario}, {self.nombre} {self.apellido_paterno}, Rol: {self.rol})"
    
    def __repr__(self) -> str:
        """Representación técnica del objeto."""
        return self.__str__()
    
    def to_dict(self) -> dict:
        """
        Convierte el objeto Usuario a diccionario.
        
        Returns:
            dict: Diccionario con los datos del usuario
        """
        return {
            'id_usuario': self.id_usuario,
            'usuario': self.usuario,
            'nombre': self.nombre,
            'apellido_paterno': self.apellido_paterno,
            'password': self.password,
            'rol': self.rol,
            'fecha_registro': self.fecha_registro
        }
    
    def nombre_completo(self) -> str:
        """
        Obtiene el nombre completo del usuario.
        
        Returns:
            str: Nombre completo
        """
        return f"{self.nombre} {self.apellido_paterno}"
    
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
    
    @staticmethod
    def from_db_row(row: tuple) -> 'Usuario':
        """
        Crea un objeto Usuario desde una fila de la base de datos.
        
        Args:
            row: Tupla con datos de la BD 
                 (Id_usuario, Usuario, Nombre, Apellido_Paterno, Password, Rol, Fecha_Registro)
        
        Returns:
            Usuario: Objeto Usuario creado
        """
        return Usuario(
            id_usuario=row[0],
            usuario=row[1],
            nombre=row[2],
            apellido_paterno=row[3],
            password=row[4],
            rol=row[5],
            fecha_registro=row[6]
        )


# Ejemplo de uso
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJEMPLO DE USO - Clase Usuario")
    print("="*60 + "\n")
    
    # Crear usuario
    usuario = Usuario(
        usuario="admin",
        nombre="Juan",
        apellido_paterno="Pérez",
        password="admin123",
        rol="admin"
    )
    
    print(f"Usuario creado: {usuario}")
    print(f"Nombre completo: {usuario.nombre_completo()}")
    print(f"Es admin: {usuario.es_admin()}")
    print(f"Es empleado: {usuario.es_empleado()}")
    print(f"\nDiccionario: {usuario.to_dict()}")
    
    print("\n" + "="*60 + "\n")