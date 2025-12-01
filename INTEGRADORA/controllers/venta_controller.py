"""
Módulo: venta_controller.py
Ubicación: controllers/venta_controller.py
Descripción: Controlador de operaciones de ventas
Sistema: MaskNGO - Renta y Venta de Disfraces
Versión: 2.6 - Con logging mejorado, validación de precios no negativos, auditoría de cancelación
"""

import logging
import uuid
from datetime import datetime, date
from typing import Dict, Tuple, List, Optional, Any
from decimal import Decimal
import mysql.connector

from models.venta import Venta
from config.database import ConexionDB
from controllers.inventario_controller import InventarioController
from controllers.auth_controller import AuthController
from utils.logger_config import setup_logger


# Configurar logging
logger = setup_logger('venta_controller', 'logs/ventas.log')


class VentaController:
    """Controlador para gestionar operaciones de ventas"""

    def __init__(self):
        """Inicializa el controlador con sus dependencias"""
        self.db = ConexionDB()
        self.inventario_ctrl = InventarioController()
        self.auth_ctrl = AuthController()

    # ==================== OPERACIONES BÁSICAS ====================

    def generar_folio(self) -> str:
        """
        Genera un folio único para la venta con formato VEN-HHMMSS-XXXX
        Ajustado para caber en VARCHAR(20) de la BD

        Returns:
            str: Folio único generado (máximo 20 caracteres)

        Ejemplo:
            >>> folio = controller.generar_folio()
            >>> print(folio)
            VEN-181012-69a3
        """
        try:
            self.db.conectar()

            ahora = datetime.now()
            # Usar solo HHMMSS (6 caracteres) en lugar de YYYYMMDD-HHMMSS
            timestamp = ahora.strftime("%H%M%S")

            # Generar UUID ULTRA CORTO (4 caracteres) 
            uuid_corto = str(uuid.uuid4()).replace("-", "")[:4]

            folio = f"VEN-{timestamp}-{uuid_corto}"

            logger.info(f"Folio generado: {folio}")
            return folio

        except Exception as e:
            logger.error(f"Error al generar folio: {e}")
            return ""

    def registrar_venta(
        self,
        id_cliente: int,
        id_usuario: int,
        detalles: List[Dict[str, Any]],
        metodo_pago: str,
        descuento_porcentaje: float = 0,
        motivo_descuento: Optional[str] = None,
        motivo_venta: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Registra una nueva venta con sus detalles y validaciones

        Args:
            id_cliente: ID del cliente que compra
            id_usuario: ID del usuario que registra la venta
            detalles: Lista de dicts {'codigo_barras': str, 'cantidad': int}
            metodo_pago: Método de pago (Efectivo, tarjeta, Transferencia)
            descuento_porcentaje: Porcentaje de descuento (0-100)
            motivo_descuento: Justificación del descuento (requerida si hay descuento)
            motivo_venta: Evento especial (Halloween, Cumpleaños, etc)

        Returns:
            Tuple[bool, str, Optional[int]]: (éxito, mensaje, id_venta)

        Validaciones:
            - Descuento requiere justificación
            - Detalles no puede estar vacío
            - Stock suficiente para todos los artículos
            - Método de pago válido
        """
        try:
            # ============ VALIDACIONES PREVIAS ============

            if descuento_porcentaje > 0 and not motivo_descuento:
                msg = "Descuento requiere justificación en 'motivo_descuento'"
                logger.warning(f"Intento de registrar venta con descuento sin justificación: {msg}")
                return (False, msg, None)

            if not detalles:
                msg = "La venta debe contener al menos un artículo"
                logger.warning(f"Intento de registrar venta sin detalles: {msg}")
                return (False, msg, None)

            # ============ PROCESAR DETALLES ============

            detalles_procesados = []
            total_venta = Decimal('0')

            for detalle in detalles:
                codigo = detalle.get('codigo_barras')
                cantidad = detalle.get('cantidad', 0)

                if not codigo or cantidad <= 0:
                    msg = f"Código o cantidad inválidos: {detalle}"
                    logger.warning(f"Intento de registrar venta con detalle inválido: {msg}")
                    return (False, msg, None)

                # Buscar disfraz en inventario
                disfraz = self.inventario_ctrl.buscar_por_codigo(codigo)
                if not disfraz:
                    msg = f"Disfraz no encontrado: {codigo}"
                    logger.warning(f"Intento de registrar venta con disfraz inexistente: {msg}")
                    return (False, msg, None)

                # Verificar stock disponible
                if disfraz.disponible < cantidad:
                    msg = (f"Stock insuficiente para {codigo}. "
                           f"Disponible: {disfraz.disponible}, Solicitado: {cantidad}")
                    logger.warning(f"Intento de registrar venta con stock insuficiente: {msg}")
                    return (False, msg, None)

                precio = Decimal(str(disfraz.precio_venta))
                
                # Validación de precios no negativos
                if precio < 0:
                    msg = f"Precio de venta no puede ser negativo para {codigo}: {precio}"
                    logger.warning(f"Intento de registrar venta con precio negativo: {msg}")
                    return (False, msg, None)

                subtotal = Decimal(cantidad) * precio
                total_venta += subtotal

                detalles_procesados.append({
                    'codigo_barras': codigo,
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'subtotal': subtotal,
                    'disfraz_obj': disfraz
                })

            # ============ CALCULAR TOTALES ============

            descuento_monto = Decimal('0')
            if descuento_porcentaje > 0:
                descuento_monto = total_venta * Decimal(str(descuento_porcentaje)) / Decimal('100')

            total_final = total_venta - descuento_monto

            # ============ INSERTAR EN BD ============

            self.db.conectar()

            # Generar folio
            folio = self.generar_folio()
            if not folio:
                msg = "Error al generar folio"
                logger.error(f"Error al registrar venta: {msg}")
                return (False, msg, None)

            # Insertar venta
            ahora = datetime.now()
            resultado = self.db.ejecutar_insert(
                """INSERT INTO VENTAS 
                   (Folio, Id_cliente, Usuario_id, Fecha_venta, metodo_pago, 
                    Total, Descuento_Porcentaje, Descuento_Monto, 
                    Motivo_Descuento, Motivo_Venta, Estado)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (folio, id_cliente, id_usuario, ahora, metodo_pago,
                 float(total_venta), float(descuento_porcentaje), float(descuento_monto),
                 motivo_descuento or '', motivo_venta or '', 'Activa')
            )

            id_venta = resultado
            if not id_venta:
                msg = "Error al insertar venta en BD"
                logger.error(f"Error al registrar venta: {msg}")
                return (False, msg, None)

            # ============ INSERTAR DETALLES ============

            for detalle_proc in detalles_procesados:
                try:
                    self.db.ejecutar_insert(
                        """INSERT INTO DETALLE_VENTAS
                           (Id_Venta, Codigo_Barras, Cantidad, Precio_Unitario, Subtotal)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (id_venta, detalle_proc['codigo_barras'],
                         detalle_proc['cantidad'],
                         float(detalle_proc['precio_unitario']),
                         float(detalle_proc['subtotal']))
                    )

                    # Actualizar stock del disfraz
                    self.inventario_ctrl.descontar_stock(
                        detalle_proc['codigo_barras'],
                        detalle_proc['cantidad']
                    )

                except mysql.connector.Error as e:
                    logger.error(f"Error de base de datos al insertar detalle: {e}")
                    # Rollback: eliminar la venta
                    self.db.ejecutar_update("DELETE FROM VENTAS WHERE Id_Venta = %s", (id_venta,))
                    msg = f"Error de base de datos al procesar detalle: {str(e)}"
                    return (False, msg, None)
                except Exception as e:
                    logger.error(f"Error inesperado al insertar detalle: {e}")
                    # Rollback: eliminar la venta
                    self.db.ejecutar_update("DELETE FROM VENTAS WHERE Id_Venta = %s", (id_venta,))
                    msg = f"Error al procesar detalle: {str(e)}"
                    return (False, msg, None)

            msg = f"Venta registrada exitosamente. Folio: {folio}"
            logger.info(f"{msg} (ID: {id_venta})")
            return (True, msg, id_venta)

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al registrar venta: {e}")
            return (False, f"Error de base de datos: {str(e)}", None)
        except Exception as e:
            logger.error(f"Error inesperado al registrar venta: {e}")
            return (False, f"Error al registrar venta: {str(e)}", None)

    # ==================== BÚSQUEDA Y RECUPERACIÓN ====================

    def obtener_venta_completa(self, id_venta: int) -> Optional[Venta]:
        """
        Obtiene una venta completa con todos sus detalles

        Args:
            id_venta: ID de la venta a recuperar

        Returns:
            Venta: Objeto Venta con detalles, o None si no existe
        """
        try:
            self.db.conectar()

            # Obtener venta
            resultado = self.db.ejecutar_query(
                """SELECT * FROM VENTAS WHERE Id_Venta = %s""",
                (id_venta,)
            )

            if not resultado:
                logger.info(f"Venta no encontrada: {id_venta}")
                return None

            fila_venta = resultado[0]

            # Obtener detalles
            detalles_resultado = self.db.ejecutar_query(
                """SELECT * FROM DETALLE_VENTAS WHERE Id_Venta = %s""",
                (id_venta,)
            )

            # Construir objeto Venta - CORREGIDO: Índices correctos según DESCRIBE VENTAS
            # [0]  Id_Venta, [1]  Folio, [2]  Id_cliente, [3]  Usuario_id, [4]  fecha_venta
            # [5]  Total, [6]  Descuento_Porcentaje, [7]  Descuento_Monto, [8]  Motivo_Descuento
            # [9]  Motivo_Venta, [10] Notas, [11] Estado, [12] Cancelada_Por
            # [13] Fecha_Cancelacion, [14] Motivo_Cancelacion, [15] metodo_pago

            venta = Venta(
                id_venta=fila_venta[0],
                folio=fila_venta[1],
                id_cliente=fila_venta[2],
                usuario_id=fila_venta[3],
                fecha_venta=fila_venta[4],
                metodo_pago=fila_venta[15],  # ← CORREGIDO: índice 15, no 5
                total=Decimal(str(fila_venta[5])),
                descuento_porcentaje=Decimal(str(fila_venta[6] or 0)),
                descuento_monto=Decimal(str(fila_venta[7] or 0)),
                motivo_descuento=fila_venta[8],
                motivo_venta=fila_venta[9],
                estado=fila_venta[11],
                cancelada_por=fila_venta[12] if len(fila_venta) > 12 else None,
                fecha_cancelacion=fila_venta[13] if len(fila_venta) > 13 else None
            )

            # Agregar detalles - DetalleVenta está en models/venta.py
            from models.venta import DetalleVenta

            for fila_detalle in detalles_resultado:
                detalle = DetalleVenta(
                    codigo_barras=fila_detalle[2],
                    cantidad=fila_detalle[3],
                    precio_unitario=Decimal(str(fila_detalle[4])),
                    id_detalle_venta=fila_detalle[0],
                    id_venta=fila_detalle[1],
                    subtotal=Decimal(str(fila_detalle[5]))
                )
                venta.agregar_detalle(detalle)

            logger.debug(f"Venta obtenida por ID {id_venta}: Folio={venta.folio}, Total={venta.total}")
            return venta

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al obtener venta completa: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener venta completa: {e}")
            return None

    def buscar_ventas_cliente(self, id_cliente: int) -> List[Venta]:
        """
        Busca todas las ventas de un cliente

        Args:
            id_cliente: ID del cliente

        Returns:
            List[Venta]: Lista de ventas del cliente
        """
        try:
            self.db.conectar()

            resultado = self.db.ejecutar_query(
                """SELECT Id_Venta FROM VENTAS WHERE Id_cliente = %s 
                   ORDER BY Fecha_venta DESC""",
                (id_cliente,)
            )

            ventas = []
            for fila in resultado:
                venta = self.obtener_venta_completa(fila[0])
                if venta:
                    ventas.append(venta)

            logger.info(f"Se encontraron {len(ventas)} ventas para cliente {id_cliente}")
            return ventas

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al buscar ventas del cliente: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado al buscar ventas del cliente: {e}")
            return []

    def buscar_por_folio(self, folio: str) -> Optional[Venta]:
        """
        Busca una venta por su folio único

        Args:
            folio: Folio de la venta

        Returns:
            Venta o None
        """
        try:
            self.db.conectar()

            resultado = self.db.ejecutar_query(
                """SELECT Id_Venta FROM VENTAS WHERE Folio = %s""",
                (folio,)
            )

            if resultado:
                venta = self.obtener_venta_completa(resultado[0][0])
                if venta:
                    logger.debug(f"Venta encontrada por folio {folio}: ID={venta.id_venta}")
                    return venta

            logger.info(f"Folio no encontrado: {folio}")
            return None

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al buscar venta por folio: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al buscar venta por folio: {e}")
            return None

    # ==================== ESTADÍSTICAS ====================

    def total_ventas_dia(self, fecha: Optional[date] = None) -> float:
        """
        Calcula el total de ventas finales de un día (descontados aplicados)

        Args:
            fecha: Fecha para consultar (default: hoy)

        Returns:
            float: Total en pesos
        """
        try:
            if not fecha:
                fecha = date.today()

            self.db.conectar()

            # Total final = Total - Descuento_Monto
            resultado = self.db.ejecutar_query(
                """SELECT COALESCE(SUM(Total - COALESCE(Descuento_Monto, 0)), 0) as total 
                   FROM VENTAS 
                   WHERE DATE(Fecha_venta) = %s AND Estado = 'Activa'""",
                (fecha,)
            )

            if resultado:
                total = float(resultado[0][0])
                logger.debug(f"Total de ventas del día {fecha}: {total}")
                return total

            logger.debug(f"Total de ventas del día {fecha}: 0.0")
            return 0.0

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al calcular total del día: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"Error inesperado al calcular total del día: {e}")
            return 0.0

    def contar_ventas(self, fecha: Optional[date] = None) -> int:
        """
        Cuenta la cantidad de ventas de un día

        Args:
            fecha: Fecha para consultar (default: hoy)

        Returns:
            int: Cantidad de ventas
        """
        try:
            if not fecha:
                fecha = date.today()

            self.db.conectar()

            resultado = self.db.ejecutar_query(
                """SELECT COUNT(*) as cantidad 
                   FROM VENTAS 
                   WHERE DATE(Fecha_venta) = %s AND Estado = 'Activa'""",
                (fecha,)
            )

            if resultado:
                cantidad = int(resultado[0][0])
                logger.debug(f"Cantidad de ventas del día {fecha}: {cantidad}")
                return cantidad

            logger.debug(f"Cantidad de ventas del día {fecha}: 0")
            return 0

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al contar ventas: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error inesperado al contar ventas: {e}")
            return 0

    def obtener_estadisticas(self, fecha: Optional[date] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas completas de ventas del día

        Args:
            fecha: Fecha para consultar (default: hoy)

        Returns:
            Dict con: cantidad_ventas, total_bruto, total_descuentos, 
                      total_final, clientes_unicos, ticket_promedio
        """
        if not fecha:
            fecha = date.today()

        try:
            self.db.conectar()

            resultado = self.db.ejecutar_query(
                """SELECT 
                   COUNT(*) as cantidad_ventas,
                   COALESCE(SUM(Total), 0) as total_bruto,
                   COALESCE(SUM(Descuento_Monto), 0) as total_descuentos,
                   COALESCE(SUM(Total - COALESCE(Descuento_Monto, 0)), 0) as total_final,
                   COUNT(DISTINCT Id_cliente) as clientes_unicos
                   FROM VENTAS 
                   WHERE DATE(Fecha_venta) = %s AND Estado = 'Activa'""",
                (fecha,)
            )

            if resultado:
                fila = resultado[0]
                cantidad = int(fila[0] or 0)
                total_final = float(fila[3] or 0)

                stats = {
                    'fecha': str(fecha),
                    'cantidad_ventas': cantidad,
                    'total_bruto': float(fila[1] or 0),
                    'total_descuentos': float(fila[2] or 0),
                    'total_final': total_final,
                    'clientes_unicos': int(fila[4] or 0),
                    'ticket_promedio': total_final / cantidad if cantidad > 0 else 0.0
                }

                logger.info(f"Estadísticas de ventas del día {fecha}: {stats}")
                return stats

            stats = {
                'fecha': str(fecha),
                'cantidad_ventas': 0,
                'total_bruto': 0.0,
                'total_descuentos': 0.0,
                'total_final': 0.0,
                'clientes_unicos': 0,
                'ticket_promedio': 0.0
            }
            logger.info(f"Estadísticas de ventas del día {fecha}: {stats}")
            return stats

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al obtener estadísticas: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error inesperado al obtener estadísticas: {e}")
            return {}

    # ==================== MODIFICACIÓN Y CANCELACIÓN ====================

    def cancelar_venta(
        self,
        id_venta: int,
        id_usuario_admin: int,
        motivo_cancelacion: str
    ) -> Tuple[bool, str]:
        """
        Cancela una venta activa (solo administrador)

        Args:
            id_venta: ID de la venta a cancelar
            id_usuario_admin: ID del usuario admin que autoriza
            motivo_cancelacion: Razón de la cancelación

        Returns:
            Tuple[bool, str]: (éxito, mensaje)

        Validaciones:
            - Solo admin puede cancelar
            - La venta debe estar activa
            - Se devuelve el stock automáticamente
        """
        try:
            # Validar que sea admin
            usuario = self.auth_ctrl.obtener_usuario_por_id(id_usuario_admin)
            if not usuario or usuario.rol != 'admin':
                logger.warning(f"Intento de cancelación no autorizado por usuario {id_usuario_admin} (no admin)")
                return (False, "Solo administradores pueden cancelar ventas")

            self.db.conectar()

            # Obtener venta
            venta = self.obtener_venta_completa(id_venta)
            if not venta:
                logger.warning(f"Intento de cancelar venta inexistente: ID {id_venta}")
                return (False, f"Venta no encontrada: {id_venta}")

            if venta.estado != 'Activa':
                logger.warning(f"Intento de cancelar venta en estado '{venta.estado}': ID {id_venta}")
                return (False, f"No se puede cancelar una venta {venta.estado}")

            # Devolver stock de cada detalle usando aumentar_stock
            for detalle in venta.detalles:
                exito, msg_stock = self.inventario_ctrl.aumentar_stock(
                    detalle.codigo_barras,
                    detalle.cantidad
                )
                if not exito:
                    logger.warning(f"Problema al devolver stock al cancelar venta {id_venta}: {msg_stock}")

            # Actualizar estado de venta
            ahora = datetime.now()
            self.db.ejecutar_update(
                """UPDATE VENTAS 
                   SET Estado = 'Cancelada', 
                       Fecha_Cancelacion = %s,
                       Cancelada_Por = %s,
                       Motivo_Cancelacion = %s
                   WHERE Id_Venta = %s""",
                (ahora, id_usuario_admin, motivo_cancelacion, id_venta)
            )

            msg = f"Venta {venta.folio} cancelada exitosamente"
            logger.info(f"{msg} (cancelada por usuario {id_usuario_admin})")
            return (True, msg)

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al cancelar venta: {e}")
            return (False, f"Error de base de datos: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado al cancelar venta: {e}")
            return (False, f"Error al cancelar venta: {str(e)}")

    # ==================== MÉTODOS AUXILIARES ====================

    def obtener_resumen_ventas(self, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen de las últimas ventas

        Args:
            limite: Cantidad máxima de ventas a retornar

        Returns:
            List[Dict]: Lista de resúmenes de ventas
        """
        try:
            self.db.conectar()

            resultado = self.db.ejecutar_query(
                """SELECT 
                   v.Id_Venta, v.Folio, v.Fecha_venta, 
                   v.Total, v.Descuento_Monto, v.Estado, 
                   c.Nombre, c.Apellido_Paterno
                   FROM VENTAS v
                   JOIN CLIENTES c ON v.Id_cliente = c.Id_cliente
                   ORDER BY v.Fecha_venta DESC
                   LIMIT %s""",
                (limite,)
            )

            resumen = []
            for fila in resultado:
                total_final = fila[3] - (fila[4] or 0)
                resumen.append({
                    'id_venta': fila[0],
                    'folio': fila[1],
                    'fecha': str(fila[2]),
                    'cliente': f"{fila[6]} {fila[7]}",
                    'total_bruto': float(fila[3]),
                    'descuento': float(fila[4] or 0),
                    'total_final': float(total_final),
                    'estado': fila[5]
                })

            logger.info(f"Obtenido resumen de últimas {len(resumen)} ventas")
            return resumen

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al obtener resumen de ventas: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado al obtener resumen de ventas: {e}")
            return []


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRUEBA - VentaController v2.6")
    print("CON LOGGING MEJORADO Y VALIDACIÓN DE PRECIOS NO NEGATIVOS")
    print("="*60 + "\n")
    
    vc = VentaController()
    
    print("1️⃣ Generando folio de prueba...")
    folio = vc.generar_folio()
    print(f"   Folio generado: {folio}\n")
    
    print("2️⃣ Obteniendo estadísticas del día...")
    stats = vc.obtener_estadisticas()
    print(f"   Estadísticas: {stats}\n")
    
    print("="*60 + "\n")