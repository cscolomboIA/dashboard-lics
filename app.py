import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
try:
    page_icon = "logo_lics.jpg" 
    st.set_page_config(page_title="Dashboard LICS", layout="wide", page_icon=page_icon)
except:
    st.set_page_config(page_title="Dashboard LICS", layout="wide", page_icon="🧬")

# --- BARRA LATERAL (SIDEBAR) ---
if os.path.exists("logo_lics.jpg"):
    st.sidebar.image("logo_lics.jpg", use_container_width=True)
else:
    st.sidebar.warning("Logo não encontrada (logo_lics.jpg)")

st.sidebar.markdown("---") 

# --- CABEÇALHO PRINCIPAL ---
col_header1, col_header2 = st.columns([1, 6])
with col_header1:
    if os.path.exists("logo_lics.jpg"):
        st.image("logo_lics.jpg", width=110)
with col_header2:
    st.title("LICS - Laboratório de Inteligência Computacional na Saúde")
    st.markdown("**Coordenação:** Prof. Cristiano da Silveira Colombo | **Atualização:** Dez/2025")

# --- SEÇÃO INTRODUTÓRIA (TEXTO LIMPO) ---
st.markdown("---")
st.markdown("""
### Painel de Controle Estratégico
Este dashboard apresenta o monitoramento em tempo real das ações de pesquisa, desenvolvimento e inovação (PD&I) realizadas pelo laboratório. 
Os dados consolidam o ciclo **2024-2025**, oferecendo transparência sobre três pilares fundamentais:

*   **Produção Científica:** Artigos em periódicos e eventos de alto impacto (CBIS, SBSI, SBCAS) focados em IA na Saúde (NER, LLMs, Ontologias).
*   **Ecossistema de Inovação:** Acompanhamento de Startups (Programas Gênesis e Centelha) e projetos de fomento.
*   **Formação de Talentos:** Envolvimento de discentes do Técnico Integrado ao Bacharelado em Sistemas de Informação.

**Guia de Navegação:**
*   **Visão Geral:** Estatísticas de aprovação, tipos de produção e linha do tempo.
*   **Envolvimento Discente:** Quantitativo de alunos capacitados por nível de ensino.
*   **Dados Detalhados:** Tabela completa para auditoria e consulta específica.
""")
st.markdown("---")

# --- CARREGAMENTO DE DADOS ---
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
        st.error(f"Erro na estrutura do CSV. Esperado: {len(novos_nomes)} colunas. Encontrado: {len(df.columns)}.")
        st.stop()
    
    cols_alunos = ['Alunos_Tec_Integrado', 'Alunos_Tec_Concomitante', 'Alunos_BSI']
    for col in cols_alunos:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['Total_Alunos'] = df[cols_alunos].sum(axis=1)
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
    st.stop()

# --- FILTROS (SIDEBAR) ---
st.sidebar.header("Filtros de Visualização")

# Filtro de Vínculo (Padrão: LICS)
opcoes_vinculo = sorted(df['Vinculo'].astype(str).unique())
padrao_vinculo = ['LICS'] if 'LICS' in opcoes_vinculo else opcoes_vinculo
vinculo_selecionado = st.sidebar.multiselect("Filtrar por Vínculo", options=opcoes_vinculo, default=padrao_vinculo)

# Filtro de Ano
anos_disponiveis = sorted(df['Ano'].unique())
anos_selecionados = st.sidebar.multiselect("Selecione o Ano", options=anos_disponiveis, default=anos_disponiveis)

# Filtro de Status
status_disponiveis = sorted(df['Status'].astype(str).unique())
status_selecionados = st.sidebar.multiselect("Status da Atividade", options=status_disponiveis, default=status_disponiveis)

# Aplicação dos Filtros
df_filtered = df[
    (df['Ano'].isin(anos_selecionados)) & 
    (df['Status'].isin(status_selecionados)) &
    (df['Vinculo'].isin(vinculo_selecionado))
]

if df_filtered.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# --- METRICAS PRINCIPAIS (KPIs) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Atividades", len(df_filtered))
col2.metric("Envolvimento de Alunos", int(df_filtered['Total_Alunos'].sum()))
col3.metric("Produção Científica (Artigos)", len(df_filtered[df_filtered['Tipo da atividade'].str.contains("Artigo", case=False, na=False)]))
col4.metric("Projetos & Inovação", len(df_filtered[df_filtered['Tipo da atividade'].str.contains("Projeto|Programa|Inovação", case=False, na=False)]))

st.markdown("---")

# --- GRÁFICOS ---
tab1, tab2, tab3 = st.tabs(["Visão Geral", "Envolvimento Discente", "Dados Detalhados"])

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
    fig_evolucao = px.bar(df_evolucao, x="Ano", y="Quantidade", color="Tipo da atividade", title="Crescimento das Atividades", barmode='group')
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
    fig_alunos = px.bar(dados_alunos, x='Nível de Ensino', y='Quantidade', color='Nível de Ensino', text='Quantidade', title="Total de Alunos Envolvidos")
    fig_alunos.update_traces(textposition='outside')
    st.plotly_chart(fig_alunos, use_container_width=True)

with tab3:
    st.subheader("Tabela de Registros Filtrados")
    st.dataframe(df_filtered)
