"""
Módulo: login_screen.py
Ubicación: views/login_screen.py
Descripción: Pantalla de inicio de sesión con CustomTkinter
Sistema: Maskify - Renta y Venta de Máscaras
"""

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont
import sys
import os

# Agregar ruta raíz al path
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)

from controllers.auth_controller import AuthController


class LoginScreen(ctk.CTk):
    """
    Ventana principal de inicio de sesión.
    Diseño basado en Figma de Maskify con paleta personalizada.
    """
    
    # PALETA DE COLORES (Personalizable)
    COLOR_MORADO_PRINCIPAL = "#7B68EE"  # Panel izquierdo y botón principal
    COLOR_MORADO_HOVER = "#6A59DD"      # Hover del botón
    COLOR_AZUL_OSCURO = "#1e293b"       # Fondo derecho
    COLOR_AZUL_MUY_OSCURO = "#0f172a"   # Fondo inputs
    COLOR_TEXTO_PRINCIPAL = "#ffffff"    # Texto principal
    COLOR_TEXTO_SECUNDARIO = "#94a3b8"   # Texto secundario/placeholders
    COLOR_BORDE = "#334155"              # Bordes de inputs
    COLOR_EXITO = "#10b981"              # Mensajes de éxito
    COLOR_ERROR = "#ef4444"              # Mensajes de error
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("Mask N Go - Inicio de Sesión")
        self.geometry("1200x700")
        self.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Controlador de autenticación
        self.auth_controller = AuthController()
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crear interfaz
        self.crear_interfaz()
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        width = 1200
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica de la pantalla de login."""
        
        # ==================== CONTENEDOR PRINCIPAL ====================
        main_frame = ctk.CTkFrame(self, fg_color=self.COLOR_AZUL_OSCURO)
        main_frame.pack(fill="both", expand=True)
        
        # ==================== PANEL IZQUIERDO (Decorativo) ====================
        left_panel = ctk.CTkFrame(
            main_frame,
            width=450,
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            corner_radius=0
        )
        left_panel.pack(side="left", fill="both")
        left_panel.pack_propagate(False)
        
        # Logo de máscaras (Comedy & Tragedy)
        logo_label = ctk.CTkLabel(
            left_panel,
            text="🎭",
            font=("Segoe UI Emoji", 140)
        )
        logo_label.place(relx=0.5, rely=0.35, anchor="center")
        
        # Nombre del sistema
        brand_label = ctk.CTkLabel(
            left_panel,
            text="Mask N Go",
            font=("Arial Bold", 56),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        )
        brand_label.place(relx=0.5, rely=0.55, anchor="center")
        
        # Slogan
        subtitle_label = ctk.CTkLabel(
            left_panel,
            text="Renta y venta de máscaras exclusivas",
            font=("Arial", 16),
            text_color="#f0f0f0"
        )
        subtitle_label.place(relx=0.5, rely=0.63, anchor="center")
        
        # ==================== PANEL DERECHO (Formulario) ====================
        right_panel = ctk.CTkFrame(
            main_frame,
            fg_color=self.COLOR_AZUL_OSCURO,
            corner_radius=0
        )
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Contenedor del formulario (centrado)
        form_frame = ctk.CTkFrame(
            right_panel,
            fg_color="transparent"
        )
        form_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # ==================== TÍTULO DEL FORMULARIO ====================
        title = ctk.CTkLabel(
            form_frame,
            text="Iniciar Sesión",
            font=("Arial Bold", 36),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        )
        title.pack(pady=(0, 8))
        
        subtitle = ctk.CTkLabel(
            form_frame,
            text="Ingresa tus credenciales para continuar",
            font=("Arial", 14),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        )
        subtitle.pack(pady=(0, 35))
        
        # ==================== CAMPO USUARIO ====================
        user_label = ctk.CTkLabel(
            form_frame,
            text="Correo electrónico",
            font=("Arial", 14),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            anchor="w"
        )
        user_label.pack(fill="x", pady=(0, 8))
        
        self.entry_usuario = ctk.CTkEntry(
            form_frame,
            width=400,
            height=50,
            placeholder_text="tu@email.com",
            font=("Arial", 14),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_BORDE,
            placeholder_text_color=self.COLOR_TEXTO_SECUNDARIO,
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            border_width=2,
            corner_radius=8
        )
        self.entry_usuario.pack(pady=(0, 20))
        
        # ==================== CAMPO CONTRASEÑA ====================
        pass_label = ctk.CTkLabel(
            form_frame,
            text="Contraseña",
            font=("Arial", 14),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            anchor="w"
        )
        pass_label.pack(fill="x", pady=(0, 8))
        
        self.entry_password = ctk.CTkEntry(
            form_frame,
            width=400,
            height=50,
            placeholder_text="••••••••",
            show="•",
            font=("Arial", 14),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_BORDE,
            placeholder_text_color=self.COLOR_TEXTO_SECUNDARIO,
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            border_width=2,
            corner_radius=8
        )
        self.entry_password.pack(pady=(0, 12))
        
        # ==================== OLVIDÉ MI CONTRASEÑA ====================
        forgot_button = ctk.CTkButton(
            form_frame,
            text="¿Olvidaste tu contraseña?",
            font=("Arial", 12),
            text_color=self.COLOR_MORADO_PRINCIPAL,
            fg_color="transparent",
            hover_color=self.COLOR_AZUL_MUY_OSCURO,
            width=100,
            command=self.recuperar_password
        )
        forgot_button.pack(pady=(0, 25))
        
        # ==================== BOTÓN INICIAR SESIÓN ====================
        self.btn_login = ctk.CTkButton(
            form_frame,
            text="Iniciar Sesión",
            width=400,
            height=50,
            font=("Arial Bold", 16),
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            corner_radius=8,
            command=self.iniciar_sesion
        )
        self.btn_login.pack(pady=(0, 25))
        
        # ==================== SEPARADOR ====================
        separator_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        separator_frame.pack(fill="x", pady=15)
        
        ctk.CTkFrame(
            separator_frame,
            height=1,
            fg_color=self.COLOR_BORDE
        ).pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        ctk.CTkLabel(
            separator_frame,
            text="o",
            text_color=self.COLOR_TEXTO_SECUNDARIO,
            font=("Arial", 12)
        ).pack(side="left")
        
        ctk.CTkFrame(
            separator_frame,
            height=1,
            fg_color=self.COLOR_BORDE
        ).pack(side="left", fill="x", expand=True, padx=(15, 0))
        
        # ==================== REGISTRARSE ====================
        register_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        register_frame.pack(pady=(10, 0))
        
        register_label = ctk.CTkLabel(
            register_frame,
            text="¿No tienes cuenta?  ",
            font=("Arial", 13),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        )
        register_label.pack(side="left")
        
        register_button = ctk.CTkButton(
            register_frame,
            text="Regístrate aquí",
            font=("Arial Bold", 13),
            text_color=self.COLOR_MORADO_PRINCIPAL,
            fg_color="transparent",
            hover_color=self.COLOR_AZUL_MUY_OSCURO,
            width=100,
            command=self.abrir_registro
        )
        register_button.pack(side="left")
        
        # ==================== LABEL DE ERROR/ÉXITO ====================
        self.mensaje_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=("Arial", 13),
            text_color=self.COLOR_ERROR
        )
        self.mensaje_label.pack(pady=(15, 0))
        
        # ==================== EVENTOS ====================
        # Permitir login con Enter
        self.entry_usuario.bind("<Return>", lambda e: self.entry_password.focus())
        self.entry_password.bind("<Return>", lambda e: self.iniciar_sesion())
        
        # Focus inicial en campo usuario
        self.after(100, lambda: self.entry_usuario.focus())
    
    def iniciar_sesion(self):
        """
        Maneja el proceso de inicio de sesión.
        Valida credenciales y redirige al dashboard.
        """
        # Limpiar mensaje previo
        self.mensaje_label.configure(text="")
        
        # Obtener credenciales
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        
        # Validar campos vacíos
        if not usuario or not password:
            self.mostrar_mensaje("Por favor, completa todos los campos", tipo="error")
            return
        
        # Deshabilitar botón durante la validación
        self.btn_login.configure(
            state="disabled", 
            text="Validando...",
            fg_color=self.COLOR_TEXTO_SECUNDARIO
        )
        self.update()
        
        # Intentar iniciar sesión
        exito, mensaje, usuario_obj = self.auth_controller.iniciar_sesion(
            usuario, 
            password
        )
        
        if exito and usuario_obj:
            # Login exitoso
            self.mostrar_mensaje(
                f"¡Bienvenido, {usuario_obj.nombre_completo()}!",
                tipo="exito"
            )
            
            # Esperar un momento y abrir dashboard
            self.after(1000, lambda: self.abrir_dashboard(usuario_obj))
        else:
            # Login fallido
            self.mostrar_mensaje(mensaje, tipo="error")
            self.btn_login.configure(
                state="normal",
                text="Iniciar Sesión",
                fg_color=self.COLOR_MORADO_PRINCIPAL
            )
            
            # Efecto visual de error
            self.efecto_shake()
    
    def mostrar_mensaje(self, texto: str, tipo: str = "error"):
        """
        Muestra un mensaje en la interfaz.
        
        Args:
            texto: Mensaje a mostrar
            tipo: 'error' o 'exito'
        """
        if tipo == "error":
            icono = "❌"
            color = self.COLOR_ERROR
        else:
            icono = "✅"
            color = self.COLOR_EXITO
        
        self.mensaje_label.configure(
            text=f"{icono} {texto}",
            text_color=color
        )
    
    def efecto_shake(self):
        """Efecto de vibración para indicar error."""
        # Cambiar borde de inputs a rojo
        self.entry_usuario.configure(border_color=self.COLOR_ERROR)
        self.entry_password.configure(border_color=self.COLOR_ERROR)
        
        # Restaurar después de 2 segundos
        self.after(2000, lambda: self.entry_usuario.configure(border_color=self.COLOR_BORDE))
        self.after(2000, lambda: self.entry_password.configure(border_color=self.COLOR_BORDE))
    
    def abrir_dashboard(self, usuario_obj):
        """
        Abre el dashboard moderno después del login exitoso.
        
        Args:
            usuario_obj: Objeto Usuario con datos de sesión
        """
        print(f"\n{'='*60}")
        print(f"🎭 SESIÓN INICIADA EXITOSAMENTE")
        print(f"{'='*60}")
        print(f"👤 Usuario: {usuario_obj.usuario}")
        print(f"📝 Nombre: {usuario_obj.nombre_completo()}")
        print(f"🎯 Rol: {usuario_obj.rol.upper()}")
        print(f"{'='*60}\n")
        
        try:
            # Ocultar ventana de login
            self.withdraw()
            
            # Importar y abrir dashboard moderno
            from views.dashboard_modern import DashboardModern
            dashboard = DashboardModern(usuario_obj)
            
            # Configurar evento de cierre del dashboard
            def on_dashboard_close():
                """Maneja el cierre del dashboard."""
                dashboard.destroy()
                self.destroy()  # Cerrar también el login
            
            dashboard.protocol("WM_DELETE_WINDOW", on_dashboard_close)
            dashboard.mainloop()
            
        except ImportError as e:
            print(f"❌ Error de importación: {e}")
            messagebox.showerror(
                "Error de Módulo",
                f"No se pudo cargar el dashboard moderno.\n\n"
                f"Asegúrate de que existe:\n"
                f"views/dashboard_modern.py\n\n"
                f"Error: {str(e)}"
            )
            self.deiconify()  # Mostrar login de nuevo
            self.btn_login.configure(
                state="normal",
                text="Iniciar Sesión",
                fg_color=self.COLOR_MORADO_PRINCIPAL
            )
        except Exception as e:
            print(f"❌ Error al abrir dashboard: {e}")
            import traceback
            traceback.print_exc()
            
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el dashboard:\n{str(e)}"
            )
            self.deiconify()  # Mostrar login de nuevo
            self.btn_login.configure(
                state="normal",
                text="Iniciar Sesión",
                fg_color=self.COLOR_MORADO_PRINCIPAL
            )
    
    def recuperar_password(self):
        """Abre el módulo de recuperación de contraseña."""
        messagebox.showinfo(
            "Recuperar Contraseña",
            "Funcionalidad en desarrollo.\n\n"
            "Contacta al administrador del sistema."
        )
    
    def abrir_registro(self):
        """Abre la pantalla de registro de nuevos usuarios."""
        messagebox.showinfo(
            "Registro",
            "Funcionalidad en desarrollo.\n\n"
            "Contacta al administrador para crear tu cuenta."
        )
    
    def on_closing(self):
        """Maneja el evento de cierre de ventana."""
        if messagebox.askokcancel("Salir", "¿Deseas salir de la aplicación?"):
            self.auth_controller.cerrar_sesion()
            self.destroy()


# ==================== EJECUTAR APLICACIÓN ====================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎭 Mask N Go - SISTEMA DE AUTENTICACIÓN")
    print("="*60 + "\n")
    
    try:
        app = LoginScreen()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()