import sqlite3
import os
import sys

# --- MAGIA PARA RUTAS ABSOLUTAS ---
# Esto asegura que la base de datos se guarde SIEMPRE junto al .exe 
# y no se borre cuando se cierra el programa.
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(BASE_DIR, "viaticos_armada.db")

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # --- CREACIÓN DE TABLAS ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS categorias (id_cat INTEGER PRIMARY KEY AUTOINCREMENT, categoria TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS jerarquias (cod_jerarquia TEXT PRIMARY KEY, descripcion TEXT NOT NULL, id_cat INTEGER NOT NULL, FOREIGN KEY (id_cat) REFERENCES categorias(id_cat) ON DELETE RESTRICT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS destinos (cod_destino INTEGER PRIMARY KEY, descripcion TEXT NOT NULL, sello_director TEXT, firma_director TEXT, nombre_director TEXT, cargo_director TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS personas (mr INTEGER PRIMARY KEY, dni INTEGER UNIQUE NOT NULL, nombre TEXT NOT NULL, apellido TEXT NOT NULL, cod_jerarquia TEXT NOT NULL, cod_destino INTEGER, FOREIGN KEY (cod_jerarquia) REFERENCES jerarquias(cod_jerarquia) ON DELETE RESTRICT, FOREIGN KEY (cod_destino) REFERENCES destinos(cod_destino) ON DELETE SET NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS meses (mes TEXT PRIMARY KEY, sueldo_almirante REAL NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS config_detall (id INTEGER PRIMARY KEY CHECK (id = 1), sello_detall TEXT, firma_detall TEXT, nombre_jefe TEXT, cargo_jefe TEXT)''')
    
    # Migraciones
    for col, default in [("nombre_jefe", "''"), ("cargo_jefe", "''")]:
        try: cursor.execute(f"ALTER TABLE config_detall ADD COLUMN {col} TEXT DEFAULT {default}")
        except Exception: pass
    for col in ["nombre_director", "cargo_director"]:
        try: cursor.execute(f"ALTER TABLE destinos ADD COLUMN {col} TEXT DEFAULT ''")
        except Exception: pass
    conn.commit()

    # --- AUTO-POBLAR JERARQUÍAS SI ESTÁ VACÍA ---
    cursor.execute("SELECT COUNT(*) as total FROM categorias")
    if cursor.fetchone()['total'] == 0:
        categorias = [
            "JEFE DE ESTADO MAYOR", "OFICIALES SUPERIORES", "OFICIALES JEFES", 
            "OFICIALES SUBALTERNOS", "SUBOFICIALES SUPERIORES", "SUBOFICIALES SUBALTERNOS", 
            "CADETES", "VOLUNTARIOS Y ASPIRANTES"
        ]
        for cat in categorias:
            cursor.execute("INSERT OR IGNORE INTO categorias (categoria) VALUES (?)", (cat,))
        
        cat_ids = {}
        cursor.execute("SELECT id_cat, categoria FROM categorias")
        for row in cursor.fetchall():
            cat_ids[row['categoria']] = row['id_cat']
            
        jerarquias = [
            ("AL", "ALMIRANTE", cat_ids["JEFE DE ESTADO MAYOR"]),
            ("VL", "VICEALMIRANTE", cat_ids["OFICIALES SUPERIORES"]),
            ("CL", "CONTRALMIRANTE", cat_ids["OFICIALES SUPERIORES"]),
            ("CN", "CAPITÁN DE NAVÍO", cat_ids["OFICIALES SUPERIORES"]),
            ("CF", "CAPITÁN DE FRAGATA", cat_ids["OFICIALES JEFES"]),
            ("CC", "CAPITÁN DE CORBETA", cat_ids["OFICIALES JEFES"]),
            ("TN", "TENIENTE DE NAVÍO", cat_ids["OFICIALES SUBALTERNOS"]),
            ("TF", "TENIENTE DE FRAGATA", cat_ids["OFICIALES SUBALTERNOS"]),
            ("TC", "TENIENTE DE CORBETA", cat_ids["OFICIALES SUBALTERNOS"]),
            ("GU", "GUARDIAMARINA", cat_ids["OFICIALES SUBALTERNOS"]),
            ("SM", "SUBOFICIAL MAYOR", cat_ids["SUBOFICIALES SUPERIORES"]),
            ("SP", "SUBOFICIAL PRINCIPAL", cat_ids["SUBOFICIALES SUPERIORES"]),
            ("SI", "SUBOFICIAL PRIMERO", cat_ids["SUBOFICIALES SUPERIORES"]),
            ("SS", "SUBOFICIAL SEGUNDO", cat_ids["SUBOFICIALES SUPERIORES"]),
            ("CP", "CABO PRINCIPAL", cat_ids["SUBOFICIALES SUBALTERNOS"]),
            ("CI", "CABO PRIMERO", cat_ids["SUBOFICIALES SUBALTERNOS"]),
            ("CS", "CABO SEGUNDO", cat_ids["SUBOFICIALES SUBALTERNOS"]),
            ("CAD", "CADETE", cat_ids["CADETES"]),
            ("MI", "MARINERO PRIMERO", cat_ids["VOLUNTARIOS Y ASPIRANTES"]),
            ("MS", "MARINERO SEGUNDO", cat_ids["VOLUNTARIOS Y ASPIRANTES"]),
        ]
        for cod, desc, id_cat in jerarquias:
            cursor.execute("INSERT OR IGNORE INTO jerarquias (cod_jerarquia, descripcion, id_cat) VALUES (?, ?, ?)", (cod, desc, id_cat))
        conn.commit()

    conn.close()

def execute_query(query, params=(), fetch=False, fetchall=False):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall() if fetchall else cursor.fetchone()
            return [dict(row) for row in result] if fetchall and result else (dict(result) if result else None)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error en BD: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

# --- ABM PERSONAS ---
def insert_persona(mr, dni, nombre, apellido, cod_jerarquia, cod_destino):
    query = "INSERT INTO personas (mr, dni, nombre, apellido, cod_jerarquia, cod_destino) VALUES (?, ?, ?, ?, ?, ?)"
    return execute_query(query, (mr, dni, nombre, apellido, cod_jerarquia, cod_destino))

def get_persona(mr):
    query = "SELECT * FROM personas WHERE mr = ?"
    return execute_query(query, (mr,), fetch=True)

def get_all_personas():
    query = """
        SELECT p.*, j.descripcion as jerarquia_desc, d.descripcion as destino_desc 
        FROM personas p
        LEFT JOIN jerarquias j ON p.cod_jerarquia = j.cod_jerarquia
        LEFT JOIN destinos d ON p.cod_destino = d.cod_destino
    """
    return execute_query(query, fetch=True, fetchall=True)

def update_persona(mr, dni, nombre, apellido, cod_jerarquia, cod_destino):
    query = "UPDATE personas SET dni=?, nombre=?, apellido=?, cod_jerarquia=?, cod_destino=? WHERE mr=?"
    return execute_query(query, (dni, nombre, apellido, cod_jerarquia, cod_destino, mr))

def delete_persona(mr):
    query = "DELETE FROM personas WHERE mr = ?"
    return execute_query(query, (mr,))

# --- ABM DESTINOS ---
def insert_destino(cod_destino, descripcion, sello_director=None, firma_director=None, nombre_director=None, cargo_director=None):
    query = "INSERT INTO destinos (cod_destino, descripcion, sello_director, firma_director, nombre_director, cargo_director) VALUES (?, ?, ?, ?, ?, ?)"
    return execute_query(query, (cod_destino, descripcion, sello_director, firma_director, nombre_director, cargo_director))

def get_destino(cod_destino):
    query = "SELECT * FROM destinos WHERE cod_destino = ?"
    return execute_query(query, (cod_destino,), fetch=True)

def update_destino(cod_destino, descripcion, sello_director, firma_director, nombre_director=None, cargo_director=None):
    query = "UPDATE destinos SET descripcion=?, sello_director=?, firma_director=?, nombre_director=?, cargo_director=? WHERE cod_destino=?"
    return execute_query(query, (descripcion, sello_director, firma_director, nombre_director, cargo_director, cod_destino))

# --- ABM JERARQUIAS ---
def get_all_jerarquias():
    query = "SELECT cod_jerarquia, descripcion FROM jerarquias ORDER BY id_cat ASC"
    return execute_query(query, fetch=True, fetchall=True)


# --- ABM MESES ---
def insert_mes(mes, sueldo_almirante):
    query = "INSERT INTO meses (mes, sueldo_almirante) VALUES (?, ?) ON CONFLICT(mes) DO UPDATE SET sueldo_almirante=excluded.sueldo_almirante"
    return execute_query(query, (mes, sueldo_almirante))

def update_mes(mes, sueldo_almirante):
    """Actualiza explícitamente el sueldo de un mes que ya existe."""
    query = "UPDATE meses SET sueldo_almirante = ? WHERE mes = ?"
    return execute_query(query, (sueldo_almirante, mes))

def get_sueldo_mes(mes):
    query = "SELECT sueldo_almirante FROM meses WHERE mes = ?"
    result = execute_query(query, (mes,), fetch=True)
    return result['sueldo_almirante'] if result else None

def get_all_meses():
    query = "SELECT mes, sueldo_almirante FROM meses ORDER BY mes DESC"
    return execute_query(query, fetch=True, fetchall=True)

def delete_mes(mes):
    """Elimina un mes y su sueldo de la base de datos."""
    query = "DELETE FROM meses WHERE mes = ?"
    return execute_query(query, (mes,))

# --- ABM CONFIG DETALL ---
def save_config_detall(sello, firma, nombre_jefe="", cargo_jefe=""):
    query = '''
        INSERT INTO config_detall (id, sello_detall, firma_detall, nombre_jefe, cargo_jefe) VALUES (1, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET sello_detall=excluded.sello_detall, firma_detall=excluded.firma_detall,
        nombre_jefe=excluded.nombre_jefe, cargo_jefe=excluded.cargo_jefe
    '''
    return execute_query(query, (sello, firma, nombre_jefe, cargo_jefe))

def get_config_detall():
    return execute_query("SELECT * FROM config_detall WHERE id = 1", fetch=True)

# Inicialización automática
init_db()