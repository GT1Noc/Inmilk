import streamlit as st
import pdfkit
from datetime import datetime

# Configuração wkhtmltopdf
WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
PDF_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

# Formatação de reais

def format_brl(value):
    try:
        s = f"{value:,.2f}"
        parts = s.split('.')
        parts[0] = parts[0].replace(',', '.')
        return f"R$ {parts[0]},{parts[1]}"
    except:
        return ""

# Layout da página
st.set_page_config(page_title="Calculadora de Custo-Benefício Inmilk", layout="wide")
st.markdown("<h1 style='text-align:center; margin-bottom:20px;'>Calculadora de Custo-Benefício Inmilk</h1>", unsafe_allow_html=True)

# Entradas (em branco)
st.header("Entradas")
col1, col2 = st.columns(2)
with col1:
    custo_racao_padrao_raw = st.text_input("Custo da ração padrão (R$)", placeholder="", help="Custo unitário da ração sem Inmilk (R$ por kg).", key="1")
    consumo_ms_raw = st.text_input("Consumo de Matéria Seca (kg/dia)", placeholder="", help="Matéria seca consumida por vaca/dia antes do ajuste.", key="2")
    consumo_racao_raw = st.text_input("Consumo de ração por vaca/dia (kg)", placeholder="", help="Ração consumida por vaca/dia.", key="3")
    n_vacas_raw = st.text_input("Número de vacas em lactação", placeholder="", help="Quantidade de vacas em lactação.", key="4")
    aumento_ingestao_raw = st.text_input("Aumento de ingestão MS (kg/dia)", placeholder="", help="Acréscimo de MS/dia com Inmilk.", key="5")
with col2:
    custo_racao_inmilk_raw = st.text_input("Custo da ração Inmilk (R$)", placeholder="", help="Custo da ração com Inmilk.", key="6")
    custo_ms_raw = st.text_input("Custo MS (R$/kg)", placeholder="", help="Custo da matéria seca por kg.", key="7")
    producao_atual_raw = st.text_input("Produção de leite atual (kg/dia)", placeholder="", help="Produção média antes do Inmilk.", key="8")
    aumento_gordura_raw = st.text_input("Aumento gordura (R$/kg leite)", placeholder="", help="Receita extra por teor de gordura.", key="9")
    incremento_leite_raw = st.text_input("Incremento de leite esperado (kg/dia)", placeholder="", help="Ganho de leite/dia com Inmilk.", key="10")
# Preço do leite único e centralizado
preco_leite_raw = st.text_input("Preço do leite (R$/kg)", placeholder="", help="Preço de venda do leite.", key="11")

# Botão para calcular
tabela_gerada = False
if st.button("Calcular"):
    tabela_gerada = True

if tabela_gerada:
    # Validação de preenchimento
    inputs = [custo_racao_padrao_raw, consumo_ms_raw, consumo_racao_raw, n_vacas_raw,
              aumento_ingestao_raw, custo_racao_inmilk_raw, custo_ms_raw, producao_atual_raw,
              aumento_gordura_raw, incremento_leite_raw, preco_leite_raw]
    if any(not s.strip() for s in inputs):
        st.error("Por favor, preencha todos os campos antes de calcular.")
    else:
        try:
            def to_float(s): return float(s.replace(',', '.'))
            custo_racao_padrao = to_float(custo_racao_padrao_raw)
            consumo_ms = to_float(consumo_ms_raw)
            consumo_racao = to_float(consumo_racao_raw)
            n_vacas = int(to_float(n_vacas_raw))
            aumento_ingestao = to_float(aumento_ingestao_raw)
            custo_racao_inmilk = to_float(custo_racao_inmilk_raw)
            custo_ms = to_float(custo_ms_raw)
            producao_atual = to_float(producao_atual_raw)
            aumento_gordura = to_float(aumento_gordura_raw)
            incremento_leite = to_float(incremento_leite_raw)
            preco_leite = to_float(preco_leite_raw)
        except ValueError:
            st.error("Certifique-se de usar apenas números válidos nos campos.")
        else:
            # Cálculos principais
            custo_total_padrao = consumo_racao * custo_racao_padrao
            custo_total_inmilk = consumo_racao * custo_racao_inmilk
            eficiencia_atual = producao_atual / consumo_ms
            producao_inmilk = producao_atual + incremento_leite
            eficiencia_inmilk = producao_inmilk / (consumo_ms + aumento_ingestao)
            receita_leite = preco_leite * incremento_leite
            receita_gordura = aumento_gordura * producao_inmilk
            receita_total = receita_leite + receita_gordura
            investimento_adicional = custo_total_inmilk - custo_total_padrao
            custo_adicional_ms = aumento_ingestao * custo_ms
            lucro_liquido = receita_total - investimento_adicional - custo_adicional_ms
            ganho_lote = lucro_liquido * n_vacas

            # PE considerando preço + gordura
            if preco_leite + aumento_gordura > 0:
                pe_completo = (investimento_adicional + custo_adicional_ms) / (preco_leite + aumento_gordura) * 1000
            else:
                pe_completo = None
            roi = receita_total / (investimento_adicional + custo_adicional_ms) if (investimento_adicional + custo_adicional_ms) > 0 else None

            # Exibição de resultados reorganizada
            st.header("Saídas")
            o1, o2, o3 = st.columns(3)
            with o1:
                st.metric("Custo total ração padrão", format_brl(custo_total_padrao), help="Gasto diário em ração antiga por vaca.")
                st.metric("Produção com Inmilk (kg/dia)", f"{producao_inmilk:.2f}", help="Produção diária prevista com Inmilk.")
                st.metric("Custo adicional MS", format_brl(custo_adicional_ms), help="Custo extra diário de MS por vaca.")
                st.metric("Receita adicional (leite)", format_brl(receita_leite), help="Receita extra por aumento de volume de leite.")
                st.metric("Lucro líquido", format_brl(lucro_liquido), help="Ganho líquido diário por vaca.")
            with o2:
                st.metric("Custo total ração Inmilk", format_brl(custo_total_inmilk), help="Gasto diário em ração com Inmilk por vaca.")
                st.metric("Eficiência atual (kg leite/kg MS)", f"{eficiencia_atual:.2f}", help="Eficiência antes de Inmilk.")
                st.metric("Ponto de equilíbrio (gordura + ml leite) vaca/dia", f"{pe_completo:.0f}" if pe_completo else "-", help="Mililitros de leite extra considerando receita de gordura.")
                st.metric("Receita adicional (gordura)", format_brl(receita_gordura), help="Receita extra por maior teor de gordura.")
                st.metric("ROI (x vezes)", f"{roi:.2f}" if roi else "-", help="Multiplicador retorno.")
            with o3:
                st.metric("Investimento adicional", format_brl(investimento_adicional), help="Diferença de custo de ração por vaca.")
                st.metric("Eficiência Inmilk (kg leite/kg MS)", f"{eficiencia_inmilk:.2f}", help="Eficiência com Inmilk.")
                st.metric("Ponto de equilíbrio (ml leite)", f"{((investimento_adicional + custo_adicional_ms)/preco_leite*1000):.0f}" if preco_leite>0 else "-", help="Leite extra para cobrir custos.")
                st.metric("Receita total adicional", format_brl(receita_total), help="Soma receitas extras.")
                st.metric("Ganho total do lote", format_brl(ganho_lote), help="Ganho líquido do lote.")

            # Geração de PDF otimizada
            data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
            html = f"""
            <html><head><meta charset='utf-8'><style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h2 {{ text-align: center; color: #2E7D32; }}
                .section-title {{ border-bottom: 2px solid #2E7D32; margin-top: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #A5D6A7; }}
            </style><title>Relatório Inmilk</title></head><body>
                <h2>Simulação de Custo-Benefício Inmilk</h2>
                <p><em>Data de geração: {data_hoje}</em></p>
                <h3 class='section-title'>Entradas</h3>
                <table><tr><th>Parâmetro</th><th>Valor</th></tr>
                <tr><td>Custo ração padrão</td><td>{format_brl(custo_racao_padrao)}</td></tr>
                <tr><td>Consumo MS</td><td>{consumo_ms:.2f} kg/dia</td></tr>
                <tr><td>Consumo ração</td><td>{consumo_racao:.2f} kg/dia</td></tr>
                <tr><td>Número vacas</td><td>{n_vacas}</td></tr>
                <tr><td>Aumento ingestão MS</td><td>{aumento_ingestao:.2f} kg/dia</td></tr>
                <tr><td>Custo ração Inmilk</td><td>{format_brl(custo_racao_inmilk)}</td></tr>
                <tr><td>Custo MS</td><td>{format_brl(custo_ms)}</td></tr>
                <tr><td>Produção atual</td><td>{producao_atual:.2f} kg/dia</td></tr>
                <tr><td>Aumento gordura</td><td>{format_brl(aumento_gordura)}</td></tr>
                <tr><td>Incremento leite</td><td>{incremento_leite:.2f} kg/dia</td></tr>
                <tr><td>Preço leite</td><td>{format_brl(preco_leite)}</td></tr>
                </table>
                <h3 class='section-title'>Saídas</h3>
                <table><tr><th>Métrica</th><th>Valor</th></tr>
                <tr><td>Custo total ração padrão</td><td>{format_brl(custo_total_padrao)}</td></tr>
                <tr><td>Produção com Inmilk</td><td>{producao_inmilk:.2f} kg/dia</td></tr>
                <tr><td>Custo adicional MS</td><td>{format_brl(custo_adicional_ms)}</td></tr>
                <tr><td>Receita adicional (leite)</td><td>{format_brl(receita_leite)}</td></tr>
                <tr><td>Lucro líquido</td><td>{format_brl(lucro_liquido)}</td></tr>
                <tr><td>Custo total ração Inmilk</td><td>{format_brl(custo_total_inmilk)}</td></tr>
                <tr><td>Eficiência atual</td><td>{eficiencia_atual:.2f}</td></tr>
                <tr><td>Ponto de equilíbrio (gordura+leite)</td><td>{pe_completo:.0f} ml</td></tr>
                <tr><td>Receita adicional (gordura)</td><td>{format_brl(receita_gordura)}</td></tr>
                <tr><td>ROI</td><td>{f"{roi:.2f}" if roi else "-"}</td></tr>
                <tr><td>Investimento adicional</td><td>{format_brl(investimento_adicional)}</td></tr>
                <tr><td>Eficiência Inmilk</td><td>{eficiencia_inmilk:.2f}</td></tr>
                <tr><td>Ponto de equilíbrio (ml leite)</td><td>{((investimento_adicional + custo_adicional_ms)/preco_leite*1000):.0f} ml</td></tr>
                <tr><td>Receita total adicional</td><td>{format_brl(receita_total)}</td></tr>
                <tr><td>Ganho total do lote</td><td>{format_brl(ganho_lote)}</td></tr>
                </table>
                <p><em>Disclaimer: Projeção sujeita a fatores externos como manejo, saúde e clima.</em></p>
            </body></html>"""

            # Gerar e baixar PDF
            pdf_bytes = pdfkit.from_string(html, False, configuration=PDF_CONFIG, options={'enable-local-file-access': None})
            st.download_button(
                "Baixar Relatório PDF",
                pdf_bytes,
                file_name="relatorio_inmilk.pdf",
                mime="application/pdf"
            )
