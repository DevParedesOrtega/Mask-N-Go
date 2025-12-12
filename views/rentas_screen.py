"""
Módulo: rentas_screen.py (VERSIÓN 4.9 - CORREGIDA Y FUNCIONAL)
Ubicación: views/rentas_screen.py
Descripción: Pantalla de gestión de rentas + Formulario Premium v4.9
Sistema: MaskNGO - Renta y Venta de Disfraces
Correcciones clave:
  ✅ Eliminados campos inexistentes: Apellido_Materno, Direccion.
  ✅ Mapeo correcto de columnas en CLIENTES (6 campos reales).
  ✅ Uso seguro de tuplas desde mysql-connector.
  ✅ Compatible con modelo Cliente() existente.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from decimal import Decimal, InvalidOperation
import sys
import os

# Asegurar que la raíz del proyecto esté en el path
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ruta_raiz)

from controllers.renta_controller import RentaController
from controllers.cliente_controller import ClienteController
from controllers.inventario_controller import InventarioController
from models.renta import Renta
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
            text="篓 No hay rentas registradas",
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
            self.label_vacio.pack(pady=40)
            return
        for renta in self.rentas_lista:
            self.agregar_fila_renta(renta)

    def agregar_fila_renta(self, renta: Renta):
        fila = ctk.CTkFrame(self.rentas_frame, fg_color=self.COLOR_AZUL_OSCURO, height=50)
        fila.pack(fill="x", padx=1, pady=1)

        ctk.CTkLabel(fila, text=str(renta.id_renta), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkLabel(fila, text=str(renta.id_cliente), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkLabel(fila, text=str(renta.dias_renta), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)

        color_estado = self.COLOR_EXITO if renta.esta_activa() else self.COLOR_ADVERTENCIA
        ctk.CTkLabel(fila, text=renta.estado, text_color=color_estado).pack(side="left", fill="x", expand=True, padx=10, pady=10)

        fecha_renta = renta.fecha_renta.strftime("%Y-%m-%d") if renta.fecha_renta else "N/A"
        ctk.CTkLabel(fila, text=fecha_renta, text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)

        fecha_dev = renta.fecha_devolucion.strftime("%Y-%m-%d") if renta.fecha_devolucion else "N/A"
        ctk.CTkLabel(fila, text=fecha_dev, text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", fill="x", expand=True, padx=10, pady=10)

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

        ctk.CTkButton(
            acciones_frame,
            text="🖨️ Imprimir",
            fg_color=self.COLOR_PELIGRO,
            hover_color="#dc2626",
            width=50,
            height=30,
            font=("Arial", 10),
            command=lambda r=renta: self.imprimir_ticket_renta(r)
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

    # === FUNCIÓN CORREGIDA ===
    def imprimir_ticket_renta(self, renta: Renta):
        """
        Genera el PDF del ticket para una renta específica.
        CORREGIDO: Solo usa los 6 campos reales de la tabla CLIENTES.
        """
        try:
            db = ConexionDB()
            db.conectar()

            # --- Renta ---
            query_renta = "SELECT * FROM RENTAS WHERE Id_Renta = %s"
            resultado_renta = db.ejecutar_query(query_renta, (renta.id_renta,))
            if not resultado_renta:
                messagebox.showerror("Error", f"No se encontró la renta ID {renta.id_renta}")
                return

            # ORDEN REAL DE COLUMNAS EN RENTAS
            columnas_renta = ['Id_Renta', 'Id_Cliente', 'Id_Usuario', 'Fecha_Renta', 'Fecha_Devolucion', 'Fecha_Devuelto', 'Penalizacion', 'Dias_Renta', 'Total', 'Deposito', 'Estado']
            renta_data = dict(zip(columnas_renta, resultado_renta[0]))

            # --- Cliente ---
            query_cliente = "SELECT * FROM CLIENTES WHERE Id_Cliente = %s"
            resultado_cliente = db.ejecutar_query(query_cliente, (renta_data['Id_Cliente'],))
            if not resultado_cliente:
                messagebox.showerror("Error", f"No se encontró el cliente ID {renta_data['Id_Cliente']}")
                return

            # ✅ ORDEN CORRECTO: 6 columnas reales (sin Apellido_Materno ni Direccion)
            columnas_cliente = ['Id_cliente', 'Nombre', 'Apellido_Paterno', 'Telefono', 'Fecha_Registro', 'Estado']
            cliente_data = dict(zip(columnas_cliente, resultado_cliente[0]))

            # ✅ Crear Cliente solo con los argumentos que espera tu modelo
            cliente = Cliente(
                id_cliente=cliente_data['Id_cliente'],
                nombre=cliente_data['Nombre'],
                apellido_paterno=cliente_data['Apellido_Paterno'],
                telefono=cliente_data['Telefono'],
                estado=cliente_data['Estado'],
                fecha_registro=cliente_data['Fecha_Registro']
            )

            # --- Detalles de disfraces ---
            query_detalles = "SELECT * FROM DETALLE_RENTAS WHERE Id_Renta = %s"
            resultados_detalles = db.ejecutar_query(query_detalles, (renta.id_renta,))
            detalles_disfraces = []
            if resultados_detalles:
                for detalle in resultados_detalles:
                    columnas_detalle = ['Id_DetalleRenta', 'Id_Renta', 'Codigo_Barras', 'Cantidad', 'Precio_Unitario', 'Subtotal']
                    detalle_dict = dict(zip(columnas_detalle, detalle))

                    # INVENTARIO también devuelve tuplas → usar índices
                    query_disfraz = "SELECT Descripcion, Precio_Renta FROM INVENTARIO WHERE Codigo_Barras = %s"
                    resultado_disfraz = db.ejecutar_query(query_disfraz, (detalle_dict['Codigo_Barras'],))
                    if resultado_disfraz:
                        descripcion = resultado_disfraz[0][0]  # Índice 0 = Descripcion
                        precio_renta = resultado_disfraz[0][1]  # Índice 1 = Precio_Renta
                    else:
                        descripcion = "Desconocido"
                        precio_renta = 0.0

                    detalles_disfraces.append({
                        'codigo_barras': detalle_dict['Codigo_Barras'],
                        'descripcion': descripcion,
                        'precio_renta': Decimal(str(precio_renta)),
                        'cantidad': detalle_dict['Cantidad'],
                        'subtotal': detalle_dict['Subtotal']
                    })

            total_calculado = sum(d['subtotal'] for d in detalles_disfraces) if detalles_disfraces else Decimal('0.00')
            deposito_calculado = Decimal(str(renta_data.get('Deposito', '0.00')))
            notas = ""

            self._generar_pdf_ticket_para_impresion(
                id_renta=renta.id_renta,
                cliente=cliente,
                detalles=detalles_disfraces,
                dias=renta_data['Dias_Renta'],
                total=total_calculado,
                deposito=deposito_calculado,
                fecha_inicio=renta_data['Fecha_Renta'],
                fecha_fin=renta_data['Fecha_Devolucion'],
                notas=notas
            )

        except Exception as e:
            print(f"[ERROR] No se pudo generar el ticket para impresión: {e}")
            messagebox.showerror("Error", f"No se pudo generar el ticket para impresión: {e}")

    def _generar_pdf_ticket_para_impresion(self, id_renta: int, cliente: Cliente, detalles: List[Dict], dias: int, total: Decimal, deposito: Decimal, fecha_inicio: datetime, fecha_fin: datetime, notas: str = ""):
        try:
            nombre_archivo = f"ticket_renta_{id_renta}.pdf"
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            story = []

            styles = getSampleStyleSheet()
            estilo_titulo = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=12, alignment=1, textColor=colors.black)
            estilo_encabezado = ParagraphStyle('HeaderBusiness', parent=styles['Normal'], fontSize=14, alignment=1, spaceAfter=6, textColor=colors.black)
            estilo_detalle = ParagraphStyle('Detail', parent=styles['Normal'], fontSize=10, spaceAfter=4, textColor=colors.black)

            story.append(Paragraph("TICKET DE RENTA", estilo_titulo))
            story.append(Spacer(1, 0.1 * inch))

            nombre_negocio, direccion_negocio, telefono_negocio = self._obtener_datos_negocio()
            story.append(Paragraph(nombre_negocio, estilo_encabezado))
            story.append(Paragraph(direccion_negocio, estilo_detalle))
            story.append(Paragraph(f"Tel: {telefono_negocio}", estilo_detalle))
            story.append(Spacer(1, 0.1 * inch))

            story.append(Paragraph("-" * 50, estilo_detalle))
            story.append(Spacer(1, 0.05 * inch))

            story.append(Paragraph(f"<b>ID Renta:</b> {id_renta}", estilo_detalle))
            story.append(Paragraph(f"<b>Cliente:</b> {cliente.nombre_completo()}", estilo_detalle))
            story.append(Paragraph(f"<b>ID Cliente:</b> {cliente.id_cliente}", estilo_detalle))
            story.append(Paragraph(f"<b>Fecha Renta:</b> {fecha_inicio.strftime('%Y-%m-%d')}", estilo_detalle))
            story.append(Paragraph(f"<b>Fecha Devolución:</b> {fecha_fin.strftime('%Y-%m-%d')}", estilo_detalle))
            story.append(Paragraph(f"<b>Días de Renta:</b> {dias}", estilo_detalle))
            story.append(Spacer(1, 0.1 * inch))

            story.append(Paragraph("<b>Disfraces Rentados:</b>", estilo_detalle))
            data = [['Código', 'Descripción', 'Precio/Día', 'Cantidad', 'Subtotal']]
            for d in detalles:
                subtotal = d['precio_renta'] * d['cantidad'] * dias
                data.append([d['codigo_barras'], d['descripcion'], f"${d['precio_renta']:.2f}", str(d['cantidad']), f"${subtotal:.2f}"])

            tabla = Table(data, colWidths=[1.0*inch, 2.0*inch, 0.8*inch, 0.6*inch, 0.8*inch])
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

            story.append(Paragraph(f"<b>Total Renta:</b> ${total:.2f}", estilo_detalle))
            story.append(Paragraph(f"<b>Depósito Pagado:</b> ${deposito:.2f}", estilo_detalle))
            story.append(Spacer(1, 0.1 * inch))

            if notas:
                story.append(Paragraph(f"<b>Notas:</b> {notas}", estilo_detalle))
                story.append(Spacer(1, 0.1 * inch))

            story.append(Paragraph("-" * 50, estilo_detalle))
            story.append(Spacer(1, 0.05 * inch))
            story.append(Paragraph("¡Gracias por su confianza!", estilo_detalle))
            story.append(Paragraph("Recuerde devolver los disfraces en tiempo y forma.", estilo_detalle))

            doc.build(story)
            self._abrir_archivo(nombre_archivo)

        except Exception as e:
            print(f"[ERROR PDF]: {e}")
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

    def abrir_formulario_renta(self):
        if not self.dashboard.id_usuario_actual:
            messagebox.showerror("Error", "❌ No hay usuario logueado. Inicia sesión primero.")
            return
        ventana_modal = ctk.CTkToplevel(self)
        ventana_modal.title("Nueva Renta - Premium")
        ventana_modal.geometry("1200x750")
        ventana_modal.transient(self.winfo_toplevel())
        ventana_modal.grab_set()
        FormularioRentaV4(ventana_modal, self.dashboard, self.cargar_rentas)

    def recargar_rentas(self):
        self.cargar_rentas()


# ==================== FORMULARIO PREMIUM V4.9 (SIN CAMBIOS) ====================
# El siguiente bloque es una copia EXACTA de tu FormularioRentaV4 de Pasted_Text_1764976554787.txt
# No se realizan cambios porque ya está correctamente adaptado a tu modelo Cliente.

class FormularioRentaV4(ctk.CTkFrame):
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
    
    def __init__(self, ventana, dashboard_ref, callback_recarga):
        super().__init__(ventana, fg_color="#1e293b")
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.ventana = ventana
        self.dashboard = dashboard_ref
        self.callback_recarga = callback_recarga
        self.renta_controller = RentaController()
        self.cliente_controller = ClienteController()
        self.inventario_controller = InventarioController()
        self.cliente_seleccionado: Optional[Cliente] = None
        self.disfraces_agregados: List[Dict] = []
        self.todos_clientes: List[Cliente] = []
        self.todos_disfraces: List[Disfraz] = []
        self.resumen_labels: Dict[str, ctk.CTkLabel] = {}
        self.tipo_descuento = ctk.StringVar(value="porcentaje")
        self.tipo_deposito = ctk.StringVar(value="porcentaje")
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
            print(f"[INFO] Disfraces cargados: {len(self.todos_disfraces)}")
            for i, d in enumerate(self.todos_disfraces[:3]):
                print(f"   {i+1}. Código: {d.codigo_barras}, Descripción: {d.descripcion}, Disponible: {d.disponible}")
        except Exception as e:
            print(f"Error cargando disfraces: {e}")
            self.todos_disfraces = []

    def _construir_ui(self):
        ctk.CTkLabel(
            self,
            text="Registrar Nueva Renta",
            font=("Arial", 22, "bold"),
            text_color=self.COLOR_TEXTO_PRINCIPAL
        ).pack(pady=(0, 10))
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        left_scroll = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
        left_scroll.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=(0, 5))
        right_col = ctk.CTkFrame(main_container, fg_color="transparent")
        right_col.pack(side="right", fill="y", expand=False, padx=(15, 0), pady=(0, 5))
        self._construir_seccion_cliente(left_scroll)
        self._construir_seccion_dias(left_scroll)
        self._construir_seccion_descuento(left_scroll)
        self._construir_seccion_deposito(left_scroll)
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

    # ========== SECCIÓN DÍAS ==========
    def _construir_seccion_dias(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(frame, text="📅 DÍAS DE RENTA", font=("Arial", 13, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(12, 10))
        dias_frame = ctk.CTkFrame(frame, fg_color="transparent")
        dias_frame.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkLabel(dias_frame, text="Días:", font=("Arial", 11), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", padx=(0, 10))
        self.entrada_dias = ctk.CTkEntry(dias_frame, placeholder_text="2", width=80, height=35, font=("Arial", 12))
        self.entrada_dias.pack(side="left", padx=(0, 15))
        self.entrada_dias.bind("<KeyRelease>", lambda _: self._actualizar_fechas_y_resumen())
        ctk.CTkLabel(dias_frame, text="Del:", font=("Arial", 11), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", padx=(0, 5))
        self.label_fecha_inicio = ctk.CTkLabel(dias_frame, text=datetime.now().strftime("%Y-%m-%d"), font=("Arial", 11), text_color=self.COLOR_EXITO)
        self.label_fecha_inicio.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(dias_frame, text="Al:", font=("Arial", 11), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", padx=(0, 5))
        self.label_fecha_fin = ctk.CTkLabel(dias_frame, text=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"), font=("Arial", 11), text_color=self.COLOR_EXITO)
        self.label_fecha_fin.pack(side="left")
    
    def _actualizar_fechas_y_resumen(self):
        try:
            dias = int(self.entrada_dias.get()) if self.entrada_dias.get() else 0
            if dias <= 0: dias = 1
            hoy = datetime.now()
            fin = hoy + timedelta(days=dias)
            self.label_fecha_inicio.configure(text=hoy.strftime("%Y-%m-%d"))
            self.label_fecha_fin.configure(text=fin.strftime("%Y-%m-%d"))
            self._actualizar_resumen()
        except:
            pass

    # ========== DESCUENTO Y DEPÓSITO ==========
    def _construir_seccion_descuento(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(frame, text="💸 DESCUENTO (Opcional)", font=("Arial", 13, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(12, 10))
        tipo_frame = ctk.CTkFrame(frame, fg_color="transparent")
        tipo_frame.pack(fill="x", padx=15, pady=(0, 8))
        ctk.CTkRadioButton(tipo_frame, text="%", variable=self.tipo_descuento, value="porcentaje", command=self._actualizar_resumen).pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(tipo_frame, text="$", variable=self.tipo_descuento, value="pesos", command=self._actualizar_resumen).pack(side="left")
        monto_frame = ctk.CTkFrame(frame, fg_color="transparent")
        monto_frame.pack(fill="x", padx=15, pady=(0, 10))
        ctk.CTkLabel(monto_frame, text="Monto:", font=("Arial", 11), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", padx=(0, 10))
        self.entrada_descuento = ctk.CTkEntry(monto_frame, placeholder_text="0", width=100, height=35, font=("Arial", 12))
        self.entrada_descuento.pack(side="left")
        self.entrada_descuento.bind("<KeyRelease>", lambda _: self._actualizar_resumen())
    
    def _construir_seccion_deposito(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(frame, text="💰 DEPÓSITO (Personalizable)", font=("Arial", 13, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(12, 10))
        tipo_frame = ctk.CTkFrame(frame, fg_color="transparent")
        tipo_frame.pack(fill="x", padx=15, pady=(0, 8))
        ctk.CTkRadioButton(tipo_frame, text="% del total", variable=self.tipo_deposito, value="porcentaje", command=self._actualizar_resumen).pack(side="left", padx=(0, 15))
        ctk.CTkRadioButton(tipo_frame, text="Monto fijo", variable=self.tipo_deposito, value="pesos", command=self._actualizar_resumen).pack(side="left")
        monto_frame = ctk.CTkFrame(frame, fg_color="transparent")
        monto_frame.pack(fill="x", padx=15, pady=(0, 10))
        ctk.CTkLabel(monto_frame, text="Monto:", font=("Arial", 11), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(side="left", padx=(0, 10))
        self.entrada_deposito = ctk.CTkEntry(monto_frame, placeholder_text="50 (para 50%) o 200 (para $200)", width=150, height=35, font=("Arial", 12))
        self.entrada_deposito.pack(side="left")
        self.entrada_deposito.bind("<KeyRelease>", lambda _: self._actualizar_resumen())

    # ========== SECCIÓN DISFRACES ==========
    def _construir_seccion_disfraces(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=10)
        frame.pack(fill="both", expand=True, pady=(0, 15))
        ctk.CTkLabel(frame, text="🎭 DISFRACES", font=("Arial", 13, "bold"), text_color=self.COLOR_MORADO_PRINCIPAL).pack(anchor="w", padx=15, pady=(12, 10))
        selector_frame = ctk.CTkFrame(frame, fg_color="transparent")
        selector_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.entrada_disfraz = ctk.CTkEntry(selector_frame, placeholder_text="Búsqueda rápida (código o descripción)...", height=35, font=("Arial", 11), fg_color=self.COLOR_AZUL_OSCURO)
        self.entrada_disfraz.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entrada_disfraz.bind("<KeyRelease>", lambda _: self._filtrar_disfraces())
        ctk.CTkButton(selector_frame, text="➕ Agregar", fg_color=self.COLOR_EXITO, hover_color="#059669", height=35, width=100, command=self._agregar_disfraz_rapido).pack(side="left", padx=(0, 5))
        ctk.CTkButton(selector_frame, text="📋 Catálogo", fg_color=self.COLOR_INFO, hover_color="#2563eb", height=35, width=100, command=self._mostrar_selector_disfraces).pack(side="left")
        self.dropdown_frame_disfraces = ctk.CTkFrame(frame, fg_color=self.COLOR_AZUL_OSCURO, corner_radius=8)
        self.dropdown_frame_disfraces.pack(fill="x", padx=15, pady=(0, 10))
        self.dropdown_frame_disfraces.pack_forget()
        ctk.CTkLabel(frame, text="Disfraces Agregados:", font=("Arial", 11, "bold"), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=15, pady=(15, 8))
        self.disfraces_frame = ctk.CTkScrollableFrame(frame, fg_color=self.COLOR_AZUL_OSCURO, corner_radius=8)
        self.disfraces_frame.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        self.label_vacio_disfraces = ctk.CTkLabel(self.disfraces_frame, text="• Ninguno agregado", font=("Arial", 10), text_color=self.COLOR_TEXTO_SECUNDARIO)
        self.label_vacio_disfraces.pack(pady=20)

    def _filtrar_disfraces(self):
        """Filtra disfraces por código de barras o descripción."""
        termino = self.entrada_disfraz.get().strip().lower()
        print(f"[DEBUG] Búsqueda de disfraces: '{termino}'")
        for w in self.dropdown_frame_disfraces.winfo_children():
            w.destroy()
        if not termino:
            self.dropdown_frame_disfraces.pack_forget()
            return
        if not self.todos_disfraces:
            print("[ERROR] self.todos_disfraces está vacío. No se pueden buscar disfraces.")
            ctk.CTkLabel(
                self.dropdown_frame_disfraces,
                text="❌ Error: No hay disfraces cargados",
                font=("Arial", 10),
                text_color=self.COLOR_PELIGRO
            ).pack(fill="x", padx=10, pady=5)
            self.dropdown_frame_disfraces.pack(fill="x", pady=(0, 10))
            return
        coincidencias = []
        for disfraz in self.todos_disfraces:
            try:
                codigo_str = str(disfraz.codigo_barras).lower() if disfraz.codigo_barras else ""
                desc_str = str(disfraz.descripcion).lower() if disfraz.descripcion else ""
                if termino.lower() in codigo_str or termino.lower() in desc_str:
                    coincidencias.append(disfraz)
            except Exception as e:
                print(f"[ERROR] Fallo al procesar disfraz {disfraz}: {e}")
        if not coincidencias:
            ctk.CTkLabel(
                self.dropdown_frame_disfraces,
                text="No hay coincidencias",
                font=("Arial", 10),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            ).pack(fill="x", padx=10, pady=5)
            self.dropdown_frame_disfraces.pack(fill="x", pady=(0, 10))
            return
        mostrados = 0
        for disfraz in coincidencias:
            if disfraz.disponible <= 0:
                continue
            if mostrados >= 5:
                break
            texto = f"{disfraz.codigo_barras} – {disfraz.descripcion} (${disfraz.precio_renta}/día) [Disp: {disfraz.disponible}]"
            ctk.CTkButton(
                self.dropdown_frame_disfraces,
                text=texto,
                fg_color=self.COLOR_AZUL_OSCURO,
                hover_color=self.COLOR_MORADO_PRINCIPAL,
                text_color=self.COLOR_TEXTO_PRINCIPAL,
                anchor="w",
                height=40,
                command=lambda d=disfraz: self._seleccionar_disfraz_desde_dropdown(d)
            ).pack(fill="x", padx=5, pady=3)
            mostrados += 1
        if mostrados == 0:
            ctk.CTkLabel(
                self.dropdown_frame_disfraces,
                text="No hay coincidencias con stock disponible",
                font=("Arial", 10),
                text_color=self.COLOR_TEXTO_SECUNDARIO
            ).pack(fill="x", padx=10, pady=5)
        self.dropdown_frame_disfraces.pack(fill="x", pady=(0, 10))

    def _seleccionar_disfraz_desde_dropdown(self, disfraz: Disfraz):
        """Selecciona un disfraz desde el dropdown de búsqueda."""
        if disfraz.disponible <= 0:
            messagebox.showwarning("Stock", f"No hay disponibles de {disfraz.descripcion}")
            return
        for item in self.disfraces_agregados:
            if item["codigo_barras"] == disfraz.codigo_barras:
                item["cantidad"] += 1
                self.entrada_disfraz.delete(0, "end")
                self.dropdown_frame_disfraces.pack_forget()
                self._actualizar_lista_disfraces()
                self._actualizar_resumen()
                return
        self.disfraces_agregados.append({
            "codigo_barras": disfraz.codigo_barras,
            "descripcion": disfraz.descripcion,
            "precio_renta": Decimal(str(disfraz.precio_renta)),
            "disponible": disfraz.disponible,
            "cantidad": 1
        })
        self.entrada_disfraz.delete(0, "end")
        self.dropdown_frame_disfraces.pack_forget()
        self._actualizar_lista_disfraces()
        self._actualizar_resumen()

    def _agregar_disfraz_rapido(self):
        termino = self.entrada_disfraz.get().strip()
        if not termino:
            messagebox.showwarning("Advertencia", "Escribe un código o nombre")
            return
        disfraz = self.inventario_controller.buscar_por_codigo(termino)
        if not disfraz:
            resultados = self.inventario_controller.buscar_por_descripcion(termino)
            if resultados: disfraz = resultados[0]
            else:
                messagebox.showerror("Error", f"Disfraz '{termino}' no encontrado")
                return
        if disfraz.disponible <= 0:
            messagebox.showwarning("Stock", f"No hay disponibles de {disfraz.descripcion}")
            return
        for item in self.disfraces_agregados:
            if item["codigo_barras"] == disfraz.codigo_barras:
                item["cantidad"] += 1
                self.entrada_disfraz.delete(0, "end")
                self._actualizar_lista_disfraces()
                self._actualizar_resumen()
                return
        self.disfraces_agregados.append({
            "codigo_barras": disfraz.codigo_barras,
            "descripcion": disfraz.descripcion,
            "precio_renta": Decimal(str(disfraz.precio_renta)),
            "disponible": disfraz.disponible,
            "cantidad": 1
        })
        self.entrada_disfraz.delete(0, "end")
        self.dropdown_frame_disfraces.pack_forget()
        self._actualizar_lista_disfraces()
        self._actualizar_resumen()

    def _mostrar_selector_disfraces(self):
        selector_window = ctk.CTkToplevel(self.ventana)
        selector_window.title("Catálogo de Disfraces")
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
            info_text = f"Código: {disfraz.codigo_barras} | Talla: {disfraz.talla} | Precio: ${disfraz.precio_renta}/día"
            ctk.CTkLabel(info_frame, text=info_text, font=("Arial", 10), text_color=self.COLOR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(3, 0))
            stock_color = self.COLOR_EXITO if disfraz.disponible > 0 else self.COLOR_PELIGRO
            ctk.CTkLabel(info_frame, text=f"Disponible: {disfraz.disponible}/{disfraz.stock}", font=("Arial", 10), text_color=stock_color).pack(anchor="w", pady=(3, 0))
            if disfraz.disponible > 0:
                ctk.CTkButton(card, text="✅ Agregar", fg_color=self.COLOR_EXITO, hover_color="#059669", width=100, height=50, command=lambda d=disfraz: (
                    self.disfraces_agregados.append({
                        "codigo_barras": d.codigo_barras,
                        "descripcion": d.descripcion,
                        "precio_renta": Decimal(str(d.precio_renta)),
                        "disponible": d.disponible,
                        "cantidad": 1
                    }),
                    self._actualizar_lista_disfraces(),
                    self._actualizar_resumen()
                )).pack(side="right", padx=12, pady=12)

    def _actualizar_lista_disfraces(self):
        for w in self.disfraces_frame.winfo_children():
            w.destroy()
        if not self.disfraces_agregados:
            self.label_vacio_disfraces = ctk.CTkLabel(self.disfraces_frame, text="• Ninguno agregado", font=("Arial", 10), text_color=self.COLOR_TEXTO_SECUNDARIO)
            self.label_vacio_disfraces.pack(pady=20)
            return
        for i, disfraz in enumerate(self.disfraces_agregados):
            item_frame = ctk.CTkFrame(self.disfraces_frame, fg_color=self.COLOR_AZUL_MUY_OSCURO, corner_radius=8)
            item_frame.pack(fill="x", pady=5)
            info = ctk.CTkFrame(item_frame, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            ctk.CTkLabel(info, text=f"🎭 {disfraz['descripcion']}", font=("Arial", 11, "bold"), text_color=self.COLOR_TEXTO_PRINCIPAL).pack(anchor="w")
            ctk.CTkLabel(info, text=f"${disfraz['precio_renta']}/día × {disfraz['cantidad']} = ${disfraz['precio_renta'] * disfraz['cantidad']}", font=("Arial", 10), text_color=self.COLOR_INFO).pack(anchor="w", pady=(2, 0))
            btns_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            btns_frame.pack(side="right", padx=10, pady=10)
            ctk.CTkButton(btns_frame, text="➖", fg_color=self.COLOR_ADVERTENCIA, width=35, height=35, command=lambda idx=i: self._quitar_disfraz(idx)).pack(side="left", padx=3)
            ctk.CTkButton(btns_frame, text="🗑️", fg_color=self.COLOR_PELIGRO, width=35, height=35, command=lambda idx=i: self._eliminar_disfraz(idx)).pack(side="left", padx=3)

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
            ("dias", "Días", "0"),
            ("disfraces", "Disfraces", "0"),
            ("subtotal", "Subtotal", "$0.00"),
            ("descuento", "Descuento", "$0.00"),
            ("total", "TOTAL", "$0.00"),
            ("deposito", "Depósito", "$0.00"),
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

    # ========== ACTUALIZACIÓN, VALIDACIÓN Y REGISTRO ==========
    def _actualizar_resumen(self):
        try:
            dias = int(self.entrada_dias.get()) if self.entrada_dias.get() else 0
            dias = max(1, dias)
            subtotal_base = sum(d["precio_renta"] * d["cantidad"] * dias for d in self.disfraces_agregados)
            subtotal_base = subtotal_base if subtotal_base > 0 else Decimal('0.00')
            descuento = Decimal('0.00')
            tipo_desc = self.tipo_descuento.get()
            monto_desc_str = self.entrada_descuento.get().strip()
            if monto_desc_str:
                try:
                    monto_desc = Decimal(monto_desc_str)
                    if monto_desc < 0: monto_desc = Decimal('0.00')
                    if tipo_desc == "porcentaje":
                        if monto_desc > 100: monto_desc = Decimal('100')
                        descuento = subtotal_base * (monto_desc / Decimal('100'))
                    else:
                        if monto_desc > subtotal_base: monto_desc = subtotal_base
                        descuento = monto_desc
                except (InvalidOperation, ValueError):
                    descuento = Decimal('0.00')
            subtotal = subtotal_base - descuento
            subtotal = max(subtotal, Decimal('0.00'))
            deposito = Decimal('0.00')
            tipo_dep = self.tipo_deposito.get()
            monto_dep_str = self.entrada_deposito.get().strip()
            if monto_dep_str:
                try:
                    monto_dep = Decimal(monto_dep_str)
                    if monto_dep < 0: monto_dep = Decimal('0.00')
                    if tipo_dep == "porcentaje":
                        if monto_dep > 100: monto_dep = Decimal('100')
                        deposito = subtotal * (monto_dep / Decimal('100'))
                    else:
                        deposito = monto_dep
                except (InvalidOperation, ValueError):
                    deposito = Decimal('0.00')
            total = subtotal
            self.resumen_labels["dias"].configure(text=str(dias))
            self.resumen_labels["disfraces"].configure(text=str(len(self.disfraces_agregados)))
            self.resumen_labels["subtotal"].configure(text=f"${subtotal_base:.2f}")
            self.resumen_labels["descuento"].configure(text=f"-${descuento:.2f}")
            self.resumen_labels["total"].configure(text=f"${total:.2f}")
            self.resumen_labels["deposito"].configure(text=f"${deposito:.2f}")
            if self.cliente_seleccionado:
                info = f"👤 {self.cliente_seleccionado.nombre} {self.cliente_seleccionado.apellido_paterno}\nID: {self.cliente_seleccionado.id_cliente}"
                self.resumen_info_cliente.configure(text=info, text_color=self.COLOR_EXITO)
            else:
                self.resumen_info_cliente.configure(text="❌ Sin cliente", text_color=self.COLOR_PELIGRO)
        except Exception as e:
            print(f"Error actualizando resumen: {e}")

    def _mostrar_preview(self):
        if not self._validar_formulario():
            return
        dias = int(self.entrada_dias.get())
        subtotal_base = sum(d["precio_renta"] * d["cantidad"] * dias for d in self.disfraces_agregados)
        subtotal_base = subtotal_base if subtotal_base > 0 else Decimal('0.00')
        descuento = Decimal('0.00')
        tipo_desc = self.tipo_descuento.get()
        monto_desc_str = self.entrada_descuento.get().strip()
        if monto_desc_str:
            try:
                monto_desc = Decimal(monto_desc_str)
                if monto_desc >= 0:
                    if tipo_desc == "porcentaje":
                        monto_desc = min(monto_desc, Decimal('100'))
                        descuento = subtotal_base * (monto_desc / Decimal('100'))
                    else:
                        descuento = min(monto_desc, subtotal_base)
            except:
                pass
        subtotal = max(subtotal_base - descuento, Decimal('0.00'))
        deposito = Decimal('0.00')
        tipo_dep = self.tipo_deposito.get()
        monto_dep_str = self.entrada_deposito.get().strip()
        if monto_dep_str:
            try:
                monto_dep = Decimal(monto_dep_str)
                if monto_dep >= 0:
                    if tipo_dep == "porcentaje":
                        monto_dep = min(monto_dep, Decimal('100'))
                        deposito = subtotal * (monto_dep / Decimal('100'))
                    else:
                        deposito = monto_dep
            except:
                pass
        total = subtotal
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
            linea_total = d["precio_renta"] * d["cantidad"] * dias
            mensaje += f"   • {d['descripcion']} x{d['cantidad']} = ${linea_total:.2f}\n"
        mensaje += f"""
💰 CÁLCULO:
   Subtotal base: ${subtotal_base:.2f}
   Descuento ({'%' if tipo_desc == 'porcentaje' else '$'}{monto_desc_str or '0'}): -${descuento:.2f}
   TOTAL: ${total:.2f}
   Depósito ({'%' if tipo_dep == 'porcentaje' else '$'}{monto_dep_str or '0'}): ${deposito:.2f}
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
            messagebox.showerror("⚠️ Validación", "\n".join(errores) + "\n✏️ Corrige los errores marcados en rojo")
            return False
        return True

    def _registrar_renta(self):
        if not self._validar_formulario():
            return
        try:
            dias = int(self.entrada_dias.get())
            id_usuario = self.dashboard.id_usuario_actual
            subtotal_base = sum(d["precio_renta"] * d["cantidad"] * dias for d in self.disfraces_agregados)
            subtotal_base = subtotal_base if subtotal_base > 0 else Decimal('0.00')
            descuento = Decimal('0.00')
            tipo_desc = self.tipo_descuento.get()
            monto_desc_str = self.entrada_descuento.get().strip()
            if monto_desc_str:
                try:
                    monto_desc = Decimal(monto_desc_str)
                    if monto_desc >= 0:
                        if tipo_desc == "porcentaje":
                            monto_desc = min(monto_desc, Decimal('100'))
                            descuento = subtotal_base * (monto_desc / Decimal('100'))
                        else:
                            descuento = min(monto_desc, subtotal_base)
                except:
                    pass
            total = max(subtotal_base - descuento, Decimal('0.00'))
            deposito = Decimal('0.00')
            tipo_dep = self.tipo_deposito.get()
            monto_dep_str = self.entrada_deposito.get().strip()
            if monto_dep_str:
                try:
                    monto_dep = Decimal(monto_dep_str)
                    if monto_dep >= 0:
                        if tipo_dep == "porcentaje":
                            monto_dep = min(monto_dep, Decimal('100'))
                            deposito = total * (monto_dep / Decimal('100'))
                        else:
                            deposito = monto_dep
                except:
                    pass
            exito, msg, id_renta = self.renta_controller.registrar_renta(
                id_cliente=self.cliente_seleccionado.id_cliente,
                id_usuario=id_usuario,
                detalles=self.disfraces_agregados,
                dias_renta=dias,
                total_personalizado=total,
                deposito_personalizado=deposito
            )
            if exito:
                messagebox.showinfo(
                    "✅ Éxito",
                    f"Renta registrada correctamente\n"
                    f"ID Renta: {id_renta}\n"
                    f"Cliente: {self.cliente_seleccionado.nombre} {self.cliente_seleccionado.apellido_paterno}\n"
                    f"Disfraces: {len(self.disfraces_agregados)}"
                )
                # Generar PDF al registrar
                dias = int(self.entrada_dias.get()) if self.entrada_dias.get() else 0
                dias = max(1, dias)
                fecha_inicio = datetime.now()
                fecha_fin = fecha_inicio + timedelta(days=dias)
                notas = self.entrada_notas.get("1.0", "end").strip()
                self._generar_pdf_ticket_directo(
                    id_renta=id_renta,
                    cliente=self.cliente_seleccionado,
                    detalles=self.disfraces_agregados,
                    dias=dias,
                    total=total,
                    deposito=deposito,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    notas=notas
                )
                self.ventana.destroy()
                self.callback_recarga()
            else:
                messagebox.showerror("❌ Error", f"No se pudo registrar: {msg}")
        except Exception as e:
            messagebox.showerror("❌ Error Fatal", f"Ocurrió un error:\n{str(e)}")

    # ========== GENERACIÓN DE PDF EN FORMULARIO ==========
    def _generar_pdf_ticket_directo(self, id_renta: int, cliente: Cliente, detalles: List[Dict], dias: int, total: Decimal, deposito: Decimal, fecha_inicio: datetime, fecha_fin: datetime, notas: str = ""):
        try:
            nombre_archivo = f"ticket_renta_{id_renta}.pdf"
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            estilo_titulo = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=12, alignment=1, textColor=colors.black)
            estilo_encabezado_negocio = ParagraphStyle('HeaderBusiness', parent=styles['Normal'], fontSize=14, alignment=1, spaceAfter=6, textColor=colors.black)
            estilo_detalle = ParagraphStyle('Detail', parent=styles['Normal'], fontSize=10, spaceAfter=4, textColor=colors.black)
            story.append(Paragraph("TICKET DE RENTA", estilo_titulo))
            story.append(Spacer(1, 0.1 * inch))
            nombre_negocio, direccion_negocio, telefono_negocio = self._obtener_datos_negocio_para_pdf()
            story.append(Paragraph(nombre_negocio, estilo_encabezado_negocio))
            story.append(Paragraph(direccion_negocio, estilo_detalle))
            story.append(Paragraph(f"Tel: {telefono_negocio}", estilo_detalle))
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph("-" * 50, estilo_detalle))
            story.append(Spacer(1, 0.05 * inch))
            story.append(Paragraph(f"<b>ID Renta:</b> {id_renta}", estilo_detalle))
            story.append(Paragraph(f"<b>Cliente:</b> {cliente.nombre_completo()}", estilo_detalle))
            story.append(Paragraph(f"<b>ID Cliente:</b> {cliente.id_cliente}", estilo_detalle))
            story.append(Paragraph(f"<b>Fecha Renta:</b> {fecha_inicio.strftime('%Y-%m-%d')}", estilo_detalle))
            story.append(Paragraph(f"<b>Fecha Devolución:</b> {fecha_fin.strftime('%Y-%m-%d')}", estilo_detalle))
            story.append(Paragraph(f"<b>Días de Renta:</b> {dias}", estilo_detalle))
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph("<b>Disfraces Rentados:</b>", estilo_detalle))
            data_disfraces = [['Código', 'Descripción', 'Precio/Día', 'Cantidad', 'Subtotal']]
            for detalle in detalles:
                subtotal_detalle = detalle['precio_renta'] * detalle['cantidad'] * dias
                data_disfraces.append([
                    detalle['codigo_barras'],
                    detalle['descripcion'],
                    f"${detalle['precio_renta']:.2f}",
                    str(detalle['cantidad']),
                    f"${subtotal_detalle:.2f}"
                ])
            tabla_disfraces = Table(data_disfraces, colWidths=[1.0 * inch, 2.0 * inch, 0.8 * inch, 0.6 * inch, 0.8 * inch])
            tabla_disfraces.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(tabla_disfraces)
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph(f"<b>Total Renta:</b> ${total:.2f}", estilo_detalle))
            story.append(Paragraph(f"<b>Depósito Pagado:</b> ${deposito:.2f}", estilo_detalle))
            story.append(Spacer(1, 0.1 * inch))
            if notas:
                story.append(Paragraph(f"<b>Notas:</b> {notas}", estilo_detalle))
                story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph("-" * 50, estilo_detalle))
            story.append(Spacer(1, 0.05 * inch))
            story.append(Paragraph("¡Gracias por su confianza!", estilo_detalle))
            story.append(Paragraph("Recuerde devolver los disfraces en tiempo y forma.", estilo_detalle))
            doc.build(story)
            self._abrir_archivo(nombre_archivo)
        except Exception as e:
            print(f"[ERROR] No se pudo generar el PDF del ticket: {e}")
            messagebox.showerror("Error", f"No se pudo generar el PDF del ticket: {e}")

    def _obtener_datos_negocio_para_pdf(self) -> tuple[str, str, str]:
        try:
            db = ConexionDB()
            db.conectar()
            query = "SELECT Parametro, Valor FROM PARAMETROS_SISTEMA WHERE Parametro IN ('Nombre_Negocio', 'Direccion_Negocio', 'Telefono_Negocio')"
            resultados = db.ejecutar_query(query)
            nombre_negocio = "MaskNGO - Renta y Venta de Disfraces"
            direccion_negocio = "Calle Ficticia #123, Ciudad, Estado"
            telefono_negocio = "618-123-4567"
            if resultados:
                for fila in resultados:
                    parametro, valor = fila
                    if parametro == 'Nombre_Negocio':
                        nombre_negocio = valor
                    elif parametro == 'Direccion_Negocio':
                        direccion_negocio = valor
                    elif parametro == 'Telefono_Negocio':
                        telefono_negocio = valor
            return nombre_negocio, direccion_negocio, telefono_negocio
        except Exception as e:
            print(f"[ERROR] No se pudieron cargar los datos del negocio desde la base de datos para el PDF del formulario: {e}")
            return "MaskNGO - Renta y Venta de Disfraces", "Calle Ficticia #123, Ciudad, Estado", "618-123-4567"

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
            print(f"[ERROR] No se pudo abrir el archivo {filepath}: {e}")
            messagebox.showwarning("Advertencia", f"No se pudo abrir el archivo PDF automáticamente. Revísalo en la carpeta del programa.")