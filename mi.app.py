import pandas as pd
import streamlit as st

# Configuración de la página (sin barra lateral)
st.set_page_config(
    page_title="Control de Cobranza - Crece & Credick", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- RECURSOS MULTIMEDIA (AVATARES E INE ANÓNIMAS) ---
AVATAR_HOMBRE = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
AVATAR_MUJER = "https://cdn-icons-png.flaticon.com/512/3135/3135789.png"

# Imágenes de credenciales INE anónimas (formato horizontal)
INE_HOMBRE = "https://img.freepik.com/vector-gratis/plantilla-tarjeta-identificacion-diseno-plano_23-2148992229.jpg"
INE_MUJER = "https://img.freepik.com/vector-gratis/plantilla-tarjeta-identificacion-femenina-diseno-plano_23-2148992228.jpg"

# --- CONSTANTES ---
FACTOR_INTERES = 1.20
SEMANAS_TOTALES = 15
PORCENTAJE_GANANCIA = 15.0
FACTOR_GANANCIA = PORCENTAJE_GANANCIA / 100.0

columnas_semanas = [f"Semana {i}" for i in range(1, 16)]

# --- FUNCIONES DE AUTOMATIZACIÓN ---
def auto_corregir_nombre(texto: str) -> str:
    """Corrige automáticamente minúsculas y espacios al dar Enter."""
    if not isinstance(texto, str) or not texto.strip():
        return "Cliente Nuevo"
    # Convierte a formato de nombre propio (capitaliza cada palabra)
    palabras = texto.strip().split()
    return " ".join([p.capitalize() for p in palabras])

def auto_detectar_genero(nombre: str) -> str:
    """Detecta el género automáticamente según el primer nombre."""
    if not nombre or nombre == "Cliente Nuevo":
        return "Hombre"
        
    primer_nombre = nombre.strip().split()[0].lower()
    
    # Nombres comunes femeninos especiales o terminaciones
    femeninos_especiales = ["guadalupe", "rosario", "carmen", "pilar", "beatriz", "luz", "mercedes", "concepcion", "socorro", "isabel", "raquel", "fernanda"]
    masculinos_especiales = ["jose", "josé", "andres", "andrés", "luca", "borja", "mapa"]
    
    if primer_nombre in femeninos_especiales:
        return "Mujer"
    if primer_nombre in masculinos_especiales:
        return "Hombre"
        
    # Regla por terminación típica en español ('a' casi siempre es femenino)
    if primer_nombre.endswith(('a', 'ia', 'ina', 'eth')):
        return "Mujer"
        
    return "Hombre"

# --- ESTADO DE LA SESIÓN ---
if "df_clientes" not in st.session_state:
    st.session_state.df_clientes = pd.DataFrame([
        {
            "Cliente": "Juan Carlos Pérez",
            "Monto Prestado": 1000.0,
            "Es Renovación": False,
            "Débito": 0.0,
            **{sem: False for sem in columnas_semanas},
        },
        {
            "Cliente": "María Elena Gómez",
            "Monto Prestado": 2500.0,
            "Es Renovación": True,
            "Débito": 300.0,
            **{sem: True if i <= 3 else False for i, sem in enumerate(columnas_semanas, 1)},
        },
    ])

# Encabezado corporativo
st.title("Crece & Credick")
st.caption("Sistema de Gestión de Crédito y Control de Cobranza - León, Guanajuato")

# --- 1. CAPTURA Y EDICIÓN DE DATOS ---
st.subheader("Captura de Clientes y Pagos Semanales")

config_columnas_edicion = {
    "Cliente": st.column_config.TextColumn("Nombre del Cliente", required=True),
    "Monto Prestado": st.column_config.NumberColumn(
        "Monto Prestado ($)", min_value=0.0, format="$%.2f", default=0.0
    ),
    "Es Renovación": st.column_config.CheckboxColumn(
        "¿Renovación?", default=False
    ),
    "Débito": st.column_config.NumberColumn(
        "Débito ($)", min_value=0.0, format="$%.2f", default=0.0
    ),
}

for sem in columnas_semanas:
    config_columnas_edicion[sem] = st.column_config.CheckboxColumn(sem, default=False)

df_editado = st.data_editor(
    st.session_state.df_clientes,
    column_config=config_columnas_edicion,
    num_rows="dynamic",
    hide_index=True,
    key="editor_tabla"
)

# --- 2. PROCESAMIENTO AUTOMÁTICO DE DATOS ---
df_calculado = df_editado.copy()

# A) Corrección automática de nombres al presionar Enter
df_calculado["Cliente"] = df_calculado["Cliente"].apply(auto_corregir_nombre)

# B) Detección automática de género
df_calculado["Género"] = df_calculado["Cliente"].apply(auto_detectar_genero)

# C) Asignación de imágenes (Avatar e INE anónima)
df_calculado["Avatar"] = df_calculado["Género"].apply(
    lambda g: AVATAR_MUJER if g == "Mujer" else AVATAR_HOMBRE
)
df_calculado["INE Anónima"] = df_calculado["Género"].apply(
    lambda g: INE_MUJER if g == "Mujer" else INE_HOMBRE
)

# Sincronizar nombres corregidos en la sesión
st.session_state.df_clientes = df_editado.copy()

# Limpieza de valores nulos
df_calculado["Monto Prestado"] = df_calculado["Monto Prestado"].fillna(0.0)
df_calculado["Débito"] = df_calculado["Débito"].fillna(0.0)
df_calculado["Es Renovación"] = df_calculado["Es Renovación"].fillna(False)
df_calculado[columnas_semanas] = df_calculado[columnas_semanas].fillna(False)

# Fórmulas financieras
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

# --- 3. MÉTRICAS GENERALES ---
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

# --- 4. TABLA RESUMEN GENERAL (CON IMÁGENES OPTIMIZADAS) ---
st.subheader("Resumen General de Saldos y Cobranza")

columnas_resumen = [
    "Avatar",
    "Cliente",
    "Género",
    "INE Anónima",
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
        # Ancho 'small' y formato optimizado para evitar desplazamientos e imágenes cortadas
        "Avatar": st.column_config.ImageColumn("Perfil", width="small"),
        "INE Anónima": st.column_config.ImageColumn("Documento INE", width="medium"),
        "Cliente": st.column_config.TextColumn("Cliente"),
        "Género": st.column_config.TextColumn("Género Detectado"),
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
