import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Simulador de Atajadas de Portero", layout="wide")

st.title("⚽ Simulador de Atajadas y Física del Tiro")
st.write(
    "Ingresa los parámetros del tiro y del portero manualmente para calcular"
    " el tiempo de reacción, la dirección y la probabilidad de atajar el balón."
)

# --- BARRA LATERAL: INGRESO MANUAL DE DATOS ---
st.sidebar.header("⚙️ Configuración (Entrada Manual)")

# 1. Medidas de la Portería
st.sidebar.subheader("📐 Portería")
ancho_porteria = st.sidebar.number_input(
    "Ancho de la portería (m)", min_value=1.0, max_value=12.0, value=7.32, step=0.1
)
alto_porteria = st.sidebar.number_input(
    "Alto de la portería (m)", min_value=1.0, max_value=4.0, value=2.44, step=0.05
)

# 2. Datos del Portero
st.sidebar.subheader("🧤 Portero")
altura_portero = st.sidebar.number_input(
    "Altura del portero (m)", min_value=1.00, max_value=2.30, value=1.85, step=0.01
)

# 3. Datos del Tiro
st.sidebar.subheader("🎯 Tiro")
distancia_tiro = st.sidebar.number_input(
    "Distancia del tiro (m)", min_value=1.0, max_value=60.0, value=11.0, step=0.5
)
velocidad_kmh = st.sidebar.number_input(
    "Velocidad del balón (km/h)", min_value=10.0, max_value=200.0, value=90.0, step=5.0
)

# Ubicación manual del disparo en coordenadas (metros)
st.sidebar.markdown("**🎯 Dirección Manual del Balón (en metros):**")
coordenada_x = st.sidebar.number_input(
    f"Posición horizontal X (0 = Poste izq, {ancho_porteria:.2f} = Poste der)",
    min_value=-1.0,
    max_value=ancho_porteria + 1.0,
    value=ancho_porteria / 2,
    step=0.1,
)
coordenada_y = st.sidebar.number_input(
    f"Posición vertical Y (0 = Suelo, {alto_porteria:.2f} = Travesaño)",
    min_value=-0.5,
    max_value=alto_porteria + 1.0,
    value=alto_porteria / 2,
    step=0.05,
)

# --- CÁLCULOS FÍSICOS Y LÓGICA ---

# Convertir velocidad a m/s
velocidad_ms = velocidad_kmh / 3.6

# Tiempo de vuelo del balón (Tiempo de reacción disponible)
tiempo_reaccion = distancia_tiro / velocidad_ms

# Coordenadas del centro de la portería
centro_x = ancho_porteria / 2

# Calcular porcentaje Y dentro del marco para la recomendación
porcentaje_y = (coordenada_y / alto_porteria) * 100

# Recomendación de la atajada según la altura vertical
if porcentaje_y <= 33:
  zona_altura = "Abajo (Raza / Al suelo)"
  recomendacion = (
      "El portero debe lanzarse arrastrado o colocar la mano abajo de rápido"
      " alcance."
  )
elif porcentaje_y <= 66:
  zona_altura = "A media altura"
  recomendacion = (
      "El portero debe realizar un salto lateral a media altura extendiendo"
      " los brazos firmes."
  )
else:
  zona_altura = "Arriba (Cerca del travesaño)"
  recomendacion = (
      "El portero debe realizar un salto explosivo hacia arriba/diagonal"
      " buscando el manotazo."
  )

# Verificar si el tiro va fuera
es_gol_o_arco = (0 <= coordenada_x <= ancho_porteria) and (
    0 <= coordenada_y <= alto_porteria
)

# Cálculo simplificado de la Probabilidad de Atajada
distancia_desde_centro = np.sqrt(
    (coordenada_x - centro_x) ** 2 + coordenada_y**2
)
alcance_maximo = altura_portero * 1.45
tiempo_util = tiempo_reaccion - 0.25  # Tiempo de reacción humano (~0.25s)

if tiempo_util <= 0 or not es_gol_o_arco:
  probabilidad = 0.0
else:
  velocidad_requerida = distancia_desde_centro / tiempo_util

  if velocidad_requerida <= (alcance_maximo * 2.0):
    probabilidad = 95 - (velocidad_requerida * 15)
  else:
    probabilidad = 20 - (velocidad_requerida * 5)

  # Ajuste por tiros a las esquinas superiores (escuadras)
  porcentaje_x = (coordenada_x / ancho_porteria) * 100
  if (porcentaje_x < 15 or porcentaje_x > 85) and porcentaje_y > 75:
    probabilidad -= 25

probabilidad = max(0.0, min(100.0, probabilidad))

# --- MOSTRAR RESULTADOS EN STREAMLIT ---

col1, col2 = st.columns(2)

with col1:
  st.subheader("⏱️ Análisis del Tiro")
  st.metric(
      label="Tiempo de Reacción Disponible",
      value=f"{tiempo_reaccion:.2f} segundos",
  )
  st.metric(
      label="Velocidad del Balón",
      value=f"{velocidad_ms:.1f} m/s ({velocidad_kmh:.0f} km/h)",
  )
  st.metric(label="Distancia del Disparo", value=f"{distancia_tiro:.1f} metros")

with col2:
  st.subheader("🧤 Análisis de la Atajada")
  if not es_gol_o_arco:
    st.error("❌ El disparo va fuera de la portería.")
  else:
    st.metric(label="Probabilidad de Atajada", value=f"{probabilidad:.1f} %")
    st.info(f"**Zona de la atajada:** {zona_altura}")
    st.success(f"**Recomendación:** {recomendacion}")

st.markdown("---")

# --- REPRESENTACIÓN GRÁFICA DE LA PORTERÍA ---
st.subheader("🎯 Visualización del Disparo en la Portería")

fig, ax = plt.subplots(figsize=(8, 4))

# Dibujar Marco de la Portería
ax.plot(
    [0, 0, ancho_porteria, ancho_porteria],
    [0, alto_porteria, alto_porteria, 0],
    color="black",
    lw=5,
    label="Portería",
)
# Línea de Gol (Suelo)
ax.plot([-0.5, ancho_porteria + 0.5], [0, 0], color="green", lw=3)

# Posición del Portero (Centro, parado)
ax.plot(
    [centro_x, centro_x],
    [0, min(altura_portero, alto_porteria)],
    color="blue",
    lw=4,
    label="Portero (Inicio)",
)
ax.scatter([centro_x], [min(altura_portero, alto_porteria)], color="blue", s=100)

# Punto de Impacto del Balón
color_balon = "red" if es_gol_o_arco else "gray"
ax.scatter(
    [coordenada_x],
    [coordenada_y],
    color=color_balon,
    s=200,
    zorder=5,
    label="Ubicación del Balón",
)

# Ajustar límites del gráfico
ax.set_xlim(-1, ancho_porteria + 1)
ax.set_ylim(-0.5, alto_porteria + 0.5)
ax.set_xlabel("Ancho (m)")
ax.set_ylabel("Alto (m)")
ax.set_title("Vista Frontal de la Portería")
ax.legend(loc="upper right")
ax.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig)
