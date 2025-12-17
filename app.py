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

# --- PAINEL DE FILTROS HORIZONTAL (TOP BAR) ---
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

# --- METRICAS PRINCIPAIS (KPIs) ---
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Atividades", len(df_filtered))
col2.metric("Envolvimento de Alunos", int(df_filtered['Total_Alunos'].sum()))
col3.metric("Produção Científica", len(df_filtered[df_filtered['Tipo da atividade'].str.contains("Artigo", case=False, na=False)]))
col4.metric("Projetos & Inovação", len(df_filtered[df_filtered['Tipo da atividade'].str.contains("Projeto|Programa|Inovação", case=False, na=False)]))

# --- GRÁFICOS (ABAS) ---
tab1, tab2, tab3 = st.tabs(["Visão Geral", "Envolvimento Discente", "Dados Detalhados"])

with tab1:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Taxa de Sucesso")
        fig_status = px.pie(df_filtered, names='Status', title='Distribuição por Status', hole=0.4)
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col_g2:
        st.subheader("Atividades por Categoria")
        
        # --- MELHORIA DE UX AQUI ---
        # 1. Preparar os dados com contagem E porcentagem
        contagem_tipo = df_filtered['Tipo da atividade'].value_counts().reset_index()
        contagem_tipo.columns = ['Tipo', 'Quantidade']
        contagem_tipo['Percentual'] = (contagem_tipo['Quantidade'] / contagem_tipo['Quantidade'].sum()) * 100
        
        # 2. Criar gráfico com gradiente de cor e ordenação
        fig_tipo = px.bar(
            contagem_tipo, 
            x='Quantidade', 
            y='Tipo', 
            orientation='h',
            text='Quantidade', # Mostra o número na ponta da barra
            color='Quantidade', # A cor muda conforme o valor (Heatmap)
            color_continuous_scale='Teal', # Escala de cor profissional (Teal combina com saúde)
            custom_data=['Percentual'] # Passa o percentual para o tooltip
        )
        
        # 3. Ajustes finos de Layout
        fig_tipo.update_layout(
            yaxis={'categoryorder':'total ascending'}, # Garante que a maior barra fique no topo
            coloraxis_showscale=False, # Esconde a legenda de cores para limpar o visual
            xaxis_title=None,
            yaxis_title=None
        )
        
        # 4. Tooltip personalizado (Ao passar o mouse)
        fig_tipo.update_traces(
            textposition='outside', 
            hovertemplate='<b>%{y}</b><br>Quantidade: %{x}<br>Representatividade: %{customdata[0]:.1f}%<extra></extra>'
        )
        
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
    # Também aplicando a melhoria visual aqui para consistência
    fig_alunos = px.bar(
        dados_alunos, 
        x='Nível de Ensino', 
        y='Quantidade', 
        color='Quantidade', # Cor baseada no valor
        color_continuous_scale='Greens', # Escala verde para diferenciar da outra aba
        text='Quantidade'
    )
    fig_alunos.update_traces(textposition='outside')
    fig_alunos.update_layout(coloraxis_showscale=False, yaxis_title=None, xaxis_title=None)
    
    st.plotly_chart(fig_alunos, use_container_width=True)

with tab3:
    st.subheader("Tabela de Registros Filtrados")
    # Melhoria na tabela: Ocultar o índice numérico padrão do Pandas para ficar mais limpo
    st.dataframe(df_filtered.set_index('Ano'), use_container_width=True)
