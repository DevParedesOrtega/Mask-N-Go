"""
Módulo: disfraz.py
Ubicación: models/disfraz.py
Descripción: Modelo de datos para disfraces del inventario
Sistema: MaskNGO - Renta y Venta de Disfraces
Versión: 2.1 - Con logging, métodos de auditoría, validaciones en constructor
"""

from typing import Optional, Dict, Any
from decimal import Decimal
import logging
from utils.logger_config import setup_logger


# Configurar logging
logger = setup_logger('disfraz_model', 'logs/disfraces_model.log')


class Disfraz:
    """
    Clase que representa un disfraz en el inventario del sistema.
    
    Attributes:
        codigo_barras (str): Código único del disfraz (PK)
        descripcion (str): Nombre/descripción del disfraz
        talla (str): Talla del disfraz (S, M, L, XL, UNI, etc.)
        color (str): Color principal (nullable)
        categoria (str): Categoría (Superhéroes, Terror, Animales, etc.) (nullable)
        precio_venta (Decimal): Precio de venta
        precio_renta (Decimal): Precio de renta por día
        stock (int): Cantidad total en inventario
        disponible (int): Cantidad actualmente disponible para rentar/vender
        estado (str): Estado del producto (Activo/Inactivo)
        historial_estados (list): Historial de cambios de estado
    
    BD Campos (tabla INVENTARIO):
        - Codigo_Barras (PK, varchar)
        - Descripcion (text)
        - Talla (text)
        - Color (text, nullable)
        - Categoria (text, nullable, indexed)
        - Precio_Venta (decimal 10,2)
        - Precio_Renta (decimal 10,2)
        - Stock (int, default 0)
        - Disponible (int, default 0)
        - Estado (enum Activo/Inactivo, default Activo)
    """
    
    # Estados válidos
    ESTADOS_VALIDOS: tuple = ('Activo', 'Inactivo')
    
    def __init__(
        self,
        codigo_barras: str,
        descripcion: str,
        talla: str,
        precio_venta: Decimal,
        precio_renta: Decimal,
        stock: int,
        color: Optional[str] = None,
        categoria: Optional[str] = None,
        disponible: Optional[int] = None,
        estado: str = 'Activo'
    ) -> None:
        """
        Constructor de la clase Disfraz.
        
        Args:
            codigo_barras: Código único del disfraz
            descripcion: Nombre/descripción del disfraz
            talla: Talla del disfraz
            precio_venta: Precio de venta (Decimal)
            precio_renta: Precio de renta diario (Decimal)
            stock: Cantidad total en inventario
            color: Color principal (opcional, nullable)
            categoria: Categoría del disfraz (opcional, nullable)
            disponible: Cantidad disponible (default: igual a stock)
            estado: Estado del producto (default: 'Activo')
        """
        # Validaciones
        if precio_venta < 0:
            raise ValueError(f"Precio de venta no puede ser negativo: {precio_venta}")
        
        if precio_renta < 0:
            raise ValueError(f"Precio de renta no puede ser negativo: {precio_renta}")
        
        if stock < 0:
            raise ValueError(f"Stock no puede ser negativo: {stock}")
        
        if disponible is not None and disponible < 0:
            raise ValueError(f"Disponible no puede ser negativo: {disponible}")

        self.codigo_barras: str = codigo_barras
        self.descripcion: str = descripcion
        self.talla: str = talla
        self.color: Optional[str] = color
        self.categoria: Optional[str] = categoria
        self.precio_venta: Decimal = Decimal(str(precio_venta))
        self.precio_renta: Decimal = Decimal(str(precio_renta))
        self.stock: int = int(stock)
        self.disponible: int = int(disponible) if disponible is not None else int(stock)
        self.estado: str = estado
        
        # Historial de auditoría de estados
        self.historial_estados: list = []

        logger.info(f"Disfraz creado: {self.descripcion} ({self.codigo_barras})")


    # ============================================================
    # REPRESENTACIÓN Y COMPARACIÓN
    # ============================================================
    
    def __str__(self) -> str:
        """
        Representación legible del disfraz.
        
        Returns:
            str: Descripción del disfraz
        """
        return (f"Disfraz(código={self.codigo_barras}, {self.descripcion}, "
                f"Talla: {self.talla}, Stock: {self.disponible}/{self.stock})")
    
    def __repr__(self) -> str:
        """
        Representación técnica del objeto.
        
        Returns:
            str: Representación técnica
        """
        return self.__str__()
    
    def __eq__(self, other: Any) -> bool:
        """
        Compara si dos disfraces son el mismo por código de barras.
        
        Args:
            other: Otro objeto Disfraz
        
        Returns:
            bool: True si tienen el mismo código de barras
        """
        if not isinstance(other, Disfraz):
            return False
        return self.codigo_barras == other.codigo_barras
    
    def __hash__(self) -> int:
        """
        Genera hash del disfraz para usar en sets o dicts.
        
        Returns:
            int: Hash basado en el código de barras
        """
        return hash(self.codigo_barras)
    
    def __lt__(self, other: 'Disfraz') -> bool:
        """
        Compara disfraces por descripción (para ordenamiento alfabético).
        
        Args:
            other: Otro objeto Disfraz
        
        Returns:
            bool: True si descripción es menor alfabéticamente
        """
        if not isinstance(other, Disfraz):
            return NotImplemented
        return self.descripcion.lower() < other.descripcion.lower()
    
    def __le__(self, other: 'Disfraz') -> bool:
        """Menor o igual que."""
        return self == other or self < other
    
    def __gt__(self, other: 'Disfraz') -> bool:
        """Mayor que."""
        return not self <= other
    
    def __ge__(self, other: 'Disfraz') -> bool:
        """Mayor o igual que."""
        return not self < other


    # ============================================================
    # CONVERSIÓN A DICCIONARIO
    # ============================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el objeto Disfraz a diccionario.
        
        Returns:
            Dict: Diccionario con los datos del disfraz
        """
        return {
            'codigo_barras': self.codigo_barras,
            'descripcion': self.descripcion,
            'talla': self.talla,
            'color': self.color,
            'categoria': self.categoria,
            'precio_venta': float(self.precio_venta),
            'precio_renta': float(self.precio_renta),
            'stock': self.stock,
            'disponible': self.disponible,
            'estado': self.estado,
            'historial_estados': self.historial_estados
        }


    # ============================================================
    # MÉTODOS DE INFORMACIÓN BÁSICA
    # ============================================================
    
    def esta_activo(self) -> bool:
        """
        Verifica si el disfraz está activo en el sistema.
        
        Returns:
            bool: True si está activo, False si está inactivo
        """
        return self.estado == 'Activo'
    
    def tiene_stock(self, cantidad: int = 1) -> bool:
        """
        Verifica si hay suficiente stock disponible.
        
        Args:
            cantidad: Cantidad requerida (default: 1)
        
        Returns:
            bool: True si hay suficiente disponible, False si no
        """
        return self.disponible >= cantidad
    
    def descripcion_completa(self) -> str:
        """
        Genera descripción completa del disfraz con detalles.
        
        Returns:
            str: Descripción completa
        """
        desc: str = f"{self.descripcion} - Talla {self.talla}"
        
        if self.color:
            desc += f" - Color: {self.color}"
        
        if self.categoria:
            desc += f" ({self.categoria})"
        
        return desc


    # ============================================================
    # MÉTODOS DE CÁLCULO DE PRECIOS
    # ============================================================
    
    def calcular_precio_renta(self, dias: int) -> Decimal:
        """
        Calcula el precio total de renta por cantidad de días.
        
        Args:
            dias: Número de días de renta
        
        Returns:
            Decimal: Precio total de renta
        """
        if dias <= 0:
            return Decimal('0')
        
        return self.precio_renta * Decimal(dias)
    
    def calcular_precio_venta_con_descuento(self, descuento_porcentaje: float) -> Decimal:
        """
        Calcula el precio de venta aplicando un descuento porcentual.
        
        Args:
            descuento_porcentaje: Descuento en porcentaje (0-100)
        
        Returns:
            Decimal: Precio final con descuento
        """
        if descuento_porcentaje < 0 or descuento_porcentaje > 100:
            return self.precio_venta
        
        descuento: Decimal = self.precio_venta * Decimal(descuento_porcentaje / 100)
        return self.precio_venta - descuento


    # ============================================================
    # MÉTODOS DE DISPONIBILIDAD
    # ============================================================
    
    def es_rentable(self) -> bool:
        """
        Verifica si el disfraz está disponible para renta.
        
        Condiciones:
        - Debe estar activo
        - Debe tener stock disponible
        
        Returns:
            bool: True si puede rentarse, False si no
        """
        return self.esta_activo() and self.disponible > 0
    
    def es_vendible(self) -> bool:
        """
        Verifica si el disfraz está disponible para venta.
        
        Condiciones:
        - Debe estar activo
        - Debe tener stock disponible
        
        Returns:
            bool: True si puede venderse, False si no
        """
        return self.esta_activo() and self.disponible > 0
    
    def rentados_actualmente(self) -> int:
        """
        Calcula la cantidad de disfraces actualmente rentados.
        
        Lógica: Rentados = Stock - Disponible
        
        Returns:
            int: Cantidad de disfraces rentados
        """
        rentados: int = self.stock - self.disponible
        return max(0, rentados)  # No puede ser negativo
    
    def porcentaje_disponible(self) -> float:
        """
        Calcula el porcentaje de stock disponible.
        
        Returns:
            float: Porcentaje (0-100)
        """
        if self.stock == 0:
            return 0.0
        
        return (self.disponible / self.stock) * 100
    
    def porcentaje_rentado(self) -> float:
        """
        Calcula el porcentaje de stock actualmente rentado.
        
        Returns:
            float: Porcentaje (0-100)
        """
        return 100.0 - self.porcentaje_disponible()


    # ============================================================
    # MÉTODOS DE AUDITORÍA
    # ============================================================

    def cambiar_estado(self, nuevo_estado: str, usuario: Optional[str] = None, motivo: Optional[str] = None) -> bool:
        """
        Cambia el estado del disfraz y registra el cambio en el historial.

        Args:
            nuevo_estado: Nuevo estado del disfraz
            usuario: Usuario que realiza el cambio (opcional)
            motivo: Motivo del cambio (opcional)

        Returns:
            bool: True si se cambió, False si no
        """
        if self.estado == nuevo_estado:
            logger.info(f"Estado no cambiado: {self.descripcion} ya está en estado '{nuevo_estado}'")
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

        logger.info(f"Estado cambiado para {self.descripcion} ({self.codigo_barras}): '{antiguo_estado}' → '{nuevo_estado}' (por {usuario or 'sistema'}, motivo: {motivo or 'sin especificar'})")
        return True

    def obtener_historial_estados(self) -> list:
        """
        Obtiene el historial de cambios de estado del disfraz.

        Returns:
            list: Lista de diccionarios con cambios de estado
        """
        return self.historial_estados

    def ultimo_cambio_estado(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el último cambio de estado del disfraz.

        Returns:
            dict o None: Último registro de cambio de estado
        """
        if self.historial_estados:
            return self.historial_estados[-1]
        return None

    def _get_current_datetime(self):
        """Obtiene la fecha/hora actual. Aislado para facilitar pruebas."""
        from datetime import datetime
        return datetime.now()


    # ============================================================
    # MÉTODOS DE REPORTE
    # ============================================================
    
    def resumen_estado(self) -> str:
        """
        Genera un resumen legible del estado del disfraz.
        
        Returns:
            str: Resumen en formato texto
        """
        estado_emoji: str = "🟢" if self.esta_activo() else "🔴"
        disponibilidad_emoji: str = "✅" if self.es_rentable() else "❌"
        
        lineas: list = [
            f"{estado_emoji} {self.descripcion_completa()}",
            f"├─ 📦 Stock: {self.disponible}/{self.stock} ({self.porcentaje_disponible():.1f}%)",
            f"├─ 🎯 Rentados: {self.rentados_actualmente()} ({self.porcentaje_rentado():.1f}%)",
            f"├─ 💰 Venta: ${self.precio_venta:.2f} | Renta: ${self.precio_renta:.2f}/día",
            f"├─ ⏱️  Renta 3 días: ${self.calcular_precio_renta(3):.2f}",
            f"└─ {disponibilidad_emoji} Estado: {'Disponible' if self.es_rentable() else 'No disponible'}"
        ]
        
        logger.debug(f"Resumen de estado generado para {self.descripcion}")
        return "\n".join(lineas)
    
    def resumen_corto(self) -> str:
        """
        Genera un resumen corto en una línea.
        
        Returns:
            str: Resumen corto
        """
        estado_emoji: str = "🟢" if self.esta_activo() else "🔴"
        resumen = f"{estado_emoji} {self.descripcion} - Stock: {self.disponible}/{self.stock}"
        logger.debug(f"Resumen corto generado para {self.descripcion}")
        return resumen
    
    def debug_info(self) -> str:
        """
        Genera información de debugging del disfraz.
        
        Returns:
            str: Información técnica del objeto
        """
        info_lines: list = [
            "🔧 DEBUG INFO - Disfraz",
            f"├─ Código: {self.codigo_barras}",
            f"├─ Descripción: '{self.descripcion}'",
            f"├─ Talla: {self.talla}",
            f"├─ Color: {self.color if self.color else 'N/A'}",
            f"├─ Categoría: {self.categoria if self.categoria else 'N/A'}",
            f"├─ Precio Venta: {self.precio_venta} (tipo: {type(self.precio_venta).__name__})",
            f"├─ Precio Renta: {self.precio_renta} (tipo: {type(self.precio_renta).__name__})",
            f"├─ Stock: {self.stock}",
            f"├─ Disponible: {self.disponible}",
            f"├─ Rentados: {self.rentados_actualmente()}",
            f"├─ Estado: {self.estado}",
            f"├─ Hash: {hash(self)}",
            f"├─ Es Rentable: {self.es_rentable()}",
            f"├─ Es Vendible: {self.es_vendible()}",
            f"├─ Historial Estados: {len(self.historial_estados)} cambios registrados",
            f"└─ Último Cambio Estado: {self.ultimo_cambio_estado() or 'Ninguno'}"
        ]
        
        logger.debug(f"Debug info generado para {self.descripcion}")
        return "\n".join(info_lines)


    # ============================================================
    # MÉTODOS DE CREACIÓN DESDE BD
    # ============================================================
    
    @staticmethod
    def from_db_row(row: tuple) -> 'Disfraz':
        """
        Crea un objeto Disfraz desde una fila de la base de datos.
        
        Args:
            row: Tupla con datos de la BD
                 (Codigo_Barras, Descripcion, Talla, Color, Categoria,
                  Precio_Venta, Precio_Renta, Stock, Disponible, Estado)
        
        Returns:
            Disfraz: Objeto Disfraz creado desde los datos
        
        Raises:
            IndexError: Si la tupla no tiene los campos requeridos
            TypeError: Si los tipos de datos no coinciden
            ValueError: Si los valores no son válidos
        """
        try:
            disfraz = Disfraz(
                codigo_barras=str(row[0]),
                descripcion=str(row[1]),
                talla=str(row[2]),
                color=str(row[3]) if row[3] else None,
                categoria=str(row[4]) if row[4] else None,
                precio_venta=Decimal(str(row[5])),
                precio_renta=Decimal(str(row[6])),
                stock=int(row[7]),
                disponible=int(row[8]),
                estado=str(row[9]) if row[9] else 'Activo'
            )
            logger.debug(f"Disfraz creado desde BD: {disfraz.descripcion} ({disfraz.codigo_barras})")
            return disfraz
        except (IndexError, TypeError, ValueError) as e:
            logger.error(f"Error al crear Disfraz desde BD: {e}")
            logger.error(f"   Row recibida: {row}")
            logger.error(f"   Tipos: {[type(x).__name__ for x in row]}")
            raise


    # ============================================================
    # MÉTODO DE VALIDACIÓN DE ESTADO
    # ============================================================
    
    def validar_estado(self) -> bool:
        """
        Valida que el estado sea uno de los válidos.
        
        Returns:
            bool: True si es válido, False si no
        """
        return self.estado in self.ESTADOS_VALIDOS



# ============================================================
# EJEMPLO DE USO
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*80)
    print("EJEMPLO DE USO - Clase Disfraz v2.1")
    print("CON LOGGING, VALIDACIONES Y MÉTODOS DE AUDITORÍA")
    print("="*80 + "\n")
    
    # Crear disfraz
    print("1️⃣ Creando disfraz...")
    disfraz = Disfraz(
        codigo_barras="DIS001",
        descripcion="Spider-Man Clásico",
        talla="M",
        color="Rojo/Azul",
        categoria="Superhéroes",
        precio_venta=Decimal('850.00'),
        precio_renta=Decimal('150.00'),
        stock=5
    )
    print()
    
    # Información básica
    print("2️⃣ Información básica...")
    print(f"   Descripción completa: {disfraz.descripcion_completa()}")
    print(f"   Está activo: {disfraz.esta_activo()}")
    print(f"   Tiene stock para 3: {disfraz.tiene_stock(3)}\n")
    
    # Cálculos de precios
    print("3️⃣ Cálculos de precios...")
    print(f"   Precio renta 3 días: ${disfraz.calcular_precio_renta(3):.2f}")
    print(f"   Precio venta con 10% descuento: ${disfraz.calcular_precio_venta_con_descuento(10):.2f}")
    print(f"   Precio venta con 25% descuento: ${disfraz.calcular_precio_venta_con_descuento(25):.2f}\n")
    
    # Disponibilidad
    print("4️⃣ Disponibilidad...")
    print(f"   Es rentable: {disfraz.es_rentable()}")
    print(f"   Es vendible: {disfraz.es_vendible()}")
    print(f"   Rentados actualmente: {disfraz.rentados_actualmente()}")
    print(f"   Porcentaje disponible: {disfraz.porcentaje_disponible():.1f}%")
    print(f"   Porcentaje rentado: {disfraz.porcentaje_rentado():.1f}%\n")
    
    # Resumen
    print("5️⃣ Resumen del estado...")
    print(f"\n{disfraz.resumen_estado()}\n")
    
    # Resumen corto
    print("6️⃣ Resumen corto...")
    print(f"   {disfraz.resumen_corto()}\n")
    
    # Comparación
    print("7️⃣ Comparación de disfraces...")
    disfraz2 = Disfraz(
        codigo_barras="DIS002",
        descripcion="Batman Oscuro",
        talla="L",
        color="Negro/Gris",
        categoria="Superhéroes",
        precio_venta=Decimal('900.00'),
        precio_renta=Decimal('160.00'),
        stock=3
    )
    
    print(f"   ¿Disfraz == Disfraz2?: {disfraz == disfraz2}")
    print(f"   ¿Disfraz < Disfraz2?: {disfraz < disfraz2}")
    print(f"   Ordenados: {sorted([disfraz2, disfraz])}\n")
    
    # Debug info
    print("8️⃣ Información de debugging...")
    print(f"\n{disfraz.debug_info()}\n")
    
    # Conversión a dict
    print("9️⃣ Conversión a diccionario...")
    disfraz_dict = disfraz.to_dict()
    print(f"   {disfraz_dict}\n")
    
    # Validación
    print("🔟 Validación...")
    print(f"   ¿Estado válido?: {disfraz.validar_estado()}\n")
    
    # Auditoría
    print("1️⃣1️⃣ Auditoría...")
    print("\n--- CAMBIO DE ESTADO ---")
    disfraz.cambiar_estado("Inactivo", usuario="admin123", motivo="No se vende más")

    print("\nHistorial de estados:")
    for hist in disfraz.obtener_historial_estados():
        print(f"  - {hist}")
    
    print("="*80 + "\n")