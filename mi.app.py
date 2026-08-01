import difflib
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Calculadora y Control de Cobranza", layout="wide"
)

# Configuración constante de comisión (sin menú lateral)
PORCENTAJE_COMISION = 15.0  # 15% fijo
FACTOR_GANANCIA = PORCENTAJE_COMISION / 100.0
FACTOR_INTERES = 1.20
SEMANAS_TOTALES = 15

st.title("👵 Calculadora y Control de Cobranza")
st.write(
    "Ingresa o busca los datos de tus clientes y marca con una palomita (✔️) las semanas pagadas."
)

# 1. Crear las columnas de las 15 semanas
columnas_semanas = [f"Semana {i}" for i in range(1, 16)]

# 2. Datos iniciales de ejemplo en estado de sesión (Session State) para preservar cambios
if "df_clientes" not in st.session_state:
    data = [
        {
            "Cliente": "Maria Gomez",
            "Monto Prestado": 1000.0,
            "Es Renovación": False,
            "Débito": 0.0,
            **{sem: False for sem in columnas_semanas},
        },
        {
            "Cliente": "Juan Perez",
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

# --- BÚSQUEDA Y CORRECCIÓN AUTOMÁTICA DE NOMBRES ---
st.subheader("🔍 Buscar Cliente")
busqueda_input = st.text_input(
    "Escribe el nombre del cliente para filtrar:",
    placeholder="Ej. Maria Gmez (corrige errores tipográficos automáticamente)",
)

df_para_mostrar = st.session_state.df_clientes.copy()

if busqueda_input.strip():
    lista_clientes = df_para_mostrar["Cliente"].dropna().astype(str).tolist()

    # Buscar coincidencia exacta o similar
    coincidencias = difflib.get_close_matches(
        busqueda_input, lista_clientes, n=3, cutoff=0.4
    )

    if coincidencias:
        nombre_sugerido = coincidencias[0]
        if busqueda_input.lower() != nombre_sugerido.lower():
            st.info(
                f"💡 ¿Quisiste decir **'{nombre_sugerido}'**? Mostrando resultados similares."
            )

        # Filtrar el DataFrame con los nombres parecidos encontrados
        df_para_mostrar = df_para_mostrar[
            df_para_mostrar["Cliente"].isin(coincidencias)
        ]
    else:
        # Búsqueda parcial si no hay coincidencias de difflib
        df_para_mostrar = df_para_mostrar[
            df_para_mostrar["Cliente"].str.contains(
                busqueda_input, case=False, na=False
            )
        ]
        if df_para_mostrar.empty:
            st.warning("⚠️ No se encontraron clientes con ese nombre.")

# Configuración del editor interactivo
config_columnas = {
    "Cliente": st.column_config.TextColumn(
        "Nombre del Cliente", required=True
    ),
    "Monto Prestado": st.column_config.NumberColumn(
        "Monto Prestado ($)", min_value=0.0, format="$%.2f", default=0.0
    ),
    "Es Renovación": st.column_config.CheckboxColumn(
        "¿Renovación?",
        help="Aplica el descuento de $50 por cada $1,000 prestados.",
        default=False,
    ),
    "Débito": st.column_config.NumberColumn(
        "Débito / Adeudo Anterior ($)",
        min_value=0.0,
        format="$%.2f",
        default=0.0,
    ),
}

for sem in columnas_semanas:
    config_columnas[sem] = st.column_config.CheckboxColumn(
        sem, help=f"Marca si pagó la {sem}", default=False
    )

# 3. Tabla editable
df_editado = st.data_editor(
    df_para_mostrar,
    column_config=config_columnas,
    num_rows="dynamic",
    hide_index=True,
    key="data_editor",
)

# Actualizar el estado global con los cambios realizados
for idx, row in df_editado.iterrows():
    st.session_state.df_clientes.loc[idx] = row

# 4. Limpieza y Cálculos
df_calculado = df_editado.copy()

if not df_calculado.empty:
    df_calculado["Cliente"] = df_calculado["Cliente"].fillna("Nuevo Cliente")
    df_calculado["Monto Prestado"] = df_calculado["Monto Prestado"].fillna(0.0)
    df_calculado["Débito"] = df_calculado["Débito"].fillna(0.0)
    df_calculado["Es Renovación"] = df_calculado["Es Renovación"].fillna(False)
    df_calculado[columnas_semanas] = df_calculado[columnas_semanas].fillna(
        False
    )

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

    # --- 5. Métricas e Indicadores ---
    ganancia_total = df_calculado["Ganancia Abuela"].sum()
    monto_total_prestado = df_calculado["Monto Prestado"].sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="💰 Total Prestado (Filtrado)",
            value=f"${monto_total_prestado:,.2f}",
        )
    with col2:
        st.metric(
            label=f"💵 Ganancia Total de la Abuela ({PORCENTAJE_COMISION:.1f}%)",
            value=f"${ganancia_total:,.2f}",
        )

    # 6. Tabla de Resumen de Saldos
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

    st.dataframe(
        df_resumen,
        column_config={
            "Monto Prestado": st.column_config.NumberColumn(
                "Monto Prestado", format="$%.2f"
            ),
            "Ganancia Abuela": st.column_config.NumberColumn(
                "Ganancia Abuela", format="$%.2f"
            ),
            "Monto Entregado a Mano": st.column_config.NumberColumn(
                "Monto Entregado a Mano", format="$%.2f"
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
