"""
Módulo: venta.py
Ubicación: models/venta.py
Descripción: Modelo de datos para ventas del sistema
Sistema: MaskNGO - Renta y Venta de Disfraces
Versión: 2.1 - Con logging, métodos de auditoría, validaciones en constructor
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
import logging
from utils.logger_config import setup_logger


# Configurar logging
logger = setup_logger('venta_model', 'logs/ventas_model.log')


class DetalleVenta:
    """
    Clase que representa un producto en una venta.
    
    Attributes:
        id_detalle_venta (int): ID único del detalle (PK)
        id_venta (int): ID de la venta padre (FK)
        codigo_barras (str): Código del disfraz (FK)
        cantidad (int): Cantidad vendida
        precio_unitario (Decimal): Precio unitario al momento de venta
        subtotal (Decimal): cantidad × precio_unitario (se calcula y valida)
        historial_estados (list): Historial de cambios de estado
    
    BD Campos (tabla DETALLE_VENTAS):
        - ID_DetalleVenta (PK, int, auto_increment)
        - Id_Venta (FK, int)
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
        id_detalle_venta: Optional[int] = None,
        id_venta: Optional[int] = None,
        subtotal: Optional[Decimal] = None
    ) -> None:
        """
        Constructor de DetalleVenta.
        
        Args:
            codigo_barras: Código del disfraz
            cantidad: Cantidad vendida
            precio_unitario: Precio unitario (Decimal)
            id_detalle_venta: ID del detalle (generado por BD)
            id_venta: ID de la venta padre
            subtotal: Subtotal pre-calculado (si viene de BD, se valida)
        """
        # Validaciones
        if cantidad <= 0:
            raise ValueError(f"Cantidad debe ser mayor a 0: {cantidad}")
        
        if precio_unitario < 0:
            raise ValueError(f"Precio unitario no puede ser negativo: {precio_unitario}")

        self.id_detalle_venta: Optional[int] = id_detalle_venta
        self.id_venta: Optional[int] = id_venta
        self.codigo_barras: str = codigo_barras
        self.cantidad: int = int(cantidad)
        self.precio_unitario: Decimal = Decimal(str(precio_unitario))
        
        # Calcular subtotal
        self.subtotal: Decimal = Decimal(self.cantidad) * self.precio_unitario
        
        # Validar si viene de BD
        if subtotal is not None:
            subtotal_bd = Decimal(str(subtotal))
            if subtotal_bd != self.subtotal:
                logger.warning(f"Subtotal de BD ({subtotal_bd}) ≠ calculado ({self.subtotal}). Usando calculado.")
        
        # Historial de auditoría de estados
        self.historial_estados: list = []

        logger.info(f"DetalleVenta creado: {self.codigo_barras} (Cant: {self.cantidad}, ${self.subtotal:.2f})")
    
    def __str__(self) -> str:
        """Representación legible del detalle."""
        return f"DetalleVenta({self.codigo_barras}, Cant: {self.cantidad}, ${self.subtotal:.2f})"
    
    def __repr__(self) -> str:
        """Representación técnica."""
        return self.__str__()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            'id_detalle_venta': self.id_detalle_venta,
            'id_venta': self.id_venta,
            'codigo_barras': self.codigo_barras,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario),
            'subtotal': float(self.subtotal),
            'historial_estados': self.historial_estados
        }
    
    @staticmethod
    def from_db_row(row: tuple) -> 'DetalleVenta':
        """
        Crea DetalleVenta desde fila de BD.
        
        Args:
            row: (ID_DetalleVenta, Id_Venta, Codigo_Barras, Cantidad, Precio_Unitario, Subtotal)
        
        Returns:
            DetalleVenta: Objeto creado
        """
        try:
            detalle = DetalleVenta(
                id_detalle_venta=int(row[0]),
                id_venta=int(row[1]),
                codigo_barras=str(row[2]),
                cantidad=int(row[3]),
                precio_unitario=Decimal(str(row[4])),
                subtotal=Decimal(str(row[5]))
            )
            logger.debug(f"DetalleVenta creado desde BD: {detalle.codigo_barras} (Cant: {detalle.cantidad})")
            return detalle
        except (IndexError, TypeError, ValueError) as e:
            logger.error(f"Error al crear DetalleVenta desde BD: {e}")
            logger.error(f"   Row recibida: {row}")
            logger.error(f"   Tipos: {[type(x).__name__ for x in row]}")
            raise


class Venta:
    """
    Clase que representa una venta en el sistema.
    
    Attributes:
        id_venta (int): ID único de la venta (PK)
        folio (str): Folio único (VEN-YYYYMMDD-####)
        id_cliente (int): ID del cliente (FK)
        usuario_id (int): ID del empleado que registró (FK)
        fecha_venta (datetime): Fecha de la venta
        total (Decimal): Total de la venta (sin descuento)
        descuento_porcentaje (Decimal): Porcentaje de descuento
        descuento_monto (Decimal): Monto del descuento en pesos
        motivo_descuento (str): Justificación del descuento (OBLIGATORIO si hay descuento)
        motivo_venta (str): Evento especial (Halloween, etc.)
        notas (str): Observaciones adicionales
        estado (str): Estado (Activa, Cancelada)
        cancelada_por (int): ID del admin que canceló
        fecha_cancelacion (datetime): Fecha de cancelación
        motivo_cancelacion (str): Razón de cancelación
        metodo_pago (str): Forma de pago (Efectivo, tarjeta, Transferencia)
        detalles (List[DetalleVenta]): Productos vendidos
        historial_estados (list): Historial de cambios de estado
    
    BD Campos (tabla VENTAS):
        - Id_Venta (PK, int, auto_increment)
        - Folio (varchar 20, UNIQUE)
        - Id_cliente (FK, int)
        - Usuario_id (FK, int)
        - fecha_venta (datetime, default CURRENT_TIMESTAMP)
        - Total (decimal 10,2)
        - Descuento_Porcentaje (decimal 5,2)
        - Descuento_Monto (decimal 10,2)
        - Motivo_Descuento (text)
        - Motivo_Venta (varchar 100)
        - Notas (text)
        - Estado (enum Activa/Cancelada)
        - Cancelada_Por (int, nullable)
        - Fecha_Cancelacion (datetime, nullable)
        - Motivo_Cancelacion (text)
        - metodo_pago (enum Efectivo/tarjeta/Transferencia, default Efectivo)
    """
    
    # Estados válidos
    ESTADOS_VALIDOS: Tuple[str, ...] = ('Activa', 'Cancelada')
    
    # Métodos de pago válidos
    METODOS_PAGO_VALIDOS: Tuple[str, ...] = ('Efectivo', 'tarjeta', 'Transferencia')
    
    # Límite máximo de descuento permitido
    DESCUENTO_MAXIMO: Decimal = Decimal('50.00')  # 50%
    
    def __init__(
        self,
        id_cliente: int,
        usuario_id: int,
        total: Decimal,
        metodo_pago: str,
        id_venta: Optional[int] = None,
        folio: Optional[str] = None,
        fecha_venta: Optional[datetime] = None,
        descuento_porcentaje: Decimal = Decimal('0.00'),
        descuento_monto: Decimal = Decimal('0.00'),
        motivo_descuento: Optional[str] = None,
        motivo_venta: Optional[str] = None,
        notas: Optional[str] = None,
        estado: str = 'Activa',
        cancelada_por: Optional[int] = None,
        fecha_cancelacion: Optional[datetime] = None,
        motivo_cancelacion: Optional[str] = None
    ) -> None:
        """
        Constructor de Venta.
        
        Args:
            id_cliente: ID del cliente
            usuario_id: ID del usuario que registró
            total: Total de la venta (Decimal)
            metodo_pago: Método de pago
            id_venta: ID de la venta (generado por BD)
            folio: Folio único (generado por controller)
            fecha_venta: Fecha de venta (default: ahora)
            descuento_porcentaje: Porcentaje de descuento (Decimal)
            descuento_monto: Monto del descuento (Decimal)
            motivo_descuento: Motivo del descuento (obligatorio si hay descuento)
            motivo_venta: Evento/motivo de venta
            notas: Observaciones
            estado: Estado de la venta (default: 'Activa')
            cancelada_por: ID del usuario que canceló
            fecha_cancelacion: Fecha de cancelación
            motivo_cancelacion: Razón de cancelación
        """
        # Validaciones
        if id_cliente <= 0:
            raise ValueError(f"ID de cliente debe ser mayor a 0: {id_cliente}")
        
        if usuario_id <= 0:
            raise ValueError(f"ID de usuario debe ser mayor a 0: {usuario_id}")
        
        if total < 0:
            raise ValueError(f"Total no puede ser negativo: {total}")
        
        if descuento_porcentaje < 0 or descuento_porcentaje > 100:
            raise ValueError(f"Descuento porcentaje debe estar entre 0% y 100%: {descuento_porcentaje}")
        
        if descuento_monto < 0:
            raise ValueError(f"Descuento monto no puede ser negativo: {descuento_monto}")
        
        if metodo_pago not in self.METODOS_PAGO_VALIDOS:
            raise ValueError(f"Método de pago '{metodo_pago}' no es válido. Válidos: {', '.join(self.METODOS_PAGO_VALIDOS)}")

        self.id_venta: Optional[int] = id_venta
        self.folio: Optional[str] = folio
        self.id_cliente: int = int(id_cliente)
        self.usuario_id: int = int(usuario_id)
        self.fecha_venta: datetime = fecha_venta or datetime.now()
        self.total: Decimal = Decimal(str(total))
        self.descuento_porcentaje: Decimal = Decimal(str(descuento_porcentaje))
        self.descuento_monto: Decimal = Decimal(str(descuento_monto))
        self.motivo_descuento: Optional[str] = motivo_descuento
        self.motivo_venta: Optional[str] = motivo_venta
        self.notas: Optional[str] = notas
        self.metodo_pago: str = metodo_pago
        self.estado: str = estado
        self.cancelada_por: Optional[int] = cancelada_por
        self.fecha_cancelacion: Optional[datetime] = fecha_cancelacion
        self.motivo_cancelacion: Optional[str] = motivo_cancelacion
        self.detalles: List[DetalleVenta] = []
        
        # Historial de auditoría de estados
        self.historial_estados: list = []

        logger.info(f"Venta creada: Folio {self.folio}, Cliente {self.id_cliente}, Total ${self.total:.2f}")


    # ============================================================
    # REPRESENTACIÓN Y COMPARACIÓN
    # ============================================================
    
    def __str__(self) -> str:
        """Representación legible de la venta."""
        return (f"Venta({self.folio}, Cliente: {self.id_cliente}, "
                f"Total: ${self.obtener_total_final():.2f}, Estado: {self.estado})")
    
    def __repr__(self) -> str:
        """Representación técnica."""
        return self.__str__()
    
    def __eq__(self, other: Any) -> bool:
        """Compara si dos ventas son la misma por ID."""
        if not isinstance(other, Venta):
            return False
        return self.id_venta == other.id_venta
    
    def __hash__(self) -> int:
        """Hash para usar en sets/dicts."""
        return hash(self.id_venta) if self.id_venta else hash(id(self))
    
    def __lt__(self, other: 'Venta') -> bool:
        """Compara ventas por fecha (para ordenamiento)."""
        if not isinstance(other, Venta):
            return NotImplemented
        return self.fecha_venta < other.fecha_venta
    
    def __le__(self, other: 'Venta') -> bool:
        """Menor o igual que."""
        return self == other or self < other
    
    def __gt__(self, other: 'Venta') -> bool:
        """Mayor que."""
        return not self <= other
    
    def __ge__(self, other: 'Venta') -> bool:
        """Mayor o igual que."""
        return not self < other


    # ============================================================
    # CONVERSIÓN A DICCIONARIO
    # ============================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la venta a diccionario."""
        return {
            'id_venta': self.id_venta,
            'folio': self.folio,
            'id_cliente': self.id_cliente,
            'usuario_id': self.usuario_id,
            'fecha_venta': self.fecha_venta.isoformat() if self.fecha_venta else None,
            'total': float(self.total),
            'descuento_porcentaje': float(self.descuento_porcentaje),
            'descuento_monto': float(self.descuento_monto),
            'motivo_descuento': self.motivo_descuento,
            'motivo_venta': self.motivo_venta,
            'notas': self.notas,
            'metodo_pago': self.metodo_pago,
            'estado': self.estado,
            'cancelada_por': self.cancelada_por,
            'fecha_cancelacion': self.fecha_cancelacion.isoformat() if self.fecha_cancelacion else None,
            'motivo_cancelacion': self.motivo_cancelacion,
            'total_final': float(self.obtener_total_final()),
            'detalles': [d.to_dict() for d in self.detalles],
            'historial_estados': self.historial_estados
        }


    # ============================================================
    # MÉTODOS DE DETALLES
    # ============================================================
    
    def agregar_detalle(self, detalle: DetalleVenta) -> None:
        """
        Agrega un producto a la venta.
        
        Args:
            detalle: Objeto DetalleVenta a agregar
        """
        detalle.id_venta = self.id_venta
        self.detalles.append(detalle)
        logger.info(f"Detalle agregado a venta {self.folio}: {detalle.codigo_barras}")
    
    def obtener_detalles(self) -> List[DetalleVenta]:
        """Retorna lista de detalles."""
        return self.detalles
    
    def contar_detalles(self) -> int:
        """Retorna cantidad de detalles."""
        return len(self.detalles)
    
    def obtener_subtotal_detalles(self) -> Decimal:
        """Calcula suma de todos los subtotales."""
        return sum(d.subtotal for d in self.detalles) if self.detalles else Decimal('0.00')


    # ============================================================
    # MÉTODOS DE DESCUENTO
    # ============================================================
    
    def tiene_descuento(self) -> bool:
        """Verifica si la venta tiene descuento."""
        return self.descuento_porcentaje > 0 or self.descuento_monto > 0
    
    def calcular_descuento_monto(self) -> Decimal:
        """
        Calcula el monto del descuento basado en el porcentaje.
        
        Returns:
            Decimal: Monto del descuento
        """
        if self.descuento_porcentaje > 0:
            return self.total * (self.descuento_porcentaje / Decimal('100'))
        return Decimal('0.00')
    
    def obtener_total_sin_descuento(self) -> Decimal:
        """
        Obtiene el total original sin descuento.
        
        Returns:
            Decimal: Total sin descuento
        """
        return self.total
    
    def obtener_total_final(self) -> Decimal:
        """
        Calcula el total final con descuento aplicado.
        
        Returns:
            Decimal: Total - descuento
        """
        return self.total - self.descuento_monto
    
    def es_descuento_valido(self, descuento_maximo: Optional[Decimal] = None) -> bool:
        """
        Verifica si el descuento no excede el límite máximo.
        
        Args:
            descuento_maximo: Límite máximo de descuento (default: 50%)
        
        Returns:
            bool: True si el descuento es válido, False si no
        """
        if descuento_maximo is None:
            descuento_maximo = self.DESCUENTO_MAXIMO
        
        return self.descuento_porcentaje <= descuento_maximo


    # ============================================================
    # MÉTODOS DE ESTADO
    # ============================================================
    
    def esta_activa(self) -> bool:
        """Verifica si la venta está activa."""
        return self.estado == 'Activa'
    
    def esta_cancelada(self) -> bool:
        """Verifica si la venta fue cancelada."""
        return self.estado == 'Cancelada'
    
    def puede_cancelarse(self) -> bool:
        """
        Verifica si la venta puede ser cancelada.
        
        Condiciones:
        - Debe estar activa
        
        Returns:
            bool: True si puede cancelarse, False si no
        """
        return self.esta_activa()
    
    def cancelar_venta(self, id_usuario: int, motivo: str) -> bool:
        """
        Cancela la venta registrando el usuario y motivo.
        
        Args:
            id_usuario: ID del usuario admin que cancela
            motivo: Razón de la cancelación
        
        Returns:
            bool: True si se canceló exitosamente, False si no pudo cancelarse
        """
        if not self.puede_cancelarse():
            logger.warning(f"La venta {self.folio} no puede cancelarse (estado: {self.estado})")
            return False
        
        self.estado = 'Cancelada'
        self.cancelada_por = id_usuario
        self.fecha_cancelacion = datetime.now()
        self.motivo_cancelacion = motivo
        
        # Registrar en historial
        registro = {
            'fecha': self.fecha_cancelacion,
            'accion': 'cancelacion',
            'usuario': id_usuario,
            'motivo': motivo
        }
        self.historial_estados.append(registro)

        logger.info(f"Venta {self.folio} cancelada por usuario {id_usuario}")
        return True
    
    def validar_metodo_pago(self) -> bool:
        """Valida que el método de pago sea válido."""
        return self.metodo_pago in self.METODOS_PAGO_VALIDOS
    
    def validar_estado(self) -> bool:
        """Valida que el estado sea uno de los válidos."""
        return self.estado in self.ESTADOS_VALIDOS


    # ============================================================
    # MÉTODOS DE AUDITORÍA
    # ============================================================

    def obtener_historial_estados(self) -> list:
        """
        Obtiene el historial de cambios de estado de la venta.

        Returns:
            list: Lista de diccionarios con cambios de estado
        """
        return self.historial_estados

    def ultimo_cambio_estado(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el último cambio de estado de la venta.

        Returns:
            dict o None: Último registro de cambio de estado
        """
        if self.historial_estados:
            return self.historial_estados[-1]
        return None


    # ============================================================
    # MÉTODOS DE VALIDACIÓN
    # ============================================================
    
    def validar_venta(self) -> Tuple[bool, str]:
        """
        Valida que la venta tenga datos correctos antes de registrar.
        
        Returns:
            Tuple[bool, str]: (es_válida, mensaje)
        """
        if not self.detalles:
            return False, "La venta debe tener al menos un producto"
        
        if self.total <= 0:
            return False, "El total debe ser mayor a 0"
        
        if self.descuento_porcentaje < 0 or self.descuento_porcentaje > 100:
            return False, "El descuento debe estar entre 0% y 100%"
        
        if not self.es_descuento_valido():
            return False, f"El descuento no puede exceder {self.DESCUENTO_MAXIMO}%"
        
        if self.tiene_descuento() and not self.motivo_descuento:
            return False, "El descuento requiere justificación (motivo)"
        
        if not self.validar_metodo_pago():
            return False, f"Método de pago '{self.metodo_pago}' no es válido. Válidos: {', '.join(self.METODOS_PAGO_VALIDOS)}"
        
        if not self.validar_estado():
            return False, f"Estado '{self.estado}' no es válido"
        
        if self.esta_cancelada() and not self.motivo_cancelacion:
            return False, "Una venta cancelada debe tener motivo de cancelación"
        
        return True, "Venta válida"


    # ============================================================
    # MÉTODOS DE REPORTE
    # ============================================================
    
    def resumen_corto(self) -> str:
        """Genera un resumen corto en una línea."""
        estado_emoji = "🟢" if self.esta_activa() else "❌"
        resumen = f"{estado_emoji} {self.folio} - Total: ${self.obtener_total_final():.2f} ({self.metodo_pago})"
        logger.debug(f"Resumen corto generado para venta {self.folio}")
        return resumen
    
    def resumen_estado(self) -> str:
        """Genera un resumen legible completo de la venta."""
        lineas: List[str] = [
            f"🧾 VENTA {self.folio}",
            f"├─ 📅 Fecha: {self.fecha_venta.strftime('%Y-%m-%d %H:%M:%S')}",
            f"├─ 👤 Cliente ID: {self.id_cliente}",
            f"├─ 👨‍💼 Usuario ID: {self.usuario_id}",
            f"├─ 📦 Productos: {self.contar_detalles()}",
            f"├─ 💰 Subtotal: ${self.total:.2f}",
        ]
        
        if self.tiene_descuento():
            lineas.append(f"├─ 🏷️  Descuento: {self.descuento_porcentaje}% (${self.descuento_monto:.2f})")
            lineas.append(f"├─ 📝 Motivo: {self.motivo_descuento}")
        
        lineas.append(f"├─ 💳 Total Final: ${self.obtener_total_final():.2f}")
        lineas.append(f"├─ 💵 Método: {self.metodo_pago}")
        lineas.append(f"├─ 📊 Estado: {self.estado}")
        
        if self.motivo_venta:
            lineas.append(f"├─ 🎉 Evento: {self.motivo_venta}")
        
        if self.notas:
            lineas.append(f"├─ 📌 Notas: {self.notas}")
        
        if self.esta_cancelada():
            lineas.append(f"├─ ❌ Cancelada: {self.fecha_cancelacion.strftime('%Y-%m-%d %H:%M:%S')}")
            lineas.append(f"├─ 👤 Cancelada por: Usuario {self.cancelada_por}")
            lineas.append(f"└─ 📝 Motivo: {self.motivo_cancelacion}")
        
        logger.debug(f"Resumen de estado generado para venta {self.folio}")
        return "\n".join(lineas)
    
    def debug_info(self) -> str:
        """Genera información de debugging de la venta."""
        valido, msg_validacion = self.validar_venta()
        
        info_lines: List[str] = [
            "🔧 DEBUG INFO - Venta",
            f"├─ ID: {self.id_venta}",
            f"├─ Folio: {self.folio}",
            f"├─ Cliente ID: {self.id_cliente}",
            f"├─ Usuario ID: {self.usuario_id}",
            f"├─ Fecha Venta: {self.fecha_venta} (tipo: {type(self.fecha_venta).__name__})",
            f"├─ Total: {self.total} (tipo: {type(self.total).__name__})",
            f"├─ Descuento %: {self.descuento_porcentaje}% (tipo: {type(self.descuento_porcentaje).__name__})",
            f"├─ Descuento $: {self.descuento_monto} (tipo: {type(self.descuento_monto).__name__})",
            f"├─ Total Final: ${self.obtener_total_final():.2f}",
            f"├─ Método Pago: {self.metodo_pago} (válido: {self.validar_metodo_pago()})",
            f"├─ Estado: {self.estado} (válido: {self.validar_estado()})",
            f"├─ Detalles: {self.contar_detalles()}",
            f"├─ Hash: {hash(self)}",
            f"├─ Está Activa: {self.esta_activa()}",
            f"├─ Puede Cancelarse: {self.puede_cancelarse()}",
            f"├─ Descuento Válido: {self.es_descuento_valido()}",
            f"├─ Validación: {'✓ Válida' if valido else '✗ Inválida'}",
            f"├─ Mensaje: {msg_validacion}",
            f"├─ Historial Estados: {len(self.historial_estados)} cambios registrados",
            f"└─ Último Cambio Estado: {self.ultimo_cambio_estado() or 'Ninguno'}"
        ]
        
        logger.debug(f"Debug info generado para venta {self.folio}")
        return "\n".join(info_lines)


    # ============================================================
    # CREACIÓN DESDE BD
    # ============================================================
    
    @staticmethod
    def from_db_row(row: tuple) -> 'Venta':
        """
        Crea un objeto Venta desde fila de BD.
        
        Args:
            row: (Id_Venta, Folio, Id_cliente, Usuario_id, fecha_venta, Total,
                  Descuento_Porcentaje, Descuento_Monto, Motivo_Descuento,
                  Motivo_Venta, Notas, Estado, Cancelada_Por,
                  Fecha_Cancelacion, Motivo_Cancelacion, metodo_pago)
        
        Returns:
            Venta: Objeto Venta creado
        
        Raises:
            IndexError: Si la tupla no tiene los campos requeridos
            TypeError: Si los tipos de datos no coinciden
            ValueError: Si los valores no son válidos
        """
        try:
            venta = Venta(
                id_venta=int(row[0]),
                folio=str(row[1]) if row[1] else None,
                id_cliente=int(row[2]),
                usuario_id=int(row[3]),
                fecha_venta=row[4] if isinstance(row[4], datetime) else datetime.fromisoformat(str(row[4])) if row[4] else None,
                total=Decimal(str(row[5])),
                descuento_porcentaje=Decimal(str(row[6])) if row[6] else Decimal('0.00'),
                descuento_monto=Decimal(str(row[7])) if row[7] else Decimal('0.00'),
                motivo_descuento=str(row[8]) if row[8] else None,
                motivo_venta=str(row[9]) if row[9] else None,
                notas=str(row[10]) if row[10] else None,
                estado=str(row[11]) if row[11] else 'Activa',
                cancelada_por=int(row[12]) if row[12] else None,
                fecha_cancelacion=row[13] if isinstance(row[13], datetime) or row[13] is None else datetime.fromisoformat(str(row[13])) if row[13] else None,
                motivo_cancelacion=str(row[14]) if row[14] else None,
                metodo_pago=str(row[15]) if row[15] else 'Efectivo'
            )
            logger.debug(f"Venta creada desde BD: Folio {venta.folio}, Cliente {venta.id_cliente}")
            return venta
        except (IndexError, TypeError, ValueError) as e:
            logger.error(f"Error al crear Venta desde BD: {e}")
            logger.error(f"   Row recibida: {row}")
            logger.error(f"   Tipos: {[type(x).__name__ for x in row]}")
            raise



# ============================================================
# EJEMPLO DE USO
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*80)
    print("EJEMPLO DE USO - Clase Venta v2.1")
    print("CON LOGGING, VALIDACIONES Y MÉTODOS DE AUDITORÍA")
    print("="*80 + "\n")
    
    # 1️⃣ Crear venta
    print("1️⃣ Creando venta...")
    venta = Venta(
        id_cliente=1,
        usuario_id=1,
        total=Decimal('1500.00'),
        metodo_pago='Efectivo',
        folio='VEN-20251126-0001',
        descuento_porcentaje=Decimal('10'),
        motivo_descuento='Cliente frecuente',
        motivo_venta='Halloween'
    )
    print()
    
    # 2️⃣ Agregar detalles
    print("2️⃣ Agregando detalles...")
    venta.agregar_detalle(DetalleVenta('DIS001', 2, Decimal('500.00')))
    venta.agregar_detalle(DetalleVenta('DIS002', 1, Decimal('500.00')))
    print()
    
    # 3️⃣ Calcular descuento
    print("3️⃣ Calculando descuento...")
    venta.descuento_monto = venta.calcular_descuento_monto()
    print(f"   Descuento calculado: ${venta.descuento_monto:.2f}\n")
    
    # 4️⃣ Validar
    print("4️⃣ Validando venta...")
    valida, msg = venta.validar_venta()
    print(f"   ¿Válida?: {valida} - {msg}\n")
    
    # 5️⃣ Información
    print("5️⃣ Información...")
    print(f"   Total sin descuento: ${venta.obtener_total_sin_descuento():.2f}")
    print(f"   Total final: ${venta.obtener_total_final():.2f}")
    print(f"   Tiene descuento: {venta.tiene_descuento()}")
    print(f"   Descuento válido: {venta.es_descuento_valido()}\n")
    
    # 6️⃣ Resumen
    print("6️⃣ Resumen completo...")
    print(venta.resumen_estado())
    print()
    
    # 7️⃣ Resumen corto
    print("7️⃣ Resumen corto...")
    print(f"   {venta.resumen_corto()}\n")
    
    # 8️⃣ Comparación
    print("8️⃣ Comparación de ventas...")
    venta2 = Venta(
        id_cliente=2,
        usuario_id=1,
        total=Decimal('2000.00'),
        metodo_pago='tarjeta',
        folio='VEN-20251126-0002'
    )
    venta2.agregar_detalle(DetalleVenta('DIS003', 3, Decimal('500.00')))
    
    print(f"   ¿Venta == Venta2?: {venta == venta2}")
    print(f"   ¿Venta < Venta2?: {venta < venta2}\n")
    
    # 9️⃣ Cancelación
    print("9️⃣ Prueba de cancelación...")
    print(f"   ¿Puede cancelarse?: {venta.puede_cancelarse()}")
    exito = venta.cancelar_venta(1, "Error en registro")
    print(f"   ¿Se canceló?: {exito}")
    print(f"   ¿Puede cancelarse ahora?: {venta.puede_cancelarse()}\n")
    
    # 🔟 Debug info
    print("🔟 Información de debugging...")
    print(venta.debug_info())
    print()
    
    # 1️⃣1️⃣ Conversión a dict
    print("1️⃣1️⃣ Conversión a diccionario...")
    venta_dict = venta.to_dict()
    print(f"   Keys: {list(venta_dict.keys())}\n")
    
    # 1️⃣2️⃣ Auditoría
    print("1️⃣2️⃣ Auditoría...")
    print("\nHistorial de estados:")
    for hist in venta.obtener_historial_estados():
        print(f"  - {hist}")
    
    print("="*80 + "\n")