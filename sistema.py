import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io
from fpdf import FPDF
import tempfile
import os

# Configuração da página
st.set_page_config(
    page_title="Sistema de Reconciliação de Cancelamentos",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Sistema de Reconciliação de Cancelamentos")
st.markdown("Faça upload das planilhas para identificar divergências entre valores calculados e pagos")
st.markdown("---")

def formatar_reais(valor):
    return f"R$ {valor:,.2f}".replace(",","X").replace(".",",").replace("X",".")

# Função para criar relatório PDF
def criar_relatorio_pdf(resultado_df, divergencias_df, calculados_df, pagos_df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Configurações iniciais
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "RELATÓRIO DE RECONCILIAÇÃO DE CANCELAMENTOS", 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, 'C')
    pdf.ln(10)
    
    # Estatísticas gerais
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "ESTATÍSTICAS GERAIS", 0, 1)
    pdf.set_font("Arial", '', 10)
    
    total_registros = len(resultado_df)
    sem_divergencia = len(resultado_df[resultado_df['Tipo_Divergencia'] == 'Sem divergência'])
    com_divergencia = total_registros - sem_divergencia
    
    pdf.cell(0, 8, f"Total de registros: {total_registros}", 0, 1)
    pdf.cell(0, 8, f"Registros sem divergência: {sem_divergencia}", 0, 1)
    pdf.cell(0, 8, f"Registros com divergência: {com_divergencia}", 0, 1)
    pdf.ln(5)
    
    # Detalhes das planilhas
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "DETALHES DAS PLANILHAS", 0, 1)
    pdf.set_font("Arial", '', 10)
    
    pdf.cell(0, 8, f"Planilha de calculados: {len(calculados_df)} registros", 0, 1)
    pdf.cell(0, 8, f"Planilha de pagos: {len(pagos_df)} registros", 0, 1)
    pdf.ln(5)
    
    # Divergências por tipo
    if not divergencias_df.empty:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "DIVERGÊNCIAS POR TIPO", 0, 1)
        pdf.set_font("Arial", '', 10)
        
        divergencia_count = divergencias_df['Tipo_Divergencia'].value_counts()
        for tipo, quantidade in divergencia_count.items():
            pdf.cell(0, 8, f"{tipo}: {quantidade} registro(s)", 0, 1)
            
            if tipo == 'Divergência de valores':
                divergencias_tipo = divergencias_df[divergencias_df['Tipo_Divergencia'] == tipo]
                total_diferenca = divergencias_tipo['Diferenca_Valor'].sum()
                pdf.cell(0, 8, f"  Diferença total: {formatar_reais(total_diferenca)}", 0, 1)
        pdf.ln(5)
        
        # Top 5 maiores divergências
        if 'Diferenca_Valor' in divergencias_df.columns:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "TOP 5 MAIORES DIVERGÊNCIAS", 0, 1)
            pdf.set_font("Arial", '', 10)
            
            top_divergencias = divergencias_df.nlargest(5, 'Diferenca_Valor', keep='all')
            for i, (index, row) in enumerate(top_divergencias.iterrows(), 1):
                pdf.cell(0, 8, f"{i}. {row['Cliente']} - {formatar_reais(row['Diferenca_Valor'])}", 0, 1)
    
    else:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "NENHUMA DIVERGÊNCIA ENCONTRADA", 0, 1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, "As planilhas estão perfeitamente reconciliadas.", 0, 1)
    
    pdf.ln(10)
    
    # Rodapé
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Relatório gerado automaticamente pelo Sistema de Reconciliação de Cancelamentos", 0, 1, 'C')
    
    return pdf

# Função para validar as planilhas
def validar_planilha(df, tipo):
    colunas_obrigatorias = {
        'calculados': ['ID_Cliente', 'Cliente', 'Valor_Calculado'],
        'pagos': ['ID_Cliente', 'Cliente', 'Valor_Pago', 'Data_Pagamento']
    }
    
    colunas_faltantes = []
    for coluna in colunas_obrigatorias[tipo]:
        if coluna not in df.columns:
            colunas_faltantes.append(coluna)
    
    return colunas_faltantes

# Função para processar e reconciliar as planilhas
def reconciliar_planilhas(calculados_df, pagos_df):
    calculados_df['ID_Cliente'] = calculados_df['ID_Cliente'].astype(str)
    pagos_df['ID_Cliente'] = pagos_df['ID_Cliente'].astype(str)
    
    merged_df = pd.merge(
        calculados_df, 
        pagos_df, 
        on=['ID_Cliente', 'Cliente'], 
        how='outer', 
        indicator=True
    )
    
    conditions = [
        (merged_df['_merge'] == 'left_only'),
        (merged_df['_merge'] == 'right_only'),
        (merged_df['_merge'] == 'both') & (merged_df['Valor_Calculado'] != merged_df['Valor_Pago'])
    ]
    
    choices = [
        'Calculado mas não pago',
        'Pago mas não calculado', 
        'Divergência de valores'
    ]
    
    merged_df['Tipo_Divergencia'] = np.select(conditions, choices, default='Sem divergência')
    
    merged_df['Diferenca_Valor'] = np.where(
        merged_df['Tipo_Divergencia'] == 'Divergência de valores',
        merged_df['Valor_Pago'] - merged_df['Valor_Calculado'],
        np.nan
    )
    
    return merged_df

# Função para criar dashboard visual
def criar_dashboard_visual(divergencias_df):
    # Dados para o dashboard
    total_divergencias = len(divergencias_df)
    tipos_divergencia = divergencias_df['Tipo_Divergencia'].value_counts()
    
    # Calcular totais financeiros
    if 'Divergência de valores' in tipos_divergencia.index:
        divergencias_valores = divergencias_df[divergencias_df['Tipo_Divergencia'] == 'Divergência de valores']
        total_diferenca = divergencias_valores['Diferenca_Valor'].sum()
        media_diferenca = divergencias_valores['Diferenca_Valor'].mean()
    else:
        total_diferenca = 0
        media_diferenca = 0
    
    # Criar dashboard com subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Distribuição dos Tipos de Divergência', 
            'Valor das Divergências por Cliente',
            'Top 10 Maiores Divergências',
            'Impacto Financeiro das Divergências'
        ),
        specs=[
            [{"type": "pie"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "indicator"}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # Gráfico 1: Pizza com tipos de divergência
    fig.add_trace(
        go.Pie(
            labels=tipos_divergencia.index,
            values=tipos_divergencia.values,
            hole=0.4,
            textinfo='label+percent+value',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Gráfico 2: Barras com valores de divergência
    if not divergencias_df.empty and 'Diferenca_Valor' in divergencias_df.columns:
        fig.add_trace(
            go.Bar(
                x=divergencias_df['Cliente'],
                y=divergencias_df['Diferenca_Valor'],
                marker_color=np.where(divergencias_df['Diferenca_Valor'] < 0, 'red', 'green'),
                name='Valor Divergência'
            ),
            row=1, col=2
        )
    
    # Gráfico 3: Top 10 maiores divergências
    if not divergencias_df.empty and 'Diferenca_Valor' in divergencias_df.columns:
        top_divergencias = divergencias_df.nlargest(10, 'Diferenca_Valor', keep='all')
        fig.add_trace(
            go.Bar(
                x=top_divergencias['Cliente'],
                y=top_divergencias['Diferenca_Valor'],
                marker_color=np.where(top_divergencias['Diferenca_Valor'] < 0, 'red', 'green'),
                name='Maiores Divergências'
            ),
            row=2, col=1
        )
    
    # Gráfico 4: Indicador de impacto financeiro
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=total_diferenca,
            number={'prefix': "R$ ", "valueformat": ",.2f"},
            title={"text": "Impacto Financeiro Total"},
            domain={'row': 1, 'column': 1}
        ),
        row=2, col=2
    )
    
    # Atualizar layout
    fig.update_layout(
        height=800,
        title_text="Dashboard de Divergências - Visão Geral",
        showlegend=False
    )
    
    return fig

# Interface para upload das planilhas
col1, col2 = st.columns(2)

with col1:
    st.subheader("Planilha de Valores Calculados")
    uploaded_calculados = st.file_uploader(
        "Faça upload da planilha com os valores calculados",
        type=['xlsx', 'csv'],
        key='calculados'
    )

with col2:
    st.subheader("Planilha de Valores Pagos")
    uploaded_pagos = st.file_uploader(
        "Faça upload da planilha com os valores pagos",
        type=['xlsx','csv'],
        key='pagos'
    )

# Processar as planilhas quando ambas forem carregadas
if uploaded_calculados is not None and uploaded_pagos is not None:
    try:
        # Ler as planilhas
        if uploaded_calculados.name.endswith('.csv'):
            calculados_df = pd.read_csv(uploaded_calculados)
        else:
            calculados_df = pd.read_excel(uploaded_calculados)
        
        if uploaded_pagos.name.endswith('.csv'):
            pagos_df = pd.read_csv(uploaded_pagos)
        else:
            pagos_df = pd.read_excel(uploaded_pagos)
        
        # Validar as planilhas
        colunas_faltantes_calc = validar_planilha(calculados_df, 'calculados')
        colunas_faltantes_pagos = validar_planilha(pagos_df, 'pagos')
        
        if colunas_faltantes_calc or colunas_faltantes_pagos:
            st.error("Erro de validação nas planilhas:")
            if colunas_faltantes_calc:
                st.error(f"Planilha de calculados: faltam colunas {colunas_faltantes_calc}")
            if colunas_faltantes_pagos:
                st.error(f"Planilha de pagos: faltam colunas {colunas_faltantes_pagos}")
        else:
            # Mostrar visualização das planilhas originais
            st.subheader("Visualização das Planilhas Carregadas")
            
            tab1, tab2 = st.tabs(["Valores Calculados", "Valores Pagos"])
            
            with tab1:
                st.dataframe(calculados_df.head(), use_container_width=True)
                st.write(f"Total de registros: {len(calculados_df)}")
            
            with tab2:
                st.dataframe(pagos_df.head(), use_container_width=True)
                st.write(f"Total de registros: {len(pagos_df)}")
            
            # Executar reconciliação
            with st.spinner("Processando reconciliação..."):
                resultado_df = reconciliar_planilhas(calculados_df, pagos_df)
            
            st.success("Reconciliação concluída!")
            st.markdown("---")
            
            # Análise das divergências
            st.subheader("Resultado da Reconciliação")
            
            # Estatísticas resumidas
            total_registros = len(resultado_df)
            sem_divergencia = len(resultado_df[resultado_df['Tipo_Divergencia'] == 'Sem divergência'])
            com_divergencia = total_registros - sem_divergencia
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Registros", total_registros)
            col2.metric("Registros sem Divergência", sem_divergencia)
            col3.metric("Registros com Divergência", com_divergencia, delta=-com_divergencia)
            
            # Filtrar apenas as divergências
            divergencias_df = resultado_df[resultado_df['Tipo_Divergencia'] != 'Sem divergência']
            
            if not divergencias_df.empty:
                # Dashboard Visual
                st.markdown("---")
                st.subheader("📊 Dashboard Visual de Divergências")
                
                # Criar e exibir dashboard
                dashboard_fig = criar_dashboard_visual(divergencias_df)
                st.plotly_chart(dashboard_fig, use_container_width=True)
                
                # Tabela detalhada
                st.subheader("Tabela Detalhada de Divergências")
                st.dataframe(divergencias_df, use_container_width=True)
                
                # Estatísticas por tipo de divergência
                st.subheader("Resumo por Tipo de Divergência")
                divergencia_count = divergencias_df['Tipo_Divergencia'].value_counts()
                
                for tipo, quantidade in divergencia_count.items():
                    with st.expander(f"{tipo} ({quantidade} registros)"):
                        st.write(f"**Quantidade**: {quantidade} registro(s)")
                        
                        if tipo == 'Divergência de valores':
                            divergencias_tipo = divergencias_df[divergencias_df['Tipo_Divergencia'] == tipo]
                            total_diferenca = divergencias_tipo['Diferenca_Valor'].sum()
                            media_diferenca = divergencias_tipo['Diferenca_Valor'].mean()
                            maior_diferenca = divergencias_tipo['Diferenca_Valor'].max()
                            menor_diferenca = divergencias_tipo['Diferenca_Valor'].min()
                            
                            st.write(f"**Diferença total de valor**: {formatar_reais(total_diferenca)}")
                            st.write(f"**Diferença média**: {formatar_reais(media_diferenca)}")
                            st.write(f"**Maior diferença**: {formatar_reais(maior_diferenca)}")
                            st.write(f"**Menor diferença**: {formatar_reais(menor_diferenca)}")
                
                # Opção para baixar relatório
                st.markdown("---")
                st.subheader("📁 Gerar Relatórios")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📊 Gerar Planilha Excel", type="primary"):
                        # Criar arquivo Excel com múltiplas abas
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            # Aba com dados completos
                            resultado_df.to_excel(writer, sheet_name='Dados Completos', index=False)
                            
                            # Aba apenas com divergências
                            divergencias_df.to_excel(writer, sheet_name='Divergências', index=False)
                            
                            # Aba com resumo estatístico
                            resumo_data = []
                            for tipo, quantidade in divergencia_count.items():
                                if tipo == 'Divergência de valores':
                                    divergencias_tipo = divergencias_df[divergencias_df['Tipo_Divergencia'] == tipo]
                                    total_diferenca = divergencias_tipo['Diferenca_Valor'].sum()
                                    resumo_data.append([tipo, quantidade, total_diferenca])
                                else:
                                    resumo_data.append([tipo, quantidade, np.nan])
                            
                            resumo_df = pd.DataFrame(resumo_data, columns=['Tipo_Divergencia', 'Quantidade', 'Diferenca_Total'])
                            resumo_df.to_excel(writer, sheet_name='Resumo', index=False)
                            
                            # Aba com top 10 maiores divergências
                            if 'Diferenca_Valor' in divergencias_df.columns:
                                top_divergencias = divergencias_df.nlargest(10, 'Diferenca_Valor', keep='all')
                                top_divergencias.to_excel(writer, sheet_name='Top 10 Divergências', index=False)
                        
                        output.seek(0)
                        
                        # Download do arquivo
                        st.download_button(
                            label="⬇️ Baixar Relatório em Excel",
                            data=output,
                            file_name=f"relatorio_reconciliacao_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                with col2:
                    if st.button("📄 Gerar Relatório PDF", type="secondary"):
                        # Criar relatório PDF
                        pdf = criar_relatorio_pdf(resultado_df, divergencias_df, calculados_df, pagos_df)
                        
                        # Criar arquivo temporário
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            pdf.output(tmp_file.name)
                            
                            # Ler o conteúdo do arquivo temporário
                            with open(tmp_file.name, 'rb') as f:
                                pdf_bytes = f.read()
                            
                            # Limpar arquivo temporário
                            os.unlink(tmp_file.name)
                        
                        # Download do PDF
                        st.download_button(
                            label="⬇️ Baixar Relatório em PDF",
                            data=pdf_bytes,
                            file_name=f"relatorio_reconciliacao_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                
                st.info("Escolha o formato do relatório:")
                st.write("✅ **Excel**: Dados completos em formato editável")
                st.write("✅ **PDF**: Relatório resumido para impressão e compartilhamento")
                    
            else:
                st.success("✅ Nenhuma divergência encontrada entre as planilhas!")
                
    except Exception as e:
        st.error(f"Erro ao processar as planilhas: {str(e)}")
        st.info("Verifique se os formatos das planilhas estão corretos.")

else:
    st.info("⚠️ Faça upload das duas planilhas para iniciar a reconciliação.")