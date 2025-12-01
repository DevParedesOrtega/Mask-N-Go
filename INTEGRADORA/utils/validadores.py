"""
Módulo: validadores.py
Ubicación: utils/validadores.py
Descripción: Funciones de validación reutilizables
Sistema: Renta y Venta de Disfraces
"""

import re
from typing import Tuple


class Validadores:
    """
    Clase con métodos estáticos para validar datos del sistema.
    
    Incluye validaciones para:
    - Usuarios
    - Contraseñas
    - Nombres
    - Roles
    - Códigos de barras
    - Precios
    - Stock
    - Teléfonos
    - Descripciones
    """
    
    @staticmethod
    def validar_usuario(usuario: str) -> Tuple[bool, str]:
        """
        Valida nombre de usuario.
        
        Reglas:
        - Mínimo 3 caracteres
        - Máximo 50 caracteres
        - Solo letras, números y guión bajo
        
        Args:
            usuario: Nombre de usuario a validar
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
        """
        if not usuario or len(usuario.strip()) == 0:
            return False, "El usuario no puede estar vacío"
        
        usuario = usuario.strip()
        
        if len(usuario) < 3:
            return False, "El usuario debe tener al menos 3 caracteres"
        
        if len(usuario) > 50:
            return False, "El usuario no puede exceder 50 caracteres"
        
        # Solo letras, números y guión bajo
        if not re.match(r'^[a-zA-Z0-9_]+$', usuario):
            return False, "El usuario solo puede contener letras, números y guión bajo"
        
        return True, "Usuario válido"
    
    @staticmethod
    def validar_password(password: str) -> Tuple[bool, str]:
        """
        Valida contraseña.
        
        Reglas:
        - Mínimo 6 caracteres
        - Máximo 100 caracteres
        
        Args:
            password: Contraseña a validar
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
        """
        if not password or len(password.strip()) == 0:
            return False, "La contraseña no puede estar vacía"
        
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        if len(password) > 100:
            return False, "La contraseña no puede exceder 100 caracteres"
        
        return True, "Contraseña válida"
    
    @staticmethod
    def validar_nombre(nombre: str) -> Tuple[bool, str]:
        """
        Valida nombres (de personas, no de disfraces).
        
        Reglas:
        - Mínimo 2 caracteres
        - Máximo 100 caracteres
        - Solo letras y espacios
        
        Args:
            nombre: Nombre a validar
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
        """
        if not nombre or len(nombre.strip()) == 0:
            return False, "El nombre no puede estar vacío"
        
        nombre = nombre.strip()
        
        if len(nombre) < 2:
            return False, "El nombre debe tener al menos 2 caracteres"
        
        if len(nombre) > 100:
            return False, "El nombre no puede exceder 100 caracteres"
        
        # Solo letras, espacios y acentos
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            return False, "El nombre solo puede contener letras y espacios"
        
        return True, "Nombre válido"
    
    @staticmethod
    def validar_rol(rol: str) -> Tuple[bool, str]:
        """
        Valida rol de usuario.
        
        Roles permitidos: 'admin', 'empleado'
        
        Args:
            rol: Rol a validar
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
        """
        roles_validos = ['admin', 'empleado']
        
        if not rol or len(rol.strip()) == 0:
            return False, "El rol no puede estar vacío"
        
        rol = rol.lower().strip()
        
        if rol not in roles_validos:
            return False, f"Rol inválido. Debe ser: {', '.join(roles_validos)}"
        
        return True, "Rol válido"
    
    @staticmethod
    def validar_codigo_barras(codigo: str) -> Tuple[bool, str]:
        """
        Valida código de barras.
        
        Reglas:
        - No puede estar vacío
        - Máximo 255 caracteres
        - Sin espacios
        
        Args:
            codigo: Código de barras a validar
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
        """
        if not codigo or len(codigo.strip()) == 0:
            return False, "El código de barras no puede estar vacío"
        
        codigo = codigo.strip()
        
        if ' ' in codigo:
            return False, "El código de barras no puede contener espacios"
        
        if len(codigo) > 255:
            return False, "El código de barras no puede exceder 255 caracteres"
        
        return True, "Código de barras válido"
    
    @staticmethod
    def validar_descripcion(descripcion: str) -> Tuple[bool, str]:
        """
        Valida descripción de disfraces.
        
        Reglas:
        - Mínimo 3 caracteres
        - Máximo 500 caracteres
        
        Args:
            descripcion: Descripción a validar
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
        """
        if not descripcion or len(descripcion.strip()) == 0:
            return False, "La descripción no puede estar vacía"
        
        descripcion = descripcion.strip()
        
        if len(descripcion) < 3:
            return False, "La descripción debe tener al menos 3 caracteres"
        
        if len(descripcion) > 500:
            return False, "La descripción no puede exceder 500 caracteres"
        
        return True, "Descripción válida"
    
    @staticmethod
    def validar_talla(talla: str) -> Tuple[bool, str]:
        """
        Valida talla de disfraz.
        
        Tallas válidas: XS, S, M, L, XL, XXL, UNI (unitalla)
        
        Args:
            talla: Talla a validar
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
        """
        tallas_validas = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'UNI']
        
        if not talla or len(talla.strip()) == 0:
            return False, "La talla no puede estar vacía"
        
        talla = talla.upper().strip()
        
        if talla not in tallas_validas:
            return False, f"Talla inválida. Debe ser: {', '.join(tallas_validas)}"
        
        return True, "Talla válida"
    
    @staticmethod
    def validar_precio(precio: float, nombre_campo: str = "precio") -> Tuple[bool, str]:
        """
        Valida precios.
        
        Reglas:
        - Debe ser número
        - Mayor o igual a 0
        - Máximo 2 decimales
        
        Args:
            precio: Precio a validar
            nombre_campo: Nombre del campo para mensajes (default: "precio")
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
        """
        try:
            precio = float(precio)
        except (ValueError, TypeError):
            return False, f"El {nombre_campo} debe ser un número válido"
        
        if precio < 0:
            return False, f"El {nombre_campo} no puede ser negativo"
        
        if precio > 999999.99:
            return False, f"El {nombre_campo} excede el límite permitido"
        
        return True, "Precio válido"
    
    @staticmethod
    def validar_stock(stock: int) -> Tuple[bool, str]:
        """
        Valida cantidad de stock.
        
        Reglas:
        - Debe ser número entero
        - Mayor o igual a 0
        
        Args:
            stock: Cantidad de stock a validar
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
        """
        try:
            stock = int(stock)
        except (ValueError, TypeError):
            return False, "El stock debe ser un número entero"
        
        if stock < 0:
            return False, "El stock no puede ser negativo"
        
        if stock > 9999:
            return False, "El stock excede el límite permitido (9999)"
        
        return True, "Stock válido"
    
    @staticmethod
    def validar_telefono(telefono: str) -> Tuple[bool, str]:
        """
        Valida número de teléfono (nacional e internacional).
        
        Reglas:
        - Mínimo 10 dígitos, máximo 15
        - Solo números (se permiten caracteres de formato)
        - Soporta formato internacional (+52, etc.)
        
        Args:
            telefono: Teléfono a validar
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
        """
        if not telefono or len(telefono.strip()) == 0:
            return False, "El teléfono no puede estar vacío"
        
        telefono_original = telefono.strip()
        
        # Remover caracteres de formato comunes
        telefono_limpio = telefono_original.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').replace('+', '')
        
        if not telefono_limpio.isdigit():
            return False, "El teléfono solo puede contener números y caracteres de formato (-, +, (), espacios)"
        
        if len(telefono_limpio) < 10:
            return False, "El teléfono debe tener al menos 10 dígitos"
        
        if len(telefono_limpio) > 15:
            return False, "El teléfono no puede exceder 15 dígitos"
        
        return True, "Teléfono válido"
    
    @staticmethod
    def validar_cantidad(cantidad: int, nombre_campo: str = "cantidad") -> Tuple[bool, str]:
        """
        Valida cantidades genéricas.
        
        Reglas:
        - Debe ser número entero
        - Mayor a 0
        
        Args:
            cantidad: Cantidad a validar
            nombre_campo: Nombre del campo para mensajes
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
        """
        try:
            cantidad = int(cantidad)
        except (ValueError, TypeError):
            return False, f"La {nombre_campo} debe ser un número entero"
        
        if cantidad <= 0:
            return False, f"La {nombre_campo} debe ser mayor a 0"
        
        if cantidad > 9999:
            return False, f"La {nombre_campo} excede el límite permitido"
        
        return True, "Cantidad válida"


# Ejemplo de uso
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJEMPLOS DE USO - Validadores")
    print("="*60 + "\n")
    
    # Prueba de validaciones
    print("1. Validar usuario:")
    valido, msg = Validadores.validar_usuario("juan123")
    print(f"   'juan123': {valido} - {msg}")
    
    print("\n2. Validar contraseña:")
    valido, msg = Validadores.validar_password("pass1234")
    print(f"   'pass1234': {valido} - {msg}")
    
    print("\n3. Validar nombre:")
    valido, msg = Validadores.validar_nombre("Juan Pérez")
    print(f"   'Juan Pérez': {valido} - {msg}")
    
    print("\n4. Validar talla:")
    valido, msg = Validadores.validar_talla("M")
    print(f"   'M': {valido} - {msg}")
    
    print("\n5. Validar precio:")
    valido, msg = Validadores.validar_precio(150.50, "precio de renta")
    print(f"   150.50: {valido} - {msg}")
    
    print("\n6. Validar teléfono:")
    valido, msg = Validadores.validar_telefono("6181234567")
    print(f"   '6181234567': {valido} - {msg}")
    
    print("\n" + "="*60 + "\n")