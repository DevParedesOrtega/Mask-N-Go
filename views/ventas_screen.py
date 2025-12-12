"""
Módulo: ventas_screen.py
Ubicación: views/ventas_screen.py
Descripción: Pantalla de gestión de ventas + Formulario Premium (basado en rentas_screen.py v4.9)
Sistema: MaskNGO - Renta y Venta de Disfraces
Características:
  - Estilo visual idéntico a rentas_screen.py
  - Cliente, productos, descuento (con motivo si aplica), método de pago
  - Resumen en tiempo real
  - Ticket de venta en PDF
  - Integración con VentaController
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from typing import Optional, List, Dict
from decimal import Decimal, InvalidOperation
import sys
import os
# Asegurar que la raíz del proyecto esté en el path
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)
from controllers.venta_controller import VentaController
from controllers.cliente_controller import ClienteController
from controllers.inventario_controller import InventarioController
from models.venta import Venta
from models.cliente import Cliente
from models.disfraz import Disfraz
# --- PDF ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import subprocess
import platform
from config.database import ConexionDB


class VentasScreen(ctk.CTkFrame):
    """
    Pantalla principal de gestión de ventas.
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
        self.venta_controller = VentaController()
        self.cliente_controller = ClienteController()
        self.inventario_controller = InventarioController()
        self.ventas_lista: List[Dict] = []
        self.construir_interfaz()
        self.cargar_ventas()

    def construir_interfaz(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            header,
            text="🛒 GESTIÓN DE VENTAS",
            font=("Arial", 24, "bold"),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(side="left")
        ctk.CTkButton(
            header,
            text="+ Nueva Venta",
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=self.abrir_formulario_venta,
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
        headers = ["ID", "Folio", "Cliente", "Total", "Método", "Estado", "Acciones"]
        for h in headers:
            ctk.CTkLabel(
                header_frame,
                text=h,
                font=("Arial", 11, "bold"),
                text_color=self.COLOR_MORADO_PRINCIPAL
            ).pack(side="left", fill="x", expand=True, padx=10, pady=10)

        self.ventas_frame = ctk.CTkFrame(tabla_frame, fg_color=self.COLOR_AZUL_OSCURO)
        self.ventas_frame.pack(fill="both", expand=True, padx=1, pady=1)

        self.label_vacio = ctk.CTkLabel(
            self.ventas_frame,
            text="🛒 No hay ventas registradas",
            font=("Arial", 14),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        )
        self.label_vacio.pack(pady=40)

    def cargar_ventas(self):
        try:
            self.ventas_lista = self.venta_controller.obtener_resumen_ventas(limite=20)
            self.actualizar_tabla()
            self.actualizar_stats()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las ventas: {e}")

    def actualizar_tabla(self):
        # Destruir toda la tabla existente
        for w in self.ventas_frame.winfo_children():
            w.destroy()
        if not self.ventas_lista:
            # Crear un nuevo label vacío
            self.label_vacio = ctk.CTkLabel(
                self.ventas_frame,
                text="🛒 No hay ventas registradas",
                font=("Arial", 14),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            )
            self.label_vacio.pack(pady=40)
            return
        # Crear una nueva tabla desde cero
        for venta in self.ventas_lista:
            self.agregar_fila_venta(venta)

    def agregar_fila_venta(self, venta: Dict):
        fila = ctk.CTkFrame(self.ventas_frame, fg_color=self.COLOR_AZUL_OSCURO, height=50)
        fila.pack(fill="x", padx=1, pady=1)
        ctk.CTkLabel(fila, text=str(venta['id_venta']), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkLabel(fila, text=venta['folio'], text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkLabel(fila, text=venta['cliente'], text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkLabel(fila, text=f"${venta['total_final']:.2f}", text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkLabel(fila, text=venta['metodo_pago'], text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        # ✅ CORRECCIÓN: Definir color_estado aquí mismo para evitar errores
        color_estado = self.COLOR_EXITO if venta['estado'] == 'Activa' else self.COLOR_PELIGRO
        ctk.CTkLabel(fila, text=venta['estado'], text_color=color_estado).pack(side="left", fill="x", expand=True, padx=10, pady=10)

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
            command=lambda v=venta: self.ver_detalle_venta(v['id_venta'])
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            acciones_frame,
            text="🖨️ Imprimir",
            fg_color=self.COLOR_PELIGRO,
            hover_color="#dc2626",
            width=50,
            height=30,
            font=("Arial", 10),
            command=lambda v=venta: self.imprimir_ticket_venta(v['id_venta'])
        ).pack(side="left", padx=5)

    def actualizar_stats(self):
        from datetime import date
        stats = self.venta_controller.obtener_estadisticas(fecha=date.today())
        if stats:
            txt = (
                f"📊 Hoy: {stats['cantidad_ventas']} ventas | "
                f"💰 Total: ${stats['total_final']:.2f} | "
                f"🎫 Ticket promedio: ${stats['ticket_promedio']:.2f}"
            )
            self.label_stats.configure(text=txt)
        else:
            self.label_stats.configure(text="📊 Sin estadísticas del día")

    def ver_detalle_venta(self, id_venta: int):
        venta = self.venta_controller.obtener_venta_completa(id_venta)
        if venta:
            messagebox.showinfo("Detalle de Venta", venta.resumen_estado())
        else:
            messagebox.showerror("Error", "No se pudo cargar el detalle de la venta.")

    def imprimir_ticket_venta(self, id_venta: int):
        try:
            venta = self.venta_controller.obtener_venta_completa(id_venta)
            if not venta:
                messagebox.showerror("Error", f"No se encontró la venta ID {id_venta}")
                return
            db = ConexionDB()
            db.conectar()
            query_cliente = "SELECT * FROM CLIENTES WHERE Id_cliente = %s"
            resultado_cliente = db.ejecutar_query(query_cliente, (venta.id_cliente,))
            if not resultado_cliente:
                cliente = Cliente(id_cliente=venta.id_cliente, nombre="Cliente", apellido_paterno="Desconocido", telefono="", estado="Activo")
            else:
                columnas_cliente = ['Id_cliente', 'Nombre', 'Apellido_Paterno', 'Telefono', 'Fecha_Registro', 'Estado']
                cliente_data = dict(zip(columnas_cliente, resultado_cliente[0]))
                cliente = Cliente(
                    id_cliente=cliente_data['Id_cliente'],
                    nombre=cliente_data['Nombre'],
                    apellido_paterno=cliente_data['Apellido_Paterno'],
                    telefono=cliente_data['Telefono'],
                    estado=cliente_data['Estado'],
                    fecha_registro=cliente_data['Fecha_Registro']
                )

            detalles_disfraces = []
            for d in venta.detalles:
                query_disfraz = "SELECT Descripcion FROM INVENTARIO WHERE Codigo_Barras = %s"
                res = db.ejecutar_query(query_disfraz, (d.codigo_barras,))
                desc = res[0][0] if res else "Desconocido"
                detalles_disfraces.append({
                    'codigo_barras': d.codigo_barras,
                    'descripcion': desc,
                    'precio_unitario': d.precio_unitario,
                    'cantidad': d.cantidad,
                    'subtotal': d.subtotal
                })

            self._generar_pdf_ticket_venta(
                id_venta=venta.id_venta,
                folio=venta.folio,
                cliente=cliente,
                detalles=detalles_disfraces,
                total_bruto=venta.total,
                descuento_monto=venta.descuento_monto,
                descuento_porcentaje=venta.descuento_porcentaje,
                motivo_descuento=venta.motivo_descuento,
                total_final=venta.obtener_total_final(),
                metodo_pago=venta.metodo_pago,
                motivo_venta=venta.motivo_venta,
                notas=venta.notas,
                fecha_venta=venta.fecha_venta
            )
        except Exception as e:
            print(f"[ERROR] No se pudo generar el ticket de venta: {e}")
            messagebox.showerror("Error", f"Error al generar el ticket: {e}")

    def _generar_pdf_ticket_venta(self, **kwargs):
        try:
            id_venta = kwargs['id_venta']
            nombre_archivo = f"ticket_venta_{id_venta}.pdf"
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            estilo_titulo = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=12, alignment=1, textColor=colors.black)
            estilo_encabezado = ParagraphStyle('HeaderBusiness', parent=styles['Normal'], fontSize=14, alignment=1, spaceAfter=6, textColor=colors.black)
            estilo_detalle = ParagraphStyle('Detail', parent=styles['Normal'], fontSize=10, spaceAfter=4, textColor=colors.black)
            story.append(Paragraph("TICKET DE VENTA", estilo_titulo))
            story.append(Spacer(1, 0.1 * inch))
            nombre_negocio, direccion_negocio, telefono_negocio = self._obtener_datos_negocio()
            story.append(Paragraph(nombre_negocio, estilo_encabezado))
            story.append(Paragraph(direccion_negocio, estilo_detalle))
            story.append(Paragraph(f"Tel: {telefono_negocio}", estilo_detalle))
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph("-" * 50, estilo_detalle))
            story.append(Spacer(1, 0.05 * inch))
            story.append(Paragraph(f"<b>Folio:</b> {kwargs['folio']}", estilo_detalle))
            story.append(Paragraph(f"<b>Cliente:</b> {kwargs['cliente'].nombre_completo()}", estilo_detalle))
            story.append(Paragraph(f"<b>Fecha:</b> {kwargs['fecha_venta'].strftime('%Y-%m-%d %H:%M')}", estilo_detalle))
            story.append(Paragraph(f"<b>Método de Pago:</b> {kwargs['metodo_pago']}", estilo_detalle))
            if kwargs.get('motivo_venta'):
                story.append(Paragraph(f"<b>Motivo:</b> {kwargs['motivo_venta']}", estilo_detalle))
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph("<b>Productos:</b>", estilo_detalle))
            data = [['Código', 'Descripción', 'Precio', 'Cant.', 'Subtotal']]
            for d in kwargs['detalles']:
                data.append([
                    d['codigo_barras'],
                    d['descripcion'],
                    f"${d['precio_unitario']:.2f}",
                    str(d['cantidad']),
                    f"${d['subtotal']:.2f}"
                ])
            tabla = Table(data, colWidths=[1.0*inch, 2.0*inch, 0.7*inch, 0.5*inch, 0.8*inch])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 8),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            story.append(tabla)
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph(f"<b>Subtotal:</b> ${kwargs['total_bruto']:.2f}", estilo_detalle))
            if kwargs['descuento_monto'] > 0:
                story.append(Paragraph(f"<b>Descuento ({kwargs['descuento_porcentaje']}%):</b> -${kwargs['descuento_monto']:.2f}", estilo_detalle))
            story.append(Paragraph(f"<b>TOTAL:</b> <b>${kwargs['total_final']:.2f}</b>", estilo_detalle))
            if kwargs.get('notas'):
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph(f"<b>Notas:</b> {kwargs['notas']}", estilo_detalle))
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph("-" * 50, estilo_detalle))
            story.append(Paragraph("¡Gracias por su compra!", estilo_detalle))
            story.append(Paragraph("Conservar este comprobante.", estilo_detalle))
            doc.build(story)
            self._abrir_archivo(nombre_archivo)
        except Exception as e:
            messagebox.showerror("Error PDF", str(e))

    def _obtener_datos_negocio(self):
        try:
            db = ConexionDB()
            db.conectar()
            query = "SELECT Parametro, Valor FROM PARAMETROS_SISTEMA WHERE Parametro IN ('Nombre_Negocio', 'Direccion_Negocio', 'Telefono_Negocio')"
            resultados = db.ejecutar_query(query)
            nombre = "MaskNGO - Renta y Venta de Disfraces"
            direccion = "Calle Ficticia #123, Ciudad, Estado"
            telefono = "618-123-4567"
            if resultados:
                for param, valor in resultados:
                    if param == 'Nombre_Negocio': nombre = valor
                    elif param == 'Direccion_Negocio': direccion = valor
                    elif param == 'Telefono_Negocio': telefono = valor
            return nombre, direccion, telefono
        except:
            return "MaskNGO", "Sin dirección", "Sin teléfono"

    def _abrir_archivo(self, filepath):
        try:
            sistema = platform.system()
            if sistema == "Windows":
                subprocess.run(["start", filepath], shell=True)
            elif sistema == "Darwin":
                subprocess.run(["open", filepath])
            else:
                subprocess.run(["xdg-open", filepath])
        except Exception as e:
            messagebox.showwarning("Advertencia", "PDF generado, pero no se pudo abrir automáticamente.")

    def abrir_formulario_venta(self):
        if not self.dashboard.id_usuario_actual:
            messagebox.showerror("Error", "❌ No hay usuario logueado. Inicia sesión primero.")
            return
        ventana_modal = ctk.CTkToplevel(self)
        ventana_modal.title("Nueva Venta - Premium")
        ventana_modal.geometry("1200x700")
        ventana_modal.transient(self.winfo_toplevel())
        ventana_modal.grab_set()
        FormularioVentaV1(ventana_modal, self.dashboard, self.cargar_ventas)

    def recargar_ventas(self):
        self.cargar_ventas()


# ==================== FORMULARIO DE VENTA ====================
class FormularioVentaV1(ctk.CTkFrame):
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

    METODOS_PAGO = ["Efectivo", "tarjeta", "Transferencia"]

    def __init__(self, ventana, dashboard_ref, callback_recarga):
        super().__init__(ventana, fg_color="#1e293b")
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.ventana = ventana
        self.dashboard = dashboard_ref
        self.callback_recarga = callback_recarga
        self.venta_controller = VentaController()
        self.cliente_controller = ClienteController()
        self.inventario_controller = InventarioController()
        self.cliente_seleccionado: Optional[Cliente] = None
        self.productos_agregados: List[Dict] = []
        self.todos_clientes: List[Cliente] = []
        self.todos_disfraces: List[Disfraz] = []
        self.resumen_labels: Dict[str, ctk.CTkLabel] = {}
        self.dropdown_frame_productos = None  # Inicializado aquí

        self._cargar_datos_iniciales()
        self._construir_ui()

    def _cargar_datos_iniciales(self):
        try:
            self.todos_clientes = self.cliente_controller.listar_todos(solo_activos=True)
        except Exception as e:
            print(f"Error cargando clientes: {e}")
            self.todos_clientes = []
        try:
            self.todos_disfraces = self.inventario_controller.listar_disfraces(solo_activos=True)
        except Exception as e:
            print(f"Error cargando disfraces: {e}")
            self.todos_disfraces = []

    def _construir_ui(self):
        ctk.CTkLabel(
            self,
            text="Registrar Nueva Venta",
            font=("Arial", 22, "bold"),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(pady=(0, 10))

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        # --- Columna izquierda (formulario) ---
        left_scroll = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
        left_scroll.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=(0, 5))

        # --- Columna derecha (resumen) ---
        right_col = ctk.CTkFrame(main_container, fg_color="transparent")
        right_col.pack(side="right", fill="y", expand=False, padx=(15, 0), pady=(0, 5))

        self._construir_seccion_cliente(left_scroll)
        self._construir_seccion_metodo_pago(left_scroll)
        self._construir_seccion_descuento(left_scroll)
        self._construir_seccion_motivo_venta(left_scroll)
        self._construir_seccion_productos(left_scroll)
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
            text="✅ Registrar Venta",
            fg_color=self.COLOR_MORADO_PRINCIPAL,
            hover_color=self.COLOR_MORADO_HOVER,
            command=self._registrar_venta,
            width=150,
            height=40
        ).pack(side="right", padx=5)

    # ========== SECCIÓN CLIENTE ==========
    def _construir_seccion_cliente(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(frame, text="👤 CLIENTE", font=("Arial", 13, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(12, 10))
        entry_frame = ctk.CTkFrame(frame, fg_color="transparent")
        entry_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.entry_cliente = ctk.CTkEntry(entry_frame, placeholder_text="Escribe nombre o ID del cliente...", height=40, font=("Arial", 12), fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE)
        self.entry_cliente.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_cliente.bind("<KeyRelease>", lambda _: self._filtrar_clientes())
        ctk.CTkButton(entry_frame, text="🔍", width=40, height=40, fg_color=self.COLOR_INFO, hover_color="#2563eb", command=self._mostrar_selector_clientes).pack(side="left")
        self.dropdown_frame = ctk.CTkFrame(frame, fg_color=self.COLOR_AZUL_OSCURO, corner_radius=8)
        self.dropdown_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.dropdown_frame.pack_forget()
        self.label_cliente_info = ctk.CTkLabel(frame, text="❌ No hay cliente seleccionado", font=("Arial", 11), text_color=self.COLOR_ADVERTENCIA)
        self.label_cliente_info.pack(anchor="w", padx=15, pady=(0, 12))

    def _filtrar_clientes(self):
        termino = self.entry_cliente.get().lower().strip()
        for w in self.dropdown_frame.winfo_children():
            w.destroy()
        if not termino:
            self.dropdown_frame.pack_forget()
            return
        coincidencias = [c for c in self.todos_clientes if termino in f"{c.nombre} {c.apellido_paterno}".lower() or termino in str(c.id_cliente)]
        if not coincidencias:
            ctk.CTkLabel(self.dropdown_frame, text="No hay coincidencias", font=("Arial", 10), text_color=self.COLOR_TEXTO_SECUNDARIO).pack(fill="x", padx=10, pady=5)
            self.dropdown_frame.pack(fill="x", before=self.label_cliente_info)
            return
        for cliente in coincidencias[:5]:
            texto = f"#{cliente.id_cliente} - {cliente.nombre} {cliente.apellido_paterno}"
            ctk.CTkButton(self.dropdown_frame, text=texto, fg_color=self.COLOR_AZUL_OSCURO, hover_color=self.COLOR_MORADO_PRINCIPAL, text_color=self.COLOR_TEXTO_PRINCIPAL, anchor="w", height=35, command=lambda c=cliente: self._seleccionar_cliente(c)).pack(fill="x", padx=5, pady=2)
        self.dropdown_frame.pack(fill="x", before=self.label_cliente_info)

    def _mostrar_selector_clientes(self):
        selector_window = ctk.CTkToplevel(self.ventana)
        selector_window.title("Selector de Clientes")
        selector_window.geometry("600x500")
        selector_window.attributes("-topmost", True)
        scroll_frame = ctk.CTkScrollableFrame(selector_window, fg_color=self.COLOR_AZUL_OSCURO)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        for cliente in self.todos_clientes:
            btn_frame = ctk.CTkFrame(scroll_frame, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=8)
            btn_frame.pack(fill="x", pady=5)
            texto = f"👤 {cliente.nombre} {cliente.apellido_paterno} (ID: {cliente.id_cliente})\nEstado: {cliente.estado} | Teléfono: {cliente.telefono or 'N/A'}"
            ctk.CTkButton(btn_frame, text=texto, fg_color=self.COLOR_AZUL_MUY_OSCURO, hover_color=self.COLOR_MORADO_PRINCIPAL, text_color=self.COLOR_TEXTO_PRINCIPAL, anchor="w", height=50, command=lambda c=cliente: (self._seleccionar_cliente(c), selector_window.destroy())).pack(fill="x", padx=5, pady=5)

    def _seleccionar_cliente(self, cliente: Cliente):
        self.cliente_seleccionado = cliente
        self.entry_cliente.delete(0, "end")
        self.entry_cliente.insert(0, f"{cliente.nombre} {cliente.apellido_paterno}")
        self.dropdown_frame.pack_forget()
        self.label_cliente_info.configure(text=f"✅ {cliente.nombre} {cliente.apellido_paterno} (ID: {cliente.id_cliente})", text_color=self.COLOR_EXITO)
        self._actualizar_resumen()

    # ========== SECCIÓN MÉTODO DE PAGO ==========
    def _construir_seccion_metodo_pago(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(frame, text="💳 MÉTODO DE PAGO", font=("Arial", 13, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(12, 10))
        self.metodo_pago_var = ctk.StringVar(value=self.METODOS_PAGO[0])
        for metodo in self.METODOS_PAGO:
            ctk.CTkRadioButton(
                frame,
                text=metodo,
                variable=self.metodo_pago_var,
                value=metodo,
                command=self._actualizar_resumen
            ).pack(anchor="w", padx=30, pady=5)

    # ========== SECCIÓN DESCUENTO ==========
    def _construir_seccion_descuento(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(frame, text="🏷️ DESCUENTO (Opcional – requiere motivo si > 0%)", font=("Arial", 13, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(12, 10))
        monto_frame = ctk.CTkFrame(frame, fg_color="transparent")
        monto_frame.pack(fill="x", padx=15, pady=(0, 8))
        ctk.CTkLabel(monto_frame, text="Porcentaje (%):", font=("Arial", 11), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", padx=(0, 10))
        self.entrada_descuento = ctk.CTkEntry(monto_frame, placeholder_text="0", width=80, height=35, font=("Arial", 12))
        self.entrada_descuento.pack(side="left")
        self.entrada_descuento.bind("<KeyRelease>", lambda _: self._actualizar_resumen())
        motivo_frame = ctk.CTkFrame(frame, fg_color="transparent")
        motivo_frame.pack(fill="x", padx=15, pady=(8, 10))
        ctk.CTkLabel(motivo_frame, text="Motivo:", font=("Arial", 11), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", padx=(0, 10))
        self.entrada_motivo_descuento = ctk.CTkEntry(motivo_frame, placeholder_text="Ej. Cliente frecuente", height=35, font=("Arial", 12))
        self.entrada_motivo_descuento.pack(side="left", fill="x", expand=True)

    # ========== SECCIÓN MOTIVO DE VENTA ==========
    def _construir_seccion_motivo_venta(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(frame, text="🎉 MOTIVO DE VENTA (Opcional)", font=("Arial", 13, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(12, 10))
        self.entrada_motivo_venta = ctk.CTkEntry(frame, placeholder_text="Ej. Halloween, Cumpleaños...", height=35, font=("Arial", 12))
        self.entrada_motivo_venta.pack(fill="x", padx=15, pady=(0, 10))

    # ========== SECCIÓN PRODUCTOS ==========
    def _construir_seccion_productos(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="both", expand=True, pady=(0, 15))
        ctk.CTkLabel(frame, text="📦 PRODUCTOS", font=("Arial", 13, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(12, 10))
        selector_frame = ctk.CTkFrame(frame, fg_color="transparent")
        selector_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.entrada_producto = ctk.CTkEntry(selector_frame, placeholder_text="Búsqueda rápida (código o descripción)...", height=35, font=("Arial", 11), fg_color=self.COLOR_AZUL_OSCURO)
        self.entrada_producto.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entrada_producto.bind("<KeyRelease>", lambda _: self._filtrar_productos())
        ctk.CTkButton(selector_frame, text="➕ Agregar", fg_color=self.COLOR_EXITO, hover_color="#059669", height=35, width=100, command=self._agregar_producto_rapido).pack(side="left", padx=(0, 5))
        ctk.CTkButton(selector_frame, text="📋 Catálogo", fg_color=self.COLOR_INFO, hover_color="#2563eb", height=35, width=100, command=self._mostrar_selector_productos).pack(side="left")

        # --- Dropdown flotante (no empaquetado aquí) ---
        self.dropdown_frame_productos = None

        ctk.CTkLabel(frame, text="Productos Agregados:", font=("Arial", 11, "bold"), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=15, pady=(15, 8))
        self.productos_frame = ctk.CTkScrollableFrame(frame, fg_color=self.COLOR_AZUL_OSCURO, corner_radius=8)
        self.productos_frame.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        self.label_vacio_productos = ctk.CTkLabel(self.productos_frame, text="• Ninguno agregado", font=("Arial", 10), text_color=self.COLOR_TEXTO_SECUNDARIO)
        self.label_vacio_productos.pack(pady=20)

    def _filtrar_productos(self):
        termino = self.entrada_producto.get().strip().lower()
        # Destruir dropdown anterior
        if self.dropdown_frame_productos and self.dropdown_frame_productos.winfo_exists():
            self.dropdown_frame_productos.destroy()
            self.dropdown_frame_productos = None
        if not termino:
            return
        if not self.todos_disfraces:
            self._crear_y_mostrar_dropdown_error("❌ Error: No hay productos cargados")
            return
        coincidencias = [
            d for d in self.todos_disfraces
            if d.disponible > 0 and (
                termino in str(d.codigo_barras).lower() or 
                termino in str(d.descripcion).lower()
            )
        ][:5]
        if not coincidencias:
            self._crear_y_mostrar_dropdown_error("No hay coincidencias")
            return
        # Crear nuevo dropdown
        self.dropdown_frame_productos = ctk.CTkFrame(self, fg_color=self.COLOR_AZUL_OSCURO, corner_radius=8, width=100)
        for disfraz in coincidencias:
            texto = f"{disfraz.codigo_barras} – {disfraz.descripcion} (${disfraz.precio_venta}) [Disp: {disfraz.disponible}]"
            ctk.CTkButton(
                self.dropdown_frame_productos,
                text=texto,
                fg_color=self.COLOR_AZUL_OSCURO,
                hover_color=self.COLOR_MORADO_PRINCIPAL,
                text_color=self.COLOR_TEXTO_PRINCIPAL,
                anchor="w",
                height=40,
                command=lambda d=disfraz: self._seleccionar_producto_desde_dropdown(d)
            ).pack(fill="x", padx=5, pady=2)
        self._posicionar_dropdown()

    def _crear_y_mostrar_dropdown_error(self, mensaje):
        self.dropdown_frame_productos = ctk.CTkFrame(self, fg_color=self.COLOR_AZUL_OSCURO, corner_radius=8, width=100)
        ctk.CTkLabel(
            self.dropdown_frame_productos,
            text=mensaje,
            font=("Arial", 10),
            text_color=self.COLOR_TEXTO_SECUNDARIO
        ).pack(fill="x", padx=10, pady=5)
        self._posicionar_dropdown()

    def _posicionar_dropdown(self):
        """Posiciona el dropdown debajo del campo de búsqueda."""
        if not self.dropdown_frame_productos:
            return
        self.update_idletasks()
        # Geometría relativa
        entrada_x = self.entrada_producto.winfo_rootx() - self.winfo_rootx()
        entrada_y = self.entrada_producto.winfo_rooty() - self.winfo_rooty()
        entrada_height = self.entrada_producto.winfo_height()
        dropdown_width = self.entrada_producto.winfo_width()
        # ✅ Ancho en constructor (no en place)
        self.dropdown_frame_productos.configure(width=dropdown_width)
        # Posicionar
        self.dropdown_frame_productos.place(
            x=entrada_x,
            y=entrada_y + entrada_height + 2,
            anchor="nw"
        )
        # ✅ Enlazar clic a la ventana modal
        self.ventana.bind("<Button-1>", self._manejar_click_fuera)

    def _manejar_click_fuera(self, event):
        try:
            if not self.dropdown_frame_productos or not self.dropdown_frame_productos.winfo_exists():
                return
            x, y = event.x_root, event.y_root
            frame_x1 = self.dropdown_frame_productos.winfo_rootx()
            frame_y1 = self.dropdown_frame_productos.winfo_rooty()
            frame_x2 = frame_x1 + self.dropdown_frame_productos.winfo_width()
            frame_y2 = frame_y1 + self.dropdown_frame_productos.winfo_height()
            if not (frame_x1 <= x <= frame_x2 and frame_y1 <= y <= frame_y2):
                self._ocultar_dropdown()
        except Exception as e:
            print(f"[DEBUG] Error en _manejar_click_fuera: {e}")
            self._ocultar_dropdown()

    def _ocultar_dropdown(self):
        if self.dropdown_frame_productos and self.dropdown_frame_productos.winfo_exists():
            self.dropdown_frame_productos.destroy()
        self.dropdown_frame_productos = None
        self.ventana.unbind("<Button-1>")

    def _seleccionar_producto_desde_dropdown(self, disfraz: Disfraz):
        if disfraz.disponible <= 0:
            messagebox.showwarning("Stock", f"No hay disponibles de {disfraz.descripcion}")
            self._ocultar_dropdown()
            return
        for item in self.productos_agregados:
            if item["codigo_barras"] == disfraz.codigo_barras:
                item["cantidad"] += 1
                self.entrada_producto.delete(0, "end")
                self._ocultar_dropdown()
                self._actualizar_lista_productos()
                self._actualizar_resumen()
                return
        self.productos_agregados.append({
            "codigo_barras": disfraz.codigo_barras,
            "descripcion": disfraz.descripcion,
            "precio_unitario": Decimal(str(disfraz.precio_venta)),
            "disponible": disfraz.disponible,
            "cantidad": 1
        })
        self.entrada_producto.delete(0, "end")
        self._ocultar_dropdown()
        self._actualizar_lista_productos()
        self._actualizar_resumen()

    def _agregar_producto_rapido(self):
        termino = self.entrada_producto.get().strip()
        if not termino:
            messagebox.showwarning("Advertencia", "Escribe un código o nombre")
            return
        disfraz = self.inventario_controller.buscar_por_codigo(termino)
        if not disfraz:
            resultados = self.inventario_controller.buscar_por_descripcion(termino)
            if resultados: disfraz = resultados[0]
            else:
                messagebox.showerror("Error", f"Producto '{termino}' no encontrado")
                return
        if disfraz.disponible <= 0:
            messagebox.showwarning("Stock", f"No hay disponibles de {disfraz.descripcion}")
            return
        for item in self.productos_agregados:
            if item["codigo_barras"] == disfraz.codigo_barras:
                item["cantidad"] += 1
                self.entrada_producto.delete(0, "end")
                self._actualizar_lista_productos()
                self._actualizar_resumen()
                return
        self.productos_agregados.append({
            "codigo_barras": disfraz.codigo_barras,
            "descripcion": disfraz.descripcion,
            "precio_unitario": Decimal(str(disfraz.precio_venta)),
            "disponible": disfraz.disponible,
            "cantidad": 1
        })
        self.entrada_producto.delete(0, "end")
        self._ocultar_dropdown()
        self._actualizar_lista_productos()
        self._actualizar_resumen()

    def _mostrar_selector_productos(self):
        selector_window = ctk.CTkToplevel(self.ventana)
        selector_window.title("Catálogo de Productos")
        selector_window.geometry("800x600")
        selector_window.attributes("-topmost", True)
        scroll_frame = ctk.CTkScrollableFrame(selector_window, fg_color=self.COLOR_AZUL_OSCURO)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        for disfraz in self.todos_disfraces:
            card = ctk.CTkFrame(scroll_frame, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
            card.pack(fill="x", pady=5)
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=12, pady=12, side="left", expand=True)
            ctk.CTkLabel(info_frame, text=f"🎭 {disfraz.descripcion}", font=("Arial", 12, "bold"), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w")
            info_text = f"Código: {disfraz.codigo_barras} | Talla: {disfraz.talla} | Precio: ${disfraz.precio_venta}"
            ctk.CTkLabel(info_frame, text=info_text, font=("Arial", 10), text_color=self.COLOR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(3, 0))
            stock_color = self.COLOR_EXITO if disfraz.disponible > 0 else self.COLOR_PELIGRO
            ctk.CTkLabel(info_frame, text=f"Disponible: {disfraz.disponible}/{disfraz.stock}", font=("Arial", 10), text_color=stock_color).pack(anchor="w", pady=(3, 0))
            if disfraz.disponible > 0:
                ctk.CTkButton(card, text="✅ Agregar", fg_color=self.COLOR_EXITO, hover_color="#059669", width=100, height=50, command=lambda d=disfraz: (
                    self.productos_agregados.append({
                        "codigo_barras": d.codigo_barras,
                        "descripcion": d.descripcion,
                        "precio_unitario": Decimal(str(d.precio_venta)),
                        "disponible": d.disponible,
                        "cantidad": 1
                    }),
                    self._actualizar_lista_productos(),
                    self._actualizar_resumen()
                )).pack(side="right", padx=12, pady=12)

    def _actualizar_lista_productos(self):
        for w in self.productos_frame.winfo_children():
            w.destroy()
        if not self.productos_agregados:
            self.label_vacio_productos = ctk.CTkLabel(self.productos_frame, text="• Ninguno agregado", font=("Arial", 10), text_color=self.COLOR_TEXTO_SECUNDARIO)
            self.label_vacio_productos.pack(pady=20)
            return
        for i, prod in enumerate(self.productos_agregados):
            item_frame = ctk.CTkFrame(self.productos_frame, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=8)
            item_frame.pack(fill="x", pady=5)
            info = ctk.CTkFrame(item_frame, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            ctk.CTkLabel(info, text=f"🎭 {prod['descripcion']}", font=("Arial", 11, "bold"), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w")
            ctk.CTkLabel(info, text=f"${prod['precio_unitario']} × {prod['cantidad']} = ${prod['precio_unitario'] * prod['cantidad']}", font=("Arial", 10), text_color=self.COLOR_INFO).pack(anchor="w", pady=(2, 0))
            btns_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            btns_frame.pack(side="right", padx=10, pady=10)
            ctk.CTkButton(btns_frame, text="➖", fg_color=self.COLOR_ADVERTENCIA, width=35, height=35, command=lambda idx=i: self._quitar_producto(idx)).pack(side="left", padx=3)
            ctk.CTkButton(btns_frame, text="🗑️", fg_color=self.COLOR_PELIGRO, width=35, height=35, command=lambda idx=i: self._eliminar_producto(idx)).pack(side="left", padx=3)

    def _quitar_producto(self, idx: int):
        if self.productos_agregados[idx]["cantidad"] > 1:
            self.productos_agregados[idx]["cantidad"] -= 1
        else:
            self.productos_agregados.pop(idx)
        self._actualizar_lista_productos()
        self._actualizar_resumen()

    def _eliminar_producto(self, idx: int):
        self.productos_agregados.pop(idx)
        self._actualizar_lista_productos()
        self._actualizar_resumen()

    # ========== NOTAS ==========
    def _construir_seccion_notas(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="x", pady=(0, 0))
        ctk.CTkLabel(frame, text="📝 NOTAS (Opcional)", font=("Arial", 13, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(12, 10))
        self.entrada_notas = ctk.CTkTextbox(frame, height=80, fg_color=self.COLOR_AZUL_OSCURO, border_color=self.COLOR_BORDE, font=("Arial", 11))
        self.entrada_notas.pack(fill="x", padx=15, pady=(0, 12))

    # ========== PANEL RESUMEN ==========
    def _construir_panel_resumen(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="y", anchor="n")
        ctk.CTkLabel(frame, text="💰 RESUMEN", font=("Arial", 13, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(12, 15))
        campos = [
            ("productos", "Productos", "0"),
            ("subtotal", "Subtotal", "$0.00"),
            ("descuento", "Descuento", "$0.00"),
            ("total", "TOTAL", "$0.00"),
            ("metodo_pago", "Método", "Efectivo"),
        ]
        for key, label, default in campos:
            item_frame = ctk.CTkFrame(frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=15, pady=4)
            ctk.CTkLabel(item_frame, text=label, font=("Arial", 11), text_color=self.COLOR_TEXTO_SECUNDARIO).pack(side="left")
            self.resumen_labels[key] = ctk.CTkLabel(item_frame, text=default, font=("Arial", 11, "bold"), text_color=self.COLOR_EXITO)
            self.resumen_labels[key].pack(side="right")
        ctk.CTkFrame(frame, height=1, fg_color=self.COLOR_BORDE).pack(fill="x", padx=15, pady=10)
        self.resumen_info_cliente = ctk.CTkLabel(frame, text="❌ Sin cliente", font=("Arial", 10), text_color=self.COLOR_ADVERTENCIA, justify="left", wraplength=250)
        self.resumen_info_cliente.pack(anchor="w", padx=15, pady=(0, 12))

    # ========== ACTUALIZACIÓN Y VALIDACIÓN ==========
    def _actualizar_resumen(self):
        try:
            subtotal = sum(p["precio_unitario"] * p["cantidad"] for p in self.productos_agregados)
            subtotal = subtotal if subtotal > 0 else Decimal('0.00')
            descuento = Decimal('0.00')
            descuento_porcentaje = Decimal('0.00')
            motivo_descuento = self.entrada_motivo_descuento.get().strip()
            descuento_str = self.entrada_descuento.get().strip()
            if descuento_str:
                try:
                    descuento_porcentaje = Decimal(descuento_str)
                    if descuento_porcentaje < 0: descuento_porcentaje = Decimal('0.00')
                    if descuento_porcentaje > 100: descuento_porcentaje = Decimal('100')
                    descuento = subtotal * (descuento_porcentaje / Decimal('100'))
                except (InvalidOperation, ValueError):
                    pass
            total = subtotal - descuento
            total = max(total, Decimal('0.00'))
            self.resumen_labels["productos"].configure(text=str(len(self.productos_agregados)))
            self.resumen_labels["subtotal"].configure(text=f"${subtotal:.2f}")
            self.resumen_labels["descuento"].configure(text=f"-${descuento:.2f}")
            self.resumen_labels["total"].configure(text=f"${total:.2f}")
            self.resumen_labels["metodo_pago"].configure(text=self.metodo_pago_var.get())
            if self.cliente_seleccionado:
                info = f"👤 {self.cliente_seleccionado.nombre} {self.cliente_seleccionado.apellido_paterno}\nID: {self.cliente_seleccionado.id_cliente}"
                self.resumen_info_cliente.configure(text=info, text_color=self.COLOR_EXITO)
            else:
                self.resumen_info_cliente.configure(text="❌ Sin cliente", text_color=self.COLOR_PELIGRO)
        except Exception as e:
            print(f"Error actualizando resumen: {e}")

    def _validar_formulario(self) -> bool:
        errores = []
        if not self.cliente_seleccionado:
            errores.append("❌ Selecciona un cliente")
            self.entry_cliente.configure(border_color=self.COLOR_PELIGRO)
        else:
            self.entry_cliente.configure(border_color=self.COLOR_BORDE)
        if not self.productos_agregados:
            errores.append("❌ Agrega al menos un producto")
        # Validar descuento con motivo
        descuento_str = self.entrada_descuento.get().strip()
        motivo_descuento = self.entrada_motivo_descuento.get().strip()
        if descuento_str:
            try:
                descuento_val = Decimal(descuento_str)
                if descuento_val > 0 and not motivo_descuento:
                    errores.append("❌ Descuento requiere motivo de justificación")
                    self.entrada_motivo_descuento.configure(border_color=self.COLOR_PELIGRO)
                else:
                    self.entrada_motivo_descuento.configure(border_color=self.COLOR_BORDE)
            except:
                errores.append("❌ Descuento inválido")
                self.entrada_descuento.configure(border_color=self.COLOR_PELIGRO)
        else:
            self.entrada_descuento.configure(border_color=self.COLOR_BORDE)
        if errores:
            messagebox.showerror("⚠️ Validación", "\n".join(errores) + "\n✏️ Corrige los errores marcados en rojo")
            return False
        return True

    def _mostrar_preview(self):
        if not self._validar_formulario():
            return
        subtotal = sum(p["precio_unitario"] * p["cantidad"] for p in self.productos_agregados)
        descuento = Decimal('0.00')
        descuento_porcentaje = Decimal('0.00')
        descuento_str = self.entrada_descuento.get().strip()
        if descuento_str:
            try:
                descuento_porcentaje = Decimal(descuento_str)
                if descuento_porcentaje > 0:
                    descuento = subtotal * (descuento_porcentaje / Decimal('100'))
            except:
                pass
        total = subtotal - descuento
        mensaje = f"""
🛒 VENTA - CONFIRMACIÓN FINAL
👤 CLIENTE:
   {self.cliente_seleccionado.nombre} {self.cliente_seleccionado.apellido_paterno}
   ID: {self.cliente_seleccionado.id_cliente}
💳 MÉTODO: {self.metodo_pago_var.get()}
📦 PRODUCTOS:
"""
        for p in self.productos_agregados:
            linea_total = p["precio_unitario"] * p["cantidad"]
            mensaje += f"   • {p['descripcion']} x{p['cantidad']} = ${linea_total:.2f}\n"
        mensaje += f"""
💰 CÁLCULO:
   Subtotal: ${subtotal:.2f}
   Descuento ({descuento_porcentaje}%): -${descuento:.2f}
   TOTAL: ${total:.2f}
🎉 Motivo: {self.entrada_motivo_venta.get().strip() or '(Ninguno)'}
📝 Notas: {self.entrada_notas.get('1.0', 'end').strip() or '(Ninguna)'}
¿Registrar esta venta?
"""
        if messagebox.askyesno("Preview", mensaje):
            self._registrar_venta()

    def _registrar_venta(self):
        if not self._validar_formulario():
            return
        try:
            subtotal = sum(p["precio_unitario"] * p["cantidad"] for p in self.productos_agregados)
            descuento_porcentaje = Decimal('0.00')
            descuento_str = self.entrada_descuento.get().strip()
            if descuento_str:
                try:
                    descuento_porcentaje = Decimal(descuento_str)
                except:
                    pass
            motivo_descuento = self.entrada_motivo_descuento.get().strip() if descuento_porcentaje > 0 else None
            motivo_venta = self.entrada_motivo_venta.get().strip() or None
            notas = self.entrada_notas.get("1.0", "end").strip() or None
            detalles = [{"codigo_barras": p["codigo_barras"], "cantidad": p["cantidad"]} for p in self.productos_agregados]
            # ✅ Corrección clave: asegurar que id_usuario sea entero
            id_usuario = int(self.dashboard.id_usuario_actual)
            exito, msg, id_venta = self.venta_controller.registrar_venta(
                id_cliente=self.cliente_seleccionado.id_cliente,
                id_usuario=id_usuario,
                detalles=detalles,
                metodo_pago=self.metodo_pago_var.get(),
                descuento_porcentaje=float(descuento_porcentaje),
                motivo_descuento=motivo_descuento,
                motivo_venta=motivo_venta
            )
            if exito:
                messagebox.showinfo("✅ Éxito", f"Venta registrada correctamente\nID Venta: {id_venta}\nCliente: {self.cliente_seleccionado.nombre}")
                self.ventana.destroy()
                self.callback_recarga()
            else:
                messagebox.showerror("❌ Error", f"No se pudo registrar: {msg}")
        except Exception as e:
            messagebox.showerror("❌ Error Fatal", f"Ocurrió un error:\n{str(e)}")