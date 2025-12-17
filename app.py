import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
# Tenta carregar a logo para o ícone da página. 
# Se não encontrar (caso vc esqueça de subir), usa um emoji de DNA para não dar erro.
try:
    page_icon = "logo_lics.jpg" # Certifique-se que o nome do arquivo no GitHub é EXATAMENTE este
    st.set_page_config(page_title="Dashboard LICS", layout="wide", page_icon=page_icon)
except:
    st.set_page_config(page_title="Dashboard LICS", layout="wide", page_icon="🧬")

# --- BARRA LATERAL (SIDEBAR) COM LOGO ---
st.sidebar.image("logo_lics.jpg", use_column_width=True) # Exibe a logo grande na barra lateral
st.sidebar.markdown("---") # Linha divisória

# --- CABEÇALHO ---
col_header1, col_header2 = st.columns([1, 5])
with col_header1:
    # Opcional: Mostra a logo pequena ao lado do título também, se quiser
    st.image("logo_lics.jpg", width=100)
with col_header2:
    st.title("LICS - Laboratório de Inteligência Computacional na Saúde")
    st.markdown(f"**Coordenação:** Prof. Cristiano da Silveira Colombo | **Atualização:** Dez/2025")

st.markdown("---")

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def load_data():
    # Lê o CSV
    df = pd.read_csv("dados.csv")
    
    # Nomes forçados para garantir a estrutura correta das colunas
    novos_nomes = [
        'Ano', 
        'Tipo da atividade', 
        'Titulo', 
        'Evento_Periodico', 
        'Data', 
        'Carga_Horaria', 
        'Autores', 
        'Qualis', 
        'Alunos_Tec_Integrado',  
        'Alunos_Tec_Concomitante', 
        'Alunos_BSI',            
        'Status', 
        'Vinculo'
    ]
    
    # Verifica integridade das colunas
    if len(df.columns) == len(novos_nomes):
        df.columns = novos_nomes
    else:
        st.error(f"O CSV tem {len(df.columns)} colunas, mas o código esperava {len(novos_nomes)}. Verifique o arquivo.")
        st.stop()
    
    # Tratamento numérico
    cols_alunos = ['Alunos_Tec_Integrado', 'Alunos_Tec_Concomitante', 'Alunos_BSI']
    for col in cols_alunos:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Criar coluna de Total de Alunos
    df['Total_Alunos'] = df[cols_alunos].sum(axis=1)
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao processar dados. Detalhe: {e}")
    st.stop()

# --- FILTROS (SIDEBAR CONTINUAÇÃO) ---
st.sidebar.header("Filtros de Visualização")
anos = st.sidebar.multiselect("Selecione o Ano", options=sorted(df['Ano'].unique()), default=sorted(df['Ano'].unique()))
status_filter = st.sidebar.multiselect("Status da Atividade", options=sorted(df['Status'].unique()), default=sorted(df['Status'].unique()))

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
tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "🎓 Envolvimento Discente", "📋 Dados Detalhados"])

with tab1:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Atividades por Status")
        fig_status = px.pie(df_filtered, names='Status', title='Taxa de Aprovação e Conclusão', hole=0.4)
        st.plotly_chart(fig_status, use_container_width=True)
    with col_g2:
        st.subheader("Tipos de Atividade")
        contagem_tipo = df_filtered['Tipo da atividade'].value_counts().reset_index()
        contagem_tipo.columns = ['Tipo', 'Quantidade']
        fig_tipo = px.bar(contagem_tipo, x='Quantidade', y='Tipo', orientation='h', title="Atividades por Categoria")
        st.plotly_chart(fig_tipo, use_container_width=True)

    st.subheader("Evolução Temporal")
    df_evolucao = df_filtered.groupby(['Ano', 'Tipo da atividade']).size().reset_index(name='Quantidade')
    fig_evolucao = px.bar(df_evolucao, x="Ano", y="Quantidade", color="Tipo da atividade", title="Crescimento das Atividades (2024-2025)", barmode='group')
    st.plotly_chart(fig_evolucao, use_container_width=True)

with tab2:
    st.subheader("Participação de Alunos por Nível")
    total_tec = df_filtered['Alunos_Tec_Integrado'].sum()
    total_con = df_filtered['Alunos_Tec_Concomitante'].sum()
    total_bsi = df_filtered['Alunos_BSI'].sum()
    
    dados_alunos = pd.DataFrame({
        'Nível de Ensino': ['Técnico Integrado', 'Técnico Concomitante', 'Bacharelado (BSI)'],
        'Quantidade': [total_tec, total_con, total_bsi]
    })
    
    fig_alunos = px.bar(dados_alunos, x='Nível de Ensino', y='Quantidade', color='Nível de Ensino', text='Quantidade', title="Total de Alunos Envolvidos")
    fig_alunos.update_traces(textposition='outside')
    st.plotly_chart(fig_alunos, use_container_width=True)

with tab3:
    st.subheader("Tabela de Registros")
    st.dataframe(df_filtered)
