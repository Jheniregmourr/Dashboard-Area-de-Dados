import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

#Configurações iniciais da página - Favicon, titulo da página e largura (tela toda nesse caso)
st.set_page_config(
    page_title="Dashboard: Área de Dados",
    page_icon="📊",
    layout="wide"
)

#Carregando os dados que serão utilizados para o Dashboard
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

#Barra lateral
st.sidebar.header("Filtros 🔍")

#Filtros laterais
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

senioridade_disponivel = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Nivel de Experiência", senioridade_disponivel, default=senioridade_disponivel)

contratos_disponivel = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Contrato", contratos_disponivel, default=contratos_disponivel)

tamanhos_disponivel = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Classificação da Empresa", tamanhos_disponivel, default=tamanhos_disponivel)

modalidade_disponivel = sorted(df['remoto'].unique())
modalidade_selecionados = st.sidebar.multiselect("Modalidade de Serviço", modalidade_disponivel, default=modalidade_disponivel)

df_filtrado = df[
    (df['ano'].isin(anos_selecionados))&
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

#Conteúdo principal
st.title("🎲 Dashboard: Área de Dados")
st.markdown(
    "Análise de salários na área de dados, considerando diferentes cargos, localizações, níveis de experiência e outros fatores relevantes.<br>"
    "Informações importantes para compreensão dos dados: O salário informado em USD refere-se a valores anuais, não mensais. Além disso, observe que na notação americana o uso da vírgula e do ponto é diferente do Brasil:<br>"
    "• Em reais (BR): 1.800 → mil e oitocentos reais<br>"
    "• Em dólares (USD): 1,800 → mil e oitocentos dólares", #unsafe_allow_html=True é necessário para o Streamlit interpretar o HTML. (a tg br para quebra de linha)
    unsafe_allow_html=True
)

#Sub-titulo inicial
st.subheader("Métricas gerais: Salários em USD")

if not df_filtrado.empty: #se a variavel df_filtrado não estiver vazia, o seguinte vai ocorrer:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registro = df_filtrado.shape[0]  #Retorna o número de linhas, ou seja, a quantidade de registros
    cargo_frequente = df_filtrado['cargo'].mode()[0] #.mode() retorna o valor que mais aparece na coluna cargo.
#[0] pega o primeiro valor (porque pode haver empate de cargos)

else: #Se o o df_filtrado estiver vazio, ele vai zerar todos os valores para não dar erro.
    salario_maximo, salario_maximo, total_registro, cargo_frequente = 0, 0, 0, " "

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio", f"${salario_medio:,.0f}")
col2.metric("Salário Máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de Registros", f"${total_registro:,.0f}")
col4.metric("Cargo mais Frequente", cargo_frequente)

st.markdown("---")

#Gráficos com Plotly
st.subheader("Gráficos")

#Gráfico de mapa
tema = st.radio("Escolha o tema do mapa:", ["dark", "light"])

if tema=='dark':
    modo = '#0E1117'
        
else:
    modo = '#FFFFFF'

if not df_filtrado.empty:
    df_gm = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
    media_por_paises = df_gm.groupby('residencia_iso3')['usd'].mean().reset_index()
    grafico_paises = px.choropleth(media_por_paises,
    locations='residencia_iso3',
    color='usd',
    color_continuous_scale='reds',
    title='Salário Médio de Cargo por País',
    labels= {'usd': 'Média salarial em USD', 'residencia_iso3': 'País'})
    grafico_paises.update_layout(
        width=1000,
        height=750
    )
#Configurações visuais do gráfico de mapa.
    grafico_paises.update_geos(
        showcountries = True, #Contornos de todos os países, mesmo que não tenham dados
        countrycolor = modo,  #Cor do contorno dos países
        framecolor = modo, #Cor da borda externa do mapa
        bgcolor = modo, #Cor de fundo geral do mapa.
        showcoastlines = True, #Linhas da costa
        coastlinecolor = '#741C18', #Cor das linhas da costa.
        landcolor = modo,  #Cor do interior da terra (continentes).
        showocean = True, #Mostrar o ocenao
        oceancolor = modo #Cor do oceano.
    )

    st.plotly_chart(grafico_paises, use_container_width=True)

else:
    print("Erro")

col_graf1, col_graf2 = st.columns(2) #Cada uma das duas coluna ira conter um gráfico. Assim eles ficam ocupando um espaço equivalente da tela simultaneamente

with col_graf1: #Gráfico de barras: Salario por Cargo
    if not df_filtrado.empty:
        ranking_cargos = df_filtrado.groupby("cargo")["usd"].mean().nlargest(10).sort_values(ascending=True).reset_index() #Primeiramente eu agrupo todos os dados de salario de cada um dos cargos e calculo sua média. Depois de calcular a média, eu seleciono as 10 maiores médias e as organizo da maior para a menor.
        grafico_ranking = px.bar(
            ranking_cargos,
            y='cargo',
            x='usd',
            title="Ranking: 10 maiores salários por profissão",
            labels={'usd': "Salário em USD", 'cargo': ""},
            color_discrete_sequence=['#B9332C']
        )
        st.plotly_chart(grafico_ranking, use_container_width=True) #No caso, permite que o gráfico apareça e utilize o espaço disponivel.
    else:
        print("Erro")
    
#Histograma de Salários por Ano.
with col_graf2:
    if not df_filtrado.empty:
        salario_ano = px.histogram(
            df_filtrado,
            x='usd',
            nbins=40,
            title='Salários Anuais',
            labels={'usd': "Faixa salarial (USD)"},
            color_discrete_sequence=['#B9332C']
        )
        salario_ano.update_layout(bargap=0.2) #Bargap é utilizado para controlar o espaço entre as colunas, sem ele todas ficam grudadas, o que pode difivultar a interpretação do gráfico.
        st.plotly_chart(salario_ano, use_container_width=True)
    else:
        print("Erro")

col_graf3, col_graf4 = st.columns(2) #Mais duas novas colunas para dois novos gráficos

#Gráfico de pizza (É interessante utilizar o gráfico de pizza para no máximo 3 valores distintos)
with col_graf3:
    if not df_filtrado.empty:
        contagem_remoto = df_filtrado['remoto'].value_counts().reset_index()
        contagem_remoto.columns = ['tipo_trabalho', 'quantidade']
        graf_pizz = px.pie(
            contagem_remoto,
            names='tipo_trabalho',
            values='quantidade',
            title='Modalidade de serviço',
            color="tipo_trabalho",
            color_discrete_map={
            'remoto':'#8A2723',
            'presencial':'#B9332C',
            'hibrido': '#D94A44'}
        )
        st.plotly_chart(graf_pizz, use_container_width=True)
    else:
        print("Erro")

#Gráfico de linha: Salário por nível de experiência.
with col_graf4:
    if not df_filtrado.empty:
        salario_senioridade = df_filtrado.groupby('senioridade')['usd'].mean().reset_index() #Agrupo os salários por nivel de experiência e calculo sua média.
        grafico_salario_senioridade = px.line(
            salario_senioridade,
            x='senioridade',
            y='usd',
            title="Salário por Nível de Experiência",
            labels={
                'senioridade': "Nível de Experiência",
                'usd': "Salário USD"
                }
        )
        grafico_salario_senioridade.update_traces(line=dict(color='#B9332C', width=3))#line=dict Permite que eu selecione a cor e a espessura da linha em px.
        st.plotly_chart(grafico_salario_senioridade, use_container_width=True)

    else:
        print("Erro")

#Tabela com os dados
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)