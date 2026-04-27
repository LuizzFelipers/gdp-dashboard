import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from datetime import timedelta
from streamlit_extras.metric_cards import style_metric_cards
from plotly.colors import sequential
import plotly.graph_objects as go

st.set_page_config(page_icon="",page_title="Facilites Cidadania4u",layout="wide",initial_sidebar_state="expanded")

st.title("Controle do Facilites")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Análise Geral","Recepção","Limpeza Geral","Arquivo","Uber"])


def formatar_reais(valor):
    return f"R$ {valor:,.2f}".replace(",","X").replace(".",",").replace("X",".")

with st.sidebar:

    st.subheader("Filtros Globais")
    date_range = st.date_input('Período de Análise',
                               [datetime.now() - timedelta(days=30), datetime.now()])
    
with tab1:
    st.subheader("Facilites")
    col1, col2= st.columns(2)

    col1.metric("Total de **Gasto Mensal**", formatar_reais(0))
    col2.metric("Última Atualização", datetime.now().strftime("%H:%M"))
    style_metric_cards()



with tab2:
    st.subheader("Recepção")
    col1, col2 = st.columns(2)
    col1.metric("Total de Gasto", formatar_reais(0))
    col2.metric("Última Atualização", datetime.now().strftime("%H:%M"))

with tab3:
    st.subheader("**3° Andar**")
    col1, col2 = st.columns(2)
    col1.metric("Total Gasto", formatar_reais(0))
    col2.metric("Última Atualização", datetime.now().strftime("%H:%M"))

    st.markdown("---------------------")
    st.subheader("**4° Andar**")
    col3, col4 = st.columns(2)
    col3.metric("Total Gasto",formatar_reais(0))
    col4.metric("Última Atualização", datetime.now().strftime("%H:%M"))
    
with tab4:
    st.subheader("**Arquivo**")
    col1, col2 = st.columns(2)
    col1.metric("Total Gasto", formatar_reais(0))
    col2.metric("Última Atualização", datetime.now().strftime("%H:%M"))

with tab5:
    #Load data uber
    df_uber = pd.read_excel("Registros Uber Original.xlsx")


    mapeamento = {"Travel | UberX":"UberX",
                  "Travel | Comfort Planet": "Comfort Planet",
                  "Travel | Flash Moto" :"Flash Moto",
                  "Travel | Prioridade":"Prioridade",
                  "Travel | Uber Espere e Economize": "Uber Espere e Economize",
                  "Travel | Bag": "Bag",
                  "Travel | Flash":"Flash"}
    
    df_uber["Serviço"] = df_uber["Serviço"].replace(mapeamento)

    st.subheader("Uber")
    col1, col2 = st.columns(2)
    with col1:

        uber_sart = st.date_input(
            "Data Inicial",
            value= df_uber["Data da solicitação (local)"].min(),
            min_value=df_uber["Data da solicitação (local)"].min(),
            max_value=df_uber["Data da solicitação (local)"].max(),
            key='uber_start'
        )
    with col2:
        uber_end = st.date_input(
            "Data Final",
            value=df_uber["Data da solicitação (local)"].max(),
            min_value=df_uber["Data da solicitação (local)"].min(),
            max_value=df_uber["Data da solicitação (local)"].max(),
            key="uber_end"
        )
    mask_uber = (df_uber["Data da solicitação (local)"] >= pd.to_datetime(uber_sart))& \
                (df_uber["Data da solicitação (local)"] <= pd.to_datetime(uber_end))
    df_uber_filtro = df_uber[mask_uber]

    col3, col4, col5 = st.columns(3)
    col3.metric("💰**Total Gasto**",formatar_reais(df_uber_filtro["Valor da transação em BRL (com tributos)"].sum()))

    
    categoria_mais_usada = df_uber_filtro["Serviço"].mode()
    categoria_mais_frequente = categoria_mais_usada.iloc[0] if not categoria_mais_usada.empty else 'Nenhum'
    freq_categoria = df_uber_filtro["Serviço"].value_counts().iloc[0] if not df_uber_filtro.empty else 0

    col4.metric("**Categoria de Uber mais usada**", categoria_mais_frequente)
    col4.caption(f"Utilizado {freq_categoria} vezes")

    qtd_solicitacoes_gerais = len(df_uber_filtro)
    col5.metric("Quantidade de Solicitações Feitas",qtd_solicitacoes_gerais)

    ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    df_uber_filtro["Mês"] = pd.Categorical(df_uber_filtro["Mês"], categories=ordem_meses, ordered=True)
    gasto_mensal = df_uber_filtro.groupby("Mês")["Valor da transação em BRL (com tributos)"].sum().reset_index(name="Valor")
    
    fig_uber = px.line(gasto_mensal,
                       x="Mês",
                       y="Valor",
                       title="Gasto Mensal com Uber",
                       labels={"Mês":"Meses",
                               "Valor":"Valor Gasto (R$)"},
                        color_discrete_sequence=["purple"],
                               markers=True)
    
    fig_uber.update_traces(
    hovertemplate='<b>Mês:</b> %{x}<br><b>Gasto:</b> R$ %{y:,.2f}<extra></extra>'
    )
    fig_uber.update_layout(
    yaxis=dict(
        tickformat=".2f",
        tickprefix="R$ "
    ),
    xaxis_title='Mês',
    yaxis_title='Gasto'
    )
    st.plotly_chart(fig_uber, use_container_width=True)
    st.markdown('--------------')
    gasto_colaborador = df_uber_filtro.groupby("Nome")["Valor da transação em BRL (com tributos)"].sum().reset_index(name="Valor total")
    
    cores_roxo = sequential.Purples[::-1]

    pull = [0.1 if i == 0 else 0 for i in range(len(gasto_colaborador))]
    
    fig_uber_colaborador = px.pie(
        gasto_colaborador,
        names="Nome",
        values="Valor total",
        title="Gasto Individual dos Colaboradores",
        hole= 0.5,
        color_discrete_sequence=cores_roxo[:len(gasto_colaborador)],
        labels={"Nome":"Nome",
                "Valor total": "Gasto Total (R$)"}
    )
    fig_uber_colaborador.update_traces(
    pull=pull,
    textinfo='percent+label+value',
    texttemplate='%{label}<br>%{value:,.2f} (%{percent})',
    hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>',
    marker=dict(line=dict(color='white', width=2))
)

# Melhorar o layout
    fig_uber_colaborador.update_layout(
        title_font_size=20,
        title_x=0.5,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        annotations=[dict(
            text=f"Total: R$ {gasto_colaborador['Valor total'].sum():,.2f}",
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False,
            font=dict(color='purple', size=14)
        )]
    )
    st.plotly_chart(fig_uber_colaborador,use_container_width=True)

    st.markdown("-----------------")

    st.subheader("Consultar um Resumo do Colaborador")

    pessoa_input = st.text_input("Digite o Nome do Colaborador")

    if pessoa_input:


        resultados = df_uber[df_uber["Nome"].str.contains(pessoa_input,case=False,na=False)]

        if not resultados.empty:
            st.subheader(f" Resumo do Colaborador: {pessoa_input.title()}")

            col1, col2, col3, col4,col8 = st.columns(5)

            with col1:
                total_gasto = resultados["Valor da transação em BRL (com tributos)"].sum()
                st.metric("**Total Gasto**", formatar_reais(total_gasto))


            with col2:
                dias_unico = resultados["Data da solicitação (local)"].nunique()
                gasto_medio_diario = total_gasto/ dias_unico if dias_unico > 0 else 0
                st.metric("**Gasto Médio Diário**", formatar_reais(gasto_medio_diario))

            with col3:
                resultados["Ano-Mes"] = resultados["Data da solicitação (local)"].dt.to_period("M")
                meses_unico = resultados["Ano-Mes"].nunique()
                gasto_mensal_medio = total_gasto / meses_unico if meses_unico > 0 else 0
                st.metric("**Gasto Médio Mensal**", formatar_reais(gasto_mensal_medio))

            with col4:
                qtd_solicitacoes = len(resultados)
                st.metric("**Quantidade de Solicitações**", qtd_solicitacoes)

            with col8:
                servico_mais_usado = resultados["Serviço"].mode()
                servico_mais_frequente = servico_mais_usado.iloc[0] if not servico_mais_usado.empty else "Nenhum"
                freq_servico = resultados["Serviço"].value_counts().iloc[0] if not resultados.empty else 0

                st.metric("**Serviço mais utilizado**", servico_mais_frequente)
                st.caption(f"Utilizado {freq_servico} vezes")

            col5, col6, col7 = st.columns(3)

            with col5:
                data_inicial = st.date_input("**Data Inicial**", value= resultados["Data da solicitação (local)"].min())
            with col6:
                data_final = st.date_input("**Data Final**", value=resultados["Data da solicitação (local)"].max())
            resultados_filtrados = resultados[
                (resultados["Data da solicitação (local)"] >= pd.to_datetime(data_inicial)) &
                (resultados["Data da solicitação (local)"] <= pd.to_datetime(data_final))
            ]

            if not resultados_filtrados.empty:

                total_periodo = resultados_filtrados["Valor da transação em BRL (com tributos)"].sum()
                qtd_solicitacoes_individuais = len(resultados_filtrados)
                
                dias_periodo = (pd.to_datetime(data_final) - pd.to_datetime(data_inicial)).days + 1
                dias_com_gasto = resultados_filtrados["Data da solicitação (local)"].nunique()
                gasto_diario_medio = total_periodo / dias_com_gasto if dias_com_gasto > 0 else 0

                meses_periodo = dias_periodo / 30.44
                gasto_mensal_medio = total_periodo / meses_periodo if meses_periodo > 0 else 0

                st.subheader(f"📊 Métricas do Período: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}")

                col1,col2,col3,col4 = st.columns(4)

                with col1:
                    st.metric("💰 Montante Gasto", formatar_reais(total_periodo))
                    st.caption("Total no Período")

                with col2:
                    st.metric("Solicitações", qtd_solicitacoes_individuais)
                    st.caption("Quantidade de Solicitações")
                
                with col3:
                    st.metric("📅Gasto Médio Diário", formatar_reais(gasto_diario_medio))
                    st.caption(f"Em {dias_com_gasto} dias com gasto")
                with col4:
                    st.metric("📊Gasto Médio Mensal",formatar_reais(gasto_mensal_medio))
                    st.caption(f"Período de {dias_periodo} dias")

                resultados_filtrados["Valor da transação em BRL (com tributos)"] = resultados_filtrados["Valor da transação em BRL (com tributos)"].apply(formatar_reais)
                st.dataframe(resultados_filtrados, use_container_width=True)
            else:
                st.warning("Nenhuma Transação encontrada neste Período")
            resultados["Valor da transação em BRL (com tributos)"] = resultados["Valor da transação em BRL (com tributos)"].apply(formatar_reais)

        else:
            st.warning("Ops...Nenhum Colaborador encontrado")        