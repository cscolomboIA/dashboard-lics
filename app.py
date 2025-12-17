import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Dashboard LICS", layout="wide", page_icon="🧬")

# Título e Cabeçalho
st.title("LICS - Laboratório de Inteligência Computacional na Saúde")
st.markdown(f"**Coordenação:** Prof. Cristiano da Silveira Colombo | **Atualização:** Dez/2025")
st.markdown("---")

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def load_data():
    # Lê o CSV. 
    df = pd.read_csv("registros-atividades-LICS-tabuladas.csv")
    
    # Limpeza dos nomes das colunas (remove quebras de linha e espaços extras)
    df.columns = [c.replace('\n', ' ').strip() for c in df.columns]
    
    # Renomeando colunas complexas para facilitar
    df.rename(columns={
        'Alunos do curso técnico integrado ao ensino médio': 'Alunos_Tec_Integrado',
        'Alunos do curso técnico concomitante': 'Alunos_Tec_Concomitante',
        'Aunos do Bacharelado em Sistemas de Informação': 'Alunos_BSI', # Notei o erro de digitação no original 'Aunos'
        'Carga horária': 'Carga_Horaria'
    }, inplace=True)
    
    # Tratamento de Nulos
    cols_alunos = ['Alunos_Tec_Integrado', 'Alunos_Tec_Concomitante', 'Alunos_BSI']
    for col in cols_alunos:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Criar coluna de Total de Alunos
    df['Total_Alunos'] = df[cols_alunos].sum(axis=1)
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar o arquivo CSV. Verifique se 'dados.csv' está no repositório. Erro: {e}")
    st.stop()

# --- SIDEBAR (FILTROS) ---
st.sidebar.header("Filtros")
anos = st.sidebar.multiselect("Selecione o Ano", options=df['Ano'].unique(), default=df['Ano'].unique())
status_filter = st.sidebar.multiselect("Status da Atividade", options=df['Status'].unique(), default=df['Status'].unique())

# Aplicando Filtros
df_filtered = df[(df['Ano'].isin(anos)) & (df['Status'].isin(status_filter))]

# --- METRICAS PRINCIPAIS (KPIs) ---
col1, col2, col3, col4 = st.columns(4)

total_atividades = len(df_filtered)
total_alunos = int(df_filtered['Total_Alunos'].sum())
total_artigos = len(df_filtered[df_filtered['Tipo da atividade'].str.contains("Artigo", case=False, na=False)])
projetos_fomento = len(df_filtered[df_filtered['Tipo da atividade'].str.contains("Projeto|Programa|Inovação", case=False, na=False)])

col1.metric("Total de Atividades", total_atividades)
col2.metric("Envolvimento de Alunos", total_alunos)
col3.metric("Produção Científica (Artigos)", total_artigos)
col4.metric("Projetos & Inovação", projetos_fomento)

st.markdown("---")

# --- GRÁFICOS ---

tab1, tab2, tab3 = st.tabs(["Visão Geral", "Envolvimento Discente", "Dados Detalhados"])

with tab1:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("Atividades por Status")
        # Aqui vemos claramente o que foi aceito vs rejeitado
        fig_status = px.pie(df_filtered, names='Status', title='Distribuição dos Status das Atividades', hole=0.4)
        st.plotly_chart(fig_status, use_container_width=True)
        
    with col_g2:
        st.subheader("Tipos de Atividade")
        contagem_tipo = df_filtered['Tipo da atividade'].value_counts().reset_index()
        contagem_tipo.columns = ['Tipo', 'Quantidade']
        fig_tipo = px.bar(contagem_tipo, x='Quantidade', y='Tipo', orientation='h', title="Atividades por Categoria")
        st.plotly_chart(fig_tipo, use_container_width=True)

    st.subheader("Evolução Temporal")
    fig_evolucao = px.histogram(df_filtered, x="Ano", color="Tipo da atividade", barmode="group", title="Atividades por Ano e Tipo")
    st.plotly_chart(fig_evolucao, use_container_width=True)

with tab2:
    st.subheader("Participação de Alunos por Nível")
    
    # Agrupando dados de alunos
    total_tec = df_filtered['Alunos_Tec_Integrado'].sum()
    total_con = df_filtered['Alunos_Tec_Concomitante'].sum()
    total_bsi = df_filtered['Alunos_BSI'].sum()
    
    dados_alunos = pd.DataFrame({
        'Nível': ['Técnico Integrado', 'Técnico Concomitante', 'Bacharelado (BSI)'],
        'Quantidade': [total_tec, total_con, total_bsi]
    })
    
    fig_alunos = px.bar(dados_alunos, x='Nível', y='Quantidade', color='Nível', text='Quantidade', title="Total de Alunos Envolvidos")
    st.plotly_chart(fig_alunos, use_container_width=True)

with tab3:
    st.subheader("Tabela de Registros")
    st.dataframe(df_filtered)
