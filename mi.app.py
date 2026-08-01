import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Calculadora de Préstamos", layout="wide")

st.title("👵 Calculadora de Cobranza Catorcenal")
st.write(
    "Ingresa o modifica el **Monto Prestado** en la tabla y los demás datos se calcularán automáticamente."
)

# 1. Definir los datos iniciales de los clientes
data = [
    {"Cliente": "Cliente 1", "Monto Prestado": 1000.0},
    {"Cliente": "Cliente 2", "Monto Prestado": 2500.0},
    {"Cliente": "Cliente 3", "Monto Prestado": 5000.0},
]

df_inicial = pd.DataFrame(data)

# 2. Mostrar la tabla editable donde tu abuela solo modifica el 'Monto Prestado'
df_editado = st.data_editor(
    df_inicial,
    column_config={
        "Cliente": st.column_config.TextColumn("Nombre del Cliente"),
        "Monto Prestado": st.column_config.NumberColumn(
            "Monto Prestado ($)", min_value=0, format="$%.2f"
        ),
    },
    disabled=["Cliente"],  # Para evitar que borre los nombres por accidente
    num_rows="dynamic",  # Permite agregar nuevos clientes si lo necesita
    hide_index=True,
)

# 3. Fórmulas de cálculo (Ajusta los factores según las políticas del trabajo)
# Ejemplo: Un interés total del 20% dividido en 14 semanas (7 catorcenas)
FACTOR_INTERES = 1.20  # Total a pagar = Monto * 1.20
SEMANAS_TOTALES = 14
CATORCENAS_TOTALES = 7

# Realizar los cálculos dinámicos sobre lo que ingresó
df_calculado = df_editado.copy()
df_calculado["Total a Pagar"] = (
    df_calculado["Monto Prestado"] * FACTOR_INTERES
)
df_calculado["Pago Semanal"] = (
    df_calculado["Total a Pagar"] / SEMANAS_TOTALES
)
df_calculado["Pago Catorcenal"] = (
    df_calculado["Total a Pagar"] / CATORCENAS_TOTALES
)

# --- Aclaración sobre la Nómina ---
# Si "Nómina" se refiere a la catorcena específica o saldo acumulado:
df_calculado["Nómina / Catorcena"] = (
    df_calculado["Pago Catorcenal"]
)  # O ajusta la fórmula correspondiente

# Reordenar y dar formato bonito para mostrar los resultados finales
st.subheader("📋 Tabla con Resultados y Pagos")

# Aplicar formato de moneda ($) para que a tu abuela le sea fácil de leer
df_formateado = df_calculado.style.format(
    {
        "Monto Prestado": "${:,.2f}",
        "Total a Pagar": "${:,.2f}",
        "Pago Semanal": "${:,.2f}",
        "Pago Catorcenal": "${:,.2f}",
        "Nómina / Catorcena": "${:,.2f}",
    }
)

st.dataframe(df_formateado, use_container_width=True)
