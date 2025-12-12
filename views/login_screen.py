"""
Módulo: login_screen.py
Ubicación: views/login_screen.py
Descripción: Pantalla de inicio de sesión con CustomTkinter
Sistema: Mask N Go - Renta y Venta de Máscaras
Versión: 2.3 - Con recuperación de contraseña mediante pregunta de seguridad y diálogos centrados
"""
import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import json
from datetime import datetime, timedelta
import threading

# Agregar ruta raíz al path
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)

from controllers.auth_controller import AuthController
from utils.logger_config import setup_logger

# Configurar logging
logger = setup_logger('login_screen', 'logs/login_screen.log')


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
    COLOR_AMARILLO_AVISO = "#f59e0b"     # Avisos
    COLOR_VERDE_FUERTE = "#22c55e"       # Contraseña fuerte
    COLOR_NARANJA_MEDIO = "#f97316"      # Contraseña media
    COLOR_ROJO_DEBIL = "#ef4444"         # Contraseña débil
    
    # Configuración de seguridad
    MAX_INTENTOS_FALLIDOS = 5
    TIEMPO_BLOQUEO_SEGUNDOS = 300  # 5 minutos

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
        
        # Contador de intentos fallidos
        self.intentos_fallidos = {}
        self.bloqueos_activos = {}
        
        # Variables de estado
        self.estado_bloqueo = False
        self.tiempo_fin_bloqueo = None
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Cargar sesión si existe
        self.cargar_sesion_guardada()
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        width = 1200
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def cargar_sesion_guardada(self):
        """Carga sesión guardada si existe."""
        try:
            with open('session.json', 'r') as f:
                data = json.load(f)
                if data.get('remember_me', False):
                    usuario = data.get('usuario', '')
                    token = data.get('token', '')
                    
                    # Aquí puedes verificar si el token sigue siendo válido
                    # Por ahora, simplemente llenamos el campo
                    if usuario:
                        self.entry_usuario.insert(0, usuario)
                        self.checkbox_recordar.select()
                        
        except FileNotFoundError:
            logger.info("No hay sesión guardada")
        except Exception as e:
            logger.error(f"Error al cargar sesión guardada: {e}")
    
    def guardar_sesion(self, usuario: str, token: str = ""):
        """Guarda sesión localmente si se marca 'Recordarme'."""
        if hasattr(self, 'checkbox_recordar') and self.checkbox_recordar.get():
            try:
                data = {
                    'usuario': usuario,
                    'token': token,
                    'remember_me': True,
                    'timestamp': datetime.now().isoformat()
                }
                with open('session.json', 'w') as f:
                    json.dump(data, f)
                logger.info(f"Sesión guardada para usuario: {usuario}")
            except Exception as e:
                logger.error(f"Error al guardar sesión: {e}")
    
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
        
        # ==================== CAMPO USUARIO (no email) ====================
        user_label = ctk.CTkLabel(
            form_frame,
            text="Usuario",
            font=("Arial", 14),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            anchor="w"
        )
        user_label.pack(fill="x", pady=(0, 8))
        
        self.entry_usuario = ctk.CTkEntry(
            form_frame,
            width=400,
            height=50,
            placeholder_text="nombre_usuario",
            font=("Arial", 14),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_BORDE,
            placeholder_text_color=self.COLOR_TEXTO_SECUNDARIO,
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            border_width=2,
            corner_radius=8
        )
        self.entry_usuario.pack(pady=(0, 20))
        
        # ==================== VALIDACIÓN EN TIEMPO REAL USUARIO ====================
        self.label_validacion_usuario = ctk.CTkLabel(
            form_frame,
            text="",
            font=("Arial", 12),
            text_color=self.COLOR_AMARILLO_AVISO
        )
        self.label_validacion_usuario.pack(fill="x", pady=(0, 8))
        
        # Bind para validación en tiempo real
        self.entry_usuario.bind("<KeyRelease>", self.validar_usuario_en_tiempo_real)
        
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
        
        # ==================== INDICADOR DE FORTALEZA DE CONTRASEÑA ====================
        self.frame_fortaleza = ctk.CTkFrame(form_frame, fg_color="transparent", height=8)
        self.frame_fortaleza.pack(fill="x", pady=(0, 8))
        
        self.barra_fortaleza = ctk.CTkProgressBar(
            self.frame_fortaleza,
            height=8,
            width=400,
            mode="determinate"
        )
        self.barra_fortaleza.pack()
        
        self.label_fortaleza = ctk.CTkLabel(
            form_frame,
            text="Fortaleza de contraseña",
            font=("Arial", 12),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        )
        self.label_fortaleza.pack(fill="x", pady=(0, 8))
        
        # Bind para indicador de fortaleza
        self.entry_password.bind("<KeyRelease>", self.actualizar_fortaleza_contraseña)
        
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
        
        # ==================== CHECKBOX "RECUÉRDAME" ====================
        self.checkbox_recordar = ctk.CTkCheckBox(
            form_frame,
            text="Recuérdame en este dispositivo",
            font=("Arial", 12),
            text_color=self.COLOR_TEXTO_SECUNDARIO,
            fg_color=self.COLOR_MORADO_PRINCIPAL
        )
        self.checkbox_recordar.pack(pady=(0, 15))
        
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
        
        # ==================== SPINNER DE CARGA ====================
        self.spinner = ctk.CTkProgressBar(
            form_frame,
            height=5,
            width=400,
            mode="indeterminate"
        )
        self.spinner.pack_forget()  # Oculto por defecto
        
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
    
    def validar_usuario_en_tiempo_real(self, event):
        """Valida usuario mientras se escribe (no email, sino 4+ caracteres)."""
        usuario = self.entry_usuario.get().strip()
        
        if len(usuario) == 0:
            self.label_validacion_usuario.configure(text="", text_color=self.COLOR_TEXTO_SECUNDARIO)
            return
        
        # Validar longitud mínima de 4 caracteres
        if len(usuario) < 4:
            self.label_validacion_usuario.configure(
                text="⚠ Usuario debe tener al menos 4 caracteres", 
                text_color=self.COLOR_AMARILLO_AVISO
            )
        else:
            self.label_validacion_usuario.configure(
                text="✓ Usuario válido", 
                text_color=self.COLOR_EXITO
            )
    
    def actualizar_fortaleza_contraseña(self, event):
        """Actualiza la barra de fortaleza de contraseña."""
        password = self.entry_password.get()
        
        if len(password) == 0:
            self.barra_fortaleza.set(0)
            self.label_fortaleza.configure(text="Fortaleza de contraseña", text_color=self.COLOR_TEXTO_SECUNDARIO)
            return
        
        # Calcular fortaleza
        fortaleza = self.calcular_fortaleza_password(password)
        
        # Actualizar barra y color
        self.barra_fortaleza.set(fortaleza / 100)
        
        if fortaleza < 40:
            color = self.COLOR_ROJO_DEBIL
            texto = "Débil"
        elif fortaleza < 70:
            color = self.COLOR_NARANJA_MEDIO
            texto = "Media"
        else:
            color = self.COLOR_VERDE_FUERTE
            texto = "Fuerte"
        
        self.label_fortaleza.configure(text=f"Contraseña {texto}", text_color=color)
        self.barra_fortaleza.configure(progress_color=color)
    
    def calcular_fortaleza_password(self, password: str) -> float:
        """Calcula la fortaleza de una contraseña."""
        puntaje = 0
        
        # Longitud
        if len(password) >= 8:
            puntaje += 25
        elif len(password) >= 6:
            puntaje += 15
        else:
            puntaje += 5
        
        # Mayúsculas
        if any(c.isupper() for c in password):
            puntaje += 20
        
        # Minúsculas
        if any(c.islower() for c in password):
            puntaje += 20
        
        # Números
        if any(c.isdigit() for c in password):
            puntaje += 20
        
        # Caracteres especiales
        especiales = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in especiales for c in password):
            puntaje += 15
        
        return min(puntaje, 100)
    
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
        
        # Validar longitud de usuario
        if len(usuario) < 4:
            self.mostrar_mensaje("El usuario debe tener al menos 4 caracteres", tipo="error")
            return
        
        # Verificar bloqueo
        if self.esta_bloqueado(usuario):
            tiempo_restante = self.tiempo_para_desbloqueo(usuario)
            self.mostrar_mensaje(f"Cuenta bloqueada. Inténtalo en {tiempo_restante}s", tipo="error")
            logger.warning(f"Intento de login bloqueado para usuario: {usuario}")
            return
        
        # Mostrar spinner de carga
        self.spinner.pack(pady=(10, 0))
        self.spinner.start()
        
        # Deshabilitar botón durante la validación
        self.btn_login.configure(
            state="disabled", 
            text="Validando...",
            fg_color=self.COLOR_TEXTO_SECUNDARIO
        )
        self.update()
        
        # Validar credenciales en segundo plano
        threading.Thread(target=self._procesar_login, args=(usuario, password), daemon=True).start()
    
    def _procesar_login(self, usuario: str, password: str):
        """Procesa login en segundo plano."""
        try:
            # Intentar iniciar sesión
            exito, mensaje, usuario_obj = self.auth_controller.iniciar_sesion(
                usuario, 
                password
            )
            
            # Actualizar interfaz en el hilo principal
            self.after(0, lambda: self._finalizar_login(exito, mensaje, usuario_obj, usuario))
            
        except Exception as e:
            logger.error(f"Error en proceso de login: {e}")
            self.after(0, lambda: self._mostrar_error_login(usuario))
    
    def _finalizar_login(self, exito: bool, mensaje: str, usuario_obj, usuario: str):
        """Finaliza el proceso de login en el hilo principal."""
        # Ocultar spinner
        self.spinner.stop()
        self.spinner.pack_forget()
        
        if exito and usuario_obj:
            # Login exitoso
            self.mostrar_mensaje(
                f"¡Bienvenido, {usuario_obj.nombre_completo()}!",
                tipo="exito"
            )
            
            # Guardar sesión si está marcado "Recordarme"
            self.guardar_sesion(usuario, "")
            
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
            
            # Incrementar contador de intentos fallidos
            self.incrementar_intentos_fallidos(usuario)
            
            # Efecto visual de error
            self.efecto_shake()
    
    def _mostrar_error_login(self, usuario: str):
        """Muestra error de login."""
        # Ocultar spinner
        self.spinner.stop()
        self.spinner.pack_forget()
        
        self.mostrar_mensaje("Error de conexión. Inténtalo más tarde.", tipo="error")
        self.btn_login.configure(
            state="normal",
            text="Iniciar Sesión",
            fg_color=self.COLOR_MORADO_PRINCIPAL
        )
        
        # Incrementar contador de intentos fallidos por error
        self.incrementar_intentos_fallidos(usuario)
    
    def incrementar_intentos_fallidos(self, usuario: str):
        """Incrementa el contador de intentos fallidos."""
        ahora = datetime.now()
        
        if usuario not in self.intentos_fallidos:
            self.intentos_fallidos[usuario] = []
        
        # Agregar intento fallido
        self.intentos_fallidos[usuario].append(ahora)
        
        # Mantener solo los últimos 10 minutos
        self.intentos_fallidos[usuario] = [
            t for t in self.intentos_fallidos[usuario] 
            if (ahora - t).seconds < 600  # 10 minutos
        ]
        
        logger.warning(f"Intento fallido para usuario: {usuario}. Intentos recientes: {len(self.intentos_fallidos[usuario])}")
        
        # Verificar si debe bloquearse
        if len(self.intentos_fallidos[usuario]) >= self.MAX_INTENTOS_FALLIDOS:
            self.bloquear_usuario(usuario)
    
    def bloquear_usuario(self, usuario: str):
        """Bloquea temporalmente a un usuario."""
        ahora = datetime.now()
        fin_bloqueo = ahora + timedelta(seconds=self.TIEMPO_BLOQUEO_SEGUNDOS)
        
        self.bloqueos_activos[usuario] = fin_bloqueo
        
        logger.warning(f"Usuario bloqueado temporalmente: {usuario} hasta {fin_bloqueo}")
    
    def esta_bloqueado(self, usuario: str) -> bool:
        """Verifica si un usuario está bloqueado."""
        if usuario in self.bloqueos_activos:
            ahora = datetime.now()
            if ahora < self.bloqueos_activos[usuario]:
                return True
            else:
                # Bloqueo expirado, eliminar
                del self.bloqueos_activos[usuario]
        
        return False
    
    def tiempo_para_desbloqueo(self, usuario: str) -> int:
        """Obtiene segundos restantes para desbloqueo."""
        if usuario in self.bloqueos_activos:
            ahora = datetime.now()
            segundos = (self.bloqueos_activos[usuario] - ahora).seconds
            return max(0, segundos)
        return 0
    
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
        logger.info(f"Sesión iniciada exitosamente para usuario: {usuario_obj.usuario}")
        
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
            logger.error(f"Error de importación al abrir dashboard: {e}")
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
            logger.error(f"Error al abrir dashboard: {e}")
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
        """Flujo de recuperación de contraseña mediante pregunta de seguridad."""
        
        # Crear una ventana Toplevel personalizada
        dialog = ctk.CTkToplevel(self)
        dialog.title("Recuperar Contraseña")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self)  # Hacerla modal
        dialog.grab_set()  # Bloquear interacción con la ventana principal
        
        # Establecer el color de fondo a #1e293b
        dialog.configure(fg_color=self.COLOR_AZUL_OSCURO)
        
        # Centrar la ventana sobre la ventana principal
        self.update_idletasks()
        x_main = self.winfo_x()
        y_main = self.winfo_y()
        w_main = self.winfo_width()
        h_main = self.winfo_height()
        w_dialog = 400
        h_dialog = 250
        x = x_main + (w_main // 2) - (w_dialog // 2)
        y = y_main + (h_main // 2) - (h_dialog // 2)
        dialog.geometry(f"{w_dialog}x{h_dialog}+{x}+{y}")
        
        # Frame principal del diálogo
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Etiqueta de instrucción
        ctk.CTkLabel(
            main_frame,
            text="Ingresa tu nombre de usuario:",
            font=("Arial", 12),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(pady=(0, 15))
        
        # Campo de entrada para el nombre de usuario
        entry_usuario = ctk.CTkEntry(
            main_frame,
            width=300,
            height=35,
            font=("Arial", 12),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_BORDE,
            placeholder_text="nombre_usuario"
        )
        entry_usuario.pack(pady=(0, 20))
        entry_usuario.focus()  # Enfocar el campo al abrir el diálogo
        
        # Frame para los botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Botón Aceptar
        btn_aceptar = ctk.CTkButton(
            button_frame,
            text="Aceptar",
            width=100,
            height=35,
            font=("Arial", 12),
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=lambda: self._procesar_recuperacion(entry_usuario.get(), dialog)
        )
        btn_aceptar.pack(side="left", padx=5)
        
        # Botón Cancelar
        btn_cancelar = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            width=100,
            height=35,
            font=("Arial", 12),
            fg_color=self.COLOR_BORDE,
            hover_color="#475569",
            command=dialog.destroy
        )
        btn_cancelar.pack(side="right", padx=5)
        
        # Permitir presionar Enter para aceptar
        entry_usuario.bind("<Return>", lambda e: btn_aceptar.invoke())

    def _procesar_recuperacion(self, usuario_str, dialog):
        """Procesa la recuperación de contraseña después de que el usuario ingrese su nombre de usuario."""
        if not usuario_str:
            messagebox.showwarning("Advertencia", "Por favor, ingresa tu nombre de usuario.")
            return
        
        # Buscar al usuario
        usuario_obj = self.auth_controller.obtener_usuario_por_nombre(usuario_str)
        if not usuario_obj:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return
        
        # Verificar si tiene pregunta de seguridad
        if not usuario_obj.pregunta_seguridad or not usuario_obj.respuesta_seguridad:
            messagebox.showinfo(
                "Atención",
                "Este usuario no tiene pregunta de seguridad configurada.\n"
                "Contacta al administrador para restablecer tu contraseña."
            )
            dialog.destroy()
            return
        
        # Cerrar el primer diálogo
        dialog.destroy()
        
        # Abrir el segundo diálogo para la pregunta de seguridad
        self._mostrar_pregunta_seguridad(usuario_obj)

    def _mostrar_pregunta_seguridad(self, usuario_obj):
        """Muestra la pregunta de seguridad y pide la respuesta."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Pregunta de Seguridad")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Establecer el color de fondo a #1e293b
        dialog.configure(fg_color=self.COLOR_AZUL_OSCURO)
        
        # Centrar la ventana
        self.update_idletasks()
        x_main = self.winfo_x()
        y_main = self.winfo_y()
        w_main = self.winfo_width()
        h_main = self.winfo_height()
        w_dialog = 400
        h_dialog = 250
        x = x_main + (w_main // 2) - (w_dialog // 2)
        y = y_main + (h_main // 2) - (h_dialog // 2)
        dialog.geometry(f"{w_dialog}x{h_dialog}+{x}+{y}")
        
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mostrar la pregunta
        ctk.CTkLabel(
            main_frame,
            text=usuario_obj.pregunta_seguridad,
            font=("Arial", 12),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            wraplength=350
        ).pack(pady=(0, 15))
        
        # Frame para el campo de entrada y el botón de ver
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=(0, 20))
        
        # Campo de entrada para la respuesta (oculto por defecto)
        entry_respuesta = ctk.CTkEntry(
            input_frame,
            width=250,
            height=35,
            font=("Arial", 12),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_BORDE,
            show="*"  # Ocultar la respuesta
        )
        entry_respuesta.pack(side="left", padx=(0, 10))
        entry_respuesta.focus()
        
        # Variable para controlar si se muestra u oculta la respuesta
        mostrar_respuesta = [False]  # Usamos una lista para poder modificarla dentro de la función interna
        
        def toggle_visibility():
            """Alterna entre mostrar y ocultar la respuesta."""
            if mostrar_respuesta[0]:
                entry_respuesta.configure(show="*")
                btn_toggle.configure(text="👁️")
            else:
                entry_respuesta.configure(show="")
                btn_toggle.configure(text="🙈")
            mostrar_respuesta[0] = not mostrar_respuesta[0]
        
        # Botón para alternar visibilidad
        btn_toggle = ctk.CTkButton(
            input_frame,
            text="👁️",
            width=35,
            height=35,
            font=("Arial", 14),
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=toggle_visibility
        )
        btn_toggle.pack(side="left")
        
        # Frame para los botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Botón Aceptar
        btn_aceptar = ctk.CTkButton(
            button_frame,
            text="Aceptar",
            width=100,
            height=35,
            font=("Arial", 12),
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=lambda: self._verificar_respuesta(entry_respuesta.get(), usuario_obj, dialog)
        )
        btn_aceptar.pack(side="left", padx=5)
        
        # Botón Cancelar
        btn_cancelar = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            width=100,
            height=35,
            font=("Arial", 12),
            fg_color=self.COLOR_BORDE,
            hover_color="#475569",
            command=dialog.destroy
        )
        btn_cancelar.pack(side="right", padx=5)
        
        # Permitir presionar Enter para aceptar
        entry_respuesta.bind("<Return>", lambda e: btn_aceptar.invoke())

    def _verificar_respuesta(self, respuesta_str, usuario_obj, dialog):
        """Verifica la respuesta de seguridad y procede a cambiar la contraseña."""
        if not respuesta_str:
            messagebox.showwarning("Advertencia", "Por favor, ingresa la respuesta.")
            return
        
        # Verificar la respuesta
        if not self.auth_controller.verificar_respuesta_seguridad(usuario_obj.id_usuario, respuesta_str):
            messagebox.showerror("Error", "Respuesta incorrecta.")
            return
        
        # Cerrar el diálogo de pregunta
        dialog.destroy()
        
        # Abrir el tercer diálogo para ingresar la nueva contraseña
        self._mostrar_nueva_contrasena(usuario_obj)

    def _mostrar_nueva_contrasena(self, usuario_obj):
        """Muestra el diálogo para ingresar la nueva contraseña."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nueva Contraseña")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Establecer el color de fondo a #1e293b
        dialog.configure(fg_color=self.COLOR_AZUL_OSCURO)
        
        # Centrar la ventana
        self.update_idletasks()
        x_main = self.winfo_x()
        y_main = self.winfo_y()
        w_main = self.winfo_width()
        h_main = self.winfo_height()
        w_dialog = 400
        h_dialog = 300
        x = x_main + (w_main // 2) - (w_dialog // 2)
        y = y_main + (h_main // 2) - (h_dialog // 2)
        dialog.geometry(f"{w_dialog}x{h_dialog}+{x}+{y}")
        
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Instrucción
        ctk.CTkLabel(
            main_frame,
            text="Ingresa tu nueva contraseña:",
            font=("Arial", 12),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(pady=(0, 15))
        
        # Campo de nueva contraseña
        entry_nueva = ctk.CTkEntry(
            main_frame,
            width=300,
            height=35,
            font=("Arial", 12),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_BORDE,
            show="*"
        )
        entry_nueva.pack(pady=(0, 10))
        
        # Confirmación de contraseña
        ctk.CTkLabel(
            main_frame,
            text="Confirma tu nueva contraseña:",
            font=("Arial", 12),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(pady=(0, 15))
        
        entry_confirmar = ctk.CTkEntry(
            main_frame,
            width=300,
            height=35,
            font=("Arial", 12),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_BORDE,
            show="*"
        )
        entry_confirmar.pack(pady=(0, 20))
        
        # Frame para los botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Botón Aceptar
        btn_aceptar = ctk.CTkButton(
            button_frame,
            text="Aceptar",
            width=100,
            height=35,
            font=("Arial", 12),
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=lambda: self._actualizar_contrasena(entry_nueva.get(), entry_confirmar.get(), usuario_obj, dialog)
        )
        btn_aceptar.pack(side="left", padx=5)
        
        # Botón Cancelar
        btn_cancelar = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            width=100,
            height=35,
            font=("Arial", 12),
            fg_color=self.COLOR_BORDE,
            hover_color="#475569",
            command=dialog.destroy
        )
        btn_cancelar.pack(side="right", padx=5)
        
        # Permitir presionar Enter para aceptar
        entry_nueva.bind("<Return>", lambda e: entry_confirmar.focus())
        entry_confirmar.bind("<Return>", lambda e: btn_aceptar.invoke())

    def _actualizar_contrasena(self, nueva_pass, confirmar_pass, usuario_obj, dialog):
        """Actualiza la contraseña del usuario."""
        if not nueva_pass or not confirmar_pass:
            messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")
            return
        
        if nueva_pass != confirmar_pass:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
        
        if len(nueva_pass) < 6:
            messagebox.showwarning("Advertencia", "La contraseña debe tener al menos 6 caracteres.")
            return
        
        # Actualizar la contraseña
        exito, msg = self.auth_controller.actualizar_password_por_id(usuario_obj.id_usuario, nueva_pass)
        if exito:
            messagebox.showinfo("Éxito", "¡Contraseña actualizada!\nYa puedes iniciar sesión.")
            dialog.destroy()
        else:
            messagebox.showerror("Error", msg)

    def abrir_registro(self):
        """Abre la pantalla de registro de nuevos usuarios."""
        logger.info("Intento de acceso a registro")
        messagebox.showinfo(
            "Registro",
            "Funcionalidad en desarrollo.\n\n"
            "Contacta al administrador para crear tu cuenta."
        )
    
    def on_closing(self):
        """Maneja el evento de cierre de ventana."""
        if messagebox.askokcancel("Salir", "¿Deseas salir de la aplicación?"):
            logger.info("Aplicación cerrada por el usuario")
            if hasattr(self.auth_controller, 'cerrar_sesion'):
                self.auth_controller.cerrar_sesion()
            self.destroy()


# ==================== EJECUTAR APLICACIÓN ====================
if __name__ == "__main__":
    logger.info("Iniciando aplicación de login")
    
    try:
        app = LoginScreen()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        logger.critical(f"Error fatal en la aplicación: {e}")
        import traceback
        traceback.print_exc()