"""
Módulo: cliente.py
Ubicación: models/cliente.py
Descripción: Modelo de datos para clientes del sistema
Sistema: MaskNGO - Renta y Venta de Disfraces
Versión: 2.3 - Con logging, métodos de auditoría
"""

from datetime import datetime
from typing import Optional, Dict, Any, Any as AnyType
import logging
from utils.logger_config import setup_logger


# Configurar logging
logger = setup_logger('cliente_model', 'logs/clientes_model.log')


class Cliente:
    """
    Clase que representa un cliente del sistema.

    Attributes:
        id_cliente (int): ID único del cliente
        nombre (str): Nombre del cliente
        apellido_paterno (str): Apellido paterno
        telefono (str): Teléfono de contacto
        estado (str): Estado del cliente ('Activo' / 'Inactivo' / 'Bloqueado' / 'Suspendido')
        fecha_registro (datetime): Fecha de registro en el sistema
        estadisticas (Dict): Diccionario con estadísticas del cliente
        historial_estados (List[Dict]): Historial de cambios de estado

    BD Campos (tabla CLIENTES):
        - Id_cliente (PK, int, auto_increment)
        - Nombre (text)
        - Apellido_Paterno (text)
        - Telefono (varchar, unique)
        - Fecha_Registro (datetime, default current_timestamp)
        - Estado (enum: 'Activo'/'Bloqueado'/'Suspendido'/'Inactivo', default 'Activo')
    """

    def __init__(
        self,
        nombre: str,
        apellido_paterno: str,
        telefono: str,
        id_cliente: Optional[int] = None,
        fecha_registro: Optional[datetime] = None,
        estado: str = "Activo",
    ) -> None:
        """
        Constructor de la clase Cliente.

        Args:
            nombre: Nombre del cliente
            apellido_paterno: Apellido paterno del cliente
            telefono: Teléfono de contacto (10-15 dígitos)
            id_cliente: ID único del cliente (generado por BD)
            fecha_registro: Fecha de registro en el sistema
            estado: Estado lógico del cliente ('Activo', 'Inactivo', 'Bloqueado', 'Suspendido')
        """
        self.id_cliente: Optional[int] = id_cliente
        self.nombre: str = nombre
        self.apellido_paterno: str = apellido_paterno
        self.telefono: str = telefono
        self.estado: str = estado or "Activo"
        self.fecha_registro: datetime = fecha_registro or datetime.now()

        # Datos de estadísticas (se cargan desde el controlador)
        self.estadisticas: Optional[Dict[str, Any]] = None

        # Historial de auditoría de estados
        self.historial_estados: list = []

        logger.info(f"Cliente creado: {self.nombre_completo()} (Estado: {self.estado})")

    # ============================================================
    # REPRESENTACIÓN Y COMPARACIÓN
    # ============================================================

    def __str__(self) -> str:
        return (
            f"Cliente(id={self.id_cliente}, {self.nombre_completo()}, "
            f"Tel: {self.telefono}, Estado: {self.estado})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: AnyType) -> bool:
        if not isinstance(other, Cliente):
            return False
        return self.id_cliente == other.id_cliente

    def __hash__(self) -> int:
        return hash(self.id_cliente) if self.id_cliente else hash(id(self))

    def __lt__(self, other: "Cliente") -> bool:
        if not isinstance(other, Cliente):
            return NotImplemented
        return self.nombre_completo().lower() < other.nombre_completo().lower()

    def __le__(self, other: "Cliente") -> bool:
        return self == other or self < other

    def __gt__(self, other: "Cliente") -> bool:
        return not self <= other

    def __ge__(self, other: "Cliente") -> bool:
        return not self < other

    # ============================================================
    # CONVERSIÓN A DICCIONARIO
    # ============================================================

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id_cliente": self.id_cliente,
            "nombre": self.nombre,
            "apellido_paterno": self.apellido_paterno,
            "telefono": self.telefono,
            "estado": self.estado,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
        }

        if self.estadisticas:
            data["estadisticas"] = self.estadisticas

        return data

    # ============================================================
    # MÉTODOS DE INFORMACIÓN BÁSICA
    # ============================================================

    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido_paterno}".strip()

    def telefono_formateado(self) -> str:
        tel_limpio: str = (
            self.telefono.replace("-", "")
            .replace(" ", "")
            .replace("(", "")
            .replace(")", "")
            .replace("+", "")
        )
        if len(tel_limpio) == 10 and tel_limpio.isdigit():
            return f"({tel_limpio[:3]}) {tel_limpio[3:6]}-{tel_limpio[6:]}"
        return self.telefono

    def dias_desde_registro(self) -> int:
        if not self.fecha_registro:
            return 0
        delta = datetime.now() - self.fecha_registro
        return delta.days

    # ============================================================
    # MÉTODOS DE ESTADÍSTICAS
    # ============================================================

    def cargar_estadisticas(self, estadisticas: Dict[str, Any]) -> None:
        self.estadisticas = estadisticas
        logger.info(f"Estadísticas cargadas para {self.nombre_completo()}")

    def tiene_historial(self) -> bool:
        if not self.estadisticas:
            return False
        total_ventas: int = self.estadisticas.get("total_ventas", 0)
        total_rentas: int = self.estadisticas.get("total_rentas", 0)
        return total_ventas > 0 or total_rentas > 0

    def tiene_rentas_activas(self) -> bool:
        if not self.estadisticas:
            return False
        return self.estadisticas.get("rentas_activas", 0) > 0

    def tiene_rentas_vencidas(self) -> bool:
        if not self.estadisticas:
            return False
        return self.estadisticas.get("rentas_vencidas", 0) > 0

    def tiene_adeudo(self) -> bool:
        if not self.estadisticas:
            return False
        adeudo: float = self.estadisticas.get("adeudo_pendiente", 0.0)
        return adeudo > 0

    def es_cliente_nuevo(self) -> bool:
        return not self.tiene_historial()

    def es_cliente_frecuente(self, minimo_transacciones: int = 5) -> bool:
        if not self.estadisticas:
            return False
        total_transacciones: int = (
            self.estadisticas.get("total_ventas", 0)
            + self.estadisticas.get("total_rentas", 0)
        )
        return total_transacciones >= minimo_transacciones

    def es_cliente_moroso(self, limite_deuda: float = 500.0) -> bool:
        if not self.estadisticas:
            return False
        adeudo: float = self.estadisticas.get("adeudo_pendiente", 0.0)
        return adeudo >= limite_deuda

    def puede_rentar(self) -> bool:
        return not (self.tiene_rentas_vencidas() or self.tiene_adeudo())

    def puede_comprar(self) -> bool:
        return not self.es_cliente_moroso()

    def obtener_total_gastado(self) -> float:
        if not self.estadisticas:
            return 0.0
        return float(self.estadisticas.get("total_gastado", 0.0))

    def obtener_adeudo_total(self) -> float:
        if not self.estadisticas:
            return 0.0
        return float(self.estadisticas.get("adeudo_pendiente", 0.0))

    def obtener_rentas_activas(self) -> int:
        if not self.estadisticas:
            return 0
        return int(self.estadisticas.get("rentas_activas", 0))

    def obtener_rentas_vencidas(self) -> int:
        if not self.estadisticas:
            return 0
        return int(self.estadisticas.get("rentas_vencidas", 0))

    # ============================================================
    # MÉTODOS DE REPORTE
    # ============================================================

    def resumen_estadisticas(self) -> str:
        if not self.estadisticas:
            return f"📋 Cliente: {self.nombre_completo()}\n⚠️ Sin estadísticas cargadas"

        lineas: list = [
            f"📋 ESTADÍSTICAS DE {self.nombre_completo().upper()}",
            f"├─ 📱 Teléfono: {self.telefono_formateado()}",
            f"├─ 📅 Registrado hace: {self.dias_desde_registro()} días",
            f"├─ 💰 Total gastado: ${self.obtener_total_gastado():.2f}",
            f"├─ 🛒 Ventas realizadas: {self.estadisticas.get('total_ventas', 0)}",
            f"├─ 🎭 Rentas realizadas: {self.estadisticas.get('total_rentas', 0)}",
            f"├─ 📦 Rentas activas: {self.obtener_rentas_activas()}",
            f"├─ ⚠️  Rentas vencidas: {self.obtener_rentas_vencidas()}",
            f"├─ 💳 Adeudo pendiente: ${self.obtener_adeudo_total():.2f}",
            f"├─ 🕒 Última visita: {self.estadisticas.get('ultima_visita', 'N/A')}",
            f"└─ 🏆 Estado: {'🟢 Activo' if self.puede_rentar() else '🔴 Con restricciones'}",
        ]

        return "\n".join(lineas)

    def resumen_estado(self) -> str:
        if not self.estadisticas:
            return f"{self.nombre_completo()} - Sin información"

        estado_texto: str = "🟢 OK"

        if self.tiene_rentas_vencidas():
            estado_texto = "🟠 ⚠️ Rentas vencidas"
        elif self.tiene_adeudo():
            estado_texto = "🔴 💳 Con adeudo"
        elif self.tiene_rentas_activas():
            estado_texto = "🟡 📦 Rentas activas"

        return f"{self.nombre_completo()} - {estado_texto}"

    # ============================================================
    # MÉTODOS DE AUDITORÍA
    # ============================================================

    def cambiar_estado(self, nuevo_estado: str, usuario: Optional[str] = None, motivo: Optional[str] = None) -> bool:
        """
        Cambia el estado del cliente y registra el cambio en el historial.

        Args:
            nuevo_estado: Nuevo estado del cliente
            usuario: Usuario que realiza el cambio (opcional)
            motivo: Motivo del cambio (opcional)

        Returns:
            bool: True si se cambió, False si no
        """
        if self.estado == nuevo_estado:
            logger.info(f"Estado no cambiado: {self.nombre_completo()} ya está en estado '{nuevo_estado}'")
            return False

        antiguo_estado = self.estado
        self.estado = nuevo_estado

        # Registrar en historial
        registro = {
            'fecha': datetime.now(),
            'antiguo_estado': antiguo_estado,
            'nuevo_estado': nuevo_estado,
            'usuario': usuario,
            'motivo': motivo
        }
        self.historial_estados.append(registro)

        logger.info(f"Estado cambiado para {self.nombre_completo()}: '{antiguo_estado}' → '{nuevo_estado}' (por {usuario or 'sistema'}, motivo: {motivo or 'sin especificar'})")
        return True

    def obtener_historial_estados(self) -> list:
        """
        Obtiene el historial de cambios de estado del cliente.

        Returns:
            list: Lista de diccionarios con cambios de estado
        """
        return self.historial_estados

    def ultimo_cambio_estado(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el último cambio de estado del cliente.

        Returns:
            dict o None: Último registro de cambio de estado
        """
        if self.historial_estados:
            return self.historial_estados[-1]
        return None

    # ============================================================
    # CREACIÓN DESDE BD - CORREGIDA
    # ============================================================

    @staticmethod
    def from_db_row(row: tuple) -> "Cliente":
        """
        Crea un objeto Cliente desde una fila de la base de datos.

        ORDEN CORRECTO DE COLUMNAS EN BD (DESCRIBE CLIENTES):
            0. Id_cliente
            1. Nombre
            2. Apellido_Paterno
            3. Telefono
            4. Fecha_Registro      ← datetime
            5. Estado              ← string enum

        Args:
            row: Tupla con datos del cliente desde BD

        Returns:
            Cliente: Objeto Cliente creado
        """
        try:
            cliente = Cliente(
                id_cliente=int(row[0]),
                nombre=str(row[1]),
                apellido_paterno=str(row[2]),
                telefono=str(row[3]),
                fecha_registro=row[4]
                if isinstance(row[4], datetime)
                else datetime.fromisoformat(str(row[4])),
                estado=str(row[5]) if row[5] else "Activo"
            )
            logger.debug(f"Cliente creado desde BD: {cliente.nombre_completo()}")
            return cliente
        except (IndexError, TypeError, ValueError) as e:
            logger.error(f"Error al crear Cliente desde BD: {e}")
            logger.error(f"   Row recibida: {row}")
            logger.error(f"   Tipos: {[type(x).__name__ for x in row]}")
            raise

    # ============================================================
    # MÉTODO PARA DEBUGGING
    # ============================================================

    def debug_info(self) -> str:
        info_lines: list = [
            "🔧 DEBUG INFO - Cliente",
            f"├─ ID: {self.id_cliente} (tipo: {type(self.id_cliente).__name__})",
            f"├─ Nombre: '{self.nombre}' (tipo: {type(self.nombre).__name__})",
            f"├─ Apellido: '{self.apellido_paterno}' (tipo: {type(self.apellido_paterno).__name__})",
            f"├─ Teléfono: '{self.telefono}' (tipo: {type(self.telefono).__name__})",
            f"├─ Estado: '{self.estado}' (tipo: {type(self.estado).__name__})",
            f"├─ Fecha Registro: {self.fecha_registro} (tipo: {type(self.fecha_registro).__name__})",
            f"├─ Hash: {hash(self)}",
            f"├─ Estadísticas: {'Cargadas' if self.estadisticas else 'No cargadas'}",
            f"├─ Historial Estados: {len(self.historial_estados)} cambios registrados",
            f"└─ Último Cambio Estado: {self.ultimo_cambio_estado() or 'Ninguno'}",
        ]
        return "\n".join(info_lines)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("EJEMPLO DE USO - Clase Cliente v2.3")
    print("CON LOGGING Y MÉTODOS DE AUDITORÍA")
    print("=" * 70 + "\n")

    cliente = Cliente(
        nombre="Juan",
        apellido_paterno="Pérez",
        telefono="618-123-4567",
        estado="Activo",
    )

    print(cliente)
    print(cliente.debug_info())

    # Ejemplo de cambio de estado con auditoría
    print("\n--- CAMBIO DE ESTADO ---")
    cliente.cambiar_estado("Bloqueado", usuario="admin123", motivo="Adeudo pendiente")

    print("\nHistorial de estados:")
    for hist in cliente.obtener_historial_estados():
        print(f"  - {hist}")

    print("=" * 70 + "\n")