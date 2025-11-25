"""
Módulo: renta_controller.py
Ubicación: controllers/renta_controller.py
Descripción: Controlador para gestión de rentas
Sistema: Renta y Venta de Disfraces

PARTE 1: Registro y Gestión de Rentas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
from models.renta import Renta, DetalleRenta
from models.disfraz import Disfraz
from utils.validadores import Validadores
from typing import Optional, Tuple, List
from datetime import datetime, timedelta


class RentaController:
    """
    Controlador para manejar rentas del sistema.
    
    Características:
    - Registro de rentas con fechas automáticas
    - Cálculo automático de depósito (precio de venta)
    - Control transaccional de stock (disponible, NO stock)
    - Devoluciones con cálculo de penalizaciones
    - Marcado automático de rentas vencidas
    - Sin extensiones (debe devolver y rentar de nuevo)
    """
    
    def __init__(self):
        """Inicializa el controlador con conexión a BD."""
        self.db = ConexionDB()
        self.penalizacion_dia = self._cargar_penalizacion_dia()
    
    def _cargar_penalizacion_dia(self) -> float:
        """
        Carga la configuración de penalización diaria desde la BD.
        
        Returns:
            float: Monto de penalización por día (default: 50.00)
        """
        try:
            self.db.conectar()
            query = "SELECT Valor_Config FROM CONFIGURACION WHERE Nombre_Config = 'PENALIZACION_DIA'"
            resultado = self.db.ejecutar_query(query)
            
            if resultado and resultado[0]:
                return float(resultado[0][0])
            
            return 50.00  # Default
        
        except Exception as e:
            print(f"⚠️ Error al cargar penalización, usando default $50.00: {e}")
            return 50.00
    
    def registrar_renta(
        self,
        id_cliente: int,
        id_usuario: int,
        detalles: List[dict],
        dias_renta: int
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Registra una nueva renta en el sistema.
        
        PROCESO TRANSACCIONAL:
        1. Valida datos y stock disponible
        2. Calcula total y depósito (suma de precios de venta)
        3. Calcula fechas automáticamente
        4. Registra renta (header)
        5. Registra detalles
        6. Descuenta disponible (NO stock)
        7. Commit o rollback completo
        
        Args:
            id_cliente: ID del cliente (obligatorio)
            id_usuario: ID del empleado que registra
            detalles: Lista de diccionarios:
                [{'codigo_barras': str, 'cantidad': int}, ...]
            dias_renta: Número de días de renta
        
        Returns:
            Tuple[bool, str, Optional[int]]: (éxito, mensaje, id_renta)
        
        Example:
            >>> controller = RentaController()
            >>> detalles = [
            >>>     {'codigo_barras': 'DIS001', 'cantidad': 2}
            >>> ]
            >>> exito, msg, id = controller.registrar_renta(
            >>>     id_cliente=1,
            >>>     id_usuario=1,
            >>>     detalles=detalles,
            >>>     dias_renta=3
            >>> )
        """
        cursor = None
        try:
            # 1. VALIDACIONES INICIALES
            if not detalles or len(detalles) == 0:
                return False, "La renta debe tener al menos un producto", None
            
            if dias_renta <= 0:
                return False, "Los días de renta deben ser mayor a 0", None
            
            if dias_renta > 30:
                return False, "El máximo de días de renta es 30", None
            
            # 2. CONECTAR Y PREPARAR TRANSACCIÓN
            self.db.conectar()
            cursor = self.db.connection.cursor()
            
            # 3. VALIDAR Y PREPARAR DETALLES
            from controllers.inventario_controller import InventarioController
            inv_controller = InventarioController()
            
            detalles_validados = []
            subtotal = 0.0
            deposito_total = 0.0
            
            for item in detalles:
                codigo = item.get('codigo_barras')
                cantidad = item.get('cantidad', 0)
                
                if not codigo or cantidad <= 0:
                    return False, f"Producto inválido: {item}", None
                
                # Verificar stock disponible
                hay_stock, msg_stock, disponible = inv_controller.verificar_disponibilidad(codigo, cantidad)
                if not hay_stock:
                    return False, msg_stock, None
                
                # Obtener disfraz con precios actuales
                disfraz = inv_controller.buscar_por_codigo(codigo)
                if not disfraz:
                    return False, f"Disfraz '{codigo}' no encontrado", None
                
                if not disfraz.esta_activo():
                    return False, f"El disfraz '{codigo}' está inactivo", None
                
                # Crear detalle con precio de renta actual
                detalle = DetalleRenta(
                    codigo_barras=codigo,
                    cantidad=cantidad,
                    precio_unitario=disfraz.precio_renta
                )
                detalle.calcular_subtotal(dias_renta)
                
                detalles_validados.append(detalle)
                subtotal += detalle.subtotal
                
                # Depósito = suma de precios de VENTA (no renta)
                deposito_total += disfraz.precio_venta * cantidad
            
            # 4. CALCULAR FECHAS
            fecha_renta = datetime.now()
            fecha_devolucion = fecha_renta + timedelta(days=dias_renta)
            
            # 5. CREAR OBJETO RENTA
            renta = Renta(
                id_cliente=id_cliente,
                id_usuario=id_usuario,
                fecha_devolucion=fecha_devolucion,
                dias_renta=dias_renta,
                total=subtotal,
                deposito=deposito_total
            )
            
            renta.detalles = detalles_validados
            
            # Validación final
            valida, msg_val = renta.validar_renta()
            if not valida:
                return False, msg_val, None
            
            # 6. INSERTAR RENTA (HEADER)
            query_renta = """
                INSERT INTO RENTAS (
                    Id_Cliente, Id_Usuario, Fecha_Renta, Fecha_Devolucion,
                    Dias_Renta, Total, Deposito, Estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'Activa')
            """
            
            cursor.execute(query_renta, (
                id_cliente, id_usuario, fecha_renta, fecha_devolucion,
                dias_renta, subtotal, deposito_total
            ))
            
            id_renta = cursor.lastrowid
            
            if not id_renta:
                self.db.connection.rollback()
                return False, "Error al registrar renta", None
            
            # 7. INSERTAR DETALLES Y DESCONTAR DISPONIBLE (NO STOCK)
            query_detalle = """
                INSERT INTO DETALLE_RENTAS (
                    Id_Renta, Codigo_Barras, Cantidad, Precio_Unitario, Subtotal
                ) VALUES (%s, %s, %s, %s, %s)
            """
            
            query_descontar = """
                UPDATE INVENTARIO 
                SET Disponible = Disponible - %s 
                WHERE Codigo_Barras = %s
            """
            
            for detalle in detalles_validados:
                # Insertar detalle
                cursor.execute(query_detalle, (
                    id_renta,
                    detalle.codigo_barras,
                    detalle.cantidad,
                    detalle.precio_unitario,
                    detalle.subtotal
                ))
                
                # Descontar SOLO disponible (el stock NO baja en rentas)
                cursor.execute(query_descontar, (
                    detalle.cantidad,
                    detalle.codigo_barras
                ))
            
            # 8. COMMIT TRANSACCIÓN
            self.db.connection.commit()
            
            print(f"✅ Renta #{id_renta} registrada exitosamente")
            print(f"   Total: ${subtotal:.2f}")
            print(f"   Depósito: ${deposito_total:.2f}")
            print(f"   Fecha devolución: {fecha_devolucion.strftime('%Y-%m-%d')}")
            print(f"   Productos: {len(detalles_validados)}")
            
            return True, f"Renta #{id_renta} registrada exitosamente", id_renta
        
        except Exception as e:
            if self.db.connection:
                self.db.connection.rollback()
            print(f"❌ Error en registrar_renta: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error inesperado: {str(e)}", None
        
        finally:
            if cursor:
                cursor.close()
    
    def devolver_renta(
        self,
        id_renta: int,
        id_usuario: int
    ) -> Tuple[bool, str, dict]:
        """
        Procesa la devolución de una renta.
        
        PROCESO:
        1. Verifica que existe y está activa/vencida
        2. Calcula días de retraso y penalización
        3. Devuelve stock disponible
        4. Marca como devuelta
        5. Calcula montos finales
        
        Args:
            id_renta: ID de la renta a devolver
            id_usuario: ID del empleado que procesa
        
        Returns:
            Tuple[bool, str, dict]: (éxito, mensaje, info_financiera)
                info_financiera = {
                    'total_renta': float,
                    'deposito': float,
                    'dias_retraso': int,
                    'penalizacion': float,
                    'deposito_devuelto': float,
                    'cobrar_adicional': float
                }
        """
        try:
            # 1. Verificar que la renta existe
            renta = self.buscar_por_id(id_renta)
            if not renta:
                return False, f"No existe renta con ID {id_renta}", {}
            
            if renta.esta_devuelta():
                return False, "La renta ya fue devuelta", {}
            
            if not renta.esta_activa() and not renta.esta_vencida():
                return False, f"La renta tiene estado '{renta.estado}' y no puede devolverse", {}
            
            # 2. Calcular días de retraso y penalización
            dias_retraso = renta.dias_de_retraso()
            penalizacion = renta.calcular_penalizacion(self.penalizacion_dia)
            
            # 3. CONECTAR
            self.db.conectar()
            
            # 4. Obtener detalles para devolver stock
            query_detalles = "SELECT Codigo_Barras, Cantidad FROM DETALLE_RENTAS WHERE Id_Renta = %s"
            detalles = self.db.ejecutar_query(query_detalles, (id_renta,))
            
            if not detalles:
                return False, "No se encontraron detalles de la renta", {}
            
            # 5. Devolver stock DISPONIBLE (NO stock físico, ya que era renta)
            for detalle in detalles:
                codigo_barras, cantidad = detalle
                query_devolver = """
                    UPDATE INVENTARIO 
                    SET Disponible = Disponible + %s 
                    WHERE Codigo_Barras = %s
                """
                self.db.ejecutar_update(query_devolver, (cantidad, codigo_barras))
                print(f"   📦 Devueltos: {cantidad} unidades de '{codigo_barras}'")
            
            # 6. Marcar renta como devuelta y registrar penalización
            query_devolver_renta = """
                UPDATE RENTAS 
                SET Estado = 'Devuelto',
                    Fecha_Devuelto = NOW(),
                    Penalizacion = %s
                WHERE Id_Renta = %s
            """
            self.db.ejecutar_update(query_devolver_renta, (penalizacion, id_renta))
            
            # 7. Calcular montos finales
            deposito_devuelto = renta.deposito_a_devolver()
            cobrar_adicional = max(0, penalizacion)  # Solo penalizaciones adicionales
            
            info_financiera = {
                'total_renta': renta.total,
                'deposito': renta.deposito,
                'dias_retraso': dias_retraso,
                'penalizacion': penalizacion,
                'deposito_devuelto': deposito_devuelto,
                'cobrar_adicional': cobrar_adicional
            }
            
            print(f"✅ Renta #{id_renta} devuelta exitosamente")
            print(f"   Días de retraso: {dias_retraso}")
            print(f"   Penalización: ${penalizacion:.2f}")
            print(f"   Depósito devuelto: ${deposito_devuelto:.2f}")
            
            return True, f"Renta #{id_renta} devuelta exitosamente", info_financiera
        
        except Exception as e:
            print(f"❌ Error en devolver_renta: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error inesperado: {str(e)}", {}
    
    def marcar_rentas_vencidas(self) -> int:
        """
        Marca automáticamente como vencidas las rentas que pasaron su fecha.
        
        Este método debe ejecutarse periódicamente (ej: diariamente).
        
        Returns:
            int: Cantidad de rentas marcadas como vencidas
        """
        try:
            self.db.conectar()
            
            query = """
                UPDATE RENTAS 
                SET Estado = 'Vencida'
                WHERE Estado = 'Activa' 
                  AND Fecha_Devolucion < NOW()
            """
            
            filas = self.db.ejecutar_update(query)
            
            if filas and filas > 0:
                print(f"⚠️ {filas} rentas marcadas como vencidas")
                return filas
            
            return 0
        
        except Exception as e:
            print(f"❌ Error en marcar_rentas_vencidas: {e}")
            return 0

# CONTINÚA EN PARTE 2...
    
    def buscar_por_id(self, id_renta: int) -> Optional[Renta]:
        """Busca una renta por su ID."""
        try:
            self.db.conectar()
            query = "SELECT * FROM RENTAS WHERE Id_Renta = %s"
            resultados = self.db.ejecutar_query(query, (id_renta,))
            
            if resultados and len(resultados) > 0:
                return Renta.from_db_row(resultados[0])
            return None
        
        except Exception as e:
            print(f"❌ Error en buscar_por_id: {e}")
            return None
    
    def cargar_detalles(self, renta: Renta) -> bool:
        """Carga los detalles de una renta."""
        try:
            self.db.conectar()
            query = "SELECT * FROM DETALLE_RENTAS WHERE Id_Renta = %s"
            resultados = self.db.ejecutar_query(query, (renta.id_renta,))
            
            if resultados:
                for row in resultados:
                    detalle = DetalleRenta(
                        id_detalle=row[0],
                        id_renta=row[1],
                        codigo_barras=row[2],
                        cantidad=row[3],
                        precio_unitario=row[4]
                    )
                    detalle.subtotal = row[5]
                    renta.agregar_detalle(detalle)
                
                return True
            return False
        
        except Exception as e:
            print(f"❌ Error en cargar_detalles: {e}")
            return False
    
    def obtener_renta_completa(self, id_renta: int) -> Optional[Renta]:
        """Obtiene una renta con sus detalles cargados."""
        renta = self.buscar_por_id(id_renta)
        if renta:
            self.cargar_detalles(renta)
        return renta
    
    def listar_rentas_activas(self) -> List[Renta]:
        """Lista todas las rentas activas."""
        try:
            self.db.conectar()
            query = "SELECT * FROM RENTAS WHERE Estado = 'Activa' ORDER BY Fecha_Devolucion ASC"
            resultados = self.db.ejecutar_query(query)
            
            if resultados:
                return [Renta.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en listar_rentas_activas: {e}")
            return []
    
    def listar_rentas_vencidas(self) -> List[Renta]:
        """Lista todas las rentas vencidas."""
        try:
            self.db.conectar()
            query = "SELECT * FROM RENTAS WHERE Estado = 'Vencida' ORDER BY Fecha_Devolucion ASC"
            resultados = self.db.ejecutar_query(query)
            
            if resultados:
                return [Renta.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en listar_rentas_vencidas: {e}")
            return []
    
    def listar_rentas_por_cliente(self, id_cliente: int) -> List[Renta]:
        """Lista todas las rentas de un cliente."""
        try:
            self.db.conectar()
            query = "SELECT * FROM RENTAS WHERE Id_Cliente = %s ORDER BY Fecha_Renta DESC"
            resultados = self.db.ejecutar_query(query, (id_cliente,))
            
            if resultados:
                return [Renta.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en listar_rentas_por_cliente: {e}")
            return []
    
    def contar_rentas_activas(self) -> int:
        """Cuenta las rentas activas."""
        try:
            self.db.conectar()
            query = "SELECT COUNT(*) FROM RENTAS WHERE Estado = 'Activa'"
            resultado = self.db.ejecutar_query(query)
            
            if resultado:
                return resultado[0][0]
            return 0
        
        except Exception as e:
            print(f"❌ Error en contar_rentas_activas: {e}")
            return 0
    
    def actualizar_penalizacion_dia(self, nuevo_monto: float) -> Tuple[bool, str]:
        """
        Actualiza el monto de penalización por día.
        
        Args:
            nuevo_monto: Nuevo monto en pesos
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            if nuevo_monto < 0:
                return False, "El monto no puede ser negativo"
            
            self.db.conectar()
            query = "UPDATE CONFIGURACION SET Valor_Config = %s WHERE Nombre_Config = 'PENALIZACION_DIA'"
            filas = self.db.ejecutar_update(query, (f"{nuevo_monto:.2f}",))
            
            if filas and filas > 0:
                self.penalizacion_dia = nuevo_monto
                print(f"✅ Penalización actualizada a ${nuevo_monto:.2f}/día")
                return True, f"Penalización actualizada a ${nuevo_monto:.2f}/día"
            
            return False, "No se pudo actualizar la configuración"
        
        except Exception as e:
            print(f"❌ Error en actualizar_penalizacion_dia: {e}")
            return False, f"Error inesperado: {str(e)}"


# Ejemplo de uso
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJEMPLO DE USO - RentaController")
    print("="*60 + "\n")
    
    controller = RentaController()
    
    print(f"Penalización configurada: ${controller.penalizacion_dia:.2f}/día")
    
    # Marcar vencidas
    print("\n1. Marcando rentas vencidas...")
    vencidas = controller.marcar_rentas_vencidas()
    print(f"   Rentas marcadas: {vencidas}")
    
    # Contar activas
    print("\n2. Contando rentas activas...")
    activas = controller.contar_rentas_activas()
    print(f"   Rentas activas: {activas}")
    
    print("\n" + "="*60 + "\n")