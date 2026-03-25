import streamlit as st
import plotly.express as px
from utilitarios import salvar_dados

def renderizar_galpao(estoque, ARQUIVO_ESTOQUE):
    busca = ""
    
    # --- CABEÇALHO ---
    with st.container():
        col_patrimonio, col_grafico_pizza, col_gastos = st.columns([1, 1.2, 1])
        
        with col_patrimonio:
            c_aux1, c_aux2 = st.columns(2)
            with c_aux1:
                valor_total = sum([it['qtd'] * it.get('preco', 0) for it in estoque])
                st.write("**Total**")
                st.caption(f"R$ {valor_total:,.2f}")
                st.divider()
                st.write("**Itens Totais**")
                st.caption(f"{len(estoque)} tipos")

            with c_aux2:
                valor_adubos = sum([it['qtd'] * it.get('preco', 0) for it in estoque if it.get('categoria') == "Adubos"])
                st.write("**Adubos**")
                st.caption(f"R$ {valor_adubos:,.2f}")
                st.divider()
                valor_defensivos = sum([it['qtd'] * it.get('preco', 0) for it in estoque if it.get('categoria') == "Defensivos"])
                st.write("**Defensivos**")
                st.caption(f"R$ {valor_defensivos:,.2f}")
                
        with col_grafico_pizza:
            st.write("📊 **Distribuição de Valor**")
            if not estoque:
                st.info("Cadastre itens para gerar o gráfico.")
            else:
                dados_por_categoria = {}
                for item in estoque:
                    cat = item.get('categoria', 'Outros')
                    valor_ocupado = item['qtd'] * item.get('preco', 0)
                    dados_por_categoria[cat] = dados_por_categoria.get(cat, 0) + valor_ocupado

                fig = px.pie(
                    names=list(dados_por_categoria.keys()), 
                    values=list(dados_por_categoria.values()), 
                    hole=0.6,
                    color_discrete_sequence=px.colors.qualitative.Prism
                )
                fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=220,
                                  legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0))
                
                # CORREÇÃO: Apenas um st.plotly_chart com KEY única
                st.plotly_chart(fig, use_container_width=True, key="grafico_principal_estoque")

        with col_gastos:
            st.write("🏆 **Top Itens (Valor)**")
            # Ordena o estoque pelo valor total (Preço * Qtd) do maior para o menor
            estoque_ordenado = sorted(estoque, key=lambda x: x['qtd'] * x.get('preco', 0), reverse=True)[:3]
            
            if not estoque:
                st.caption("Sem dados")
            else:
                for item in estoque_ordenado:
                    valor_item = item['qtd'] * item.get('preco', 0)
                    percentual = (valor_item / valor_total) if valor_total > 0 else 0
                    with st.container():
                        c_n, c_v = st.columns([2, 1])
                        c_n.caption(f"**{item['nome']}**")
                        c_v.write(f"R$ {valor_item:,.0f}")
                        st.progress(percentual)

    st.divider()

    # --- ÁREA DE OPERAÇÃO (INVENTÁRIO) ---
    col_titulo, col_busca, col_botao = st.columns([1.5, 2, 1])
    with col_titulo:
        st.write("### Estoque")
    with col_busca:
        busca = st.text_input("", placeholder="Pesquisar produto...", label_visibility="collapsed")
    with col_botao:
        with st.popover("Novo Insumo", use_container_width=True):
            with st.form("cad_novo"):
                n = st.text_input("Nome")
                cat = st.selectbox("Categoria", ["Sementes", "Adubos", "Diesel", "Defensivos", "Outros"])
                q = st.number_input("Qtd", min_value=0.0)
                p = st.number_input("Preço Unitário", min_value=0.0)
                if st.form_submit_button("Salvar Insumo"):
                    item_existente = next((it for it in estoque if it['nome'].lower() == n.lower() and it['categoria'] == cat), None)
                    
                    if item_existente:
                        item_existente['qtd'] += q
                        item_existente['preco'] = p  # Atualiza para o preço mais recente
                        st.success(f"Quantidade de '{n}' atualizada!")
                    else:
                        # 3. Se não existe, adiciona como novo
                        estoque.append({"nome": n, "categoria": cat, "qtd": q, "preco": p, "unidade": "un"})
                        st.success(f"'{n}' cadastrado com sucesso!")
                    salvar_dados(estoque, ARQUIVO_ESTOQUE)
                    st.rerun()

    if not estoque:
        st.info("O galpão está vazio.")
    else:
        estoque_filtrado = [it for it in estoque if busca.lower() in it['nome'].lower()]
        categorias = sorted(list(set([it.get('categoria', 'Outros') for it in estoque_filtrado])))
        
        if not categorias:
            st.warning("Nenhum item encontrado.")
        else:
            abas = st.tabs(categorias)
            for i, cat in enumerate(categorias):
                with abas[i]:
                    itens_cat = [it for it in estoque_filtrado if it.get('categoria') == cat]
                    h1, h2, h3, h4, h5 = st.columns([2, 1, 1, 1, 0.5])
                    h1.caption("PRODUTO")
                    h2.caption("ESTOQUE")
                    h3.caption("UNITÁRIO")
                    h4.caption("TOTAL")
                    h5.caption("EXCLUIR")

                    for idx, it in enumerate(itens_cat):
                        with st.container(border=True):
                            c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 0.5])
                            status = "🔴" if it['qtd'] <= 5 else "🟢"
                            c1.write(f"{status} **{it['nome']}**")
                            c2.write(f"{it['qtd']} {it.get('unidade', 'un')}")
                            c3.write(f"R$ {it.get('preco', 0):,.2f}")
                            v_total = it.get('preco', 0) * it['qtd']
                            c4.write(f"**R$ {v_total:,.2f}**")
                            with c5:
                                with st.popover("🗑️"):
                                    st.warning("Deseja Excluir?")
                                    if st.button("Sim", key=f"del_{cat}_{idx}", type="primary"):
                                        estoque.remove(it)
                                        salvar_dados(estoque, ARQUIVO_ESTOQUE)
                                        st.rerun()