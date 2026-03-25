from datetime import datetime, timedelta
import json

def gerar_agenda_do_dia():
    try:
        with open("meu_plantio.json", "r") as f:
            plantios = json.load(f)
    except FileNotFoundError:
        print("Nenhum plantio encontrado.")
        return

    hoje = datetime.now()
    print(f"--- 🚜 RELATÓRIO DE CAMPO - {hoje.strftime('%d/%m/%Y')} ---")

    for p in plantios:
        data_p = datetime.strptime(p['data_plantio'], "%d/%m/%Y")
        dias_passados = (hoje - data_p).days
        
        print(f"\n🌱 Cultura: {p['cultura']} (Área: {p['area_hectares']} ha)")
        print(f"   Idade da planta: {dias_passados} dias")

        # Lógica de I.A. Simples (Regras de Manejo)
        if p['cultura'].lower() == "milho":
            if 15 <= dias_passados <= 22:
                print("   ⚠️ ALERTA: Janela ideal para ADUBAÇÃO DE COBERTURA!")
            elif dias_passados > 110:
                print("   🚜 PREPARAÇÃO: Ponto de colheita se aproximando.")
        
        # Aqui podemos adicionar Soja, Feijão, etc.
    print("\n-------------------------------------------")

# Executa o relatório
gerar_agenda_do_dia()