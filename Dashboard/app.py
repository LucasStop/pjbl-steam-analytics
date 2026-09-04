"""Dashboard PJBL — Steam (Data Analytics).

Duas seções: catálogo histórico (games_clean.csv, análise da mesma pergunta
de pesquisa do Notebooks/02_analysis_visualization.ipynb) e dado ao vivo
(SteamSpy + Steam Store API por AppID, o diferencial do projeto: comparar
histórico x tempo real).
"""

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Steam — PJBL Data Analytics", layout="wide")

CAMINHO_LIMPO = "../Dataset/fronkongames/games_clean.csv"

# Jogos populares pré-definidos, pra não obrigar o usuário a saber o AppID de cor.
JOGOS_POPULARES = {
    "Dota 2 (570)": 570,
    "Counter-Strike 2 (730)": 730,
    "Apex Legends (1172470)": 1172470,
    "Destiny 2 (1085660)": 1085660,
    "Grand Theft Auto V (271590)": 271590,
}


@st.cache_data
def carregar_dataset():
    # Só as colunas usadas no dashboard — o CSV completo tem 400MB, carregar
    # tudo seria desperdício de memória e tempo de load.
    colunas = [
        "AppID", "Name", "Release date", "Price", "Peak CCU",
        "Metacritic score", "owners_avg", "Genres",
    ]
    df = pd.read_csv(CAMINHO_LIMPO, usecols=colunas)
    df_genero = df.assign(Genre=df["Genres"].str.split(",")).explode("Genre")
    df_genero["Genre"] = df_genero["Genre"].str.strip()
    return df, df_genero


@st.cache_data(ttl=300)  # 5 min: dado ao vivo muda, mas não a cada segundo
def buscar_steamspy(appid: int):
    url = f"https://steamspy.com/api.php?request=appdetails&appid={appid}"
    resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=300)
def buscar_steam_store(appid: int):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()[str(appid)]


df, df_genero = carregar_dataset()

st.title("Steam — catálogo histórico x dado ao vivo")
st.caption(
    "Pergunta de pesquisa: quais características de um jogo (preço, gênero, "
    "nota de review) estão associadas a maior pico de jogadores simultâneos, "
    "e como o catálogo histórico se compara ao comportamento ao vivo?"
)

aba_historico, aba_live = st.tabs(["Catálogo histórico", "Dado ao vivo"])

# ---------------------------------------------------------------------------
with aba_historico:
    st.subheader("Filtros")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        generos_disponiveis = sorted(
            g for g in df_genero["Genre"].dropna().unique() if g != "Not specified"
        )
        generos_sel = st.multiselect(
            "Gênero", generos_disponiveis, default=["Action", "Indie"]
        )
    with col_f2:
        preco_max_dataset = float(df["Price"].max())
        faixa_preco = st.slider(
            "Faixa de preço (USD)", 0.0, preco_max_dataset, (0.0, 60.0)
        )

    if generos_sel:
        appids_filtrados = df_genero.loc[
            df_genero["Genre"].isin(generos_sel), "AppID"
        ].unique()
        df_f = df[df["AppID"].isin(appids_filtrados)]
    else:
        df_f = df
    df_f = df_f[df_f["Price"].between(*faixa_preco)]

    st.caption(f"{len(df_f):,} jogos após filtro".replace(",", "."))

    col1, col2 = st.columns(2)
    with col1:
        fig_preco = px.histogram(
            df_f, x="Price", nbins=50, title="Distribuição de preço"
        )
        st.plotly_chart(fig_preco, width="stretch")
    with col2:
        fig_meta = px.histogram(
            df_f.dropna(subset=["Metacritic score"]),
            x="Metacritic score",
            nbins=30,
            title="Distribuição de Metacritic score (jogos avaliados)",
        )
        st.plotly_chart(fig_meta, width="stretch")

    # Peak CCU por gênero — só jogos com CCU > 0, senão o boxplot vira uma
    # linha reta em zero (achado do notebook: ~84% do catálogo tem CCU == 0).
    # Só AppID/Genre aqui — df_genero_f já tem "Peak CCU" (herdada de df_genero),
    # então incluir de novo no merge geraria colunas duplicadas ("Peak CCU_x"/"_y").
    df_genero_f = df_genero.loc[
        df_genero["AppID"].isin(df_f["AppID"]) & (df_genero["Genre"] != "Not specified"),
        ["AppID", "Genre"],
    ]
    df_genero_ccu = df_genero_f.merge(
        df_f[["AppID", "Peak CCU"]], on="AppID"
    )
    df_genero_ccu = df_genero_ccu[df_genero_ccu["Peak CCU"] > 0]
    if not df_genero_ccu.empty:
        fig_ccu = px.box(
            df_genero_ccu,
            x="Genre",
            y="Peak CCU",
            log_y=True,
            title="Peak CCU por gênero (jogos com Peak CCU > 0, escala log)",
        )
        st.plotly_chart(fig_ccu, width="stretch")
    else:
        st.info("Nenhum jogo com Peak CCU > 0 no filtro atual.")

# ---------------------------------------------------------------------------
with aba_live:
    st.subheader("Consulta ao vivo por AppID")
    st.caption(
        "SteamSpy e Steam Store API não têm endpoint de listagem completa "
        "(GetAppList foi descontinuado, ver API/README.md) — a consulta é "
        "sempre por AppID específico."
    )

    modo = st.radio("Escolher jogo", ["Lista de populares", "Digitar AppID"], horizontal=True)
    if modo == "Lista de populares":
        escolha = st.selectbox("Jogo", list(JOGOS_POPULARES.keys()))
        appid = JOGOS_POPULARES[escolha]
    else:
        appid = st.number_input("AppID", min_value=1, value=570, step=1)

    if st.button("Buscar dado ao vivo"):
        try:
            spy = buscar_steamspy(int(appid))
            store = buscar_steam_store(int(appid))
        except requests.RequestException as e:
            st.error(f"Falha ao consultar API: {e}")
        else:
            col_live, col_hist = st.columns(2)

            with col_live:
                st.markdown("### Dado ao vivo (SteamSpy + Steam Store)")
                if store.get("success"):
                    game = store["data"]
                    st.write(f"**Nome:** {game.get('name')}")
                    preco = game.get("price_overview", {}).get("final_formatted", "Free / N-A")
                    st.write(f"**Preço atual:** {preco}")
                    st.write(f"**Gêneros:** {', '.join(g['description'] for g in game.get('genres', []))}")
                else:
                    st.warning("Steam Store API não retornou dados pra esse AppID.")
                st.write(f"**Owners (SteamSpy, estimado):** {spy.get('owners', 'N/A')}")
                st.write(f"**Peak CCU (SteamSpy, 24h):** {spy.get('ccu', 'N/A')}")
                st.write(f"**Reviews +/-:** {spy.get('positive', 'N/A')}/{spy.get('negative', 'N/A')}")

            with col_hist:
                st.markdown("### Linha correspondente no dataset histórico")
                linha = df[df["AppID"] == int(appid)]
                if linha.empty:
                    st.info("AppID não encontrado em games_clean.csv.")
                else:
                    linha = linha.iloc[0]
                    st.write(f"**Nome:** {linha['Name']}")
                    st.write(f"**Preço (histórico):** ${linha['Price']:.2f}")
                    st.write(f"**Peak CCU (histórico):** {linha['Peak CCU']:.0f}")
                    st.write(f"**Metacritic score:** {linha['Metacritic score']}")
                    st.write(f"**owners_avg (histórico):** {linha['owners_avg']:.0f}")
                    st.write(f"**Gêneros:** {linha['Genres']}")
