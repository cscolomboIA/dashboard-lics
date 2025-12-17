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

# --- BARRA LATERAL ---
if os.path.exists("logo_lics.jpg"):
    st.sidebar.image("logo_lics.jpg", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.info("**LICS - Laboratório de Inteligência Computacional na Saúde**\n\nCoordenação: Prof. Cristiano da Silveira Colombo")

# --- CABEÇALHO ---
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

    # Categorização simples (apenas para organização interna, sem exibição visual pesada)
    def definir_categoria(tipo):
        tipo = str(tipo).lower()
        if any(x in tipo for x in ['inovação', 'startup', 'gênesis', 'centelha', 'software', 'patente']):
            return 'Inovação & Startups'
        elif any(x in tipo for x in ['artigo', 'revista', 'periódico', 'livro']):
            return 'Produção Intelectual'
        elif any(x in tipo for x in ['orientação', 'tcc', 'curso', 'minicurso', 'iniciação']):
            return 'Formação & Orientações'
        else:
            return 'Outros'

    df['Categoria_Macro'] = df['Tipo da atividade'].apply(definir_categoria)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
    st.stop()

# --- FILTROS HORIZONTAIS ---
with st.container(border=True):
    st.markdown("###### Filtros de Visualização")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        modo_visualizacao = st.radio("Origem dos Dados:", ("Apenas LICS", "Todos (LICS + IFES)"), index=0, horizontal=True)
    with col_f2:
        filtro_situacao = st.radio("Situação:", ("Tudo", "Concluídos/Aceitos", "Em Andamento"), index=0, horizontal=True)
    with col_f3:
        anos_disponiveis = sorted(df['Ano'].unique())
        anos_selecionados = st.multiselect("Anos:", options=anos_disponiveis, default=anos_disponiveis, placeholder="Selecione os anos")

# Lógica de Filtragem
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

# --- KPIs ---
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

# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["Visão Estratégica", "Envolvimento Discente", "Dados Detalhados"])

with tab1:
    # --- COLUNA 1: SELETOR DE ATIVIDADE (O PEDIDO PRINCIPAL) ---
    col_detalhe_1, col_detalhe_2 = st.columns([2, 1])
    
    with col_detalhe_1:
        st.subheader("Explorador de Atividades")
        
        # Cria lista de atividades disponíveis nos dados filtrados
        lista_atividades = sorted(df_filtered['Tipo da atividade'].unique())
        
        # O Combobox (Selectbox)
        atividade_selecionada = st.selectbox("Selecione para ver detalhes:", options=lista_atividades)
        
        # Filtra os dados apenas para a atividade selecionada
        df_atividade = df_filtered[df_filtered['Tipo da atividade'] == atividade_selecionada]
        
        # Mostra métrica específica
        st.metric(f"Total de: {atividade_selecionada}", len(df_atividade))
        
        # Gráfico da Atividade Selecionada
        grafico_atividade = df_atividade.groupby('Ano').size().reset_index(name='Quantidade')
        fig_atividade = px.bar(
            grafico_atividade, 
            x='Ano', 
            y='Quantidade', 
            title=f"Evolução: {atividade_selecionada}",
            text='Quantidade'
        )
        fig_atividade.update_traces(textposition='outside')
        fig_atividade.update_layout(xaxis=dict(tickmode='linear', dtick=1)) # Garante mostrar ano a ano
        st.plotly_chart(fig_atividade, use_container_width=True)
        
        # Tabela simples com os títulos dessa atividade
        with st.expander(f"Ver lista de títulos ({len(df_atividade)})", expanded=True):
            st.dataframe(
                df_atividade[['Ano', 'Titulo', 'Status']].reset_index(drop=True),
                use_container_width=True
            )

    # --- COLUNA 2: HALL DE PUBLICAÇÕES (EVENTOS) ---
    with col_detalhe_2:
        st.subheader("Onde Publicamos?")
        st.markdown("Eventos e Revistas com artigos aceitos/concluídos:")
        
        # Filtra apenas Artigos que foram Aceitos ou Concluídos (Independente do filtro de situação global, aqui olhamos o sucesso)
        # Nota: Usamos o dataframe original (df) ou filtrado (df_filtered) dependendo se quer respeitar os filtros de ano
        termos_artigo = ['artigo', 'publicação', 'revista']
        termos_sucesso = ['aceito', 'concluído']
        
        df_pubs = df_filtered[
            (df_filtered['Tipo da atividade'].str.lower().str.contains('|'.join(termos_artigo))) &
            (df_filtered['Status'].str.lower().str.contains('|'.join(termos_sucesso)))
        ]
        
        # Pega lista única de eventos
        eventos_unicos = sorted(df_pubs['Evento_Periodico'].dropna().unique())
        
        if len(eventos_unicos) > 0:
            for evento in eventos_unicos:
                # Limpa traços soltos se houver
                if evento.strip() != "-":
                    st.markdown(f"- **{evento}**")
        else:
            st.info("Nenhuma publicação encontrada nos critérios filtrados.")
            
        st.markdown("---")
        st.markdown("**Distribuição Macro**")
        # Gráfico de Pizza Pequeno para contexto geral
        fig_pizza = px.pie(df_filtered, names='Categoria_Macro', hole=0.5)
        fig_pizza.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pizza, use_container_width=True)

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
