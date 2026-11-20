import html
import json
import re
import unicodedata
import urllib.error
import urllib.request
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
    .stApp { font-family: 'DM Sans', sans-serif; }
    [data-testid="stAppViewContainer"] { background: var(--background-color); }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1220px; padding-top: 1.35rem; padding-bottom: 2rem; }

    h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] {
        color: var(--text-color);
    }
    h1, h2, h3 { letter-spacing: -0.035em; }
    h1 { font-weight: 800; }

    .sf-hero {
        position: relative; overflow: hidden;
        padding: clamp(24px, 4vw, 42px);
        border-radius: 26px; margin: 4px 0 22px;
        color: #ffffff;
        background: linear-gradient(118deg, #0d5146 0%, #147b66 58%, #27977b 100%);
        box-shadow: 0 14px 35px rgba(8, 65, 54, .18);
    }
    .sf-hero:after {
        content: ''; position: absolute; width: 230px; height: 230px;
        border: 1px solid rgba(255,255,255,.15); border-radius: 50%;
        right: -55px; top: -105px; box-shadow: 0 0 0 28px rgba(255,255,255,.035), 0 0 0 58px rgba(255,255,255,.025);
    }
    .sf-kicker { color: #c9eee2 !important; text-transform: uppercase; letter-spacing: .14em; font-size: .72rem; font-weight: 800; }
    .sf-hero h1 { color: #ffffff !important; font-size: clamp(2rem, 4vw, 3rem); margin: 7px 0 8px; line-height: 1.08; }
    .sf-hero p { color: #e7f7f1 !important; max-width: 720px; margin: 0; font-size: 1.02rem; }

    .sf-section-kicker { color: var(--sf-green) !important; font-size: .76rem; text-transform: uppercase; letter-spacing: .12em; font-weight: 800; margin-bottom: 3px; }
    .sf-feature {
        height: 100%; min-height: 150px; padding: 20px;
        border: 1px solid var(--sf-border); border-radius: var(--sf-radius);
        background: var(--secondary-background-color);
    }
    .sf-feature .sf-icon { font-size: 1.45rem; margin-bottom: 9px; }
    .sf-feature h3 { font-size: 1.04rem; margin: 0 0 7px; color: var(--text-color) !important; }
    .sf-feature p { color: var(--text-color) !important; opacity: .82; font-size: .91rem; margin: 0; line-height: 1.5; }
    .sf-note {
        padding: 16px 18px; border-radius: 15px;
        background: var(--secondary-background-color);
        border: 1px solid var(--sf-border); margin: 8px 0 14px;
    }
    .sf-team {
        padding: 13px 15px; margin: 5px 0;
        border: 1px solid var(--sf-border); border-radius: 13px;
        background: var(--secondary-background-color); font-weight: 600;
        color: var(--text-color);
    }
    [data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid var(--sf-border); padding: 16px 18px;
        border-radius: 17px;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] { color: var(--text-color) !important; }
    [data-testid="stRadio"] > div {
        gap: 7px; padding: 7px; border: 1px solid var(--sf-border);
        border-radius: 15px; background: var(--secondary-background-color);
    }
    [data-testid="stRadio"] label { border-radius: 10px; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--sf-border) !important; border-radius: 17px !important;
    }
    div[data-testid="stButton"] button, div[data-testid="stLinkButton"] a {
        border-radius: 12px; font-weight: 700; min-height: 42px;
    }
    [data-testid="stCaptionContainer"] { opacity: .82; }
    .sf-footer { text-align: center; padding: 18px 8px 4px; color: var(--text-color); opacity: .72; font-size: .86rem; }

    @media (max-width: 700px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        .sf-hero { border-radius: 20px; }
        [data-testid="stRadio"] > div { gap: 2px; }
        [data-testid="stRadio"] label { padding-left: 7px; padding-right: 7px; }
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
    '<div class="sf-hero"><div class="sf-kicker">Guia digital de serviços de saúde · Juazeiro – BA</div>'
    '<h1>🏥 Saúde em Foco</h1><p>Informação organizada para aproximar a população dos serviços públicos de saúde.</p></div>',
    unsafe_allow_html=True,
)

paginas = ["Início", "Buscar unidades", "Perguntas frequentes", "Mobilidade", "Sobre o projeto", "Avaliar"]
if "pagina" not in st.session_state:
    st.session_state.pagina = "Início"
pagina = st.radio(
    "Navegação principal", paginas, horizontal=True,
    label_visibility="collapsed", key="menu_superior",
)

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
          '<b>Unidades</b><br><span class="ponto" style="background:#16806b"></span>UBS<br><span class="ponto" style="background:#df922e"></span>UPA<br><span class="ponto" style="background:#cf514d"></span>Hospital<br>Contorno tracejado: coordenada não validada';return d;};legenda.addTo(mapa);
        </script></body></html>""".replace("__DADOS__", dados_mapa)
        components.html(html_mapa, height=445, scrolling=False)
        st.caption("Marcadores com contorno tracejado representam coordenadas cadastradas que ainda não foram validadas.")
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
        with st.container(border=True):
            titulo_col, tag_col = st.columns([4, 1])
            with titulo_col:
                st.subheader(nome)
            with tag_col:
                st.markdown(f"**{categoria}**")

            info1, info2 = st.columns(2)
            with info1:
                st.markdown(f"**Bairro**  \n{unidade.get('bairro', 'Não informado')}")
                st.markdown(f"**Endereço**  \n{unidade.get('endereco', 'Não informado')}")
                st.markdown(f"**Contato**  \n{unidade.get('contato', 'Não informado')}")
            with info2:
                st.markdown(f"**Horário informado**  \n{unidade.get('horario', 'Não informado')}")
                if unidade.get("cnes"):
                    st.markdown(f"**CNES**  \n{unidade['cnes']}")
                if unidade.get("esfera_gestao"):
                    st.markdown(f"**Gestão**  \n{unidade['esfera_gestao']}")

            servicos = unidade.get("servicos", [])
            st.markdown("**🩺 Serviços e informações cadastradas**")
            if servicos:
                serv_col1, serv_col2 = st.columns(2)
                for i, servico in enumerate(servicos):
                    alvo = serv_col1 if i % 2 == 0 else serv_col2
                    with alvo:
                        if isinstance(servico, dict):
                            rotulo = servico.get("categoria", "Serviço")
                            descricao = servico.get("descricao", "")
                            st.markdown(f"• **{servico.get('icone', '🩺')} {rotulo}**")
                            if descricao:
                                st.caption(descricao)
                        else:
                            st.markdown(f"• 🩺 {servico}")
            else:
                st.caption("Serviços específicos ainda não cadastrados. Confirme a oferta diretamente com o estabelecimento.")

            transporte = unidade.get("transporte", {})
            if isinstance(transporte, dict) and transporte:
                st.markdown("**🚌 Transporte público**")
                linhas = transporte.get("linhas", [])
                st.write(", ".join(map(str, linhas)) if linhas else "Linhas ainda não confirmadas.")
                if transporte.get("observacao"):
                    st.caption(transporte["observacao"])
                link_transporte = link_valido(transporte.get("link"))
                if link_transporte:
                    st.link_button("Consultar transporte", link_transporte)

            links = st.columns(2)
            link_mapa = link_valido(unidade.get("mapa", unidade.get("maps", "")))
            link_fonte = link_valido(unidade.get("fonte", ""))
            with links[0]:
                if link_mapa:
                    st.link_button("📍 Ver no Google Maps", link_mapa, use_container_width=True)
            with links[1]:
                if link_fonte:
                    st.link_button("Consultar fonte", link_fonte, use_container_width=True)
            fontes_adicionais = unidade.get("fontes_adicionais", [])
            if fontes_adicionais:
                with st.expander("Fontes complementares"):
                    for fonte in fontes_adicionais:
                        url = link_valido(fonte.get("url")) if isinstance(fonte, dict) else link_valido(fonte)
                        if url:
                            rotulo = fonte.get("nome", "Fonte complementar") if isinstance(fonte, dict) else "Fonte complementar"
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
    st.markdown("### Tecnologias")
    tech = st.columns(4)
    for coluna, nome, detalhe in zip(tech, ["Python", "Streamlit", "JSON", "Leaflet + OSM"], ["Linguagem", "Aplicação web", "Base de dados", "Mapa interativo"]):
        with coluna:
            with st.container(border=True):
                st.markdown(f"**{nome}**")
                st.caption(detalhe)
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
