import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Calculadora de Préstamos", layout="wide")

st.title("👵 Calculadora y Control de Cobranza (15 Semanas)")
st.write(
    "Ingresa los datos del cliente y marca con una palomita (✔️) las semanas que ya pagó."
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

# Configuración del editor para la tabla interactiva
config_columnas = {
    "Cliente": st.column_config.TextColumn("Nombre del Cliente"),
    "Monto Prestado": st.column_config.NumberColumn(
        "Monto Prestado ($)", min_value=0, format="$%.2f"
    ),
    "Es Renovación": st.column_config.CheckboxColumn(
        "¿Renovación?",
        help="Aplica el descuento de $50 por cada $1,000 prestados.",
        default=False,
    ),
    "Débito": st.column_config.NumberColumn(
        "Débito / Adeudo Anterior ($)", min_value=0, format="$%.2f"
    ),
}

# Agregar la configuración de la casilla (checkbox) para cada una de las 15 semanas
for sem in columnas_semanas:
    config_columnas[sem] = st.column_config.CheckboxColumn(
        sem, help=f"Marca si pagó la {sem}", default=False
    )

# 3. Mostrar la tabla para que tu abuela ingrese o controle los pagos
df_editado = st.data_editor(
    df_inicial,
    column_config=config_columnas,
    disabled=["Cliente"],
    num_rows="dynamic",
    hide_index=True,
)

# 4. Fórmulas de cálculo
FACTOR_INTERES = 1.20  # 20% de interés total
SEMANAS_TOTALES = 15
CATORCENAS_TOTALES = 7.5

df_calculado = df_editado.copy()

# Descuento por renovación ($50 por cada $1,000)
df_calculado["Descuento Renovación"] = df_calculado.apply(
    lambda row: (row["Monto Prestado"] / 1000.0) * 50.0
    if row["Es Renovación"]
    else 0.0,
    axis=1,
)

# Monto a entregar en mano
df_calculado["Monto Entregado a Mano"] = (
    df_calculado["Monto Prestado"]
    - df_calculado["Descuento Renovación"]
    - df_calculado["Débito"]
)

# Cálculo del total y pagos
df_calculado["Total a Pagar"] = (
    df_calculado["Monto Prestado"] * FACTOR_INTERES
)
df_calculado["Pago Semanal"] = (
    df_calculado["Total a Pagar"] / SEMANAS_TOTALES
)

# Contar cuántas semanas ha palomeado tu abuela
df_calculado["Semanas Pagadas"] = df_calculado[columnas_semanas].sum(axis=1)

# Calcular cuánto dinero ha abonado y cuánto le falta por pagar
df_calculado["Total Cobrado"] = (
    df_calculado["Semanas Pagadas"] * df_calculado["Pago Semanal"]
)
df_calculado["Saldo Restante"] = (
    df_calculado["Total a Pagar"] - df_calculado["Total Cobrado"]
)

# 5. Tabla de Resumen de Saldos
st.subheader("📊 Control de Pagos y Saldo Restante")

columnas_resumen = [
    "Cliente",
    "Monto Prestado",
    "Monto Entregado a Mano",
    "Total a Pagar",
    "Pago Semanal",
    "Semanas Pagadas",
    "Total Cobrado",
    "Saldo Restante",
]

df_resumen = df_calculado[columnas_resumen]

st.dataframe(
    df_resumen.style.format(
        {
            "Monto Prestado": "${:,.2f}",
            "Monto Entregado a Mano": "${:,.2f}",
            "Total a Pagar": "${:,.2f}",
            "Pago Semanal": "${:,.2f}",
            "Total Cobrado": "${:,.2f}",
            "Saldo Restante": "${:,.2f}",
        }
    ),
    use_container_width=True,
)
