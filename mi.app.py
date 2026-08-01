import pandas as pd
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Control de Cobranza - Crece & CrediK", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- URL DEL LOGO OFICIAL CRECE & CREDIK ---
URL_LOGO_CRECE_CREDIK = "https://i.ibb.co/2vBvRkS/image-6d7741.png"

# --- ESTILOS CSS PERSONALIZADOS (MODO CLARO Y OSCURO) ---
st.markdown("""
    <style>
    .stApp {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Encabezado con Logo Oficial */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
    }
    .brand-logo-img {
        max-height: 85px;
        width: auto;
        object-fit: contain;
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.1;
    }
    .header-subtitle {
        opacity: 0.8;
        font-size: 0.95rem;
        margin: 4px 0 0 0;
    }

    /* Tarjetas de Métricas estilizadas */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        padding: 12px 16px;
        border-left: 5px solid #00A887;
    }

    /* Credencial INE México estilo limpio */
    .ine-card {
        width: 250px;
        height: 145px;
        border: 1px solid rgba(128, 128, 128, 0.4);
        background: rgba(128, 128, 128, 0.08);
        border-radius: 8px;
        padding: 8px;
        font-family: Arial, sans-serif;
        position: relative;
        margin-bottom: 10px;
    }
    .ine-header {
        font-size: 7.5px;
        font-weight: bold;
        text-align: center;
        border-bottom: 1px solid rgba(128, 128, 128, 0.3);
        padding-bottom: 2px;
        margin-bottom: 6px;
    }
    .ine-body {
        display: flex;
        gap: 8px;
    }
    .ine-photo {
        width: 45px !important;
        height: 60px !important;
        border-radius: 3px !important;
        border: 1px solid rgba(128, 128, 128, 0.5);
        object-fit: cover;
    }
    .ine-details {
        font-size: 8px;
        line-height: 1.2;
    }
    .ine-footer {
        position: absolute;
        bottom: 4px;
        left: 8px;
        right: 8px;
        font-size: 6.5px;
        font-family: monospace;
        letter-spacing: 1px;
        border: 1px solid rgba(128, 128, 128, 0.3);
        padding: 1px;
        text-align: center;
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
    """Corrige automáticamente minúsculas y espacios al formato Nombre Propio."""
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
    """Genera credencial INE compacta adaptable a modo claro/oscuro."""
    curp_dummy = f"{nombre[:2].upper()}X900101HMCLR09"
    foto_url = AVATAR_MUJER if genero == "Mujer" else AVATAR_HOMBRE
    return f"""
    <div class="ine-card">
        <div class="ine-header">
            INSTITUTO NACIONAL ELECTORAL<br>CREDENCIAL PARA VOTAR
        </div>
        <div class="ine-body">
            <img src="{foto_url}" class="ine-photo">
            <div class="ine-details">
                <b>NOMBRE:</b><br>{nombre.upper()}<br><br>
                <b>DOMICILIO:</b><br>LEON, GUANAJUATO<br><br>
                <b>CURP:</b> {curp_dummy}
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

# --- ENCABEZADO CON LOGO OFICIAL ---
st.markdown(f"""
    <div class="brand-container">
        <img src="{URL_LOGO_CRECE_CREDIK}" class="brand-logo-img" alt="Crece & CrediK Logo">
        <div>
            <h1 class="header-title">Crece & CrediK</h1>
            <p class="header-subtitle">Sistema Simplificado de Control de Cobranza y Crédito - León, Guanajuato</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- CONTROLES OPERATIVOS ---
with st.expander("Filtros y Calculadora de Préstamos", expanded=True):
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    
    with col_ctrl1:
        cobrador_seleccionado = st.selectbox(
            "Seleccionar Ruta / Cobrador:",
            ["Todas las Rutas", "Ruta 1 - Zona Centro", "Ruta 2 - León Moderno", "Ruta 3 - San Miguel"]
        )
    
    with col_ctrl2:
        filtro_buscar = st.text_input("Buscar Cliente por Nombre:", placeholder="Escriba aquí para buscar...")
        
    with col_ctrl3:
        st.write("Calculadora Rápida:")
        monto_sim = st.number_input("Monto a Calcular ($):", value=1000.0, step=500.0)
        pago_semanal_sim = (monto_sim * FACTOR_INTERES) / SEMANAS_TOTALES
        st.caption(f"Pago semanal: **${pago_semanal_sim:,.2f}** a {SEMANAS_TOTALES} semanas.")

# --- PESTAÑAS PRINCIPALES ---
tab_captura, tab_resumen, tab_fichas = st.tabs(["Captura y Pagos", "Resumen de Saldos", "Fichas e INE"])

with tab_captura:
    st.subheader("Captura de Clientes y Cobranza Semanal")
    st.info("Instrucciones: Modifique las casillas directamente en la tabla. Al presionar 'Enter' en el nombre, se corregirá automáticamente.")
    
    # Pre-procesar corrección de nombres
    df_temp = st.session_state.df_clientes.copy()
    if "Cliente" in df_temp.columns:
        df_temp["Cliente"] = df_temp["Cliente"].apply(auto_corregir_nombre)

    # Filtrar por cliente si se busca
    if filtro_buscar:
        df_temp = df_temp[df_temp["Cliente"].str.contains(filtro_buscar, case=False, na=False)]

    # Configuración limpia sin columna Avatar
    config_columnas_edicion = {
        "Cliente": st.column_config.TextColumn("Nombre del Cliente", required=True),
        "Monto Prestado": st.column_config.NumberColumn("Monto Prestado ($)", min_value=0.0, format="$%.2f", default=0.0),
        "Es Renovación": st.column_config.CheckboxColumn("¿Es Renovación?", default=False),
        "Débito": st.column_config.NumberColumn("Débito ($)", min_value=0.0, format="$%.2f", default=0.0),
    }

    for sem in columnas_semanas:
        config_columnas_edicion[sem] = st.column_config.CheckboxColumn(sem, default=False)

    # Botón para agregar rápidamente una fila nueva
    if st.button("Agregar Nuevo Cliente"):
        nuevo_registro = {
            "Cliente": "Nuevo Cliente",
            "Monto Prestado": 1000.0,
            "Es Renovación": False,
            "Débito": 0.0,
            **{sem: False for sem in columnas_semanas}
        }
        st.session_state.df_clientes = pd.concat([st.session_state.df_clientes, pd.DataFrame([nuevo_registro])], ignore_index=True)
        st.rerun()

    # Data Editor sin avatares ni hipervínculos
    df_editado = st.data_editor(
        df_temp,
        column_config=config_columnas_edicion,
        num_rows="dynamic",
        hide_index=True,
        key="editor_tabla"
    )

    df_editado["Cliente"] = df_editado["Cliente"].apply(auto_corregir_nombre)
    st.session_state.df_clientes = df_editado.copy()

# --- CÁLCULOS FINANCIEROS ---
df_calculado = st.session_state.df_clientes.copy()

df_calculado["Género"] = df_calculado["Cliente"].apply(auto_detectar_genero)

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

# --- PESTAÑA RESUMEN ---
with tab_resumen:
    st.subheader("Métricas Totales")
    
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
    st.subheader("Resumen de Saldos")

    columnas_resumen = [
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
            "Cliente": st.column_config.TextColumn("Nombre Cliente"),
            "Género": st.column_config.TextColumn("Género"),
            "Monto Prestado": st.column_config.NumberColumn("Monto Prestado", format="$%.2f"),
            "Ganancia Empresa": st.column_config.NumberColumn("Ganancia Empresa", format="$%.2f"),
            "Monto Entregado": st.column_config.NumberColumn("Monto Entregado", format="$%.2f"),
            "Total a Pagar": st.column_config.NumberColumn("Total a Pagar", format="$%.2f"),
            "Pago Semanal": st.column_config.NumberColumn("Pago Semanal", format="$%.2f"),
            "Total Cobrado": st.column_config.NumberColumn("Total Cobrado", format="$%.2f"),
            "Saldo Restante": st.column_config.NumberColumn("Saldo Restante", format="$%.2f"),
        },
        use_container_width=True,
        hide_index=True,
    )

# --- PESTAÑA FICHAS E INE ---
with tab_fichas:
    st.subheader("Identificaciones INE (Muestra Visual)")
    st.caption("Muestra automatizada de credenciales de elector para el expediente corporativo.")
    
    if not df_calculado.empty:
        columnas_por_fila = 3
        registros = df_calculado.to_dict('records')
        
        # Iteración modular para prevenir errores de índice
        for i in range(0, len(registros), columnas_por_fila):
            chunk = registros[i:i + columnas_por_fila]
            cols = st.columns(columnas_por_fila)
            for idx, row in enumerate(chunk):
                with cols[idx]:
                    st.markdown(f"**{row['Cliente']}**")
                    ine_html = generar_html_ine(row["Cliente"], row["Género"])
                    st.markdown(ine_html, unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info("No hay clientes registrados en el sistema.")
