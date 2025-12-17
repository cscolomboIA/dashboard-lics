import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
try:
    page_icon = "logo_lics.jpg" 
    st.set_page_config(page_title="Dashboard LICS", layout="wide", page_icon=page_icon)
except:
    st.set_page_config(page_title="Dashboard LICS", layout="wide")

# --- BARRA LATERAL (APENAS LOGO E INFO) ---
if os.path.exists("logo_lics.jpg"):
    st.sidebar.image("logo_lics.jpg", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.info("**LICS - Laboratório de Inteligência Computacional na Saúde**\n\nCoordenação: Prof. Cristiano da Silveira Colombo")

# --- CABEÇALHO PRINCIPAL ---
col_header1, col_header2 = st.columns([1, 6])
with col_header1:
    if os.path.exists("logo_lics.jpg"):
        st.image("logo_lics.jpg", width=100)
with col_header2:
    st.title("Painel de Controle Estratégico")
    st.markdown("Monitoramento de ações de Pesquisa, Inovação e Formação (Ciclo 2024-2025)")

# --- CARREGAMENTO E TRATAMENTO DE DADOS ---
@st.cache_data
def load_data():
    df = pd.read_csv("dados.csv")
    novos_nomes = [
        'Ano', 'Tipo da atividade', 'Titulo', 'Evento_Periodico', 'Data', 
        'Carga_Horaria', 'Autores', 'Qualis', 'Alunos_Tec_Integrado',  
        'Alunos_Tec_Concomitante', 'Alunos_BSI', 'Status', 'Vinculo'
    ]
    if len(df.columns) == len(novos_nomes):
        df.columns = novos_nomes
    else:
        st.error("Erro na estrutura do CSV.")
        st.stop()
    
    cols_alunos = ['Alunos_Tec_Integrado', 'Alunos_Tec_Concomitante', 'Alunos_BSI']
    for col in cols_alunos:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['Total_Alunos'] = df[cols_alunos].sum(axis=1)

    # --- CATEGORIZAÇÃO (SEM ÍCONES) ---
    def definir_categoria(tipo):
        tipo = str(tipo).lower()
        if any(x in tipo for x in ['inovação', 'startup', 'gênesis', 'centelha', 'software', 'patente', 'grupo', 'incubação']):
            return 'Inovação & Startups'
        elif any(x in tipo for x in ['artigo', 'revista', 'periódico', 'livro', 'publicação']):
            return 'Produção Intelectual'
        elif any(x in tipo for x in ['orientação', 'tcc', 'curso', 'minicurso', 'iniciação', 'pic', 'ensino']):
            return 'Formação & Orientações'
        elif any(x in tipo for x in ['evento', 'apresentação', 'palestra', 'participação']):
            return 'Eventos & Divulgação'
        else:
            return 'Outros'

    df['Categoria_Macro'] = df['Tipo da atividade'].apply(definir_categoria)
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
    st.stop()

# --- PAINEL DE FILTROS HORIZONTAL ---
with st.container(border=True):
    st.markdown("###### Filtros de Visualização")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        modo_visualizacao = st.radio(
            "Origem dos Dados:",
            ("Apenas LICS", "Todos (LICS + IFES)"),
            index=0,
            horizontal=True
        )

    with col_f2:
        filtro_situacao = st.radio(
            "Situação:",
            ("Tudo", "Concluídos/Aceitos", "Em Andamento"),
            index=0,
            horizontal=True
        )

    with col_f3:
        anos_disponiveis = sorted(df['Ano'].unique())
        anos_selecionados = st.multiselect(
            "Anos:",
            options=anos_disponiveis,
            default=anos_disponiveis,
            placeholder="Selecione os anos"
        )

# --- LÓGICA DE FILTRAGEM ---
if modo_visualizacao == "Apenas LICS":
    df_filtered = df[df['Vinculo'] == 'LICS']
else:
    df_filtered = df 

if filtro_situacao == "Concluídos/Aceitos":
    termos_positivos = ['Aceito', 'Concluído', 'Certificado', 'Habilitado']
    df_filtered = df_filtered[df_filtered['Status'].str.contains('|'.join(termos_positivos), case=False, na=False)]
elif filtro_situacao == "Em Andamento":
    termos_andamento = ['Em andamento', 'Submissão', 'Julgamento', 'Rejeitado']
    df_filtered = df_filtered[df_filtered['Status'].str.contains('|'.join(termos_andamento), case=False, na=False)]

df_filtered = df_filtered[df_filtered['Ano'].isin(anos_selecionados)]

if df_filtered.empty:
    st.warning("Nenhum dado encontrado. Ajuste os filtros acima.")
    st.stop()

# --- MAPA DE CORES CONSISTENTE ---
# Definindo as cores uma única vez para usar em todos os gráficos
mapa_cores = {
    'Inovação & Startups': '#FF4B4B', # Vermelho
    'Produção Intelectual': '#1C83E1', # Azul
    'Formação & Orientações': '#00CC96', # Verde
    'Eventos & Divulgação': '#FFA15A', # Laranja
    'Outros': '#d3d3d3' # Cinza
}

# --- METRICAS PRINCIPAIS (KPIs) ---
st.markdown("---")
total_inovacao = len(df_filtered[df_filtered['Categoria_Macro'] == 'Inovação & Startups'])
total_intelectual = len(df_filtered[df_filtered['Categoria_Macro'] == 'Produção Intelectual'])
total_formacao = len(df_filtered[df_filtered['Categoria_Macro'] == 'Formação & Orientações'])
total_alunos = int(df_filtered['Total_Alunos'].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Inovação & Startups", total_inovacao)
col2.metric("Produção Intelectual", total_intelectual)
col3.metric("Formação (Orientações)", total_formacao)
col4.metric("Alunos Envolvidos", total_alunos)

# --- GRÁFICOS (ABAS) ---
tab1, tab2, tab3 = st.tabs(["Visão Estratégica", "Envolvimento Discente", "Dados Detalhados"])

with tab1:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Distribuição por Macro-Categoria")
        fig_cat = px.pie(
            df_filtered, 
            names='Categoria_Macro', 
            title='Proporção das Áreas de Atuação', 
            hole=0.4,
            color='Categoria_Macro',
            color_discrete_map=mapa_cores
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col_g2:
        st.subheader("Ranking de Atividades (Volume)")
        # Agrupamento para contar quantos itens tem em cada tipo específico
        df_ranking = df_filtered.groupby(['Tipo da atividade', 'Categoria_Macro']).size().reset_index(name='Quantidade')
        
        # Gráfico de Barras Simples e Limpo
        fig_ranking = px.bar(
            df_ranking, 
            x='Quantidade', 
            y='Tipo da atividade', 
            color='Categoria_Macro', # A cor indica a qual grupo pertence
            orientation='h',
            text='Quantidade',
            title="O que mais produzimos? (Top Atividades)",
            color_discrete_map=mapa_cores
        )
        
        # Ordena do maior para o menor
        fig_ranking.update_layout(
            yaxis={'categoryorder':'total ascending'}, 
            legend_title_text='Área',
            xaxis_title=None,
            yaxis_title=None
        )
        st.plotly_chart(fig_ranking, use_container_width=True)

    st.subheader("Evolução das Categorias (2024-2025)")
    df_evolucao = df_filtered.groupby(['Ano', 'Categoria_Macro']).size().reset_index(name='Quantidade')
    fig_evolucao = px.bar(
        df_evolucao, 
        x="Ano", 
        y="Quantidade", 
        color="Categoria_Macro", 
        barmode='group',
        text='Quantidade',
        color_discrete_map=mapa_cores
    )
    fig_evolucao.update_traces(textposition='outside')
    st.plotly_chart(fig_evolucao, use_container_width=True)

with tab2:
    st.subheader("Participação de Alunos por Nível")
    dados_alunos = pd.DataFrame({
        'Nível de Ensino': ['Técnico Integrado', 'Técnico Concomitante', 'Bacharelado (BSI)'],
        'Quantidade': [
            df_filtered['Alunos_Tec_Integrado'].sum(),
            df_filtered['Alunos_Tec_Concomitante'].sum(),
            df_filtered['Alunos_BSI'].sum()
        ]
    })
    fig_alunos = px.bar(
        dados_alunos, 
        x='Nível de Ensino', 
        y='Quantidade', 
        color='Quantidade', 
        color_continuous_scale='Greens',
        text='Quantidade'
    )
    fig_alunos.update_traces(textposition='outside')
    fig_alunos.update_layout(coloraxis_showscale=False, yaxis_title=None, xaxis_title=None)
    st.plotly_chart(fig_alunos, use_container_width=True)

with tab3:
    st.subheader("Tabela de Registros Filtrados")
    st.dataframe(df_filtered.set_index('Ano'), use_container_width=True)
