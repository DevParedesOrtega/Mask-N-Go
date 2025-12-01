"""
Módulo: formulario_usuarios.py
Ubicación: views/formulario_usuarios.py
Descripción: Formularios para gestión de usuarios (Agregar/Editar)
Sistema: Maskify - Renta y Venta de Máscaras
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)

from controllers.auth_controller import AuthController
from utils.validadores import Validadores


class FormularioUsuario(ctk.CTkToplevel):
    """
    Formulario modal para agregar o editar usuarios.
    
    Args:
        parent: Ventana padre
        usuario_obj: Objeto Usuario para editar (None si es nuevo)
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
    
    def __init__(self, parent, usuario_obj=None, callback=None):
        super().__init__(parent)
        
        self.auth_controller = AuthController()
        self.usuario_editando = usuario_obj
        self.callback = callback
        self.es_edicion = usuario_obj is not None
        
        # Configuración de la ventana
        titulo = "✏️ Editar Usuario" if self.es_edicion else "➕ Agregar Usuario"
        self.title(titulo)
        self.geometry("600x750")
        self.resizable(False, False)
        
        # Centrar ventana
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
        width = 600
        height = 750
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
        
        # Icono y título
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(expand=True)
        
        icono = "✏️" if self.es_edicion else "➕"
        titulo = "Editar Usuario" if self.es_edicion else "Nuevo Usuario"
        
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
        
        # Campo: Usuario
        self.crear_campo_input(
            form_container,
            "Usuario *",
            "usuario",
            "Ej: juan.perez o juan@email.com",
            "Nombre de usuario para iniciar sesión"
        )
        
        # Campo: Nombre
        self.crear_campo_input(
            form_container,
            "Nombre *",
            "nombre",
            "Ej: Juan",
            "Nombre(s) del usuario"
        )
        
        # Campo: Apellido Paterno
        self.crear_campo_input(
            form_container,
            "Apellido Paterno *",
            "apellido_paterno",
            "Ej: Pérez",
            "Apellido paterno del usuario"
        )
        
        # Campo: Contraseña (solo si es nuevo o si se quiere cambiar)
        if not self.es_edicion:
            self.crear_campo_password(
                form_container,
                "Contraseña *",
                "password",
                "Mínimo 6 caracteres"
            )
            
            self.crear_campo_password(
                form_container,
                "Confirmar Contraseña *",
                "password_confirm",
                "Debe coincidir con la contraseña"
            )
        else:
            # Checkbox para cambiar contraseña
            self.cambiar_password_var = ctk.BooleanVar(value=False)
            
            checkbox_frame = ctk.CTkFrame(form_container, fg_color="transparent")
            checkbox_frame.pack(fill="x", pady=(10, 0))
            
            ctk.CTkCheckBox(
                checkbox_frame,
                text="Cambiar contraseña",
                variable=self.cambiar_password_var,
                font=("Arial", 13),
                text_color=self.COLOR_TEXTO_PRINCIPAL,
                fg_color=self.COLOR_MORADO_PRINCIPAL,
                hover_color=self.COLOR_MORADO_HOVER,
                command=self.toggle_password_fields
            ).pack(anchor="w")
            
            # Frame para campos de contraseña (ocultos inicialmente)
            self.password_frame = ctk.CTkFrame(form_container, fg_color="transparent")
            
            self.crear_campo_password(
                self.password_frame,
                "Nueva Contraseña *",
                "password",
                "Mínimo 6 caracteres"
            )
            
            self.crear_campo_password(
                self.password_frame,
                "Confirmar Contraseña *",
                "password_confirm",
                "Debe coincidir con la contraseña"
            )
        
        # Campo: Rol
        self.crear_campo_rol(form_container)
        
        # Separador
        ctk.CTkFrame(
            form_container,
            height=1,
            fg_color=self.COLOR_AZUL_MUY_OSCURO
        ).pack(fill="x", pady=20)
        
        # Label de campos obligatorios
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
            wraplength=520
        )
        self.mensaje_label.pack(pady=10)
        
        # ==================== BOTONES ====================
        buttons_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Botón Cancelar
        ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            font=("Arial Bold", 14),
            width=250,
            height=45,
            fg_color="transparent",
            border_width=2,
            border_color=self.COLOR_TEXTO_SECUNDARIO,
            text_color=self.COLOR_TEXTO_SECUNDARIO,
            hover_color=self.COLOR_AZUL_MUY_OSCURO,
            command=self.cancelar
        ).pack(side="left", expand=True, padx=5)
        
        # Botón Guardar
        texto_boton = "Actualizar" if self.es_edicion else "Guardar"
        self.btn_guardar = ctk.CTkButton(
            buttons_frame,
            text=texto_boton,
            font=("Arial Bold", 14),
            width=250,
            height=45,
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=self.guardar_usuario
        )
        self.btn_guardar.pack(side="right", expand=True, padx=5)
    
    def crear_campo_input(self, parent, label, campo_id, placeholder, ayuda=None):
        """Crea un campo de entrada estándar."""
        # Frame contenedor
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
        
        # Texto de ayuda (opcional)
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
    
    def crear_campo_password(self, parent, label, campo_id, placeholder):
        """Crea un campo de contraseña con botón mostrar/ocultar."""
        # Frame contenedor
        campo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        campo_frame.pack(fill="x", pady=10)
        
        # Label
        ctk.CTkLabel(
            campo_frame,
            text=label,
            font=("Arial Bold", 13),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            anchor="w"
        ).pack(fill="x")
        
        # Frame para input y botón
        input_frame = ctk.CTkFrame(campo_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=(5, 0))
        
        # Input
        entry = ctk.CTkEntry(
            input_frame,
            height=45,
            placeholder_text=placeholder,
            show="•",
            font=("Arial", 13),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_TEXTO_SECUNDARIO,
            border_width=1,
            corner_radius=8
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Botón mostrar/ocultar
        btn_toggle = ctk.CTkButton(
            input_frame,
            text="👁️",
            width=45,
            height=45,
            font=("Arial", 16),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            hover_color=self.COLOR_TEXTO_SECUNDARIO,
            command=lambda: self.toggle_password_visibility(entry, btn_toggle)
        )
        btn_toggle.pack(side="right")
        
        # Guardar referencia
        setattr(self, f"entry_{campo_id}", entry)
        
        # Validación en tiempo real
        entry.bind("<KeyRelease>", lambda e: self.validar_campo_en_tiempo_real(campo_id))
    
    def crear_campo_rol(self, parent):
        """Crea el selector de rol."""
        campo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        campo_frame.pack(fill="x", pady=10)
        
        # Label
        ctk.CTkLabel(
            campo_frame,
            text="Rol *",
            font=("Arial Bold", 13),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            anchor="w"
        ).pack(fill="x")
        
        # ComboBox
        self.combo_rol = ctk.CTkComboBox(
            campo_frame,
            values=["empleado", "admin"],
            height=45,
            font=("Arial", 13),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_TEXTO_SECUNDARIO,
            button_color=self.COLOR_MORADO_PRINCIPAL,
            button_hover_color=self.COLOR_MORADO_HOVER,
            dropdown_fg_color=self.COLOR_AZUL_MUY_OSCURO,
            dropdown_hover_color=self.COLOR_MORADO_PRINCIPAL
        )
        self.combo_rol.pack(fill="x", pady=(5, 0))
        self.combo_rol.set("empleado")
    
    def toggle_password_visibility(self, entry, button):
        """Alterna la visibilidad de la contraseña."""
        if entry.cget("show") == "•":
            entry.configure(show="")
            button.configure(text="🙈")
        else:
            entry.configure(show="•")
            button.configure(text="👁️")
    
    def toggle_password_fields(self):
        """Muestra/oculta campos de contraseña en modo edición."""
        if self.cambiar_password_var.get():
            self.password_frame.pack(fill="x", pady=10)
        else:
            self.password_frame.pack_forget()
    
    def validar_campo_en_tiempo_real(self, campo_id):
        """Valida un campo mientras el usuario escribe."""
        entry = getattr(self, f"entry_{campo_id}")
        valor = entry.get().strip()
        
        # Cambiar color de borde según validación
        if not valor:
            entry.configure(border_color=self.COLOR_TEXTO_SECUNDARIO)
            return
        
        valido = True
        
        if campo_id == "usuario":
            valido, _ = Validadores.validar_usuario(valor)
        elif campo_id in ["nombre", "apellido_paterno"]:
            valido, _ = Validadores.validar_nombre(valor)
        elif campo_id == "password":
            valido, _ = Validadores.validar_password(valor)
        
        if valido:
            entry.configure(border_color=self.COLOR_EXITO)
        else:
            entry.configure(border_color=self.COLOR_ADVERTENCIA)
    
    def llenar_campos(self):
        """Llena los campos con datos del usuario a editar."""
        if not self.usuario_editando:
            return
        
        self.entry_usuario.insert(0, self.usuario_editando.usuario)
        self.entry_nombre.insert(0, self.usuario_editando.nombre)
        self.entry_apellido_paterno.insert(0, self.usuario_editando.apellido_paterno)
        self.combo_rol.set(self.usuario_editando.rol)
        
        # Deshabilitar campo usuario en edición (no se puede cambiar)
        self.entry_usuario.configure(state="disabled")
    
    def validar_formulario(self):
        """Valida todos los campos del formulario."""
        # Obtener valores
        usuario = self.entry_usuario.get().strip()
        nombre = self.entry_nombre.get().strip()
        apellido_paterno = self.entry_apellido_paterno.get().strip()
        rol = self.combo_rol.get()
        
        # Validar campos obligatorios
        if not usuario or not nombre or not apellido_paterno:
            self.mostrar_mensaje("Por favor, completa todos los campos obligatorios", "error")
            return False, None
        
        # Validar usuario
        valido, mensaje = Validadores.validar_usuario(usuario)
        if not valido:
            self.mostrar_mensaje(f"Usuario inválido: {mensaje}", "error")
            return False, None
        
        # Validar nombre
        valido, mensaje = Validadores.validar_nombre(nombre)
        if not valido:
            self.mostrar_mensaje(f"Nombre inválido: {mensaje}", "error")
            return False, None
        
        # Validar apellido
        valido, mensaje = Validadores.validar_nombre(apellido_paterno)
        if not valido:
            self.mostrar_mensaje(f"Apellido inválido: {mensaje}", "error")
            return False, None
        
        # Validar rol
        valido, mensaje = Validadores.validar_rol(rol)
        if not valido:
            self.mostrar_mensaje(f"Rol inválido: {mensaje}", "error")
            return False, None
        
        # Validar contraseñas
        password = None
        if not self.es_edicion:
            # Nuevo usuario: contraseña obligatoria
            password = self.entry_password.get().strip()
            password_confirm = self.entry_password_confirm.get().strip()
            
            if not password:
                self.mostrar_mensaje("La contraseña es obligatoria", "error")
                return False, None
            
            valido, mensaje = Validadores.validar_password(password)
            if not valido:
                self.mostrar_mensaje(f"Contraseña inválida: {mensaje}", "error")
                return False, None
            
            if password != password_confirm:
                self.mostrar_mensaje("Las contraseñas no coinciden", "error")
                return False, None
        
        else:
            # Edición: contraseña opcional
            if self.cambiar_password_var.get():
                password = self.entry_password.get().strip()
                password_confirm = self.entry_password_confirm.get().strip()
                
                if not password:
                    self.mostrar_mensaje("Ingresa la nueva contraseña", "error")
                    return False, None
                
                valido, mensaje = Validadores.validar_password(password)
                if not valido:
                    self.mostrar_mensaje(f"Contraseña inválida: {mensaje}", "error")
                    return False, None
                
                if password != password_confirm:
                    self.mostrar_mensaje("Las contraseñas no coinciden", "error")
                    return False, None
        
        # Todo válido
        datos = {
            "usuario": usuario,
            "nombre": nombre,
            "apellido_paterno": apellido_paterno,
            "password": password,
            "rol": rol
        }
        
        return True, datos
    
    def guardar_usuario(self):
        """Guarda o actualiza el usuario."""
        # Validar formulario
        valido, datos = self.validar_formulario()
        if not valido:
            return
        
        # Deshabilitar botón
        self.btn_guardar.configure(state="disabled", text="Guardando...")
        self.update()
        
        try:
            if self.es_edicion:
                # Actualizar usuario existente
                exito = self.actualizar_usuario(datos)
            else:
                # Crear nuevo usuario
                exito = self.crear_usuario(datos)
            
            if exito:
                # Llamar callback si existe
                if self.callback:
                    self.callback()
                
                # Cerrar ventana
                self.destroy()
        
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
            self.mostrar_mensaje(f"Error inesperado: {str(e)}", "error")
            self.btn_guardar.configure(state="normal", text="Guardar")
    
    def crear_usuario(self, datos):
        """Crea un nuevo usuario."""
        exito, mensaje, id_usuario = self.auth_controller.registrar_usuario(
            usuario=datos["usuario"],
            nombre=datos["nombre"],
            apellido_paterno=datos["apellido_paterno"],
            password=datos["password"],
            rol=datos["rol"]
        )
        
        if exito:
            # Mostrar notificación en el dashboard padre
            if hasattr(self.master, 'mostrar_notificacion'):
                self.master.mostrar_notificacion(
                    f"Usuario '{datos['usuario']}' creado exitosamente",
                    "exito"
                )
            return True
        else:
            self.mostrar_mensaje(mensaje, "error")
            self.btn_guardar.configure(state="normal", text="Guardar")
            return False
    
    def actualizar_usuario(self, datos):
        """Actualiza un usuario existente."""
        exito, mensaje = self.auth_controller.actualizar_usuario(
            id_usuario=self.usuario_editando.id_usuario,
            nombre=datos["nombre"],
            apellido_paterno=datos["apellido_paterno"],
            rol=datos["rol"],
            password=datos["password"]  # None si no se cambió
        )
        
        if exito:
            # Mostrar notificación en el dashboard padre
            if hasattr(self.master, 'mostrar_notificacion'):
                self.master.mostrar_notificacion(
                    f"Usuario '{self.usuario_editando.usuario}' actualizado exitosamente",
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
    root.title("Prueba Formulario Usuarios")
    root.geometry("400x300")
    
    ctk.set_appearance_mode("dark")
    
    def abrir_formulario_nuevo():
        FormularioUsuario(root, callback=lambda: print("Usuario guardado"))
    
    def abrir_formulario_editar():
        from models.usuario import Usuario
        from datetime import datetime
        
        usuario_test = Usuario(
            id_usuario=1,
            usuario="test_user",
            nombre="Usuario",
            apellido_paterno="De Prueba",
            password="test123",
            rol="empleado",
            fecha_registro=datetime.now()
        )
        
        FormularioUsuario(root, usuario_obj=usuario_test, callback=lambda: print("Usuario actualizado"))
    
    ctk.CTkButton(
        root,
        text="➕ Agregar Usuario",
        command=abrir_formulario_nuevo,
        height=50
    ).pack(pady=20, padx=50, fill="x")
    
    ctk.CTkButton(
        root,
        text="✏️ Editar Usuario",
        command=abrir_formulario_editar,
        height=50
    ).pack(pady=20, padx=50, fill="x")
    
    root.mainloop()