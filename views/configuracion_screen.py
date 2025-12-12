"""
Módulo: configuracion_screen.py
Ubicación: views/configuracion_screen.py
Descripción: Pantalla de configuración del sistema
Sistema: MaskNGO - Renta y Venta de Disfraces
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Optional, List
import sys
import os
import glob
import logging
from datetime import datetime
# Asegurar que la raíz del proyecto esté en el path
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)
from controllers.auth_controller import AuthController
from models.usuario import Usuario
# Importar ConexionDB
from config.database import ConexionDB
class ConfiguracionScreen(ctk.CTkFrame):
    """
    Pantalla principal de configuración del sistema.
    Incluye Perfil del Usuario Actual, Configuración del Sistema y Auditoría/Logs.
    """
    # Paleta de colores (mismo estilo que dashboard y rentas)
    COLOR_MORADO_PRINCIPAL = "#7B68EE"
    COLOR_MORADO_HOVER = "#6A59DD"
    COLOR_AZUL_OSCURO = "#1e293b"
    COLOR_AZUL_MUY_OSCURO = "#0f172a"
    COLOR_TEXTO_PRINCIPAL = "#ffffff"
    COLOR_TEXTO_SECUNDARIO = "#94a3b8"
    COLOR_EXITO = "#10b981"
    COLOR_ADVERTENCIA = "#fbbf24"
    COLOR_INFO = "#3b82f6"
    COLOR_PELIGRO = "#ef4444"
    COLOR_BORDE = "#334155"
    # Definir los campos disponibles para el recibo aquí
    # Esta es la lista de opciones que se mostrarán como checkboxes
    CAMPOS_DISPONIBLES_RECIBO = [
        "Nombre_Negocio",
        "Direccion_Negocio",
        "Telefono_Negocio",
        "Cliente",
        "Disfraces",
        "Total",
        "Dia_Renta",
        "Dia_Devolucion"
    ]

    def __init__(self, parent, dashboard_ref):
        super().__init__(parent, fg_color="transparent")
        self.dashboard = dashboard_ref
        # Usar la sesión activa del dashboard
        self.usuario_actual = self.dashboard.usuario
        if not self.usuario_actual:
            # Esto no debería pasar si la navegación es correcta, pero por si acaso
            messagebox.showerror("Error", "❌ No hay sesión activa. Inicia sesión de nuevo.")
            return
        # Inicializar conexión a la base de datos
        self.db = ConexionDB()
        self.parametros = {} # Diccionario para almacenar los parámetros cargados
        self._cargar_parametros()
        # Diccionario para almacenar las variables de los checkboxes de formato de recibo
        self.checkbox_vars = {}
        self.construir_interfaz()
    def _cargar_parametros(self):
        """Carga los parámetros de configuración desde la base de datos."""
        try:
            self.db.conectar()
            query = "SELECT Parametro, Valor FROM PARAMETROS_SISTEMA"
            resultados = self.db.ejecutar_query(query)

            if resultados:
                for fila in resultados:
                    parametro, valor = fila
                    self.parametros[parametro] = valor
                print(f"[INFO] Parámetros de sistema cargados: {list(self.parametros.keys())}")
            else:
                print("[WARNING] No se encontraron parámetros en PARAMETROS_SISTEMA. Se usarán valores por defecto.")
                # Opcional: Inicializar con valores por defecto si no existen
                self._inicializar_parametros_por_defecto()
        except Exception as e:
            print(f"[ERROR] No se pudieron cargar los parámetros de sistema: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los parámetros de sistema: {e}")
    def _inicializar_parametros_por_defecto(self):
        """Inicializa el diccionario con valores por defecto si no existen en la BD."""
        self.parametros = {
            'Nombre_Negocio': 'MaskNGO - Renta y Venta de Disfraces',
            'Telefono_Negocio': '618-123-4567',
            'Direccion_Negocio': 'Calle Ficticia #123, Ciudad, Estado',
            'Dias_Gracia_Renta': '2',
            'Penalizacion_Vencimiento': '50.00',
            'Limite_Disfraces_Renta': '10',
            'Requerir_Deposito': '1',
            'Metodos_Pago': 'Efectivo,Tarjeta,Transferencia',
            'Descuento_Volumen_Cantidad': '3',
            'Descuento_Volumen_Porcentaje': '10.0',
            'Alerta_Stock_Minimo': '5',
            'Formato_Recibo': 'Nombre_Negocio,Direccion_Negocio,Telefono_Negocio,Cliente,Disfraces,Total,Dia_Renta,Dia_Devolucion'
        }
    def construir_interfaz(self):
        # Header con título
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            header,
            text="⚙️ CONFIGURACIÓN DEL SISTEMA",
            font=("Arial", 24, "bold"),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(anchor="w")
        # Contenedor principal con pestañas
        self.tabview = ctk.CTkTabview(self, fg_color=self.COLOR_AZUL_OSCURO, segmented_button_fg_color=self.COLOR_AZUL_MUY_OSCURO, segmented_button_selected_color=self.COLOR_MORADO_PRINCIPAL)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        # Pestaña: Perfil del Usuario Actual
        self.tabview.add("👤 Perfil del Usuario Actual")
        self._construir_seccion_perfil(self.tabview.tab("👤 Perfil del Usuario Actual"))
        # Pestaña: Configuración del Sistema
        self.tabview.add("🔧 Configuración del Sistema")
        self._construir_seccion_sistema(self.tabview.tab("🔧 Configuración del Sistema"))
        # Pestaña: Auditoría y Logs
        self.tabview.add("📋 Auditoría y Logs")
        self._construir_seccion_logs(self.tabview.tab("📋 Auditoría y Logs"))
    def _construir_seccion_perfil(self, parent):
        # Frame principal para el perfil
        frame_perfil = ctk.CTkFrame(parent, fg_color="transparent")
        frame_perfil.pack(fill="both", expand=True, padx=10, pady=10)
        # Información actual del usuario
        info_frame = ctk.CTkFrame(frame_perfil, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=(0, 15))
        ctk.CTkLabel(info_frame, text="Información Actual", font=("Arial", 16, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(15, 10))
        # Mostrar datos
        ctk.CTkLabel(info_frame, text=f"ID Usuario: {self.usuario_actual.id_usuario}", font=("Arial", 12), text_color=self.COLOR_TEXTO_SECUNDARIO).pack(anchor="w", padx=20, pady=2)
        ctk.CTkLabel(info_frame, text=f"Usuario: {self.usuario_actual.usuario}", font=("Arial", 12), text_color=self.COLOR_TEXTO_SECUNDARIO).pack(anchor="w", padx=20, pady=2)
        ctk.CTkLabel(info_frame, text=f"Nombre Completo: {self.usuario_actual.nombre_completo()}", font=("Arial", 12), text_color=self.COLOR_TEXTO_SECUNDARIO).pack(anchor="w", padx=20, pady=2)
        ctk.CTkLabel(info_frame, text=f"Rol: {self.usuario_actual.rol.upper()}", font=("Arial", 12), text_color=self.COLOR_TEXTO_SECUNDARIO).pack(anchor="w", padx=20, pady=2)
        ctk.CTkLabel(info_frame, text=f"Fecha de Registro: {self.usuario_actual.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')}", font=("Arial", 12), text_color=self.COLOR_TEXTO_SECUNDARIO).pack(anchor="w", padx=20, pady=2)
        # Formulario para editar datos personales
        form_frame = ctk.CTkFrame(frame_perfil, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        form_frame.pack(fill="x", padx=10, pady=(0, 15))
        ctk.CTkLabel(form_frame, text="Editar Datos Personales", font=("Arial", 16, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(15, 10))
        # Campos de entrada
        ctk.CTkLabel(form_frame, text="Nombre*", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_nombre = ctk.CTkEntry(form_frame, placeholder_text=self.usuario_actual.nombre, height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_nombre.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(form_frame, text="Apellido Paterno*", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_apellido = ctk.CTkEntry(form_frame, placeholder_text=self.usuario_actual.apellido_paterno, height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_apellido.pack(fill="x", padx=20, pady=(0, 10))
        # Botón para guardar cambios
        ctk.CTkButton(
            form_frame,
            text="Guardar Cambios",
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=self._guardar_datos_personales,
            height=40
        ).pack(pady=20)
        # Formulario para cambiar contraseña
        pass_frame = ctk.CTkFrame(frame_perfil, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        pass_frame.pack(fill="x", padx=10, pady=(0, 15))
        ctk.CTkLabel(pass_frame, text="Cambiar Contraseña", font=("Arial", 16, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(15, 10))
        ctk.CTkLabel(pass_frame, text="Contraseña Actual*", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_pass_actual = ctk.CTkEntry(pass_frame, show="*", height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_pass_actual.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(pass_frame, text="Nueva Contraseña*", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_pass_nueva = ctk.CTkEntry(pass_frame, show="*", height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_pass_nueva.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(pass_frame, text="Confirmar Nueva Contraseña*", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_pass_confirma = ctk.CTkEntry(pass_frame, show="*", height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_pass_confirma.pack(fill="x", padx=20, pady=(0, 10))
        # Botón para cambiar contraseña
        ctk.CTkButton(
            pass_frame,
            text="Cambiar Contraseña",
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=self._cambiar_contrasena,
            height=40
        ).pack(pady=20)
    def _guardar_datos_personales(self):
        nuevo_nombre = self.entrada_nombre.get().strip()
        nuevo_apellido = self.entrada_apellido.get().strip()
        if not nuevo_nombre and not nuevo_apellido:
            messagebox.showwarning("Advertencia", "Por favor, introduce al menos un nuevo valor para Nombre o Apellido.")
            return
        # Si no se introduce un campo, mantener el valor actual
        nombre_final = nuevo_nombre if nuevo_nombre else self.usuario_actual.nombre
        apellido_final = nuevo_apellido if nuevo_apellido else self.usuario_actual.apellido_paterno
        # Actualizar solo nombre y apellido (rol no se cambia aquí)
        # Usar el controlador del dashboard
        exito, msg = self.dashboard.auth_controller.actualizar_usuario(
            id_usuario=self.usuario_actual.id_usuario,
            nombre=nombre_final,
            apellido_paterno=apellido_final,
            rol=self.usuario_actual.rol # Mantener rol actual
        )
        if exito:
            messagebox.showinfo("Éxito", msg)
            # Actualizar la información local del usuario
            self.usuario_actual.nombre = nombre_final
            self.usuario_actual.apellido_paterno = apellido_final
            # Recargar la interfaz para mostrar los cambios
            self._construir_seccion_perfil(self.tabview.tab("👤 Perfil del Usuario Actual"))
        else:
            messagebox.showerror("Error", msg)
    def _cambiar_contrasena(self):
        pass_actual = self.entrada_pass_actual.get().strip()
        pass_nueva = self.entrada_pass_nueva.get().strip()
        pass_confirma = self.entrada_pass_confirma.get().strip()

        if not pass_actual or not pass_nueva or not pass_confirma:
            messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")
            return
        if pass_nueva != pass_confirma:
            messagebox.showerror("Error", "La nueva contraseña y su confirmación no coinciden.")
            return
        # Usar el controlador del dashboard para intentar el cambio de contraseña
        exito, msg = self.dashboard.auth_controller.cambiar_password(self.usuario_actual.usuario, pass_actual, pass_nueva)
        if exito:
            messagebox.showinfo("Éxito", msg)
            # Limpiar campos de contraseña
            self.entrada_pass_actual.delete(0, "end")
            self.entrada_pass_nueva.delete(0, "end")
            self.entrada_pass_confirma.delete(0, "end")
        else:
            messagebox.showerror("Error", msg)
    def _construir_seccion_sistema(self, parent):
        # Frame principal para configuración del sistema
        frame_sistema = ctk.CTkFrame(parent, fg_color="transparent")
        frame_sistema.pack(fill="both", expand=True, padx=10, pady=10)
        # --- 1. Configuración General del Negocio ---
        general_frame = ctk.CTkFrame(frame_sistema, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        general_frame.pack(fill="x", padx=10, pady=5, anchor="n")
        ctk.CTkLabel(general_frame, text="🔧 Configuración General del Negocio", font=("Arial", 14, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(general_frame, text="Nombre del Negocio", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_nombre_negocio = ctk.CTkEntry(general_frame, height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_nombre_negocio.pack(fill="x", padx=20, pady=(0, 5))
        self.entrada_nombre_negocio.insert(0, self.parametros.get('Nombre_Negocio', ''))
        ctk.CTkLabel(general_frame, text="Teléfono del Negocio", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_telefono_negocio = ctk.CTkEntry(general_frame, height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_telefono_negocio.pack(fill="x", padx=20, pady=(0, 5))
        self.entrada_telefono_negocio.insert(0, self.parametros.get('Telefono_Negocio', ''))
        ctk.CTkLabel(general_frame, text="Dirección del Negocio", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_direccion_negocio = ctk.CTkEntry(general_frame, height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_direccion_negocio.pack(fill="x", padx=20, pady=(0, 10))
        self.entrada_direccion_negocio.insert(0, self.parametros.get('Direccion_Negocio', ''))
        # --- 2. Configuración de Renta ---
        renta_frame = ctk.CTkFrame(frame_sistema, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        renta_frame.pack(fill="x", padx=10, pady=5, anchor="n")
        ctk.CTkLabel(renta_frame, text="🔄 Configuración de Renta", font=("Arial", 14, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(renta_frame, text="Días de Gracia", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_dias_gracia = ctk.CTkEntry(renta_frame, height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_dias_gracia.pack(fill="x", padx=20, pady=(0, 5))
        self.entrada_dias_gracia.insert(0, self.parametros.get('Dias_Gracia_Renta', '2'))
        ctk.CTkLabel(renta_frame, text="Penalización por Vencimiento ($)", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_penalizacion = ctk.CTkEntry(renta_frame, height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_penalizacion.pack(fill="x", padx=20, pady=(0, 5))
        self.entrada_penalizacion.insert(0, self.parametros.get('Penalizacion_Vencimiento', '50.00'))
        ctk.CTkLabel(renta_frame, text="Límite de Disfraces por Renta", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_limite_disfraces = ctk.CTkEntry(renta_frame, height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_limite_disfraces.pack(fill="x", padx=20, pady=(0, 5))
        self.entrada_limite_disfraces.insert(0, self.parametros.get('Limite_Disfraces_Renta', '10'))
        self.switch_deposito = ctk.CTkSwitch(renta_frame, text="Requerir Depósito", font=("Arial", 12), onvalue="1", offvalue="0")
        self.switch_deposito.pack(anchor="w", padx=20, pady=(5, 10))
        self.switch_deposito_var = ctk.StringVar(value=self.parametros.get('Requerir_Deposito', '1'))
        self.switch_deposito.configure(variable=self.switch_deposito_var)
        # --- 3. Configuración de Venta ---
        venta_frame = ctk.CTkFrame(frame_sistema, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        venta_frame.pack(fill="x", padx=10, pady=5, anchor="n")
        ctk.CTkLabel(venta_frame, text="🛒 Configuración de Venta", font=("Arial", 14, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(venta_frame, text="Métodos de Pago (separados por coma)", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_metodos_pago = ctk.CTkEntry(venta_frame, height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_metodos_pago.pack(fill="x", padx=20, pady=(0, 5))
        self.entrada_metodos_pago.insert(0, self.parametros.get('Metodos_Pago', 'Efectivo,Tarjeta,Transferencia'))
        ctk.CTkLabel(venta_frame, text="Descuento por Volumen (%)", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_descuento_volumen = ctk.CTkEntry(venta_frame, height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_descuento_volumen.pack(fill="x", padx=20, pady=(0, 10))
        self.entrada_descuento_volumen.insert(0, self.parametros.get('Descuento_Volumen_Porcentaje', '10.0'))
        # --- 4. Configuración de Inventario ---
        inventario_frame = ctk.CTkFrame(frame_sistema, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        inventario_frame.pack(fill="x", padx=10, pady=5, anchor="n")
        ctk.CTkLabel(inventario_frame, text="📦 Configuración de Inventario", font=("Arial", 14, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(inventario_frame, text="Alerta de Stock Mínimo", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        self.entrada_alerta_stock = ctk.CTkEntry(inventario_frame, height=35, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_alerta_stock.pack(fill="x", padx=20, pady=(0, 10))
        self.entrada_alerta_stock.insert(0, self.parametros.get('Alerta_Stock_Minimo', '5'))
        # --- 7. Configuración de Impresión ---
        impresion_frame = ctk.CTkFrame(frame_sistema, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        impresion_frame.pack(fill="x", padx=10, pady=5, anchor="n")
        ctk.CTkLabel(impresion_frame, text="🖨️ Configuración de Impresión", font=("Arial", 14, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(10, 5))
        # --- NUEVO: Checkboxes para campos del recibo ---
        ctk.CTkLabel(impresion_frame, text="Formato de Recibo", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(5, 0))
        # Frame para contener los checkboxes
        checkboxes_frame = ctk.CTkFrame(impresion_frame, fg_color="transparent")
        checkboxes_frame.pack(fill="x", padx=20, pady=(0, 10))
        # Obtener los campos actuales seleccionados del parámetro guardado
        campos_actuales_str = self.parametros.get('Formato_Recibo', 'Nombre_Negocio,Direccion_Negocio,Telefono_Negocio,Cliente,Disfraces,Total,Dia_Renta,Dia_Devolucion')
        campos_actuales_set = set(campos_actuales_str.split(','))
        # Crear un checkbox para cada campo disponible
        for campo in self.CAMPOS_DISPONIBLES_RECIBO:
            var = ctk.BooleanVar(value=(campo in campos_actuales_set))
            checkbox = ctk.CTkCheckBox(checkboxes_frame, text=campo, variable=var, font=("Arial", 11))
            checkbox.pack(anchor="w", padx=10, pady=2)
            # Almacenar la variable para accederla luego al guardar
            self.checkbox_vars[campo] = var
        # --- FIN NUEVO ---
        # Botón para guardar configuración del sistema
        ctk.CTkButton(
            frame_sistema,
            text="Guardar Configuración del Sistema",
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=self._guardar_configuracion_sistema,
            height=40
        ).pack(pady=20, fill="x", padx=10)
    def _guardar_configuracion_sistema(self):
        """Guarda los parámetros de configuración en la base de datos."""
        try:
            # Recopilar nuevos valores de los widgets
            nuevos_parametros = {
                'Nombre_Negocio': self.entrada_nombre_negocio.get().strip(),
                'Telefono_Negocio': self.entrada_telefono_negocio.get().strip(),
                'Direccion_Negocio': self.entrada_direccion_negocio.get().strip(),
                'Dias_Gracia_Renta': self.entrada_dias_gracia.get().strip(),
                'Penalizacion_Vencimiento': self.entrada_penalizacion.get().strip(),
                'Limite_Disfraces_Renta': self.entrada_limite_disfraces.get().strip(),
                'Requerir_Deposito': self.switch_deposito_var.get(), # Usar la variable del switch
                'Metodos_Pago': self.entrada_metodos_pago.get().strip(),
                'Descuento_Volumen_Porcentaje': self.entrada_descuento_volumen.get().strip(),
                'Alerta_Stock_Minimo': self.entrada_alerta_stock.get().strip(),
                # 'Formato_Recibo': self.entrada_formato_recibo.get().strip(), # Ya no se usa este campo de entrada
            }
            # Obtener los campos seleccionados de los checkboxes
            campos_seleccionados = [campo for campo, var in self.checkbox_vars.items() if var.get()]
            nuevos_parametros['Formato_Recibo'] = ','.join(campos_seleccionados)
            # Validaciones básicas (puedes añadir más)
            for key, value in nuevos_parametros.items():
                if key in ['Dias_Gracia_Renta', 'Limite_Disfraces_Renta', 'Alerta_Stock_Minimo']:
                    try:
                        int(value)
                    except ValueError:
                        messagebox.showerror("Error", f"El valor para '{key}' debe ser un número entero.")
                        return
                elif key in ['Penalizacion_Vencimiento', 'Descuento_Volumen_Porcentaje']:
                    try:
                        float(value)
                    except ValueError:
                        messagebox.showerror("Error", f"El valor para '{key}' debe ser un número.")
                        return
                elif key == 'Metodos_Pago':
                    if not value:
                        messagebox.showerror("Error", f"La lista de métodos de pago no puede estar vacía.")
                        return
            # Guardar en la base de datos
            self.db.conectar()
            for parametro, valor in nuevos_parametros.items():
                query = "UPDATE PARAMETROS_SISTEMA SET Valor = %s WHERE Parametro = %s"
                self.db.ejecutar_update(query, (str(valor), parametro))
            # Actualizar el diccionario local
            self.parametros.update(nuevos_parametros)
            messagebox.showinfo("Éxito", "Configuración del sistema guardada correctamente.")
        except Exception as e:
            print(f"[ERROR] No se pudo guardar la configuración del sistema: {e}")
            messagebox.showerror("Error", f"No se pudo guardar la configuración del sistema: {e}")
    def _construir_seccion_logs(self, parent):
        # Frame principal para auditoría y logs
        frame_logs = ctk.CTkFrame(parent, fg_color="transparent")
        frame_logs.pack(fill="both", expand=True, padx=10, pady=10)
        # Botón para recargar logs
        ctk.CTkButton(
            frame_logs,
            text="🔄 Recargar Logs",
            fg_color=self.COLOR_INFO,
            hover_color="#2563eb",
            command=self._cargar_y_mostrar_logs,
            width=120,
            height=35
        ).pack(anchor="ne", padx=10, pady=(0, 10))
        # Textbox para mostrar logs
        self.textbox_logs = ctk.CTkTextbox(frame_logs, fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE, font=("Consolas", 10))
        self.textbox_logs.pack(fill="both", expand=True, padx=10, pady=10)
        # Cargar logs iniciales
        self._cargar_y_mostrar_logs()
    def _cargar_y_mostrar_logs(self):
        # Limpia el textbox
        self.textbox_logs.delete("0.0", "end")
        # Buscar archivos de log en la carpeta 'logs'
        archivos_log = glob.glob("logs/*.log")
        if not archivos_log:
            self.textbox_logs.insert("0.0", "No se encontraron archivos de log en la carpeta 'logs/'.\n")
            return
        # Ordenar por fecha de modificación (más reciente primero)
        archivos_log.sort(key=os.path.getmtime, reverse=True)
        contenido_completo = ""
        for archivo in archivos_log:
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    contenido_completo += f"\n--- Archivo: {archivo} ---\n{contenido}\n"
            except Exception as e:
                contenido_completo += f"\n--- Error leyendo {archivo}: {e} ---\n"
        # Insertar contenido en el textbox
        self.textbox_logs.insert("0.0", contenido_completo)
        self.textbox_logs.see("end") # Hacer scroll al final