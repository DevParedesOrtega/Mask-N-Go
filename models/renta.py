"""
Módulo: renta.py
Ubicación: models/renta.py
Descripción: Modelo de datos para rentas del sistema
Sistema: MaskNGO - Renta y Venta de Disfraces
Versión: 2.1 - Con logging, métodos de auditoría, validaciones en constructor
            y gestión segura del subtotal en DetalleRenta.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
import logging
from utils.logger_config import setup_logger


# Configurar logging
logger = setup_logger('renta_model', 'logs/rentas_model.log')


class DetalleRenta:
    """
    Clase que representa un producto en una renta.
    
    Attributes:
        id_detalle_renta (int): ID único del detalle (PK)
        id_renta (int): ID de la renta padre (FK)
        codigo_barras (str): Código del disfraz (FK)
        cantidad (int): Cantidad de disfraces rentados
        precio_unitario (Decimal): Precio por unidad por día
        subtotal (Decimal): cantidad × precio_unitario × días (calculado o cargado desde BD)
        historial_estados (list): Historial de cambios de estado (reservado para futuras extensiones)
    
    BD Campos (tabla DETALLE_RENTAS):
        - Id_DetalleRenta (PK, int, auto_increment)
        - Id_Renta (FK, int)
        - Codigo_Barras (FK, varchar)
        - Cantidad (int)
        - Precio_Unitario (decimal 10,2)
        - Subtotal (decimal 10,2)
    """
    
    def __init__(
        self,
        codigo_barras: str,
        cantidad: int,
        precio_unitario: Decimal,
        id_detalle_renta: Optional[int] = None,
        id_renta: Optional[int] = None
    ) -> None:
        """
        Constructor de DetalleRenta.
        
        Args:
            codigo_barras: Código del disfraz
            cantidad: Cantidad rentada
            precio_unitario: Precio por unidad por día (Decimal)
            id_detalle_renta: ID del detalle (generado por BD)
            id_renta: ID de la renta padre
        """
        # Validaciones
        if cantidad <= 0:
            raise ValueError(f"Cantidad debe ser mayor a 0: {cantidad}")
        
        if precio_unitario < 0:
            raise ValueError(f"Precio unitario no puede ser negativo: {precio_unitario}")

        self.id_detalle_renta: Optional[int] = id_detalle_renta
        self.id_renta: Optional[int] = id_renta
        self.codigo_barras: str = codigo_barras
        self.cantidad: int = int(cantidad)
        self.precio_unitario: Decimal = Decimal(str(precio_unitario))
        self.subtotal: Decimal = Decimal('0.00')  # Inicial temporal; se calcula al asociarse a una renta
        
        # Historial de auditoría de estados
        self.historial_estados: list = []

        logger.info(f"DetalleRenta creado: {self.codigo_barras} (Cant: {self.cantidad})")
    
    def calcular_subtotal(self, dias_renta: int) -> Decimal:
        """
        Calcula el subtotal basado en días de renta.
        
        Fórmula: cantidad × precio_unitario × días
        
        Args:
            dias_renta: Número de días de renta
        
        Returns:
            Decimal: Subtotal calculado
        """
        if dias_renta <= 0:
            self.subtotal = Decimal('0.00')
            return self.subtotal
        
        self.subtotal = Decimal(self.cantidad) * self.precio_unitario * Decimal(dias_renta)
        return self.subtotal
    
    def __str__(self) -> str:
        """Representación legible del detalle."""
        return f"DetalleRenta({self.codigo_barras}, Cant: {self.cantidad}, ${self.subtotal:.2f})"
    
    def __repr__(self) -> str:
        """Representación técnica."""
        return self.__str__()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            'id_detalle_renta': self.id_detalle_renta,
            'id_renta': self.id_renta,
            'codigo_barras': self.codigo_barras,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario),
            'subtotal': float(self.subtotal),
            'historial_estados': self.historial_estados
        }
    
    @staticmethod
    def from_db_row(row: tuple) -> 'DetalleRenta':
        """
        Crea DetalleRenta desde fila de BD.
        
        Args:
            row: (Id_DetalleRenta, Id_Renta, Codigo_Barras, Cantidad, Precio_Unitario, Subtotal)
        
        Returns:
            DetalleRenta: Objeto creado
        """
        try:
            # Crear sin pasar subtotal al constructor
            detalle = DetalleRenta(
                id_detalle_renta=int(row[0]),
                id_renta=int(row[1]),
                codigo_barras=str(row[2]),
                cantidad=int(row[3]),
                precio_unitario=Decimal(str(row[4]))
            )
            # Asignar subtotal directamente desde la BD
            detalle.subtotal = Decimal(str(row[5]))
            logger.debug(f"DetalleRenta creado desde BD: {detalle.codigo_barras} (Cant: {detalle.cantidad})")
            return detalle
        except (IndexError, TypeError, ValueError) as e:
            logger.error(f"Error al crear DetalleRenta desde BD: {e}")
            logger.error(f"   Row recibida: {row}")
            logger.error(f"   Tipos: {[type(x).__name__ for x in row]}")
            raise


class Renta:
    """
    Clase que representa una renta en el sistema.
    
    Attributes:
        id_renta (int): ID único de la renta (PK)
        id_cliente (int): ID del cliente (FK)
        id_usuario (int): ID del empleado que registró (FK)
        fecha_renta (datetime): Fecha de inicio de renta
        fecha_devolucion (datetime): Fecha esperada de devolución
        fecha_devuelto (datetime): Fecha real de devolución (NULL si activa)
        penalizacion (Decimal): Monto de penalización por retraso
        dias_renta (int): Días totales de renta
        total (Decimal): Total de la renta
        deposito (Decimal): Depósito dado por el cliente
        estado (str): Estado (Activa, Devuelto, Vencida)
        detalles (List[DetalleRenta]): Productos rentados
        historial_estados (list): Historial de cambios de estado
    
    BD Campos (tabla RENTAS):
        - Id_Renta (PK, int, auto_increment)
        - Id_Cliente (FK, int)
        - Id_Usuario (FK, int)
        - Fecha_Renta (datetime, default CURRENT_TIMESTAMP)
        - Fecha_Devolucion (datetime)
        - Fecha_Devuelto (datetime, nullable)
        - Penalizacion (decimal 10,2, default 0.00)
        - Dias_Renta (int)
        - Total (decimal 10,2)
        - Deposito (decimal 10,2, default 0.00)
        - Estado (enum Activa/Devuelto/Vencida, default Activa)
    """
    
    # Estados válidos
    ESTADOS_VALIDOS: Tuple[str, ...] = ('Activa', 'Devuelto', 'Vencida')
    
    def __init__(
        self,
        id_cliente: int,
        id_usuario: int,
        fecha_devolucion: datetime,
        dias_renta: int,
        total: Decimal,
        id_renta: Optional[int] = None,
        fecha_renta: Optional[datetime] = None,
        fecha_devuelto: Optional[datetime] = None,
        penalizacion: Decimal = Decimal('0.00'),
        deposito: Decimal = Decimal('0.00'),
        estado: str = 'Activa'
    ) -> None:
        """
        Constructor de Renta.
        
        Args:
            id_cliente: ID del cliente
            id_usuario: ID del usuario que registró
            fecha_devolucion: Fecha esperada de devolución
            dias_renta: Días totales de renta
            total: Total de la renta (Decimal)
            id_renta: ID de la renta (generado por BD)
            fecha_renta: Fecha de inicio (default: ahora)
            fecha_devuelto: Fecha real de devolución (NULL si activa)
            penalizacion: Penalización por retraso (Decimal)
            deposito: Depósito del cliente (Decimal)
            estado: Estado de la renta (default: 'Activa')
        """
        # Validaciones
        if id_cliente <= 0:
            raise ValueError(f"ID de cliente debe ser mayor a 0: {id_cliente}")
        
        if id_usuario <= 0:
            raise ValueError(f"ID de usuario debe ser mayor a 0: {id_usuario}")
        
        if dias_renta <= 0:
            raise ValueError(f"Días de renta deben ser mayor a 0: {dias_renta}")
        
        if total < 0:
            raise ValueError(f"Total no puede ser negativo: {total}")
        
        if deposito < 0:
            raise ValueError(f"Depósito no puede ser negativo: {deposito}")
        
        if penalizacion < 0:
            raise ValueError(f"Penalización no puede ser negativa: {penalizacion}")
        
        if fecha_devolucion <= (fecha_renta or datetime.now()):
            raise ValueError("Fecha de devolución debe ser posterior a fecha de renta")

        self.id_renta: Optional[int] = id_renta
        self.id_cliente: int = int(id_cliente)
        self.id_usuario: int = int(id_usuario)
        self.fecha_renta: datetime = fecha_renta or datetime.now()
        self.fecha_devolucion: datetime = fecha_devolucion
        self.fecha_devuelto: Optional[datetime] = fecha_devuelto
        self.penalizacion: Decimal = Decimal(str(penalizacion))
        self.dias_renta: int = int(dias_renta)
        self.total: Decimal = Decimal(str(total))
        self.deposito: Decimal = Decimal(str(deposito))
        self.estado: str = estado
        self.detalles: List[DetalleRenta] = []
        
        # Historial de auditoría de estados
        self.historial_estados: list = []

        logger.info(f"Renta creada: ID {self.id_renta}, Cliente {self.id_cliente}, {self.dias_renta} días")


    # ============================================================
    # REPRESENTACIÓN Y COMPARACIÓN
    # ============================================================
    
    def __str__(self) -> str:
        """Representación legible de la renta."""
        return (f"Renta(id={self.id_renta}, Cliente: {self.id_cliente}, "
                f"Días: {self.dias_renta}, Estado: {self.estado})")
    
    def __repr__(self) -> str:
        """Representación técnica."""
        return self.__str__()
    
    def __eq__(self, other: Any) -> bool:
        """Compara si dos rentas son la misma por ID."""
        if not isinstance(other, Renta):
            return False
        return self.id_renta == other.id_renta
    
    def __hash__(self) -> int:
        """Hash para usar en sets/dicts."""
        return hash(self.id_renta) if self.id_renta else hash(id(self))
    
    def __lt__(self, other: 'Renta') -> bool:
        """Compara rentas por fecha (para ordenamiento)."""
        if not isinstance(other, Renta):
            return NotImplemented
        return self.fecha_renta < other.fecha_renta
    
    def __le__(self, other: 'Renta') -> bool:
        """Menor o igual que."""
        return self == other or self < other
    
    def __gt__(self, other: 'Renta') -> bool:
        """Mayor que."""
        return not self <= other
    
    def __ge__(self, other: 'Renta') -> bool:
        """Mayor o igual que."""
        return not self < other


    # ============================================================
    # MÉTODOS DE DETALLES
    # ============================================================
    
    def agregar_detalle(self, detalle: DetalleRenta) -> None:
        """
        Agrega un producto a la renta.
        
        Args:
            detalle: Objeto DetalleRenta a agregar
        """
        detalle.calcular_subtotal(self.dias_renta)
        detalle.id_renta = self.id_renta
        self.detalles.append(detalle)
        logger.info(f"Detalle agregado a renta {self.id_renta}: {detalle.codigo_barras}")
    
    def obtener_detalles(self) -> List[DetalleRenta]:
        """Retorna lista de detalles."""
        return self.detalles
    
    def contar_detalles(self) -> int:
        """Retorna cantidad de detalles."""
        return len(self.detalles)
    
    def obtener_subtotal_detalles(self) -> Decimal:
        """Calcula suma de todos los subtotales."""
        return sum(d.subtotal for d in self.detalles) if self.detalles else Decimal('0.00')


    # ============================================================
    # MÉTODOS DE ESTADO
    # ============================================================
    
    def esta_activa(self) -> bool:
        """Verifica si la renta está activa."""
        return self.estado == 'Activa'
    
    def esta_devuelta(self) -> bool:
        """Verifica si la renta fue devuelta."""
        return self.estado == 'Devuelto'
    
    def esta_vencida(self) -> bool:
        """Verifica si la renta está vencida."""
        return self.estado == 'Vencida'
    
    def validar_estado(self) -> bool:
        """Valida que el estado sea uno de los válidos."""
        return self.estado in self.ESTADOS_VALIDOS


    # ============================================================
    # MÉTODOS DE AUDITORÍA
    # ============================================================

    def cambiar_estado(self, nuevo_estado: str, usuario: Optional[str] = None, motivo: Optional[str] = None) -> bool:
        """
        Cambia el estado de la renta y registra el cambio en el historial.

        Args:
            nuevo_estado: Nuevo estado de la renta
            usuario: Usuario que realiza el cambio (opcional)
            motivo: Motivo del cambio (opcional)

        Returns:
            bool: True si se cambió, False si no
        """
        if self.estado == nuevo_estado:
            logger.info(f"Estado no cambiado: Renta {self.id_renta} ya está en estado '{nuevo_estado}'")
            return False

        if nuevo_estado not in self.ESTADOS_VALIDOS:
            logger.warning(f"Intento de cambiar estado a valor inválido: {nuevo_estado}")
            return False

        antiguo_estado = self.estado
        self.estado = nuevo_estado

        # Registrar en historial
        registro = {
            'fecha': self._get_current_datetime(),
            'antiguo_estado': antiguo_estado,
            'nuevo_estado': nuevo_estado,
            'usuario': usuario,
            'motivo': motivo
        }
        self.historial_estados.append(registro)

        logger.info(f"Estado cambiado para renta {self.id_renta}: '{antiguo_estado}' → '{nuevo_estado}' (por {usuario or 'sistema'}, motivo: {motivo or 'sin especificar'})")
        return True

    def obtener_historial_estados(self) -> list:
        """
        Obtiene el historial de cambios de estado de la renta.

        Returns:
            list: Lista de diccionarios con cambios de estado
        """
        return self.historial_estados

    def ultimo_cambio_estado(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el último cambio de estado de la renta.

        Returns:
            dict o None: Último registro de cambio de estado
        """
        if self.historial_estados:
            return self.historial_estados[-1]
        return None

    def _get_current_datetime(self):
        """Obtiene la fecha/hora actual. Aislado para facilitar pruebas."""
        return datetime.now()


    # ============================================================
    # MÉTODOS DE CÁLCULO DE RETRASO Y PENALIZACIÓN
    # ============================================================
    
    def dias_de_retraso(self) -> int:
        """
        Calcula los días de retraso en devolución.
        
        Lógica:
        - Si está devuelta: calcula desde fecha_devuelto
        - Si está activa/vencida: calcula desde ahora
        
        Returns:
            int: Días de retraso (0 si está a tiempo)
        """
        # Determinar fecha de comparación
        if self.fecha_devuelto:
            fecha_comparacion = self.fecha_devuelto
        else:
            fecha_comparacion = datetime.now()
        
        # Calcular diferencia
        if fecha_comparacion > self.fecha_devolucion:
            delta = fecha_comparacion - self.fecha_devolucion
            return delta.days
        
        return 0
    
    def horas_de_retraso(self) -> float:
        """
        Calcula las horas de retraso (incluyendo fracción).
        
        Returns:
            float: Horas de retraso
        """
        if self.fecha_devuelto:
            fecha_comparacion = self.fecha_devuelto
        else:
            fecha_comparacion = datetime.now()
        
        if fecha_comparacion > self.fecha_devolucion:
            delta = fecha_comparacion - self.fecha_devolucion
            return delta.total_seconds() / 3600  # Convertir a horas
        
        return 0.0
    
    def calcular_penalizacion(self, penalizacion_por_dia: Decimal) -> Decimal:
        """
        Calcula la penalización basada en días de retraso.
        
        Args:
            penalizacion_por_dia: Monto fijo por día de retraso (Decimal)
        
        Returns:
            Decimal: Monto total de penalización
        """
        dias_retraso = self.dias_de_retraso()
        
        if dias_retraso > 0:
            return Decimal(dias_retraso) * Decimal(str(penalizacion_por_dia))
        
        return Decimal('0.00')
    
    def debe_marcarse_vencida(self) -> bool:
        """
        Verifica si la renta debe marcarse como vencida.
        
        Condiciones:
        - Debe estar Activa
        - Debe haber pasado la fecha de devolución esperada
        
        NOTA: Este método SOLO VERIFICA. El controlador debe actualizar la BD.
        
        Returns:
            bool: True si debe marcarse vencida, False si no
        """
        if not self.esta_activa():
            return False
        
        return datetime.now() > self.fecha_devolucion


    # ============================================================
    # MÉTODOS DE DEPÓSITO Y PAGO
    # ============================================================
    
    def deposito_a_devolver(self) -> Decimal:
        """
        Calcula el depósito a devolver al cliente.
        
        Lógica:
        - SIEMPRE se devuelve el 100% del depósito
        - La penalización se cobra APARTE
        
        Returns:
            Decimal: Monto del depósito a devolver
        """
        return self.deposito
    
    def total_a_pagar_sin_deposito(self) -> Decimal:
        """
        Calcula lo que debe pagar por la renta (sin aplicar depósito).
        
        Fórmula: total + penalización
        
        Returns:
            Decimal: Total a pagar sin considerar depósito
        """
        return self.total + self.penalizacion
    
    def total_a_pagar_con_deposito(self) -> Decimal:
        """
        Calcula el saldo final a pagar/devolver al cliente.
        
        Lógica:
        - Si cliente pagó: deposito - penalización = saldo
        - Si positivo: se devuelve saldo al cliente
        - Si negativo: cliente debe pagar diferencia
        
        Returns:
            Decimal: Saldo final (+ devuelve cliente, - debe pagar cliente)
        """
        return self.deposito - self.penalizacion


    # ============================================================
    # MÉTODOS DE VALIDACIÓN
    # ============================================================
    
    def validar_renta(self) -> Tuple[bool, str]:
        """
        Valida que la renta tenga datos correctos.
        
        Returns:
            Tuple[bool, str]: (es_válida, mensaje)
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
            return False, "Fecha de devolución debe ser posterior a fecha de renta"
        
        if not self.validar_estado():
            return False, f"Estado '{self.estado}' no es válido"
        
        return True, "Renta válida"


    # ============================================================
    # MÉTODOS DE REPORTE
    # ============================================================
    
    def resumen_estado(self) -> str:
        """Genera un resumen corto del estado."""
        estado_emoji = "🟢" if self.esta_activa() else "🔴" if self.esta_vencida() else "✅"
        logger.debug(f"Resumen de estado generado para renta {self.id_renta}")
        return f"{estado_emoji} Renta #{self.id_renta} - {self.estado} ({self.dias_renta} días)"
    
    def resumen_completo(self) -> str:
        """Genera un resumen legible completo de la renta."""
        lineas: List[str] = [
            f"🎭 RENTA #{self.id_renta}",
            f"├─ 📅 Fecha renta: {self.fecha_renta.strftime('%Y-%m-%d %H:%M:%S')}",
            f"├─ 📆 Fecha devolución: {self.fecha_devolucion.strftime('%Y-%m-%d %H:%M:%S')}",
            f"├─ 👤 Cliente ID: {self.id_cliente}",
            f"├─ 👨‍💼 Usuario ID: {self.id_usuario}",
            f"├─ 📦 Productos: {self.contar_detalles()}",
            f"├─ ⏱️  Días: {self.dias_renta}",
            f"├─ 💰 Total: ${self.total:.2f}",
            f"├─ 💵 Depósito: ${self.deposito:.2f}",
            f"├─ 📊 Estado: {self.estado}",
        ]
        
        if self.fecha_devuelto:
            lineas.append(f"├─ ✅ Devuelto: {self.fecha_devuelto.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.penalizacion > 0:
            lineas.append(f"├─ ⚠️  Penalización: ${self.penalizacion:.2f}")
        
        dias_retraso = self.dias_de_retraso()
        if dias_retraso > 0:
            lineas.append(f"├─ ⏰ Días de retraso: {dias_retraso}")
        
        saldo = self.total_a_pagar_con_deposito()
        if saldo > 0:
            lineas.append(f"└─ 💳 Saldo a devolver: ${saldo:.2f}")
        elif saldo < 0:
            lineas.append(f"└─ 💳 Saldo a pagar: ${abs(saldo):.2f}")
        else:
            lineas.append(f"└─ 💳 Saldo: Pagado")
        
        logger.debug(f"Resumen completo generado para renta {self.id_renta}")
        return "\n".join(lineas)
    
    def debug_info(self) -> str:
        """Genera información de debugging."""
        info_lines: List[str] = [
            "🔧 DEBUG INFO - Renta",
            f"├─ ID: {self.id_renta}",
            f"├─ Cliente ID: {self.id_cliente}",
            f"├─ Usuario ID: {self.id_usuario}",
            f"├─ Fecha Renta: {self.fecha_renta} (tipo: {type(self.fecha_renta).__name__})",
            f"├─ Fecha Devolución: {self.fecha_devolucion}",
            f"├─ Fecha Devuelto: {self.fecha_devuelto}",
            f"├─ Días Renta: {self.dias_renta}",
            f"├─ Total: {self.total} (tipo: {type(self.total).__name__})",
            f"├─ Deposito: {self.deposito} (tipo: {type(self.deposito).__name__})",
            f"├─ Penalización: {self.penalizacion}",
            f"├─ Estado: {self.estado}",
            f"├─ Detalles: {self.contar_detalles()}",
            f"├─ Hash: {hash(self)}",
            f"├─ Está Activa: {self.esta_activa()}",
            f"├─ Debe Marcarse Vencida: {self.debe_marcarse_vencida()}",
            f"├─ Días de Retraso: {self.dias_de_retraso()}",
            f"├─ Es Válida: {self.validar_renta()[0]}",
            f"├─ Historial Estados: {len(self.historial_estados)} cambios registrados",
            f"└─ Último Cambio Estado: {self.ultimo_cambio_estado() or 'Ninguno'}"
        ]
        
        logger.debug(f"Debug info generado para renta {self.id_renta}")
        return "\n".join(info_lines)


    # ============================================================
    # CONVERSIÓN A DICCIONARIO
    # ============================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la renta a diccionario."""
        return {
            'id_renta': self.id_renta,
            'id_cliente': self.id_cliente,
            'id_usuario': self.id_usuario,
            'fecha_renta': self.fecha_renta.isoformat() if self.fecha_renta else None,
            'fecha_devolucion': self.fecha_devolucion.isoformat() if self.fecha_devolucion else None,
            'fecha_devuelto': self.fecha_devuelto.isoformat() if self.fecha_devuelto else None,
            'penalizacion': float(self.penalizacion),
            'dias_renta': self.dias_renta,
            'total': float(self.total),
            'deposito': float(self.deposito),
            'estado': self.estado,
            'dias_retraso': self.dias_de_retraso(),
            'detalles': [d.to_dict() for d in self.detalles],
            'historial_estados': self.historial_estados
        }


    # ============================================================
    # CREACIÓN DESDE BD
    # ============================================================
    
    @staticmethod
    def from_db_row(row: tuple) -> 'Renta':
        """
        Crea un objeto Renta desde fila de BD.
        
        Args:
            row: (Id_Renta, Id_Cliente, Id_Usuario, Fecha_Renta, Fecha_Devolucion,
                  Fecha_Devuelto, Penalizacion, Dias_Renta, Total, Deposito, Estado)
        
        Returns:
            Renta: Objeto Renta creado
        """
        try:
            renta = Renta(
                id_renta=int(row[0]),
                id_cliente=int(row[1]),
                id_usuario=int(row[2]),
                fecha_renta=row[3] if isinstance(row[3], datetime) else datetime.fromisoformat(str(row[3])),
                fecha_devolucion=row[4] if isinstance(row[4], datetime) else datetime.fromisoformat(str(row[4])),
                fecha_devuelto=row[5] if isinstance(row[5], datetime) or row[5] is None else datetime.fromisoformat(str(row[5])),
                penalizacion=Decimal(str(row[6])) if row[6] else Decimal('0.00'),
                dias_renta=int(row[7]),
                total=Decimal(str(row[8])),
                deposito=Decimal(str(row[9])) if row[9] else Decimal('0.00'),
                estado=str(row[10]) if row[10] else 'Activa'
            )
            logger.debug(f"Renta creada desde BD: ID {renta.id_renta}, Cliente {renta.id_cliente}")
            return renta
        except (IndexError, TypeError, ValueError) as e:
            logger.error(f"Error al crear Renta desde BD: {e}")
            logger.error(f"   Row recibida: {row}")
            logger.error(f"   Tipos: {[type(x).__name__ for x in row]}")
            raise



# ============================================================
# EJEMPLO DE USO
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*80)
    print("EJEMPLO DE USO - Clase Renta v2.1 (versión segura)")
    print("CON LOGGING, VALIDACIONES, AUDITORÍA Y SUBTOTAL CONTROLADO")
    print("="*80 + "\n")
    
    from datetime import timedelta
    
    # 1️⃣ Crear renta
    print("1️⃣ Creando renta...")
    fecha_dev = datetime.now() + timedelta(days=3)
    renta = Renta(
        id_cliente=1,
        id_usuario=1,
        fecha_devolucion=fecha_dev,
        dias_renta=3,
        total=Decimal('450.00'),
        deposito=Decimal('800.00')
    )
    print()
    
    # 2️⃣ Agregar detalles
    print("2️⃣ Agregando detalles...")
    detalle1 = DetalleRenta('DIS001', 1, Decimal('150.00'))
    renta.agregar_detalle(detalle1)
    print()
    
    # 3️⃣ Validar
    print("3️⃣ Validando renta...")
    valida, msg = renta.validar_renta()
    print(f"   ¿Válida?: {valida} - {msg}\n")
    
    # 4️⃣ Mostrar resumen
    print("4️⃣ Resumen completo...")
    print(renta.resumen_completo())
    print()
    
    # 5️⃣ Verificar si debe marcarse vencida
    print("5️⃣ Verificaciones de estado...")
    print(f"   ¿Debe marcarse vencida?: {renta.debe_marcarse_vencida()}")
    print(f"   Días de retraso: {renta.dias_de_retraso()}\n")
    
    # 6️⃣ Simular retraso
    print("6️⃣ Simulando retraso (cambiar fecha de devolución al pasado)...")
    renta.fecha_devolucion = datetime.now() - timedelta(days=2)
    renta.cambiar_estado('Vencida', usuario='admin123', motivo='Fecha de devolución pasada')
    
    dias_retraso = renta.dias_de_retraso()
    penalizacion = renta.calcular_penalizacion(Decimal('50.00'))
    
    print(f"   ⏰ Días de retraso: {dias_retraso}")
    print(f"   ⚠️ Penalización (${50}/día): ${penalizacion:.2f}")
    print(f"   💳 Saldo a pagar/devolver: ${renta.total_a_pagar_con_deposito():.2f}\n")
    
    # 7️⃣ Comparación
    print("7️⃣ Comparación de rentas...")
    renta2 = Renta(
        id_cliente=2,
        id_usuario=1,
        fecha_devolucion=datetime.now() + timedelta(days=5),
        dias_renta=5,
        total=Decimal('750.00'),
        deposito=Decimal('1000.00')
    )
    
    print(f"   ¿Renta == Renta2?: {renta == renta2}")
    print(f"   ¿Renta < Renta2?: {renta < renta2}\n")
    
    # 8️⃣ Debug info
    print("8️⃣ Información de debugging...")
    print(renta.debug_info())
    print()
    
    # 9️⃣ Conversión a dict
    print("9️⃣ Conversión a diccionario...")
    renta_dict = renta.to_dict()
    print(f"   Keys: {list(renta_dict.keys())}\n")
    
    # 10️⃣ Auditoría
    print("1️⃣0️⃣ Auditoría...")
    print("\nHistorial de estados:")
    for hist in renta.obtener_historial_estados():
        print(f"  - {hist}")
    
    print("="*80 + "\n")