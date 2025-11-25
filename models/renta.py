"""
Módulo: renta.py
Ubicación: models/renta.py
Descripción: Modelo de datos para rentas del sistema
Sistema: Renta y Venta de Disfraces
"""

from datetime import datetime, timedelta
from typing import Optional, List


class DetalleRenta:
    """
    Clase que representa un producto en una renta.
    
    Attributes:
        id_detalle (int): ID del detalle
        id_renta (int): ID de la renta padre
        codigo_barras (str): Código del disfraz
        cantidad (int): Cantidad rentada
        precio_unitario (float): Precio por día
        subtotal (float): cantidad × precio_unitario × días
    """
    
    def __init__(
        self,
        codigo_barras: str,
        cantidad: int,
        precio_unitario: float,
        id_detalle: Optional[int] = None,
        id_renta: Optional[int] = None
    ):
        self.id_detalle = id_detalle
        self.id_renta = id_renta
        self.codigo_barras = codigo_barras
        self.cantidad = int(cantidad)
        self.precio_unitario = float(precio_unitario)
        self.subtotal = 0.0  # Se calcula después con los días
    
    def calcular_subtotal(self, dias: int) -> float:
        """Calcula el subtotal basado en días."""
        self.subtotal = self.cantidad * self.precio_unitario * dias
        return self.subtotal
    
    def __str__(self) -> str:
        return f"DetalleRenta({self.codigo_barras}, Cant: {self.cantidad}, ${self.subtotal:.2f})"
    
    def to_dict(self) -> dict:
        return {
            'id_detalle': self.id_detalle,
            'id_renta': self.id_renta,
            'codigo_barras': self.codigo_barras,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'subtotal': self.subtotal
        }


class Renta:
    """
    Clase que representa una renta en el sistema.
    
    Attributes:
        id_renta (int): ID único de la renta
        id_cliente (int): ID del cliente
        id_usuario (int): ID del empleado que registró
        fecha_renta (datetime): Fecha de inicio de renta
        fecha_devolucion (datetime): Fecha esperada de devolución
        fecha_devuelto (datetime): Fecha real de devolución (NULL si activa)
        penalizacion (float): Monto de penalización por retraso
        dias_renta (int): Días totales de renta
        total (float): Total de la renta
        deposito (float): Depósito dado por el cliente
        estado (str): Estado (Activa/Devuelto/Vencida)
        detalles (List[DetalleRenta]): Productos rentados
    """
    
    def __init__(
        self,
        id_cliente: int,
        id_usuario: int,
        fecha_devolucion: datetime,
        dias_renta: int,
        total: float,
        deposito: float,
        id_renta: Optional[int] = None,
        fecha_renta: Optional[datetime] = None,
        fecha_devuelto: Optional[datetime] = None,
        penalizacion: float = 0.0,
        estado: str = 'Activa'
    ):
        self.id_renta = id_renta
        self.id_cliente = id_cliente
        self.id_usuario = id_usuario
        self.fecha_renta = fecha_renta or datetime.now()
        self.fecha_devolucion = fecha_devolucion
        self.fecha_devuelto = fecha_devuelto
        self.penalizacion = float(penalizacion)
        self.dias_renta = int(dias_renta)
        self.total = float(total)
        self.deposito = float(deposito)
        self.estado = estado
        self.detalles: List[DetalleRenta] = []
    
    def __str__(self) -> str:
        return f"Renta({self.id_renta}, Cliente: {self.id_cliente}, Días: {self.dias_renta}, Estado: {self.estado})"
    
    def agregar_detalle(self, detalle: DetalleRenta) -> None:
        """Agrega un producto a la renta."""
        detalle.calcular_subtotal(self.dias_renta)
        self.detalles.append(detalle)
    
    def esta_activa(self) -> bool:
        """Verifica si la renta está activa."""
        return self.estado == 'Activa'
    
    def esta_devuelta(self) -> bool:
        """Verifica si la renta fue devuelta."""
        return self.estado == 'Devuelto'
    
    def esta_vencida(self) -> bool:
        """Verifica si la renta está vencida."""
        return self.estado == 'Vencida'
    
    def dias_de_retraso(self) -> int:
        """
        Calcula los días de retraso si la renta está vencida.
        
        Returns:
            int: Días de retraso (0 si no hay retraso)
        """
        if not self.esta_activa() and not self.esta_vencida():
            return 0
        
        fecha_comparacion = self.fecha_devuelto if self.fecha_devuelto else datetime.now()
        
        if fecha_comparacion > self.fecha_devolucion:
            delta = fecha_comparacion - self.fecha_devolucion
            return delta.days
        
        return 0
    
    def calcular_penalizacion(self, penalizacion_por_dia: float) -> float:
        """
        Calcula la penalización basada en días de retraso.
        
        Args:
            penalizacion_por_dia: Monto fijo por día de retraso
        
        Returns:
            float: Monto total de penalización
        """
        dias_retraso = self.dias_de_retraso()
        if dias_retraso > 0:
            return dias_retraso * penalizacion_por_dia
        return 0.0
    
    def debe_marcarse_vencida(self) -> bool:
        """
        Verifica si la renta debe marcarse como vencida.
        
        Returns:
            bool: True si pasó la fecha de devolución y sigue activa
        """
        return self.esta_activa() and datetime.now() > self.fecha_devolucion
    
    def total_a_pagar_devolucion(self, penalizacion_por_dia: float) -> float:
        """
        Calcula el total a pagar en la devolución.
        
        Args:
            penalizacion_por_dia: Monto por día de retraso
        
        Returns:
            float: Total - depósito + penalizaciones
        """
        penalizacion_calculada = self.calcular_penalizacion(penalizacion_por_dia)
        # Total de renta - depósito + penalización
        return self.total - self.deposito + penalizacion_calculada
    
    def deposito_a_devolver(self) -> float:
        """
        Calcula el depósito a devolver al cliente.
        Según tu configuración: siempre se devuelve completo.
        
        Returns:
            float: Monto del depósito
        """
        return self.deposito
    
    def validar_renta(self) -> tuple[bool, str]:
        """
        Valida que la renta tenga datos correctos.
        
        Returns:
            tuple[bool, str]: (es_valida, mensaje_error)
        """
        if not self.detalles:
            return False, "La renta debe tener al menos un producto"
        
        if self.dias_renta <= 0:
            return False, "Los días de renta deben ser mayor a 0"
        
        if self.total <= 0:
            return False, "El total debe ser mayor a 0"
        
        if self.deposito < 0:
            return False, "El depósito no puede ser negativo"
        
        if self.fecha_devolucion <= self.fecha_renta:
            return False, "La fecha de devolución debe ser posterior a la fecha de renta"
        
        return True, "Renta válida"
    
    def resumen(self) -> str:
        """
        Genera un resumen legible de la renta.
        
        Returns:
            str: Resumen en texto
        """
        lineas = [
            f"🎭 Renta #{self.id_renta}",
            f"📅 Fecha renta: {self.fecha_renta}",
            f"📆 Fecha devolución: {self.fecha_devolucion}",
            f"👤 Cliente ID: {self.id_cliente}",
            f"👨‍💼 Usuario ID: {self.id_usuario}",
            f"🎭 Productos: {len(self.detalles)}",
            f"📆 Días: {self.dias_renta}",
            f"💰 Total: ${self.total:.2f}",
            f"💵 Depósito: ${self.deposito:.2f}",
            f"📊 Estado: {self.estado}",
        ]
        
        if self.fecha_devuelto:
            lineas.append(f"✅ Devuelto el: {self.fecha_devuelto}")
        
        if self.penalizacion > 0:
            lineas.append(f"⚠️ Penalización: ${self.penalizacion:.2f}")
        
        dias_retraso = self.dias_de_retraso()
        if dias_retraso > 0:
            lineas.append(f"⏰ Días de retraso: {dias_retraso}")
        
        return "\n".join(lineas)
    
    def to_dict(self) -> dict:
        """Convierte la renta a diccionario."""
        return {
            'id_renta': self.id_renta,
            'id_cliente': self.id_cliente,
            'id_usuario': self.id_usuario,
            'fecha_renta': self.fecha_renta,
            'fecha_devolucion': self.fecha_devolucion,
            'fecha_devuelto': self.fecha_devuelto,
            'penalizacion': self.penalizacion,
            'dias_renta': self.dias_renta,
            'total': self.total,
            'deposito': self.deposito,
            'estado': self.estado,
            'dias_retraso': self.dias_de_retraso(),
            'detalles': [d.to_dict() for d in self.detalles]
        }
    
    @staticmethod
    def from_db_row(row: tuple) -> 'Renta':
        """
        Crea un objeto Renta desde una fila de la BD.
        
        Args:
            row: Tupla con datos de RENTAS
                (Id_Renta, Id_Cliente, Id_Usuario, Fecha_Renta, Fecha_Devolucion,
                 Fecha_Devuelto, Penalizacion, Dias_Renta, Total, Deposito, Estado)
        
        Returns:
            Renta: Objeto Renta creado
        """
        return Renta(
            id_renta=row[0],
            id_cliente=row[1],
            id_usuario=row[2],
            fecha_renta=row[3],
            fecha_devolucion=row[4],
            fecha_devuelto=row[5],  # Agregado: Fecha_Devuelto
            penalizacion=row[6],
            dias_renta=row[7],
            total=row[8],
            deposito=row[9],
            estado=row[10]
        )


# Ejemplo de uso
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJEMPLO DE USO - Modelo Renta")
    print("="*60 + "\n")
    
    # Crear renta
    fecha_dev = datetime.now() + timedelta(days=3)
    renta = Renta(
        id_cliente=1,
        id_usuario=1,
        fecha_devolucion=fecha_dev,
        dias_renta=3,
        total=450.00,  # 3 días × $150/día
        deposito=800.00  # Depósito = precio venta
    )
    
    # Agregar detalles
    renta.agregar_detalle(DetalleRenta('DIS001', 1, 150.00))
    
    # Validar
    valida, msg = renta.validar_renta()
    print(f"¿Válida?: {valida} - {msg}\n")
    
    # Mostrar resumen
    print(renta.resumen())
    
    # Simular retraso
    renta.fecha_devolucion = datetime.now() - timedelta(days=2)
    dias_retraso = renta.dias_de_retraso()
    penalizacion = renta.calcular_penalizacion(50.00)
    
    print(f"\n⏰ Días de retraso: {dias_retraso}")
    print(f"⚠️ Penalización: ${penalizacion:.2f}")
    
    print("\n" + "="*60 + "\n")