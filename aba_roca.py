import streamlit as st
from datetime import datetime
from utilitarios import salvar_dados

def renderizar_operacao_lote(p, i, estoque, plantios, ARQUIVO_PLANTIO, ARQUIVO_ESTOQUE):
    c1, c2, c3 = st.columns([1, 1.2, 1])
    
    with c1:
                    
                    st.subheader(f"🌱 {p['cultura']}")
                    st.caption(f"🧬 {p.get('variedade', '')} | 📐 {p['area']} hc")
                    st.write(f"📅 Plantio: {p['data_plantio']}")
                    
                    
                    # --- CÁLCULO DE DIAS PLANTADO ---
                    try:
                        from datetime import datetime
                        data_str = p['data_plantio']
                        hoje = datetime.now().date()
                        
                        # Tenta formato Ano-Mês-Dia (Padrão do seletor)
                        if '-' in data_str:
                            data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
                        # Tenta formato Dia/Mês/Ano (Padrão manual)
                        else:
                            data_obj = datetime.strptime(data_str, '%d/%m/%Y').date()
                        
                        dias_passados = (hoje - data_obj).days
                        st.info(f"Sua Planta está com {dias_passados} dias")
                    except Exception as e:
                        st.caption(f"Ciclo: Verifique a data ({p['data_plantio']})")

                    if st.button("🗑️ Remover Lote", key=f"del_lote_{i}"):
                        plantios.pop(i)
                        salvar_dados(plantios, ARQUIVO_PLANTIO)
                        st.rerun()

    with c2:
        with st.expander("**Registrar Operação**"):
            # Seletor de Categoria
            tipo_op = st.selectbox("Tipo de Operação:", 
                                ["Insumo (Galpão)", "Mão de Obra (Peão)", "Diesel / Máquina", "Outros"], 
                                key=f"tipo_op_{i}")
            
            # Tamanho da caixa expander
            with st.container(height=102, border=False):
                
                # --- CATEGORIA 1: INSUMOS ---
                if tipo_op == "Insumo (Galpão)":
                    opcoes_produtos = ["Escolha do Galpão..."]
                    if estoque:
                        opcoes_produtos += [f"{item['nome']} ({item['categoria']})" for item in estoque]
                    opcoes_produtos.append(" Compra Direta (Novo Produto)")
                    
                    escolha = st.selectbox("Produto:", opcoes_produtos, key=f"sel_ap_{i}")
                    
                    # --- LÓGICA 1.1: COMPRA DIRETA ---
                    if "Compra Direta" in escolha:
                        data_ap_av = st.date_input("Data:", datetime.now(), key=f"dt_av_{i}")
                        nome_avulso = st.text_input("Nome do Produto:", placeholder="Ex: Inseticida X", key=f"nome_av_{i}")
                        col_un, col_vlr = st.columns(2)
                        unidade_av = col_un.selectbox("Unid:", ["L", "Kg"], key=f"un_av_{i}")
                        preco_base = col_vlr.number_input(f"Preço (R$):", min_value=0.0, step=1.0, key=f"vlr_av_{i}")
                        qtd_av = st.number_input(f"Qtd ({unidade_av}):", min_value=0.0, step=0.100, format="%.3f", key=f"q_av_{i}")

                        txt_btn = "🚀 Confirmar Compra" if data_ap_av <= datetime.now().date() else "📅 Agendar"
                        if st.button(txt_btn, key=f"btn_av_{i}", use_container_width=True):
                            if nome_avulso:
                                dt_f = data_ap_av.strftime('%d/%m/%Y')
                                qtd_txt = f"{qtd_av*1000:g}" if qtd_av < 1 else f"{qtd_av:g}"
                                uni_txt = ("ml" if unidade_av == "L" else "g") if qtd_av < 1 else unidade_av
                                
                                if data_ap_av <= datetime.now().date():
                                    valor_total_av = qtd_av * preco_base
                                    p['custo_total'] = p.get('custo_total', 0) + valor_total_av
                                    p['diario'].append(f"{dt_f}: [COMPRA] {nome_avulso} -> {qtd_txt} {uni_txt}. (R$ {valor_total_av:.2f})")
                                    # Lança no estoque
                                    if not any(item['nome'].lower() == nome_avulso.lower() for item in estoque):
                                        estoque.append({"nome": nome_avulso, "categoria": "Outros", "qtd": -qtd_av, "preco": preco_base, "unidade": unidade_av})
                                        salvar_dados(estoque, ARQUIVO_ESTOQUE)
                                else:
                                    p['diario'].append(f"⏳ {dt_f}: [AGENDADO] {nome_avulso} -> {qtd_txt} {uni_txt}")
                                salvar_dados(plantios, ARQUIVO_PLANTIO)
                                st.rerun()

                    # --- LÓGICA 1.2: PRODUTO DO GALPÃO ---
                    elif "Escolha do Galpão" not in escolha:
                        data_aplicacao = st.date_input("Data:", datetime.now(), key=f"dt_ap_{i}")
                        nome_puro = escolha.split(" (")[0]
                        item_estoque = next((item for item in estoque if item['nome'] == nome_puro), None)
                        unidade_est = item_estoque['unidade'] if item_estoque else "L"
                        qtd_ap = st.number_input(f"Qtd ({unidade_est}):", min_value=0.0, step=0.001, key=f"qtd_ap_{i}")
                        
                        if item_estoque and qtd_ap > item_estoque['qtd']:
                            st.warning(f"⚠️ Saldo insuficiente! Saldo: {item_estoque['qtd']:g}{unidade_est}")

                        txt_btn_est = "🚀 Confirmar Baixa" if data_aplicacao <= datetime.now().date() else "📅 Agendar Uso"
                        if st.button(txt_btn_est, key=f"baixa_ap_{i}", use_container_width=True):
                            if item_estoque:
                                dt_f = data_aplicacao.strftime('%d/%m/%Y')
                                qtd_txt = f"{qtd_ap*1000:g}" if qtd_ap < 1 else f"{qtd_ap:g}"
                                uni_txt = ("ml" if unidade_est == "L" else "g") if qtd_ap < 1 else unidade_est

                                if data_aplicacao <= datetime.now().date():
                                    item_estoque['qtd'] -= qtd_ap
                                    valor_gasto = qtd_ap * item_estoque.get('preco', 0)
                                    p['custo_total'] = p.get('custo_total', 0) + valor_gasto
                                    p['diario'].append(f"{dt_f}: Aplicado {qtd_txt} {uni_txt} de {nome_puro}. (R$ {valor_gasto:.2f})")
                                    salvar_dados(estoque, ARQUIVO_ESTOQUE)
                                else:
                                    p['diario'].append(f"⏳ {dt_f}: [AGENDADO] {nome_puro} -> {qtd_txt} {uni_txt}")
                                salvar_dados(plantios, ARQUIVO_PLANTIO)
                                st.rerun()

                # --- CATEGORIA 2: MÃO DE OBRA ---
                elif tipo_op == "Mão de Obra (Peão)":
                    dt_mo = st.date_input("Data do Serviço:", datetime.now(), key=f"dt_mo_{i}")
                    servico = st.text_input("Descrição:", placeholder="Ex: Capina manual", key=f"srv_mo_{i}")
                    valor_mo = st.number_input("Valor Pago (R$):", min_value=0.0, step=50.0, key=f"vlr_mo_{i}")
                    if st.button("🚀 Registrar Mão de Obra", key=f"btn_mo_{i}", use_container_width=True):
                        dt_f = dt_mo.strftime('%d/%m/%Y')
                        p['custo_total'] = p.get('custo_total', 0) + valor_mo
                        p['diario'].append(f"{dt_f}: [PEÃO] {servico} - R$ {valor_mo:.2f}")
                        salvar_dados(plantios, ARQUIVO_PLANTIO)
                        st.rerun()

                # --- CATEGORIA 3: DIESEL / MÁQUINA ---
                elif tipo_op == "Diesel / Máquina":
                    dt_ds = st.date_input("Data:", datetime.now(), key=f"dt_ds_{i}")
                    operacao = st.text_input("Operação:", placeholder="Ex: Gradagem / Frete", key=f"op_ds_{i}")
                    custo_ds = st.number_input("Custo Estimado (R$):", min_value=0.0, step=10.0, key=f"vlr_ds_{i}")
                    if st.button("🚀 Registrar Custo Máquina", key=f"btn_ds_{i}", use_container_width=True):
                        dt_f = dt_ds.strftime('%d/%m/%Y')
                        p['custo_total'] = p.get('custo_total', 0) + custo_ds
                        p['diario'].append(f"{dt_f}: [DIESEL] {operacao} - R$ {custo_ds:.2f}")
                        salvar_dados(plantios, ARQUIVO_PLANTIO)
                        st.rerun()

    with c3:
        with st.expander("**📝 Diário**"):
            nova_nota = st.text_input("Anotação:", key=f"nota_{i}")
            if st.button("Salvar Nota", key=f"btn_nota_{i}") and nova_nota:
                p['diario'].append(f"{datetime.now().strftime('%d/%m/%Y')}: {nova_nota}")
                salvar_dados(plantios, ARQUIVO_PLANTIO)
                st.rerun()

        with st.expander("Histórico", expanded=False):
            # 1. FUNÇÃO DE ORDENAÇÃO
            def extrair_data_v3(texto):
                try:
                    limpo = texto.replace("⏳","").replace("✅ ", "").replace("📝 ", "").strip()
                    return datetime.strptime(limpo[:10], '%d/%m/%Y')
                except:
                    return datetime(1900, 1, 1)

            lista_diario = p.get('diario', [])
            historico_ordenado = sorted(lista_diario, key=extrair_data_v3, reverse=True)

            with st.container(height=130, border=False):
                st.markdown("""
            <style>
            div[data-testid="column"] button {
                height: 20px !important;
                width: 20px !important;
                padding: 0px !important;
                margin: 0px !important;
                line-height: 20px !important;
                font-size: 12px !important;
                border-radius: 5px !important;
                border: 1px solid rgba(250, 250, 250, 0.2) !important;
            }
            </style>
        """, unsafe_allow_html=True)
                if not historico_ordenado:
                    st.caption("Nenhum registro.")
                
                for idx, nota in enumerate(historico_ordenado):
                    c_txt, c_del = st.columns([0.80, 0.20])
                    
                    with c_txt:
                        if "AGENDADO" in nota:
                            data_e_resto = nota.split(":", 1)
                            if len(data_e_resto) > 8:
                                st.write(f" :orange[{data_e_resto[0]}] :grey[{data_e_resto[1]}]")
                            else:
                                st.write(f":orange[{nota}]")
                        elif "Aplicado" in nota or "COMPRA" in nota:
                            st.caption(f"✅ {nota}")
                        else:
                            st.caption(f"📝 {nota}")
                    
                    with c_del:
                        if st.button("❌", key=f"del_{i}_{idx}_{hash(nota)}", use_container_width=True):
                            # 1. TENTA IDENTIFICAR O PRODUTO E A QTD PARA DEVOLVER
                            # Exemplo de nota: "✅ Aplicado: 10.0 un de Adubo NPK | R$ 500.00"
                            try:
                                if "Aplicado:" in nota:
                                    # Extrai a quantidade e o nome (ajuste conforme o seu formato de texto)
                                    partes = nota.split("Aplicado:")[1].split("|")[0].strip() 
                                    # partes -> "10.0 un de Adubo NPK"
                                    qtd_devolver = float(partes.split(" ")[0])
                                    nome_produto = partes.split(" de ")[1].strip()

                                    # 2. PROCURA O PRODUTO NO ESTOQUE E SOMA DE VOLTA
                                    for item in estoque:
                                        if item['nome'] == nome_produto:
                                            item['qtd'] += qtd_devolver
                                            break
                                    
                                    # Salva o estoque atualizado
                                    from utilitarios import ARQUIVO_ESTOQUE # Garanta que tem o caminho do arquivo
                                    salvar_dados(estoque, ARQUIVO_ESTOQUE)
                            except Exception as e:
                                st.error(f"Erro ao devolver ao estoque: {e}")

                            # 3. ABATE O VALOR FINANCEIRO (Lógica anterior)
                            if "R$" in nota:
                                try:
                                    valor_texto = nota.split("R$")[-1].strip().replace(',', '.')
                                    p['custo_total'] = max(0, p.get('custo_total', 0) - float(valor_texto))
                                except:
                                    pass
                            
                            # 4. REMOVE A NOTA E SALVA A ROÇA
                            p['diario'].remove(nota)
                            salvar_dados(plantios, ARQUIVO_PLANTIO)
                            st.rerun()