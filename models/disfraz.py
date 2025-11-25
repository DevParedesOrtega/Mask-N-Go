"""
Módulo: disfraz.py
Ubicación: models/disfraz.py
Descripción: Modelo de datos para disfraces del inventario
Sistema: Renta y Venta de Disfraces
"""

from typing import Optional


class Disfraz:
    """
    Clase que representa un disfraz en el inventario.
    
    Attributes:
        codigo_barras (str): Código único del disfraz (PK)
        descripcion (str): Nombre/descripción del disfraz
        talla (str): Talla del disfraz (S, M, L, XL, UNI)
        color (str): Color principal
        categoria (str): Categoría (Superhéroes, Terror, etc.)
        precio_venta (float): Precio de venta
        precio_renta (float): Precio de renta por día
        stock (int): Cantidad total en inventario
        disponible (int): Cantidad actualmente disponible
        estado (str): Estado del producto (Activo/Inactivo)
    """
    
    def __init__(
        self,
        codigo_barras: str,
        descripcion: str,
        talla: str,
        color: str,
        categoria: str,
        precio_venta: float,
        precio_renta: float,
        stock: int,
        disponible: Optional[int] = None,
        estado: str = 'Activo'
    ):
        """
        Constructor de la clase Disfraz.
        
        Args:
            codigo_barras: Código único del disfraz
            descripcion: Nombre/descripción
            talla: Talla del disfraz
            color: Color principal
            categoria: Categoría del disfraz
            precio_venta: Precio de venta
            precio_renta: Precio de renta diario
            stock: Cantidad total
            disponible: Cantidad disponible (default: igual a stock)
            estado: Estado del producto (default: 'Activo')
        """
        self.codigo_barras = codigo_barras
        self.descripcion = descripcion
        self.talla = talla
        self.color = color
        self.categoria = categoria
        self.precio_venta = float(precio_venta)
        self.precio_renta = float(precio_renta)
        self.stock = int(stock)
        self.disponible = int(disponible) if disponible is not None else int(stock)
        self.estado = estado
    
    def __str__(self) -> str:
        """
        Representación en texto del disfraz.
        
        Returns:
            str: Descripción del disfraz
        """
        return f"Disfraz({self.codigo_barras}, {self.descripcion}, Talla: {self.talla}, Stock: {self.disponible}/{self.stock})"
    
    def __repr__(self) -> str:
        """Representación técnica del objeto."""
        return self.__str__()
    
    def to_dict(self) -> dict:
        """
        Convierte el objeto Disfraz a diccionario.
        
        Returns:
            dict: Diccionario con los datos del disfraz
        """
        return {
            'codigo_barras': self.codigo_barras,
            'descripcion': self.descripcion,
            'talla': self.talla,
            'color': self.color,
            'categoria': self.categoria,
            'precio_venta': self.precio_venta,
            'precio_renta': self.precio_renta,
            'stock': self.stock,
            'disponible': self.disponible,
            'estado': self.estado
        }
    
    def esta_activo(self) -> bool:
        """
        Verifica si el disfraz está activo.
        
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
            bool: True si hay suficiente stock, False si no
        """
        return self.disponible >= cantidad
    
    def calcular_precio_renta(self, dias: int) -> float:
        """
        Calcula el precio total de renta por cantidad de días.
        
        Args:
            dias: Número de días de renta
        
        Returns:
            float: Precio total de renta
        """
        return self.precio_renta * dias
    
    def es_rentable(self) -> bool:
        """
        Determina si el disfraz está disponible para renta.
        
        Returns:
            bool: True si está activo y tiene stock disponible
        """
        return self.esta_activo() and self.disponible > 0
    
    def es_vendible(self) -> bool:
        """
        Determina si el disfraz está disponible para venta.
        
        Returns:
            bool: True si está activo y tiene stock disponible
        """
        return self.esta_activo() and self.disponible > 0
    
    @staticmethod
    def from_db_row(row: tuple) -> 'Disfraz':
        """
        Crea un objeto Disfraz desde una fila de la base de datos.
        
        Args:
            row: Tupla con datos de la BD
                 (Codigo_Barras, Descripcion, Talla, Color, Categoria,
                  Precio_Venta, Precio_Renta, Stock, Disponible, Estado)
        
        Returns:
            Disfraz: Objeto Disfraz creado
        """
        return Disfraz(
            codigo_barras=row[0],
            descripcion=row[1],
            talla=row[2],
            color=row[3],
            categoria=row[4],
            precio_venta=row[5],
            precio_renta=row[6],
            stock=row[7],
            disponible=row[8],
            estado=row[9]
        )


# Ejemplo de uso
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJEMPLO DE USO - Clase Disfraz")
    print("="*60 + "\n")
    
    # Crear disfraz
    disfraz = Disfraz(
        codigo_barras="DIS001",
        descripcion="Spider-Man Clásico",
        talla="M",
        color="Rojo/Azul",
        categoria="Superheroes",
        precio_venta=850.00,
        precio_renta=150.00,
        stock=5
    )
    
    print(f"Disfraz creado: {disfraz}")
    print(f"Está activo: {disfraz.esta_activo()}")
    print(f"Tiene stock para 3: {disfraz.tiene_stock(3)}")
    print(f"Precio renta 3 días: ${disfraz.calcular_precio_renta(3)}")
    print(f"Es rentable: {disfraz.es_rentable()}")
    print(f"\nDiccionario: {disfraz.to_dict()}")
    
    print("\n" + "="*60 + "\n")