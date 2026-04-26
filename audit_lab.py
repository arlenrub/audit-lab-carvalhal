import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client, Client
from prophet import Prophet

# 1. Configuração da Página
st.set_page_config(page_title="Audit Lab - Carvalhal", layout="wide")

st.title("🛡️ Auditoria Contínua e Compliance")
st.markdown("Monitoramento de **KRIs** e Alertas em Tempo Real (Conectado ao **Supabase**).")

# Barra Lateral de Filtros
st.sidebar.header("🔍 Filtros de Auditoria")
unidade_selecionada = st.sidebar.selectbox(
    "Selecione a Unidade para analisar:",
    ["Todas as Unidades", "Recife", "Jaboatão", "Olinda"]
)
st.sidebar.markdown("---")
st.sidebar.info("Use este filtro para isolar os alertas e investigar fraudes em filiais específicas.")

st.markdown("---")

# 2. Conexão com o Supabase
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

@st.cache_data(ttl=10)
def carregar_alertas():
    resposta = supabase.table("alertas_compliance").select("*").execute()
    return pd.DataFrame(resposta.data)

df_banco_real = carregar_alertas()

# ==========================================
# 3. O FIM DO DADO FALSO (Conectando Gráficos aos Dados Reais)
# ==========================================
if not df_banco_real.empty:
    df_banco_real = df_banco_real[['data_hora', 'tipo_divergencia', 'unidade', 'valor_envolvido', 'status']]
    df_banco_real.columns = ['Data/Hora', 'Tipo de Divergência', 'Unidade', 'Valor (R$)', 'Status']
    
    # 0. A TRAVA DE SEGURANÇA: Converte a data avisando que o DIA vem primeiro (dayfirst=True)
    df_banco_real['Data/Hora'] = pd.to_datetime(df_banco_real['Data/Hora'], dayfirst=True, errors='coerce')
    
    # ORDENAÇÃO: Agora que o Python entendeu a data, coloca o mais novo no topo
    df_banco_real = df_banco_real.sort_values(by='Data/Hora', ascending=False)
    
    # 1. Cria a coluna de Data para a IA (usando a data limpa)
    df_banco_real['Data'] = df_banco_real['Data/Hora'].dt.date
    df_banco_real['Data'] = pd.to_datetime(df_banco_real['Data']) 
    
    # 2. Formatação Visual: Arrumando a Data/Hora para o padrão Brasileiro (DD/MM/AAAA HH:MM)
    df_banco_real['Data/Hora'] = df_banco_real['Data/Hora'].dt.strftime('%d/%m/%Y %H:%M:%S')
    
    # 3. Formatação Visual: Arrumando o Valor para moeda brasileira
    df_banco_real['Valor (R$)'] = df_banco_real['Valor (R$)'].apply(lambda x: f"{float(x):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

    # Agrupa os dados reais
    df_graficos = df_banco_real.groupby(['Data', 'Unidade']).agg(
        Divergências=('Tipo de Divergência', 'count'),
        Risco_Financeiro=('Valor (R$)', lambda x: x.str.replace('.', '').str.replace(',', '.').astype(float).sum()) 
    ).reset_index()
else:
    df_graficos = pd.DataFrame(columns=['Data', 'Unidade', 'Divergências', 'Risco_Financeiro'])

# Aplicando o Filtro do Usuário
if unidade_selecionada != "Todas as Unidades":
    if not df_banco_real.empty:
        df_banco_real = df_banco_real[df_banco_real['Unidade'] == unidade_selecionada]
    df_graficos = df_graficos[df_graficos['Unidade'] == unidade_selecionada]

# 4. Métricas Executivas no Topo
st.markdown(f"### 🎯 Resumo Operacional: **{unidade_selecionada}**")
c1, c2, c3 = st.columns(3)
c1.metric("Transações Monitoradas", "Conectado ao BD")
c2.metric("Total de Divergências", df_graficos['Divergências'].sum(), "Registradas", delta_color="inverse")

if unidade_selecionada == "Todas as Unidades":
    if not df_graficos.empty:
        unidade_critica = df_graficos.groupby('Unidade')['Divergências'].sum().idxmax()
        c3.metric("Unidade em Alerta Máximo", unidade_critica)
else:
    c3.metric("Status do Monitoramento", "Isolado")

st.markdown("---")

# 5. GRÁFICOS COM IA PREDITIVA (USANDO DADOS REAIS)
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔮 Tendência de Volume Financeiro em Risco")
    st.caption("A IA projeta o risco financeiro para os próximos 7 dias *(Valores em R$ Milhares)*.")
    
    if len(df_graficos) > 2: 
        # Prepara os dados reais
        risco_diario = df_graficos.groupby('Data')['Risco_Financeiro'].sum().reset_index()
        
        # O TRUQUE DE DESIGN: Divide por 1.000 para tirar o excesso de zeros do gráfico
        risco_diario['Risco_Financeiro'] = risco_diario['Risco_Financeiro'] / 1000
        
        df_prophet = risco_diario.rename(columns={'Data': 'ds', 'Risco_Financeiro': 'y'})
        
        # Treina a IA
        m = Prophet(daily_seasonality=False, yearly_seasonality=False, weekly_seasonality=True)
        m.fit(df_prophet)
        
        # Projeta
        futuro = m.make_future_dataframe(periods=7)
        previsao = m.predict(futuro)
        
        # Organiza
        df_plot = previsao[['ds', 'yhat']].rename(columns={'ds': 'Data', 'yhat': 'Projeção (IA)'}).set_index('Data')
        
        # A CORREÇÃO ESTÁ AQUI: Trocando 'Risco_Financeiro' para o nome final
        df_real = risco_diario.rename(columns={'Risco_Financeiro': 'Risco Real (R$ Mil)'}).set_index('Data')
        
        df_final = df_real.join(df_plot, how='outer')
        st.line_chart(df_final[['Risco Real (R$ Mil)', 'Projeção (IA)']])
    else:
        st.warning("Aguardando mais dias de histórico real para gerar previsões.")

with col2:
    st.subheader("🚨 Volume de Divergências por Unidade")
    if not df_graficos.empty:
        erros_unidade = df_graficos.groupby('Unidade')['Divergências'].sum()
        st.bar_chart(erros_unidade)

# 6. Tabela DADOS REAIS E EXPORTAÇÃO
st.markdown("---")
st.subheader("📋 Últimos Alertas Críticos (Ao Vivo do Banco de Dados)")

if not df_banco_real.empty:
    # Mostra a tabela escondendo a coluna extra 'Data' que usamos para cálculo
    st.dataframe(df_banco_real.drop(columns=['Data']), use_container_width=True)
    
    st.markdown("---")
    st.subheader("📥 Gerar Relatório de Conformidade")
    st.caption("Faça o download dos dados filtrados para análise offline.")
    
    csv = df_banco_real.drop(columns=['Data']).to_csv(index=False, sep=';', decimal=',', encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="📊 Baixar Relatório (Excel/CSV)",
        data=csv,
        file_name=f"relatorio_auditoria_{unidade_selecionada}.csv",
        mime="text/csv",
    )
else:
    st.success(f"Nenhum alerta registrado no banco de dados para **{unidade_selecionada}**.")
