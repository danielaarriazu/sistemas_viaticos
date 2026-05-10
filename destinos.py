import database as db

def guardar_destino(cod_destino, descripcion, sello_director=None, firma_director=None):
    try:
        cod_int = int(cod_destino)
    except ValueError:
        raise ValueError("El Código de Destino debe ser numérico.")
    
    descripcion = descripcion.strip().upper()
    if not descripcion:
        raise ValueError("La descripción es obligatoria.")

    existe = db.get_destino(cod_int)
    if existe:
        db.update_destino(cod_int, descripcion, sello_director, firma_director)
        return "Actualizado"
    else:
        db.insert_destino(cod_int, descripcion, sello_director, firma_director)
        return "Creado"

def obtener_destino(cod_destino):
    try:
        return db.get_destino(int(cod_destino))
    except ValueError:
        return None

def listar_destinos():
    query = "SELECT cod_destino, descripcion FROM destinos"
    return db.execute_query(query, fetch=True, fetchall=True)