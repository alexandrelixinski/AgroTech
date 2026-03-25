import streamlit as st
from datetime import datetime
from utilitarios import carregar_dados, salvar_dados
from aba_roca import renderizar_operacao_lote
from aba_galpao import renderizar_galpao
from aba_financas import renderizar_financas


# Configurações iniciais
st.set_page_config(page_title="AgroTech Pro", page_icon="🚜", layout="wide")

ARQUIVO_PLANTIO = "meu_plantio.json"
ARQUIVO_ESTOQUE = "meu_estoque.json"
ARQUIVO_VENDAS = "vendas.json"
ARQUIVO_FINANCAS = "minhas_financas.json"

estoque = carregar_dados(ARQUIVO_ESTOQUE)
plantios = carregar_dados(ARQUIVO_PLANTIO)
financas_extras = carregar_dados(ARQUIVO_FINANCAS)
vendas = carregar_dados(ARQUIVO_VENDAS)

aba_roca, aba_galpao, aba_financas = st.tabs(["🚜 Minha Roça", "🏠 Meu Galpão", "💰 Finanças"])
st.write("###")

with aba_roca:
    st.header("Gerenciamento de Safras")
    
    with st.sidebar:
        st.header("🌱 Novo Lote")
        with st.form("form_lote"):
            cultura = st.text_input("Cultura")
            variedade = st.text_input("Variedade")
            area = st.number_input("Hectares", min_value=0.0)
            data_p = st.date_input("Data Plantio", datetime.now())
            if st.form_submit_button("Cadastrar Lote") and cultura:
                plantios.append({
                    "cultura": cultura, "variedade": variedade, "area": area, 
                    "data_plantio": data_p.strftime("%d/%m/%Y"),
                    "diario": [f"{datetime.now().strftime('%d/%m/%Y')}: Lote cadastrado."],
                    "custo_total": 0.0
                })
                salvar_dados(plantios, ARQUIVO_PLANTIO)
                st.rerun()

    # Exibição dos Lotes
    if plantios:
        for i, p in enumerate(plantios):
            with st.container(border=True):
                renderizar_operacao_lote(p, i, estoque, plantios, ARQUIVO_PLANTIO, ARQUIVO_ESTOQUE)
    else:
        st.info("Nenhum lote cadastrado. Use o menu lateral para começar!")
                
# ---------------------------------------------------------
# ABA 2: MEU GALPÃO
# ---------------------------------------------------------
with aba_galpao:
    renderizar_galpao(estoque, ARQUIVO_ESTOQUE)
    
# ---------------------------------------------------------
# ABA 3: FINANÇAS
# ---------------------------------------------------------
with aba_financas:
    renderizar_financas(financas_extras, ARQUIVO_FINANCAS, vendas, ARQUIVO_VENDAS, estoque, plantios)

    
