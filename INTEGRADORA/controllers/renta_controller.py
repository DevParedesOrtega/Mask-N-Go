"""
Módulo: renta_controller.py
Ubicación: controllers/renta_controller.py
Descripción: Controlador para gestión de rentas
Sistema: MaskNGO - Renta y Venta de Disfraces
Versión: 3.1 - Con logging, validaciones de precios no negativos, auditoría de devolución
"""

import sys
import os
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import mysql.connector

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
from models.renta import Renta
from controllers.inventario_controller import InventarioController
from controllers.cliente_controller import ClienteController
from utils.logger_config import setup_logger


# Configurar logging
logger = setup_logger('renta_controller', 'logs/rentas.log')


class RentaController:
    """
    Controlador para gestión de rentas de disfraces.

    Características:
    - Registrar rentas con detalles y depósito opcional.
    - Usa InventarioController para verificar y mover Disponible (no Stock).
    - Calcula total como suma de subtotales (cantidad × precio_renta × días).
    - Calcula depósito por defecto como precio_venta × cantidad (puede ser 0).
    - Lee y actualiza penalización diaria desde tabla CONFIGURACION.
    - Soporta devolución, cálculo de penalización y marcado automático de vencidas.
    - Incluye métodos exactos para test_rentas.py.
    """

    def __init__(self):
        self.db = ConexionDB()
        self.inv_controller = InventarioController()
        self.cliente_controller = ClienteController()
        self.penalizacion_dia: float = 50.0  # valor por defecto
        self._cargar_penalizacion_config()

    # ============================================================
    # CONFIGURACIÓN (PENALIZACIÓN POR DÍA)
    # ============================================================

    def _cargar_penalizacion_config(self) -> None:
        """Carga penalización por día desde tabla CONFIGURACION."""
        try:
            self.db.conectar()
            q = """
                SELECT Valor_Config
                FROM CONFIGURACION
                WHERE Nombre_Config = 'PENALIZACIONDIA'
                LIMIT 1
            """
            r = self.db.ejecutar_query(q)
            if r and r[0][0] is not None:
                self.penalizacion_dia = float(r[0][0])
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos al cargar penalización desde configuración: {e}")
        except Exception as e:
            logger.error(f"Error inesperado al cargar penalización desde configuración: {e}")

    def actualizar_penalizacion_dia(self, monto: float) -> Tuple[bool, str]:
        """
        Actualiza el valor de penalización por día en CONFIGURACION
        y en el atributo penalizacion_dia.
        """
        try:
            monto = float(monto)
            if monto < 0:
                logger.warning(f"Intento de actualizar penalización a valor negativo: {monto}")
                return False, "La penalización por día no puede ser negativa"

            self.db.conectar()
            # Verificar si ya existe el registro
            q_exist = """
                SELECT Id_Config FROM CONFIGURACION
                WHERE Nombre_Config = 'PENALIZACIONDIA'
                LIMIT 1
            """
            r = self.db.ejecutar_query(q_exist)

            if r:
                q_upd = """
                    UPDATE CONFIGURACION
                    SET Valor_Config = %s, Fecha_Modificacion = CURRENT_TIMESTAMP
                    WHERE Id_Config = %s
                """
                self.db.ejecutar_update(q_upd, (str(monto), r[0][0]))
            else:
                q_ins = """
                    INSERT INTO CONFIGURACION (Nombre_Config, Valor_Config, Descripcion)
                    VALUES ('PENALIZACIONDIA', %s, 'Monto de penalización por día de retraso en rentas')
                """
                self.db.ejecutar_insert(q_ins, (str(monto),))

            self.penalizacion_dia = monto
            logger.info(f"Penalización por día actualizada a ${monto:.2f}")
            return True, f"Penalización por día actualizada a ${monto:.2f}"
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en actualizar_penalizacion_dia: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en actualizar_penalizacion_dia: {e}")
            return False, f"Error inesperado: {str(e)}"

    # ============================================================
    # VALIDACIONES
    # ============================================================

    def _validar_datos_renta_basicos(
        self,
        id_cliente: int,
        id_usuario: int,
        detalles: List[Dict[str, Any]],
        dias_renta: int
    ) -> Tuple[bool, str]:
        """Valida cliente, usuario, detalles y días."""
        # Cliente
        cliente = self.cliente_controller.buscar_por_id(id_cliente)
        if not cliente:
            logger.warning(f"Intento de registrar renta con cliente inexistente: ID {id_cliente}")
            return False, f"Cliente con ID {id_cliente} no encontrado"

        # Usuario
        try:
            self.db.conectar()
            q = "SELECT COUNT(*) FROM USUARIOS WHERE Id_Usuario = %s"
            r = self.db.ejecutar_query(q, (id_usuario,))
            if not r or r[0][0] == 0:
                logger.warning(f"Intento de registrar renta con usuario inexistente: ID {id_usuario}")
                return False, f"Usuario con ID {id_usuario} no encontrado"
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos validando usuario en _validar_datos_renta_basicos: {e}")
            return False, "Error al validar usuario"
        except Exception as e:
            logger.error(f"Error inesperado validando usuario en _validar_datos_renta_basicos: {e}")
            return False, "Error al validar usuario"

        # Detalles
        if not detalles or len(detalles) == 0:
            logger.warning("Intento de registrar renta sin detalles")
            return False, "La renta debe tener al menos un disfraz"

        # Días
        if not isinstance(dias_renta, int) or dias_renta <= 0:
            logger.warning(f"Intento de registrar renta con días inválidos: {dias_renta}")
            return False, "Los días de renta deben ser mayor a 0"

        return True, "OK"

    # ============================================================
    # REGISTRAR RENTA (usado por test_rentas.py)
    # ============================================================

    def registrar_renta(
        self,
        id_cliente: int,
        id_usuario: int,
        detalles: List[Dict[str, Any]],
        dias_renta: int
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Registra una renta completa con detalles.

        - Verifica cliente y usuario.
        - Verifica disponibilidad por cada detalle.
        - Calcula total y depósito.
        - Inserta en RENTAS y DETALLE_RENTAS.
        - Descuenta Disponible usando InventarioController.
        """
        # 1. Validaciones básicas
        ok, msg = self._validar_datos_renta_basicos(id_cliente, id_usuario, detalles, dias_renta)
        if not ok:
            logger.warning(f"Intento de registrar renta fallido: {msg}")
            return False, msg, None

        try:
            self.db.conectar()

            # 2. Preparar datos base
            ahora = datetime.now()

            total = Decimal('0.00')
            deposito = Decimal('0.00')

            # Primero verificar disponibilidad y calcular total y depósito
            for item in detalles:
                codigo = item['codigo_barras']
                cantidad = int(item['cantidad'])

                # Verificar disponibilidad
                hay, msg_disp, _ = self.inv_controller.verificar_disponibilidad(codigo, cantidad)
                if not hay:
                    logger.info(f"Intento de registrar renta con stock insuficiente para {codigo}: {msg_disp}")
                    return False, f"Sin stock suficiente para {codigo}: {msg_disp}", None

                # Obtener datos de inventario
                disfraz = self.inv_controller.buscar_por_codigo(codigo)
                if not disfraz:
                    logger.warning(f"Disfraz no encontrado al registrar renta: {codigo}")
                    return False, f"Disfraz no encontrado: {codigo}", None

                precio_renta = Decimal(str(disfraz.precio_renta))
                precio_venta = Decimal(str(disfraz.precio_venta))

                # Validación de precios no negativos
                if precio_renta < 0:
                    logger.warning(f"Precio de renta negativo para {codigo}: {precio_renta}")
                    return False, f"Precio de renta no puede ser negativo para {codigo}", None

                if precio_venta < 0:
                    logger.warning(f"Precio de venta negativo para {codigo}: {precio_venta}")
                    return False, f"Precio de venta no puede ser negativo para {codigo}", None

                # Subtotal de renta: cantidad × precio_renta × dias_renta
                subtotal = Decimal(cantidad) * precio_renta * Decimal(dias_renta)
                total += subtotal

                # Depósito por defecto: precio_venta × cantidad
                deposito += (precio_venta * Decimal(cantidad))

            # 3. Insertar en RENTAS
            fecha_devolucion = ahora + timedelta(days=dias_renta)

            q_renta = """
                INSERT INTO RENTAS
                (Id_Cliente, Id_Usuario, Fecha_Renta, Fecha_Devolucion,
                 Fecha_Devuelto, Penalizacion, Dias_Renta, Total, Deposito, Estado)
                VALUES (%s, %s, %s, %s, NULL, 0.00, %s, %s, %s, 'Activa')
            """
            nuevo_id = self.db.ejecutar_insert(
                q_renta,
                (
                    id_cliente,
                    id_usuario,
                    ahora,
                    fecha_devolucion,
                    dias_renta,
                    float(total),
                    float(deposito)
                )
            )

            if not nuevo_id:
                logger.error("Error al registrar la renta en la base de datos")
                return False, "Error al registrar la renta en la base de datos", None

            # 4. Insertar detalles y descontar Disponible
            for item in detalles:
                codigo = item['codigo_barras']
                cantidad = int(item['cantidad'])

                disfraz = self.inv_controller.buscar_por_codigo(codigo)
                precio_renta = Decimal(str(disfraz.precio_renta))

                subtotal = Decimal(cantidad) * precio_renta * Decimal(dias_renta)

                # Insertar detalle
                q_det = """
                    INSERT INTO DETALLE_RENTAS
                    (Id_Renta, Codigo_Barras, Cantidad, Precio_Unitario, Subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """
                self.db.ejecutar_insert(
                    q_det,
                    (
                        nuevo_id,
                        codigo,
                        cantidad,
                        float(precio_renta),
                        float(subtotal)
                    )
                )

                # Descontar disponible
                ok_desc, msg_desc = self.inv_controller.descontar_stock(codigo, cantidad)
                if not ok_desc:
                    logger.warning(f"Error al descontar stock de {codigo}: {msg_desc}")

            logger.info(f"Renta registrada correctamente (ID {nuevo_id})")
            return True, "Renta registrado correctamente", nuevo_id

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en registrar_renta: {e}")
            return False, f"Error de base de datos: {str(e)}", None
        except Exception as e:
            logger.error(f"Error inesperado en registrar_renta: {e}")
            return False, f"Error inesperado: {str(e)}", None

    # ============================================================
    # OBTENER RENTA COMPLETA (usado en prueba 2)
    # ============================================================

    def obtener_renta_completa(self, id_renta: int) -> Optional[Renta]:
        """
        Obtiene una renta por ID, con sus campos principales.
        (Las pruebas solo usan renta.deposito y renta.total)
        """
        try:
            self.db.conectar()
            q = "SELECT * FROM RENTAS WHERE Id_Renta = %s"
            r = self.db.ejecutar_query(q, (id_renta,))
            if not r:
                logger.info(f"Renta con ID {id_renta} no encontrada")
                return None
            renta = Renta.from_db_row(r[0])
            logger.debug(f"Renta encontrada por ID {id_renta}: Total={renta.total}, Deposito={renta.deposito}")
            return renta
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en obtener_renta_completa: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en obtener_renta_completa: {e}")
            return None

    # ============================================================
    # DEVOLVER RENTA (usado en pruebas 5 y 6)
    # ============================================================

    def devolver_renta(
        self,
        id_renta: int,
        id_usuario: int
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Devuelve una renta (a tiempo o con retraso).

        - Solo permite devolver rentas en estado 'Activa' o 'Vencida'.
        - Restaura Disponible para cada detalle.
        - Calcula días de retraso y penalización usando penalizacion_dia.
        - Actualiza Fecha_Devuelto, Penalizacion y Estado='Devuelto'.
        - Retorna info: dias_retraso, penalizacion, deposito_devuelto.
        """
        try:
            self.db.conectar()
            # 1. Obtener renta
            q_renta = "SELECT * FROM RENTAS WHERE Id_Renta = %s"
            r = self.db.ejecutar_query(q_renta, (id_renta,))
            if not r:
                logger.warning(f"Intento de devolver renta inexistente: ID {id_renta}")
                return False, f"Renta con ID {id_renta} no encontrada", None

            renta = Renta.from_db_row(r[0])

            if renta.estado not in ('Activa', 'Vencida'):
                logger.warning(f"No se puede devolver una renta en estado '{renta.estado}': ID {id_renta}")
                return False, f"No se puede devolver una renta en estado '{renta.estado}'", None

            ahora = datetime.now()

            # 2. Obtener detalles para restaurar stock disponible
            q_det = """
                SELECT Codigo_Barras, Cantidad
                FROM DETALLE_RENTAS
                WHERE Id_Renta = %s
            """
            dets = self.db.ejecutar_query(q_det, (id_renta,))

            if dets:
                for codigo, cant in dets:
                    ok_aum, msg_aum = self.inv_controller.aumentar_stock(codigo, int(cant))
                    if not ok_aum:
                        logger.warning(f"Error al aumentar stock de {codigo}: {msg_aum}")

            # 3. Calcular días de retraso y penalización
            dias_retraso = 0
            penalizacion = Decimal('0.00')

            if ahora > renta.fecha_devolucion:
                delta = ahora - renta.fecha_devolucion
                dias_retraso = delta.days
                if dias_retraso > 0:
                    penalizacion = Decimal(str(self.penalizacion_dia)) * Decimal(dias_retraso)

            # 4. Actualizar renta
            q_upd = """
                UPDATE RENTAS
                SET Fecha_Devuelto = %s,
                    Penalizacion = %s,
                    Estado = 'Devuelto'
                WHERE Id_Renta = %s
            """
            self.db.ejecutar_update(q_upd, (ahora, float(penalizacion), id_renta))

            info = {
                'dias_retraso': dias_retraso,
                'penalizacion': float(penalizacion),
                'deposito_devuelto': float(renta.deposito)
            }

            # Log de auditoría
            logger.info(
                f"Renta ID {id_renta} devuelta por usuario ID {id_usuario}. "
                f"Días retraso: {dias_retraso}, Penalización: {penalizacion}, "
                f"Depósito devuelto: {renta.deposito}"
            )
            return True, "Renta devuelta correctamente", info

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en devolver_renta: {e}")
            return False, f"Error de base de datos: {str(e)}", None
        except Exception as e:
            logger.error(f"Error inesperado en devolver_renta: {e}")
            return False, f"Error inesperado: {str(e)}", None

    # ============================================================
    # MARCAR RENTAS VENCIDAS (usado en prueba 7)
    # ============================================================

    def marcar_rentas_vencidas(self) -> int:
        """
        Marca como 'Vencida' las rentas 'Activa' cuya Fecha_Devolucion < ahora.
        Retorna cuántas filas se actualizaron.
        """
        try:
            self.db.conectar()
            ahora = datetime.now()
            q = """
                UPDATE RENTAS
                SET Estado = 'Vencida'
                WHERE Estado = 'Activa'
                  AND Fecha_Devolucion < %s
            """
            filas = self.db.ejecutar_update(q, (ahora,))
            if not filas:
                filas = 0
            logger.info(f"Rentas vencidas marcadas: {filas}")
            return filas
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en marcar_rentas_vencidas: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error inesperado en marcar_rentas_vencidas: {e}")
            return 0

    # ============================================================
    # LISTAR Y CONTAR RENTAS ACTIVAS (usado en pruebas 8 y 10)
    # ============================================================

    def listar_rentas_activas(self) -> List[Renta]:
        """
        Lista las rentas con Estado 'Activa' o 'Vencida'
        (las que siguen "abiertas").
        """
        try:
            self.db.conectar()
            q = """
                SELECT * FROM RENTAS
                WHERE Estado IN ('Activa', 'Vencida')
                ORDER BY Fecha_Renta DESC
            """
            r = self.db.ejecutar_query(q)
            rentas = [Renta.from_db_row(row) for row in r] if r else []
            logger.info(f"Listando rentas activas - encontradas: {len(rentas)}")
            return rentas
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en listar_rentas_activas: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en listar_rentas_activas: {e}")
            return []

    def contar_rentas_activas(self) -> int:
        """
        Cuenta las rentas 'Activa' o 'Vencida'.
        """
        try:
            self.db.conectar()
            q = """
                SELECT COUNT(*)
                FROM RENTAS
                WHERE Estado IN ('Activa', 'Vencida')
            """
            r = self.db.ejecutar_query(q)
            total = int(r[0][0]) if r else 0
            logger.info(f"Conteo de rentas activas: {total}")
            return total
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en contar_rentas_activas: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error inesperado en contar_rentas_activas: {e}")
            return 0


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRUEBA - RentaController v3.1")
    print("CON LOGGING Y VALIDACIONES DE PRECIOS NO NEGATIVOS")
    print("="*60 + "\n")
    
    rc = RentaController()
    
    print("1️⃣ Penalización por día actual:")
    print(f"   ${rc.penalizacion_dia:.2f}\n")
    
    print("2️⃣ Contando rentas activas...")
    total = rc.contar_rentas_activas()
    print(f"   Total: {total}\n")
    
    print("3️⃣ Listando rentas activas...")
    rentas = rc.listar_rentas_activas()
    print(f"   Encontradas: {len(rentas)}\n")
    
    print("="*60 + "\n")