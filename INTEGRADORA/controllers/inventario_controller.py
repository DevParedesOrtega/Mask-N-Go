"""
Módulo: inventario_controller.py
Ubicación: controllers/inventario_controller.py
Descripción: Controlador moderno para gestión de inventario
Sistema: MaskNGO - Renta y Venta de Disfraces
Versión: 2.2 - Con logging, validaciones de stock, disponibilidad y métodos extra
"""

import sys
import os
from typing import List, Tuple, Optional
import mysql.connector

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
from models.disfraz import Disfraz
from utils.validadores import Validadores
from utils.logger_config import setup_logger


# Configurar logging
logger = setup_logger('inventario_controller', 'logs/inventario.log')


class InventarioController:
    """
    Controlador para gestión de inventario de disfraces.
    
    Características:
    - Validación exhaustiva de datos
    - Control de Stock (total) y Disponible (para rentar)
    - Búsquedas insensibles a mayúsculas
    - Validación de stock en ediciones
    - Método verificar_disponibilidad() para rentas/ventas
    - Soft delete si disfraz tiene movimiento
    - Eliminación física solo si nunca se rentó/vendió
    """

    def __init__(self):
        """Inicializa el controlador con conexión a BD."""
        self.db = ConexionDB()

    # ============================================================
    # VALIDACIONES PRIVADAS
    # ============================================================

    def _validar_datos(self, codigo_barras, descripcion, talla, color, categoria,
                       precio_venta, precio_renta, stock):
        """Valida los campos básicos antes de insertar o editar."""
        # Validar código
        if not codigo_barras or len(codigo_barras.strip()) < 3:
            return False, "Código de barras requerido (mínimo 3 caracteres)"
        
        # Validar descripción
        if not descripcion or len(descripcion.strip()) < 5:
            return False, "Descripción requerida (mínimo 5 caracteres)"
        
        # Validar talla
        if not talla or talla.strip() == "":
            return False, "Talla requerida"
        
        # Validar color
        if not color or color.strip() == "":
            return False, "Color requerido"
        
        # Validar categoría
        if not categoria or categoria.strip() == "":
            return False, "Categoría requerida"
        
        # Validar precios
        try:
            precio_venta = float(precio_venta)
            precio_renta = float(precio_renta)
            stock = int(stock)
            
            if precio_venta <= 0:
                return False, "Precio de venta debe ser mayor a 0"
            if precio_renta <= 0:
                return False, "Precio de renta debe ser mayor a 0"
            if stock < 0:
                return False, "Stock no puede ser negativo"
        
        except (ValueError, TypeError):
            return False, "Precios y stock deben ser números válidos"
        
        return True, ""

    def _disfraz_tiene_movimiento(self, codigo_barras: str) -> bool:
        """
        Verifica si disfraz tiene rentas o ventas registradas.
        """
        try:
            self.db.conectar()
            
            query_rentas = "SELECT COUNT(*) FROM DETALLE_RENTAS WHERE Codigo_Barras = %s"
            resultado_rentas = self.db.ejecutar_query(query_rentas, (codigo_barras,))
            
            query_ventas = "SELECT COUNT(*) FROM DETALLE_VENTAS WHERE Codigo_Barras = %s"
            resultado_ventas = self.db.ejecutar_query(query_ventas, (codigo_barras,))
            
            rentas = resultado_rentas[0][0] if resultado_rentas else 0
            ventas = resultado_ventas[0][0] if resultado_ventas else 0
            
            return (rentas > 0) or (ventas > 0)
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en _disfraz_tiene_movimiento: {e}")
            return True  # Por seguridad
        except Exception as e:
            logger.error(f"Error inesperado en _disfraz_tiene_movimiento: {e}")
            return True

    def _eliminar_disfraz_fisico(self, codigo_barras: str) -> Tuple[bool, str]:
        """Elimina físicamente un disfraz (DELETE)."""
        try:
            self.db.conectar()
            query = "DELETE FROM INVENTARIO WHERE Codigo_Barras = %s"
            filas = self.db.ejecutar_update(query, (codigo_barras,))
            
            if filas and filas > 0:
                logger.info(f"Disfraz '{codigo_barras}' eliminado completamente de la base de datos")
                return True, "Disfraz eliminado completamente de la base de datos"
            logger.warning(f"No se pudo eliminar disfraz '{codigo_barras}'")
            return False, "No se pudo eliminar el disfraz"
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en _eliminar_disfraz_fisico: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en _eliminar_disfraz_fisico: {e}")
            return False, f"Error: {str(e)}"

    def _cambiar_a_inactivo(self, codigo_barras: str) -> Tuple[bool, str]:
        """Soft delete: pasa Estado a 'Inactivo'."""
        try:
            disfraz = self.buscar_por_codigo(codigo_barras)
            if not disfraz:
                logger.warning(f"Disfraz con código {codigo_barras} no encontrado para inactivar")
                return False, f"Disfraz con código {codigo_barras} no encontrado"
            
            self.db.conectar()
            query = "UPDATE INVENTARIO SET Estado = 'Inactivo' WHERE Codigo_Barras = %s"
            filas = self.db.ejecutar_update(query, (codigo_barras,))
            
            if filas and filas > 0:
                logger.info(f"Disfraz '{disfraz.descripcion}' marcado como inactivo (tiene movimiento)")
                return True, f"Disfraz '{disfraz.descripcion}' marcado como inactivo (tiene movimiento)"
            
            logger.warning(f"No se pudo cambiar estado del disfraz '{codigo_barras}'")
            return False, "No se pudo cambiar estado del disfraz"
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en _cambiar_a_inactivo: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en _cambiar_a_inactivo: {e}")
            return False, f"Error: {str(e)}"

    # ============================================================
    # VERIFICACIÓN DE DISPONIBILIDAD
    # ============================================================

    def verificar_disponibilidad(self, codigo_barras: str, cantidad: int) -> Tuple[bool, str, int]:
        """
        Verifica si hay suficiente disponible para rentar o vender.
        """
        try:
            disfraz = self.buscar_por_codigo(codigo_barras)
            
            if not disfraz:
                logger.warning(f"Disfraz no encontrado: {codigo_barras}")
                return False, f"Disfraz no encontrado: {codigo_barras}", 0
            
            if not disfraz.esta_activo():
                logger.warning(f"Disfraz inactivo: {codigo_barras}")
                return False, f"Disfraz inactivo: {codigo_barras}", 0
            
            if cantidad <= 0:
                logger.warning(f"Cantidad inválida para verificar disponibilidad: {cantidad}")
                return False, "Cantidad debe ser mayor a 0", disfraz.disponible
            
            if disfraz.disponible < cantidad:
                logger.info(f"Stock insuficiente para {codigo_barras}: disponible={disfraz.disponible}, solicitado={cantidad}")
                return False, f"Stock insuficiente: disponible={disfraz.disponible}, solicitado={cantidad}", disfraz.disponible
            
            logger.debug(f"Disponibilidad verificada para {codigo_barras}: OK")
            return True, "OK", disfraz.disponible
        
        except Exception as e:
            logger.error(f"Error inesperado en verificar_disponibilidad: {e}")
            return False, f"Error: {str(e)}", 0

    def obtener_disponible(self, codigo_barras: str) -> int:
        """Retorna Disponible de un disfraz."""
        try:
            disfraz = self.buscar_por_codigo(codigo_barras)
            disponible = disfraz.disponible if disfraz else 0
            logger.debug(f"Disponible para {codigo_barras}: {disponible}")
            return disponible
        except Exception as e:
            logger.error(f"Error inesperado en obtener_disponible: {e}")
            return 0

    def tiene_disponible(self, codigo_barras: str, cantidad: int) -> bool:
        """True si hay suficiente disponible."""
        try:
            disfraz = self.buscar_por_codigo(codigo_barras)
            tiene = disfraz.disponible >= cantidad if disfraz else False
            logger.debug(f"Disponible para {codigo_barras}: {disfraz.disponible if disfraz else 0}, solicitado: {cantidad}, tiene: {tiene}")
            return tiene
        except Exception as e:
            logger.error(f"Error inesperado en tiene_disponible: {e}")
            return False

    # ============================================================
    # STOCK: DESCONTAR / AUMENTAR
    # ============================================================

    def descontar_stock(self, codigo_barras: str, cantidad: int) -> Tuple[bool, str]:
        """
        Descuenta unidades de Disponible (para renta/venta confirmada).
        """
        try:
            disfraz = self.buscar_por_codigo(codigo_barras)
            if not disfraz:
                logger.warning(f"Disfraz no encontrado para descontar stock: {codigo_barras}")
                return False, f"Disfraz no encontrado: {codigo_barras}"

            if not disfraz.esta_activo():
                logger.warning(f"Disfraz inactivo para descontar stock: {codigo_barras}")
                return False, f"Disfraz inactivo: {codigo_barras}"

            if cantidad <= 0:
                logger.warning(f"Cantidad inválida para descontar stock: {cantidad}")
                return False, "La cantidad a descontar debe ser mayor a 0"

            if disfraz.disponible < cantidad:
                logger.info(f"Stock insuficiente para descontar: disponible={disfraz.disponible}, solicitado={cantidad}")
                return False, f"Stock insuficiente: disponible={disfraz.disponible}, solicitado={cantidad}"

            nuevo_disponible = disfraz.disponible - cantidad

            self.db.conectar()
            q = "UPDATE INVENTARIO SET Disponible = %s WHERE Codigo_Barras = %s"
            filas = self.db.ejecutar_update(q, (nuevo_disponible, codigo_barras))

            if filas and filas > 0:
                logger.info(f"Stock descontado para {codigo_barras}: -{cantidad} (nuevo disponible={nuevo_disponible})")
                return True, "Stock descontado correctamente"

            logger.warning(f"No se pudo actualizar el stock para {codigo_barras}")
            return False, "No se pudo actualizar el stock"

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en descontar_stock: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en descontar_stock: {e}")
            return False, f"Error inesperado: {str(e)}"

    def aumentar_stock(self, codigo_barras: str, cantidad: int) -> Tuple[bool, str]:
        """
        Aumenta unidades de Disponible (por devolución/cancelación).
        """
        try:
            disfraz = self.buscar_por_codigo(codigo_barras)
            if not disfraz:
                logger.warning(f"Disfraz no encontrado para aumentar stock: {codigo_barras}")
                return False, f"Disfraz no encontrado: {codigo_barras}"

            if cantidad <= 0:
                logger.warning(f"Cantidad inválida para aumentar stock: {cantidad}")
                return False, "La cantidad a aumentar debe ser mayor a 0"

            nuevo_disponible = disfraz.disponible + cantidad

            if nuevo_disponible > disfraz.stock:
                logger.warning(
                    f"No se puede aumentar disponible por encima del stock. "
                    f"Stock={disfraz.stock}, disponible actual={disfraz.disponible}, intento={cantidad}"
                )
                return False, (
                    f"No se puede aumentar disponible por encima del stock. "
                    f"Stock={disfraz.stock}, disponible actual={disfraz.disponible}, "
                    f"intento={cantidad}"
                )

            self.db.conectar()
            q = "UPDATE INVENTARIO SET Disponible = %s WHERE Codigo_Barras = %s"
            filas = self.db.ejecutar_update(q, (nuevo_disponible, codigo_barras))

            if filas and filas > 0:
                logger.info(f"Stock aumentado para {codigo_barras}: +{cantidad} (nuevo disponible={nuevo_disponible})")
                return True, "Stock aumentado correctamente"

            logger.warning(f"No se pudo actualizar el stock para {codigo_barras}")
            return False, "No se pudo actualizar el stock"

        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en aumentar_stock: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en aumentar_stock: {e}")
            return False, f"Error inesperado: {str(e)}"

    # ============================================================
    # AGREGAR DISFRAZ
    # ============================================================

    def agregar_disfraz(self, codigo_barras, descripcion, talla, color, categoria,
                        precio_venta, precio_renta, stock):
        """
        Registra un disfraz nuevo en el inventario.
        """
        ok, msg = self._validar_datos(codigo_barras, descripcion, talla, color, categoria,
                                      precio_venta, precio_renta, stock)
        if not ok:
            logger.warning(f"Intento de agregar disfraz fallido: {msg}")
            return False, msg, None

        if self.buscar_por_codigo(codigo_barras):
            logger.warning(f"Intento de agregar disfraz duplicado: {codigo_barras}")
            return False, f"El código '{codigo_barras}' ya existe", None

        try:
            self.db.conectar()
            query = """
                INSERT INTO INVENTARIO 
                (Codigo_Barras, Descripcion, Talla, Color, Categoria, 
                 Precio_Venta, Precio_Renta, Stock, Disponible, Estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Activo')
            """
            stock = int(stock)
            nuevo_id = self.db.ejecutar_insert(
                query,
                (codigo_barras, descripcion, talla, color, categoria,
                 precio_venta, precio_renta, stock, stock)
            )

            # INVENTARIO no tiene autoincrement; si no hubo excepción, consideramos éxito.
            logger.info(f"Disfraz '{descripcion}' agregado exitosamente en INVENTARIO")
            return True, "Disfraz agregado exitosamente", nuevo_id
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en agregar_disfraz: {e}")
            return False, f"Error de base de datos: {str(e)}", None
        except Exception as e:
            logger.error(f"Error inesperado en agregar_disfraz: {e}")
            return False, f"Error inesperado: {str(e)}", None

    # ============================================================
    # EDITAR DISFRAZ
    # ============================================================

    def editar_disfraz(self, codigo_barras, descripcion=None, talla=None, color=None,
                       categoria=None, precio_venta=None, precio_renta=None, stock=None):
        """
        Edita información del disfraz con validación de stock.
        """
        disfraz = self.buscar_por_codigo(codigo_barras)
        if not disfraz:
            logger.warning(f"Intento de editar disfraz inexistente: {codigo_barras}")
            return False, "Disfraz no encontrado"

        campos = []
        valores = []

        if descripcion is not None:
            if not descripcion or len(descripcion.strip()) < 5:
                logger.warning(f"Intento de editar disfraz con descripción inválida: {descripcion}")
                return False, "Descripción debe tener mínimo 5 caracteres"
            campos.append("Descripcion = %s")
            valores.append(descripcion)

        if talla is not None:
            if not talla or talla.strip() == "":
                logger.warning(f"Intento de editar disfraz con talla vacía: {talla}")
                return False, "Talla no puede estar vacía"
            campos.append("Talla = %s")
            valores.append(talla)

        if color is not None:
            if not color or color.strip() == "":
                logger.warning(f"Intento de editar disfraz con color vacío: {color}")
                return False, "Color no puede estar vacío"
            campos.append("Color = %s")
            valores.append(color)

        if categoria is not None:
            if not categoria or categoria.strip() == "":
                logger.warning(f"Intento de editar disfraz con categoría vacía: {categoria}")
                return False, "Categoría no puede estar vacía"
            campos.append("Categoria = %s")
            valores.append(categoria)

        if precio_venta is not None:
            try:
                precio_venta = float(precio_venta)
                if precio_venta <= 0:
                    logger.warning(f"Intento de editar disfraz con precio de venta inválido: {precio_venta}")
                    return False, "Precio de venta debe ser mayor a 0"
                campos.append("Precio_Venta = %s")
                valores.append(precio_venta)
            except (ValueError, TypeError):
                logger.warning(f"Intento de editar disfraz con precio de venta no numérico: {precio_venta}")
                return False, "Precio de venta debe ser un número válido"

        if precio_renta is not None:
            try:
                precio_renta = float(precio_renta)
                if precio_renta <= 0:
                    logger.warning(f"Intento de editar disfraz con precio de renta inválido: {precio_renta}")
                    return False, "Precio de renta debe ser mayor a 0"
                campos.append("Precio_Renta = %s")
                valores.append(precio_renta)
            except (ValueError, TypeError):
                logger.warning(f"Intento de editar disfraz con precio de renta no numérico: {precio_renta}")
                return False, "Precio de renta debe ser un número válido"

        if stock is not None:
            try:
                nuevo_stock = int(stock)
                if nuevo_stock < 0:
                    logger.warning(f"Intento de editar disfraz con stock negativo: {nuevo_stock}")
                    return False, "Stock no puede ser negativo"
                
                rentados = disfraz.stock - disfraz.disponible
                if nuevo_stock < rentados:
                    logger.warning(
                        f"No puedes reducir stock por debajo de {rentados} "
                        f"(actualmente rentados). Nuevo stock mínimo: {rentados}"
                    )
                    return False, (
                        f"No puedes reducir stock por debajo de {rentados} "
                        f"(actualmente rentados). Nuevo stock mínimo: {rentados}"
                    )
                campos.append("Stock = %s")
                valores.append(nuevo_stock)
            except (ValueError, TypeError):
                logger.warning(f"Intento de editar disfraz con stock no entero: {stock}")
                return False, "Stock debe ser un número entero válido"

        if not campos:
            logger.info(f"No hay cambios para aplicar al disfraz '{codigo_barras}'")
            return False, "No hay datos para actualizar"

        valores.append(codigo_barras)

        try:
            self.db.conectar()
            query = f"UPDATE INVENTARIO SET {', '.join(campos)} WHERE Codigo_Barras = %s"
            rows = self.db.ejecutar_update(query, tuple(valores))
            
            if rows and rows > 0:
                logger.info(f"Disfraz '{codigo_barras}' actualizado exitosamente")
                return True, "Disfraz actualizado exitosamente"
            
            logger.warning(f"No se realizaron cambios al actualizar disfraz '{codigo_barras}'")
            return False, "No se realizaron cambios"
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en editar_disfraz: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en editar_disfraz: {e}")
            return False, f"Error inesperado: {str(e)}"

    # ============================================================
    # ELIMINAR DISFRAZ
    # ============================================================

    def eliminar_disfraz(self, codigo_barras):
        """
        Elimina un disfraz del sistema (soft delete o delete físico).
        """
        try:
            disfraz = self.buscar_por_codigo(codigo_barras)
            if not disfraz:
                logger.warning(f"Intento de eliminar disfraz inexistente: {codigo_barras}")
                return False, f"Disfraz con código {codigo_barras} no encontrado"

            if self._disfraz_tiene_movimiento(codigo_barras):
                logger.info(f"Disfraz '{codigo_barras}' tiene movimiento. Cambiando a inactivo...")
                return self._cambiar_a_inactivo(codigo_barras)
            else:
                logger.info(f"Disfraz '{codigo_barras}' sin movimiento. Eliminando completamente...")
                return self._eliminar_disfraz_fisico(codigo_barras)
        
        except Exception as e:
            logger.error(f"Error inesperado en eliminar_disfraz: {e}")
            return False, f"Error inesperado: {str(e)}"

    # ============================================================
    # BÚSQUEDAS
    # ============================================================

    def buscar_por_codigo(self, codigo_barras: str) -> Optional[Disfraz]:
        try:
            self.db.conectar()
            q = "SELECT * FROM INVENTARIO WHERE Codigo_Barras = %s"
            r = self.db.ejecutar_query(q, (codigo_barras,))
            disfraz = Disfraz.from_db_row(r[0]) if r else None
            if disfraz:
                logger.debug(f"Disfraz encontrado por código '{codigo_barras}': {disfraz.descripcion}")
            else:
                logger.info(f"Disfraz con código '{codigo_barras}' no encontrado")
            return disfraz
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en buscar_por_codigo: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en buscar_por_codigo: {e}")
            return None

    def buscar_por_descripcion(self, termino: str) -> List[Disfraz]:
        try:
            self.db.conectar()
            like = f"%{termino}%"
            q = """
                SELECT * FROM INVENTARIO
                WHERE Estado = 'Activo'
                  AND LOWER(Descripcion) LIKE LOWER(%s)
                ORDER BY Descripcion
                LIMIT 25
            """
            r = self.db.ejecutar_query(q, (like,))
            disfraces = [Disfraz.from_db_row(x) for x in r] if r else []
            logger.info(f"Buscando disfraces por descripción '{termino}' - encontrados: {len(disfraces)}")
            return disfraces
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en buscar_por_descripcion: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en buscar_por_descripcion: {e}")
            return []

    def buscar_por_categoria(self, categoria: str) -> List[Disfraz]:
        try:
            self.db.conectar()
            like = f"%{categoria}%"
            q = """
                SELECT * FROM INVENTARIO
                WHERE Estado = 'Activo'
                  AND LOWER(Categoria) LIKE LOWER(%s)
                ORDER BY Descripcion
                LIMIT 25
            """
            r = self.db.ejecutar_query(q, (like,))
            disfraces = [Disfraz.from_db_row(x) for x in r] if r else []
            logger.info(f"Buscando disfraces por categoría '{categoria}' - encontrados: {len(disfraces)}")
            return disfraces
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en buscar_por_categoria: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en buscar_por_categoria: {e}")
            return []

    def buscar_completo(self, termino: str) -> List[Disfraz]:
        try:
            self.db.conectar()
            like = f"%{termino}%"
            q = """
                SELECT * FROM INVENTARIO
                WHERE Estado = 'Activo'
                  AND (LOWER(Codigo_Barras) LIKE LOWER(%s)
                    OR LOWER(Descripcion) LIKE LOWER(%s)
                    OR LOWER(Talla) LIKE LOWER(%s)
                    OR LOWER(Color) LIKE LOWER(%s)
                    OR LOWER(Categoria) LIKE LOWER(%s))
                ORDER BY Descripcion
                LIMIT 25
            """
            r = self.db.ejecutar_query(q, (like, like, like, like, like))
            disfraces = [Disfraz.from_db_row(x) for x in r] if r else []
            logger.info(f"Buscando disfraces completos por término '{termino}' - encontrados: {len(disfraces)}")
            return disfraces
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en buscar_completo: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en buscar_completo: {e}")
            return []

    # ============================================================
    # LISTAR Y CONTAR
    # ============================================================

    def listar_disponibles(self) -> List[Disfraz]:
        """
        Lista disfraces activos con Disponible > 0.
        """
        try:
            self.db.conectar()
            q = """
                SELECT * FROM INVENTARIO
                WHERE Estado = 'Activo' AND Disponible > 0
                ORDER BY Descripcion
            """
            r = self.db.ejecutar_query(q)
            disfraces = [Disfraz.from_db_row(x) for x in r] if r else []
            logger.info(f"Listando disfraces disponibles - encontrados: {len(disfraces)}")
            return disfraces
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en listar_disponibles: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en listar_disponibles: {e}")
            return []

    def listar_disfraces(self, categoria: Optional[str] = None, solo_activos: bool = True) -> List[Disfraz]:
        try:
            self.db.conectar()
            
            if categoria:
                if solo_activos:
                    q = """
                        SELECT * FROM INVENTARIO 
                        WHERE Estado = 'Activo' AND Categoria = %s
                        ORDER BY Descripcion
                    """
                    r = self.db.ejecutar_query(q, (categoria,))
                else:
                    q = """
                        SELECT * FROM INVENTARIO 
                        WHERE Categoria = %s
                        ORDER BY Descripcion
                    """
                    r = self.db.ejecutar_query(q, (categoria,))
            else:
                if solo_activos:
                    q = "SELECT * FROM INVENTARIO WHERE Estado = 'Activo' ORDER BY Descripcion"
                else:
                    q = "SELECT * FROM INVENTARIO ORDER BY Descripcion"
                r = self.db.ejecutar_query(q)
            
            disfraces = [Disfraz.from_db_row(x) for x in r] if r else []
            logger.info(f"Listando disfraces - encontrados: {len(disfraces)} (solo_activos={solo_activos}, categoria={categoria})")
            return disfraces
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en listar_disfraces: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en listar_disfraces: {e}")
            return []

    def contar_disfraces(self, solo_activos: bool = True) -> int:
        try:
            self.db.conectar()
            
            if solo_activos:
                q = "SELECT COUNT(*) FROM INVENTARIO WHERE Estado = 'Activo'"
            else:
                q = "SELECT COUNT(*) FROM INVENTARIO"
            
            r = self.db.ejecutar_query(q)
            total = r[0][0] if r else 0
            logger.info(f"Conteo de disfraces - total: {total} (solo_activos={solo_activos})")
            return total
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en contar_disfraces: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error inesperado en contar_disfraces: {e}")
            return 0

    def obtener_ultimos_disfraces(self, limite: int = 10) -> List[Disfraz]:
        try:
            self.db.conectar()
            q = """
                SELECT * FROM INVENTARIO 
                WHERE Estado = 'Activo'
                ORDER BY Fecha_Registro DESC 
                LIMIT %s
            """
            r = self.db.ejecutar_query(q, (limite,))
            disfraces = [Disfraz.from_db_row(x) for x in r] if r else []
            logger.info(f"Obteniendo últimos {limite} disfraces - encontrados: {len(disfraces)}")
            return disfraces
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en obtener_ultimos_disfraces: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en obtener_ultimos_disfraces: {e}")
            return []

    # ============================================================
    # ANÁLISIS Y REPORTES
    # ============================================================

    def obtener_stock_total(self) -> int:
        try:
            self.db.conectar()
            q = "SELECT COALESCE(SUM(Stock), 0) FROM INVENTARIO WHERE Estado = 'Activo'"
            r = self.db.ejecutar_query(q)
            total = r[0][0] if r else 0
            logger.info(f"Stock total del sistema: {total}")
            return total
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en obtener_stock_total: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error inesperado en obtener_stock_total: {e}")
            return 0

    def obtener_disponible_total(self) -> int:
        try:
            self.db.conectar()
            q = "SELECT COALESCE(SUM(Disponible), 0) FROM INVENTARIO WHERE Estado = 'Activo'"
            r = self.db.ejecutar_query(q)
            total = r[0][0] if r else 0
            logger.info(f"Disponible total del sistema: {total}")
            return total
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en obtener_disponible_total: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error inesperado en obtener_disponible_total: {e}")
            return 0

    def obtener_rentados_total(self) -> int:
        try:
            stock = self.obtener_stock_total()
            disponible = self.obtener_disponible_total()
            rentados = stock - disponible
            logger.info(f"Rentados total del sistema: {rentados}")
            return rentados
        except Exception as e:
            logger.error(f"Error inesperado en obtener_rentados_total: {e}")
            return 0


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRUEBA - InventarioController v2.2")
    print("CON LOGGING Y VALIDACIONES DE STOCK")
    print("="*60 + "\n")
    
    inv = InventarioController()
    
    print("1️⃣ Listando disfraces activos...")
    disfraces = inv.listar_disfraces(solo_activos=True)
    print(f"   Total: {len(disfraces)}\n")
    
    print("2️⃣ Contando disfraces...")
    total = inv.contar_disfraces()
    print(f"   Total: {total}\n")
    
    print("3️⃣ Stock total del sistema...")
    stock = inv.obtener_stock_total()
    disponible = inv.obtener_disponible_total()
    rentados = inv.obtener_rentados_total()
    print(f"   Stock Total: {stock}")
    print(f"   Disponible: {disponible}")
    print(f"   Rentados: {rentados}\n")
    
    print("4️⃣ Buscando disfraces por descripción...")
    resultados = inv.buscar_por_descripcion("halloween")
    print(f"   Encontrados: {len(resultados)}\n")
    
    print("="*60 + "\n")