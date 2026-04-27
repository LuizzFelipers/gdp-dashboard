import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import json
import requests

st.set_page_config(layout="wide",page_title="Pagamentos Pendentes")

# def formatar_reais(valor):
#     return f"R$ {valor:,.2f}".replace()

if 'pagamentos' not in st.session_state:
    st.session_state.pagamentos = pd.DataFrame(columns=[
        "Cliente","Valor Original","Moeda","Valor em BRL",
        "Data de Vencimento", "Status", "Data de Pagamento"
            ])

def verirficar_pagamentos():
    # Integração com a API de pagamentos    
    api_url = ""
    headers = {"Authorization": f"Bearer {st.secrets['API_KEY']}"}

    try:
        response = requests.get(api_url, headers=headers)
        pagamentos = response.json()

        for pagamento in pagamentos:
            if pagamento['Status'] == 'Pago' and pagamento['id'] not in st.session_state.pagamentos.index:
                st.session_state.pagamentos.loc[pagamento['id'], 'Status'] = 'Pago'
                st.session_state.pagamentos.loc[pagamento['id'], 'Data de Pagamento'] = datetime.now()

    except Exception as e:
        st.error(f'Erro ao Verificar pagamentos: {e}')

def get_cotacao(moeda):
    # Obtém a cotação atual da moeda
    if moeda == 'BRL':
        return 1.0
    
    try:

        url = f'https://api.exchangerate-api.com/v4/latest/{moeda}'
        response = requests.get(url)
        data = response.json()
        return data["rates"]["BRL"]
    except:
        return st.session_state.ultima_cotacao.get(moeda, 1.0)
    
def main():

    st.title("Acompanhar Pagamentos Pendentes")
    # Atualizar a cada 5 minutos
    if st.button(" Atualizar Pagamentos") or st.session_state.get("auto_update", False):
        verirficar_pagamentos()
        st.session_state.auto_update = True
        st.rerun()

    # exibir os totais 
    pendentes = st.session_state.pagamentos[st.session_state.pagamentos['Status'] == 'Pendente']
    total_pendente = pendentes["Valor em BRL"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Pendente",f"R$ {total_pendente:,.2f}")
    col2.metric("Valor Recuperado", f"R$ {0}")
    col3.metric("Quantidade Pendente",len(pendentes))
    col4.metric("Última Atualização", datetime.now().strftime("%H:%M"))

    st.subheader("Detalhamento dos Pagamentos")
    st.dataframe(st.session_state.pagamentos, use_container_width=True)

    st.subheader('Análise Visual')
    fig = px.pie(st.session_state.pagamentos, names='Status', title="Distribuição por status")


    st.plotly_chart(fig)

main()
get_cotacao()