import unicodedata
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Calculadora y Control de Cobranza",
    page_icon="👵",
    layout="wide",
)

# Configuración fija de comisión e interés
PORCENTAJE_COMISION = 15.0
FACTOR_GANANCIA = PORCENTAJE_COMISION / 100.0
FACTOR_INTERES = 1.20
SEMANAS_TOTALES = 15

# Diccionario de acentuación automática
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
    """Corrige espacios, mayúsculas iniciales y acentos."""
    if not isinstance(cadena, str) or not cadena.strip():
        return ""
    texto = " ".join(cadena.split())
    palabras = texto.split(" ")
    palabras_corregidas = []

    for p in palabras:
        p_lower = p.lower()
        if p_lower in NOMBRES_ACENTUADOS:
            palabras_corregidas.append(NOMBRES_ACENTUADOS[p_lower])
        else:
            palabras_corregidas.append(p.capitalize())

    return " ".join(palabras_corregidas)


# 1. Crear las columnas de las 15 semanas
columnas_semanas = [f"Semana {i}" for i in range(1, 16)]

# Imagen por defecto si no hay foto cargada
AVATAR_DEFAULT = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

# 2. Inicializar la base de datos en Session State (Preservar datos)
if "df_clientes" not in st.session_state:
    data = [
        {
            "Foto": "https://raw.githubusercontent.com/streamlit/streamlit/main/e2e/scripts/components_iframe/static/avatar.png",
            "Cliente": "María Gómez",
            "Monto Prestado": 1000.0,
            "Es Renovación": False,
            "Débito": 0.0,
            **{sem: False for sem in columnas_semanas},
        },
        {
            "Foto": AVATAR_DEFAULT,
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


# Callback para guardar los cambios y corregir texto de forma persistente
def guardar_cambios():
    if "editor_tabla" in st.session_state:
        # Obtener los cambios del editor
        edits = st.session_state["editor_tabla"]

        # Filas editadas
        for idx, cambios in edits.get("edited_rows", {}).items():
            for col, val in cambios.items():
                if col == "Cliente":
                    val = auto_corregir_nombre(val)
                st.session_state.df_clientes.at[idx, col] = val

        # Filas agregadas
        for nueva_fila in edits.get("added_rows", []):
            if "Foto" not in nueva_fila or not nueva_fila["Foto"]:
                nueva_fila["Foto"] = AVATAR_DEFAULT
            if "Cliente" in nueva_fila:
                nueva_fila["Cliente"] = auto_corregir_nombre(
                    nueva_fila["Cliente"]
                )

            # Rellenar valores por defecto para evitar NaN
            for sem in columnas_semanas:
                if sem not in nueva_fila:
                    nueva_fila[sem] = False

            st.session_state.df_clientes = pd.concat(
                [
                    st.session_state.df_clientes,
                    pd.DataFrame([nueva_fila]),
                ],
                ignore_index=True,
            )

        # Filas eliminadas
        filas_borradas = edits.get("deleted_rows", [])
        if filas_borradas:
            st.session_state.df_clientes = st.session_state.df_clientes.drop(
                filas_borradas
            ).reset_index(drop=True)


# --- INTERFAZ PRINCIPAL ---
st.title("👵 Control de Cobranza y Préstamos")
st.caption(
    "Sistema de control semanal. Las casillas marcadas y los nombres se guardan en tiempo real."
)

st.markdown("---")

# Configuración visual de columnas
config_columnas = {
    "Foto": st.column_config.ImageColumn(
        "Foto", help="Enlace URL de la foto del cliente", width="small"
    ),
    "Cliente": st.column_config.TextColumn(
        "Nombre del Cliente",
        help="Escribe el nombre; se autocorregirá mayúsculas y acentos.",
        required=True,
        width="medium",
    ),
    "Monto Prestado": st.column_config.NumberColumn(
        "Monto Prestado ($)", min_value=0.0, format="$%.2f", default=0.0
    ),
    "Es Renovación": st.column_config.CheckboxColumn(
        "¿Renovación?",
        help="Aplica descuento de $50 por cada $1,000 prestados.",
        default=False,
    ),
    "Débito": st.column_config.NumberColumn(
        "Débito Anterior ($)", min_value=0.0, format="$%.2f", default=0.0
    ),
}

# Configuración de casillas para semanas
for sem in columnas_semanas:
    config_columnas[sem] = st.column_config.CheckboxColumn(
        sem, help=f"Marca si pagó {sem}", default=False
    )

# 3. Mostrar Editor de Tabla Interactivo
st.subheader("📋 Registro e Historial de Pagos")

st.data_editor(
    st.session_state.df_clientes,
    column_config=config_columnas,
    num_rows="dynamic",
    hide_index=True,
    key="editor_tabla",
    on_change=guardar_cambios,
)

# 4. Cálculos Matemáticos
df_calculado = st.session_state.df_clientes.copy()

if not df_calculado.empty:
    # Asegurar valores no nulos
    df_calculado["Monto Prestado"] = df_calculado["Monto Prestado"].fillna(0.0)
    df_calculado["Débito"] = df_calculado["Débito"].fillna(0.0)
    df_calculado["Es Renovación"] = df_calculado["Es Renovación"].fillna(False)
    df_calculado[columnas_semanas] = df_calculado[columnas_semanas].fillna(
        False
    )

    # Aplicar Fórmulas
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

    st.markdown("---")

    # --- MÉTRICAS GENERALES ---
    st.subheader("📈 Resumen Financiero")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="💰 TotalPrestado",
            value=f"${df_calculado['Monto Prestado'].sum():,.2f}",
        )
    with col2:
        st.metric(
            label="💵 Ganancia Estimada",
            value=f"${df_calculado['Ganancia Abuela'].sum():,.2f}",
        )
    with col3:
        st.metric(
            label="📉 Saldo Pendiente por Cobrar",
            value=f"${df_calculado['Saldo Restante'].sum():,.2f}",
        )

    # --- TABLA RESUMEN ---
    st.subheader("📊 Resumen de Cuentas por Cliente")

    columnas_resumen = [
        "Foto",
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
            "Foto": st.column_config.ImageColumn("Foto", width="small"),
            "Monto Prestado": st.column_config.NumberColumn(
                "Monto Prestado", format="$%.2f"
            ),
            "Ganancia Abuela": st.column_config.NumberColumn(
                "Ganancia Abuela", format="$%.2f"
            ),
            "Monto Entregado a Mano": st.column_config.NumberColumn(
                "Entregado a Mano", format="$%.2f"
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
