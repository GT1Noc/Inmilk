import streamlit as st
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

# Formatação de reais
def format_brl(value):
    try:
        s = f"{value:,.2f}"
        parts = s.split('.')
        parts[0] = parts[0].replace(',', '.')
        return f"R$ {parts[0]},{parts[1]}"
    except:
        return ""

# Função para gerar PDF em memória usando ReportLab
def gerar_pdf_reportlab(dados_entradas: dict, dados_saidas: dict):
    """
    Gera um PDF em BytesIO com as tabelas de Entradas e Saídas e cabeçalho/rodapé.
    'dados_entradas' e 'dados_saidas' são dicionários com chave=str e valor=str (já formatados).
    """
    buffer = BytesIO()
    # Configura documento: A4 com margens padrão
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    # Ajustar estilo do título
    style_title = styles["Heading1"]
    style_title.alignment = 1  # 0=left,1=center,2=right
    style_title.fontSize = 18

    # Estilo para seções
    style_h3 = styles["Heading3"]
    style_h3.alignment = 0  # esquerda

    # Estilo para parágrafos normais
    style_normal = styles["BodyText"]
    style_normal.fontSize = 10

    story = []
    # Título principal
    story.append(Paragraph("Simulação de Custo-Benefício Inmilk", style_title))
    story.append(Spacer(1, 6))

    # Data/hora de geração
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"<i>Data de geração: {data_hoje}</i>", style_normal))
    story.append(Spacer(1, 12))

    # Entradas
    story.append(Paragraph("Entradas", style_h3))
    story.append(Spacer(1, 6))
    # Montar dados da tabela de entradas: cabeçalho + linhas
    entradas_data = [["Parâmetro", "Valor"]]
    for chave, valor in dados_entradas.items():
        entradas_data.append([chave, valor])
    # Criar Table
    table_entradas = Table(entradas_data, colWidths=[None, None])
    # Definir estilo da tabela
    table_entradas.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#A5D6A7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(table_entradas)
    story.append(Spacer(1, 12))

    # Saídas
    story.append(Paragraph("Saídas", style_h3))
    story.append(Spacer(1, 6))
    saidas_data = [["Métrica", "Valor"]]
    for chave, valor in dados_saidas.items():
        saidas_data.append([chave, valor])
    table_saidas = Table(saidas_data, colWidths=[None, None])
    table_saidas.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#A5D6A7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(table_saidas)
    story.append(Spacer(1, 12))

    # Disclaimer no rodapé
    disclaimer = "Disclaimer: Projeção sujeita a fatores externos como manejo, saúde e clima."
    story.append(Paragraph(f"<i>{disclaimer}</i>", style_normal))

    # Construir documento
    doc.build(story)
    buffer.seek(0)
    return buffer

# Layout da página Streamlit
st.set_page_config(page_title="Calculadora de Custo-Benefício Inmilk", layout="wide")
st.markdown("<h1 style='text-align:center; margin-bottom:20px;'>Calculadora de Custo-Benefício Inmilk</h1>", unsafe_allow_html=True)

# Entradas (texto) com help/tooltips
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
# Preço do leite
preco_leite_raw = st.text_input("Preço do leite (R$/kg)", placeholder="", help="Preço de venda do leite.", key="11")

# Botão para calcular
tabela_gerada = False
if st.button("Calcular"):
    tabela_gerada = True

if tabela_gerada:
    # Validação de preenchimento
    inputs = [
        custo_racao_padrao_raw, consumo_ms_raw, consumo_racao_raw, n_vacas_raw,
        aumento_ingestao_raw, custo_racao_inmilk_raw, custo_ms_raw, producao_atual_raw,
        aumento_gordura_raw, incremento_leite_raw, preco_leite_raw
    ]
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
            # Cálculos principais (mesma lógica anterior)
            custo_total_padrao = consumo_racao * custo_racao_padrao
            custo_total_inmilk = consumo_racao * custo_racao_inmilk
            eficiencia_atual = producao_atual / consumo_ms if consumo_ms != 0 else None
            producao_inmilk = producao_atual + incremento_leite
            eficiencia_inmilk = producao_inmilk / (consumo_ms + aumento_ingestao) if (consumo_ms + aumento_ingestao) != 0 else None
            receita_leite = preco_leite * incremento_leite
            receita_gordura = aumento_gordura * producao_inmilk
            receita_total = receita_leite + receita_gordura
            investimento_adicional = custo_total_inmilk - custo_total_padrao
            custo_adicional_ms = aumento_ingestao * custo_ms
            lucro_liquido = receita_total - investimento_adicional - custo_adicional_ms
            ganho_lote = lucro_liquido * n_vacas

            # Ponto de equilíbrio considerando gordura + leite
            if (preco_leite + aumento_gordura) > 0:
                pe_completo = (investimento_adicional + custo_adicional_ms) / (preco_leite + aumento_gordura) * 1000
            else:
                pe_completo = None
            # ROI
            if (investimento_adicional + custo_adicional_ms) > 0:
                roi = receita_total / (investimento_adicional + custo_adicional_ms)
            else:
                roi = None

            # Exibição de resultados na tela
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
                st.metric("Eficiência atual (kg leite/kg MS)", f"{eficiencia_atual:.2f}" if eficiencia_atual is not None else "-", help="Eficiência antes de Inmilk.")
                st.metric("Ponto de equilíbrio (gordura + leite) vaca/dia", f"{pe_completo:.0f}" if pe_completo is not None else "-", help="Mililitros de leite extra considerando receita de gordura.")
                st.metric("Receita adicional (gordura)", format_brl(receita_gordura), help="Receita extra por maior teor de gordura.")
                st.metric("ROI (x vezes)", f"{roi:.2f}" if roi is not None else "-", help="Multiplicador retorno.")
            with o3:
                st.metric("Investimento adicional", format_brl(investimento_adicional), help="Diferença de custo de ração por vaca.")
                st.metric("Eficiência Inmilk (kg leite/kg MS)", f"{eficiencia_inmilk:.2f}" if eficiencia_inmilk is not None else "-", help="Eficiência com Inmilk.")
                # Ponto de equilíbrio somente leite (sem gordura)
                if preco_leite > 0:
                    pe_leite = (investimento_adicional + custo_adicional_ms) / preco_leite * 1000
                    st.metric("Ponto de equilíbrio (ml leite)", f"{pe_leite:.0f}", help="Leite extra para cobrir custos.")
                else:
                    st.metric("Ponto de equilíbrio (ml leite)", "-", help="Leite extra para cobrir custos.")
                st.metric("Receita total adicional", format_brl(receita_total), help="Soma receitas extras.")
                st.metric("Ganho total do lote", format_brl(ganho_lote), help="Ganho líquido do lote.")

            # Preparar dicionários de texto para PDF
            dados_entradas = {
                "Custo ração padrão": format_brl(custo_racao_padrao),
                "Consumo MS": f"{consumo_ms:.2f} kg/dia",
                "Consumo ração": f"{consumo_racao:.2f} kg/dia",
                "Número vacas": str(n_vacas),
                "Aumento ingestão MS": f"{aumento_ingestao:.2f} kg/dia",
                "Custo ração Inmilk": format_brl(custo_racao_inmilk),
                "Custo MS": format_brl(custo_ms),
                "Produção atual": f"{producao_atual:.2f} kg/dia",
                "Aumento gordura": format_brl(aumento_gordura),
                "Incremento leite": f"{incremento_leite:.2f} kg/dia",
                "Preço leite": format_brl(preco_leite),
            }
            # Formatar saídas em strings
            dados_saidas = {
                "Custo total ração padrão": format_brl(custo_total_padrao),
                "Produção com Inmilk": f"{producao_inmilk:.2f} kg/dia",
                "Custo adicional MS": format_brl(custo_adicional_ms),
                "Receita adicional (leite)": format_brl(receita_leite),
                "Lucro líquido": format_brl(lucro_liquido),
                "Custo total ração Inmilk": format_brl(custo_total_inmilk),
                "Eficiência atual": f"{eficiencia_atual:.2f}" if eficiencia_atual is not None else "-",
                "Ponto equilíbrio (gordura+leite)": f"{pe_completo:.0f} ml" if pe_completo is not None else "-",
                "Receita adicional (gordura)": format_brl(receita_gordura),
                "ROI": f"{roi:.2f}" if roi is not None else "-",
                "Investimento adicional": format_brl(investimento_adicional),
                "Eficiência Inmilk": f"{eficiencia_inmilk:.2f}" if eficiencia_inmilk is not None else "-",
                "Ponto equilíbrio (leite)": f"{pe_leite:.0f} ml" if preco_leite > 0 else "-",
                "Receita total adicional": format_brl(receita_total),
                "Ganho total do lote": format_brl(ganho_lote),
            }

            # Gerar PDF e oferecer download
            pdf_buffer = gerar_pdf_reportlab(dados_entradas, dados_saidas)
            st.download_button(
                "Baixar Relatório em PDF",
                pdf_buffer,
                file_name="relatorio_inmilk.pdf",
                mime="application/pdf"
            )
