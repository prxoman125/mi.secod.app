import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Calculadora y Control de Cobranza", layout="wide"
)

# --- BARRA LATERAL (Sidebar) ---
st.sidebar.header("⚙️ Configuración de Ganancia")

porcentaje_comision = st.sidebar.number_input(
    "Porcentaje de Ganancia (%)",
    min_value=0.0,
    max_value=100.0,
    value=15.0,
    step=0.5,
    help="Ingresa el porcentaje que gana la abuela por cada $100 prestados.",
)

factor_ganancia = porcentaje_comision / 100.0

st.title("👵 Calculadora y Control de Cobranza")
st.write(
    "Ingresa los datos del cliente y marca con una palomita (✔️) las semanas pagadas."
)

# 1. Crear las columnas de las 15 semanas
columnas_semanas = [f"Semana {i}" for i in range(1, 16)]

# 2. Datos iniciales de ejemplo
data = [
    {
        "Cliente": "Cliente 1",
        "Monto Prestado": 1000.0,
        "Es Renovación": False,
        "Débito": 0.0,
        **{sem: False for sem in columnas_semanas},
    },
    {
        "Cliente": "Cliente 2",
        "Monto Prestado": 2500.0,
        "Es Renovación": True,
        "Débito": 300.0,
        **{sem: True if i <= 3 else False for i, sem in enumerate(columnas_semanas, 1)},
    },
]

df_inicial = pd.DataFrame(data)

# Configuración del editor interactivo
config_columnas = {
    "Cliente": st.column_config.TextColumn("Nombre del Cliente"),
    "Monto Prestado": st.column_config.NumberColumn(
        "Monto Prestado ($)", min_value=0.0, format="$%.2f", default=0.0
    ),
    "Es Renovación": st.column_config.CheckboxColumn(
        "¿Renovación?",
        help="Aplica el descuento de $50 por cada $1,000 prestados.",
        default=False,
    ),
    "Débito": st.column_config.NumberColumn(
        "Débito / Adeudo Anterior ($)", min_value=0.0, format="$%.2f", default=0.0
    ),
}

for sem in columnas_semanas:
    config_columnas[sem] = st.column_config.CheckboxColumn(
        sem, help=f"Marca si pagó la {sem}", default=False
    )

# 3. Tabla editable
df_editado = st.data_editor(
    df_inicial,
    column_config=config_columnas,
    num_rows="dynamic",
    hide_index=True,
)

# 4. Limpieza de datos (evita errores con filas nuevas o vacías)
df_calculado = df_editado.copy()

# Rellenar casillas vacías de texto o números para evitar fallas
df_calculado["Cliente"] = df_calculado["Cliente"].fillna("Nuevo Cliente")
df_calculado["Monto Prestado"] = df_calculado["Monto Prestado"].fillna(0.0)
df_calculado["Débito"] = df_calculado["Débito"].fillna(0.0)
df_calculado["Es Renovación"] = df_calculado["Es Renovación"].fillna(False)
df_calculado[columnas_semanas] = df_calculado[columnas_semanas].fillna(False)

# Fórmulas de cálculo
FACTOR_INTERES = 1.20
SEMANAS_TOTALES = 15

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
    df_calculado["Monto Prestado"] * factor_ganancia
)

df_calculado["Total a Pagar"] = (
    df_calculado["Monto Prestado"] * FACTOR_INTERES
)
df_calculado["Pago Semanal"] = (
    df_calculado["Total a Pagar"] / SEMANAS_TOTALES
)

df_calculado["Semanas Pagadas"] = df_calculado[columnas_semanas].sum(axis=1)
df_calculado["Total Cobrado"] = (
    df_calculado["Semanas Pagadas"] * df_calculado["Pago Semanal"]
)
df_calculado["Saldo Restante"] = (
    df_calculado["Total a Pagar"] - df_calculado["Total Cobrado"]
)

# --- 5. Métricas e Indicadores ---
ganancia_total = df_calculado["Ganancia Abuela"].sum()
monto_total_prestado = df_calculado["Monto Prestado"].sum()

col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="💰 Total Prestado", value=f"${monto_total_prestado:,.2f}"
    )
with col2:
    st.metric(
        label=f"💵 Ganancia Total de la Abuela ({porcentaje_comision:.1f}%)",
        value=f"${ganancia_total:,.2f}",
    )

# 6. Tabla de Resumen de Saldos (Usando column_config seguro)
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

df_resumen = df_calculado[columnas_resumen]

# Muestra la tabla usando la configuración segura de Streamlit
st.dataframe(
    df_resumen,
    column_config={
        "Monto Prestado": st.column_config.NumberColumn("Monto Prestado", format="$%.2f"),
        "Ganancia Abuela": st.column_config.NumberColumn("Ganancia Abuela", format="$%.2f"),
        "Monto Entregado a Mano": st.column_config.NumberColumn("Monto Entregado a Mano", format="$%.2f"),
        "Total a Pagar": st.column_config.NumberColumn("Total a Pagar", format="$%.2f"),
        "Pago Semanal": st.column_config.NumberColumn("Pago Semanal", format="$%.2f"),
        "Total Cobrado": st.column_config.NumberColumn("Total Cobrado", format="$%.2f"),
        "Saldo Restante": st.column_config.NumberColumn("Saldo Restante", format="$%.2f"),
    },
    use_container_width=True,
    hide_index=True,
)
