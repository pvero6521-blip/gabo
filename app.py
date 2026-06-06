import streamlit as st
import json
from datetime import date, timedelta
from typing import Dict, List, Tuple

# ── Página ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Predictor de Siembra — Morelos 2026",
    page_icon="🌱",
    layout="centered"
)

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

ZONAS_CLIMA: Dict[str, Dict] = {
    "ZONA_1_NORTE_ALTO": {
        "descripcion": "Norte alto / Volcánico",
        "clima_tipo": "Templado subhúmedo C(w)",
        "altitud_ref": "2000-3000 msnm",
        "temp_media":     [9.5, 10.8, 13.2, 15.4, 16.0, 15.2, 14.1, 14.0, 13.6, 12.0, 10.2, 9.0],
        "precipitacion":  [8.2, 6.4,  10.8, 22.0, 56.4, 128.6, 175.2, 162.4, 128.8, 58.2, 14.4, 7.6],
        "humedad_rel":    [72, 65, 58, 56, 60, 74, 82, 83, 82, 76, 70, 72],
        "heladas_riesgo": [True, True, True, False, False, False, False, False, False, False, True, True],
    },
    "ZONA_2_VALLES_ALTOS": {
        "descripcion": "Valles altos / Cuernavaca",
        "clima_tipo": "Semicálido subhúmedo A(C)(w)",
        "altitud_ref": "1200-2000 msnm",
        "temp_media":     [17.2, 18.6, 21.0, 23.2, 24.4, 23.2, 22.0, 21.8, 21.4, 20.2, 18.4, 17.0],
        "precipitacion":  [8.2,  5.6,  9.4,  22.8, 60.4, 158.6, 188.4, 174.2, 128.6, 52.8, 12.4, 6.8],
        "humedad_rel":    [60, 54, 48, 46, 52, 68, 76, 77, 76, 69, 61, 60],
        "heladas_riesgo": [False]*12,
    },
    "ZONA_3_CUENCA_ORIENTE": {
        "descripcion": "Cuenca oriente / Cuautla-Yautepec",
        "clima_tipo": "Cálido subhúmedo Aw",
        "altitud_ref": "900-1500 msnm",
        "temp_media":     [18.4, 19.8, 22.4, 25.0, 26.8, 25.6, 24.2, 24.0, 23.4, 21.8, 19.4, 17.8],
        "precipitacion":  [9.4,  6.8,  8.2,  20.4, 58.2, 152.4, 196.8, 186.4, 148.6, 62.4, 14.2, 8.6],
        "humedad_rel":    [57, 51, 46, 44, 50, 67, 75, 76, 74, 67, 58, 57],
        "heladas_riesgo": [False]*12,
    },
    "ZONA_4_SUR_CALIDO": {
        "descripcion": "Sur cálido / Jojutla-Zacatepec",
        "clima_tipo": "Cálido subhúmedo Aw (más cálido)",
        "altitud_ref": "700-1200 msnm",
        "temp_media":     [20.8, 22.2, 25.0, 27.8, 29.6, 28.4, 27.0, 26.8, 26.2, 24.4, 21.8, 20.2],
        "precipitacion":  [10.4, 7.2,  7.6,  18.6, 52.4, 164.8, 218.6, 204.2, 162.4, 68.8, 16.4, 9.8],
        "humedad_rel":    [62, 56, 50, 48, 54, 72, 80, 81, 80, 73, 64, 62],
        "heladas_riesgo": [False]*12,
    },
}

MUNICIPIOS: Dict[str, Dict] = {
    "Huitzilac":         {"zona":"ZONA_1_NORTE_ALTO","altitud":2650,"region":"Norte volcánico","cultivos_principales":["Papa","Maíz","Avena forrajera","Haba"]},
    "Tlalnepantla":      {"zona":"ZONA_1_NORTE_ALTO","altitud":2400,"region":"Norte volcánico","cultivos_principales":["Nopal","Maíz","Papa","Maguey"]},
    "Tetela del Volcán": {"zona":"ZONA_1_NORTE_ALTO","altitud":2200,"region":"Norte volcánico","cultivos_principales":["Papa","Maíz","Durazno","Pera"]},
    "Hueyapan":          {"zona":"ZONA_1_NORTE_ALTO","altitud":2100,"region":"Norte volcánico","cultivos_principales":["Maíz","Frijol","Papa","Durazno"]},
    "Ocuituco":          {"zona":"ZONA_1_NORTE_ALTO","altitud":1950,"region":"Norte volcánico","cultivos_principales":["Maíz","Frijol","Papa","Aguacate"]},
    "Cuernavaca":        {"zona":"ZONA_2_VALLES_ALTOS","altitud":1510,"region":"Valle central","cultivos_principales":["Flores ornamentales","Maíz","Aguacate","Jitomate"]},
    "Jiutepec":          {"zona":"ZONA_2_VALLES_ALTOS","altitud":1300,"region":"Valle central","cultivos_principales":["Flores ornamentales","Maíz","Aguacate"]},
    "Temixco":           {"zona":"ZONA_2_VALLES_ALTOS","altitud":1260,"region":"Valle central","cultivos_principales":["Maíz","Flores ornamentales","Aguacate","Chile"]},
    "Xochitepec":        {"zona":"ZONA_2_VALLES_ALTOS","altitud":1200,"region":"Valle central","cultivos_principales":["Maíz","Flores","Caña de azúcar","Sorgo"]},
    "Emiliano Zapata":   {"zona":"ZONA_2_VALLES_ALTOS","altitud":1280,"region":"Valle central","cultivos_principales":["Flores ornamentales","Maíz","Jitomate"]},
    "Tepoztlán":         {"zona":"ZONA_2_VALLES_ALTOS","altitud":1700,"region":"Norte serrano","cultivos_principales":["Nopal","Maíz","Aguacate","Durazno"]},
    "Atlatlahucan":      {"zona":"ZONA_2_VALLES_ALTOS","altitud":1560,"region":"Oriente serrano","cultivos_principales":["Maíz","Frijol","Aguacate"]},
    "Totolapan":         {"zona":"ZONA_2_VALLES_ALTOS","altitud":1650,"region":"Oriente serrano","cultivos_principales":["Nopal","Maíz","Aguacate","Pera"]},
    "Cuautla":           {"zona":"ZONA_3_CUENCA_ORIENTE","altitud":1310,"region":"Valle oriente","cultivos_principales":["Flores ornamentales","Maíz","Sorgo","Jitomate"]},
    "Yautepec":          {"zona":"ZONA_3_CUENCA_ORIENTE","altitud":1200,"region":"Valle oriente","cultivos_principales":["Caña de azúcar","Maíz","Sorgo","Flores"]},
    "Ayala":             {"zona":"ZONA_3_CUENCA_ORIENTE","altitud":1240,"region":"Valle oriente","cultivos_principales":["Maíz","Sorgo","Jitomate","Chile"]},
    "Yecapixtla":        {"zona":"ZONA_3_CUENCA_ORIENTE","altitud":1580,"region":"Oriente serrano","cultivos_principales":["Maíz","Frijol","Aguacate","Durazno"]},
    "Jonacatepec":       {"zona":"ZONA_3_CUENCA_ORIENTE","altitud":1180,"region":"Suroriente","cultivos_principales":["Maíz","Sorgo","Jitomate","Pepino"]},
    "Jantetelco":        {"zona":"ZONA_3_CUENCA_ORIENTE","altitud":1100,"region":"Suroriente","cultivos_principales":["Maíz","Sorgo","Caña de azúcar","Frijol"]},
    "Tepalcingo":        {"zona":"ZONA_3_CUENCA_ORIENTE","altitud":980,"region":"Suroriente","cultivos_principales":["Maíz","Sorgo","Caña de azúcar","Jitomate"]},
    "Axochiapan":        {"zona":"ZONA_3_CUENCA_ORIENTE","altitud":940,"region":"Suroriente","cultivos_principales":["Maíz","Sorgo","Caña de azúcar","Chile"]},
    "Zacualpan de Amilpas":{"zona":"ZONA_3_CUENCA_ORIENTE","altitud":1250,"region":"Suroriente","cultivos_principales":["Maíz","Frijol","Aguacate"]},
    "Temoac":            {"zona":"ZONA_3_CUENCA_ORIENTE","altitud":1380,"region":"Oriente serrano","cultivos_principales":["Maíz","Frijol","Aguacate","Nopal"]},
    "Zacatepec":         {"zona":"ZONA_4_SUR_CALIDO","altitud":917,"region":"Sur cañero","cultivos_principales":["Caña de azúcar","Sorgo","Maíz","Frijol"]},
    "Jojutla":           {"zona":"ZONA_4_SUR_CALIDO","altitud":900,"region":"Sur cañero","cultivos_principales":["Caña de azúcar","Arroz","Sorgo","Maíz"]},
    "Tlaltizapán":       {"zona":"ZONA_4_SUR_CALIDO","altitud":930,"region":"Sur cañero","cultivos_principales":["Caña de azúcar","Sorgo","Maíz","Arroz"]},
    "Puente de Ixtla":   {"zona":"ZONA_4_SUR_CALIDO","altitud":890,"region":"Sur cañero","cultivos_principales":["Arroz","Caña de azúcar","Sorgo","Maíz"]},
    "Tlaquiltenango":    {"zona":"ZONA_4_SUR_CALIDO","altitud":820,"region":"Sur cañero","cultivos_principales":["Caña de azúcar","Sorgo","Maíz","Jitomate"]},
    "Amacuzac":          {"zona":"ZONA_4_SUR_CALIDO","altitud":800,"region":"Sur cañero","cultivos_principales":["Caña de azúcar","Sorgo","Maíz"]},
    "Tetecala":          {"zona":"ZONA_4_SUR_CALIDO","altitud":880,"region":"Poniente cálido","cultivos_principales":["Caña de azúcar","Maíz","Sorgo"]},
    "Mazatepec":         {"zona":"ZONA_4_SUR_CALIDO","altitud":940,"region":"Poniente cálido","cultivos_principales":["Maíz","Caña de azúcar","Sorgo","Aguacate"]},
    "Miacatlán":         {"zona":"ZONA_4_SUR_CALIDO","altitud":980,"region":"Poniente cálido","cultivos_principales":["Maíz","Sorgo","Aguacate","Caña de azúcar"]},
    "Coatlán del Río":   {"zona":"ZONA_4_SUR_CALIDO","altitud":860,"region":"Poniente cálido","cultivos_principales":["Caña de azúcar","Maíz","Sorgo"]},
    "Coatetelco":        {"zona":"ZONA_4_SUR_CALIDO","altitud":920,"region":"Poniente cálido","cultivos_principales":["Maíz","Sorgo","Caña de azúcar"]},
    "Xoxocotla":         {"zona":"ZONA_4_SUR_CALIDO","altitud":900,"region":"Sur cañero","cultivos_principales":["Caña de azúcar","Maíz","Sorgo"]},
}

CULTIVOS: Dict[str, Dict] = {
    "Maíz (temporal)":        {"emoji":"🌽","temp_min_germ":10,"temp_optima":25,"temp_max":35,"temp_min_crec":15,"precip_ciclo_mm":500,"ciclo_dias":120,"dias_a_cosecha":90,"humedad_optima":(60,80),"requiere_lluvia":True},
    "Caña de azúcar":         {"emoji":"🌿","temp_min_germ":18,"temp_optima":28,"temp_max":38,"temp_min_crec":20,"precip_ciclo_mm":1200,"ciclo_dias":365,"dias_a_cosecha":330,"humedad_optima":(60,80),"requiere_lluvia":True},
    "Arroz":                  {"emoji":"🌾","temp_min_germ":18,"temp_optima":28,"temp_max":38,"temp_min_crec":20,"precip_ciclo_mm":900,"ciclo_dias":130,"dias_a_cosecha":110,"humedad_optima":(75,90),"requiere_lluvia":True},
    "Sorgo":                  {"emoji":"🌾","temp_min_germ":15,"temp_optima":27,"temp_max":38,"temp_min_crec":18,"precip_ciclo_mm":400,"ciclo_dias":120,"dias_a_cosecha":90,"humedad_optima":(50,70),"requiere_lluvia":True},
    "Jitomate / Tomate rojo": {"emoji":"🍅","temp_min_germ":15,"temp_optima":24,"temp_max":32,"temp_min_crec":16,"precip_ciclo_mm":300,"ciclo_dias":120,"dias_a_cosecha":80,"humedad_optima":(60,70),"requiere_lluvia":False},
    "Nopal (verdura)":        {"emoji":"🌵","temp_min_germ":12,"temp_optima":22,"temp_max":32,"temp_min_crec":15,"precip_ciclo_mm":350,"ciclo_dias":90,"dias_a_cosecha":45,"humedad_optima":(40,65),"requiere_lluvia":False},
    "Flores ornamentales":    {"emoji":"🌸","temp_min_germ":14,"temp_optima":20,"temp_max":28,"temp_min_crec":15,"precip_ciclo_mm":600,"ciclo_dias":180,"dias_a_cosecha":90,"humedad_optima":(60,75),"requiere_lluvia":False},
    "Aguacate":               {"emoji":"🥑","temp_min_germ":16,"temp_optima":22,"temp_max":30,"temp_min_crec":14,"precip_ciclo_mm":1200,"ciclo_dias":365,"dias_a_cosecha":270,"humedad_optima":(65,80),"requiere_lluvia":True},
    "Frijol":                 {"emoji":"🫘","temp_min_germ":12,"temp_optima":22,"temp_max":32,"temp_min_crec":14,"precip_ciclo_mm":350,"ciclo_dias":90,"dias_a_cosecha":75,"humedad_optima":(50,70),"requiere_lluvia":True},
    "Papa":                   {"emoji":"🥔","temp_min_germ":7,"temp_optima":18,"temp_max":25,"temp_min_crec":10,"precip_ciclo_mm":500,"ciclo_dias":110,"dias_a_cosecha":90,"humedad_optima":(70,85),"requiere_lluvia":False},
    "Chile / Pimiento":       {"emoji":"🌶️","temp_min_germ":16,"temp_optima":26,"temp_max":35,"temp_min_crec":18,"precip_ciclo_mm":400,"ciclo_dias":150,"dias_a_cosecha":90,"humedad_optima":(60,75),"requiere_lluvia":False},
    "Durazno":                {"emoji":"🍑","temp_min_germ":5,"temp_optima":18,"temp_max":26,"temp_min_crec":8,"precip_ciclo_mm":600,"ciclo_dias":365,"dias_a_cosecha":120,"humedad_optima":(55,75),"requiere_lluvia":False},
}

def calcular_score_mes(mes_idx, cultivo, clima):
    score = 100.0
    razones = []
    temp    = clima["temp_media"][mes_idx]
    precip  = clima["precipitacion"][mes_idx]
    humedad = clima["humedad_rel"][mes_idx]
    helada  = clima["heladas_riesgo"][mes_idx]
    t_min, t_opt, t_max = cultivo["temp_min_germ"], cultivo["temp_optima"], cultivo["temp_max"]
    if temp < t_min:
        pen = min(65, (t_min - temp) * 9)
        score -= pen
        razones.append(f"⚠️ Temp {temp:.1f}°C bajo mínimo ({t_min}°C)")
    elif temp > t_max:
        pen = min(55, (temp - t_max) * 7)
        score -= pen
        razones.append(f"🔥 Temp {temp:.1f}°C excede máximo ({t_max}°C)")
    else:
        rango = t_max - t_min
        dist  = abs(temp - t_opt) / (rango / 2 + 0.1)
        score += max(0, 12 * (1 - dist))
        razones.append(f"✅ Temperatura óptima ({temp:.1f}°C)")
    if helada:
        score -= 45
        razones.append("❄️ Riesgo de heladas")
    precip_mens = cultivo["precip_ciclo_mm"] / (cultivo["ciclo_dias"] / 30)
    if cultivo["requiere_lluvia"]:
        if precip < precip_mens * 0.3:
            score -= 22
            razones.append(f"🏜️ Lluvia insuficiente ({precip:.0f}mm)")
        elif precip >= precip_mens * 0.75:
            score += 8
            razones.append(f"🌧️ Lluvia favorable ({precip:.0f}mm)")
    else:
        if precip > 220:
            score -= 12
            razones.append(f"🌊 Lluvia excesiva ({precip:.0f}mm)")
    h_min, h_max = cultivo["humedad_optima"]
    if h_min <= humedad <= h_max:
        score += 5
        razones.append(f"💧 Humedad óptima ({humedad}%)")
    elif humedad > h_max + 12:
        score -= 8
        razones.append(f"💦 Humedad alta ({humedad}%)")
    return max(0.0, min(100.0, score)), razones

def predecir(municipio, cultivo_nombre, anio=2026):
    mun  = MUNICIPIOS[municipio]
    zona = ZONAS_CLIMA[mun["zona"]]
    cult = CULTIVOS[cultivo_nombre]
    resultados = []
    for i in range(12):
        score, razones = calcular_score_mes(i, cult, zona)
        f_inicio  = date(anio, i + 1, 15)
        f_cosecha = f_inicio + timedelta(days=cult["dias_a_cosecha"])
        resultados.append({
            "mes": MESES[i], "mes_idx": i,
            "score": round(score, 1),
            "fecha_siembra": f_inicio.strftime("%d/%b/%Y"),
            "fecha_cosecha": f_cosecha.strftime("%d/%b/%Y"),
            "temp": zona["temp_media"][i],
            "precipitacion": zona["precipitacion"][i],
            "humedad": zona["humedad_rel"][i],
            "helada": zona["heladas_riesgo"][i],
            "razones": razones,
        })
    ranking = sorted(resultados, key=lambda x: x["score"], reverse=True)
    return ranking, resultados

def color_semaforo(score):
    if score >= 80: return "🟢"
    if score >= 65: return "🟡"
    if score >= 40: return "🟠"
    return "🔴"

def etiqueta(score):
    if score >= 80: return "Excelente"
    if score >= 65: return "Bueno"
    if score >= 40: return "Regular"
    return "No apto"

# ── UI ────────────────────────────────────────────────────────────────────────
st.title("🌱 Predictor de Siembra — Morelos 2026")
st.caption("Fuentes: CONAGUA · SADER · INIFAP · SIAP | Normales Climatológicas 1981-2010")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    municipio = st.selectbox(
        "📍 Selecciona tu municipio",
        sorted(MUNICIPIOS.keys()),
        index=sorted(MUNICIPIOS.keys()).index("Zacatepec")
    )

with col2:
    cultivo_nombre = st.selectbox(
        "🌿 Selecciona el cultivo",
        list(CULTIVOS.keys()),
        format_func=lambda x: f"{CULTIVOS[x]['emoji']} {x}"
    )

if st.button("🔍 Analizar fechas óptimas", use_container_width=True, type="primary"):
    mun_data  = MUNICIPIOS[municipio]
    zona_data = ZONAS_CLIMA[mun_data["zona"]]

    st.markdown("---")

    # Info del municipio
    with st.expander("📍 Información del municipio", expanded=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("Altitud", f"{mun_data['altitud']} msnm")
        c2.metric("Región", mun_data["region"])
        c3.metric("Zona climática", zona_data["descripcion"])
        st.caption(f"Cultivos típicos: {', '.join(mun_data['cultivos_principales'])}")

    ranking, todos = predecir(municipio, cultivo_nombre)

    # Top 3
    st.subheader("🏆 Mejores meses para sembrar")
    cols = st.columns(3)
    for i, m in enumerate(ranking[:3]):
        with cols[i]:
            st.metric(
                label=f"#{i+1} — {m['mes']}",
                value=f"{m['score']:.0f}/100",
                delta=etiqueta(m['score'])
            )
            st.markdown(f"**{color_semaforo(m['score'])} {etiqueta(m['score'])}**")
            st.caption(f"Siembra: {m['fecha_siembra']}")
            st.caption(f"Cosecha: {m['fecha_cosecha']}")
            st.caption(f"🌡️ {m['temp']:.1f}°C | 🌧️ {m['precipitacion']:.0f}mm")

    # Tabla completa
    st.subheader("📊 Ranking completo — los 12 meses")
    for m in ranking:
        barra_val = int(m["score"] / 5)
        barra_txt = "█" * barra_val + "·" * (20 - barra_val)
        helada_ico = "❄️" if m["helada"] else ""
        st.markdown(
            f"`{m['mes']:<12}` {color_semaforo(m['score'])} **{m['score']:.0f}%** "
            f"`{barra_txt}` "
            f"🌡️{m['temp']:.1f}°C 🌧️{m['precipitacion']:.0f}mm {helada_ico}"
        )

    # Detalle del mejor mes
    st.subheader(f"🔎 Detalle del mejor mes: {ranking[0]['mes']}")
    for r in ranking[0]["razones"]:
        st.markdown(f"- {r}")

    st.markdown("---")
    st.caption("⚠️ Prototipo basado en Normales Climatológicas históricas (1981-2010). "
               "Para decisiones reales consultar al CADER o técnico INIFAP de tu región.")
