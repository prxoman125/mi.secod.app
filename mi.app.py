import pandas as pd
import streamlit as st

# Configuración de la página (sin barra lateral visible)
st.set_page_config(
    page_title="Control de Cobranza - Crece & Credick", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# URLs de avatares anónimos (Hombre / Mujer)
AVATAR_HOMBRE = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
AVATAR_MUJER = "https://cdn-icons-png.flaticon.com/512/3135/3135789.png"

# Fórmulas y constantes
FACTOR_INTERES = 1.20
SEMANAS_TOTALES = 15
PORCENTAJE_GANANCIA = 15.0  # 15% predeterminado
FACTOR_GANANCIA = PORCENTAJE_GANANCIA / 100.0

columnas_semanas = [f"Semana {i}" for i in range(1, 16)]

# Inicialización de datos en Session State para mantener sincronizadas ambas tablas
if "df_clientes" not in st.session_state:
    st.session_state.df_clientes = pd.DataFrame([
        {
            "Género": "Hombre",
            "Avatar": AVATAR_HOMBRE,
            "Cliente": "Cliente 1",
            "Monto Prestado": 1000.0,
            "Es Renovación": False,
            "Débito": 0.0,
            **{sem: False for sem in columnas_semanas},
        },
        {
            "Género": "Mujer",
            "Avatar": AVATAR_MUJER,
            "Cliente": "Cliente 2",
            "Monto Prestado": 2500.0,
            "Es Renovación": True,
            "Débito": 300.0,
            **{sem: True if i <= 3 else False for i, sem in enumerate(columnas_semanas, 1)},
        },
    ])

st.title("Crece & Credick")
st.caption("Sistema de Gestión de Crédito y Control de Cobranza")

# --- 1. TABLA EDITABLE ---
st.subheader("Captura de Clientes y Pagos Semanales")

config_columnas_edicion = {
    "Género": st.column_config.SelectboxColumn(
        "Género",
        options=["Hombre", "Mujer"],
        default="Hombre",
        required=True
    ),
    "Avatar": st.column_config.ImageColumn(
        "Perfil", 
        width="small"
    ),
    "Cliente": st.column_config.TextColumn("Nombre del Cliente", required=True),
    "Monto Prestado": st.column_config.NumberColumn(
        "Monto Prestado ($)", min_value=0.0, format="$%.2f", default=0.0
    ),
    "Es Renovación": st.column_config.CheckboxColumn(
        "¿Renovación?",
        default=False,
    ),
    "Débito": st.column_config.NumberColumn(
        "Débito ($)", min_value=0.0, format="$%.2f", default=0.0
    ),
}

for sem in columnas_semanas:
    config_columnas_edicion[sem] = st.column_config.CheckboxColumn(
        sem, default=False
    )

# Editor interactivo
df_editado = st.data_editor(
    st.session_state.df_clientes,
    column_config=config_columnas_edicion,
    num_rows="dynamic",
    hide_index=True,
    key="editor_tabla"
)

# Actualizar el avatar dinámicamente según el género seleccionado
df_editado["Avatar"] = df_editado["Género"].apply(
    lambda g: AVATAR_MUJER if g == "Mujer" else AVATAR_HOMBRE
)

# Guardar cambios sincronizados
st.session_state.df_clientes = df_editado.copy()

# --- 2. CÁLCULOS Y LIMPIEZA ---
df_calculado = df_editado.copy()

df_calculado["Cliente"] = df_calculado["Cliente"].fillna("Nuevo Cliente")
df_calculado["Monto Prestado"] = df_calculado["Monto Prestado"].fillna(0.0)
df_calculado["Débito"] = df_calculado["Débito"].fillna(0.0)
df_calculado["Es Renovación"] = df_calculado["Es Renovación"].fillna(False)
df_calculado[columnas_semanas] = df_calculado[columnas_semanas].fillna(False)

df_calculado["Descuento Renovación"] = df_calculado.apply(
    lambda row: (row["Monto Prestado"] / 1000.0) * 50.0 if row["Es Renovación"] else 0.0,
    axis=1,
)

df_calculado["Monto Entregado"] = (
    df_calculado["Monto Prestado"]
    - df_calculado["Descuento Renovación"]
    - df_calculado["Débito"]
)

df_calculado["Ganancia Empresa"] = df_calculado["Monto Prestado"] * FACTOR_GANANCIA
df_calculado["Total a Pagar"] = df_calculado["Monto Prestado"] * FACTOR_INTERES
df_calculado["Pago Semanal"] = df_calculado["Total a Pagar"] / SEMANAS_TOTALES

df_calculado["Semanas Pagadas"] = df_calculado[columnas_semanas].sum(axis=1)
df_calculado["Total Cobrado"] = df_calculado["Semanas Pagadas"] * df_calculado["Pago Semanal"]
df_calculado["Saldo Restante"] = df_calculado["Total a Pagar"] - df_calculado["Total Cobrado"]

# --- 3. TARJETAS DE MÉTRICAS ---
st.divider()

col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="Total Capital Prestado", 
        value=f"${df_calculado['Monto Prestado'].sum():,.2f}"
    )
with col2:
    st.metric(
        label=f"Ganancia Estimada ({PORCENTAJE_GANANCIA:.1f}%)",
        value=f"${df_calculado['Ganancia Empresa'].sum():,.2f}",
    )

st.divider()

# --- 4. TABLA RESUMEN DE SALDOS ---
st.subheader("Resumen General de Saldos y Cobranza")

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
        "Avatar": st.column_config.ImageColumn("Perfil", width="small"),
        "Cliente": st.column_config.TextColumn("Cliente"),
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
