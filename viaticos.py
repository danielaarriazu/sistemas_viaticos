from datetime import datetime
from num2words import num2words

CORTE_HORARIO = 13  # Hora de corte reglamentaria para computar medio día o día entero


PORCENTAJES_CATEGORIA = {
    "JEFE DE ESTADO MAYOR": 4.00,
    "OFICIALES SUPERIORES": 3.30,
    "OFICIALES JEFES": 2.60,
    "OFICIALES SUBALTERNOS": 2.20,
    "SUBOFICIALES SUPERIORES": 2.00,
    "SUBOFICIALES SUBALTERNOS": 1.80,
    "CADETES": 1.30,
    "VOLUNTARIOS Y ASPIRANTES": 1.20
}

def calcular_importe_diario(sueldo_almirante: float, categoria: str) -> float:
    """
    Calcula el valor de 1 día de viático al 100% cruzando el sueldo base 
    del Almirante con el porcentaje correspondiente a la categoría.
    """
    porcentaje = PORCENTAJES_CATEGORIA.get(categoria.upper(), 0.0)
    importe = sueldo_almirante * (porcentaje / 100.0)
    return round(importe, 2)

def travel_breakdown(fecha_salida, hora_salida, fecha_regreso, hora_regreso, porcentaje_estadia=100.0):
    """
    Calcula los días (equivalente decimal) y el texto a liquidar 
    según la hora de cruce (13:00).
    """
    formato = "%d/%m/%Y %H:%M"
    try:
        salida = datetime.strptime(f"{fecha_salida} {hora_salida}", formato)
        regreso = datetime.strptime(f"{fecha_regreso} {hora_regreso}", formato)
    except ValueError:
        raise ValueError("Error en el formato de fecha u hora. Use DD/MM/AAAA y HH:MM.")

    if regreso < salida:
        raise ValueError("La fecha/hora de regreso no puede ser anterior a la salida.")

    # Caso 1: Sale y vuelve el mismo día
    if salida.date() == regreso.date():
        ida_pct = 100 if (salida.hour < CORTE_HORARIO and regreso.hour >= CORTE_HORARIO) else 50
        return {
            "equivalente_total": ida_pct / 100.0,
            "texto": f"UN (01) día de viático al {ida_pct}%"
        }

    # Caso 2: Viaje de más de un día
    ida_pct = 100 if salida.hour < CORTE_HORARIO else 50
    vuelta_pct = 100 if regreso.hour >= CORTE_HORARIO else 50
    estadia = max((regreso.date() - salida.date()).days - 1, 0)
    
    equivalente = (estadia * porcentaje_estadia / 100.0) + (ida_pct / 100.0) + (vuelta_pct / 100.0)

    partes = [
        f"UN (01) día de viático al {ida_pct}% de ida",
        f"UN (01) día de vuelta al {vuelta_pct}%"
    ]
    if estadia > 0:
        partes.append(f"más {estadia} días de viático al {porcentaje_estadia}% por estadía")

    return {
        "equivalente_total": equivalente,
        "texto": " y ".join(partes)
    }

def liquidar_viatico(sueldo_almirante, categoria, fecha_salida, hora_salida, fecha_regreso, hora_regreso):
    """
    Función maestra: Calcula el importe diario y lo multiplica por los días.
    Retorna un diccionario con todo listo para el PDF.
    """
    importe_diario = calcular_importe_diario(sueldo_almirante, categoria)
    breakdown = travel_breakdown(fecha_salida, hora_salida, fecha_regreso, hora_regreso)
    
    total_calculado = round(importe_diario * breakdown["equivalente_total"], 2)
    
    return {
        "importe_diario": importe_diario,
        "total_calculado": total_calculado,
        "detalle_breakdown": breakdown["texto"]
    }

# --- UTILIDADES DE FORMATO ---
def format_money(value: float) -> str:
    return f"$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def importe_a_letras(numero: float) -> str:
    """Convierte el total a letras para el recibo (versión simple)."""
    enteros = int(numero)
    letras= num2words(enteros, lang= 'es').upper()
    centavos = int(round((numero - enteros) * 100))
    
    return f"PESOS {letras} CON {centavos:02d}/100 CTVS"