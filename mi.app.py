import unicodedata
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Calculadora y Control de Cobranza", layout="wide"
)

# Configuración constante de comisión
PORCENTAJE_COMISION = 15.0
FACTOR_GANANCIA = PORCENTAJE_COMISION / 100.0
FACTOR_INTERES = 1.20
SEMANAS_TOTALES = 15

# Diccionario ampliado de nombres y apellidos comunes con acento
NOMBRES_ACENTUADOS = {
    "maria": "María",
    "jose": "José",
    "jesus": "Jesús",
    "angel": "Ángel",
    "ramon": "Ramón",
    "martin": "Martín",
    "raul": "Raúl",
    "sofia": "Sofía",
    "lucia": "Lucía",
    "veronica": "Verónica",
    "monica": "Mónica",
    "andres": "Andrés",
    "adrian": "Adrián",
    "oscar": "Óscar",
    "ruben": "Rubén",
    "perez": "Pérez",
    "gomez": "Gómez",
    "rodriguez": "Rodríguez",
    "hernandez": "Hernández",
    "martinez": "Martínez",
    "lopez": "López",
    "gonzalez": "González",
    "sanchez": "Sánchez",
    "ramirez": "Ramírez",
    "diaz": "Díaz",
    "vazquez": "Vázquez",
    "jimenez": "Jiménez",
    "gutierrez": "Gutiérrez",
    "alvarez": "Álvarez",
    "suarez": "Suárez",
}


def auto_corregir_nombre(cadena):
    """Limpia espacios, aplica formato de mayúsculas (Capitalize)

    y corrige acentos según el diccionario.
    """
    if not isinstance(cadena, str) or not cadena.strip():
        return ""

    # Normalizar espacios extras
    texto = " ".join(cadena.split())

    palabras = texto.split(" ")
    palabras_corregidas = []

    for p in palabras:
        p_lower = p.lower()
        # Si la palabra sin acento está en nuestro diccionario, se reemplaza por la correcta
        if p_lower in NOMBRES_ACENTUADOS:
            palabras_corregidas.append(NOMBRES_ACENTUADOS[p_lower])
        else:
            # Si no está, asegura Mayúscula Inicial (ej: "juan" -> "Juan")
            palabras_corregidas.append(p.capitalize())

    return " ".join(palabras_corregidas)


st.title("👵 Calculadora y Control de Cobranza")
st.write(
    "Escribe en la tabla. Al presionar **Enter** o salir de la casilla, el nombre se **corregirá automáticamente** en su propio recuadro."
)

# 1. Crear las columnas de las 15 semanas
columnas_semanas = [f"Semana {i}" for i in range(1, 16)]

# 2. Inicializar la base de datos en Session State
if "df_clientes" not in st.session_state:
    data = [
        {
            "Cliente": "María Gómez",
            "Monto Prestado": 1000.0,
            "Es Renovación": False,
            "Débito": 0.0,
            **{sem: False for sem in columnas_semanas},
        },
        {
            "Cliente": "Juan Pérez",
            "Monto Prestado": 2500.0,
            "Es Renovación": True,
            "Débito": 300.0,
            **{
                sem: True if i <= 3 else False
                for i, sem in enumerate(columnas_semanas, 1)
            },
        },
    ]
    st.session_state.df_clientes = pd.DataFrame(data)

# Configuración del editor interactivo
config_columnas = {
    "Cliente": st.column_config.TextColumn(
        "Nombre del Cliente",
        help="Escribe en minúsculas o sin acento; se autocorregirá al confirmar.",
        required=True,
    ),
    "Monto Prestado": st.column_config.NumberColumn(
        "Monto Prestado ($)", min_value=0.0, format="$%.2f", default=0.0
    ),
    "Es Renovación": st.column_config.CheckboxColumn(
        "¿Renovación?",
        help="Aplica el descuento de $50 por cada $1,000 prestados.",
        default=False,
    ),
    "Débito": st.column_config.NumberColumn(
        "Débito / Adeudo Anterior ($)",
        min_value=0.0,
        format="$%.2f",
        default=0.0,
    ),
}

for sem in columnas_semanas:
    config_columnas[sem] = st.column_config.CheckboxColumn(
        sem, help=f"Marca si pagó la {sem}", default=False
    )

# 3. Mostrar Editor Interactivos
df_editado = st.data_editor(
    st.session_state.df_clientes,
    column_config=config_columnas,
    num_rows="dynamic",
    hide_index=True,
    key="editor_tabla",
)

# --- CORRECCIÓN AUTOMÁTICA DIRECTA ---
# Se aplica la corrección a la columna 'Cliente'
df_editado["Cliente"] = df_editado["Cliente"].apply(auto_corregir_nombre)

# Guardar los cambios directamente en la sesión
st.session_state.df_clientes = df_editado.copy()

# 4. Limpieza y Fórmulas de cálculo
df_calculado = st.session_state.df_clientes.copy()

if not df_calculado.empty:
    df_calculado["Monto Prestado"] = df_calculado["Monto Prestado"].fillna(0.0)
    df_calculado["Débito"] = df_calculado["Débito"].fillna(0.0)
    df_calculado["Es Renovación"] = df_calculado["Es Renovación"].fillna(False)
    df_calculado[columnas_semanas] = df_calculado[columnas_semanas].fillna(
        False
    )

    df_calculado["Descuento Renovación"] = df_calculado.apply(
        lambda row: (row["Monto Prestado"] / 1000.0) * 50.0
        if row["Es Renovación"]
        else 0.0,
        axis=1,
    )

    df_calculado["Monto Entregado a Mano"] = (
        df_calculado["Monto Prestado"]
        - df_calculado["Descuento Renovación"]
        - df_calculado["Débito"]
    )

    df_calculado["Ganancia Abuela"] = (
        df_calculado["Monto Prestado"] * FACTOR_GANANCIA
    )

    df_calculado["Total a Pagar"] = (
        df_calculado["Monto Prestado"] * FACTOR_INTERES
    )
    df_calculado["Pago Semanal"] = (
        df_calculado["Total a Pagar"] / SEMANAS_TOTALES
    )

    df_calculado["Semanas Pagadas"] = df_calculado[columnas_semanas].sum(
        axis=1
    )
    df_calculado["Total Cobrado"] = (
        df_calculado["Semanas Pagadas"] * df_calculado["Pago Semanal"]
    )
    df_calculado["Saldo Restante"] = (
        df_calculado["Total a Pagar"] - df_calculado["Total Cobrado"]
    )

    # Métricas
    ganancia_total = df_calculado["Ganancia Abuela"].sum()
    monto_total_prestado = df_calculado["Monto Prestado"].sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="💰 Total Prestado", value=f"${monto_total_prestado:,.2f}"
        )
    with col2:
        st.metric(
            label=f"💵 Ganancia Total ({PORCENTAJE_COMISION:.1f}%)",
            value=f"${ganancia_total:,.2f}",
        )

    # Tabla de Resumen
    st.subheader("📊 Control de Pagos, Saldos y Ganancias")

    columnas_resumen = [
        "Cliente",
        "Monto Prestado",
        "Ganancia Abuela",
        "Monto Entregado a Mano",
        "Total a Pagar",
        "Pago Semanal",
        "Semanas Pagadas",
        "Total Cobrado",
        "Saldo Restante",
    ]

    st.dataframe(
        df_calculado[columnas_resumen],
        column_config={
            "Monto Prestado": st.column_config.NumberColumn(
                "Monto Prestado", format="$%.2f"
            ),
            "Ganancia Abuela": st.column_config.NumberColumn(
                "Ganancia Abuela", format="$%.2f"
            ),
            "Monto Entregado a Mano": st.column_config.NumberColumn(
                "Monto Entregado a Mano", format="$%.2f"
            ),
            "Total a Pagar": st.column_config.NumberColumn(
                "Total a Pagar", format="$%.2f"
            ),
            "Pago Semanal": st.column_config.NumberColumn(
                "Pago Semanal", format="$%.2f"
            ),
            "Total Cobrado": st.column_config.NumberColumn(
                "Total Cobrado", format="$%.2f"
            ),
            "Saldo Restante": st.column_config.NumberColumn(
                "Saldo Restante", format="$%.2f"
            ),
        },
        use_container_width=True,
        hide_index=True,
    )
