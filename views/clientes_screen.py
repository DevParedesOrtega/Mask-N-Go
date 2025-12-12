"""
Módulo: clientes_screen.py
Ubicación: views/clientes_screen.py
Descripción: Pantalla de gestión de clientes
Sistema: MaskNGO - Renta y Venta de Disfraces
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, List
import sys
import os
from controllers.cliente_controller import ClienteController
from models.cliente import Cliente


class ClientesScreen(ctk.CTkFrame):
    """
    Pantalla principal de gestión de clientes.
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

    def __init__(self, parent, dashboard_ref):
        super().__init__(parent, fg_color="transparent")
        self.dashboard = dashboard_ref
        self.cliente_controller = ClienteController()
        self.clientes_lista: List[Cliente] = []
        self.construir_interfaz()
        self.cargar_clientes()

    def construir_interfaz(self):
        # Header con título y botón de agregar
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            header,
            text="👥 GESTIÓN DE CLIENTES",
            font=("Arial", 24, "bold"),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(side="left")
        ctk.CTkButton(
            header,
            text="+ Nuevo Cliente",
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=self.abrir_formulario_cliente,
            width=150,
            height=40
        ).pack(side="right")

        # Frame para filtros
        filtros_frame = ctk.CTkFrame(self, fg_color="transparent")
        filtros_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(filtros_frame, text="🔍 Filtrar por:", font=("Arial", 12), text_color=self.COLOR_TEXTO_SECUNDARIO).pack(side="left", padx=(0, 10))
        
        self.entrada_filtro = ctk.CTkEntry(filtros_frame, placeholder_text="Nombre, apellido o teléfono...", height=35, width=300)
        self.entrada_filtro.pack(side="left", padx=(0, 10))
        self.entrada_filtro.bind("<KeyRelease>", lambda _: self._filtrar_clientes()) # Filtrar al teclear

        ctk.CTkButton(
            filtros_frame,
            text="Limpiar",
            fg_color=self.COLOR_BORDE,
            hover_color="#475569",
            command=self._limpiar_filtro,
            width=80,
            height=35
        ).pack(side="left")

        # Frame de la tabla
        tabla_frame = ctk.CTkFrame(self, fg_color=self.COLOR_AZUL_OSCURO)
        tabla_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Header de la tabla
        header_frame = ctk.CTkFrame(tabla_frame, fg_color=self.COLOR_AZUL_MUY_OSCURO, height=40)
        header_frame.pack(fill="x", padx=1, pady=1)
        headers = ["ID", "Nombre", "Apellido", "Teléfono", "Estado", "Acciones"]
        for h in headers:
            ctk.CTkLabel(
                header_frame,
                text=h,
                font=("Arial", 11, "bold"),
                text_color=self.COLOR_MORADO_PRINCIPAL
            ).pack(side="left", fill="x", expand=True, padx=10, pady=10)

        # Frame donde se cargarán las filas de clientes
        self.clientes_frame = ctk.CTkFrame(tabla_frame, fg_color=self.COLOR_AZUL_OSCURO)
        self.clientes_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Mensaje si no hay clientes
        self.label_vacio = ctk.CTkLabel(
            self.clientes_frame,
            text="📭 No hay clientes registrados",
            font=("Arial", 14),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        )
        self.label_vacio.pack(pady=40)

    def cargar_clientes(self):
        try:
            self.clientes_lista = self.cliente_controller.listar_todos(solo_activos=True) # Cargar solo activos por defecto
            self.actualizar_tabla()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los clientes: {e}")

    def actualizar_tabla(self):
        # Limpiar filas anteriores
        for w in self.clientes_frame.winfo_children():
            w.destroy()

        if not self.clientes_lista:
            self.label_vacio.pack(pady=40)
            return
        
        self.label_vacio.pack_forget() # Ocultar mensaje vacío

        for cliente in self.clientes_lista:
            self.agregar_fila_cliente(cliente)

    def agregar_fila_cliente(self, cliente: Cliente):
        fila = ctk.CTkFrame(self.clientes_frame, fg_color=self.COLOR_AZUL_OSCURO, height=50)
        fila.pack(fill="x", padx=1, pady=1)
        
        ctk.CTkLabel(fila, text=str(cliente.id_cliente), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkLabel(fila, text=cliente.nombre, text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkLabel(fila, text=cliente.apellido_paterno, text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkLabel(fila, text=cliente.telefono_formateado(), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        # Color del estado
        color_estado = self.COLOR_EXITO if cliente.estado == "Activo" else self.COLOR_ADVERTENCIA
        ctk.CTkLabel(fila, text=cliente.estado, text_color=color_estado).pack(side="left", fill="x", expand=True, padx=10, pady=10)

        # Frame para botones de acción
        acciones_frame = ctk.CTkFrame(fila, fg_color="transparent")
        acciones_frame.pack(side="right", padx=10, pady=10)
        
        ctk.CTkButton(
            acciones_frame,
            text="👁️ Ver",
            fg_color=self.COLOR_INFO,
            hover_color="#2563eb",
            width=50,
            height=30,
            font=("Arial", 10),
            command=lambda c=cliente: self.ver_detalle_cliente(c)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            acciones_frame,
            text="✏️ Editar",
            fg_color=self.COLOR_ADVERTENCIA,
            hover_color="#ca8a04",
            width=50,
            height=30,
            font=("Arial", 10),
            command=lambda c=cliente: self.abrir_formulario_cliente(cliente_a_editar=c)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            acciones_frame,
            text="🗑️ Eliminar",
            fg_color=self.COLOR_PELIGRO,
            hover_color="#dc2626",
            width=50,
            height=30,
            font=("Arial", 10),
            command=lambda c=cliente: self.eliminar_cliente(c)
        ).pack(side="left", padx=5)

    def ver_detalle_cliente(self, cliente: Cliente):
        # Cargar estadísticas si es posible
        try:
            estadisticas = {
                "total_gastado": self.cliente_controller.obtener_total_gastado(cliente.id_cliente),
                "tiene_rentas_activas": self.cliente_controller.cliente_tiene_rentas_activas(cliente.id_cliente),
                "tiene_deudas": self.cliente_controller.cliente_tiene_deudas(cliente.id_cliente),
            }
            cliente.cargar_estadisticas(estadisticas)
        except Exception as e:
            print(f"Error cargando estadísticas para {cliente.nombre_completo()}: {e}")

        detalles = cliente.resumen_estadisticas()
        messagebox.showinfo(f"Detalles de {cliente.nombre_completo()}", detalles)

    def eliminar_cliente(self, cliente: Cliente):
        if messagebox.askyesno("Confirmar Eliminación", f"¿Eliminar al cliente '{cliente.nombre_completo()}'?\n\n"
                                                       f"ID: {cliente.id_cliente}\n"
                                                       f"Teléfono: {cliente.telefono_formateado()}\n\n"
                                                       f"Esta acción no se puede deshacer."):
            exito, msg = self.cliente_controller.eliminar_cliente(cliente.id_cliente)
            if exito:
                messagebox.showinfo("Éxito", msg)
                self.cargar_clientes() # Recargar la lista
            else:
                messagebox.showerror("Error", msg)

    def abrir_formulario_cliente(self, cliente_a_editar: Optional[Cliente] = None):
        ventana_modal = ctk.CTkToplevel(self)
        ventana_modal.title("Agregar/Editar Cliente" if not cliente_a_editar else f"Editar Cliente: {cliente_a_editar.nombre_completo()}")
        ventana_modal.geometry("600x500")
        ventana_modal.transient(self.winfo_toplevel())
        ventana_modal.grab_set()
        ventana_modal.focus_force()
        ventana_modal.lift()
        
        def callback_recarga():
            self.cargar_clientes()
        
        FormularioCliente(ventana_modal, self.cliente_controller, callback_recarga, cliente_a_editar)

    # --- Funciones de filtrado ---
    def _filtrar_clientes(self):
        termino = self.entrada_filtro.get().strip().lower()
        if not termino:
            self.cargar_clientes() # Volver a cargar todos si el filtro está vacío
            return

        clientes_filtrados = [
            c for c in self.clientes_lista
            if termino in c.nombre.lower() or
               termino in c.apellido_paterno.lower() or
               termino in c.telefono.lower()
        ]
        
        # Actualizar la tabla con los resultados filtrados
        for w in self.clientes_frame.winfo_children():
            w.destroy()

        if not clientes_filtrados:
            self.label_vacio.pack(pady=40)
            return
        
        self.label_vacio.pack_forget()

        for cliente in clientes_filtrados:
            self.agregar_fila_cliente(cliente)

    def _limpiar_filtro(self):
        self.entrada_filtro.delete(0, "end")
        self.cargar_clientes() # Volver a cargar todos los clientes


# ==================== FORMULARIO DE CLIENTE ====================
class FormularioCliente(ctk.CTkFrame):
    """
    Formulario modal para agregar o editar un cliente.
    """
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

    def __init__(self, ventana, controller, callback_recarga, cliente_a_editar: Optional[Cliente] = None):
        super().__init__(ventana, fg_color="#1e293b")
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.ventana = ventana
        self.controller = controller
        self.callback_recarga = callback_recarga
        self.cliente_a_editar = cliente_a_editar

        self.nombre_var = ctk.StringVar()
        self.apellido_var = ctk.StringVar()
        self.telefono_var = ctk.StringVar()

        if cliente_a_editar:
            self.nombre_var.set(cliente_a_editar.nombre)
            self.apellido_var.set(cliente_a_editar.apellido_paterno)
            self.telefono_var.set(cliente_a_editar.telefono)

        self._construir_ui()

    def _construir_ui(self):
        ctk.CTkLabel(
            self,
            text="Agregar Nuevo Cliente" if not self.cliente_a_editar else "Editar Cliente",
            font=("Arial", 22, "bold"),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(pady=(0, 20))

        # Campos de entrada
        campos_frame = ctk.CTkFrame(self, fg_color="transparent")
        campos_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(campos_frame, text="Nombre*", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=10, pady=(10, 0))
        self.entrada_nombre = ctk.CTkEntry(campos_frame, textvariable=self.nombre_var, height=40, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_nombre.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(campos_frame, text="Apellido*", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=10, pady=(10, 0))
        self.entrada_apellido = ctk.CTkEntry(campos_frame, textvariable=self.apellido_var, height=40, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_apellido.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(campos_frame, text="Teléfono*", font=("Arial", 12), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=10, pady=(10, 0))
        self.entrada_telefono = ctk.CTkEntry(campos_frame, textvariable=self.telefono_var, height=40, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entrada_telefono.pack(fill="x", padx=10, pady=(0, 10))

        # Botones
        botones_frame = ctk.CTkFrame(self, fg_color="transparent")
        botones_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(
            botones_frame,
            text="Cancelar",
            fg_color=self.COLOR_BORDE,
            hover_color="#475569",
            command=self.ventana.destroy,
            width=120,
            height=40
        ).pack(side="left", padx=5)
        
        texto_btn = "Actualizar Cliente" if self.cliente_a_editar else "Agregar Cliente"
        comando_btn = self._actualizar_cliente if self.cliente_a_editar else self._agregar_cliente
        ctk.CTkButton(
            botones_frame,
            text=texto_btn,
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=comando_btn,
            width=180,
            height=40
        ).pack(side="right", padx=5)

    def _agregar_cliente(self):
        nombre = self.entrada_nombre.get().strip()
        apellido = self.entrada_apellido.get().strip()
        telefono = self.entrada_telefono.get().strip()

        if not nombre or not apellido or not telefono:
            messagebox.showwarning("Advertencia", "Por favor, completa todos los campos obligatorios (*).")
            return

        # Verificar duplicados antes de agregar
        duplicados = self.controller.buscar_duplicados(nombre, apellido, telefono)
        if duplicados:
            msg = f"Se encontraron clientes similares:\n"
            for d in duplicados:
                msg += f"- {d.nombre} {d.apellido_paterno} ({d.telefono})\n"
            msg += "\n¿Deseas continuar con el registro de todos modos?"
            if not messagebox.askyesno("Duplicado Detectado", msg):
                return

        exito, msg, id_cliente, _ = self.controller.agregar_cliente(nombre, apellido, telefono)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.ventana.destroy()
            self.callback_recarga()
        else:
            messagebox.showerror("Error", msg)

    def _actualizar_cliente(self):
        nombre = self.entrada_nombre.get().strip()
        apellido = self.entrada_apellido.get().strip()
        telefono = self.entrada_telefono.get().strip()

        if not nombre or not apellido or not telefono:
            messagebox.showwarning("Advertencia", "Por favor, completa todos los campos obligatorios (*).")
            return

        # Verificar si el teléfono nuevo ya está en uso por otro cliente
        cliente_existente = self.controller.buscar_por_telefono(telefono)
        if cliente_existente and cliente_existente.id_cliente != self.cliente_a_editar.id_cliente:
            messagebox.showerror("Error", f"El teléfono {telefono} ya está registrado con otro cliente.")
            return

        exito, msg = self.controller.editar_cliente(
            id_cliente=self.cliente_a_editar.id_cliente,
            nombre=nombre,
            apellido=apellido,
            telefono=telefono
        )
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.ventana.destroy()
            self.callback_recarga()
        else:
            messagebox.showerror("Error", msg)