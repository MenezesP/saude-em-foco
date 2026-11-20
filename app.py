import html
import json
import re
import unicodedata
import urllib.error
import urllib.request
from urllib.parse import quote_plus
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Saúde em Foco | Juazeiro",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# A interface usa as variáveis nativas do tema do Streamlit. Assim, os mesmos
# componentes acompanham corretamente os modos light, dark e system.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --sf-green: #16806b;
        --sf-green-dark: #0d5b4c;
        --sf-radius: 20px;
        --sf-border: var(--secondary-background-color);
    }

    .stApp {
        font-family: 'DM Sans', sans-serif;
        background: var(--background-color);
    }
    [data-testid="stAppViewContainer"] { background: var(--background-color); }
    [data-testid="stHeader"] { background: transparent; }
    .block-container {
        max-width: 1240px;
        padding-top: 1.25rem;
        padding-bottom: 2.5rem;
    }

    h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] {
        color: var(--text-color);
    }
    h1, h2, h3 { letter-spacing: -0.035em; }
    h1 { font-weight: 800; letter-spacing: -0.045em; }
    h2, h3 { font-weight: 750; }
    [data-testid="stMarkdownContainer"] p { line-height: 1.65; }

    /* Cabeçalho principal */
    .sf-hero {
        position: relative;
        isolation: isolate;
        overflow: hidden;
        padding: clamp(27px, 4.5vw, 50px);
        border-radius: 28px;
        margin: 4px 0 22px;
        color: #ffffff;
        background: linear-gradient(118deg, #0b463e 0%, #116b5a 52%, #23947a 100%);
        box-shadow: 0 16px 38px rgba(8, 65, 54, .17);
    }
    .sf-hero:before {
        content: '';
        position: absolute;
        z-index: -1;
        width: 310px;
        height: 310px;
        right: -85px;
        top: -155px;
        border: 1px solid rgba(255,255,255,.18);
        border-radius: 50%;
        box-shadow: 0 0 0 26px rgba(255,255,255,.045),
                    0 0 0 56px rgba(255,255,255,.035),
                    0 0 0 88px rgba(255,255,255,.025);
    }
    .sf-kicker {
        color: #c9eee2 !important;
        text-transform: uppercase;
        letter-spacing: .14em;
        font-size: .72rem;
        font-weight: 800;
    }
    .sf-hero h1 {
        color: #ffffff !important;
        font-size: clamp(2.1rem, 4.5vw, 3.25rem);
        margin: 9px 0 10px;
        line-height: 1.06;
    }
    .sf-hero p {
        color: #e7f7f1 !important;
        max-width: 730px;
        margin: 0;
        font-size: 1.02rem;
        line-height: 1.65;
    }

    /* Identidade visual e navegação em cartões */
    .sf-brand-row {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 18px;
    }
    .sf-brand-mark {
        width: 58px;
        height: 58px;
        flex: 0 0 58px;
        display: grid;
        place-items: center;
        border-radius: 18px;
        color: #ffffff;
        background: linear-gradient(145deg, #0d5b4c, #16806b);
        box-shadow: 0 8px 20px rgba(13,91,76,.20);
    }
    .sf-brand-name {
        color: var(--text-color);
        font-size: clamp(1.35rem, 2.8vw, 1.8rem);
        line-height: 1.12;
        font-weight: 800;
        letter-spacing: -.045em;
    }
    .sf-brand-subtitle {
        margin-top: 5px;
        color: var(--sf-green);
        font-size: .68rem;
        line-height: 1.4;
        font-weight: 800;
        letter-spacing: .13em;
        text-transform: uppercase;
    }
    .sf-menu-heading {
        margin: 4px 0 9px;
        color: var(--text-color);
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: .10em;
        text-transform: uppercase;
        opacity: .68;
    }
    div[data-testid="stButton"] button {
        min-height: 58px;
        white-space: normal;
        border-radius: 15px;
        border: 1px solid var(--sf-border);
        background: var(--secondary-background-color);
        color: var(--text-color);
        font-size: .91rem;
        font-weight: 700;
        line-height: 1.25;
        padding: 10px 12px;
        box-shadow: 0 3px 12px rgba(20,50,40,.035);
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(115deg, #0d5b4c, #16806b);
        border-color: #16806b;
        color: #ffffff;
        box-shadow: 0 7px 18px rgba(13,91,76,.16);
    }
    div[data-testid="stButton"] button:hover {
        border-color: var(--sf-green);
        color: var(--sf-green-dark);
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(13,91,76,.10);
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        color: #ffffff;
    }

    /* Títulos de seção e blocos informativos */
    .sf-section-kicker {
        color: var(--sf-green) !important;
        font-size: .76rem;
        text-transform: uppercase;
        letter-spacing: .12em;
        font-weight: 800;
        margin-bottom: 3px;
    }
    .sf-feature {
        height: 100%;
        min-height: 158px;
        padding: 22px;
        border: 1px solid var(--sf-border);
        border-radius: var(--sf-radius);
        background: var(--secondary-background-color);
        box-shadow: 0 5px 18px rgba(20, 50, 40, .035);
        transition: transform .18s ease, box-shadow .18s ease;
    }
    .sf-feature:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(20, 50, 40, .08);
    }
    .sf-feature .sf-icon { font-size: 1.55rem; margin-bottom: 11px; }
    .sf-feature h3 {
        font-size: 1.04rem;
        margin: 0 0 8px;
        color: var(--text-color) !important;
    }
    .sf-feature p {
        color: var(--text-color) !important;
        opacity: .82;
        font-size: .91rem;
        margin: 0;
        line-height: 1.55;
    }
    .sf-note {
        padding: 17px 20px;
        border-radius: 16px;
        background: var(--secondary-background-color);
        border: 1px solid var(--sf-border);
        border-left: 4px solid var(--sf-green);
        margin: 9px 0 16px;
        line-height: 1.65;
    }
    .sf-team {
        padding: 14px 16px;
        margin: 5px 0;
        border: 1px solid var(--sf-border);
        border-radius: 14px;
        background: var(--secondary-background-color);
        font-weight: 600;
        color: var(--text-color);
    }

    /* Indicadores e cartões */
    [data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid var(--sf-border);
        padding: 18px 20px;
        border-radius: 18px;
        box-shadow: 0 5px 18px rgba(20, 50, 40, .035);
    }
    [data-testid="stMetricLabel"] { font-weight: 600; }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: var(--text-color) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--sf-border) !important;
        border-radius: 18px !important;
        background: var(--secondary-background-color);
    }

    /* Campos, botões e componentes interativos */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border-radius: 12px;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--sf-green) !important;
        box-shadow: 0 0 0 1px var(--sf-green) !important;
    }
    div[data-testid="stButton"] button,
    div[data-testid="stLinkButton"] a,
    [data-testid="stFormSubmitButton"] button {
        border-radius: 12px;
        font-weight: 700;
        min-height: 43px;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    div[data-testid="stButton"] button:hover,
    div[data-testid="stLinkButton"] a:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 14px rgba(13, 91, 76, .12);
    }
    [data-testid="stExpander"] {
        border: 1px solid var(--sf-border);
        border-radius: 14px;
        overflow: hidden;
    }
    [data-testid="stCaptionContainer"] { opacity: .82; }

    /* Rodapé */
    .sf-footer {
        text-align: center;
        padding: 23px 8px 5px;
        margin-top: 28px;
        border-top: 1px solid var(--sf-border);
        color: var(--text-color);
        opacity: .72;
        font-size: .86rem;
        line-height: 1.7;
    }

    /* Adaptação para celulares */
    @media (max-width: 700px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: .8rem;
        }
        .sf-hero {
            border-radius: 21px;
            padding: 25px 21px;
        }
        .sf-hero p { font-size: .94rem; }
        .sf-brand-row { gap: 11px; }
        .sf-brand-mark {
            width: 50px;
            height: 50px;
            flex-basis: 50px;
            border-radius: 15px;
        }
        .sf-brand-subtitle { font-size: .59rem; letter-spacing: .09em; }
        div[data-testid="stButton"] button {
            min-height: 64px;
            padding: 9px 7px;
            font-size: .82rem;
        }
        [data-testid="stMetric"] {
            padding: 14px;
            border-radius: 15px;
        }
        .sf-feature { min-height: 0; padding: 18px; }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *:before, *:after {
            transition-duration: .01ms !important;
            animation-duration: .01ms !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def normalizar_texto(valor):
    texto = str(valor or "").casefold().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9 ]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def obter_categoria(unidade):
    categoria = normalizar_texto(unidade.get("categoria", unidade.get("tipo", "")))
    if "hospital" in categoria:
        return "Hospital"
    if "upa" in categoria:
        return "UPA"
    if "ubs" in categoria or "usf" in categoria:
        return "UBS"
    return categoria.title() if categoria else "Não informada"


def obter_coordenadas(unidade):
    """Aceita tanto latitude/longitude na raiz quanto o objeto coordenadas antigo."""
    coordenadas = unidade.get("coordenadas", {})
    if not isinstance(coordenadas, dict):
        coordenadas = {}
    lat = unidade.get("latitude", coordenadas.get("latitude", coordenadas.get("lat")))
    lon = unidade.get(
        "longitude",
        coordenadas.get("longitude", coordenadas.get("lon", coordenadas.get("lng"))),
    )
    try:
        if lat is None or lon is None:
            return None
        lat, lon = float(lat), float(lon)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None
        return {"latitude": lat, "longitude": lon}
    except (TypeError, ValueError):
        return None


def link_valido(url):
    url = str(url or "").strip()
    return url if url.startswith(("https://", "http://")) else ""


def link_pesquisa_google_maps(unidade):
    """Gera uma pesquisa pelo nome e endereço, em vez de abrir apenas as coordenadas."""
    nome = str(unidade.get("nome", "")).strip()
    endereco = str(unidade.get("endereco", "")).strip()
    bairro = str(unidade.get("bairro", "")).strip()
    partes = [parte for parte in [nome, endereco, bairro, "Juazeiro - BA"] if parte]
    consulta = ", ".join(dict.fromkeys(partes))
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(consulta)}" if consulta else ""


def link_coordenadas_google_maps(unidade):
    """Abre o ponto geográfico cadastrado, quando houver coordenadas válidas."""
    coordenadas = obter_coordenadas(unidade)
    if not coordenadas:
        return ""
    consulta = f"{coordenadas['latitude']},{coordenadas['longitude']}"
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(consulta)}"


# Leitura e validação básica da base de dados.
arquivo_dados = Path(__file__).with_name("unidades.json")
try:
    with arquivo_dados.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, list):
        raise ValueError("A estrutura principal precisa ser uma lista.")
    unidades = [u for u in dados if isinstance(u, dict) and u.get("nome")]
except FileNotFoundError:
    st.error("Não encontrei o arquivo unidades.json. Ele precisa ficar na mesma pasta do app.py.")
    st.stop()
except (json.JSONDecodeError, ValueError) as erro:
    st.error(f"Não foi possível ler unidades.json: {erro}")
    st.stop()


# Leitura da base de perguntas frequentes.
arquivo_faq = Path(__file__).with_name("faq.json")
try:
    with arquivo_faq.open("r", encoding="utf-8") as arquivo:
        perguntas_frequentes = json.load(arquivo)
    if not isinstance(perguntas_frequentes, list):
        raise ValueError("A estrutura principal precisa ser uma lista.")
    perguntas_frequentes = [
        item for item in perguntas_frequentes
        if isinstance(item, dict) and item.get("pergunta") and item.get("resposta")
    ]
except FileNotFoundError:
    st.error("Não encontrei o arquivo faq.json. Ele precisa ficar na mesma pasta do app.py.")
    st.stop()
except (json.JSONDecodeError, ValueError) as erro:
    st.error(f"Não foi possível ler faq.json: {erro}")
    st.stop()

# O escopo do projeto permanece restrito a Juazeiro (BA).
unidades = [
    u for u in unidades
    if normalizar_texto(u.get("municipio", "juazeiro")) in ("juazeiro", "juazeiro ba", "")
]

st.markdown(
    '<div class="sf-brand-row">'
    '<div class="sf-brand-mark"><svg width="34" height="34" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<path d="M3 12h4l2.1-5.2L13 17l2.2-5H21" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M12 2.8c-2.1-2-5.5-1.8-7.3.3-1.9 2.2-1.5 5.4.4 7.3L12 17l6.9-6.6c1.9-1.9 2.3-5.1.4-7.3-1.8-2.1-5.2-2.3-7.3-.3Z" stroke="white" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" opacity=".72" transform="translate(0 3) scale(1 .82)"/>'
    '</svg></div>'
    '<div><div class="sf-brand-name">Saúde em Foco</div>'
    '<div class="sf-brand-subtitle">Guia digital de serviços de saúde · Juazeiro – BA</div></div></div>'
    '<div class="sf-hero"><div class="sf-kicker">Informação, localização e acesso</div>'
    '<h1>Saúde mais perto de você.</h1>'
    '<p>Informação organizada para aproximar a população dos serviços públicos de saúde.</p></div>',
    unsafe_allow_html=True,
)

paginas_menu = [
    ("Início", "⌂  Início"),
    ("Buscar unidades", "⌕  Buscar unidades"),
    ("Perguntas frequentes", "?  Perguntas frequentes"),
    ("Mobilidade", "↗  Mobilidade"),
    ("Sobre o projeto", "ⓘ  Sobre o projeto"),
    ("Avaliar", "☆  Avaliar"),
]
if "pagina" not in st.session_state or st.session_state.pagina not in [p[0] for p in paginas_menu]:
    st.session_state.pagina = "Início"

st.markdown('<div class="sf-menu-heading">Explore o guia</div>', unsafe_allow_html=True)
menu_linhas = [st.columns(3), st.columns(3)]
for indice, (nome_pagina, rotulo) in enumerate(paginas_menu):
    linha = indice // 3
    coluna = indice % 3
    with menu_linhas[linha][coluna]:
        st.button(
            rotulo,
            key=f"menu_{indice}",
            type="primary" if st.session_state.pagina == nome_pagina else "secondary",
            use_container_width=True,
            on_click=lambda destino=nome_pagina: st.session_state.update(pagina=destino),
        )

pagina = st.session_state.pagina

if pagina == "Início":
    st.markdown('<div class="sf-section-kicker">Bem-vindo(a)</div>', unsafe_allow_html=True)
    st.title("Encontre informações de saúde em Juazeiro.")
    st.write("Pesquise estabelecimentos, consulte dados cadastrados e visualize no mapa os locais que possuem coordenadas disponíveis.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Unidades no guia", len(unidades))
    c2.metric("Categorias", len({obter_categoria(u) for u in unidades}))
    c3.metric("Com coordenadas", sum(obter_coordenadas(u) is not None for u in unidades))

    st.markdown("### O que você pode fazer")
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown('<div class="sf-feature"><div class="sf-icon">🔎</div><h3>Encontrar unidades</h3><p>Pesquise pelo nome, bairro ou endereço e filtre por categoria.</p></div>', unsafe_allow_html=True)
    with f2:
        st.markdown('<div class="sf-feature"><div class="sf-icon">🗺️</div><h3>Consultar localização</h3><p>Veja no mapa os estabelecimentos com coordenadas cadastradas.</p></div>', unsafe_allow_html=True)
    with f3:
        st.markdown('<div class="sf-feature"><div class="sf-icon">🚌</div><h3>Mobilidade</h3><p>Acesse a consulta externa de linhas e itinerários de ônibus.</p></div>', unsafe_allow_html=True)
    st.info("A base reúne uma seleção de estabelecimentos, não necessariamente toda a rede municipal. Use **Buscar unidades** para consultar os registros disponíveis.")

elif pagina == "Buscar unidades":
    st.title("🔎 Buscar unidades de saúde")
    st.write("Encontre estabelecimentos pelo nome, bairro ou endereço.")
    col_busca, col_categoria = st.columns([2, 1])
    with col_busca:
        pesquisa = st.text_input("Pesquisar", placeholder="Ex.: Angari, Centro, UPA...", key="pesquisa_unidade")
    with col_categoria:
        filtro_categoria = st.selectbox("Categoria", ["Todas", "UBS", "UPA", "Hospital"], key="filtro_categoria")

    termo = normalizar_texto(pesquisa)
    filtradas = []
    for unidade in unidades:
        campos = " ".join(str(unidade.get(campo, "")) for campo in ("nome", "bairro", "endereco"))
        corresponde_texto = not termo or termo in normalizar_texto(campos)
        corresponde_categoria = filtro_categoria == "Todas" or obter_categoria(unidade) == filtro_categoria
        if corresponde_texto and corresponde_categoria:
            filtradas.append(unidade)

    st.caption(f"{len(filtradas)} estabelecimento(s) encontrado(s).")

    marcadores, sem_coordenadas = [], []
    for unidade in filtradas:
        coords = obter_coordenadas(unidade)
        nome = str(unidade.get("nome", "Unidade sem nome"))
        if not coords:
            sem_coordenadas.append(nome)
            continue
        confirmada = unidade.get("localizacao_confirmada") is True
        categoria = obter_categoria(unidade)
        popup = (
            f"<strong>{html.escape(nome)}</strong><br>"
            f"{html.escape(categoria)} · {html.escape(str(unidade.get('bairro', 'Bairro não informado')))}<br>"
            f"{'Localização validada' if confirmada else 'Coordenada cadastrada, ainda não validada'}"
        )
        marcadores.append({
            "latitude": coords["latitude"], "longitude": coords["longitude"],
            "popup": popup, "categoria": categoria, "confirmada": confirmada,
        })

    st.markdown("### 🗺️ Mapa dos estabelecimentos")
    if marcadores:
        dados_mapa = json.dumps(marcadores, ensure_ascii=False).replace("</", "<\\/")
        html_mapa = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"><style>
        html,body{margin:0;padding:0;background:transparent}#mapa{height:430px;width:100%;border-radius:18px;z-index:1}
        .legenda{font:13px Arial,sans-serif;padding:9px 12px;background:white;color:#26352f;border-radius:10px;box-shadow:0 1px 6px #0002;line-height:1.7}
        .ponto{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px}
        @media(max-width:600px){#mapa{height:350px}}
        </style></head><body><div id="mapa"></div>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script>
        const dados=__DADOS__;
        const mapa=L.map('mapa').setView([-9.43,-40.50],13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; OpenStreetMap contributors',maxZoom:19}).addTo(mapa);
        const cores={'UBS':'#16806b','UPA':'#df922e','Hospital':'#cf514d'}; const pontos=[];
        dados.forEach(u=>{const p=[u.latitude,u.longitude], cor=cores[u.categoria]||'#16806b';
          L.circleMarker(p,{radius:9,color:cor,fillColor:cor,fillOpacity:u.confirmada?.9:.35,weight:u.confirmada?2:3,dashArray:u.confirmada?null:'4 4'})
          .addTo(mapa).bindPopup(u.popup);pontos.push(p);});
        if(pontos.length>1)mapa.fitBounds(pontos,{padding:[28,28]});else if(pontos.length===1)mapa.setView(pontos[0],15);
        const legenda=L.control({position:'bottomright'});legenda.onAdd=function(){const d=L.DomUtil.create('div','legenda');d.innerHTML=
          '<b>Unidades</b><br><span class="ponto" style="background:#16806b"></span>UBS<br><span class="ponto" style="background:#df922e"></span>UPA<br><span class="ponto" style="background:#cf514d"></span>Hospital<br>Contorno tracejado: localização provisória';return d;};legenda.addTo(mapa);
        </script></body></html>""".replace("__DADOS__", dados_mapa)
        components.html(html_mapa, height=445, scrolling=False)
        st.caption("Marcadores com contorno tracejado representam localizações provisórias, ainda não confirmadas pela equipe.")
    else:
        st.info("Nenhuma das unidades encontradas possui coordenadas cadastradas para exibição no mapa.")

    if sem_coordenadas:
        with st.expander(f"Unidades sem coordenadas ({len(sem_coordenadas)})"):
            st.write(" · ".join(sem_coordenadas))

    st.markdown("### Resultados")
    if not filtradas:
        st.warning("Nenhuma unidade encontrada. Tente outro termo ou categoria.")

    for unidade in filtradas:
        nome = str(unidade.get("nome", "Nome não informado"))
        categoria = obter_categoria(unidade)
        bairro = unidade.get("bairro") or "Bairro não informado"
        endereco = unidade.get("endereco") or "Endereço não informado"
        contato = unidade.get("contato") or "Contato não informado"
        horario = unidade.get("horario") or "Horário não informado"
        servicos = unidade.get("servicos", [])

        with st.container(border=True):
            titulo_col, tag_col = st.columns([4, 1])
            with titulo_col:
                st.subheader(nome)
                st.caption(f"📍 {bairro}")
            with tag_col:
                st.markdown(f"**{categoria}**")

            # Resumo rápido: informações essenciais visíveis sem abrir os detalhes.
            resumo = st.columns(3)
            with resumo[0]:
                st.caption("📍 Localização")
                st.write(bairro)
            with resumo[1]:
                st.caption("🕒 Atendimento")
                st.write("Consulte os horários" if horario != "Horário não informado" else "Não informado")
            with resumo[2]:
                st.caption("🩺 Serviços")
                st.write(f"{len(servicos)} {'informação' if len(servicos) == 1 else 'informações'}" if isinstance(servicos, list) and servicos else "Consulte os detalhes")

            with st.expander("📍 Localização e contato", expanded=False):
                st.markdown(f"**Endereço**  \n{endereco}")
                st.markdown(f"**Bairro**  \n{bairro}")
                st.markdown(f"**Contato**  \n{contato}")

            with st.expander("🕒 Horários e cadastro", expanded=False):
                st.markdown(f"**Horário informado**  \n{horario}")
                cadastro_col1, cadastro_col2 = st.columns(2)
                with cadastro_col1:
                    if unidade.get("cnes"):
                        st.markdown(f"**CNES**  \n{unidade['cnes']}")
                    else:
                        st.caption("CNES não informado.")
                with cadastro_col2:
                    if unidade.get("esfera_gestao"):
                        st.markdown(f"**Esfera de gestão**  \n{unidade['esfera_gestao']}")
                    else:
                        st.caption("Esfera de gestão não informada.")

            with st.expander("🩺 Serviços disponíveis", expanded=False):
                if isinstance(servicos, list) and servicos:
                    serv_col1, serv_col2 = st.columns(2)
                    for i, servico in enumerate(servicos):
                        alvo = serv_col1 if i % 2 == 0 else serv_col2
                        with alvo:
                            if isinstance(servico, dict):
                                rotulo = servico.get("categoria", "Serviço")
                                descricao = servico.get("descricao", "")
                                icone = servico.get("icone", "🩺")
                                st.markdown(f"**{icone} {rotulo}**")
                                if descricao:
                                    st.caption(descricao)
                            else:
                                st.markdown(f"• 🩺 {servico}")
                else:
                    st.info("Serviços específicos ainda não cadastrados. Confirme a oferta diretamente com o estabelecimento.")

            with st.expander("🔗 Fontes e localização no mapa", expanded=False):
                link_pesquisa = link_pesquisa_google_maps(unidade)
                link_coordenadas = link_coordenadas_google_maps(unidade)
                link_fonte = link_valido(unidade.get("fonte", ""))
                botoes = st.columns(3)
                with botoes[0]:
                    if link_pesquisa:
                        st.link_button("🔎 Encontrar unidade", link_pesquisa, use_container_width=True)
                    else:
                        st.caption("Pesquisa não disponível.")
                with botoes[1]:
                    if link_coordenadas:
                        st.link_button("📍 Ver coordenadas", link_coordenadas, use_container_width=True)
                    else:
                        st.caption("Coordenadas não cadastradas.")
                with botoes[2]:
                    if link_fonte:
                        st.link_button("Consultar fonte", link_fonte, use_container_width=True)
                    else:
                        st.caption("Fonte principal não cadastrada.")

                fontes_adicionais = unidade.get("fontes_adicionais", [])
                fontes_validas = []
                if isinstance(fontes_adicionais, list):
                    for fonte in fontes_adicionais:
                        url = link_valido(fonte.get("url")) if isinstance(fonte, dict) else link_valido(fonte)
                        if url:
                            rotulo = fonte.get("nome", "Fonte complementar") if isinstance(fonte, dict) else "Fonte complementar"
                            fontes_validas.append((rotulo, url))
                if fontes_validas:
                    st.markdown("**Fontes complementares**")
                    for rotulo, url in fontes_validas:
                        st.markdown(f"- [{rotulo}]({url})")


elif pagina == "Perguntas frequentes":
    st.title("❓ Perguntas frequentes")
    st.write(
        "Pesquise por uma palavra-chave ou escolha uma das perguntas sugeridas "
        "para entender como utilizar o Saúde em Foco."
    )

    termo_faq = st.text_input(
        "O que você deseja saber?",
        placeholder="Ex.: UBS, vacinação, endereço, ônibus, agendamento...",
        key="pesquisa_faq",
    )
    termo_normalizado = normalizar_texto(termo_faq)

    if termo_normalizado:
        palavras_busca = termo_normalizado.split()
        resultados_faq = []
        for item in perguntas_frequentes:
            texto_item = normalizar_texto(" ".join([
                str(item.get("pergunta", "")),
                str(item.get("resposta", "")),
                " ".join(item.get("palavras_chave", []))
                    if isinstance(item.get("palavras_chave", []), list)
                    else str(item.get("palavras_chave", "")),
                str(item.get("categoria", "")),
            ]))
            if all(palavra in texto_item for palavra in palavras_busca):
                resultados_faq.append(item)
    else:
        resultados_faq = perguntas_frequentes

    st.caption(f"{len(resultados_faq)} pergunta(s) encontrada(s).")

    if not resultados_faq:
        st.info(
            "Não encontramos uma pergunta com esses termos. "
            "Tente palavras mais simples, como “UBS”, “mapa” ou “horário”."
        )
    else:
        categorias_faq = []
        for item in resultados_faq:
            categoria = item.get("categoria", "Outras dúvidas")
            if categoria not in categorias_faq:
                categorias_faq.append(categoria)

        for categoria in categorias_faq:
            st.markdown(f"### {categoria}")
            itens_categoria = [
                item for item in resultados_faq
                if item.get("categoria", "Outras dúvidas") == categoria
            ]
            for item in itens_categoria:
                with st.expander(item["pergunta"]):
                    st.write(item["resposta"])
                    if item.get("observacao"):
                        st.caption(item["observacao"])

    st.markdown("---")
    st.caption(
        "As respostas têm caráter informativo. Para confirmar horários, serviços "
        "e condições de atendimento, consulte diretamente o estabelecimento ou "
        "os canais oficiais de saúde."
    )

elif pagina == "Mobilidade":
    st.title("🚌 Mobilidade e transporte público")
    st.write("Consulte linhas, itinerários e pontos de parada do transporte coletivo de Juazeiro.")
    url_cittamobi = "https://linhas-preview.cittamobi.com.br/linhas/estado/bahia/juazeiro"
    st.markdown('<div class="sf-note"><strong>Consulta de itinerários</strong><br>As linhas e os horários podem sofrer alterações. Por isso, a consulta atualizada deve ser feita diretamente na plataforma de transporte.</div>', unsafe_allow_html=True)
    st.link_button("Abrir linhas e itinerários no Cittamobi", url_cittamobi, use_container_width=True)
    st.markdown("### Linhas identificadas na pesquisa")
    linhas = [
        ("102", "João Paulo II / Piranga"),
        ("106", "Piranga / Centro"),
        ("200", "Dom José Rodrigues / Piranga"),
        ("202", "Humberto Martins"),
        ("203", "Kidé"),
        ("204", "Itaberaba / Circular"),
        ("207", "Rua São Francisco / Humberto Martins / Piranga"),
    ]
    colunas = st.columns(2)
    for i, (codigo, nome_linha) in enumerate(linhas):
        with colunas[i % 2]:
            with st.container(border=True):
                st.markdown(f"**Linha {codigo}**")
                st.write(nome_linha)
    st.caption("Relação inicial, não necessariamente completa. Confira o itinerário atualizado na plataforma antes de viajar.")
    st.markdown("### Integração com as unidades de saúde")
    st.write("Uma linha só será associada a uma unidade quando houver confirmação de pontos de parada próximos ao endereço. O guia não indica, neste momento, linhas específicas para cada estabelecimento para evitar informações incorretas.")

elif pagina == "Sobre o projeto":
    st.title("ℹ️ Sobre o Saúde em Foco")
    st.markdown('<div class="sf-note"><strong>Nosso propósito</strong><br>O Saúde em Foco é um guia digital acadêmico que reúne informações sobre estabelecimentos públicos de saúde de Juazeiro – Bahia, facilitando a consulta de endereços, contatos, horários, serviços cadastrados e localização.</div>', unsafe_allow_html=True)
    st.markdown("### Objetivo")
    st.write("Facilitar o acesso a informações organizadas sobre unidades públicas de saúde do município, contribuindo para que a população encontre e localize esses serviços.")
    st.markdown("### Como funciona")
    st.write("A aplicação utiliza uma base de dados em JSON, permite pesquisar estabelecimentos pelo nome, bairro ou endereço, filtrar por categoria e visualizar no mapa os registros com coordenadas cadastradas.")
    st.markdown("### Tecnologias e ferramentas")
    st.write("O projeto combina ferramentas de desenvolvimento web, organização de dados, mapas digitais e registro de avaliações.")

    grupos_tecnologias = [
        ("Desenvolvimento da aplicação", [
            ("Python", "Linguagem de programação utilizada na lógica e no funcionamento do sistema."),
            ("Streamlit", "Framework utilizado para construir e disponibilizar a aplicação web."),
        ]),
        ("Interface e organização de dados", [
            ("HTML, CSS e JavaScript", "Tecnologias utilizadas na estrutura, apresentação visual e interações de componentes da interface e do mapa."),
            ("JSON", "Formato de arquivo estruturado utilizado para organizar os dados das unidades e as perguntas frequentes."),
        ]),
        ("Mapas e integração", [
            ("Leaflet + OpenStreetMap", "Biblioteca de mapas interativos e base cartográfica utilizada na visualização geográfica."),
            ("Google Apps Script", "Serviço utilizado para intermediar o envio das avaliações preenchidas na aplicação."),
            ("Google Sheets", "Planilha utilizada para receber e organizar as respostas da avaliação, conforme a configuração da integração."),
        ]),
    ]

    for titulo_grupo, tecnologias in grupos_tecnologias:
        st.markdown(f"#### {titulo_grupo}")
        tech_cols = st.columns(3)
        for i, (nome, detalhe) in enumerate(tecnologias):
            with tech_cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**{nome}**")
                    st.caption(detalhe)

    st.caption("Observação: o registro das avaliações depende da configuração do endereço e da chave de acesso da integração nos segredos da aplicação.")
    st.markdown("### Equipe desenvolvedora")
    equipe = [
        "Ana Julia Alves de Lima Silva", "Emilly Kauany M. Silva",
        "Marianna Haika da Silva Oliveira", "Rebeca Fonseca da Silva",
        "Sophia Santos Araujo", "Valentina Santana Queiroz",
    ]
    equipe_cols = st.columns(2)
    for i, nome in enumerate(equipe):
        with equipe_cols[i % 2]:
            st.markdown(f'<div class="sf-team">{html.escape(nome)}</div>', unsafe_allow_html=True)
    st.markdown("### Créditos acadêmicos")
    st.write("**Universidade:** Universidade do Estado da Bahia – UNEB  \n**Curso:** Jornalismo em Multimeios  \n**Professor orientador:** Cecílio Bastos  \n**Local:** Juazeiro – Bahia  \n**Ano:** 2026")
    st.info("A base representa uma seleção de estabelecimentos e não deve ser interpretada como a relação completa da rede municipal. Dados cadastrais, horários e serviços podem mudar; confirme informações diretamente com a unidade.")
    st.caption("Mapa: © OpenStreetMap contributors.")

else:  # Avaliar
    st.title("⭐ Avalie sua experiência")
    st.write("Sua opinião ajuda a equipe a avaliar a facilidade de uso do guia.")
    st.markdown(
        '<div class="sf-note"><strong>Queremos ouvir você!</strong><br>'
        'Responda às perguntas abaixo. Não solicitamos nome, e-mail ou informações de saúde.</div>',
        unsafe_allow_html=True,
    )

    with st.form("formulario_avaliacao", clear_on_submit=True):
        avaliacao = st.radio(
            "1. Como você avalia sua experiência geral?",
            ["Muito boa", "Boa", "Regular", "Ruim"],
            index=None,
        )
        utilidade = st.radio(
            "2. As informações encontradas foram úteis?",
            ["Sim", "Parcialmente", "Não"],
            index=None,
        )
        localizacao = st.radio(
            "3. Você conseguiu localizar uma unidade de saúde?",
            ["Sim", "Não", "Não tentei localizar"],
            index=None,
        )
        navegacao = st.radio(
            "4. Como foi navegar pelo Saúde em Foco?",
            ["Muito fácil", "Fácil", "Regular", "Difícil"],
            index=None,
        )
        sugestao = st.text_area(
            "5. Deixe uma sugestão ou comentário (opcional)",
            max_chars=1000,
            placeholder="Conte o que funcionou bem ou o que podemos melhorar...",
        )
        recomendacao = st.radio(
            "6. Você recomendaria este guia a outra pessoa?",
            ["Sim", "Não", "Talvez"],
            index=None,
        )
        enviar = st.form_submit_button("Enviar avaliação", use_container_width=True)

    if enviar:
        campos_obrigatorios = [avaliacao, utilidade, localizacao, navegacao, recomendacao]
        if any(campo is None for campo in campos_obrigatorios):
            st.warning("Responda às perguntas obrigatórias antes de enviar. A sugestão é opcional.")
        else:
            try:
                configuracao = st.secrets["feedback"]
                url_script = str(configuracao["url"]).strip()
                token = str(configuracao["token"]).strip()

                if not url_script.startswith("https://script.google.com/"):
                    raise ValueError("A URL de integração não está configurada corretamente.")
                if not token:
                    raise ValueError("O token de segurança não foi configurado.")

                payload = {
                    "token": token,
                    "avaliacao": avaliacao,
                    "utilidade": utilidade,
                    "localizacao": localizacao,
                    "navegacao": navegacao,
                    "sugestao": sugestao.strip(),
                    "recomendacao": recomendacao,
                }
                requisicao = urllib.request.Request(
                    url_script,
                    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(requisicao, timeout=25) as resposta_http:
                    retorno = json.loads(resposta_http.read().decode("utf-8"))

                if retorno.get("sucesso") is True:
                    st.success("Avaliação enviada com sucesso! Obrigado por contribuir com o Saúde em Foco. 💚")
                else:
                    st.error(
                        "Não foi possível registrar a avaliação. "
                        + str(retorno.get("mensagem", "Verifique a configuração da integração."))
                    )
            except KeyError:
                st.error(
                    "A integração ainda não foi configurada nos Secrets do Streamlit Cloud. "
                    "Adicione as configurações indicadas pela equipe do projeto."
                )
            except urllib.error.HTTPError as erro:
                st.error(f"O serviço de avaliação retornou um erro HTTP ({erro.code}). Tente novamente mais tarde.")
            except urllib.error.URLError:
                st.error("Não foi possível conectar à planilha. Verifique a internet e tente novamente.")
            except (TimeoutError, json.JSONDecodeError, ValueError) as erro:
                st.error(f"Não foi possível concluir o envio: {erro}")
            except Exception:
                st.error("Ocorreu um erro inesperado ao enviar sua avaliação. Tente novamente.")

    st.caption(
        "As respostas serão armazenadas em uma planilha para avaliação acadêmica do projeto. "
        "Não inclua dados pessoais ou informações sensíveis no campo de sugestão."
    )

st.markdown('<div class="sf-footer"><strong>🏥 Saúde em Foco</strong><br>Guia Digital de Serviços de Saúde · Juazeiro – Bahia · 2026</div>', unsafe_allow_html=True)
