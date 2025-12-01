"""
Módulo: rentas_screen.py (VERSIÓN 4.0 MEJORADA)
Ubicación: views/rentas_screen.py
Descripción: Pantalla de gestión de rentas + Formulario Premium v4.0
Sistema: MaskNGO - Renta y Venta de Disfraces
Versión: 4.0 - PREMIUM con autocomplete, selector visual, resumen dinámico
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.renta_controller import RentaController
from controllers.cliente_controller import ClienteController
from controllers.inventario_controller import InventarioController
from models.renta import Renta
from models.cliente import Cliente
from models.disfraz import Disfraz


class RentasScreen(ctk.CTkFrame):
    """
    Pantalla principal de gestión de rentas.
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

    def __init__(self, parent, dashboard_ref):
        super().__init__(parent, fg_color="transparent")
        self.dashboard = dashboard_ref

        self.renta_controller = RentaController()
        self.cliente_controller = ClienteController()
        self.inventario_controller = InventarioController()

        self.rentas_lista: List[Renta] = []

        self.construir_interfaz()
        self.cargar_rentas()

    def construir_interfaz(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text="🎭 GESTIÓN DE RENTAS",
            font=("Arial", 24, "bold"),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="+ Nueva Renta",
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=self.abrir_formulario_renta,
            width=150,
            height=40
        ).pack(side="right")

        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)

        self.label_stats = ctk.CTkLabel(
            stats_frame,
            text="📊 Cargando estadísticas...",
            font=("Arial", 12),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        )
        self.label_stats.pack(side="left")

        tabla_frame = ctk.CTkFrame(self, fg_color=self.COLOR_AZUL_OSCURO)
        tabla_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        header_frame = ctk.CTkFrame(tabla_frame, fg_color=self.COLOR_AZUL_MUY_OSCURO, height=40)
        header_frame.pack(fill="x", padx=1, pady=1)

        headers = ["ID", "Cliente", "Días", "Estado", "Fecha Renta", "Devolución", "Acciones"]
        for h in headers:
            ctk.CTkLabel(
                header_frame,
                text=h,
                font=("Arial", 11, "bold"),
                text_color=self.COLOR_MORADO_PRINCIPAL
            ).pack(side="left", fill="x", expand=True, padx=10, pady=10)

        self.rentas_frame = ctk.CTkFrame(tabla_frame, fg_color=self.COLOR_AZUL_OSCURO)
        self.rentas_frame.pack(fill="both", expand=True, padx=1, pady=1)

        self.label_vacio = ctk.CTkLabel(
            self.rentas_frame,
            text="📭 No hay rentas registradas",
            font=("Arial", 14),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        )
        self.label_vacio.pack(pady=40)

    def cargar_rentas(self):
        try:
            self.rentas_lista = self.renta_controller.listar_rentas_activas()
            self.actualizar_tabla()
            self.actualizar_stats()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las rentas: {e}")

    def actualizar_tabla(self):
        for w in self.rentas_frame.winfo_children():
            w.destroy()

        if not self.rentas_lista:
            self.label_vacio = ctk.CTkLabel(
                self.rentas_frame,
                text="📭 No hay rentas registradas",
                font=("Arial", 14),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            )
            self.label_vacio.pack(pady=40)
            return

        for renta in self.rentas_lista:
            self.agregar_fila_renta(renta)

    def agregar_fila_renta(self, renta: Renta):
        fila = ctk.CTkFrame(self.rentas_frame, fg_color=self.COLOR_AZUL_OSCURO, height=50)
        fila.pack(fill="x", padx=1, pady=1)

        ctk.CTkLabel(fila, text=str(renta.id_renta),
                     text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkLabel(fila, text=str(renta.id_cliente),
                     text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkLabel(fila, text=str(renta.dias_renta),
                     text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)

        color_estado = self.COLOR_EXITO if renta.esta_activa() else self.COLOR_ADVERTENCIA
        ctk.CTkLabel(fila, text=renta.estado,
                     text_color=color_estado).pack(side="left", fill="x", expand=True, padx=10, pady=10)

        fecha_renta = renta.fecha_renta.strftime("%Y-%m-%d") if renta.fecha_renta else "N/A"
        ctk.CTkLabel(fila, text=fecha_renta,
                     text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)

        fecha_dev = renta.fecha_devolucion.strftime("%Y-%m-%d") if renta.fecha_devolucion else "N/A"
        ctk.CTkLabel(fila, text=fecha_dev,
                     text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)

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
            command=lambda r=renta: self.ver_detalle_renta(r)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            acciones_frame,
            text="🔄 Devolver",
            fg_color=self.COLOR_EXITO,
            hover_color="#059669",
            width=50,
            height=30,
            font=("Arial", 10),
            command=lambda r=renta: self.devolver_renta(r)
        ).pack(side="left", padx=5)

    def actualizar_stats(self):
        total = len(self.rentas_lista)
        activas = sum(1 for r in self.rentas_lista if r.esta_activa())
        vencidas = sum(1 for r in self.rentas_lista if r.esta_vencida())
        self.label_stats.configure(
            text=f"📊 Total: {total} | 🟢 Activas: {activas} | 🟠 Vencidas: {vencidas}"
        )

    def ver_detalle_renta(self, renta: Renta):
        detalles = self.renta_controller.obtener_renta_completa(renta.id_renta)
        if detalles:
            messagebox.showinfo("Detalle de Renta", detalles.resumen_completo())

    def devolver_renta(self, renta: Renta):
        if messagebox.askyesno("Confirmar", f"¿Devolver renta ID {renta.id_renta}?"):
            exito, msg, _ = self.renta_controller.devolver_renta(
                id_renta=renta.id_renta,
                id_usuario=self.dashboard.id_usuario_actual
            )
            if exito:
                messagebox.showinfo("Éxito", msg)
                self.recargar_rentas()
            else:
                messagebox.showerror("Error", msg)

    def abrir_formulario_renta(self):
        if not self.dashboard.id_usuario_actual:
            messagebox.showerror("Error", "❌ No hay usuario logueado. Inicia sesión primero.")
            return

        ventana_modal = ctk.CTkToplevel(self)
        ventana_modal.title("Nueva Renta - Premium")
        ventana_modal.geometry("1200x700")

        # Modal encima del dashboard
        ventana_modal.transient(self.winfo_toplevel())
        ventana_modal.grab_set()
        ventana_modal.focus_force()
        ventana_modal.lift()

        FormularioRentaV4(ventana_modal, self.dashboard, self)

    def recargar_rentas(self):
        self.cargar_rentas()


# ==================== FORMULARIO PREMIUM V4.0 ====================

class FormularioRentaV4(ctk.CTkFrame):
    """
    Formulario PREMIUM de Nueva Renta v4.0
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

    def __init__(self, ventana, dashboard_ref, pantalla_rentas_ref):
        super().__init__(ventana, fg_color="#1e293b")
        self.pack(fill="both", expand=True, padx=20, pady=20)

        self.ventana = ventana
        self.dashboard = dashboard_ref
        self.pantalla_rentas = pantalla_rentas_ref

        self.renta_controller = RentaController()
        self.cliente_controller = ClienteController()
        self.inventario_controller = InventarioController()

        self.cliente_seleccionado: Optional[Cliente] = None
        self.disfraces_agregados: List[Dict] = []
        self.todos_clientes: List[Cliente] = []
        self.todos_disfraces: List[Disfraz] = []
        self.resumen_labels: Dict[str, ctk.CTkLabel] = {}

        self._cargar_datos_iniciales()
        self._construir_ui()

    def _cargar_datos_iniciales(self):
        try:
            self.todos_clientes = self.cliente_controller.listar_todos(solo_activos=True)
        except Exception as e:
            print(f"❌ Error cargando clientes: {e}")
            self.todos_clientes = []

        try:
            if hasattr(self.inventario_controller, "listar_disfraces"):
                self.todos_disfraces = self.inventario_controller.listar_disfraces(solo_activos=True)
            else:
                self.todos_disfraces = self.inventario_controller.listar_todos()
        except Exception as e:
            print(f"❌ Error cargando disfraces: {e}")
            self.todos_disfraces = []

    def _construir_ui(self):
        ctk.CTkLabel(
            self,
            text="🎭 Nueva Renta - Formulario Premium",
            font=("Arial", 22, "bold"),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(pady=(0, 10))

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        # Columna izquierda con scroll
        left_scroll = ctk.CTkScrollableFrame(
            main_container,
            fg_color="transparent"
        )
        left_scroll.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=(0, 5))

        # Columna derecha fija (resumen)
        right_col = ctk.CTkFrame(main_container, fg_color="transparent")
        right_col.pack(side="right", fill="y", expand=False, padx=(15, 0), pady=(0, 5))

        self._construir_seccion_cliente(left_scroll)
        self._construir_seccion_dias(left_scroll)
        self._construir_seccion_disfraces(left_scroll)
        self._construir_seccion_notas(left_scroll)

        self._construir_panel_resumen(right_col)

        botones_frame = ctk.CTkFrame(self, fg_color="transparent")
        botones_frame.pack(fill="x", pady=(5, 0))

        ctk.CTkButton(
            botones_frame,
            text="Cancelar",
            fg_color=self.COLOR_BORDE,
            hover_color="#475569",
            command=self.ventana.destroy,
            width=120,
            height=40
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            botones_frame,
            text="📋 Preview",
            fg_color=self.COLOR_INFO,
            hover_color="#2563eb",
            command=self._mostrar_preview,
            width=120,
            height=40
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            botones_frame,
            text="✅ Registrar Renta",
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=self._registrar_renta,
            width=150,
            height=40
        ).pack(side="right", padx=5)

    # ---------- CLIENTE ----------

    def _construir_seccion_cliente(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            frame,
            text="👤 CLIENTE",
            font=("Arial", 13, "bold"),
            text_color=self.COLOR_MORADO_PRINCIPAL
        ).pack(anchor="w", padx=15, pady=(12, 10))

        entry_frame = ctk.CTkFrame(frame, fg_color="transparent")
        entry_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.entry_cliente = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Escribe nombre o ID del cliente...",
            height=40,
            font=("Arial", 12),
            fg_color=self.COLOR_AZUL_OSCURO,
            border_color=self.COLOR_BORDE
        )
        self.entry_cliente.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_cliente.bind("<KeyRelease>", lambda _: self._filtrar_clientes())

        ctk.CTkButton(
            entry_frame,
            text="🔍",
            width=40,
            height=40,
            fg_color=self.COLOR_INFO,
            hover_color="#2563eb",
            command=self._mostrar_selector_clientes
        ).pack(side="left")

        self.dropdown_frame = ctk.CTkFrame(frame, fg_color=self.COLOR_AZUL_OSCURO, corner_radius=8)
        self.dropdown_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.dropdown_frame.pack_forget()

        self.label_cliente_info = ctk.CTkLabel(
            frame,
            text="❌ No hay cliente seleccionado",
            font=("Arial", 11),
            text_color=self.COLOR_ADVERTENCIA
        )
        self.label_cliente_info.pack(anchor="w", padx=15, pady=(0, 12))

    def _filtrar_clientes(self):
        termino = self.entry_cliente.get().lower().strip()

        for w in self.dropdown_frame.winfo_children():
            w.destroy()

        if not termino:
            self.dropdown_frame.pack_forget()
            return

        coincidencias = []
        for c in self.todos_clientes:
            nombre_completo = f"{c.nombre} {c.apellido_paterno}".lower()
            if termino in nombre_completo or termino in str(c.id_cliente):
                coincidencias.append(c)

        if not coincidencias:
            ctk.CTkLabel(
                self.dropdown_frame,
                text="No hay coincidencias",
                font=("Arial", 10),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            ).pack(fill="x", padx=10, pady=5)
            self.dropdown_frame.pack(fill="x", before=self.label_cliente_info)
            return

        for cliente in coincidencias[:5]:
            texto = f"#{cliente.id_cliente} - {cliente.nombre} {cliente.apellido_paterno}"
            ctk.CTkButton(
                self.dropdown_frame,
                text=texto,
                fg_color=self.COLOR_AZUL_OSCURO,
                hover_color=self.COLOR_MORADO_PRINCIPAL,
                text_color=self.COLOR_TEXTO_PRINCIPAL,
                anchor="w",
                height=35,
                command=lambda c=cliente: self._seleccionar_cliente(c)
            ).pack(fill="x", padx=5, pady=2)

        self.dropdown_frame.pack(fill="x", before=self.label_cliente_info)

    def _mostrar_selector_clientes(self):
        selector_window = ctk.CTkToplevel(self.ventana)
        selector_window.title("Selector de Clientes")
        selector_window.geometry("600x500")

        scroll_frame = ctk.CTkScrollableFrame(
            selector_window,
            fg_color=self.COLOR_AZUL_OSCURO
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        for cliente in self.todos_clientes:
            btn_frame = ctk.CTkFrame(
                scroll_frame,
                fg_color=self.COLOR_AZUL_MUY_OSCURO,
                corner_radius=8
            )
            btn_frame.pack(fill="x", pady=5)

            texto = (
                f"👤 {cliente.nombre} {cliente.apellido_paterno} (ID: {cliente.id_cliente})\n"
                f"Estado: {cliente.estado} | Teléfono: {cliente.telefono or 'N/A'}"
            )

            ctk.CTkButton(
                btn_frame,
                text=texto,
                fg_color=self.COLOR_AZUL_MUY_OSCURO,
                hover_color=self.COLOR_MORADO_PRINCIPAL,
                text_color=self.COLOR_TEXTO_PRINCIPAL,
                anchor="w",
                height=50,
                command=lambda c=cliente: (self._seleccionar_cliente(c), selector_window.destroy())
            ).pack(fill="x", padx=5, pady=5)

    def _seleccionar_cliente(self, cliente: Cliente):
        self.cliente_seleccionado = cliente
        self.entry_cliente.delete(0, "end")
        self.entry_cliente.insert(0, f"{cliente.nombre} {cliente.apellido_paterno}")
        self.dropdown_frame.pack_forget()

        self.label_cliente_info.configure(
            text=f"✅ {cliente.nombre} {cliente.apellido_paterno} (ID: {cliente.id_cliente})",
            text_color=self.COLOR_EXITO
        )
        self._actualizar_resumen()

    # ---------- DÍAS ----------

    def _construir_seccion_dias(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            frame,
            text="📅 DÍAS DE RENTA",
            font=("Arial", 13, "bold"),
            text_color=self.COLOR_MORADO_PRINCIPAL
        ).pack(anchor="w", padx=15, pady=(12, 10))

        dias_frame = ctk.CTkFrame(frame, fg_color="transparent")
        dias_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(
            dias_frame,
            text="Días:",
            font=("Arial", 11),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(side="left", padx=(0, 10))

        self.entrada_dias = ctk.CTkEntry(
            dias_frame,
            placeholder_text="2",
            width=80,
            height=35,
            font=("Arial", 12)
        )
        self.entrada_dias.pack(side="left", padx=(0, 15))
        self.entrada_dias.bind("<KeyRelease>", lambda _: self._actualizar_fechas_y_resumen())

        ctk.CTkLabel(
            dias_frame,
            text="Del:",
            font=("Arial", 11),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(side="left", padx=(0, 5))

        self.label_fecha_inicio = ctk.CTkLabel(
            dias_frame,
            text=datetime.now().strftime("%Y-%m-%d"),
            font=("Arial", 11),
            text_color=self.COLOR_EXITO
        )
        self.label_fecha_inicio.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(
            dias_frame,
            text="Al:",
            font=("Arial", 11),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(side="left", padx=(0, 5))

        self.label_fecha_fin = ctk.CTkLabel(
            dias_frame,
            text=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            font=("Arial", 11),
            text_color=self.COLOR_EXITO
        )
        self.label_fecha_fin.pack(side="left")

    def _actualizar_fechas_y_resumen(self):
        try:
            dias = int(self.entrada_dias.get()) if self.entrada_dias.get() else 0
            if dias <= 0:
                dias = 1

            hoy = datetime.now()
            fin = hoy + timedelta(days=dias)

            self.label_fecha_inicio.configure(text=hoy.strftime("%Y-%m-%d"))
            self.label_fecha_fin.configure(text=fin.strftime("%Y-%m-%d"))

            self._actualizar_resumen()
        except:
            pass

    # ---------- DISFRACES ----------

    def _construir_seccion_disfraces(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="both", expand=True, pady=(0, 15))

        ctk.CTkLabel(
            frame,
            text="🎭 DISFRACES",
            font=("Arial", 13, "bold"),
            text_color=self.COLOR_MORADO_PRINCIPAL
        ).pack(anchor="w", padx=15, pady=(12, 10))

        selector_frame = ctk.CTkFrame(frame, fg_color="transparent")
        selector_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.entrada_disfraz = ctk.CTkEntry(
            selector_frame,
            placeholder_text="Búsqueda rápida (código o descripción)...",
            height=35,
            font=("Arial", 11),
            fg_color=self.COLOR_AZUL_OSCURO
        )
        self.entrada_disfraz.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            selector_frame,
            text="➕ Agregar",
            fg_color=self.COLOR_EXITO,
            hover_color="#059669",
            height=35,
            width=100,
            command=self._agregar_disfraz_rapido
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            selector_frame,
            text="📋 Catálogo",
            fg_color=self.COLOR_INFO,
            hover_color="#2563eb",
            height=35,
            width=100,
            command=self._mostrar_selector_disfraces
        ).pack(side="left")

        ctk.CTkLabel(
            frame,
            text="Disfraces Agregados:",
            font=("Arial", 11, "bold"),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(anchor="w", padx=15, pady=(15, 8))

        self.disfraces_frame = ctk.CTkScrollableFrame(
            frame,
            fg_color=self.COLOR_AZUL_OSCURO,
            corner_radius=8
        )
        self.disfraces_frame.pack(fill="both", expand=True, padx=15, pady=(0, 12))

        self.label_vacio_disfraces = ctk.CTkLabel(
            self.disfraces_frame,
            text="• Ninguno agregado",
            font=("Arial", 10),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        )
        self.label_vacio_disfraces.pack(pady=20)

    def _agregar_disfraz_rapido(self):
        termino = self.entrada_disfraz.get().strip()
        if not termino:
            messagebox.showwarning("Advertencia", "Escribe un código o nombre")
            return

        disfraz = self.inventario_controller.buscar_por_codigo(termino)
        if not disfraz:
            resultados = self.inventario_controller.buscar_por_descripcion(termino)
            if resultados:
                disfraz = resultados[0]
            else:
                messagebox.showerror("Error", f"Disfraz '{termino}' no encontrado")
                return

        if disfraz.disponible <= 0:
            messagebox.showwarning("Stock", f"No hay disponibles de {disfraz.descripcion}")
            return

        self.disfraces_agregados.append({
            "codigo": disfraz.codigo_barras,
            "descripcion": disfraz.descripcion,
            "precio_renta": disfraz.precio_renta,
            "disponible": disfraz.disponible,
            "cantidad": 1
        })

        self.entrada_disfraz.delete(0, "end")
        self._actualizar_lista_disfraces()
        self._actualizar_resumen()

    def _mostrar_selector_disfraces(self):
        selector_window = ctk.CTkToplevel(self.ventana)
        selector_window.title("Catálogo de Disfraces")
        selector_window.geometry("800x600")

        scroll_frame = ctk.CTkScrollableFrame(
            selector_window,
            fg_color=self.COLOR_AZUL_OSCURO
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        for disfraz in self.todos_disfraces:
            card = ctk.CTkFrame(
                scroll_frame,
                fg_color=self.COLOR_AZUL_MUY_OSCURO,
                corner_radius=10
            )
            card.pack(fill="x", pady=5)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=12, pady=12, side="left", expand=True)

            ctk.CTkLabel(
                info_frame,
                text=f"🎭 {disfraz.descripcion}",
                font=("Arial", 12, "bold"),
                text_color=self.COLOR_TEXTO_PRINCIPAL
            ).pack(anchor="w")

            info_text = f"Código: {disfraz.codigo_barras} | Talla: {disfraz.talla} | Precio: ${disfraz.precio_renta}/día"
            ctk.CTkLabel(
                info_frame,
                text=info_text,
                font=("Arial", 10),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            ).pack(anchor="w", pady=(3, 0))

            stock_color = self.COLOR_EXITO if disfraz.disponible > 0 else self.COLOR_PELIGRO
            ctk.CTkLabel(
                info_frame,
                text=f"Disponible: {disfraz.disponible}/{disfraz.stock}",
                font=("Arial", 10),
                text_color=stock_color
            ).pack(anchor="w", pady=(3, 0))

            if disfraz.disponible > 0:
                ctk.CTkButton(
                    card,
                    text="✅ Agregar",
                    fg_color=self.COLOR_EXITO,
                    hover_color="#059669",
                    width=100,
                    height=50,
                    command=lambda d=disfraz: (
                        self.disfraces_agregados.append({
                            "codigo": d.codigo_barras,
                            "descripcion": d.descripcion,
                            "precio_renta": d.precio_renta,
                            "disponible": d.disponible,
                            "cantidad": 1
                        }),
                        self._actualizar_lista_disfraces(),
                        self._actualizar_resumen()
                    )
                ).pack(side="right", padx=12, pady=12)

    def _actualizar_lista_disfraces(self):
        for w in self.disfraces_frame.winfo_children():
            w.destroy()

        if not self.disfraces_agregados:
            self.label_vacio_disfraces = ctk.CTkLabel(
                self.disfraces_frame,
                text="• Ninguno agregado",
                font=("Arial", 10),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            )
            self.label_vacio_disfraces.pack(pady=20)
            return

        for i, disfraz in enumerate(self.disfraces_agregados):
            item_frame = ctk.CTkFrame(
                self.disfraces_frame,
                fg_color=self.COLOR_AZUL_MUY_OSCURO,
                corner_radius=8
            )
            item_frame.pack(fill="x", pady=5)

            info = ctk.CTkFrame(item_frame, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=10, pady=10)

            ctk.CTkLabel(
                info,
                text=f"🎭 {disfraz['descripcion']}",
                font=("Arial", 11, "bold"),
                text_color=self.COLOR_TEXTO_PRINCIPAL
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=f"${disfraz['precio_renta']}/día × {disfraz['cantidad']} = ${disfraz['precio_renta'] * disfraz['cantidad']}",
                font=("Arial", 10),
                text_color=self.COLOR_INFO
            ).pack(anchor="w", pady=(2, 0))

            btns_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            btns_frame.pack(side="right", padx=10, pady=10)

            ctk.CTkButton(
                btns_frame,
                text="➖",
                fg_color=self.COLOR_ADVERTENCIA,
                width=35,
                height=35,
                command=lambda idx=i: self._quitar_disfraz(idx)
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                btns_frame,
                text="🗑️",
                fg_color=self.COLOR_PELIGRO,
                width=35,
                height=35,
                command=lambda idx=i: self._eliminar_disfraz(idx)
            ).pack(side="left", padx=3)

    def _quitar_disfraz(self, idx: int):
        if self.disfraces_agregados[idx]["cantidad"] > 1:
            self.disfraces_agregados[idx]["cantidad"] -= 1
        else:
            self.disfraces_agregados.pop(idx)
        self._actualizar_lista_disfraces()
        self._actualizar_resumen()

    def _eliminar_disfraz(self, idx: int):
        self.disfraces_agregados.pop(idx)
        self._actualizar_lista_disfraces()
        self._actualizar_resumen()

    # ---------- NOTAS ----------

    def _construir_seccion_notas(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="x", pady=(0, 0))

        ctk.CTkLabel(
            frame,
            text="📝 NOTAS (Opcional)",
            font=("Arial", 13, "bold"),
            text_color=self.COLOR_MORADO_PRINCIPAL
        ).pack(anchor="w", padx=15, pady=(12, 10))

        self.entrada_notas = ctk.CTkTextbox(
            frame,
            height=80,
            fg_color=self.COLOR_AZUL_OSCURO,
            border_color=self.COLOR_BORDE,
            font=("Arial", 11)
        )
        self.entrada_notas.pack(fill="x", padx=15, pady=(0, 12))

    # ---------- RESUMEN ----------

    def _construir_panel_resumen(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="x", anchor="n")

        ctk.CTkLabel(
            frame,
            text="💰 RESUMEN",
            font=("Arial", 13, "bold"),
            text_color=self.COLOR_MORADO_PRINCIPAL
        ).pack(anchor="w", padx=15, pady=(12, 15))

        campos = [
            ("dias", "Días", "0"),
            ("disfraces", "Disfraces", "0"),
            ("subtotal", "Subtotal", "$0.00"),
            ("descuento", "Descuento", "$0.00"),
            ("total", "TOTAL", "$0.00"),
            ("deposito", "Depósito (50%)", "$0.00"),
        ]

        for key, label, default in campos:
            item_frame = ctk.CTkFrame(frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=15, pady=4)

            ctk.CTkLabel(
                item_frame,
                text=label,
                font=("Arial", 11),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            ).pack(side="left")

            self.resumen_labels[key] = ctk.CTkLabel(
                item_frame,
                text=default,
                font=("Arial", 11, "bold"),
                text_color=self.COLOR_EXITO
            )
            self.resumen_labels[key].pack(side="right")

        ctk.CTkFrame(frame, height=1, fg_color=self.COLOR_BORDE).pack(fill="x", padx=15, pady=10)

        self.resumen_info_cliente = ctk.CTkLabel(
            frame,
            text="❌ Sin cliente",
            font=("Arial", 10),
            text_color=self.COLOR_ADVERTENCIA,
            justify="left",
            wraplength=250
        )
        self.resumen_info_cliente.pack(anchor="w", padx=15, pady=(0, 12))

    def _actualizar_resumen(self):
        try:
            dias = int(self.entrada_dias.get()) if self.entrada_dias.get() else 0
            dias = max(1, dias)

            subtotal = sum(d["precio_renta"] * d["cantidad"] * dias for d in self.disfraces_agregados)
            deposito = subtotal * 0.5

            self.resumen_labels["dias"].configure(text=str(dias))
            self.resumen_labels["disfraces"].configure(text=str(len(self.disfraces_agregados)))
            self.resumen_labels["subtotal"].configure(text=f"${subtotal:.2f}")
            self.resumen_labels["descuento"].configure(text="$0.00")
            self.resumen_labels["total"].configure(text=f"${subtotal:.2f}")
            self.resumen_labels["deposito"].configure(text=f"${deposito:.2f}")

            if self.cliente_seleccionado:
                info = f"👤 {self.cliente_seleccionado.nombre} {self.cliente_seleccionado.apellido_paterno}\n"
                info += f"ID: {self.cliente_seleccionado.id_cliente}"
                self.resumen_info_cliente.configure(text=info, text_color=self.COLOR_EXITO)
            else:
                self.resumen_info_cliente.configure(text="❌ Sin cliente", text_color=self.COLOR_PELIGRO)
        except Exception as e:
            print(f"Error actualizando resumen: {e}")

    # ---------- PREVIEW Y REGISTRO ----------

    def _mostrar_preview(self):
        if not self._validar_formulario():
            return

        dias = int(self.entrada_dias.get())
        subtotal = sum(d["precio_renta"] * d["cantidad"] * dias for d in self.disfraces_agregados)
        deposito = subtotal * 0.5

        mensaje = f"""
🎭 RENTA - CONFIRMACIÓN FINAL

👤 CLIENTE:
   {self.cliente_seleccionado.nombre} {self.cliente_seleccionado.apellido_paterno}
   ID: {self.cliente_seleccionado.id_cliente}

📅 PERÍODO:
   {self.label_fecha_inicio.cget('text')} → {self.label_fecha_fin.cget('text')}
   ({dias} días)

🎭 DISFRACES:
"""
        for d in self.disfraces_agregados:
            mensaje += f"   • {d['descripcion']} x{d['cantidad']} = ${d['precio_renta'] * d['cantidad'] * dias:.2f}\n"

        mensaje += f"""
💰 CÁLCULO:
   Subtotal: ${subtotal:.2f}
   Depósito requerido (50%): ${deposito:.2f}

📝 NOTAS: {self.entrada_notas.get('1.0', 'end').strip() or '(Ninguna)'}

¿Registrar esta renta?
"""

        if messagebox.askyesno("Preview", mensaje):
            self._registrar_renta()

    def _validar_formulario(self) -> bool:
        errores = []

        if not self.cliente_seleccionado:
            errores.append("❌ Selecciona un cliente")
            self.entry_cliente.configure(border_color=self.COLOR_PELIGRO)
        else:
            self.entry_cliente.configure(border_color=self.COLOR_BORDE)

        try:
            dias = int(self.entrada_dias.get())
            if dias <= 0:
                errores.append("❌ Días debe ser mayor a 0")
                self.entrada_dias.configure(border_color=self.COLOR_PELIGRO)
            else:
                self.entrada_dias.configure(border_color=self.COLOR_BORDE)
        except:
            errores.append("❌ Días debe ser un número")
            self.entrada_dias.configure(border_color=self.COLOR_PELIGRO)

        if not self.disfraces_agregados:
            errores.append("❌ Agrega al menos un disfraz")

        if errores:
            messagebox.showerror(
                "⚠️ Validación",
                "\n".join(errores) + "\n\n✏️ Corrige los errores marcados en rojo"
            )
            return False

        return True

    def _registrar_renta(self):
        if not self._validar_formulario():
            return

        try:
            dias = int(self.entrada_dias.get())
            id_usuario = self.dashboard.id_usuario_actual

            exito, msg, id_renta = self.renta_controller.registrar_renta(
                id_cliente=self.cliente_seleccionado.id_cliente,
                id_usuario=id_usuario,
                detalles=self.disfraces_agregados,
                dias_renta=dias
            )

            if exito:
                messagebox.showinfo(
                    "✅ Éxito",
                    f"Renta registrada correctamente\n\n"
                    f"ID Renta: {id_renta}\n"
                    f"Cliente: {self.cliente_seleccionado.nombre} {self.cliente_seleccionado.apellido_paterno}\n"
                    f"Disfraces: {len(self.disfraces_agregados)}"
                )
                self.ventana.destroy()
                self.pantalla_rentas.recargar_rentas()
            else:
                messagebox.showerror("❌ Error", f"No se pudo registrar: {msg}")

        except Exception as e:
            messagebox.showerror("❌ Error Fatal", f"Ocurrió un error:\n{str(e)}")
