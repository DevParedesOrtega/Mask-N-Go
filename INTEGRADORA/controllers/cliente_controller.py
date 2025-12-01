"""
Módulo: cliente_controller.py
Ubicación: controllers/cliente_controller.py
Descripción: Controlador moderno para gestión de clientes
Sistema: MaskNGO - Renta y Venta de Disfraces
Versión: 2.1 - Con logging y mejoras de seguridad y validaciones
"""

import sys
import os
from typing import List, Tuple, Optional
import mysql.connector

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
from models.cliente import Cliente
from utils.validadores import Validadores
from utils.logger_config import setup_logger


# Configurar logging
logger = setup_logger('cliente_controller', 'logs/clientes.log')


class ClienteController:
    """
    Controlador para gestión de clientes.
    
    Características:
    - Validación exhaustiva de datos
    - Detección de duplicados (advertencia, no rechazo)
    - Teléfono único por cliente
    - Búsquedas insensibles a mayúsculas
    - Soft delete si cliente tiene transacciones
    - Eliminación física solo si nunca compró/rentó
    - Métodos de reportes y análisis
    """

    def __init__(self):
        """Inicializa el controlador con conexión a BD."""
        self.db = ConexionDB()

    # ============================================================
    # VALIDACIONES PRIVADAS
    # ============================================================

    def _validar_datos(self, nombre, apellido, telefono):
        """Valida los campos básicos antes de insertar o editar."""

        v1, msg = Validadores.validar_nombre(nombre)
        if not v1:
            return False, f"Nombre inválido: {msg}"

        v2, msg = Validadores.validar_nombre(apellido)
        if not v2:
            return False, f"Apellido inválido: {msg}"

        v3, msg = Validadores.validar_telefono(telefono)
        if not v3:
            return False, f"Teléfono inválido: {msg}"

        return True, ""

    def _cliente_tiene_transacciones(self, id_cliente: int) -> bool:
        """
        Verifica si cliente tiene rentas o ventas registradas.
        
        Args:
            id_cliente: ID del cliente
        
        Returns:
            bool: True si tiene transacciones, False si no
        """
        try:
            self.db.conectar()
            
            # Verificar rentas
            query_rentas = "SELECT COUNT(*) FROM RENTAS WHERE Id_Cliente = %s"
            resultado_rentas = self.db.ejecutar_query(query_rentas, (id_cliente,))
            
            # Verificar ventas
            query_ventas = "SELECT COUNT(*) FROM VENTAS WHERE Id_cliente = %s"
            resultado_ventas = self.db.ejecutar_query(query_ventas, (id_cliente,))
            
            rentas = resultado_rentas[0][0] if resultado_rentas else 0
            ventas = resultado_ventas[0][0] if resultado_ventas else 0
            
            return (rentas > 0) or (ventas > 0)
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en _cliente_tiene_transacciones: {e}")
            return True  # Por seguridad, asumir que sí tiene transacciones
        except Exception as e:
            logger.error(f"Error inesperado en _cliente_tiene_transacciones: {e}")
            return True

    def _eliminar_cliente_fisico(self, id_cliente: int) -> Tuple[bool, str]:
        """
        Elimina un cliente físicamente (DELETE).
        SOLO para clientes sin transacciones.
        
        Args:
            id_cliente: ID del cliente a eliminar
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            self.db.conectar()
            query = "DELETE FROM CLIENTES WHERE Id_cliente = %s"
            filas = self.db.ejecutar_update(query, (id_cliente,))
            
            if filas and filas > 0:
                logger.info(f"Cliente ID {id_cliente} eliminado completamente de la base de datos")
                return True, "Cliente eliminado completamente de la base de datos"
            logger.warning(f"No se pudo eliminar cliente ID {id_cliente}")
            return False, "No se pudo eliminar el cliente"
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en _eliminar_cliente_fisico: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en _eliminar_cliente_fisico: {e}")
            return False, f"Error: {str(e)}"

    def _cambiar_a_inactivo(self, id_cliente: int) -> Tuple[bool, str]:
        """
        Cambia estado de cliente a inactivo (Soft delete).
        Para clientes con transacciones.
        
        Args:
            id_cliente: ID del cliente
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            cliente = self.buscar_por_id(id_cliente)
            if not cliente:
                logger.warning(f"Cliente con ID {id_cliente} no encontrado para inactivar")
                return False, f"Cliente con ID {id_cliente} no encontrado"
            
            self.db.conectar()
            query = "UPDATE CLIENTES SET Estado = 'Inactivo' WHERE Id_cliente = %s"
            filas = self.db.ejecutar_update(query, (id_cliente,))
            
            if filas and filas > 0:
                logger.info(f"Cliente '{cliente.nombre} {cliente.apellido_paterno}' marcado como inactivo (tiene transacciones)")
                return True, f"Cliente '{cliente.nombre} {cliente.apellido_paterno}' marcado como inactivo (tiene transacciones)"
            
            logger.warning(f"No se pudo cambiar estado del cliente ID {id_cliente}")
            return False, "No se pudo cambiar estado del cliente"
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en _cambiar_a_inactivo: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en _cambiar_a_inactivo: {e}")
            return False, f"Error: {str(e)}"

    # ============================================================
    # BÚSQUEDA DE DUPLICADOS
    # ============================================================

    def buscar_duplicados(self, nombre: str, apellido: str, telefono: str) -> List[Cliente]:
        """
        Devuelve posibles clientes duplicados por nombre o teléfono.
        
        Args:
            nombre: Nombre del cliente
            apellido: Apellido del cliente
            telefono: Teléfono del cliente
        
        Returns:
            List[Cliente]: Lista de posibles duplicados
        """
        try:
            self.db.conectar()
            query = """
                SELECT * FROM CLIENTES
                WHERE (LOWER(Nombre) = LOWER(%s) AND LOWER(Apellido_Paterno) = LOWER(%s))
                   OR Telefono = %s
            """
            rows = self.db.ejecutar_query(query, (nombre, apellido, telefono))
            
            if rows:
                clientes = [Cliente.from_db_row(r) for r in rows]
                logger.info(f"Buscando duplicados para {nombre} {apellido} - encontrados: {len(clientes)}")
                return clientes
            return []
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en buscar_duplicados: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en buscar_duplicados: {e}")
            return []

    # ============================================================
    # AGREGAR CLIENTE
    # ============================================================

    def agregar_cliente(self, nombre, apellido, telefono, forzar=False):
        """
        Registra un cliente nuevo con validación y detector de duplicados.
        
        Args:
            nombre: Nombre del cliente
            apellido: Apellido paterno
            telefono: Teléfono de contacto
            forzar: Si True, ignora advertencia de duplicados
        
        Returns:
            Tuple[bool, str, Optional[int], Optional[List]]: 
                (éxito, mensaje, id_cliente, duplicados)
        """
        # 1. Validar campos
        ok, msg = self._validar_datos(nombre, apellido, telefono)
        if not ok:
            logger.warning(f"Intento de registro de cliente fallido: {msg}")
            return False, msg, None, None

        # 2. Verificar que el teléfono NO esté registrado (debe ser único)
        existente = self.buscar_por_telefono(telefono)
        if existente:
            logger.warning(f"Intento de registro con teléfono duplicado: {telefono}")
            return False, f"El teléfono {telefono} ya está registrado con otro cliente", None, None

        # 3. Buscar duplicados por nombre/apellido
        duplicados = self.buscar_duplicados(nombre, apellido, telefono)

        # Si hay duplicados exactos y no fuerza → advertencia
        if duplicados and not forzar:
            logger.info(f"Posibles duplicados encontrados para {nombre} {apellido}")
            return False, "⚠️ Posibles duplicados encontrados. ¿Confirmar registro?", None, duplicados

        # 4. Insertar en BD
        try:
            self.db.conectar()
            query = """
                INSERT INTO CLIENTES (Nombre, Apellido_Paterno, Telefono, Estado)
                VALUES (%s, %s, %s, 'Activo')
            """
            new_id = self.db.ejecutar_insert(query, (nombre, apellido, telefono))

            if new_id:
                logger.info(f"Cliente '{nombre} {apellido}' agregado exitosamente con ID {new_id}")
                return True, "Cliente agregado exitosamente", new_id, None
            
            logger.error(f"Error al registrar cliente '{nombre} {apellido}' en la base de datos")
            return False, "Error al registrar cliente", None, None
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en agregar_cliente: {e}")
            return False, f"Error de base de datos: {str(e)}", None, None
        except Exception as e:
            logger.error(f"Error inesperado en agregar_cliente: {e}")
            return False, f"Error inesperado: {str(e)}", None, None

    # ============================================================
    # EDITAR CLIENTE
    # ============================================================

    def editar_cliente(self, id_cliente, nombre=None, apellido=None, telefono=None):
        """
        Edita información del cliente.
        
        Args:
            id_cliente: ID del cliente a editar
            nombre: Nuevo nombre (opcional)
            apellido: Nuevo apellido (opcional)
            telefono: Nuevo teléfono (opcional)
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """

        # 1. Comprobar si existe
        cliente = self.buscar_por_id(id_cliente)
        if not cliente:
            logger.warning(f"Intento de editar cliente inexistente: ID {id_cliente}")
            return False, "Cliente no encontrado"

        campos = []
        valores = []

        # Validar y preparar campos a actualizar
        if nombre is not None:
            v, msg = Validadores.validar_nombre(nombre)
            if not v:
                logger.warning(f"Intento de edición con nombre inválido: {msg}")
                return False, f"Nombre: {msg}"
            campos.append("Nombre = %s")
            valores.append(nombre)

        if apellido is not None:
            v, msg = Validadores.validar_nombre(apellido)
            if not v:
                logger.warning(f"Intento de edición con apellido inválido: {msg}")
                return False, f"Apellido: {msg}"
            campos.append("Apellido_Paterno = %s")
            valores.append(apellido)

        if telefono is not None:
            v, msg = Validadores.validar_telefono(telefono)
            if not v:
                logger.warning(f"Intento de edición con teléfono inválido: {msg}")
                return False, f"Teléfono: {msg}"

            # Verificar que el nuevo teléfono NO esté en uso
            existe = self.buscar_por_telefono(telefono)
            if existe and existe.id_cliente != id_cliente:
                logger.warning(f"Intento de edición con teléfono ya registrado: {telefono}")
                return False, f"El teléfono {telefono} ya está registrado con otro cliente"

            campos.append("Telefono = %s")
            valores.append(telefono)

        if not campos:
            logger.info(f"No hay cambios para aplicar al cliente ID {id_cliente}")
            return False, "No hay datos para actualizar"

        valores.append(id_cliente)

        # Ejecutar actualización
        try:
            self.db.conectar()
            query = f"UPDATE CLIENTES SET {', '.join(campos)} WHERE Id_cliente = %s"
            rows = self.db.ejecutar_update(query, tuple(valores))
            
            if rows and rows > 0:
                logger.info(f"Cliente ID {id_cliente} actualizado exitosamente")
                return True, "Cliente actualizado exitosamente"
            
            logger.warning(f"No se realizaron cambios al actualizar cliente ID {id_cliente}")
            return False, "No se realizaron cambios"
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en editar_cliente: {e}")
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en editar_cliente: {e}")
            return False, f"Error inesperado: {str(e)}"

    # ============================================================
    # ELIMINAR CLIENTE
    # ============================================================

    def eliminar_cliente(self, id_cliente):
        """
        Elimina un cliente del sistema.
        
        LÓGICA:
        - Si tiene rentas/ventas → Cambiar a inactivo (soft delete)
        - Si NO tiene transacciones → Eliminar físicamente (DELETE)
        
        Args:
            id_cliente: ID del cliente a eliminar
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            cliente = self.buscar_por_id(id_cliente)
            if not cliente:
                logger.warning(f"Intento de eliminar cliente inexistente: ID {id_cliente}")
                return False, f"Cliente con ID {id_cliente} no encontrado"

            # Verificar si tiene transacciones
            if self._cliente_tiene_transacciones(id_cliente):
                # Soft delete: cambiar a inactivo
                logger.info(f"Cliente {id_cliente} tiene transacciones. Cambiando a inactivo...")
                return self._cambiar_a_inactivo(id_cliente)
            else:
                # Delete físico: no tiene transacciones
                logger.info(f"Cliente {id_cliente} sin transacciones. Eliminando completamente...")
                return self._eliminar_cliente_fisico(id_cliente)
        
        except Exception as e:
            logger.error(f"Error inesperado en eliminar_cliente: {e}")
            return False, f"Error inesperado: {str(e)}"

    # ============================================================
    # BÚSQUEDAS
    # ============================================================

    def buscar_por_id(self, id_cliente) -> Optional[Cliente]:
        """
        Busca un cliente por su ID.
        
        Args:
            id_cliente: ID del cliente
        
        Returns:
            Optional[Cliente]: Objeto Cliente o None
        """
        try:
            self.db.conectar()
            q = "SELECT * FROM CLIENTES WHERE Id_cliente = %s"
            r = self.db.ejecutar_query(q, (id_cliente,))
            cliente = Cliente.from_db_row(r[0]) if r else None
            if cliente:
                logger.debug(f"Cliente encontrado por ID {id_cliente}: {cliente.nombre} {cliente.apellido_paterno}")
            else:
                logger.info(f"Cliente con ID {id_cliente} no encontrado")
            return cliente
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en buscar_por_id: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en buscar_por_id: {e}")
            return None

    def buscar_por_telefono(self, telefono) -> Optional[Cliente]:
        """
        Busca un cliente por su teléfono.
        
        Args:
            telefono: Teléfono del cliente
        
        Returns:
            Optional[Cliente]: Objeto Cliente o None
        """
        try:
            self.db.conectar()
            q = "SELECT * FROM CLIENTES WHERE Telefono = %s"
            r = self.db.ejecutar_query(q, (telefono,))
            cliente = Cliente.from_db_row(r[0]) if r else None
            if cliente:
                logger.debug(f"Cliente encontrado por teléfono {telefono}: {cliente.nombre} {cliente.apellido_paterno}")
            else:
                logger.info(f"Cliente con teléfono {telefono} no encontrado")
            return cliente
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en buscar_por_telefono: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en buscar_por_telefono: {e}")
            return None

    def buscar_por_nombre(self, termino: str) -> List[Cliente]:
        """
        Busca clientes por nombre o apellido (insensible a mayúsculas).
        
        Args:
            termino: Término de búsqueda
        
        Returns:
            List[Cliente]: Lista de clientes encontrados
        """
        try:
            self.db.conectar()
            like = f"%{termino}%"
            q = """
                SELECT * FROM CLIENTES
                WHERE LOWER(Nombre) LIKE LOWER(%s) 
                   OR LOWER(Apellido_Paterno) LIKE LOWER(%s)
                ORDER BY Nombre
            """
            r = self.db.ejecutar_query(q, (like, like))
            clientes = [Cliente.from_db_row(x) for x in r] if r else []
            logger.info(f"Buscando clientes por nombre '{termino}' - encontrados: {len(clientes)}")
            return clientes
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en buscar_por_nombre: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en buscar_por_nombre: {e}")
            return []

    # ============================================================
    # LISTAR Y CONTAR
    # ============================================================

    def listar_todos(self, solo_activos=True) -> List[Cliente]:
        """
        Lista todos los clientes del sistema.
        
        Args:
            solo_activos: Si True, solo clientes activos
        
        Returns:
            List[Cliente]: Lista de clientes
        """
        try:
            self.db.conectar()
            
            if solo_activos:
                q = "SELECT * FROM CLIENTES WHERE Estado = 'Activo' ORDER BY Fecha_Registro DESC"
            else:
                q = "SELECT * FROM CLIENTES ORDER BY Fecha_Registro DESC"
            
            r = self.db.ejecutar_query(q)
            clientes = [Cliente.from_db_row(x) for x in r] if r else []
            logger.info(f"Listando clientes - total: {len(clientes)} (solo_activos={solo_activos})")
            return clientes
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en listar_todos: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en listar_todos: {e}")
            return []

    def contar_clientes(self, solo_activos=True) -> int:
        """
        Cuenta el total de clientes.
        
        Args:
            solo_activos: Si True, solo clientes activos
        
        Returns:
            int: Total de clientes
        """
        try:
            self.db.conectar()
            
            if solo_activos:
                q = "SELECT COUNT(*) FROM CLIENTES WHERE Estado = 'Activo'"
            else:
                q = "SELECT COUNT(*) FROM CLIENTES"
            
            r = self.db.ejecutar_query(q)
            total = r[0][0] if r else 0
            logger.info(f"Conteo de clientes - total: {total} (solo_activos={solo_activos})")
            return total
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en contar_clientes: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error inesperado en contar_clientes: {e}")
            return 0

    def obtener_ultimos_clientes(self, limite: int = 10) -> List[Cliente]:
        """
        Obtiene los últimos N clientes registrados.
        
        Args:
            limite: Número de clientes a traer
        
        Returns:
            List[Cliente]: Lista de últimos clientes
        """
        try:
            self.db.conectar()
            q = """
                SELECT * FROM CLIENTES 
                WHERE Estado = 'Activo'
                ORDER BY Fecha_Registro DESC 
                LIMIT %s
            """
            r = self.db.ejecutar_query(q, (limite,))
            clientes = [Cliente.from_db_row(x) for x in r] if r else []
            logger.info(f"Obteniendo últimos {limite} clientes - encontrados: {len(clientes)}")
            return clientes
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en obtener_ultimos_clientes: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en obtener_ultimos_clientes: {e}")
            return []

    # ============================================================
    # ANÁLISIS Y REPORTES
    # ============================================================

    def cliente_tiene_rentas_activas(self, id_cliente: int) -> bool:
        """
        Verifica si cliente tiene rentas activas sin devolver.
        
        Args:
            id_cliente: ID del cliente
        
        Returns:
            bool: True si tiene rentas activas, False si no
        """
        try:
            self.db.conectar()
            q = """
                SELECT COUNT(*) FROM RENTAS 
                WHERE Id_Cliente = %s AND Estado IN ('Activa', 'Vencida')
            """
            r = self.db.ejecutar_query(q, (id_cliente,))
            tiene = r[0][0] > 0 if r else False
            logger.debug(f"Cliente {id_cliente} tiene rentas activas: {tiene}")
            return tiene
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en cliente_tiene_rentas_activas: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado en cliente_tiene_rentas_activas: {e}")
            return False

    def cliente_tiene_deudas(self, id_cliente: int) -> float:
        """
        Calcula deudas totales del cliente (penalizaciones no pagadas).
        
        Args:
            id_cliente: ID del cliente
        
        Returns:
            float: Total de deudas en pesos
        """
        try:
            self.db.conectar()
            q = """
                SELECT COALESCE(SUM(Penalizacion), 0) 
                FROM RENTAS 
                WHERE Id_Cliente = %s AND Penalizacion > 0
            """
            r = self.db.ejecutar_query(q, (id_cliente,))
            deuda = float(r[0][0]) if r else 0.0
            logger.debug(f"Cliente {id_cliente} tiene deuda: {deuda}")
            return deuda
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en cliente_tiene_deudas: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"Error inesperado en cliente_tiene_deudas: {e}")
            return 0.0

    def obtener_total_gastado(self, id_cliente: int) -> float:
        """
        Calcula total gastado por cliente (rentas + ventas).
        
        Args:
            id_cliente: ID del cliente
        
        Returns:
            float: Total gastado en pesos
        """
        try:
            self.db.conectar()
            
            # Total en rentas
            q_rentas = """
                SELECT COALESCE(SUM(Total), 0) FROM RENTAS 
                WHERE Id_Cliente = %s AND Estado IN ('Activa', 'Devuelto', 'Vencida')
            """
            r_rentas = self.db.ejecutar_query(q_rentas, (id_cliente,))
            total_rentas = float(r_rentas[0][0]) if r_rentas else 0.0
            
            # Total en ventas
            q_ventas = """
                SELECT COALESCE(SUM(Total - Descuento_Monto), 0) FROM VENTAS 
                WHERE Id_cliente = %s AND Estado = 'Activa'
            """
            r_ventas = self.db.ejecutar_query(q_ventas, (id_cliente,))
            total_ventas = float(r_ventas[0][0]) if r_ventas else 0.0
            
            total = total_rentas + total_ventas
            logger.debug(f"Cliente {id_cliente} ha gastado: {total}")
            return total
        
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en obtener_total_gastado: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"Error inesperado en obtener_total_gastado: {e}")
            return 0.0


# ============================================================
# PRUEBA INDEPENDIENTE
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRUEBA - ClienteController v2.1")
    print("CON LOGGING Y MEJORAS DE SEGURIDAD")
    print("="*60 + "\n")
    
    c = ClienteController()
    
    # Ejemplo 1: Listar clientes
    print("1️⃣ Listando clientes activos...")
    clientes = c.listar_todos(solo_activos=True)
    print(f"   Total: {len(clientes)}\n")
    
    # Ejemplo 2: Contar clientes
    print("2️⃣ Contando clientes...")
    total = c.contar_clientes()
    print(f"   Total: {total}\n")
    
    # Ejemplo 3: Buscar por nombre
    print("3️⃣ Buscando clientes por nombre...")
    resultados = c.buscar_por_nombre("juan")
    print(f"   Encontrados: {len(resultados)}\n")
    
    # Ejemplo 4: Obtener últimos clientes
    print("4️⃣ Últimos 5 clientes...")
    ultimos = c.obtener_ultimos_clientes(limite=5)
    print(f"   Encontrados: {len(ultimos)}\n")
    
    print("="*60 + "\n")