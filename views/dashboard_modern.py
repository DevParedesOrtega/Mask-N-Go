"""
Módulo: dashboard_modern.py (VERSIÓN MODERNA v2.0)
Ubicación: views/dashboard_modern.py
Descripción: Dashboard moderno con tema oscuro + Usuario integrado para rentas
Sistema: Maskify - Renta y Venta de Máscaras
Versión: 2.0 - MEJORADO: Integrado id_usuario_actual para rentas_screen.py v3.0
"""


import customtkinter as ctk
from tkinter import messagebox
import sys
import os


ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)


from controllers.auth_controller import AuthController



class DashboardModern(ctk.CTk):
    """
    Dashboard moderno con tema oscuro y diseño minimalista.
    Layout: Sidebar compacto + Panel principal fluido
    Control de permisos por rol (admin/empleado)
    
    VERSIÓN 2.0:
    - Integración de id_usuario_actual para rentas_screen.py v3.0
    - Usuario cargado automáticamente al iniciar
    - Método cargar_usuario_actual() para login futuro
    """
    
    # PALETA DE COLORES (Tu paleta)
    COLOR_MORADO_PRINCIPAL = "#7B68EE"
    COLOR_MORADO_HOVER = "#6A59DD"
    COLOR_AZUL_OSCURO = "#1e293b"
    COLOR_AZUL_MUY_OSCURO = "#0f172a"
    COLOR_TEXTO_PRINCIPAL = "#ffffff"
    COLOR_TEXTO_SECUNDARIO = "#94a3b8"
    COLOR_FONDO_CARD = "#1e293b"
    COLOR_EXITO = "#10b981"
    COLOR_ADVERTENCIA = "#fbbf24"
    COLOR_INFO = "#3b82f6"
    COLOR_PELIGRO = "#ef4444"
    
    def __init__(self, usuario_obj):
        super().__init__()
        
        self.usuario = usuario_obj
        self.auth_controller = AuthController()
        self.auth_controller.sesion_activa = usuario_obj
        
        # ============================================================
        # OPCIÓN A: USUARIO ACTUAL PARA RENTAS (v2.0 NUEVO)
        # ============================================================
        # Guardar el OBJETO COMPLETO del usuario logueado
        self.usuario_actual_obj = usuario_obj          # ← Objeto Usuario completo
        self.id_usuario_actual = usuario_obj.id_usuario  # ← Solo el ID (para rentas)
        
        # Cargar usuario actual al iniciar
        self.id_usuario_actual = usuario_obj.id_usuario
        self.usuario_actual = usuario_obj.usuario
        print(f"✅ Usuario actual cargado: {usuario_obj.usuario} (ID: {usuario_obj.id_usuario})")
        
        # Variable para rastrear vista activa
        self.vista_actual = "inicio"
        
        # Configuración ventana
        self.title("Mask N Go - Dashboard Moderno")
        self.geometry("1400x800")
        self.resizable(True, True)
        self.center_window()
        
        # Tema oscuro
        ctk.set_appearance_mode("dark")
        
        # Crear interfaz
        self.crear_interfaz()
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        width = 1400
        height = 800
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def es_admin(self):
        """Verifica si el usuario actual es administrador."""
        return self.usuario.rol.lower() == 'admin'
    
    def cargar_usuario_actual(self, id_usuario: int, nombre_usuario: str):
        """
        Carga el usuario actual desde login (útil para futuros cambios de usuario).
        
        Args:
            id_usuario: ID del usuario desde BD
            nombre_usuario: Nombre de usuario (login)
        """
        self.id_usuario_actual = id_usuario
        self.usuario_actual = nombre_usuario
        print(f"✅ Usuario actual cargado: {nombre_usuario} (ID: {id_usuario})")
    
    def crear_interfaz(self):
        """Crea la interfaz completa del dashboard."""
        
        # ==================== SIDEBAR COMPACTO ====================
        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo header
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            height=80
        )
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            logo_frame,
            text="🎭 Mask N Go",
            font=("Arial Bold", 24),
            text_color="white"
        ).pack(pady=25)
        
        # Info usuario
        user_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        user_frame.pack(pady=20, padx=15)
        
        ctk.CTkLabel(
            user_frame,
            text="👤",
            font=("Arial", 32)
        ).pack()
        
        ctk.CTkLabel(
            user_frame,
            text=self.usuario.nombre_completo(),
            font=("Arial Bold", 14),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack()
        
        # Badge de rol
        rol_badge = ctk.CTkFrame(
            user_frame,
            fg_color=self.COLOR_MORADO_PRINCIPAL if self.es_admin() else self.COLOR_INFO,
            corner_radius=12
        )
        rol_badge.pack(pady=5)
        
        ctk.CTkLabel(
            rol_badge,
            text=f"🔑 {self.usuario.rol.upper()}",
            font=("Arial Bold", 10),
            text_color="white"
        ).pack(padx=10, pady=3)
        
        # Separador
        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=self.COLOR_AZUL_OSCURO
        ).pack(fill="x", padx=15, pady=10)
        
        # Menú de navegación
        self.crear_menu_navegacion()
        
        # Botón cerrar sesión
        ctk.CTkButton(
            self.sidebar,
            text="🚪 Cerrar Sesión",
            font=("Arial Bold", 13),
            fg_color=self.COLOR_PELIGRO,
            hover_color="#dc2626",
            height=40,
            command=self.cerrar_sesion
        ).pack(side="bottom", pady=20, padx=15, fill="x")
        
        # ==================== PANEL PRINCIPAL ====================
        self.main_panel = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_AZUL_OSCURO,
            corner_radius=0
        )
        self.main_panel.pack(side="right", fill="both", expand=True)
        
        # Header con gradiente visual
        self.crear_header()
        
        # Contenido scrollable
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_panel,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=25, pady=10)
        
        # Mostrar vista inicial
        self.mostrar_inicio()
    
    def crear_menu_navegacion(self):
        """Crea el menú de navegación del sidebar con permisos por rol."""
        # Menú para todos los usuarios
        menu_items = [
            ("🏠", "Dashboard", self.mostrar_inicio, "inicio"),
            ("📦", "Inventario", self.mostrar_inventario, "inventario"),
            ("🔄", "Rentas", self.mostrar_rentas, "rentas"),
            ("🛒", "Ventas", self.mostrar_ventas, "ventas"),
            ("👥", "Clientes", self.mostrar_clientes, "clientes"),
            ("💰", "Caja", self.mostrar_caja, "caja"),
        ]
        
        # Agregar Usuarios solo para Admin
        if self.es_admin():
            menu_items.append(("👨‍💼", "Usuarios", self.mostrar_usuarios, "usuarios"))
        
        # Agregar Configuración al final
        menu_items.append(("⚙️", "Configuración", self.mostrar_configuracion, "configuracion"))
        
        # Crear botones
        self.menu_buttons = {}
        for icono, texto, comando, key in menu_items:
            activo = (key == "inicio")
            
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icono}  {texto}",
                font=("Arial Bold" if activo else "Arial", 13),
                fg_color=self.COLOR_MORADO_PRINCIPAL if activo else "transparent",
                hover_color=self.COLOR_AZUL_OSCURO,
                text_color=self.COLOR_TEXTO_PRINCIPAL,
                anchor="w",
                height=45,
                command=lambda cmd=comando, k=key: self.cambiar_vista(cmd, k)
            )
            btn.pack(pady=3, padx=15, fill="x")
            self.menu_buttons[key] = btn
    
    def cambiar_vista(self, comando, key):
        """Cambia de vista y actualiza el menú activo."""
        # Desactivar todos los botones
        for btn_key, btn in self.menu_buttons.items():
            if btn_key == key:
                btn.configure(
                    fg_color=self.COLOR_MORADO_PRINCIPAL,
                    font=("Arial Bold", 13)
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    font=("Arial", 13)
                )
        
        self.vista_actual = key
        comando()
    
    def crear_header(self):
        """Crea el header superior."""
        header = ctk.CTkFrame(
            self.main_panel,
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            height=100
        )
        header.pack(fill="x", padx=25, pady=(25, 15))
        header.pack_propagate(False)
        
        # Título
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=25, pady=20)
        
        ctk.CTkLabel(
            title_frame,
            text=f"¡Hola, {self.usuario.nombre}! 👋",
            font=("Arial Bold", 28),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Aquí está el resumen de tu negocio hoy",
            font=("Arial", 14),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        ).pack(anchor="w")
        
        # Botones de acción rápida
        actions_frame = ctk.CTkFrame(header, fg_color="transparent")
        actions_frame.pack(side="right", padx=25)
        
        ctk.CTkButton(
            actions_frame,
            text="+ Nueva Renta",
            font=("Arial Bold", 13),
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            width=140,
            height=40,
            command=lambda: messagebox.showinfo("Renta", "Ir a la sección de Rentas para crear una nueva")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="🔔",
            font=("Arial", 18),
            width=40,
            height=40,
            fg_color=self.COLOR_FONDO_CARD,
            hover_color=self.COLOR_AZUL_OSCURO,
            command=lambda: messagebox.showinfo("Notificaciones", "Sin notificaciones nuevas")
        ).pack(side="left", padx=5)
    
    def limpiar_contenido(self):
        """Limpia el contenido del scroll frame."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
    
    def mostrar_inicio(self):
        """Muestra el panel de inicio con métricas."""
        self.limpiar_contenido()
        
        # ==================== MÉTRICAS PRINCIPALES ====================
        metrics_title = ctk.CTkLabel(
            self.scroll_frame,
            text="📊 Métricas Principales",
            font=("Arial Bold", 20),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        )
        metrics_title.pack(anchor="w", pady=(0, 15))
        
        metrics_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 25))
        
        metrics = [
            ("🎭", "127", "Máscaras", "+12 este mes", self.COLOR_MORADO_PRINCIPAL),
            ("📅", "24", "Rentas Activas", "3 nuevas hoy", self.COLOR_INFO),
            ("🛒", "8", "Ventas del Día", "$2,450 MXN", self.COLOR_EXITO),
            ("💵", "$4,250", "Ingresos", "↑ 23% vs ayer", self.COLOR_ADVERTENCIA),
        ]
        
        for i, (icono, valor, titulo, detalle, color) in enumerate(metrics):
            self.crear_metric_card(metrics_frame, icono, valor, titulo, detalle, color, i)
        
        # ==================== GRÁFICA DE RENTAS (Simulada) ====================
        chart_title = ctk.CTkLabel(
            self.scroll_frame,
            text="📈 Actividad de Rentas (Últimos 7 días)",
            font=("Arial Bold", 20),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        )
        chart_title.pack(anchor="w", pady=(15, 15))
        
        chart_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            corner_radius=15
        )
        chart_card.pack(fill="x", pady=(0, 25))
        
        # Simulación de gráfica con barras
        chart_content = ctk.CTkFrame(chart_card, fg_color="transparent")
        chart_content.pack(fill="both", expand=True, padx=30, pady=30)
        
        dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        valores = [12, 15, 8, 20, 18, 25, 22]
        
        bars_frame = ctk.CTkFrame(chart_content, fg_color="transparent")
        bars_frame.pack(fill="both", expand=True)
        
        for i, (dia, valor) in enumerate(zip(dias, valores)):
            bar_container = ctk.CTkFrame(bars_frame, fg_color="transparent")
            bar_container.pack(side="left", expand=True, padx=10)
            
            # Valor
            ctk.CTkLabel(
                bar_container,
                text=str(valor),
                font=("Arial Bold", 12),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            ).pack()
            
            # Barra (simulada con frame de altura variable)
            bar_height = valor * 5  # Escalar
            bar = ctk.CTkFrame(
                bar_container,
                width=40,
                height=bar_height,
                fg_color=self.COLOR_MORADO_PRINCIPAL,
                corner_radius=5
            )
            bar.pack(pady=5)
            
            # Día
            ctk.CTkLabel(
                bar_container,
                text=dia,
                font=("Arial", 11),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            ).pack()
        
        # ==================== TABLA DE RENTAS ====================
        table_title = ctk.CTkLabel(
            self.scroll_frame,
            text="🔄 Rentas Recientes",
            font=("Arial Bold", 20),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        )
        table_title.pack(anchor="w", pady=(15, 15))
        
        table_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            corner_radius=15
        )
        table_card.pack(fill="both", expand=True)
        
        # Headers
        headers_frame = ctk.CTkFrame(table_card, fg_color="transparent", height=50)
        headers_frame.pack(fill="x", padx=25, pady=(20, 10))
        
        headers = ["Cliente", "Máscara", "Fecha Renta", "Fecha Devolución", "Estado"]
        for header in headers:
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=("Arial Bold", 13),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            ).pack(side="left", expand=True)
        
        # Datos
        rentas_data = [
            ("Ana García", "Veneciana Dorada", "15/11/25", "22/11/25", "Activa", self.COLOR_EXITO),
            ("Carlos Ruiz", "Colombina Plata", "14/11/25", "21/11/25", "Activa", self.COLOR_EXITO),
            ("María López", "Bauta Negra", "13/11/25", "20/11/25", "Pendiente", self.COLOR_ADVERTENCIA),
            ("Juan Pérez", "Moretta Rosa", "12/11/25", "19/11/25", "Activa", self.COLOR_EXITO),
        ]
        
        for renta in rentas_data:
            self.crear_fila_moderna(table_card, renta)
    
    def mostrar_usuarios(self):
        """Muestra el módulo de gestión de usuarios (SOLO ADMIN)."""
        if not self.es_admin():
            messagebox.showerror(
                "Acceso Denegado",
                "No tienes permisos para acceder a este módulo.\n"
                "Solo los administradores pueden gestionar usuarios."
            )
            return
        
        self.limpiar_contenido()
        
        # ==================== HEADER DEL MÓDULO ====================
        header_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Título
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left")
        
        ctk.CTkLabel(
            title_container,
            text="👨‍💼 Gestión de Usuarios",
            font=("Arial Bold", 28),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_container,
            text="Administra los usuarios del sistema",
            font=("Arial", 14),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        ).pack(anchor="w")
        
        # Botón agregar usuario
        ctk.CTkButton(
            header_frame,
            text="+ Agregar Usuario",
            font=("Arial Bold", 14),
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            height=45,
            width=160,
            command=self.agregar_usuario
        ).pack(side="right")
        
        # ==================== ESTADÍSTICAS RÁPIDAS ====================
        stats_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # CRÍTICO: Consultar datos FRESCOS directamente de la BD
        usuarios_frescos = self.auth_controller.listar_usuarios()
        total_usuarios = len(usuarios_frescos)
        total_admins = len([u for u in usuarios_frescos if u.rol.lower() == 'admin'])
        total_empleados = len([u for u in usuarios_frescos if u.rol.lower() == 'empleado'])
        
        # Tarjetas de estadísticas
        stats_data = [
            ("👥", str(total_usuarios), "Total Usuarios", self.COLOR_INFO),
            ("👑", str(total_admins), "Administradores", self.COLOR_MORADO_PRINCIPAL),
            ("👤", str(total_empleados), "Empleados", self.COLOR_EXITO),
        ]
        
        for i, (icono, valor, titulo, color) in enumerate(stats_data):
            card = ctk.CTkFrame(
                stats_frame,
                fg_color=self.COLOR_AZUL_MUY_OSCURO,
                corner_radius=10
            )
            card.grid(row=0, column=i, padx=10, sticky="ew")
            stats_frame.columnconfigure(i, weight=1)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(pady=15, padx=20)
            
            # Icono
            icon_frame = ctk.CTkFrame(content, fg_color=color, width=40, height=40, corner_radius=8)
            icon_frame.pack(side="left", padx=(0, 15))
            icon_frame.pack_propagate(False)
            
            ctk.CTkLabel(
                icon_frame,
                text=icono,
                font=("Arial", 20)
            ).place(relx=0.5, rely=0.5, anchor="center")
            
            # Info
            info_frame = ctk.CTkFrame(content, fg_color="transparent")
            info_frame.pack(side="left")
            
            ctk.CTkLabel(
                info_frame,
                text=valor,
                font=("Arial Bold", 28),
                text_color=self.COLOR_TEXTO_PRINCIPAL
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                info_frame,
                text=titulo,
                font=("Arial", 12),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            ).pack(anchor="w")
        
        # ==================== TABLA DE USUARIOS ====================
        # Usar usuarios_frescos en lugar de consultar de nuevo
        if not usuarios_frescos:
            self.crear_placeholder("👥 No hay usuarios", "Agrega el primer usuario del sistema")
            return
        
        # Card contenedor
        table_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            corner_radius=15
        )
        table_card.pack(fill="both", expand=True)
        
        # Headers
        headers_frame = ctk.CTkFrame(table_card, fg_color="transparent", height=50)
        headers_frame.pack(fill="x", padx=25, pady=(20, 10))
        
        headers = ["ID", "Usuario", "Nombre Completo", "Rol", "Fecha Registro", "Acciones"]
        widths = [50, 200, 250, 120, 150, 150]
        
        for header, width in zip(headers, widths):
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=("Arial Bold", 13),
                text_color=self.COLOR_TEXTO_SECUNDARIO,
                width=width
            ).pack(side="left", padx=5)
        
        # Separador
        ctk.CTkFrame(
            table_card,
            height=1,
            fg_color=self.COLOR_AZUL_OSCURO
        ).pack(fill="x", padx=25, pady=5)
        
        # Filas de usuarios (usar datos frescos)
        for usuario in usuarios_frescos:
            self.crear_fila_usuario(table_card, usuario, widths)
    
    def crear_fila_usuario(self, parent, usuario, widths):
        """Crea una fila en la tabla de usuarios."""
        row = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        row.pack(fill="x", padx=25, pady=3)
        
        # ID
        ctk.CTkLabel(
            row,
            text=str(usuario.id_usuario),
            font=("Arial Bold", 12),
            text_color=self.COLOR_TEXTO_SECUNDARIO,
            width=widths[0]
        ).pack(side="left", padx=5)
        
        # Usuario
        ctk.CTkLabel(
            row,
            text=usuario.usuario,
            font=("Arial", 13),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            width=widths[1],
            anchor="w"
        ).pack(side="left", padx=5)
        
        # Nombre completo
        ctk.CTkLabel(
            row,
            text=usuario.nombre_completo(),
            font=("Arial", 13),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            width=widths[2],
            anchor="w"
        ).pack(side="left", padx=5)
        
        # Rol (badge)
        rol_color = self.COLOR_MORADO_PRINCIPAL if usuario.es_admin() else self.COLOR_INFO
        rol_badge = ctk.CTkFrame(row, fg_color=rol_color, corner_radius=15, width=widths[3])
        rol_badge.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            rol_badge,
            text=usuario.rol.upper(),
            font=("Arial Bold", 11),
            text_color="white"
        ).pack(padx=15, pady=8)
        
        # Fecha
        fecha_str = usuario.fecha_registro.strftime("%d/%m/%Y") if usuario.fecha_registro else "N/A"
        ctk.CTkLabel(
            row,
            text=fecha_str,
            font=("Arial", 12),
            text_color=self.COLOR_TEXTO_SECUNDARIO,
            width=widths[4]
        ).pack(side="left", padx=5)
        
        # Acciones
        actions_frame = ctk.CTkFrame(row, fg_color="transparent", width=widths[5])
        actions_frame.pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=35,
            height=35,
            font=("Arial", 14),
            fg_color=self.COLOR_INFO,
            hover_color="#2563eb",
            command=lambda u=usuario: self.editar_usuario(u)
        ).pack(side="left", padx=2)
        
        # No permitir eliminar el usuario actual
        if usuario.id_usuario != self.usuario.id_usuario:
            ctk.CTkButton(
                actions_frame,
                text="🗑️",
                width=35,
                height=35,
                font=("Arial", 14),
                fg_color=self.COLOR_PELIGRO,
                hover_color="#dc2626",
                command=lambda u=usuario: self.eliminar_usuario(u)
            ).pack(side="left", padx=2)
    
    def agregar_usuario(self):
        from views.formulario_usuarios import FormularioUsuario
        FormularioUsuario(self, self.usuario, callback=self.recargar_vista_usuarios)

    def editar_usuario(self, usuario):
        from views.formulario_usuarios import FormularioUsuario
        FormularioUsuario(self, self.usuario, usuario_obj=usuario, callback=self.recargar_vista_usuarios)
    
    def mostrar_notificacion(self, mensaje: str, tipo: str = "exito"):
        """
        Muestra una notificación temporal tipo toast.
        
        Args:
            mensaje: Mensaje a mostrar
            tipo: 'exito', 'error', 'info', 'advertencia'
        """
        # Colores según tipo
        colores = {
            "exito": self.COLOR_EXITO,
            "error": self.COLOR_PELIGRO,
            "info": self.COLOR_INFO,
            "advertencia": self.COLOR_ADVERTENCIA
        }
        
        iconos = {
            "exito": "✅",
            "error": "❌",
            "info": "ℹ️",
            "advertencia": "⚠️"
        }
        
        color = colores.get(tipo, self.COLOR_INFO)
        icono = iconos.get(tipo, "ℹ️")
        
        # Crear notificación
        notif = ctk.CTkFrame(
            self,
            fg_color=color,
            corner_radius=10,
            border_width=0
        )
        notif.place(relx=0.5, y=20, anchor="n")
        
        # Contenido
        content_frame = ctk.CTkFrame(notif, fg_color="transparent")
        content_frame.pack(padx=20, pady=12)
        
        ctk.CTkLabel(
            content_frame,
            text=f"{icono} {mensaje}",
            font=("Arial Bold", 14),
            text_color="white"
        ).pack()
        
        # Auto-ocultar después de 3 segundos
        self.after(3000, notif.destroy)
    
    def recargar_vista_usuarios(self):
        """Recarga la vista de usuarios con datos frescos de la BD."""
        print("\n🔄 RECARGANDO VISTA DE USUARIOS...")
        
        # Mostrar mensaje temporal
        self.limpiar_contenido()
        
        loading_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        loading_frame.pack(expand=True)
        
        ctk.CTkLabel(
            loading_frame,
            text="🔄",
            font=("Arial", 60)
        ).pack(pady=20)
        
        ctk.CTkLabel(
            loading_frame,
            text="Actualizando lista de usuarios...",
            font=("Arial Bold", 18),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack()
        
        # Forzar actualización de la UI
        self.update()
        
        # CRÍTICO: Crear nueva instancia del controlador para forzar consulta fresca
        print("📡 Creando nueva instancia de AuthController...")
        self.auth_controller = AuthController()
        self.auth_controller.sesion_activa = self.usuario
        print("✅ Nueva instancia creada\n")
        
        # Esperar un momento y recargar con datos frescos
        self.after(300, self.mostrar_usuarios)
    
    def eliminar_usuario(self, usuario):
        """Elimina un usuario del sistema."""
        confirmar = messagebox.askyesno(
            "Eliminar Usuario",
            f"¿Estás seguro de eliminar al usuario:\n\n"
            f"👤 {usuario.nombre_completo()}\n"
            f"📧 {usuario.usuario}\n"
            f"🎯 Rol: {usuario.rol}\n\n"
            f"⚠️ Esta acción no se puede deshacer."
        )
        
        if confirmar:
            try:
                # Eliminar usando el controlador
                exito, mensaje = self.auth_controller.eliminar_usuario(usuario.id_usuario)
                
                if exito:
                    # Mostrar notificación de éxito
                    self.mostrar_notificacion(
                        f"Usuario '{usuario.usuario}' eliminado correctamente",
                        "exito"
                    )
                    # Recargar vista con animación
                    self.recargar_vista_usuarios()
                else:
                    # Mostrar notificación de error
                    self.mostrar_notificacion(mensaje, "error")
            except Exception as e:
                print(f"❌ Error al eliminar: {e}")
                self.mostrar_notificacion(
                    f"Error al eliminar usuario: {str(e)}",
                    "error"
                )
    
    def crear_metric_card(self, parent, icono, valor, titulo, detalle, color, index):
        """Crea una tarjeta de métrica moderna."""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            corner_radius=15
        )
        card.grid(row=0, column=index, padx=8, sticky="ew")
        parent.columnconfigure(index, weight=1)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header con icono
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        icon_frame = ctk.CTkFrame(header, fg_color=color, width=45, height=45, corner_radius=10)
        icon_frame.pack(side="left")
        icon_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            icon_frame,
            text=icono,
            font=("Arial", 22)
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Valor principal
        ctk.CTkLabel(
            content,
            text=valor,
            font=("Arial Bold", 32),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(anchor="w", pady=(5, 0))
        
        # Título
        ctk.CTkLabel(
            content,
            text=titulo,
            font=("Arial", 13),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        ).pack(anchor="w")
        
        # Detalle
        ctk.CTkLabel(
            content,
            text=detalle,
            font=("Arial", 11),
            text_color=color
        ).pack(anchor="w", pady=(5, 0))
    
    def crear_fila_moderna(self, parent, datos):
        """Crea una fila moderna en la tabla."""
        row = ctk.CTkFrame(parent, fg_color="transparent", height=55)
        row.pack(fill="x", padx=25, pady=3)
        
        for i, dato in enumerate(datos[:-1]):
            if i == 4:  # Estado
                badge = ctk.CTkFrame(row, fg_color=datos[-1], corner_radius=15)
                badge.pack(side="left", expand=True, padx=5)
                
                ctk.CTkLabel(
                    badge,
                    text=dato,
                    font=("Arial Bold", 11),
                    text_color="white"
                ).pack(padx=12, pady=6)
            else:
                ctk.CTkLabel(
                    row,
                    text=dato,
                    font=("Arial", 13),
                    text_color=self.COLOR_TEXTO_PRINCIPAL
                ).pack(side="left", expand=True, padx=5)
    
    # Métodos de navegación (placeholders)
    def mostrar_inventario(self):
        """Muestra el módulo de gestión de inventario."""
        self.limpiar_contenido()
        
        # Importar controlador
        from controllers.inventario_controller import InventarioController
        inv_controller = InventarioController()
        
        # ==================== HEADER DEL MÓDULO ====================
        header_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Título
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left")
        
        ctk.CTkLabel(
            title_container,
            text="📦 Gestión de Inventario",
            font=("Arial Bold", 28),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(anchor="w")
        
        subtitulo_texto = "Administra máscaras y disfraces" if self.es_admin() else "Consulta de inventario (Solo lectura)"
        ctk.CTkLabel(
            title_container,
            text=subtitulo_texto,
            font=("Arial", 14),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        ).pack(anchor="w")
        
        # Botones de acción (SOLO ADMIN)
        if self.es_admin():
            actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            actions_frame.pack(side="right")
            
            ctk.CTkButton(
                actions_frame,
                text="+ Agregar Disfraz",
                font=("Arial Bold", 14),
                fg_color=self.COLOR_MORADO_PRINCIPAL,
                hover_color=self.COLOR_MORADO_HOVER,
                height=45,
                width=160,
                command=self.agregar_disfraz
            ).pack(side="left", padx=5)
        
        # ==================== BUSCADOR ====================
        search_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 20))
        
        self.entry_buscar_inv = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Buscar por nombre o código...",
            height=45,
            width=400,
            font=("Arial", 14),
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            border_color=self.COLOR_TEXTO_SECUNDARIO
        )
        self.entry_buscar_inv.pack(side="left", padx=(0, 10))
        self.entry_buscar_inv.bind("<Return>", lambda e: self.buscar_inventario())
        
        ctk.CTkButton(
            search_frame,
            text="Buscar",
            width=100,
            height=45,
            font=("Arial Bold", 14),
            fg_color=self.COLOR_INFO,
            hover_color="#2563eb",
            command=self.buscar_inventario
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            search_frame,
            text="Ver Todo",
            width=100,
            height=45,
            font=("Arial Bold", 14),
            fg_color=self.COLOR_TEXTO_SECUNDARIO,
            hover_color=self.COLOR_AZUL_OSCURO,
            command=self.mostrar_inventario
        ).pack(side="left")
        
        # ==================== ESTADÍSTICAS ====================
        stats_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Consultar datos frescos
        todos_disfraces = inv_controller.listar_disfraces(solo_activos=True)
        disponibles = inv_controller.listar_disponibles()
        total = len(todos_disfraces)
        total_disponibles = len(disponibles)
        total_rentados = sum(1 for d in todos_disfraces if d.stock > d.disponible)
        total_sin_stock = sum(1 for d in todos_disfraces if d.disponible == 0)
        
        stats_data = [
            ("📦", str(total), "Total Disfraces", self.COLOR_INFO),
            ("✅", str(total_disponibles), "Disponibles", self.COLOR_EXITO),
            ("🔄", str(total_rentados), "Rentados", self.COLOR_ADVERTENCIA),
            ("❌", str(total_sin_stock), "Sin Stock", self.COLOR_PELIGRO),
        ]
        
        for i, (icono, valor, titulo, color) in enumerate(stats_data):
            card = ctk.CTkFrame(
                stats_frame,
                fg_color=self.COLOR_AZUL_MUY_OSCURO,
                corner_radius=10
            )
            card.grid(row=0, column=i, padx=8, sticky="ew")
            stats_frame.columnconfigure(i, weight=1)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(pady=15, padx=20)
            
            # Icono
            icon_frame = ctk.CTkFrame(content, fg_color=color, width=40, height=40, corner_radius=8)
            icon_frame.pack(side="left", padx=(0, 15))
            icon_frame.pack_propagate(False)
            
            ctk.CTkLabel(
                icon_frame,
                text=icono,
                font=("Arial", 20)
            ).place(relx=0.5, rely=0.5, anchor="center")
            
            # Info
            info_frame = ctk.CTkFrame(content, fg_color="transparent")
            info_frame.pack(side="left")
            
            ctk.CTkLabel(
                info_frame,
                text=valor,
                font=("Arial Bold", 28),
                text_color=self.COLOR_TEXTO_PRINCIPAL
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                info_frame,
                text=titulo,
                font=("Arial", 12),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            ).pack(anchor="w")
        
        # ==================== TABLA ====================
        if not todos_disfraces:
            self.crear_placeholder("📦 No hay disfraces", "Agrega el primer disfraz al inventario")
            return
        
        table_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            corner_radius=15
        )
        table_card.pack(fill="both", expand=True)
        
        # Headers
        headers_frame = ctk.CTkFrame(table_card, fg_color="transparent", height=50)
        headers_frame.pack(fill="x", padx=25, pady=(20, 10))
        
        headers = ["Código", "Descripción", "Talla", "Categoría", "Stock", "Precio Renta", "Acciones"]
        widths = [120, 250, 80, 150, 100, 120, 150]
        
        for header, width in zip(headers, widths):
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=("Arial Bold", 13),
                text_color=self.COLOR_TEXTO_SECUNDARIO,
                width=width
            ).pack(side="left", padx=5)
        
        # Separador
        ctk.CTkFrame(
            table_card,
            height=1,
            fg_color=self.COLOR_AZUL_OSCURO
        ).pack(fill="x", padx=25, pady=5)
        
        # Filas
        for disfraz in todos_disfraces[:20]:  # Limitar a 20 para no sobrecargar
            self.crear_fila_disfraz(table_card, disfraz, widths)
    
    def crear_fila_disfraz(self, parent, disfraz, widths):
        """Crea una fila en la tabla de inventario."""
        row = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        row.pack(fill="x", padx=25, pady=3)
        
        # Código
        ctk.CTkLabel(
            row,
            text=disfraz.codigo_barras,
            font=("Arial Bold", 12),
            text_color=self.COLOR_TEXTO_SECUNDARIO,
            width=widths[0]
        ).pack(side="left", padx=5)
        
        # Descripción
        ctk.CTkLabel(
            row,
            text=disfraz.descripcion[:30] + "..." if len(disfraz.descripcion) > 30 else disfraz.descripcion,
            font=("Arial", 13),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            width=widths[1],
            anchor="w"
        ).pack(side="left", padx=5)
        
        # Talla
        ctk.CTkLabel(
            row,
            text=disfraz.talla,
            font=("Arial", 13),
            text_color=self.COLOR_TEXTO_PRINCIPAL,
            width=widths[2]
        ).pack(side="left", padx=5)
        
        # Categoría
        ctk.CTkLabel(
            row,
            text=disfraz.categoria,
            font=("Arial", 12),
            text_color=self.COLOR_TEXTO_SECUNDARIO,
            width=widths[3]
        ).pack(side="left", padx=5)
        
        # Stock (badge)
        stock_color = self.COLOR_EXITO if disfraz.disponible > 0 else self.COLOR_PELIGRO
        stock_frame = ctk.CTkFrame(row, fg_color=stock_color, corner_radius=15, width=widths[4])
        stock_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            stock_frame,
            text=f"{disfraz.disponible}/{disfraz.stock}",
            font=("Arial Bold", 12),
            text_color="white"
        ).pack(padx=12, pady=6)
        
        # Precio Renta
        ctk.CTkLabel(
            row,
            text=f"${disfraz.precio_renta:.2f}",
            font=("Arial Bold", 13),
            text_color=self.COLOR_MORADO_PRINCIPAL,
            width=widths[5]
        ).pack(side="left", padx=5)
        
        # Acciones
        actions_frame = ctk.CTkFrame(row, fg_color="transparent", width=widths[6])
        actions_frame.pack(side="left", padx=5)
        
        # Botón Ver (todos pueden ver)
        ctk.CTkButton(
            actions_frame,
            text="👁️",
            width=35,
            height=35,
            font=("Arial", 14),
            fg_color=self.COLOR_INFO,
            hover_color="#2563eb",
            command=lambda d=disfraz: self.ver_detalle_disfraz(d)
        ).pack(side="left", padx=2)
        
        # Botones Editar y Eliminar (SOLO ADMIN)
        if self.es_admin():
            # Botón Editar
            ctk.CTkButton(
                actions_frame,
                text="✏️",
                width=35,
                height=35,
                font=("Arial", 14),
                fg_color=self.COLOR_ADVERTENCIA,
                hover_color="#f59e0b",
                command=lambda d=disfraz: self.editar_disfraz(d)
            ).pack(side="left", padx=2)
            
            # Botón Eliminar
            ctk.CTkButton(
                actions_frame,
                text="🗑️",
                width=35,
                height=35,
                font=("Arial", 14),
                fg_color=self.COLOR_PELIGRO,
                hover_color="#dc2626",
                command=lambda d=disfraz: self.eliminar_disfraz(d)
            ).pack(side="left", padx=2)
    
    def agregar_disfraz(self):
        """Abre formulario para agregar disfraz (SOLO ADMIN)."""
        if not self.es_admin():
            messagebox.showerror(
                "Acceso Denegado",
                "No tienes permisos para agregar disfraces.\nSolo los administradores pueden realizar esta acción."
            )
            return
        
        from views.inventario_screen import FormularioDisfraz
        FormularioDisfraz(self, callback=self.recargar_vista_inventario)
    
    def editar_disfraz(self, disfraz):
        """Abre formulario para editar disfraz (SOLO ADMIN)."""
        if not self.es_admin():
            messagebox.showerror(
                "Acceso Denegado",
                "No tienes permisos para editar disfraces.\nSolo los administradores pueden realizar esta acción."
            )
            return
        
        from views.inventario_screen import FormularioDisfraz
        FormularioDisfraz(self, disfraz_obj=disfraz, callback=self.recargar_vista_inventario)
    
    def ver_detalle_disfraz(self, disfraz):
        """Muestra detalles completos del disfraz."""
        detalles = f"""
📦 DETALLES DEL DISFRAZ

Código: {disfraz.codigo_barras}
Descripción: {disfraz.descripcion}
Talla: {disfraz.talla}
Color: {disfraz.color}
Categoría: {disfraz.categoria}

💰 PRECIOS:
Venta: ${disfraz.precio_venta:.2f}
Renta: ${disfraz.precio_renta:.2f}/día

📊 STOCK:
Total: {disfraz.stock}
Disponible: {disfraz.disponible}
Rentados: {disfraz.stock - disfraz.disponible}

Estado: {disfraz.estado}
        """
        messagebox.showinfo("Detalles del Disfraz", detalles)
    
    def eliminar_disfraz(self, disfraz):
        """Elimina (inactiva) un disfraz (SOLO ADMIN)."""
        if not self.es_admin():
            messagebox.showerror(
                "Acceso Denegado",
                "No tienes permisos para eliminar disfraces.\nSolo los administradores pueden realizar esta acción."
            )
            return
        
        confirmar = messagebox.askyesno(
            "Eliminar Disfraz",
            f"¿Estás seguro de eliminar:\n\n"
            f"📦 {disfraz.descripcion}\n"
            f"🔢 Código: {disfraz.codigo_barras}\n"
            f"📊 Stock: {disfraz.stock}\n\n"
            f"⚠️ Se marcará como inactivo."
        )
        
        if confirmar:
            from controllers.inventario_controller import InventarioController
            inv_controller = InventarioController()
            
            exito, mensaje = inv_controller.eliminar_disfraz(disfraz.codigo_barras)
            
            if exito:
                self.mostrar_notificacion(
                    f"Disfraz '{disfraz.descripcion}' eliminado",
                    "exito"
                )
                self.recargar_vista_inventario()
            else:
                self.mostrar_notificacion(mensaje, "error")
    
    def buscar_inventario(self):
        """Busca disfraces por nombre o código."""
        termino = self.entry_buscar_inv.get().strip()
        
        if not termino:
            self.mostrar_inventario()
            return
        
        from controllers.inventario_controller import InventarioController
        inv_controller = InventarioController()
        
        # Buscar por nombre
        resultados = inv_controller.buscar_por_descripcion(termino)
        # Si no encuentra, buscar por código
        if not resultados:
            disfraz = inv_controller.buscar_por_codigo(termino)
            if disfraz:
                resultados = [disfraz]
        
        # Mostrar resultados
        self.mostrar_resultados_busqueda(resultados, termino)
    
    def mostrar_resultados_busqueda(self, resultados, termino):
        """Muestra resultados de búsqueda."""
        self.limpiar_contenido()
        
        # Header
        header_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame,
            text=f"🔍 Resultados para: '{termino}'",
            font=("Arial Bold", 24),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(side="left")
        
        ctk.CTkButton(
            header_frame,
            text="← Volver",
            font=("Arial Bold", 14),
            fg_color=self.COLOR_TEXTO_SECUNDARIO,
            hover_color=self.COLOR_AZUL_OSCURO,
            command=self.mostrar_inventario
        ).pack(side="right")
        
        if not resultados:
            self.crear_placeholder(
                f"No se encontraron resultados para '{termino}'",
                "Intenta con otro término de búsqueda"
            )
            return
        
        # Mostrar cantidad
        ctk.CTkLabel(
            self.scroll_frame,
            text=f"Se encontraron {len(resultados)} resultado(s)",
            font=("Arial", 14),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        ).pack(anchor="w", pady=(0, 20))
        
        # Tabla de resultados
        table_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.COLOR_AZUL_MUY_OSCURO,
            corner_radius=15
        )
        table_card.pack(fill="both", expand=True)
        
        headers_frame = ctk.CTkFrame(table_card, fg_color="transparent", height=50)
        headers_frame.pack(fill="x", padx=25, pady=(20, 10))
        
        headers = ["Código", "Descripción", "Talla", "Categoría", "Stock", "Precio Renta", "Acciones"]
        widths = [120, 250, 80, 150, 100, 120, 150]
        
        for header, width in zip(headers, widths):
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=("Arial Bold", 13),
                text_color=self.COLOR_TEXTO_SECUNDARIO,
                width=width
            ).pack(side="left", padx=5)
        
        ctk.CTkFrame(
            table_card,
            height=1,
            fg_color=self.COLOR_AZUL_OSCURO
        ).pack(fill="x", padx=25, pady=5)
        
        for disfraz in resultados:
            self.crear_fila_disfraz(table_card, disfraz, widths)
    
    def recargar_vista_inventario(self):
        """Recarga la vista de inventario."""
        print("\n🔄 RECARGANDO VISTA DE INVENTARIO...")
        
        self.limpiar_contenido()
        
        loading_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        loading_frame.pack(expand=True)
        
        ctk.CTkLabel(
            loading_frame,
            text="🔄",
            font=("Arial", 60)
        ).pack(pady=20)
        
        ctk.CTkLabel(
            loading_frame,
            text="Actualizando inventario...",
            font=("Arial Bold", 18),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack()
        
        self.update()
        self.after(300, self.mostrar_inventario)
    
    def mostrar_rentas(self):
        """Carga la pantalla de rentas real dentro del dashboard."""
        self.limpiar_contenido()

        # Import aquí para evitar importación circular
        try:
            from views.rentas_screen import RentasScreen
        except Exception as e:
            self.crear_placeholder("❌ Error al cargar Rentas", str(e))
            return

        # Frame contenedor
        contenedor = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        contenedor.pack(fill="both", expand=True)

        # Cargar pantalla de rentas CON referencia al dashboard
        pantalla_rentas = RentasScreen(contenedor, self)
        pantalla_rentas.pack(fill="both", expand=True)
    
    # Dentro de la clase DashboardModern en dashboard_modern.py
    def mostrar_ventas(self):
        """Carga la pantalla de ventas real dentro del dashboard."""
        self.limpiar_contenido()
        # Import aquí para evitar importación circular
        try:
            from views.ventas_screen import VentasScreen
        except Exception as e:
            self.crear_placeholder("❌ Error al cargar Ventas", str(e))
            return
        # Frame contenedor
        contenedor = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        contenedor.pack(fill="both", expand=True)
        # Cargar pantalla de ventas CON referencia al dashboard
        pantalla_ventas = VentasScreen(contenedor, self)
        pantalla_ventas.pack(fill="both", expand=True)
    
    # En dashboard_modern.py, dentro de la clase DashboardModern
    def mostrar_clientes(self):
        """Muestra el módulo de gestión de clientes."""
        self.limpiar_contenido()
        from views.clientes_screen import ClientesScreen # Importar aquí
        clientes_frame = ClientesScreen(self.scroll_frame, self)
        clientes_frame.pack(fill="both", expand=True)
    
    def mostrar_caja(self):
        self.limpiar_contenido()
        self.crear_placeholder("💰 Caja", "Control de ingresos y egresos")
    
    def mostrar_configuracion(self):
        """Muestra el módulo de configuración del sistema."""
        # Opcional: Puedes restringirlo solo a admins como con usuarios
        # if not self.es_admin():
        #     messagebox.showerror("Acceso Denegado", "Solo administradores pueden acceder a la configuración.")
        #     return
        self.limpiar_contenido()
        try:
            # Import aquí para evitar importación circular
            from views.configuracion_screen import ConfiguracionScreen
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo importar la pantalla de configuración: {e}")
            return

        # Frame contenedor
        contenedor = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        contenedor.pack(fill="both", expand=True)

        # Cargar pantalla de configuración CON referencia al dashboard
        pantalla_config = ConfiguracionScreen(contenedor, self)
        pantalla_config.pack(fill="both", expand=True)
    
    def crear_placeholder(self, titulo, subtitulo):
        """Crea un placeholder para módulos en construcción."""
        container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        container.pack(expand=True)
        
        ctk.CTkLabel(
            container,
            text="🚧",
            font=("Arial", 80)
        ).pack(pady=20)
        
        ctk.CTkLabel(
            container,
            text=titulo,
            font=("Arial Bold", 32),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack()
        
        ctk.CTkLabel(
            container,
            text=subtitulo,
            font=("Arial", 16),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        ).pack(pady=10)
        
        ctk.CTkLabel(
            container,
            text="Módulo en construcción",
            font=("Arial", 14),
            text_color=self.COLOR_MORADO_PRINCIPAL
        ).pack(pady=5)
    
    def cerrar_sesion(self):
        """Cierra la sesión y vuelve al login."""
        if messagebox.askyesno("Cerrar Sesión", "¿Seguro que deseas cerrar sesión?"):
            self.auth_controller.cerrar_sesion()
            self.destroy()
            
            from views.login_screen import LoginScreen
            login = LoginScreen()
            login.mainloop()



# ==================== PRUEBA INDEPENDIENTE ====================
if __name__ == "__main__":
    from models.usuario import Usuario
    
    usuario_prueba = Usuario(
        id_usuario=1,
        usuario="admin",
        nombre="Administrador",
        apellido_paterno="Sistema",
        password="admin123",
        rol="admin"
    )
    
    app = DashboardModern(usuario_prueba)
    app.mainloop()