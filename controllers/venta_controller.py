"""
Módulo: venta_controller.py
Ubicación: controllers/venta_controller.py
Descripción: Controlador para gestión de ventas
Sistema: Renta y Venta de Disfraces
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
from models.venta import Venta, DetalleVenta
from models.disfraz import Disfraz
from utils.validadores import Validadores
from typing import Optional, Tuple, List
from datetime import datetime


class VentaController:
    """
    Controlador para manejar ventas del sistema.
    
    Características:
    - Registro de ventas con validación completa
    - Descuentos con justificación obligatoria
    - Generación automática de folio único
    - Control transaccional de stock
    - Ventas inmutables (no se pueden editar)
    - Cancelación solo por Admin
    - Búsquedas y reportes detallados
    """
    
    def __init__(self):
        """Inicializa el controlador con conexión a BD."""
        self.db = ConexionDB()
    
    def generar_folio(self) -> str:
        """
        Genera un folio único para la venta.
        Formato: VEN-YYYYMMDD-####
        Ejemplo: VEN-20250121-0001
        
        Returns:
            str: Folio único generado
        """
        try:
            self.db.conectar()
            
            # Obtener el último folio del día
            fecha_hoy = datetime.now().strftime('%Y%m%d')
            query = """
                SELECT Folio FROM VENTAS 
                WHERE DATE(fecha_venta) = CURDATE() 
                ORDER BY Id_Venta DESC 
                LIMIT 1
            """
            resultado = self.db.ejecutar_query(query)
            
            if resultado and resultado[0][0]:
                ultimo_folio = resultado[0][0]
                # Extraer número y sumar 1
                numero = int(ultimo_folio.split('-')[-1]) + 1
            else:
                numero = 1
            
            folio = f"VEN-{fecha_hoy}-{numero:04d}"
            print(f"✅ Folio generado: {folio}")
            return folio
        
        except Exception as e:
            print(f"❌ Error al generar folio: {e}")
            # Folio de respaldo
            import random
            return f"VEN-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    
    def registrar_venta(
        self,
        id_cliente: int,
        id_usuario: int,
        detalles: List[dict],
        metodo_pago: str,
        descuento_porcentaje: float = 0.0,
        motivo_descuento: Optional[str] = None,
        motivo_venta: Optional[str] = None,
        notas: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Registra una nueva venta en el sistema.
        
        PROCESO TRANSACCIONAL:
        1. Valida todos los datos
        2. Verifica stock disponible
        3. Genera folio único
        4. Registra venta (header)
        5. Registra detalles
        6. Descuenta stock
        7. Commit o rollback completo
        
        Args:
            id_cliente: ID del cliente (obligatorio)
            id_usuario: ID del empleado que registra
            detalles: Lista de diccionarios:
                [{'codigo_barras': str, 'cantidad': int}, ...]
            metodo_pago: Forma de pago (Efectivo/tarjeta/Transferencia)
            descuento_porcentaje: Porcentaje de descuento (0-100)
            motivo_descuento: Justificación (obligatorio si hay descuento)
            motivo_venta: Evento especial (Halloween, etc.)
            notas: Observaciones adicionales
        
        Returns:
            Tuple[bool, str, Optional[int]]: (éxito, mensaje, id_venta)
        
        Example:
            >>> controller = VentaController()
            >>> detalles = [
            >>>     {'codigo_barras': 'DIS001', 'cantidad': 2},
            >>>     {'codigo_barras': 'DIS002', 'cantidad': 1}
            >>> ]
            >>> exito, msg, id = controller.registrar_venta(
            >>>     id_cliente=1,
            >>>     id_usuario=1,
            >>>     detalles=detalles,
            >>>     metodo_pago='Efectivo',
            >>>     descuento_porcentaje=10,
            >>>     motivo_descuento='Cliente frecuente'
            >>> )
        """
        cursor = None
        try:
            # 1. VALIDACIONES INICIALES
            if not detalles or len(detalles) == 0:
                return False, "La venta debe tener al menos un producto", None
            
            # Validar descuento
            if descuento_porcentaje < 0 or descuento_porcentaje > 100:
                return False, "El descuento debe estar entre 0% y 100%", None
            
            if descuento_porcentaje > 0 and not motivo_descuento:
                return False, "El descuento requiere justificación", None
            
            # Validar método de pago
            metodos_validos = ['Efectivo', 'tarjeta', 'Transferencia']
            if metodo_pago not in metodos_validos:
                return False, f"Método de pago inválido. Debe ser: {', '.join(metodos_validos)}", None
            
            # 2. CONECTAR Y PREPARAR TRANSACCIÓN
            self.db.conectar()
            cursor = self.db.connection.cursor()
            
            # 3. VALIDAR Y PREPARAR DETALLES
            from controllers.inventario_controller import InventarioController
            inv_controller = InventarioController()
            
            detalles_validados = []
            subtotal = 0.0
            
            for item in detalles:
                codigo = item.get('codigo_barras')
                cantidad = item.get('cantidad', 0)
                
                if not codigo or cantidad <= 0:
                    return False, f"Producto inválido: {item}", None
                
                # Verificar stock disponible
                hay_stock, msg_stock, disponible = inv_controller.verificar_disponibilidad(codigo, cantidad)
                if not hay_stock:
                    return False, msg_stock, None
                
                # Obtener disfraz con precio actual
                disfraz = inv_controller.buscar_por_codigo(codigo)
                if not disfraz:
                    return False, f"Disfraz '{codigo}' no encontrado", None
                
                if not disfraz.esta_activo():
                    return False, f"El disfraz '{codigo}' está inactivo y no se puede vender", None
                
                # Crear detalle con precio actual de BD
                detalle = DetalleVenta(
                    codigo_barras=codigo,
                    cantidad=cantidad,
                    precio_unitario=disfraz.precio_venta
                )
                
                detalles_validados.append(detalle)
                subtotal += detalle.subtotal
            
            # 4. CALCULAR TOTALES
            total_sin_descuento = subtotal
            descuento_monto = total_sin_descuento * (descuento_porcentaje / 100)
            total_final = total_sin_descuento - descuento_monto
            
            if total_final <= 0:
                return False, "El total de la venta debe ser mayor a 0", None
            
            # 5. GENERAR FOLIO
            folio = self.generar_folio()
            
            # 6. CREAR OBJETO VENTA
            venta = Venta(
                id_cliente=id_cliente,
                id_usuario=id_usuario,
                total=total_sin_descuento,
                metodo_pago=metodo_pago,
                folio=folio,
                descuento_porcentaje=descuento_porcentaje,
                descuento_monto=descuento_monto,
                motivo_descuento=motivo_descuento,
                motivo_venta=motivo_venta,
                notas=notas
            )
            
            venta.detalles = detalles_validados
            
            # Validación final
            valida, msg_val = venta.validar_venta()
            if not valida:
                return False, msg_val, None
            
            # 7. INSERTAR VENTA (HEADER)
            query_venta = """
                INSERT INTO VENTAS (
                    Folio, Id_cliente, Usuario_id, Total,
                    Descuento_Porcentaje, Descuento_Monto, Motivo_Descuento,
                    Motivo_Venta, Notas, metodo_pago, Estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Activa')
            """
            
            cursor.execute(query_venta, (
                folio, id_cliente, id_usuario, total_sin_descuento,
                descuento_porcentaje, descuento_monto, motivo_descuento,
                motivo_venta, notas, metodo_pago
            ))
            
            id_venta = cursor.lastrowid
            
            if not id_venta:
                self.db.connection.rollback()
                return False, "Error al registrar venta", None
            
            # 8. INSERTAR DETALLES Y DESCONTAR STOCK
            query_detalle = """
                INSERT INTO DETALLE_VENTAS (
                    Id_Venta, Codigo_Barras, Cantidad, Precio_Unitario, Subtotal
                ) VALUES (%s, %s, %s, %s, %s)
            """
            
            query_descontar = """
                UPDATE INVENTARIO 
                SET Stock = Stock - %s, Disponible = Disponible - %s 
                WHERE Codigo_Barras = %s
            """
            
            for detalle in detalles_validados:
                # Insertar detalle
                cursor.execute(query_detalle, (
                    id_venta,
                    detalle.codigo_barras,
                    detalle.cantidad,
                    detalle.precio_unitario,
                    detalle.subtotal
                ))
                
                # Descontar stock
                cursor.execute(query_descontar, (
                    detalle.cantidad,
                    detalle.cantidad,
                    detalle.codigo_barras
                ))
            
            # 9. COMMIT TRANSACCIÓN
            self.db.connection.commit()
            
            print(f"✅ Venta {folio} registrada exitosamente")
            print(f"   Total: ${total_final:.2f}")
            print(f"   Productos: {len(detalles_validados)}")
            
            return True, f"Venta {folio} registrada exitosamente", id_venta
        
        except Exception as e:
            if self.db.connection:
                self.db.connection.rollback()
            print(f"❌ Error en registrar_venta: {e}")
            return False, f"Error inesperado: {str(e)}", None
        
        finally:
            if cursor:
                cursor.close()
    
    def cancelar_venta(
        self,
        id_venta: int,
        id_usuario_admin: int,
        motivo_cancelacion: str
    ) -> Tuple[bool, str]:
        """
        Cancela una venta (solo Admin).
        
        PROCESO:
        1. Verifica que existe y está activa
        2. Verifica que usuario es Admin
        3. Devuelve el stock
        4. Marca como cancelada
        
        Args:
            id_venta: ID de la venta a cancelar
            id_usuario_admin: ID del admin que cancela
            motivo_cancelacion: Razón de la cancelación
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # 1. Verificar que la venta existe
            venta = self.buscar_por_id(id_venta)
            if not venta:
                return False, f"No existe venta con ID {id_venta}"
            
            if venta.esta_cancelada():
                return False, "La venta ya está cancelada"
            
            # 2. Verificar que usuario es Admin
            from controllers.auth_controller import AuthController
            auth = AuthController()
            usuario = auth.obtener_usuario_por_id(id_usuario_admin)
            
            if not usuario or not usuario.es_admin():
                return False, "Solo administradores pueden cancelar ventas"
            
            if not motivo_cancelacion or len(motivo_cancelacion.strip()) < 10:
                return False, "Debe proporcionar un motivo detallado (mínimo 10 caracteres)"
            
            # 3. CONECTAR Y USAR CONEXIÓN DIRECTA (sin cursor separado)
            self.db.conectar()
            
            # 4. Obtener detalles para devolver stock
            query_detalles = "SELECT Codigo_Barras, Cantidad FROM DETALLE_VENTAS WHERE Id_Venta = %s"
            detalles = self.db.ejecutar_query(query_detalles, (id_venta,))
            
            if not detalles:
                return False, "No se encontraron detalles de la venta"
            
            # 5. Devolver stock (ejecutar UPDATE directamente)
            for detalle in detalles:
                codigo_barras, cantidad = detalle
                query_devolver = """
                    UPDATE INVENTARIO 
                    SET Stock = Stock + %s, Disponible = Disponible + %s 
                    WHERE Codigo_Barras = %s
                """
                filas = self.db.ejecutar_update(query_devolver, (cantidad, cantidad, codigo_barras))
                print(f"   📦 Devueltos: {cantidad} unidades de '{codigo_barras}' (Filas afectadas: {filas})")
            
            # 6. Marcar venta como cancelada
            query_cancelar = """
                UPDATE VENTAS 
                SET Estado = 'Cancelada',
                    Cancelada_Por = %s,
                    Fecha_Cancelacion = NOW(),
                    Motivo_Cancelacion = %s
                WHERE Id_Venta = %s
            """
            self.db.ejecutar_update(query_cancelar, (id_usuario_admin, motivo_cancelacion, id_venta))
            
            print(f"✅ Venta {venta.folio} cancelada por Admin ID {id_usuario_admin}")
            print(f"   Stock devuelto correctamente")
            
            return True, f"Venta {venta.folio} cancelada exitosamente"
        
        except Exception as e:
            print(f"❌ Error en cancelar_venta: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error inesperado: {str(e)}"
    
    def buscar_por_id(self, id_venta: int) -> Optional[Venta]:
        """
        Busca una venta por su ID.
        
        Args:
            id_venta: ID de la venta
        
        Returns:
            Optional[Venta]: Objeto Venta o None
        """
        try:
            self.db.conectar()
            query = "SELECT * FROM VENTAS WHERE Id_Venta = %s"
            resultados = self.db.ejecutar_query(query, (id_venta,))
            
            if resultados and len(resultados) > 0:
                return Venta.from_db_row(resultados[0])
            return None
        
        except Exception as e:
            print(f"❌ Error en buscar_por_id: {e}")
            return None
    
    def buscar_por_folio(self, folio: str) -> Optional[Venta]:
        """Busca una venta por su folio."""
        try:
            self.db.conectar()
            query = "SELECT * FROM VENTAS WHERE Folio = %s"
            resultados = self.db.ejecutar_query(query, (folio,))
            
            if resultados and len(resultados) > 0:
                return Venta.from_db_row(resultados[0])
            return None
        
        except Exception as e:
            print(f"❌ Error en buscar_por_folio: {e}")
            return None
    
    def cargar_detalles(self, venta: Venta) -> bool:
        """
        Carga los detalles de una venta.
        
        Args:
            venta: Objeto Venta
        
        Returns:
            bool: True si se cargó correctamente
        """
        try:
            self.db.conectar()
            query = "SELECT * FROM DETALLE_VENTAS WHERE Id_Venta = %s"
            resultados = self.db.ejecutar_query(query, (venta.id_venta,))
            
            if resultados:
                for row in resultados:
                    detalle = DetalleVenta(
                        id_detalle=row[0],
                        id_venta=row[1],
                        codigo_barras=row[2],
                        cantidad=row[3],
                        precio_unitario=row[4]
                    )
                    venta.agregar_detalle(detalle)
                
                return True
            return False
        
        except Exception as e:
            print(f"❌ Error en cargar_detalles: {e}")
            return False
    
    def obtener_venta_completa(self, id_venta: int) -> Optional[Venta]:
        """Obtiene una venta con sus detalles cargados."""
        venta = self.buscar_por_id(id_venta)
        if venta:
            self.cargar_detalles(venta)
        return venta
    
    def listar_ventas_por_fecha(self, fecha: datetime) -> List[Venta]:
        """Lista ventas de un día específico."""
        try:
            self.db.conectar()
            query = "SELECT * FROM VENTAS WHERE DATE(fecha_venta) = %s ORDER BY fecha_venta DESC"
            resultados = self.db.ejecutar_query(query, (fecha.date(),))
            
            if resultados:
                return [Venta.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en listar_ventas_por_fecha: {e}")
            return []
    
    def listar_ventas_por_rango(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[Venta]:
        """Lista ventas en un rango de fechas."""
        try:
            self.db.conectar()
            query = """
                SELECT * FROM VENTAS 
                WHERE DATE(fecha_venta) BETWEEN %s AND %s 
                ORDER BY fecha_venta DESC
            """
            resultados = self.db.ejecutar_query(query, (fecha_inicio.date(), fecha_fin.date()))
            
            if resultados:
                return [Venta.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en listar_ventas_por_rango: {e}")
            return []
    
    def listar_ventas_por_cliente(self, id_cliente: int) -> List[Venta]:
        """Lista todas las ventas de un cliente."""
        try:
            self.db.conectar()
            query = "SELECT * FROM VENTAS WHERE Id_cliente = %s ORDER BY fecha_venta DESC"
            resultados = self.db.ejecutar_query(query, (id_cliente,))
            
            if resultados:
                return [Venta.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en listar_ventas_por_cliente: {e}")
            return []
    
    def total_ventas_dia(self, fecha: Optional[datetime] = None) -> float:
        """Calcula el total vendido en un día."""
        try:
            fecha = fecha or datetime.now()
            self.db.conectar()
            
            query = """
                SELECT COALESCE(SUM(Total - Descuento_Monto), 0)
                FROM VENTAS 
                WHERE DATE(fecha_venta) = %s AND Estado = 'Activa'
            """
            resultado = self.db.ejecutar_query(query, (fecha.date(),))
            
            if resultado:
                return float(resultado[0][0])
            return 0.0
        
        except Exception as e:
            print(f"❌ Error en total_ventas_dia: {e}")
            return 0.0
    
    def contar_ventas(self, fecha: Optional[datetime] = None) -> int:
        """Cuenta las ventas de un día."""
        try:
            fecha = fecha or datetime.now()
            self.db.conectar()
            
            query = """
                SELECT COUNT(*) 
                FROM VENTAS 
                WHERE DATE(fecha_venta) = %s AND Estado = 'Activa'
            """
            resultado = self.db.ejecutar_query(query, (fecha.date(),))
            
            if resultado:
                return resultado[0][0]
            return 0
        
        except Exception as e:
            print(f"❌ Error en contar_ventas: {e}")
            return 0


# Ejemplo de uso
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJEMPLO DE USO - VentaController")
    print("="*60 + "\n")
    
    controller = VentaController()
    
    # Ejemplo: Registrar venta
    print("1. Registrando venta de prueba...")
    detalles = [
        {'codigo_barras': 'TEST001', 'cantidad': 2}
    ]
    
    exito, msg, id_venta = controller.registrar_venta(
        id_cliente=1,
        id_usuario=1,
        detalles=detalles,
        metodo_pago='Efectivo',
        descuento_porcentaje=10,
        motivo_descuento='Cliente frecuente',
        motivo_venta='Halloween'
    )
    
    print(f"   {msg}\n")
    
    if exito and id_venta:
        # Obtener venta completa
        print("2. Obteniendo venta completa...")
        venta = controller.obtener_venta_completa(id_venta)
        if venta:
            print(f"\n{venta.resumen()}\n")
    
    print("="*60 + "\n")