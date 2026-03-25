import streamlit as st
from utilitarios import salvar_dados
from datetime import datetime

def renderizar_financas(financas_extras, ARQUIVO_FINANCAS, vendas, ARQUIVO_VENDAS, estoque, plantios):
    # TUDO DAQUI PARA BAIXO TEM 1 TAB DE DISTÂNCIA DA PAREDE
    st.header("💰 Gestão Financeira e Lucratividade")
    
    # 1. CÁLCULOS GERAIS
    val_armazem = sum([it['qtd'] * it.get('preco', 0) for it in estoque]) if estoque else 0
    val_custos_roca = sum([p.get('custo_total', 0) for p in plantios]) if plantios else 0
    val_extras = sum([f.get('val', 0) for f in financas_extras]) if financas_extras else 0
    val_custos_totais = val_custos_roca + val_extras
    
    val_vendas = sum([v.get('valor_total', 0) for v in vendas]) if vendas else 0
    lucro_total = val_vendas - val_custos_totais
    margem_total = (lucro_total / val_vendas * 100) if val_vendas > 0 else 0

    # 2. MÉTRICAS NO TOPO
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🏠 Valor no Armazém", f"R$ {val_armazem:,.2f}")
    m2.metric("💸 Custos Totais", f"R$ {val_custos_totais:,.2f}")
    m3.metric("💰 Total Vendas", f"R$ {val_vendas:,.2f}")
    m4.metric("📈 Lucro Geral", f"R$ {lucro_total:,.2f}", f"{margem_total:.1f}%")

    st.divider()

    # 3. LANÇAMENTOS E RESULTADOS
    col_l, col_r = st.columns([1, 2])

    with col_l:
        st.subheader("📝 Lançar Movimentação")
        tipo = st.radio("Tipo:", ["Gasto Operacional", "Venda de Safra"], horizontal=True)
        
        with st.form("form_fin"):
            if tipo == "Gasto Operacional":
                f_desc = st.text_input("Descrição (Ex: Diesel, Peão)")
                f_val = st.number_input("Valor R$", min_value=0.0)
                # Só mostra lotes se eles existirem
                lista_lotes = ["Geral"] + [p['cultura'] for p in plantios] if plantios else ["Geral"]
                f_lote = st.selectbox("Vincular a:", lista_lotes)
                
                if st.form_submit_button("Registrar Gasto"):
                    financas_extras.append({
                        "data": datetime.now().strftime("%d/%m"), 
                        "desc": f_desc, "val": f_val, "lote": f_lote
                    })
                    salvar_dados(financas_extras, ARQUIVO_FINANCAS)
                    st.rerun()
            else:
                if not plantios:
                    st.warning("Cadastre um lote na Roça primeiro.")
                else:
                    v_lote = st.selectbox("Lote Vendido:", [p['cultura'] for p in plantios])
                    v_qtd = st.number_input("Qtd Vendida", min_value=0.0)
                    v_val = st.number_input("Valor Total R$", min_value=0.0)
                    
                    if st.form_submit_button("Registrar Venda"):
                        vendas.append({
                            "lote": v_lote, "qtd": v_qtd, 
                            "valor_total": v_val, "data": datetime.now().strftime("%d/%m")
                        })
                        salvar_dados(vendas, ARQUIVO_VENDAS)
                        st.rerun()

    with col_r:
        st.subheader("📊 Resultados por Lote")
        if not plantios:
            st.info("Aguardando lotes para análise.")
        else:
            for p in plantios:
                # Lógica simplificada de exibição
                vendas_lote = sum([v['valor_total'] for v in vendas if v['lote'] == p['cultura']])
                with st.expander(f"Lote: {p['cultura'].upper()}"):
                    st.write(f"Vendas deste lote: R$ {vendas_lote:,.2f}")
                    # Adicione aqui os gráficos que você criou antes