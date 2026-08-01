import pandas as pd
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Control de Cobranza - Crece & Credick", 
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="💳"
)

# --- ESTILOS CSS PERSONALIZADOS (MEJORA DE DISEÑO UI/UX) ---
st.markdown("""
    <style>
    /* Estilo general y fondo */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Encabezado principal */
    .header-title {
        color: #1E3A8A;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .header-subtitle {
        color: #4B5563;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }

    /* Tarjetas de métricas */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 5px solid #1E3A8A;
    }

    /* Credencial INE México estilo SVG/HTML */
    .ine-card {
        width: 300px;
        height: 180px;
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
        border: 2px solid #000;
        border-radius: 10px;
        padding: 10px;
        font-family: Arial, sans-serif;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        position: relative;
        color: #333;
    }
    .ine-header {
        font-size: 10px;
        font-weight: bold;
        color: #000;
        text-align: center;
        border-bottom: 1px solid #000;
        padding-bottom: 2px;
        margin-bottom: 5px;
    }
    .ine-body {
        display: flex;
        gap: 10px;
    }
    .ine-photo {
        width: 75px;
        height: 95px;
        background-color: #ccc;
        border: 1px solid #555;
        border-radius: 4px;
        object-fit: cover;
    }
    .ine-details {
        font-size: 9px;
        line-height: 1.2;
    }
    .ine-details strong {
        color: #000;
    }
    .ine-footer {
        position: absolute;
        bottom: 5px;
        left: 10px;
        right: 10px;
        font-size: 8px;
        font-family: monospace;
        letter-spacing: 1px;
        background: #fff;
        padding: 2px;
        border: 1px solid #aaa;
    }
    </style>
""", unsafe_allow_html=True)

# --- RECURSOS MULTIMEDIA ---
AVATAR_HOMBRE = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
AVATAR_MUJER = "https://cdn-icons-png.flaticon.com/512/3135/3135789.png"

# --- CONSTANTES FINANCIERAS ---
FACTOR_INTERES = 1.20
SEMANAS_TOTALES = 15
PORCENTAJE_GANANCIA = 15.0
FACTOR_GANANCIA = PORCENTAJE_GANANCIA / 100.0

columnas_semanas = [f"Semana {i}" for i in range(1, 16)]

# --- FUNCIONES DE AUTOMATIZACIÓN ---
def auto_corregir_nombre(texto: str) -> str:
    """Corrige automáticamente minúsculas y espacios formato Nombre Propio."""
    if not isinstance(texto, str) or not texto.strip():
        return "Cliente Nuevo"
    palabras = texto.strip().split()
    return " ".join([p.capitalize() for p in palabras])

def auto_detectar_genero(nombre: str) -> str:
    """Detecta el género según el primer nombre."""
    if not nombre or nombre == "Cliente Nuevo":
        return "Hombre"
        
    primer_nombre = nombre.strip().split()[0].lower()
    
    femeninos_especiales = ["guadalupe", "rosario", "carmen", "pilar", "beatriz", "luz", "mercedes", "concepcion", "socorro", "isabel", "raquel", "fernanda"]
    masculinos_especiales = ["jose", "josé", "andres", "andrés", "luca", "borja"]
    
    if primer_nombre in femeninos_especiales:
        return "Mujer"
    if primer_nombre in masculinos_especiales:
        return "Hombre"
        
    if primer_nombre.endswith(('a', 'ia', 'ina', 'eth')):
        return "Mujer"
        
    return "Hombre"

def generar_html_ine(nombre: str, genero: str) -> str:
    """Genera una tarjeta INE de México en HTML/CSS estilizada."""
    curp_dummy = f"{nombre[:2].upper()}X{900101}HMCLR09"
    foto_url = AVATAR_MUJER if genero == "Mujer" else AVATAR_HOMBRE
    return f"""
    <div class="ine-card">
        <div class="ine-header">
            INSTITUTO NACIONAL ELECTORAL<br><b>CREDENCIAL PARA VOTAR</b>
        </div>
        <div class="ine-body">
            <img src="{foto_url}" class="ine-photo">
            <div class="ine-details">
                <strong>NOMBRE:</strong><br>{nombre.upper()}<br><br>
                <strong>DOMICILIO:</strong><br>LEÓN, GUANAJUATO, MX<br><br>
                <strong>CURP:</strong> {curp_dummy}
            </div>
        </div>
        <div class="ine-footer">
            IDMEX1829384938<<029384920384
        </div>
    </div>
    """

# --- INICIALIZACIÓN DEL ESTADO DE LA SESIÓN ---
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

# --- ENCABEZADO Y TÍTULO ---
st.markdown("<h1 class='header-title'>Crece & Credick</h1>", unsafe_allow_html=True)
st.markdown("<p class='header-subtitle'>Sistema de Gestión de Crédito y Control de Cobranza - León, Guanajuato</p>", unsafe_allow_html=True)

# --- PESTAÑAS PRINCIPALES (MEJORA DE ORGANIZACIÓN) ---
tab_captura, tab_resumen, tab_fichas = st.tabs(["📝 Captura y Pagos", "📊 Resumen de Saldos", "🪪 Fichas e INE"])

with tab_captura:
    st.subheader("Control de Clientes y Pagos Semanales")
    
    # Pre-procesar corrección de nombres directo en el DataFrame base para actualizar ambas tablas a la vez
    df_temp = st.session_state.df_clientes.copy()
    if "Cliente" in df_temp.columns:
        df_temp["Cliente"] = df_temp["Cliente"].apply(auto_corregir_nombre)

    config_columnas_edicion = {
        "Cliente": st.column_config.TextColumn("Nombre del Cliente", required=True),
        "Monto Prestado": st.column_config.NumberColumn("Monto Prestado ($)", min_value=0.0, format="$%.2f", default=0.0),
        "Es Renovación": st.column_config.CheckboxColumn("¿Renovación?", default=False),
        "Débito": st.column_config.NumberColumn("Débito ($)", min_value=0.0, format="$%.2f", default=0.0),
    }

    for sem in columnas_semanas:
        config_columnas_edicion[sem] = st.column_config.CheckboxColumn(sem, default=False)

    # Editor de datos
    df_editado = st.data_editor(
        df_temp,
        column_config=config_columnas_edicion,
        num_rows="dynamic",
        hide_index=True,
        key="editor_tabla"
    )

    # Corrección automática inmediata de los nombres ingresados
    df_editado["Cliente"] = df_editado["Cliente"].apply(auto_corregir_nombre)
    st.session_state.df_clientes = df_editado.copy()

# --- PROCESAMIENTO MATEMÁTICO Y FINANCIERO ---
df_calculado = st.session_state.df_clientes.copy()

df_calculado["Género"] = df_calculado["Cliente"].apply(auto_detectar_genero)
df_calculado["Avatar"] = df_calculado["Género"].apply(lambda g: AVATAR_MUJER if g == "Mujer" else AVATAR_HOMBRE)

df_calculado["Monto Prestado"] = df_calculado["Monto Prestado"].fillna(0.0)
df_calculado["Débito"] = df_calculado["Débito"].fillna(0.0)
df_calculado["Es Renovación"] = df_calculado["Es Renovación"].fillna(False)
df_calculado[columnas_semanas] = df_calculado[columnas_semanas].fillna(False)

# Fórmulas de Crédito
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

# --- CONTENIDO DE LA PESTAÑA RESUMEN ---
with tab_resumen:
    st.subheader("Métricas Globales")
    
    col1, col2, col3 = st.columns(3)
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
    with col3:
        st.metric(
            label="Total Cobrado a la Fecha",
            value=f"${df_calculado['Total Cobrado'].sum():,.2f}",
        )
        
    st.divider()
    st.subheader("Resumen de Saldos y Cobranza")

    columnas_resumen = [
        "Avatar",
        "Cliente",
        "Género",
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
            "Género": st.column_config.TextColumn("Género Detectado"),
            "Monto Prestado": st.column_config.NumberColumn("Monto Prestado", format="$%.2f"),
            "Ganancia Empresa": st.column_config.NumberColumn("Ganancia Crece", format="$%.2f"),
            "Monto Entregado": st.column_config.NumberColumn("Monto Entregado", format="$%.2f"),
            "Total a Pagar": st.column_config.NumberColumn("Total a Pagar", format="$%.2f"),
            "Pago Semanal": st.column_config.NumberColumn("Pago Semanal", format="$%.2f"),
            "Total Cobrado": st.column_config.NumberColumn("Total Cobrado", format="$%.2f"),
            "Saldo Restante": st.column_config.NumberColumn("Saldo Restante", format="$%.2f"),
        },
        use_container_width=True,
        hide_index=True,
    )

# --- CONTENIDO DE LA PESTAÑA DE FICHAS E INE ---
with tab_fichas:
    st.subheader("Vista Previa de Identificación (INE México)")
    st.caption("Ejemplo visual de credenciales de elector generadas para los clientes registrados.")
    
    if not df_calculado.empty:
        cols_ine = st.columns(min(len(df_calculado), 3))
        for idx, row in df_calculado.iterrows():
            col_idx = idx % 3
            with cols_ine[col_idx]:
                st.markdown(f"**Cliente:** {row['Cliente']}")
                ine_html = generar_html_ine(row["Cliente"], row["Género"])
                st.markdown(ine_html, unsafe_allow_html=True)
                st.markdown("---")
    else:
        st.info("No hay clientes registrados para mostrar credenciales.")
