"""
Módulo: cliente.py
Ubicación: models/cliente.py
Descripción: Modelo de datos para clientes del sistema
Sistema: Renta y Venta de Disfraces
"""

from datetime import datetime
from typing import Optional, Dict


class Cliente:
    """
    Clase que representa un cliente del sistema.
    
    Attributes:
        id_cliente (int): ID único del cliente
        nombre (str): Nombre del cliente
        apellido_paterno (str): Apellido paterno
        telefono (str): Teléfono de contacto
        fecha_registro (datetime): Fecha de registro
    """
    
    def __init__(
        self,
        nombre: str,
        apellido_paterno: str,
        telefono: str,
        id_cliente: Optional[int] = None,
        fecha_registro: Optional[datetime] = None
    ):
        """
        Constructor de la clase Cliente.
        
        Args:
            nombre: Nombre del cliente
            apellido_paterno: Apellido paterno
            telefono: Teléfono de contacto (10-15 dígitos)
            id_cliente: ID del cliente (opcional, lo genera la BD)
            fecha_registro: Fecha de registro (opcional)
        """
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.telefono = telefono
        self.fecha_registro = fecha_registro or datetime.now()
        
        # Datos de historial (se llenan desde el controlador)
        self.estadisticas: Optional[Dict] = None
    
    def __str__(self) -> str:
        """
        Representación en texto del cliente.
        
        Returns:
            str: Descripción del cliente
        """
        return f"Cliente({self.id_cliente}, {self.nombre_completo()}, Tel: {self.telefono})"
    
    def __repr__(self) -> str:
        """Representación técnica del objeto."""
        return self.__str__()
    
    def to_dict(self) -> dict:
        """
        Convierte el objeto Cliente a diccionario.
        
        Returns:
            dict: Diccionario con los datos del cliente
        """
        data = {
            'id_cliente': self.id_cliente,
            'nombre': self.nombre,
            'apellido_paterno': self.apellido_paterno,
            'telefono': self.telefono,
            'fecha_registro': self.fecha_registro
        }
        
        if self.estadisticas:
            data['estadisticas'] = self.estadisticas
        
        return data
    
    def nombre_completo(self) -> str:
        """
        Obtiene el nombre completo del cliente.
        
        Returns:
            str: Nombre completo
        """
        return f"{self.nombre} {self.apellido_paterno}"
    
    def telefono_formateado(self) -> str:
        """
        Formatea el teléfono.
        - Si tiene 10 dígitos: (XXX) XXX-XXXX
        - Si no, devuelve tal cual
        
        Returns:
            str: Teléfono formateado
        """
        # Limpiar el teléfono
        tel_limpio = self.telefono.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').replace('+', '')
        
        if len(tel_limpio) == 10:
            return f"({tel_limpio[:3]}) {tel_limpio[3:6]}-{tel_limpio[6:]}"
        else:
            return self.telefono
    
    def cargar_estadisticas(self, estadisticas: Dict) -> None:
        """
        Carga las estadísticas del cliente desde la BD.
        
        Args:
            estadisticas: Diccionario con estadísticas
                {
                    'total_gastado': float,
                    'total_ventas': int,
                    'total_rentas': int,
                    'rentas_activas': int,
                    'rentas_vencidas': int,
                    'adeudo_pendiente': float,
                    'ultima_visita': datetime
                }
        """
        self.estadisticas = estadisticas
    
    def tiene_historial(self) -> bool:
        """
        Verifica si el cliente tiene historial de transacciones.
        
        Returns:
            bool: True si tiene ventas o rentas registradas
        """
        if not self.estadisticas:
            return False
        
        return (self.estadisticas.get('total_ventas', 0) > 0 or 
                self.estadisticas.get('total_rentas', 0) > 0)
    
    def tiene_rentas_activas(self) -> bool:
        """
        Verifica si tiene rentas activas actualmente.
        
        Returns:
            bool: True si tiene rentas activas
        """
        if not self.estadisticas:
            return False
        
        return self.estadisticas.get('rentas_activas', 0) > 0
    
    def tiene_adeudo(self) -> bool:
        """
        Verifica si tiene pagos pendientes.
        
        Returns:
            bool: True si tiene adeudo
        """
        if not self.estadisticas:
            return False
        
        return self.estadisticas.get('adeudo_pendiente', 0) > 0
    
    def es_cliente_nuevo(self) -> bool:
        """
        Verifica si es un cliente sin transacciones.
        
        Returns:
            bool: True si no tiene historial
        """
        return not self.tiene_historial()
    
    def resumen_estadisticas(self) -> str:
        """
        Genera un resumen legible de las estadísticas.
        
        Returns:
            str: Resumen en texto
        """
        if not self.estadisticas:
            return "Sin estadísticas cargadas"
        
        lineas = [
            f"📊 Estadísticas de {self.nombre_completo()}",
            f"💰 Total gastado: ${self.estadisticas.get('total_gastado', 0):.2f}",
            f"🛒 Ventas realizadas: {self.estadisticas.get('total_ventas', 0)}",
            f"🎭 Rentas realizadas: {self.estadisticas.get('total_rentas', 0)}",
            f"📦 Rentas activas: {self.estadisticas.get('rentas_activas', 0)}",
            f"⚠️ Rentas vencidas: {self.estadisticas.get('rentas_vencidas', 0)}",
            f"💳 Adeudo: ${self.estadisticas.get('adeudo_pendiente', 0):.2f}",
            f"🕒 Última visita: {self.estadisticas.get('ultima_visita', 'N/A')}"
        ]
        
        return "\n".join(lineas)
    
    @staticmethod
    def from_db_row(row: tuple) -> 'Cliente':
        """
        Crea un objeto Cliente desde una fila de la base de datos.
        
        Args:
            row: Tupla con datos de la BD
                 (Id_cliente, Nombre, Apellido_Paterno, Telefono, Fecha_Registro)
        
        Returns:
            Cliente: Objeto Cliente creado
        """
        return Cliente(
            id_cliente=row[0],
            nombre=row[1],
            apellido_paterno=row[2],
            telefono=row[3],
            fecha_registro=row[4]
        )


# Ejemplo de uso
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJEMPLO DE USO - Clase Cliente")
    print("="*60 + "\n")
    
    # Crear cliente
    cliente = Cliente(
        nombre="Juan",
        apellido_paterno="Pérez",
        telefono="+52 618 123 4567"
    )
    
    print(f"Cliente creado: {cliente}")
    print(f"Nombre completo: {cliente.nombre_completo()}")
    print(f"Teléfono formateado: {cliente.telefono_formateado()}")
    
    # Simular carga de estadísticas
    cliente.cargar_estadisticas({
        'total_gastado': 2500.00,
        'total_ventas': 5,
        'total_rentas': 3,
        'rentas_activas': 1,
        'rentas_vencidas': 0,
        'adeudo_pendiente': 0,
        'ultima_visita': datetime.now()
    })
    
    print(f"\n{cliente.resumen_estadisticas()}")
    print(f"\n¿Tiene historial?: {cliente.tiene_historial()}")
    print(f"¿Tiene rentas activas?: {cliente.tiene_rentas_activas()}")
    
    print("\n" + "="*60 + "\n")