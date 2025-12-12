"""
Módulo: database.py
Ubicación: config/database.py
Descripción: Clase para conexión a MySQL
Sistema: Renta y Venta de Disfraces
"""

import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Tuple


class ConexionDB:
    """
    Clase para gestionar conexión a MySQL.
    
    Uso básico:
        db = ConexionDB()
        db.conectar()
        resultados = db.ejecutar_query("SELECT * FROM USUARIOS")
        db.desconectar()
    """
    
    def __init__(self, host="localhost", user="root", password="", database="maskngo"):
        """
        Inicializa la configuración de conexión.
        
        Args:
            host: Servidor MySQL (default: localhost)
            user: Usuario MySQL (default: root)
            password: Contraseña MySQL (default: vacío)
            database: Nombre de la BD (default: maskngo)
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        print(f"✅ ConexionDB inicializada para BD: {database}")
    
    def conectar(self):
        """
        Conecta a MySQL.
        
        Returns:
            bool: True si conectó, False si falló
        """
        try:
            if self.connection and self.connection.is_connected():
                print("ℹ️ Ya hay conexión activa")
                return True
            
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
            
            if self.connection.is_connected():
                version = self.connection.get_server_info()
                print(f"✅ Conectado a MySQL {version}")
                print(f"📂 Base de datos: {self.database}")
                return True
                
        except Error as e:
            print(f"❌ Error de conexión: {e}")
            self.connection = None
            return False
    
    def desconectar(self):
        """Cierra la conexión MySQL."""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("🔌 Conexión cerrada")
                self.connection = None
        except Error as e:
            print(f"❌ Error al cerrar: {e}")
    
    def esta_conectado(self):
        """
        Verifica si hay conexión activa.
        
        Returns:
            bool: True si conectado, False si no
        """
        return self.connection is not None and self.connection.is_connected()
    
    def ejecutar_query(self, query, parametros=None):
        """
        Ejecuta SELECT y devuelve resultados.
        
        Args:
            query: Consulta SQL
            parametros: Tupla con parámetros (opcional)
        
        Returns:
            List[Tuple]: Resultados o None si error
        """
        cursor = None
        try:
            if not self.esta_conectado():
                print("⚠️ Reconectando...")
                if not self.conectar():
                    return None
            
            cursor = self.connection.cursor()
            
            if parametros:
                cursor.execute(query, parametros)
            else:
                cursor.execute(query)
            
            resultados = cursor.fetchall()
            print(f"✅ Query OK: {len(resultados)} filas")
            return resultados
            
        except Error as e:
            print(f"❌ Error query: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def ejecutar_insert(self, query, parametros=None):
        """
        Ejecuta INSERT.
        
        Args:
            query: Consulta INSERT
            parametros: Tupla con valores (opcional)
        
        Returns:
            int: ID insertado o None si error
        """
        cursor = None
        try:
            if not self.esta_conectado():
                if not self.conectar():
                    return None
            
            cursor = self.connection.cursor()
            
            if parametros:
                cursor.execute(query, parametros)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            id_insertado = cursor.lastrowid
            print(f"✅ INSERT OK. ID: {id_insertado}")
            return id_insertado
            
        except Error as e:
            print(f"❌ Error INSERT: {e}")
            if self.connection:
                self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
    
    def ejecutar_update(self, query, parametros=None):
        """
        Ejecuta UPDATE o DELETE.
        
        Args:
            query: Consulta UPDATE/DELETE
            parametros: Tupla con valores (opcional)
        
        Returns:
            int: Filas afectadas o None si error
        """
        cursor = None
        try:
            if not self.esta_conectado():
                if not self.conectar():
                    return None
            
            cursor = self.connection.cursor()
            
            if parametros:
                cursor.execute(query, parametros)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            filas = cursor.rowcount
            print(f"✅ UPDATE/DELETE OK. Filas: {filas}")
            return filas
            
        except Error as e:
            print(f"❌ Error UPDATE/DELETE: {e}")
            if self.connection:
                self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
    
    def __del__(self):
        """Destructor: cierra conexión automáticamente."""
        self.desconectar()


# Prueba rápida si ejecutas este archivo directamente
if __name__ == "__main__":
    print("\n" + "="*50)
    print("PRUEBA RÁPIDA - ConexionDB")
    print("="*50 + "\n")
    
    db = ConexionDB()
    
    if db.conectar():
        print("\n✅ Conexión exitosa!")
        
        # Probar query
        tablas = db.ejecutar_query("SHOW TABLES")
        if tablas:
            print(f"\n📊 Tablas encontradas: {len(tablas)}")
        
        db.desconectar()
    else:
        print("\n❌ Error de conexión")
    
    print("\n" + "="*50 + "\n")