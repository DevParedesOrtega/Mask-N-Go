"""
Módulo: cliente_controller.py
Ubicación: controllers/cliente_controller.py
Descripción: Controlador para gestión de clientes
Sistema: Renta y Venta de Disfraces
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import ConexionDB
from models.cliente import Cliente
from utils.validadores import Validadores
from typing import Optional, Tuple, List, Dict


class ClienteController:
    """
    Controlador para manejar clientes del sistema.
    
    Gestiona:
    - CRUD completo de clientes
    - Búsquedas inteligentes (nombre, teléfono, ID)
    - Historial completo del cliente
    - Detección de duplicados
    - Validación de datos
    """
    
    def __init__(self):
        """Inicializa el controlador con conexión a BD."""
        self.db = ConexionDB()
    
    def buscar_duplicados(self, nombre: str, apellido_paterno: str, telefono: str) -> List[Cliente]:
        """
        Busca posibles clientes duplicados ANTES de registrar.
        
        Busca por:
        - Nombre + Apellido exacto
        - Teléfono similar
        
        Args:
            nombre: Nombre del cliente
            apellido_paterno: Apellido paterno
            telefono: Teléfono
        
        Returns:
            List[Cliente]: Lista de clientes similares encontrados
        """
        try:
            self.db.conectar()
            
            # Buscar por nombre completo similar o teléfono exacto
            query = """
                SELECT * FROM CLIENTES 
                WHERE (LOWER(Nombre) = LOWER(%s) AND LOWER(Apellido_Paterno) = LOWER(%s))
                   OR Telefono = %s
            """
            
            resultados = self.db.ejecutar_query(query, (nombre, apellido_paterno, telefono))
            
            if resultados:
                return [Cliente.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en buscar_duplicados: {e}")
            return []
    
    def agregar_cliente(
        self,
        nombre: str,
        apellido_paterno: str,
        telefono: str,
        forzar: bool = False
    ) -> Tuple[bool, str, Optional[int], Optional[List[Cliente]]]:
        """
        Agrega un nuevo cliente al sistema con detección de duplicados.
        
        Args:
            nombre: Nombre del cliente
            apellido_paterno: Apellido paterno
            telefono: Teléfono de contacto (10-15 dígitos)
            forzar: Si True, ignora advertencias de duplicados
        
        Returns:
            Tuple[bool, str, Optional[int], Optional[List[Cliente]]]: 
                (éxito, mensaje, id_cliente, posibles_duplicados)
        
        Example:
            >>> controller = ClienteController()
            >>> exito, msg, id, dups = controller.agregar_cliente('Juan', 'Pérez', '6181234567')
            >>> if not exito and dups:
            >>>     print(f"Clientes similares: {dups}")
        """
        try:
            # 1. Validar nombre
            valido, mensaje = Validadores.validar_nombre(nombre)
            if not valido:
                return False, mensaje, None, None
            
            # 2. Validar apellido
            valido, mensaje = Validadores.validar_nombre(apellido_paterno)
            if not valido:
                return False, f"Apellido: {mensaje}", None, None
            
            # 3. Validar teléfono (soporta internacional)
            valido, mensaje = Validadores.validar_telefono(telefono)
            if not valido:
                return False, mensaje, None, None
            
            # 4. Buscar duplicados (solo si no es forzado)
            if not forzar:
                duplicados = self.buscar_duplicados(nombre, apellido_paterno, telefono)
                
                if duplicados:
                    # Verificar si es teléfono exacto (no permitir)
                    for dup in duplicados:
                        if dup.telefono == telefono:
                            return False, f"El teléfono '{telefono}' ya está registrado con {dup.nombre_completo()}", None, duplicados
                    
                    # Solo nombre similar (advertir pero no bloquear)
                    return False, f"Clientes similares encontrados. Revisa antes de continuar.", None, duplicados
            
            # 5. Insertar en base de datos
            self.db.conectar()
            query = """
                INSERT INTO CLIENTES (Nombre, Apellido_Paterno, Telefono)
                VALUES (%s, %s, %s)
            """
            nuevo_id = self.db.ejecutar_insert(
                query,
                (nombre, apellido_paterno, telefono)
            )
            
            if nuevo_id:
                print(f"✅ Cliente '{nombre} {apellido_paterno}' agregado con ID {nuevo_id}")
                return True, "Cliente agregado exitosamente", nuevo_id, None
            else:
                return False, "Error al agregar cliente en la base de datos", None, None
        
        except Exception as e:
            print(f"❌ Error en agregar_cliente: {e}")
            return False, f"Error inesperado: {str(e)}", None, None
    
    def editar_cliente(
        self,
        id_cliente: int,
        nombre: Optional[str] = None,
        apellido_paterno: Optional[str] = None,
        telefono: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Edita los datos de un cliente existente.
        
        IMPORTANTE: Cambiar el teléfono requiere confirmación especial
        ya que es el identificador principal para búsquedas.
        
        Args:
            id_cliente: ID del cliente a editar
            nombre: Nuevo nombre (opcional)
            apellido_paterno: Nuevo apellido (opcional)
            telefono: Nuevo teléfono (opcional, CRÍTICO)
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # 1. Verificar que el cliente existe
            if not self.existe_cliente(id_cliente):
                return False, f"No existe cliente con ID {id_cliente}"
            
            # 2. Construir query dinámicamente
            campos = []
            valores = []
            
            if nombre is not None:
                valido, mensaje = Validadores.validar_nombre(nombre)
                if not valido:
                    return False, mensaje
                campos.append("Nombre = %s")
                valores.append(nombre)
            
            if apellido_paterno is not None:
                valido, mensaje = Validadores.validar_nombre(apellido_paterno)
                if not valido:
                    return False, f"Apellido: {mensaje}"
                campos.append("Apellido_Paterno = %s")
                valores.append(apellido_paterno)
            
            if telefono is not None:
                valido, mensaje = Validadores.validar_telefono(telefono)
                if not valido:
                    return False, mensaje
                
                # ADVERTENCIA: Cambio de teléfono
                cliente_actual = self.buscar_por_id(id_cliente)
                if cliente_actual and cliente_actual.telefono != telefono:
                    print(f"⚠️ ADVERTENCIA: Cambiando teléfono de {cliente_actual.telefono} a {telefono}")
                    print(f"   Este cambio es CRÍTICO ya que el teléfono se usa para búsquedas")
                
                # Verificar que el nuevo teléfono no esté en uso
                if self.telefono_existe(telefono):
                    cliente_existente = self.buscar_por_telefono(telefono)
                    if cliente_existente and cliente_existente.id_cliente != id_cliente:
                        return False, f"El teléfono '{telefono}' ya está registrado con {cliente_existente.nombre_completo()}"
                
                campos.append("Telefono = %s")
                valores.append(telefono)
            
            if not campos:
                return False, "No se proporcionaron campos para actualizar"
            
            # 3. Ejecutar UPDATE
            valores.append(id_cliente)
            query = f"UPDATE CLIENTES SET {', '.join(campos)} WHERE Id_cliente = %s"
            
            self.db.conectar()
            filas = self.db.ejecutar_update(query, tuple(valores))
            
            if filas and filas > 0:
                print(f"✅ Cliente ID {id_cliente} actualizado")
                return True, "Cliente actualizado exitosamente"
            else:
                return False, "No se pudo actualizar el cliente"
        
        except Exception as e:
            print(f"❌ Error en editar_cliente: {e}")
            return False, f"Error inesperado: {str(e)}"
    
    def eliminar_cliente(self, id_cliente: int) -> Tuple[bool, str]:
        """
        Elimina un cliente del sistema.
        
        POLÍTICA: Solo permite eliminar si NO tiene historial (ventas/rentas).
        Esto protege la integridad de los registros históricos.
        
        Args:
            id_cliente: ID del cliente a eliminar
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # 1. Verificar que existe
            cliente = self.buscar_por_id(id_cliente)
            if not cliente:
                return False, f"No existe cliente con ID {id_cliente}"
            
            # 2. Cargar historial para verificar
            self.cargar_historial_cliente(cliente)
            
            # 3. Verificar que NO tenga historial
            if cliente.tiene_historial():
                return False, f"No se puede eliminar: el cliente tiene historial de transacciones. Ventas: {cliente.estadisticas.get('total_ventas', 0)}, Rentas: {cliente.estadisticas.get('total_rentas', 0)}"
            
            # 4. Eliminar cliente
            self.db.conectar()
            query_delete = "DELETE FROM CLIENTES WHERE Id_cliente = %s"
            filas = self.db.ejecutar_update(query_delete, (id_cliente,))
            
            if filas and filas > 0:
                print(f"✅ Cliente ID {id_cliente} ({cliente.nombre_completo()}) eliminado")
                return True, "Cliente eliminado exitosamente"
            else:
                return False, "No se pudo eliminar el cliente"
        
        except Exception as e:
            print(f"❌ Error en eliminar_cliente: {e}")
            return False, f"Error inesperado: {str(e)}"
    
    def buscar_por_id(self, id_cliente: int) -> Optional[Cliente]:
        """
        Busca un cliente por su ID.
        
        Args:
            id_cliente: ID del cliente a buscar
        
        Returns:
            Optional[Cliente]: Objeto Cliente o None si no existe
        """
        try:
            self.db.conectar()
            query = "SELECT * FROM CLIENTES WHERE Id_cliente = %s"
            resultados = self.db.ejecutar_query(query, (id_cliente,))
            
            if resultados and len(resultados) > 0:
                return Cliente.from_db_row(resultados[0])
            return None
        
        except Exception as e:
            print(f"❌ Error en buscar_por_id: {e}")
            return None
    
    def buscar_por_telefono(self, telefono: str) -> Optional[Cliente]:
        """
        Busca un cliente por su teléfono.
        
        Args:
            telefono: Teléfono del cliente
        
        Returns:
            Optional[Cliente]: Objeto Cliente o None si no existe
        """
        try:
            self.db.conectar()
            query = "SELECT * FROM CLIENTES WHERE Telefono = %s"
            resultados = self.db.ejecutar_query(query, (telefono,))
            
            if resultados and len(resultados) > 0:
                return Cliente.from_db_row(resultados[0])
            return None
        
        except Exception as e:
            print(f"❌ Error en buscar_por_telefono: {e}")
            return None
    
    def buscar_por_nombre(self, termino: str) -> List[Cliente]:
        """
        Busca clientes por nombre o apellido (búsqueda con LIKE).
        
        Args:
            termino: Término a buscar en nombre o apellido
        
        Returns:
            List[Cliente]: Lista de clientes encontrados
        """
        try:
            self.db.conectar()
            query = """
                SELECT * FROM CLIENTES 
                WHERE Nombre LIKE %s OR Apellido_Paterno LIKE %s
                ORDER BY Nombre, Apellido_Paterno
            """
            patron = f"%{termino}%"
            resultados = self.db.ejecutar_query(query, (patron, patron))
            
            if resultados:
                return [Cliente.from_db_row(row) for row in resultados]
            return []
        
        except Exception as e:
            print(f"❌ Error en buscar_por_nombre: {e}")
            return []
    
    def cargar_historial_cliente(self, cliente: Cliente) -> bool:
        """
        Carga el historial completo del cliente desde la BD.
        
        Calcula:
        - Total gastado (ventas + rentas)
        - Número de ventas
        - Número de rentas
        - Rentas activas
        - Rentas vencidas
        - Adeudo pendiente
        - Última visita
        
        Args:
            cliente: Objeto Cliente a cargar
        
        Returns:
            bool: True si se cargó correctamente
        """
        try:
            self.db.conectar()
            
            # 1. Total de ventas y monto
            query_ventas = """
                SELECT COUNT(*), COALESCE(SUM(Total), 0)
                FROM VENTAS 
                WHERE Id_cliente = %s
            """
            resultado_ventas = self.db.ejecutar_query(query_ventas, (cliente.id_cliente,))
            total_ventas = resultado_ventas[0][0] if resultado_ventas else 0
            monto_ventas = float(resultado_ventas[0][1]) if resultado_ventas else 0.0
            
            # 2. Total de rentas y monto
            query_rentas = """
                SELECT COUNT(*), COALESCE(SUM(Total), 0)
                FROM RENTAS 
                WHERE Id_cliente = %s
            """
            resultado_rentas = self.db.ejecutar_query(query_rentas, (cliente.id_cliente,))
            total_rentas = resultado_rentas[0][0] if resultado_rentas else 0
            monto_rentas = float(resultado_rentas[0][1]) if resultado_rentas else 0.0
            
            # 3. Rentas activas
            query_activas = """
                SELECT COUNT(*)
                FROM RENTAS 
                WHERE Id_cliente = %s AND Estado = 'Activa'
            """
            resultado_activas = self.db.ejecutar_query(query_activas, (cliente.id_cliente,))
            rentas_activas = resultado_activas[0][0] if resultado_activas else 0
            
            # 4. Rentas vencidas
            query_vencidas = """
                SELECT COUNT(*)
                FROM RENTAS 
                WHERE Id_cliente = %s AND Estado = 'Vencida'
            """
            resultado_vencidas = self.db.ejecutar_query(query_vencidas, (cliente.id_cliente,))
            rentas_vencidas = resultado_vencidas[0][0] if resultado_vencidas else 0
            
            # 5. Adeudo pendiente (suma de penalizaciones de rentas vencidas)
            query_adeudo = """
                SELECT COALESCE(SUM(Penalizacion), 0)
                FROM RENTAS 
                WHERE Id_cliente = %s AND Estado = 'Vencida'
            """
            resultado_adeudo = self.db.ejecutar_query(query_adeudo, (cliente.id_cliente,))
            adeudo_pendiente = float(resultado_adeudo[0][0]) if resultado_adeudo else 0.0
            
            # 6. Última visita (fecha más reciente entre ventas y rentas)
            query_ultima = """
                SELECT MAX(fecha) FROM (
                    SELECT MAX(fecha_venta) as fecha FROM VENTAS WHERE Id_cliente = %s
                    UNION ALL
                    SELECT MAX(Fecha_Renta) as fecha FROM RENTAS WHERE Id_cliente = %s
                ) as ultimas
            """
            resultado_ultima = self.db.ejecutar_query(query_ultima, (cliente.id_cliente, cliente.id_cliente))
            ultima_visita = resultado_ultima[0][0] if resultado_ultima and resultado_ultima[0][0] else None
            
            # 7. Cargar estadísticas en el cliente
            estadisticas = {
                'total_gastado': monto_ventas + monto_rentas,
                'total_ventas': total_ventas,
                'total_rentas': total_rentas,
                'rentas_activas': rentas_activas,
                'rentas_vencidas': rentas_vencidas,
                'adeudo_pendiente': adeudo_pendiente,
                'ultima_visita': ultima_visita
            }
            
            cliente.cargar_estadisticas(estadisticas)
            
            print(f"✅ Historial cargado para {cliente.nombre_completo()}")
            return True
        
        except Exception as e:
            print(f"❌ Error en cargar_historial_cliente: {e}")
            return False
    
    def obtener_cliente_con_historial(self, id_cliente: int) -> Optional[Cliente]:
        """
        Obtiene un cliente con su historial completo cargado.
        
        Args:
            id_cliente: ID del cliente
        
        Returns:
            Optional[Cliente]: Cliente con historial o None
        """
        cliente = self.buscar_por_id(id_cliente)
        if cliente:
            self.cargar_historial_cliente(cliente)
        return cliente
    
    def listar_todos(self, cargar_historial: bool = False) -> List[Cliente]:
        """
        Lista todos los clientes del sistema.
        
        Args:
            cargar_historial: Si True, carga historial de cada cliente (más lento)
        
        Returns:
            List[Cliente]: Lista de todos los clientes
        """
        try:
            self.db.conectar()
            query = "SELECT * FROM CLIENTES ORDER BY Fecha_Registro DESC"
            resultados = self.db.ejecutar_query(query)
            
            if resultados:
                clientes = [Cliente.from_db_row(row) for row in resultados]
                
                if cargar_historial:
                    for cliente in clientes:
                        self.cargar_historial_cliente(cliente)
                
                return clientes
            return []
        
        except Exception as e:
            print(f"❌ Error en listar_todos: {e}")
            return []
    
    def existe_cliente(self, id_cliente: int) -> bool:
        """
        Verifica si existe un cliente con el ID dado.
        
        Args:
            id_cliente: ID del cliente a verificar
        
        Returns:
            bool: True si existe, False si no
        """
        try:
            self.db.conectar()
            query = "SELECT COUNT(*) FROM CLIENTES WHERE Id_cliente = %s"
            resultados = self.db.ejecutar_query(query, (id_cliente,))
            
            if resultados and resultados[0][0] > 0:
                return True
            return False
        
        except Exception as e:
            print(f"❌ Error en existe_cliente: {e}")
            return False
    
    def telefono_existe(self, telefono: str) -> bool:
        """
        Verifica si un teléfono ya está registrado.
        
        Args:
            telefono: Teléfono a verificar
        
        Returns:
            bool: True si existe, False si no
        """
        try:
            self.db.conectar()
            query = "SELECT COUNT(*) FROM CLIENTES WHERE Telefono = %s"
            resultados = self.db.ejecutar_query(query, (telefono,))
            
            if resultados and resultados[0][0] > 0:
                return True
            return False
        
        except Exception as e:
            print(f"❌ Error en telefono_existe: {e}")
            return False
    
    def contar_clientes(self) -> int:
        """
        Cuenta el total de clientes registrados.
        
        Returns:
            int: Total de clientes
        """
        try:
            self.db.conectar()
            query = "SELECT COUNT(*) FROM CLIENTES"
            resultados = self.db.ejecutar_query(query)
            
            if resultados:
                return resultados[0][0]
            return 0
        
        except Exception as e:
            print(f"❌ Error en contar_clientes: {e}")
            return 0


# Ejemplo de uso
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJEMPLO DE USO - ClienteController")
    print("="*60 + "\n")
    
    controller = ClienteController()
    
    # Ejemplo 1: Buscar duplicados antes de agregar
    print("1. Buscando duplicados antes de registrar...")
    duplicados = controller.buscar_duplicados("María", "García", "6187654321")
    if duplicados:
        print(f"   ⚠️ {len(duplicados)} clientes similares encontrados:")
        for dup in duplicados:
            print(f"      - {dup}")
    else:
        print("   ✅ No hay duplicados\n")
    
    # Ejemplo 2: Agregar cliente
    print("2. Agregando cliente...")
    exito, msg, id, dups = controller.agregar_cliente(
        nombre="María",
        apellido_paterno="García",
        telefono="+52 618 765 4321"
    )
    print(f"   {msg}")
    if dups:
        print(f"   Clientes similares: {len(dups)}")
    print()
    
    if exito and id:
        # Ejemplo 3: Obtener cliente con historial
        print("3. Obteniendo cliente con historial...")
        cliente = controller.obtener_cliente_con_historial(id)
        if cliente:
            print(f"   {cliente.resumen_estadisticas()}\n")
        
        # Ejemplo 4: Eliminar
        print("4. Eliminando cliente de prueba...")
        exito_del, msg_del = controller.eliminar_cliente(id)
        print(f"   {msg_del}\n")
    
    print("="*60 + "\n")