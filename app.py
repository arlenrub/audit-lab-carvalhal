import streamlit as st
import pandas as pd

st.set_page_config(page_title="Techguia Data Science", page_icon="📊")

st.title("📊 Techguia Digital - Dashboard de Teste")
st.write(f"Olá Arlen! Este dashboard está rodando na Oracle Cloud.")

# Uma tabelinha simples para testar o Pandas
df = pd.DataFrame({
    'Serviço': ['Automação n8n', 'Landing Page', 'Data Science'],
    'Status': ['Ativo', 'Ativo', 'Em Estudo']
})

st.table(df)

st.success("Ambiente configurado com sucesso para o curso do CESAR School!")
