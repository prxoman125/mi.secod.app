import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Calculadora de Préstamos", layout="wide")

st.title("👵 Calculadora de Cobranza Catorcenal")
st.write(
    "Ingresa o modifica los datos directamente en la tabla para calcular automáticamente los entregables y pagos."
)

# 1. Datos iniciales de ejemplo con la columna 'Débito'
data = [
    {
        "Cliente": "Cliente 1",
        "Monto Prestado": 1000.0,
        "Es Renovación": False,
        "Débito": 0.0,
    },
    {
        "Cliente": "Cliente 2",
        "Monto Prestado": 2500.0,
        "Es Renovación": True,
        "Débito": 300.0,
    },
    {
        "Cliente": "Cliente 3",
        "Monto Prestado": 5000.0,
        "Es Renovación": False,
        "Débito": 500.0,
    },
]

df_inicial = pd.DataFrame(data)

# 2. Tabla editable para tu abuela
df_editado = st.data_editor(
    df_inicial,
    column_config={
        "Cliente": st.column_config.TextColumn("Nombre del Cliente"),
        "Monto Prestado": st.column_config.NumberColumn(
            "Monto Nuevo Préstamo ($)", min_value=0, format="$%.2f"
        ),
        "Es Renovación": st.column_config.CheckboxColumn(
            "¿Renovación?",
            help="Aplica el descuento de $50 por cada $1,000 prestados.",
            default=False,
        ),
        "Débito": st.column_config.NumberColumn(
            "Débito / Adeudo Anterior ($)",
            min_value=0,
            format="$%.2f",
            help="Ingresa cuánto debía el cliente anteriormente.",
        ),
    },
    disabled=["Cliente"],  # Bloquea los nombres para evitar borrados
    num_rows="dynamic",  # Permite agregar o eliminar clientes
    hide_index=True,
)

# 3. Fórmulas de cálculo
FACTOR_INTERES = 1.20  # 20% de interés total
SEMANAS_TOTALES = 14
CATORCENAS_TOTALES = 7

df_calculado = df_editado.copy()

# Cálculo del descuento por renovación ($50 por cada $1,000)
df_calculado["Descuento Renovación"] = df_calculado.apply(
    lambda row: (row["Monto Prestado"] / 1000.0) * 50.0
    if row["Es Renovación"]
    else 0.0,
    axis=1,
)

# Monto Efectivo a Entregar = Monto Prestado - Descuento Renovación - Débito Anterior
df_calculado["Monto Entregado a Mano"] = (
    df_calculado["Monto Prestado"]
    - df_calculado["Descuento Renovación"]
    - df_calculado["Débito"]
)

# Cálculos de pagos cobrados al cliente (basado en el Monto Prestado Total)
df_calculado["Total a Pagar"] = (
    df_calculado["Monto Prestado"] * FACTOR_INTERES
)
df_calculado["Pago Semanal"] = (
    df_calculado["Total a Pagar"] / SEMANAS_TOTALES
)
df_calculado["Pago Catorcenal"] = (
    df_calculado["Total a Pagar"] / CATORCENAS_TOTALES
)
df_calculado["Nómina / Catorcena"] = df_calculado["Pago Catorcenal"]

# 4. Presentación final de los resultados
st.subheader("📋 Resumen de Entregas y Cobranza")

columnas_mostrar = [
    "Cliente",
    "Monto Prestado",
    "Es Renovación",
    "Descuento Renovación",
    "Débito",
    "Monto Entregado a Mano",
    "Total a Pagar",
    "Pago Semanal",
    "Pago Catorcenal",
    "Nómina / Catorcena",
]

df_resultado = df_calculado[columnas_mostrar]

# Formatear números con signo de dinero
df_formateado = df_resultado.style.format(
    {
        "Monto Prestado": "${:,.2f}",
        "Descuento Renovación": "${:,.2f}",
        "Débito": "${:,.2f}",
        "Monto Entregado a Mano": "${:,.2f}",
        "Total a Pagar": "${:,.2f}",
        "Pago Semanal": "${:,.2f}",
        "Pago Catorcenal": "${:,.2f}",
        "Nómina / Catorcena": "${:,.2f}",
    }
)

st.dataframe(df_formateado, use_container_width=True)
