"""
Módulo: inventario_screen.py
Ubicación: views/inventario_screen.py
Descripción: Pantalla completa de gestión de inventario
Sistema: Maskify - Renta y Venta de Máscaras
Versión: 1.1 - Corregido error al guardar: "too many values to unpack"
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)

from controllers.inventario_controller import InventarioController
from models.disfraz import Disfraz


class FormularioDisfraz(ctk.CTkToplevel):
    """
    Formulario modal para agregar o editar disfraces.
    
    Args:
        parent: Ventana padre
        disfraz_obj: Objeto Disfraz para editar (None si es nuevo)
        callback: Función a ejecutar después de guardar
    """
    
    # PALETA DE COLORES
    COLOR_MORADO_PRINCIPAL = "#7B68EE"
    COLOR_MORADO_HOVER = "#6A59DD"
    COLOR_AZUL_OSCURO = "#1e293b"
    COLOR_AZUL_MUY_OSCURO = "#0f172a"
    COLOR_TEXTO_PRINCIPAL = "#ffffff"
    COLOR_TEXTO_SECUNDARIO = "#94a3b8"
    COLOR_EXITO = "#10b981"
    COLOR_ERROR = "#ef4444"
    COLOR_ADVERTENCIA = "#fbbf24"
    
    def __init__(self, parent, disfraz_obj=None, callback=None):
        super().__init__(parent)
        
        self.inv_controller = InventarioController()
        self.disfraz_editando = disfraz_obj
        self.callback = callback
        self.es_edicion = disfraz_obj is not None
        
        # Configuración ventana
        titulo = "✏️ Editar Disfraz" if self.es_edicion else "➕ Agregar Disfraz"
        self.title(titulo)
        self.geometry("650x800")
        self.resizable(False, False)
        
        # Centrar
        self.center_window()
        
        # Configurar tema
        self.configure(fg_color=self.COLOR_AZUL_OSCURO)
        
        # Hacer modal
        self.transient(parent)
        self.grab_set()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Si es edición, llenar campos
        if self.es_edicion:
            self.llenar_campos()
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        width = 650
        height = 800
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def crear_interfaz(self):
        """Crea la interfaz del formulario."""
        
        # ==================== HEADER ====================
        header = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            height=100
        )
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(expand=True)
        
        icono = "✏️" if self.es_edicion else "➕"
        titulo = "Editar Disfraz" if self.es_edicion else "Nuevo Disfraz"
        
        ctk.CTkLabel(
            header_content,
            text=icono,
            font=("Arial", 40)
        ).pack(pady=(10, 0))
        
        ctk.CTkLabel(
            header_content,
            text=titulo,
            font=("Arial Bold", 24),
            text_color="white"
        ).pack()
        
        # ==================== FORMULARIO ====================
        form_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        form_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Código de Barras
        self.crear_campo_input(
            form_container,
            "Código de Barras *",
            "codigo_barras",
            "Ej: DIS001, MASK123",
            "Código único del producto"
        )
        
        # Descripción
        self.crear_campo_input(
            form_container,
            "Descripción *",
            "descripcion",
            "Ej: Spider-Man Clásico",
            "Nombre del disfraz/máscara"
        )
        
        # Talla
        self.crear_campo_talla(form_container)
        
        # Color
        self.crear_campo_input(
            form_container,
            "Color",
            "color",
            "Ej: Rojo/Azul, Negro",
            "Color principal"
        )
        
        # Categoría
        self.crear_campo_categoria(form_container)
        
        # Precio Venta
        self.crear_campo_input(
            form_container,
            "Precio de Venta *",
            "precio_venta",
            "Ej: 850.00",
            "Precio si se vende"
        )
        
        # Precio Renta
        self.crear_campo_input(
            form_container,
            "Precio de Renta (por día) *",
            "precio_renta",
            "Ej: 150.00",
            "Precio de renta diario"
        )
        
        # Stock
        self.crear_campo_input(
            form_container,
            "Stock Total *",
            "stock",
            "Ej: 10",
            "Cantidad total en inventario"
        )
        
        # Disponible (solo en edición)
        if self.es_edicion:
            self.crear_campo_input(
                form_container,
                "Disponible *",
                "disponible",
                "Ej: 7",
                "Cantidad actualmente disponible"
            )
        
        # Separador
        ctk.CTkFrame(
            form_container,
            height=1,
            fg_color=self.COLOR_AZUL_MUY_OSCURO
        ).pack(fill="x", pady=20)
        
        # Label campos obligatorios
        ctk.CTkLabel(
            form_container,
            text="* Campos obligatorios",
            font=("Arial", 11),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        ).pack(anchor="w", pady=(0, 10))
        
        # Mensaje de error/éxito
        self.mensaje_label = ctk.CTkLabel(
            form_container,
            text="",
            font=("Arial", 12),
            text_color=self.COLOR_ERROR,
            wraplength=570
        )
        self.mensaje_label.pack(pady=10)
        
        # ==================== BOTONES ====================
        buttons_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Cancelar
        ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            font=("Arial Bold", 14),
            width=280,
            height=45,
            fg_color="transparent",
            border_width=2,
            border_color=self.COLOR_TEXTO_SECUNDARIO,
            text_color=self.COLOR_TEXTO_SECUNDARIO,
            hover_color=self.COLOR_AZUL_MUY_OSCURO,
            command=self.cancelar
        ).pack(side="left", expand=True, padx=5)
        
        # Guardar
        texto_boton = "Actualizar" if self.es_edicion else "Guardar"
        self.btn_guardar = ctk.CTkButton(
            buttons_frame,
            text=texto_boton,
            font=("Arial Bold", 14),
            width=280,
            height=45,
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=self.guardar_disfraz
        )
        self.btn_guardar.pack(side="right", expand=True, padx=5)
    
    def crear_campo_input(self, parent, label, campo_id, placeholder, ayuda=None):
        """Crea un campo de entrada estándar."""
        campo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        campo_frame.pack(fill="x", pady=10)
        
        # Label
        label_frame = ctk.CTkFrame(campo_frame, fg_color="transparent")
        label_frame.pack(fill="x")
        
        ctk.CTkLabel(
            label_frame,
            text=label,
            font=("Arial Bold", 13),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            anchor="w"
        ).pack(side="left")
        
        if ayuda:
            ctk.CTkLabel(
                label_frame,
                text=f"  ℹ️ {ayuda}",
                font=("Arial", 10),
                text_color=self.COLOR_TEXTO_SECUNDARIO,
                anchor="w"
            ).pack(side="left")
        
        # Input
        entry = ctk.CTkEntry(
            campo_frame,
            height=45,
            placeholder_text=placeholder,
            font=("Arial", 13),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_TEXTO_SECUNDARIO,
            border_width=1,
            corner_radius=8
        )
        entry.pack(fill="x", pady=(5, 0))
        
        # Guardar referencia
        setattr(self, f"entry_{campo_id}", entry)
        
        # Validación en tiempo real
        entry.bind("<KeyRelease>", lambda e: self.validar_campo_en_tiempo_real(campo_id))
    
    def crear_campo_talla(self, parent):
        """Crea el selector de talla."""
        campo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        campo_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            campo_frame,
            text="Talla *",
            font=("Arial Bold", 13),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            anchor="w"
        ).pack(fill="x")
        
        self.combo_talla = ctk.CTkComboBox(
            campo_frame,
            values=["XS", "S", "M", "L", "XL", "XXL", "UNICA"],
            height=45,
            font=("Arial", 13),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_TEXTO_SECUNDARIO,
            button_color=self.COLOR_MORADO_PRINCIPAL,
            button_hover_color=self.COLOR_MORADO_HOVER,
            dropdown_fg_color=self.COLOR_AZUL_MUY_OSCURO,
            dropdown_hover_color=self.COLOR_MORADO_PRINCIPAL
        )
        self.combo_talla.pack(fill="x", pady=(5, 0))
        self.combo_talla.set("M")
    
    def crear_campo_categoria(self, parent):
        """Crea el selector de categoría."""
        campo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        campo_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            campo_frame,
            text="Categoría *",
            font=("Arial Bold", 13),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            anchor="w"
        ).pack(fill="x")
        
        self.combo_categoria = ctk.CTkComboBox(
            campo_frame,
            values=[
                "Mascaras",
                "Superheroes",
                "Terror",
                "Animales",
                "Profesiones",
                "Epoca",
                "Fantasia",
                "Otros"
            ],
            height=45,
            font=("Arial", 13),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_TEXTO_SECUNDARIO,
            button_color=self.COLOR_MORADO_PRINCIPAL,
            button_hover_color=self.COLOR_MORADO_HOVER,
            dropdown_fg_color=self.COLOR_AZUL_MUY_OSCURO,
            dropdown_hover_color=self.COLOR_MORADO_PRINCIPAL
        )
        self.combo_categoria.pack(fill="x", pady=(5, 0))
        self.combo_categoria.set("Mascaras")
    
    def validar_campo_en_tiempo_real(self, campo_id):
        """Valida un campo mientras el usuario escribe."""
        entry = getattr(self, f"entry_{campo_id}")
        valor = entry.get().strip()
        
        if not valor:
            entry.configure(border_color=self.COLOR_TEXTO_SECUNDARIO)
            return
        
        valido = True
        
        # Validaciones específicas
        if campo_id == "codigo_barras":
            valido = len(valor) >= 3 and len(valor) <= 50
        elif campo_id == "descripcion":
            valido = len(valor) >= 3 and len(valor) <= 200
        elif campo_id in ["precio_venta", "precio_renta"]:
            try:
                precio = float(valor)
                valido = precio > 0
            except:
                valido = False
        elif campo_id == "stock":
            try:
                stock = int(valor)
                valido = stock >= 0
            except:
                valido = False
        
        if valido:
            entry.configure(border_color=self.COLOR_EXITO)
        else:
            entry.configure(border_color=self.COLOR_ADVERTENCIA)
    
    def llenar_campos(self):
        """Llena los campos con datos del disfraz a editar."""
        if not self.disfraz_editando:
            return
        
        self.entry_codigo_barras.insert(0, self.disfraz_editando.codigo_barras)
        self.entry_descripcion.insert(0, self.disfraz_editando.descripcion)
        self.combo_talla.set(self.disfraz_editando.talla)
        self.entry_color.insert(0, self.disfraz_editando.color)
        self.combo_categoria.set(self.disfraz_editando.categoria)
        self.entry_precio_venta.insert(0, str(self.disfraz_editando.precio_venta))
        self.entry_precio_renta.insert(0, str(self.disfraz_editando.precio_renta))
        self.entry_stock.insert(0, str(self.disfraz_editando.stock))
        
        # Llenar disponible si existe el campo
        if hasattr(self, 'entry_disponible'):
            self.entry_disponible.insert(0, str(self.disfraz_editando.disponible))
        
        # Deshabilitar código en edición
        self.entry_codigo_barras.configure(state="disabled")
    
    def validar_formulario(self):
        """Valida todos los campos del formulario."""
        # Obtener valores
        codigo_barras = self.entry_codigo_barras.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        talla = self.combo_talla.get()
        color = self.entry_color.get().strip()
        categoria = self.combo_categoria.get()
        precio_venta_str = self.entry_precio_venta.get().strip()
        precio_renta_str = self.entry_precio_renta.get().strip()
        stock_str = self.entry_stock.get().strip()
        
        # Obtener disponible si existe (solo en edición)
        disponible_str = None
        if hasattr(self, 'entry_disponible'):
            disponible_str = self.entry_disponible.get().strip()
        
        # Validar campos obligatorios
        if not codigo_barras or not descripcion or not precio_venta_str or not precio_renta_str or not stock_str:
            self.mostrar_mensaje("Por favor, completa todos los campos obligatorios", "error")
            return False, None
        
        # Validar código
        if len(codigo_barras) < 3:
            self.mostrar_mensaje("El código debe tener al menos 3 caracteres", "error")
            return False, None
        
        # Validar descripción
        if len(descripcion) < 3:
            self.mostrar_mensaje("La descripción debe tener al menos 3 caracteres", "error")
            return False, None
        
        # Validar precios
        try:
            precio_venta = float(precio_venta_str)
            if precio_venta <= 0:
                self.mostrar_mensaje("El precio de venta debe ser mayor a 0", "error")
                return False, None
        except ValueError:
            self.mostrar_mensaje("Precio de venta inválido", "error")
            return False, None
        
        try:
            precio_renta = float(precio_renta_str)
            if precio_renta <= 0:
                self.mostrar_mensaje("El precio de renta debe ser mayor a 0", "error")
                return False, None
        except ValueError:
            self.mostrar_mensaje("Precio de renta inválido", "error")
            return False, None
        
        # Validar stock
        try:
            stock = int(stock_str)
            if stock < 0:
                self.mostrar_mensaje("El stock no puede ser negativo", "error")
                return False, None
        except ValueError:
            self.mostrar_mensaje("Stock inválido", "error")
            return False, None
        
        # Validar disponible (solo en edición)
        disponible = None
        if disponible_str:
            try:
                disponible = int(disponible_str)
                if disponible < 0:
                    self.mostrar_mensaje("El disponible no puede ser negativo", "error")
                    return False, None
                if disponible > stock:
                    self.mostrar_mensaje("El disponible no puede ser mayor que el stock total", "error")
                    return False, None
            except ValueError:
                self.mostrar_mensaje("Disponible inválido", "error")
                return False, None
        
        # Todo válido
        datos = {
            "codigo_barras": codigo_barras,
            "descripcion": descripcion,
            "talla": talla,
            "color": color if color else "N/A",
            "categoria": categoria,
            "precio_venta": precio_venta,
            "precio_renta": precio_renta,
            "stock": stock,
            "disponible": disponible  # None si es nuevo, int si es edición
        }
        
        return True, datos
    
    def guardar_disfraz(self):
        """Guarda o actualiza el disfraz."""
        # Validar formulario
        valido, datos = self.validar_formulario()
        if not valido:
            return
        
        # Deshabilitar botón
        self.btn_guardar.configure(state="disabled", text="Guardando...")
        self.update()
        
        try:
            if self.es_edicion:
                exito = self.actualizar_disfraz(datos)
            else:
                exito = self.crear_disfraz(datos)
            
            if exito:
                if self.callback:
                    self.callback()
                self.destroy()
        
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
            self.mostrar_mensaje(f"Error inesperado: {str(e)}", "error")
            self.btn_guardar.configure(state="normal", text="Guardar" if not self.es_edicion else "Actualizar")
    
    def crear_disfraz(self, datos):
        """Crea un nuevo disfraz."""
        resultado = self.inv_controller.agregar_disfraz(
            codigo_barras=datos["codigo_barras"],
            descripcion=datos["descripcion"],
            talla=datos["talla"],
            color=datos["color"],
            categoria=datos["categoria"],
            precio_venta=datos["precio_venta"],
            precio_renta=datos["precio_renta"],
            stock=datos["stock"]
        )
        
        # ✅ Manejo seguro del retorno
        if isinstance(resultado, tuple) and len(resultado) == 2:
            exito, mensaje = resultado
        else:
            exito = False
            mensaje = "Error interno: el sistema no devolvió una respuesta válida"
        
        if exito:
            if hasattr(self.master, 'mostrar_notificacion'):
                self.master.mostrar_notificacion(
                    f"Disfraz '{datos['descripcion']}' agregado exitosamente",
                    "exito"
                )
            return True
        else:
            self.mostrar_mensaje(mensaje, "error")
            self.btn_guardar.configure(state="normal", text="Guardar")
            return False
    
    def actualizar_disfraz(self, datos):
        """Actualiza un disfraz existente."""
        # Si hay disponible, actualizar también en BD directamente
        if datos["disponible"] is not None:
            from config.database import ConexionDB
            db = ConexionDB()
            db.conectar()
            
            query = """
                UPDATE INVENTARIO 
                SET Descripcion = %s, Talla = %s, Color = %s, Categoria = %s,
                    Precio_Venta = %s, Precio_Renta = %s, Stock = %s, Disponible = %s
                WHERE Codigo_Barras = %s
            """
            
            filas = db.ejecutar_update(
                query,
                (datos["descripcion"], datos["talla"], datos["color"], datos["categoria"],
                 datos["precio_venta"], datos["precio_renta"], datos["stock"], 
                 datos["disponible"], datos["codigo_barras"])
            )
            
            if filas and filas > 0:
                if hasattr(self.master, 'mostrar_notificacion'):
                    self.master.mostrar_notificacion(
                        f"Disfraz '{datos['descripcion']}' actualizado exitosamente",
                        "exito"
                    )
                return True
            else:
                self.mostrar_mensaje("No se pudo actualizar el disfraz", "error")
                self.btn_guardar.configure(state="normal", text="Actualizar")
                return False
        else:
            # Sin disponible, usar método normal del controlador
            resultado = self.inv_controller.editar_disfraz(
                codigo_barras=datos["codigo_barras"],
                descripcion=datos["descripcion"],
                talla=datos["talla"],
                color=datos["color"],
                categoria=datos["categoria"],
                precio_venta=datos["precio_venta"],
                precio_renta=datos["precio_renta"],
                stock=datos["stock"]
            )
            
            # ✅ Manejo seguro del retorno
            if isinstance(resultado, tuple) and len(resultado) == 2:
                exito, mensaje = resultado
            else:
                exito = False
                mensaje = "Error interno: el sistema no devolvió una respuesta válida"
            
            if exito:
                if hasattr(self.master, 'mostrar_notificacion'):
                    self.master.mostrar_notificacion(
                        f"Disfraz '{datos['descripcion']}' actualizado exitosamente",
                        "exito"
                    )
                return True
            else:
                self.mostrar_mensaje(mensaje, "error")
                self.btn_guardar.configure(state="normal", text="Actualizar")
                return False
    
    def mostrar_mensaje(self, texto, tipo="error"):
        """Muestra un mensaje en el formulario."""
        if tipo == "error":
            icono = "❌"
            color = self.COLOR_ERROR
        elif tipo == "exito":
            icono = "✅"
            color = self.COLOR_EXITO
        else:
            icono = "⚠️"
            color = self.COLOR_ADVERTENCIA
        
        self.mensaje_label.configure(
            text=f"{icono} {texto}",
            text_color=color
        )
    
    def cancelar(self):
        """Cancela y cierra el formulario."""
        confirmar = messagebox.askyesno(
            "Cancelar",
            "¿Deseas cancelar? Se perderán los cambios no guardados."
        )
        
        if confirmar:
            self.destroy()


# ==================== PRUEBA INDEPENDIENTE ====================
if __name__ == "__main__":
    # Crear ventana de prueba
    root = ctk.CTk()
    root.title("Prueba Formulario Inventario")
    root.geometry("500x400")
    
    ctk.set_appearance_mode("dark")
    
    # Logo
    ctk.CTkLabel(
        root,
        text="🎭",
        font=("Arial", 80)
    ).pack(pady=30)
    
    ctk.CTkLabel(
        root,
        text="Maskify - Inventario",
        font=("Arial Bold", 28),
        text_color="#7B68EE"
    ).pack()
    
    def abrir_formulario_nuevo():
        FormularioDisfraz(root, callback=lambda: print("✅ Disfraz guardado"))
    
    def abrir_formulario_editar():
        # Crear disfraz de prueba
        disfraz_test = Disfraz(
            codigo_barras="TEST001",
            descripcion="Spider-Man Clásico",
            talla="M",
            color="Rojo/Azul",
            categoria="Superheroes",
            precio_venta=850.00,
            precio_renta=150.00,
            stock=5,
            disponible=3
        )
        
        FormularioDisfraz(root, disfraz_obj=disfraz_test, callback=lambda: print("✅ Disfraz actualizado"))
    
    ctk.CTkButton(
        root,
        text="➕ Agregar Disfraz",
        command=abrir_formulario_nuevo,
        height=50,
        width=300,
        font=("Arial Bold", 14),
        fg_color="#7B68EE"
    ).pack(pady=10, padx=50)
    
    ctk.CTkButton(
        root,
        text="✏️ Editar Disfraz",
        command=abrir_formulario_editar,
        height=50,
        width=300,
        font=("Arial Bold", 14),
        fg_color="#fbbf24"
    ).pack(pady=10, padx=50)
    
    root.mainloop()