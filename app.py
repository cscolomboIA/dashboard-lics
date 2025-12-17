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
    st.sidebar.warning("Logo não encontrada")

st.sidebar.markdown("---") 

# --- CABEÇALHO PRINCIPAL ---
col_header1, col_header2 = st.columns([1, 6])
with col_header1:
    if os.path.exists("logo_lics.jpg"):
        st.image("logo_lics.jpg", width=110)
with col_header2:
    st.title("LICS - Laboratório de Inteligência Computacional na Saúde")
    st.markdown("**Coordenação:** Prof. Cristiano da Silveira Colombo | **Atualização:** Dez/2025")

# --- SEÇÃO INTRODUTÓRIA ---
st.markdown("---")
st.markdown("""
### Painel de Controle Estratégico
Este dashboard apresenta o monitoramento em tempo real das ações de pesquisa, desenvolvimento e inovação (PD&I).
Os dados consolidam o ciclo **2024-2025**, oferecendo transparência sobre três pilares fundamentais:

*   **Produção Científica:** Artigos em periódicos e eventos de alto impacto focados em IA na Saúde.
*   **Ecossistema de Inovação:** Startups (Programas Gênesis/Centelha) e projetos de fomento.
*   **Formação de Talentos:** Envolvimento de discentes do Técnico Integrado ao Bacharelado.

**Guia de Navegação:**
*   **Visão Geral:** Estatísticas de aprovação e evolução temporal.
*   **Envolvimento Discente:** Quantitativo de alunos capacitados.
*   **Dados Detalhados:** Tabela completa para consulta.
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
        st.error("Erro na estrutura do CSV.")
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

# --- FILTROS INTUITIVOS (SIDEBAR NOVA) ---
st.sidebar.header("Painel de Filtros")

# 1. Filtro de Vínculo (Radio Button - Mais intuitivo)
st.sidebar.subheader("1. Origem dos Dados")
modo_visualizacao = st.sidebar.radio(
    "Escolha o escopo:",
    ("Apenas LICS", "Todos (LICS + IFES)"),
    index=0 # Começa marcado o primeiro (LICS)
)

# Lógica do Filtro de Vínculo
if modo_visualizacao == "Apenas LICS":
    df_filtered = df[df['Vinculo'] == 'LICS']
else:
    df_filtered = df # Pega tudo

# 2. Filtro de Ano (Checkboxes - Sempre visíveis)
st.sidebar.subheader("2. Período")
col_ano1, col_ano2 = st.sidebar.columns(2)
ver_2024 = col_ano1.checkbox("2024", value=True)
ver_2025 = col_ano2.checkbox("2025", value=True)

# Lógica do Filtro de Ano
anos_selecionados = []
if ver_2024: anos_selecionados.append(2024)
if ver_2025: anos_selecionados.append(2025)

# 3. Filtro de Situação (Simplificado)
st.sidebar.subheader("3. Situação")
filtro_situacao = st.sidebar.radio(
    "O que deseja ver?",
    ("Tudo", "Apenas Concluídos/Aceitos", "Em Andamento/Submissões")
)

# Lógica do Filtro de Status
if filtro_situacao == "Apenas Concluídos/Aceitos":
    # Lista de termos que indicam sucesso
    termos_positivos = ['Aceito', 'Concluído', 'Certificado', 'Habilitado']
    # Filtra onde o status contém qualquer um desses termos
    df_filtered = df_filtered[df_filtered['Status'].str.contains('|'.join(termos_positivos), case=False, na=False)]
elif filtro_situacao == "Em Andamento/Submissões":
    termos_andamento = ['Em andamento', 'Submissão', 'Julgamento', 'Rejeitado'] # Rejeitado entra aqui como "Tentativas" ou pode ser removido
    df_filtered = df_filtered[df_filtered['Status'].str.contains('|'.join(termos_andamento), case=False, na=False)]

# Aplica filtro final de Ano
df_filtered = df_filtered[df_filtered['Ano'].isin(anos_selecionados)]

# Aviso se não tiver dados
if df_filtered.empty:
    st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# --- METRICAS PRINCIPAIS (KPIs) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Atividades", len(df_filtered))
col2.metric("Envolvimento de Alunos", int(df_filtered['Total_Alunos'].sum()))
col3.metric("Produção Científica", len(df_filtered[df_filtered['Tipo da atividade'].str.contains("Artigo", case=False, na=False)]))
col4.metric("Projetos & Inovação", len(df_filtered[df_filtered['Tipo da atividade'].str.contains("Projeto|Programa|Inovação", case=False, na=False)]))

st.markdown("---")

# --- GRÁFICOS ---
tab1, tab2, tab3 = st.tabs(["Visão Geral", "Envolvimento Discente", "Dados Detalhados"])

with tab1:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Taxa de Sucesso")
        fig_status = px.pie(df_filtered, names='Status', title='Distribuição por Status', hole=0.4)
        st.plotly_chart(fig_status, use_container_width=True)
    with col_g2:
        st.subheader("Atividades por Categoria")
        contagem_tipo = df_filtered['Tipo da atividade'].value_counts().reset_index()
        contagem_tipo.columns = ['Tipo', 'Quantidade']
        fig_tipo = px.bar(contagem_tipo, x='Quantidade', y='Tipo', orientation='h')
        st.plotly_chart(fig_tipo, use_container_width=True)

    st.subheader("Evolução Temporal")
    df_evolucao = df_filtered.groupby(['Ano', 'Tipo da atividade']).size().reset_index(name='Quantidade')
    fig_evolucao = px.bar(df_evolucao, x="Ano", y="Quantidade", color="Tipo da atividade", barmode='group')
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
    fig_alunos = px.bar(dados_alunos, x='Nível de Ensino', y='Quantidade', color='Nível de Ensino', text='Quantidade')
    fig_alunos.update_traces(textposition='outside')
    st.plotly_chart(fig_alunos, use_container_width=True)

with tab3:
    st.subheader("Tabela de Registros Filtrados")
    st.dataframe(df_filtered)
