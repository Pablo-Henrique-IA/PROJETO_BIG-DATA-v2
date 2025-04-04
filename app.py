import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
import requests
import json

# Carregar os dados



@st.cache_data
def load_data1():
    url = "http://127.0.0.1:8000/mongo"  # Substitua pela URL real da API

    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança erro se a resposta for ruim (4xx ou 5xx)

        data = response.json()  # Converte resposta JSON para dicionário

        df = pd.DataFrame(data["dados"])

# Converter colunas numéricas
        df["IDH"] = df["IDH"].str.replace(",", ".").str.extract(r'([\d\.]+)').astype(float)
        df["Population"] = df["Population"].str.replace(".", "").astype(int)

        df = df[[
            "Country", "IDH", "Population",
            "Food service estimate (kg/capita/year)",
            "Food service estimate (tonnes/year)",
            "Region"
        ]]

        df.dropna(inplace=True)  # Remove linhas com valores nulos
        return df   

    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar os dados: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro








#@st.cache_data
#def load_data():
#    df = pd.read_excel("Desperdício x IDH e População (1).xlsx")
#    df["IDH"] = df["IDH"].str.replace(",", ".").str.extract(r'([\d\.]+)').astype(float)
#    df = df[[
#        "Country", "IDH", "Population", 
#        "Food service estimate (kg/capita/year)", 
#       "Food service estimate (tonnes/year)", 
#        "Region"
#    ]]
#    df.dropna(inplace=True)
#    return df





@st.cache_data
def load_coordinates():
    coords_df = pd.read_csv("country_coordinates.csv")
    return coords_df

df = load_data1()
coords_df = load_coordinates()

# Juntar coordenadas
df_map = pd.merge(df, coords_df, on="Country", how="left")
df_map.dropna(subset=["Latitude", "Longitude"], inplace=True)
df_map["radius"] = df_map["Food service estimate (kg/capita/year)"] * 1000

st.title("Análise: Desperdício de Comida x IDH e População")
st.write("Este painel mostra como o **IDH** e a **população** de diferentes países se relacionam com o **desperdício de comida** no setor de food service.")

# Filtro por país
selected_country = st.selectbox("Selecione um país para destacar:", options=sorted(df["Country"].unique()))

# Gráfico de dispersão com país destacado
st.subheader("Desperdício Per Capita vs IDH")
fig, ax = plt.subplots()
scatter = ax.scatter(df["IDH"], df["Food service estimate (tonnes/year)"], c=df["Population"], cmap="plasma", alpha=0.7)
highlight = df[df["Country"] == selected_country]
ax.scatter(highlight["IDH"], highlight["Food service estimate (tonnes/year)"], color='red', s=100, label=selected_country)
ax.set_xlabel("IDH")
ax.set_ylabel("Desperdício (tonelada/ano)")
ax.set_title("Relação entre IDH e Desperdício de Comida")
ax.legend()
cbar = fig.colorbar(scatter, ax=ax)
cbar.set_label("População")
st.pyplot(fig)

# Informações do país selecionado
st.subheader(f"Detalhes do país selecionado: {selected_country}")
country_data = df[df["Country"] == selected_country].iloc[0]
st.markdown(
    f"""
- **IDH:** {country_data['IDH']}
- **População:** {int(country_data['Population']):,}
- **Desperdício total (toneladas/ano):** {int(country_data['Food service estimate (tonnes/year)']):,}
""")

# Mapa interativo
st.subheader("Mapa Interativo: Desperdício per capita por país")
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_map,
    get_position='[Longitude, Latitude]',
    get_fill_color='[255, 140, 0, 140]',
    get_radius="radius",
    pickable=True,
)

view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1)
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{Country}\nDesperdício : {Food service estimate (tonnes/year)} toneladas/ano"},
)
st.pydeck_chart(r)

# Correlação
st.subheader("Correlação entre Variáveis")
corr_df = df[["IDH", "Population", "Food service estimate (tonnes/year)"]].corr()
st.dataframe(corr_df)

# Interpretação automática
def interpretar_correlacao(valor):
    if abs(valor) < 0.1:
        return "nenhuma correlação significativa"
    elif abs(valor) < 0.3:
        return "correlação fraca"
    elif abs(valor) < 0.7:
        return "correlação moderada"
    else:
        return "correlação forte"


st.subheader("Interpretação automática da correlação:")
ja_exibido = set()
for col in corr_df.columns:
    for row in corr_df.index:
        if row != col and (row, col) not in ja_exibido and (col, row) not in ja_exibido:
            valor = corr_df.loc[row, col]
            st.markdown(f"- A correlação entre **{row}** e **{col}** é **{valor:.2f}**, o que indica **{interpretar_correlacao(valor)}**.")
            ja_exibido.add((row, col))

