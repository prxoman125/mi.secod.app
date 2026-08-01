import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Control de Cobranza - Crece & Credick", 
    layout="wide"
)

# Imagen por defecto para el avatar de usuario anónimo
AVATAR_ANONIMO = "https://www.w3schools.com/howto/img_avatar.png"

# --- BARRA LATERAL (Sidebar) ---
st.sidebar.title("Configuración")
st.sidebar.subheader("Parámetros de Comisión")

porcentaje_comision = st.sidebar.number_input(
    "Porcentaje de Comisión / Ganancia (%)",
    min_value=0.0,
    max_value=100.0,
    value=15.0,
    step=0.5,
    help="Porcentaje de ganancia aplicado sobre cada $100 prestados.",
)

factor_ganancia = porcentaje_comision / 100.0

st.title("Crece & Credick")
st.caption("Sistema Integral de Gestión de Crédito y Control de Cobranza")
st.write("Ingrese los datos del cliente y marque las semanas liquidadas.")

# 1. Crear las columnas de las 15 semanas
columnas_semanas = [f"Semana {i}" for i in range(1, 16)]

# 2. Datos iniciales de ejemplo
data = [
    {
        "Avatar": AVATAR_ANONIMO,
        "Cliente": "Cliente 1",
        "Monto Prestado": 1000.0,
        "Es Renovación": False,
        "Débito": 0.0,
        **{sem: False for sem in columnas_semanas},
    },
    {
        "Avatar": AVATAR_ANONIMO,
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
    "Avatar": st.column_config.ImageColumn(
        "Perfil", 
        help="Fotografía o avatar del cliente"
    ),
    "Cliente": st.column_config.TextColumn("Nombre del Cliente"),
    "Monto Prestado": st.column_config.NumberColumn(
        "Monto Prestado ($)", min_value=0.0, format="$%.2f", default=0.0
    ),
    "Es Renovación": st.column_config.CheckboxColumn(
        "¿Renovación?",
        help="Aplica bonificación/descuento por renovación.",
        default=False,
    ),
    "Débito": st.column_config.NumberColumn(
        "Débito / Saldo Anterior ($)", min_value=0.0, format="$%.2f", default=0.0
    ),
}

for sem in columnas_semanas:
    config_columnas[sem] = st.column_config.CheckboxColumn(
        sem, help=f"Estatus de pago para {sem}", default=False
    )

# 3. Tabla editable
df_editado = st.data_editor(
    df_inicial,
    column_config=config_columnas,
    num_rows="dynamic",
    hide_index=True,
    disabled=["Avatar"] # El avatar se mantiene fijo por defecto en nuevas filas
)

# 4. Limpieza de datos
df_calculado = df_editado.copy()

df_calculado["Avatar"] = df_calculado["Avatar"].fillna(AVATAR_ANONIMO)
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

df_calculado["Monto Entregado"] = (
    df_calculado["Monto Prestado"]
    - df_calculado["Descuento Renovación"]
    - df_calculado["Débito"]
)

df_calculado["Ganancia Empresa"] = (
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

# --- 5. Métricas Generales ---
ganancia_total = df_calculado["Ganancia Empresa"].sum()
monto_total_prestado = df_calculado["Monto Prestado"].sum()

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="Total Capital Prestado", 
        value=f"${monto_total_prestado:,.2f}"
    )
with col2:
    st.metric(
        label=f"Comisión / Ganancia Estimada ({porcentaje_comision:.1f}%)",
        value=f"${ganancia_total:,.2f}",
    )

st.divider()

# 6. Tabla Resumen
st.subheader("Resumen de Saldos y Cobranza")

columnas_resumen = [
    "Avatar",
    "Cliente",
    "Monto Prestado",
    "Ganancia Empresa",
    "Monto Entregado",
    "Total a Pagar",
    "Pago Semanal",
    "Semanas Pagadas",
    "Total Cobrado",
    "Saldo Restante",
]

df_resumen = df_calculado[columnas_resumen]

st.dataframe(
    df_resumen,
    column_config={
        "Avatar": st.column_config.ImageColumn("Perfil"),
        "Monto Prestado": st.column_config.NumberColumn("Monto Prestado", format="$%.2f"),
        "Ganancia Empresa": st.column_config.NumberColumn("Ganancia Crece & Credick", format="$%.2f"),
        "Monto Entregado": st.column_config.NumberColumn("Monto Entregado", format="$%.2f"),
        "Total a Pagar": st.column_config.NumberColumn("Total a Pagar", format="$%.2f"),
        "Pago Semanal": st.column_config.NumberColumn("Pago Semanal", format="$%.2f"),
        "Total Cobrado": st.column_config.NumberColumn("Total Cobrado", format="$%.2f"),
        "Saldo Restante": st.column_config.NumberColumn("Saldo Restante", format="$%.2f"),
    },
    use_container_width=True,
    hide_index=True,
)
