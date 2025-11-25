"""
Módulo: inventario_controller.py
Ubicación: controllers/inventario_controller.py
Descripción: Controlador para gestión de inventario de disfraces
Sistema: Renta y Venta de Disfraces
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
from models.disfraz import Disfraz
from utils.validadores import Validadores
from typing import Optional, Tuple, List


class InventarioController:
    """
    Controlador para manejar el inventario de disfraces.
    
    Gestiona:
    - CRUD completo de disfraces
    - Búsquedas múltiples (código, categoría, talla, nombre)
    - Control estricto de stock
    - Actualización de disponibilidad
    """
    
    def __init__(self):
        """Inicializa el controlador con conexión a BD."""
        self.db = ConexionDB()
    
    def agregar_disfraz(
        self,
        codigo_barras: str,
        descripcion: str,
        talla: str,
        color: str,
        categoria: str,
        precio_venta: float,
        precio_renta: float,
        stock: int
    ) -> Tuple[bool, str]:
        """
        Agrega un nuevo disfraz al inventario.
        
        Args:
            codigo_barras: Código único del disfraz
            descripcion: Nombre/descripción
            talla: Talla del disfraz
            color: Color principal
            categoria: Categoría
            precio_venta: Precio de venta
            precio_renta: Precio de renta diario
            stock: Cantidad inicial
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # 1. Validar código de barras
            valido, mensaje = Validadores.validar_codigo_barras(codigo_barras)
            if not valido:
                return False, mensaje
            
            # 2. Verificar que no exista
            if self.existe_codigo(codigo_barras):
                return False, f"El código '{codigo_barras}' ya existe en el inventario"
            
            # 3. Validar descripción
            valido, mensaje = Validadores.validar_descripcion(descripcion)
            if not valido:
                return False, mensaje
            
            # 4. Validar talla
            valido, mensaje = Validadores.validar_talla(talla)
            if not valido:
                return False, mensaje
            
            # 5. Validar precios
            valido, mensaje = Validadores.validar_precio(precio_venta, "precio de venta")
            if not valido:
                return False, mensaje
            
            valido, mensaje = Validadores.validar_precio(precio_renta, "precio de renta")
            if not valido:
                return False, mensaje
            
            # 6. Validar stock
            valido, mensaje = Validadores.validar_stock(stock)
            if not valido:
                return False, mensaje
            
            # 7. Insertar en BD
            self.db.conectar()
            query = """
                INSERT INTO INVENTARIO 
                (Codigo_Barras, Descripcion, Talla, Color, Categoria, 
                 Precio_Venta, Precio_Renta, Stock, Disponible, Estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Activo')
            """
            
            resultado = self.db.ejecutar_insert(
                query,
                (codigo_barras, descripcion, talla, color, categoria,
                 precio_venta, precio_renta, stock, stock)
            )
            
            if resultado is not None:
                print(f"✅ Disfraz '{descripcion}' agregado con código {codigo_barras}")
                return True, f"Disfraz agregado exitosamente"
            else:
                return False, "Error al agregar disfraz en la base de datos"
        
        except Exception as e:
            print(f"❌ Error en agregar_disfraz: {e}")
            return False, f"Error inesperado: {str(e)}"
    
    def editar_disfraz(
        self,
        codigo_barras: str,
        descripcion: Optional[str] = None,
        talla: Optional[str] = None,
        color: Optional[str] = None,
        categoria: Optional[str] = None,
        precio_venta: Optional[float] = None,
        precio_renta: Optional[float] = None,
        stock: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Edita un disfraz existente.
        
        Args:
            codigo_barras: Código del disfraz a editar
            descripcion: Nueva descripción (opcional)
            talla: Nueva talla (opcional)
            color: Nuevo color (opcional)
            categoria: Nueva categoría (opcional)
            precio_venta: Nuevo precio de venta (opcional)
            precio_renta: Nuevo precio de renta (opcional)
            stock: Nuevo stock total (opcional)
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # 1. Verificar que existe
            if not self.existe_codigo(codigo_barras):
                return False, f"No existe disfraz con código '{codigo_barras}'"
            
            # 2. Construir query dinámicamente
            campos = []
            valores = []
            
            if descripcion is not None:
                valido, mensaje = Validadores.validar_descripcion(descripcion)
                if not valido:
                    return False, mensaje
                campos.append("Descripcion = %s")
                valores.append(descripcion)
            
            if talla is not None:
                valido, mensaje = Validadores.validar_talla(talla)
                if not valido:
                    return False, mensaje
                campos.append("Talla = %s")
                valores.append(talla)
            
            if color is not None:
                campos.append("Color = %s")
                valores.append(color)
            
            if categoria is not None:
                campos.append("Categoria = %s")
                valores.append(categoria)
            
            if precio_venta is not None:
                valido, mensaje = Validadores.validar_precio(precio_venta, "precio de venta")
                if not valido:
                    return False, mensaje
                campos.append("Precio_Venta = %s")
                valores.append(precio_venta)
            
            if precio_renta is not None:
                valido, mensaje = Validadores.validar_precio(precio_renta, "precio de renta")
                if not valido:
                    return False, mensaje
                campos.append("Precio_Renta = %s")
                valores.append(precio_renta)
            
            if stock is not None:
                valido, mensaje = Validadores.validar_stock(stock)
                if not valido:
                    return False, mensaje
                campos.append("Stock = %s")
                valores.append(stock)
            
            if not campos:
                return False, "No se proporcionaron campos para actualizar"
            
            # 3. Ejecutar UPDATE
            valores.append(codigo_barras)
            query = f"UPDATE INVENTARIO SET {', '.join(campos)} WHERE Codigo_Barras = %s"
            
            self.db.conectar()
            filas = self.db.ejecutar_update(query, tuple(valores))
            
            if filas and filas > 0:
                print(f"✅ Disfraz '{codigo_barras}' actualizado")
                return True, "Disfraz actualizado exitosamente"
            else:
                return False, "No se pudo actualizar el disfraz"
        
        except Exception as e:
            print(f"❌ Error en editar_disfraz: {e}")
            return False, f"Error inesperado: {str(e)}"
    
    def eliminar_disfraz(self, codigo_barras: str) -> Tuple[bool, str]:
        """
        Elimina lógicamente un disfraz (marca como Inactivo).
        
        Args:
            codigo_barras: Código del disfraz a eliminar
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # 1. Verificar que existe
            if not self.existe_codigo(codigo_barras):
                return False, f"No existe disfraz con código '{codigo_barras}'"
            
            # 2. Marcar como Inactivo
            self.db.conectar()
            query = "UPDATE INVENTARIO SET Estado = 'Inactivo' WHERE Codigo_Barras = %s"
            filas = self.db.ejecutar_update(query, (codigo_barras,))
            
            if filas and filas > 0:
                print(f"✅ Disfraz '{codigo_barras}' eliminado (marcado como Inactivo)")
                return True, "Disfraz eliminado exitosamente"
            else:
                return False, "No se pudo eliminar el disfraz"
        
        except Exception as e:
            print(f"❌ Error en eliminar_disfraz: {e}")
            return False, f"Error inesperado: {str(e)}"
    
    def buscar_por_codigo(self, codigo_barras: str) -> Optional[Disfraz]:
        """
        Busca un disfraz por su código de barras.
        
        Args:
            codigo_barras: Código a buscar
        
        Returns:
            Optional[Disfraz]: Objeto Disfraz o None si no existe
        """
        try:
            self.db.conectar()
            query = "SELECT * FROM INVENTARIO WHERE Codigo_Barras = %s"
            resultados = self.db.ejecutar_query(query, (codigo_barras,))
            
            if resultados and len(resultados) > 0:
                return Disfraz.from_db_row(resultados[0])
            return None
        
        except Exception as e:
            print(f"❌ Error en buscar_por_codigo: {e}")
            return None
    
    def buscar_por_categoria(self, categoria: str) -> List[Disfraz]:
        """
        Busca disfraces por categoría.
        
        Args:
            categoria: Categoría a buscar
        
        Returns:
            List[Disfraz]: Lista de disfraces encontrados
        """
        try:
            self.db.conectar()
            query = """
                SELECT * FROM INVENTARIO 
                WHERE Categoria = %s AND Estado = 'Activo'
                ORDER BY Descripcion
            """
            resultados = self.db.ejecutar_query(query, (categoria,))
            
            if resultados:
                return [Disfraz.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en buscar_por_categoria: {e}")
            return []
    
    def buscar_por_talla(self, talla: str) -> List[Disfraz]:
        """
        Busca disfraces por talla.
        
        Args:
            talla: Talla a buscar
        
        Returns:
            List[Disfraz]: Lista de disfraces encontrados
        """
        try:
            self.db.conectar()
            query = """
                SELECT * FROM INVENTARIO 
                WHERE Talla = %s AND Estado = 'Activo'
                ORDER BY Descripcion
            """
            resultados = self.db.ejecutar_query(query, (talla.upper(),))
            
            if resultados:
                return [Disfraz.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en buscar_por_talla: {e}")
            return []
    
    def buscar_por_nombre(self, termino: str) -> List[Disfraz]:
        """
        Busca disfraces por nombre/descripción (búsqueda con LIKE).
        
        Args:
            termino: Término a buscar en la descripción
        
        Returns:
            List[Disfraz]: Lista de disfraces encontrados
        """
        try:
            self.db.conectar()
            query = """
                SELECT * FROM INVENTARIO 
                WHERE Descripcion LIKE %s AND Estado = 'Activo'
                ORDER BY Descripcion
            """
            patron = f"%{termino}%"
            resultados = self.db.ejecutar_query(query, (patron,))
            
            if resultados:
                return [Disfraz.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en buscar_por_nombre: {e}")
            return []
    
    def listar_disponibles(self) -> List[Disfraz]:
        """
        Lista todos los disfraces con stock disponible.
        
        Returns:
            List[Disfraz]: Lista de disfraces disponibles
        """
        try:
            self.db.conectar()
            query = """
                SELECT * FROM INVENTARIO 
                WHERE Disponible > 0 AND Estado = 'Activo'
                ORDER BY Categoria, Descripcion
            """
            resultados = self.db.ejecutar_query(query)
            
            if resultados:
                return [Disfraz.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en listar_disponibles: {e}")
            return []
    
    def listar_todos(self, incluir_inactivos: bool = False) -> List[Disfraz]:
        """
        Lista todos los disfraces del inventario.
        
        Args:
            incluir_inactivos: Si True, incluye los inactivos (default: False)
        
        Returns:
            List[Disfraz]: Lista de disfraces
        """
        try:
            self.db.conectar()
            if incluir_inactivos:
                query = "SELECT * FROM INVENTARIO ORDER BY Estado, Categoria, Descripcion"
                resultados = self.db.ejecutar_query(query)
            else:
                query = "SELECT * FROM INVENTARIO WHERE Estado = 'Activo' ORDER BY Categoria, Descripcion"
                resultados = self.db.ejecutar_query(query)
            
            if resultados:
                return [Disfraz.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en listar_todos: {e}")
            return []
    
    def verificar_disponibilidad(self, codigo_barras: str, cantidad: int) -> Tuple[bool, str, int]:
        """
        Verifica si hay suficiente stock disponible (control estricto).
        
        Args:
            codigo_barras: Código del disfraz
            cantidad: Cantidad requerida
        
        Returns:
            Tuple[bool, str, int]: (hay_stock, mensaje, disponible_actual)
        """
        try:
            disfraz = self.buscar_por_codigo(codigo_barras)
            
            if not disfraz:
                return False, f"No existe disfraz con código '{codigo_barras}'", 0
            
            if not disfraz.esta_activo():
                return False, f"El disfraz '{codigo_barras}' está inactivo", 0
            
            if disfraz.disponible < cantidad:
                return False, f"Stock insuficiente. Disponible: {disfraz.disponible}, Requerido: {cantidad}", disfraz.disponible
            
            return True, "Stock suficiente", disfraz.disponible
        
        except Exception as e:
            print(f"❌ Error en verificar_disponibilidad: {e}")
            return False, f"Error al verificar disponibilidad: {str(e)}", 0
    
    def descontar_stock(self, codigo_barras: str, cantidad: int) -> Tuple[bool, str]:
        """
        Descuenta stock disponible (para ventas/rentas).
        Implementa control estricto: no permite si no hay suficiente.
        
        Args:
            codigo_barras: Código del disfraz
            cantidad: Cantidad a descontar
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # 1. Verificar disponibilidad (control estricto)
            hay_stock, mensaje, disponible = self.verificar_disponibilidad(codigo_barras, cantidad)
            
            if not hay_stock:
                return False, mensaje
            
            # 2. Descontar stock
            self.db.conectar()
            query = """
                UPDATE INVENTARIO 
                SET Disponible = Disponible - %s 
                WHERE Codigo_Barras = %s
            """
            filas = self.db.ejecutar_update(query, (cantidad, codigo_barras))
            
            if filas and filas > 0:
                print(f"✅ Stock descontado: {cantidad} unidades de '{codigo_barras}'")
                return True, f"Stock actualizado correctamente"
            else:
                return False, "No se pudo actualizar el stock"
        
        except Exception as e:
            print(f"❌ Error en descontar_stock: {e}")
            return False, f"Error inesperado: {str(e)}"
    
    def aumentar_stock(self, codigo_barras: str, cantidad: int) -> Tuple[bool, str]:
        """
        Aumenta stock disponible (para devoluciones).
        
        Args:
            codigo_barras: Código del disfraz
            cantidad: Cantidad a aumentar
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # 1. Verificar que existe
            disfraz = self.buscar_por_codigo(codigo_barras)
            if not disfraz:
                return False, f"No existe disfraz con código '{codigo_barras}'"
            
            # 2. Aumentar stock
            self.db.conectar()
            query = """
                UPDATE INVENTARIO 
                SET Disponible = Disponible + %s 
                WHERE Codigo_Barras = %s
            """
            filas = self.db.ejecutar_update(query, (cantidad, codigo_barras))
            
            if filas and filas > 0:
                print(f"✅ Stock aumentado: {cantidad} unidades de '{codigo_barras}'")
                return True, f"Stock actualizado correctamente"
            else:
                return False, "No se pudo actualizar el stock"
        
        except Exception as e:
            print(f"❌ Error en aumentar_stock: {e}")
            return False, f"Error inesperado: {str(e)}"
    
    def existe_codigo(self, codigo_barras: str) -> bool:
        """
        Verifica si existe un disfraz con el código dado.
        
        Args:
            codigo_barras: Código a verificar
        
        Returns:
            bool: True si existe, False si no
        """
        try:
            self.db.conectar()
            query = "SELECT COUNT(*) FROM INVENTARIO WHERE Codigo_Barras = %s"
            resultados = self.db.ejecutar_query(query, (codigo_barras,))
            
            if resultados and resultados[0][0] > 0:
                return True
            return False
        
        except Exception as e:
            print(f"❌ Error en existe_codigo: {e}")
            return False


# Ejemplo de uso
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJEMPLO DE USO - InventarioController")
    print("="*60 + "\n")
    
    inventario = InventarioController()
    
    # Ejemplo 1: Agregar disfraz
    print("1. Agregando disfraz de prueba...")
    exito, msg = inventario.agregar_disfraz(
        codigo_barras="TEST001",
        descripcion="Disfraz de Prueba",
        talla="M",
        color="Azul",
        categoria="Test",
        precio_venta=500.00,
        precio_renta=100.00,
        stock=10
    )
    print(f"   {msg}\n")
    
    if exito:
        # Ejemplo 2: Buscar por código
        print("2. Buscando por código...")
        disfraz = inventario.buscar_por_codigo("TEST001")
        if disfraz:
            print(f"   Encontrado: {disfraz}\n")
        
        # Ejemplo 3: Verificar y descontar stock
        print("3. Descontando stock (control estricto)...")
        exito_stock, msg_stock = inventario.descontar_stock("TEST001", 3)
        print(f"   {msg_stock}\n")
        
        # Ejemplo 4: Eliminar (marcar como inactivo)
        print("4. Eliminando disfraz de prueba...")
        exito_del, msg_del = inventario.eliminar_disfraz("TEST001")
        print(f"   {msg_del}\n")
    
    print("="*60 + "\n")