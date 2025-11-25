"""
Módulo: venta.py
Ubicación: models/venta.py
Descripción: Modelo de datos para ventas del sistema
Sistema: Renta y Venta de Disfraces
"""

from datetime import datetime
from typing import Optional, List, Dict


class DetalleVenta:
    """
    Clase que representa un producto en una venta.
    
    Attributes:
        id_detalle (int): ID del detalle
        id_venta (int): ID de la venta padre
        codigo_barras (str): Código del disfraz
        cantidad (int): Cantidad vendida
        precio_unitario (float): Precio unitario al momento de venta
        subtotal (float): cantidad × precio_unitario
    """
    
    def __init__(
        self,
        codigo_barras: str,
        cantidad: int,
        precio_unitario: float,
        id_detalle: Optional[int] = None,
        id_venta: Optional[int] = None
    ):
        self.id_detalle = id_detalle
        self.id_venta = id_venta
        self.codigo_barras = codigo_barras
        self.cantidad = int(cantidad)
        self.precio_unitario = float(precio_unitario)
        self.subtotal = self.cantidad * self.precio_unitario
    
    def __str__(self) -> str:
        return f"DetalleVenta({self.codigo_barras}, Cant: {self.cantidad}, ${self.subtotal:.2f})"
    
    def to_dict(self) -> dict:
        return {
            'id_detalle': self.id_detalle,
            'id_venta': self.id_venta,
            'codigo_barras': self.codigo_barras,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'subtotal': self.subtotal
        }


class Venta:
    """
    Clase que representa una venta en el sistema.
    
    Attributes:
        id_venta (int): ID único de la venta
        folio (str): Folio único autogenerado (VEN-YYYYMMDD-####)
        id_cliente (int): ID del cliente
        id_usuario (int): ID del empleado que registró
        fecha_venta (datetime): Fecha de la venta
        total (float): Total de la venta (sin descuento)
        descuento_porcentaje (float): Porcentaje de descuento aplicado
        descuento_monto (float): Monto del descuento en pesos
        motivo_descuento (str): Justificación del descuento
        motivo_venta (str): Evento especial (Halloween, etc.)
        notas (str): Observaciones adicionales
        metodo_pago (str): Forma de pago
        estado (str): Estado de la venta (Activa/Cancelada)
        cancelada_por (int): ID del admin que canceló
        fecha_cancelacion (datetime): Fecha de cancelación
        motivo_cancelacion (str): Razón de cancelación
        detalles (List[DetalleVenta]): Productos vendidos
    """
    
    def __init__(
        self,
        id_cliente: int,
        id_usuario: int,
        total: float,
        metodo_pago: str,
        id_venta: Optional[int] = None,
        folio: Optional[str] = None,
        fecha_venta: Optional[datetime] = None,
        descuento_porcentaje: float = 0.0,
        descuento_monto: float = 0.0,
        motivo_descuento: Optional[str] = None,
        motivo_venta: Optional[str] = None,
        notas: Optional[str] = None,
        estado: str = 'Activa',
        cancelada_por: Optional[int] = None,
        fecha_cancelacion: Optional[datetime] = None,
        motivo_cancelacion: Optional[str] = None
    ):
        self.id_venta = id_venta
        self.folio = folio
        self.id_cliente = id_cliente
        self.id_usuario = id_usuario
        self.fecha_venta = fecha_venta or datetime.now()
        self.total = float(total)
        self.descuento_porcentaje = float(descuento_porcentaje)
        self.descuento_monto = float(descuento_monto)
        self.motivo_descuento = motivo_descuento
        self.motivo_venta = motivo_venta
        self.notas = notas
        self.metodo_pago = metodo_pago
        self.estado = estado
        self.cancelada_por = cancelada_por
        self.fecha_cancelacion = fecha_cancelacion
        self.motivo_cancelacion = motivo_cancelacion
        self.detalles: List[DetalleVenta] = []
    
    def __str__(self) -> str:
        return f"Venta({self.folio}, Cliente: {self.id_cliente}, Total: ${self.total_con_descuento():.2f}, Estado: {self.estado})"
    
    def agregar_detalle(self, detalle: DetalleVenta) -> None:
        """Agrega un producto a la venta."""
        self.detalles.append(detalle)
    
    def calcular_subtotal(self) -> float:
        """
        Calcula el subtotal de todos los productos.
        
        Returns:
            float: Suma de todos los subtotales
        """
        return sum(detalle.subtotal for detalle in self.detalles)
    
    def calcular_descuento_monto(self) -> float:
        """
        Calcula el monto del descuento basado en el porcentaje.
        
        Returns:
            float: Monto del descuento
        """
        if self.descuento_porcentaje > 0:
            return self.total * (self.descuento_porcentaje / 100)
        return 0.0
    
    def total_con_descuento(self) -> float:
        """
        Calcula el total final con descuento aplicado.
        
        Returns:
            float: Total - descuento
        """
        return self.total - self.descuento_monto
    
    def tiene_descuento(self) -> bool:
        """Verifica si la venta tiene descuento."""
        return self.descuento_porcentaje > 0 or self.descuento_monto > 0
    
    def esta_activa(self) -> bool:
        """Verifica si la venta está activa."""
        return self.estado == 'Activa'
    
    def esta_cancelada(self) -> bool:
        """Verifica si la venta fue cancelada."""
        return self.estado == 'Cancelada'
    
    def validar_venta(self) -> tuple[bool, str]:
        """
        Valida que la venta tenga datos correctos antes de registrar.
        
        Returns:
            tuple[bool, str]: (es_valida, mensaje_error)
        """
        if not self.detalles:
            return False, "La venta debe tener al menos un producto"
        
        if self.total <= 0:
            return False, "El total debe ser mayor a 0"
        
        if self.descuento_porcentaje < 0 or self.descuento_porcentaje > 100:
            return False, "El descuento debe estar entre 0% y 100%"
        
        if self.tiene_descuento() and not self.motivo_descuento:
            return False, "El descuento requiere justificación"
        
        return True, "Venta válida"
    
    def resumen(self) -> str:
        """
        Genera un resumen legible de la venta.
        
        Returns:
            str: Resumen en texto
        """
        lineas = [
            f"🧾 Venta {self.folio}",
            f"📅 Fecha: {self.fecha_venta}",
            f"👤 Cliente ID: {self.id_cliente}",
            f"👨‍💼 Usuario ID: {self.id_usuario}",
            f"🎭 Productos: {len(self.detalles)}",
            f"💰 Subtotal: ${self.total:.2f}",
        ]
        
        if self.tiene_descuento():
            lineas.append(f"🏷️ Descuento: {self.descuento_porcentaje}% (${self.descuento_monto:.2f})")
            lineas.append(f"📝 Motivo: {self.motivo_descuento}")
        
        lineas.append(f"💳 Total Final: ${self.total_con_descuento():.2f}")
        lineas.append(f"💵 Método: {self.metodo_pago}")
        lineas.append(f"📊 Estado: {self.estado}")
        
        if self.motivo_venta:
            lineas.append(f"🎉 Motivo: {self.motivo_venta}")
        
        if self.notas:
            lineas.append(f"📌 Notas: {self.notas}")
        
        if self.esta_cancelada():
            lineas.append(f"❌ Cancelada el: {self.fecha_cancelacion}")
            lineas.append(f"📝 Motivo: {self.motivo_cancelacion}")
        
        return "\n".join(lineas)
    
    def to_dict(self) -> dict:
        """Convierte la venta a diccionario."""
        return {
            'id_venta': self.id_venta,
            'folio': self.folio,
            'id_cliente': self.id_cliente,
            'id_usuario': self.id_usuario,
            'fecha_venta': self.fecha_venta,
            'total': self.total,
            'descuento_porcentaje': self.descuento_porcentaje,
            'descuento_monto': self.descuento_monto,
            'motivo_descuento': self.motivo_descuento,
            'motivo_venta': self.motivo_venta,
            'notas': self.notas,
            'metodo_pago': self.metodo_pago,
            'estado': self.estado,
            'total_final': self.total_con_descuento(),
            'detalles': [d.to_dict() for d in self.detalles]
        }
    
    @staticmethod
    def from_db_row(row: tuple) -> 'Venta':
        """
        Crea un objeto Venta desde una fila de la BD.
        
        Args:
            row: Tupla con datos de VENTAS
                (Id_Venta, Folio, Id_cliente, Usuario_id, fecha_venta, Total,
                 Descuento_Porcentaje, Descuento_Monto, Motivo_Descuento,
                 Motivo_Venta, Notas, metodo_pago, Estado, Cancelada_Por,
                 Fecha_Cancelacion, Motivo_Cancelacion)
        
        Returns:
            Venta: Objeto Venta creado
        """
        return Venta(
            id_venta=row[0],
            folio=row[1],
            id_cliente=row[2],
            id_usuario=row[3],
            fecha_venta=row[4],
            total=row[5],
            descuento_porcentaje=row[6],
            descuento_monto=row[7],
            motivo_descuento=row[8],
            motivo_venta=row[9],
            notas=row[10],
            metodo_pago=row[11],
            estado=row[12],
            cancelada_por=row[13],
            fecha_cancelacion=row[14],
            motivo_cancelacion=row[15]
        )


# Ejemplo de uso
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJEMPLO DE USO - Modelo Venta")
    print("="*60 + "\n")
    
    # Crear venta
    venta = Venta(
        id_cliente=1,
        id_usuario=1,
        total=1500.00,
        metodo_pago='Efectivo',
        folio='VEN-20250121-0001',
        descuento_porcentaje=10,
        motivo_descuento='Cliente frecuente',
        motivo_venta='Halloween'
    )
    
    # Calcular descuento
    venta.descuento_monto = venta.calcular_descuento_monto()
    
    # Agregar productos
    venta.agregar_detalle(DetalleVenta('DIS001', 2, 500.00))
    venta.agregar_detalle(DetalleVenta('DIS002', 1, 500.00))
    
    # Validar
    valida, msg = venta.validar_venta()
    print(f"¿Válida?: {valida} - {msg}\n")
    
    # Mostrar resumen
    print(venta.resumen())
    
    print("\n" + "="*60 + "\n")