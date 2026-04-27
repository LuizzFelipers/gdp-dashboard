import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import os
import gspread
from google.oauth2.service_account import Credentials
import io

# Configuração da página
st.set_page_config(
    page_title="Controle de Estoque Recepção", 
    page_icon="📦", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título da aplicação
st.title("📦 Controle de Estoque - Recepção")
st.markdown("---")

# Opções de armazenamento
st.sidebar.header("⚙️ Configuração de Armazenamento")
modo_armazenamento = st.sidebar.radio(
    "Onde salvar os dados:",
    ["Google Sheets (Recomendado)", "Arquivo Local (Apenas teste)"]
)

# Função para configuração do Google Sheets
def setup_google_sheets():
    st.sidebar.subheader("🔐 Configuração do Google Sheets")
    
    with st.sidebar.expander("Configurar Google Sheets"):
        st.info("""
        Para usar o Google Sheets, você precisa:
        1. Criar uma planilha no Google Sheets
        2. Compartilhar com o e-mail de serviço
        3. Configurar as credenciais de API
        """)
        
        # Upload das credenciais
        credenciais_json = st.file_uploader("Upload do arquivo de credenciais JSON", type="json")
        sheet_url = st.text_input("URL da Planilha Google Sheets")
        
        if st.button("Salvar Configuração"):
            if credenciais_json and sheet_url:
                # Salva as credenciais
                with open("credenciais_google.json", "wb") as f:
                    f.write(credenciais_json.getvalue())
                
                # Extrai o ID da planilha da URL
                if "spreadsheets/d/" in sheet_url:
                    sheet_id = sheet_url.split("spreadsheets/d/")[1].split("/")[0]
                    st.session_state.sheet_id = sheet_id
                    st.session_state.google_sheets_configurado = True
                    st.success("Configuração do Google Sheets salva!")
                else:
                    st.error("URL da planilha inválida")
            else:
                st.error("Preencha todos os campos")

# Função para conectar ao Google Sheets
def conectar_google_sheets():
    try:
        # Escopos necessários
        escopos = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Carrega as credenciais
        credenciais = Credentials.from_service_account_file(
            'credenciais_google.json', 
            scopes=escopos
        )
        
        # Conecta ao Google Sheets
        cliente = gspread.authorize(credenciais)
        
        # Abre a planilha
        planilha = cliente.open_by_key(st.session_state.sheet_id)
        worksheet = planilha.sheet1
        
        return worksheet
    except Exception as e:
        st.error(f"Erro ao conectar com Google Sheets: {e}")
        return None

# Função para carregar dados do Google Sheets
def carregar_google_sheets():
    worksheet = conectar_google_sheets()
    if worksheet:
        try:
            # Obtém todos os dados
            dados = worksheet.get_all_records()
            if dados:
                df = pd.DataFrame(dados)
                return df
            else:
                return pd.DataFrame(columns=[
                    'Nome do colaborador', 'Setor', 'Material', 'Quantidade', 'Mês', 'valor'
                ])
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return pd.DataFrame(columns=[
                'Nome do colaborador', 'Setor', 'Material', 'Quantidade', 'Mês', 'valor'
            ])
    return None

# Função para salvar no Google Sheets
def salvar_google_sheets(df):
    worksheet = conectar_google_sheets()
    if worksheet:
        try:
            # Limpa a planilha existente
            worksheet.clear()
            
            # Adiciona cabeçalhos
            cabecalhos = ['Nome do colaborador', 'Setor', 'Material', 'Quantidade', 'Mês', 'valor']
            worksheet.append_row(cabecalhos)
            
            # Adiciona dados
            for _, row in df.iterrows():
                worksheet.append_row([
                    row['Nome do colaborador'],
                    row['Setor'],
                    row['Material'],
                    row['Quantidade'],
                    row['Mês'],
                    row['valor'] if 'valor' in row else ""
                ])
            
            return True
        except Exception as e:
            st.error(f"Erro ao salvar no Google Sheets: {e}")
            return False
    return False

# Nome do arquivo Excel local
ARQUIVO_EXCEL = "Controle_de_estoque_recepcao.xlsx"

# Função para carregar dados do Excel local
def carregar_excel_local():
    if os.path.exists(ARQUIVO_EXCEL):
        try:
            df = pd.read_excel(ARQUIVO_EXCEL)
            return df
        except Exception as e:
            st.error(f"Erro ao carregar arquivo Excel: {e}")
            return pd.DataFrame(columns=[
                'Nome do colaborador', 'Setor', 'Material', 'Quantidade', 'Mês', 'valor'
            ])
    else:
        return pd.DataFrame(columns=[
            'Nome do colaborador', 'Setor', 'Material', 'Quantidade', 'Mês', 'valor'
        ])

# Função para salvar dados no Excel local
def salvar_excel_local(df):
    try:
        df.to_excel(ARQUIVO_EXCEL, index=False)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar arquivo Excel: {e}")
        return False

# Configuração inicial
if 'google_sheets_configurado' not in st.session_state:
    st.session_state.google_sheets_configurado = False

if 'sheet_id' not in st.session_state:
    st.session_state.sheet_id = None

# Interface de configuração
setup_google_sheets()

# Carrega os dados baseado no modo selecionado
if 'dados_estoque' not in st.session_state:
    if modo_armazenamento == "Google Sheets (Recomendado)" and st.session_state.google_sheets_configurado:
        st.session_state.dados_estoque = carregar_google_sheets()
    else:
        st.session_state.dados_estoque = carregar_excel_local()

# Layout principal (igual ao anterior, mas com lógica de salvamento atualizada)
col1, col2 = st.columns(2)

with col1:
    st.subheader("➕ Novo Registro de Estoque")
        
    with st.form("form_estoque"):
        # [TODO: Manter todos os campos do formulário anteriores]
        colaborador = st.text_input("Nome do colaborador:", max_chars=100)
        setor = st.selectbox("Setor:", ["BackOffice", "TI", "Comercial", "Financeiro", "GG", "Marketing", "Governança", "Processos e Qualidade", "Tesouraria", "Be Civis", "Cordenação Back Office"])
        material = st.selectbox("Material:", ["Pilha AA", "Pilha AAA", "Saco Plástico PP 240mm X 320mm: 50 unidades", "RESMA DE PAPEL A4 - 500FLS", "Post-it Pequeno", "Post-It Grande", "Caderno", "Caneta Azul", "Caneta Preta", "Caneta Vermelha", "Caneta Colorida", "Agenda", "Lápis", "Borracha", "Apontador", "Marca-Texto", "Lapizeira", "Grafite", "Corretivo", "Clip", "Pilha C", "Grampo", "Grampeador", "Apoio de Pé", "Apoio de Notebook", "Papel Timbrado", "COLA EM BASTAO 40G", "TESOUSA", "CURATIVO - JOELHO", "CURATIVO TRANSPARENTE", "FITA CREPE - 12mmX30M", "Álcool em Gel 50g", "Extrator de Grampo Galvanizado", "Envelope Personalizado", "Envelope A4 Saco Kraf Pardo 240x340 cm", "APOIO/SUPORTE DE MONITOR", "Cartão Presente - SPOTIFY PREMIUM", "Etiqueta Adesiva A4 350 - 100 Folhas - 3000 Etiq.", "AGUA COM GAS", "ÁGUA MINERAL 250ML", "REDBUD - ZERO", "LEITE", "REFRIGERANTE - SCHWEPPES", "CERVEJA", "REFRIGERANTE COCA-COLA 310ML", "REFRIGERANTE COCA-COLA ZERO 220ML", "REFRIGERANTE COCA-COLA ZERO 310ML", "REFRIGERANTE FANTA UVA", "REFRIGERANTE GUARANA 350ML", "SUCO 290ML", "PAPEL TIMBRADO", "PAPEL TOALHA", "MÁSCARA", "REABASTECEDOR PARA PINCEL DE QUADRO BRANCO - PRETO", "REABASTECEDOR PARA PINCEL DE QUADRO BRANCO - AZUL", "REABASTECEDOR PARA PINCEL DE QUADRO BRANCO - VERMELHO", "MINI-GRAMPEADOR GENMES P/25FLS CORES DIVERSAS", "PASTA PLASTICA EM L PP 0,15 A4 - TRANSPARENTE", "FITA ADESIVA PP 12MMX30M DUREX HB0041744262 3M PT 10 UM", "FITA CREPE - 12mmX30M", "FITA DUPLA FACE 3M SCOTCH FIXA FORTE FIXAÇÃO EXTREMA - 24mm x 2"])
        quantidade = st.number_input("Quantidade:", min_value=1, max_value=1000, step=1, value=1)
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        mes = st.selectbox("Mês:", meses, index=datetime.now().month-1)
        valor = st.text_input("Valor (opcional, use = para fórmulas):", value="")
            
        submitted = st.form_submit_button("✅ Registrar Movimento")
            
        if submitted:
            if colaborador and material:
                novo_registro = {
                    'Nome do colaborador': colaborador,
                    'Setor': setor,
                    'Material': material,
                    'Quantidade': quantidade,
                    'Mês': mes,
                    'valor': valor if valor else ""
                }
                    
                novo_df = pd.concat([st.session_state.dados_estoque, pd.DataFrame([novo_registro])], ignore_index=True)
                st.session_state.dados_estoque = novo_df
                    
                # Salva no local selecionado
                sucesso = False
                if modo_armazenamento == "Google Sheets (Recomendado)" and st.session_state.google_sheets_configurado:
                    sucesso = salvar_google_sheets(st.session_state.dados_estoque)
                else:
                    sucesso = salvar_excel_local(st.session_state.dados_estoque)
                    
                if sucesso:
                    st.success("✅ Registro salvo com sucesso!")
                    st.balloons()
                else:
                    st.error("❌ Erro ao salvar os dados!")
            else:
                st.error("❌ Preencha todos os campos obrigatórios!")

with col2:
    st.subheader("📊 Estatísticas do Estoque")
    
    if not st.session_state.dados_estoque.empty:
        # [TODO: Manter todas as estatísticas e gráficos anteriores]
        total_itens = st.session_state.dados_estoque['Quantidade'].sum()
        total_registros = len(st.session_state.dados_estoque)
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Total de Itens", f"{total_itens:,}")
        with col2: st.metric("Total de Registros", total_registros)
        with col3: st.metric("Meses com Registros", st.session_state.dados_estoque['Mês'].nunique())
        
        # Gráficos (simplificado para exemplo)
        itens_por_setor = st.session_state.dados_estoque.groupby('Setor')['Quantidade'].sum().reset_index()
        fig = px.bar(itens_por_setor, x='Setor', y='Quantidade', title="Itens por Setor")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para exibir estatísticas.")

# [TODO: Manter o restante da interface de visualização e exclusão de dados]

# Informações na sidebar
with st.sidebar:
    st.header("ℹ️ Status do Armazenamento")
    
    if modo_armazenamento == "Google Sheets (Recomendado)":
        if st.session_state.google_sheets_configurado:
            st.success("✅ Google Sheets configurado")
            st.info(f"Planilha ID: {st.session_state.sheet_id}")
        else:
            st.warning("⚠️ Google Sheets não configurado")
            st.info("Use a seção de configuração acima")
    else:
        st.info("📁 Usando armazenamento local")
        st.warning("⚠️ Dados serão perdidos no reboot")
    
    st.markdown("---")
    st.info("""
    **Para compartilhar com outras pessoas:**
    1. Use o modo Google Sheets
    2. Compartilhe a planilha com os usuários
    3. Todos verão os mesmos dados em tempo real
    """)