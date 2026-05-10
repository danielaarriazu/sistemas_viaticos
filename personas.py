import database as db

def guardar_persona(mr, dni, nombre, apellido, cod_jerarquia, cod_destino):
    """Valida y guarda/actualiza un personal militar en la base de datos."""
    try:
        mr_int = int(mr)
        dni_int = int(dni)
    except ValueError:
        raise ValueError("El MR y el DNI deben ser números enteros sin puntos ni comas.")

    if not nombre.strip() or not apellido.strip():
        raise ValueError("El nombre y el apellido son obligatorios.")
    if not cod_jerarquia:
        raise ValueError("Debe seleccionar una jerarquía.")

    # Convertir a mayúsculas para mantener estándar formal
    nombre = nombre.strip().upper()
    apellido = apellido.strip().upper()

    existe = db.get_persona(mr_int)
    if existe:
        db.update_persona(mr_int, dni_int, nombre, apellido, cod_jerarquia, cod_destino)
        return "Actualizado"
    else:
        db.insert_persona(mr_int, dni_int, nombre, apellido, cod_jerarquia, cod_destino)
        return "Creado"

def obtener_persona(mr):
    try:
        return db.get_persona(int(mr))
    except ValueError:
        return None

def listar_personas():
    return db.get_all_personas()

def eliminar_persona(mr):
    try:
        db.delete_persona(int(mr))
    except Exception as e:
        raise ValueError(f"No se pudo eliminar: {e}")