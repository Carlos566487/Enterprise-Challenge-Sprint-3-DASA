from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, PageBreak)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

doc = SimpleDocTemplate(
    "relatorio_genera_simulado.pdf",
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm
)

styles = getSampleStyleSheet()
W = A4[0] - 4*cm

# Estilos customizados
titulo = ParagraphStyle('titulo', parent=styles['Title'], fontSize=18,
                        textColor=colors.HexColor('#1a3a5c'), spaceAfter=6, alignment=TA_CENTER)
subtitulo = ParagraphStyle('subtitulo', parent=styles['Heading2'], fontSize=13,
                           textColor=colors.HexColor('#1a3a5c'), spaceBefore=14, spaceAfter=4)
corpo = ParagraphStyle('corpo', parent=styles['Normal'], fontSize=9,
                       leading=14, spaceAfter=4, alignment=TA_JUSTIFY)
tecnico = ParagraphStyle('tecnico', parent=styles['Normal'], fontSize=8,
                         leading=12, textColor=colors.HexColor('#333333'), spaceAfter=3)
rodape_style = ParagraphStyle('rodape', parent=styles['Normal'], fontSize=7,
                              textColor=colors.grey, alignment=TA_CENTER)
label = ParagraphStyle('label', parent=styles['Normal'], fontSize=8,
                       textColor=colors.HexColor('#555555'), spaceAfter=2)


def hr(): return HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor('#1a3a5c'), spaceAfter=8, spaceBefore=8)


def hr_light(): return HRFlowable(width="100%", thickness=0.5,
                                  color=colors.lightgrey, spaceAfter=6, spaceBefore=6)


story = []

# ── CABEÇALHO ──────────────────────────────────────────────────────────────
story.append(Paragraph("DASA | GENERA", titulo))
story.append(Paragraph("Relatório de Análise Genômica Personalizada", ParagraphStyle(
    'sub2', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER,
    textColor=colors.HexColor('#2e6da4'), spaceAfter=4)))
story.append(Paragraph("Medicina de Precisão — Diagnóstico Genético Avançado", ParagraphStyle(
    'sub3', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER,
    textColor=colors.grey, spaceAfter=10)))
story.append(hr())

# Dados do paciente
dados_pac = [
    ["Paciente:", "Carlos Eduardo Mendes", "ID Relatório:", "GEN-2024-00847"],
    ["Data de Nascimento:", "14/03/1985", "Data do Exame:", "05/11/2024"],
    ["CPF:", "***.***.***-**", "Data de Emissão:", "12/11/2024"],
    ["Médico Solicitante:", "Dra. Fernanda Lopes CRM/SP 87432",
        "Laboratório:", "Dasa Genômica — SP"],
]
t_pac = Table(dados_pac, colWidths=[3.8*cm, 6.5*cm, 3.8*cm, 5.5*cm])
t_pac.setStyle(TableStyle([
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a3a5c')),
    ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#1a3a5c')),
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
]))
story.append(t_pac)
story.append(hr())

# ── SUMÁRIO EXECUTIVO ──────────────────────────────────────────────────────
story.append(Paragraph("1. SUMÁRIO EXECUTIVO", subtitulo))
story.append(Paragraph(
    "Este relatório apresenta os resultados da análise genômica completa do paciente Carlos Eduardo Mendes, "
    "realizada a partir de amostra de saliva coletada em 05/11/2024. Foram analisadas variantes de nucleotídeo "
    "único (SNPs) em regiões associadas a condições de saúde relevantes, utilizando plataforma de genotipagem "
    "de alta densidade (Illumina GSA v3.0, cobertura de 654.027 SNPs).", corpo))
story.append(Paragraph(
    "A análise identificou <b>7 condições genéticas avaliadas</b>, sendo <b>2 de risco Alto</b>, "
    "<b>3 de risco Médio</b> e <b>2 de risco Baixo</b>. Os resultados devem ser interpretados em conjunto "
    "com histórico clínico e familiar pelo profissional de saúde responsável.", corpo))

sumario_data = [
    ["Condições Analisadas", "Risco Alto", "Risco Médio",
        "Risco Baixo", "Cobertura Genômica"],
    ["7", "2", "3", "2", "654.027 SNPs"],
]
t_sum = Table(sumario_data, colWidths=[W/5]*5)
t_sum.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a5c')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#f8d7da')),
    ('BACKGROUND', (2, 1), (2, 1), colors.HexColor('#fff3cd')),
    ('BACKGROUND', (3, 1), (3, 1), colors.HexColor('#d4edda')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
]))
story.append(t_sum)
story.append(Spacer(1, 10))
story.append(Paragraph(
    "<b>Aviso Legal:</b> Este relatório tem caráter informativo e não substitui consulta médica. "
    "Predisposição genética não determina desenvolvimento de doença. Fatores ambientais e de estilo de vida "
    "influenciam significativamente os desfechos clínicos.", tecnico))
story.append(PageBreak())

# ── RESULTADOS GENÉTICOS ───────────────────────────────────────────────────
story.append(Paragraph("2. RESULTADOS DAS ANÁLISES GENÉTICAS", subtitulo))
story.append(hr_light())

condicoes = [
    {
        "num": "2.1", "doenca": "Diabetes Mellitus Tipo 2", "risco": "ALTO",
        "cor": colors.HexColor('#c0392b'), "bg": colors.HexColor('#f8d7da'),
        "categoria": "Metabolismo e Endocrinologia",
        "marcadores": "RS7903146 (TCF7L2) — alelo T/T | RS12255372 (TCF7L2) — alelo T/G | RS1801282 (PPARG) — alelo C/G",
        "descricao": (
            "A análise identificou homozigose para o alelo de risco T no polimorfismo RS7903146 do gene TCF7L2 "
            "(Transcription Factor 7-Like 2), variante com odds ratio de 1,37 por alelo de risco em populações "
            "europeias (OR combinado: 1,88). Adicionalmente, heterozigose em RS12255372 (TCF7L2) e RS1801282 "
            "(PPARG — Pro12Ala) foram detectadas, conferindo susceptibilidade aumentada à resistência insulínica "
            "e disfunção das células beta pancreáticas. Escore poligênico de risco (PRS): percentil 89."
        ),
        "recomendacao": (
            "Monitoramento semestral de glicemia de jejum e HbA1c. Adoção de dieta hipoglicídica com índice "
            "glicêmico controlado. Prática regular de atividade física aeróbica (≥150 min/semana). "
            "Avaliação com endocrinologista recomendada."
        ),
    },
    {
        "num": "2.2", "doenca": "Carcinoma de Mama (BRCA-relacionado)", "risco": "ALTO",
        "cor": colors.HexColor('#c0392b'), "bg": colors.HexColor('#f8d7da'),
        "categoria": "Oncologia",
        "marcadores": "RS80357906 (BRCA2) — variante patogênica c.5946delT | RS28897696 (BRCA1) — alelo G/A | RS4986850 (BRCA1) — alelo T/T",
        "descricao": (
            "Identificada variante patogênica de perda de função no gene BRCA2 (c.5946delT, p.Ser1982Argfs), "
            "classificada como Patogênica (Classe 5) segundo critérios ACMG/AMP. Esta variante está associada "
            "a risco cumulativo de carcinoma de mama de 45–85% ao longo da vida e risco de carcinoma ovariano "
            "de 10–30%. Variantes adicionais em BRCA1 (RS28897696, RS4986850) com efeito modificador detectadas. "
            "Recomenda-se aconselhamento genético imediato."
        ),
        "recomendacao": (
            "Encaminhamento urgente para aconselhamento genético oncológico. Rastreamento mamográfico anual "
            "a partir dos 25 anos. Ressonância magnética de mama anual. Discussão de estratégias de redução "
            "de risco com oncologista geneticista."
        ),
    },
]

for c in condicoes:
    story.append(Paragraph(f"{c['num']} {c['doenca']}", subtitulo))
    risco_data = [["Nível de Risco", "Categoria", "Marcadores Principais"],
                  [c['risco'], c['categoria'], c['marcadores']]]
    t = Table(risco_data, colWidths=[3*cm, 5*cm, W-8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (0, 1), c['bg']),
        ('TEXTCOLOR', (0, 1), (0, 1), c['cor']),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Descrição Técnica:</b>", label))
    story.append(Paragraph(c['descricao'], tecnico))
    story.append(Paragraph("<b>Recomendação Clínica:</b>", label))
    story.append(Paragraph(c['recomendacao'], tecnico))
    story.append(hr_light())

condicoes2 = [
    {
        "num": "2.3", "doenca": "Hipertensão Arterial Essencial", "risco": "MÉDIO",
        "cor": colors.HexColor('#856404'), "bg": colors.HexColor('#fff3cd'),
        "categoria": "Cardiologia",
        "marcadores": "RS4340 (ACE) — alelo I/D | RS699 (AGT) — alelo M235T | RS5186 (AGTR1) — alelo A/C",
        "descricao": (
            "Heterozigose para o polimorfismo de inserção/deleção RS4340 no gene ACE (Enzima Conversora de "
            "Angiotensina), associado a níveis elevados de ACE sérica no genótipo D/D. Variante RS699 no gene "
            "AGT (Angiotensinogênio) com alelo M235T em heterozigose, relacionada a maior produção de "
            "angiotensinogênio. RS5186 (AGTR1 — receptor AT1) em heterozigose. Escore poligênico: percentil 67."
        ),
        "recomendacao": (
            "Monitoramento regular da pressão arterial (≥2x/ano). Dieta hipossódica (<2g NaCl/dia). "
            "Controle de peso corporal e prática de exercícios físicos regulares. Avaliação cardiológica anual."
        ),
    },
    {
        "num": "2.4", "doenca": "Doença de Alzheimer (início tardio)", "risco": "MÉDIO",
        "cor": colors.HexColor('#856404'), "bg": colors.HexColor('#fff3cd'),
        "categoria": "Neurologia",
        "marcadores": "RS429358 (APOE) — alelo ε3/ε4 | RS7412 (APOE) — alelo C/T | RS11136000 (CLU) — alelo C/T",
        "descricao": (
            "Identificado genótipo APOE ε3/ε4 (heterozigoto), conferindo risco relativo de 3–4x para "
            "desenvolvimento de Doença de Alzheimer de início tardio em comparação ao genótipo ε3/ε3. "
            "O alelo ε4 está presente em aproximadamente 40% dos casos de Alzheimer esporádico. "
            "Variante RS11136000 no gene CLU (Clusterina) com efeito protetor parcial detectada. "
            "Escore poligênico: percentil 72."
        ),
        "recomendacao": (
            "Manutenção de atividade cognitiva regular (leitura, aprendizado). Controle de fatores de risco "
            "cardiovascular. Dieta mediterrânea. Avaliação neurológica periódica a partir dos 50 anos. "
            "Comunicar histórico familiar ao neurologista."
        ),
    },
    {
        "num": "2.5", "doenca": "Doença Celíaca", "risco": "MÉDIO",
        "cor": colors.HexColor('#856404'), "bg": colors.HexColor('#fff3cd'),
        "categoria": "Gastroenterologia / Imunologia",
        "marcadores": "RS2187668 (HLA-DQA1*05) — alelo positivo | RS7454108 (HLA-DQ2.5) — alelo positivo | RS4713586 (IL18RAP) — alelo A/G",
        "descricao": (
            "Presença do haplótipo HLA-DQ2.5 (DQA1*05:01/DQB1*02:01) em heterozigose, presente em "
            "aproximadamente 90–95% dos pacientes com doença celíaca. A presença isolada do haplótipo "
            "confere predisposição, mas não determina o desenvolvimento da doença (penetrância ~3%). "
            "Variante RS4713586 em IL18RAP com efeito modulador da resposta inflamatória intestinal."
        ),
        "recomendacao": (
            "Atenção a sintomas gastrointestinais persistentes (diarreia, distensão, má absorção). "
            "Sorologia para anticorpos anti-transglutaminase (tTG-IgA) em caso de sintomas. "
            "Não iniciar dieta isenta de glúten sem diagnóstico confirmado por biópsia intestinal."
        ),
    },
    {
        "num": "2.6", "doenca": "Trombofilia Hereditária (Fator V de Leiden)", "risco": "BAIXO",
        "cor": colors.HexColor('#155724'), "bg": colors.HexColor('#d4edda'),
        "categoria": "Hematologia",
        "marcadores": "RS6025 (F5 — Fator V Leiden) — alelo G/G (wild-type) | RS1799963 (F2 — Protrombina G20210A) — alelo G/G",
        "descricao": (
            "Ausência da mutação Fator V Leiden (RS6025, G1691A) — genótipo wild-type G/G identificado. "
            "Ausência da mutação de protrombina G20210A (RS1799963) — genótipo wild-type G/G. "
            "Sem evidência de variantes patogênicas nos genes MTHFR, PROC e PROS1 analisados. "
            "Risco de tromboembolismo venoso dentro dos parâmetros populacionais basais."
        ),
        "recomendacao": (
            "Sem restrições específicas relacionadas a trombofilia hereditária. Manter hidratação adequada "
            "em viagens longas. Informar médico sobre resultado antes de uso de anticoncepcionais hormonais."
        ),
    },
    {
        "num": "2.7", "doenca": "Intolerância à Lactose (tipo adulto)", "risco": "BAIXO",
        "cor": colors.HexColor('#155724'), "bg": colors.HexColor('#d4edda'),
        "categoria": "Nutrigenômica",
        "marcadores": "RS4988235 (MCM6/LCT) — alelo C/T (persistência parcial) | RS182549 (MCM6) — alelo C/T",
        "descricao": (
            "Genótipo heterozigoto C/T para RS4988235 (região regulatória do gene LCT — Lactase), "
            "associado à persistência parcial da lactase na vida adulta. Indivíduos com este genótipo "
            "geralmente toleram quantidades moderadas de lactose (até 12g/refeição) sem sintomas "
            "significativos. Genótipo homozigoto C/C seria indicativo de não-persistência completa."
        ),
        "recomendacao": (
            "Tolerância moderada a produtos lácteos esperada. Observar sintomas individuais. "
            "Produtos fermentados (iogurte, queijos curados) geralmente bem tolerados. "
            "Suplementação de cálcio não necessária se consumo moderado de laticínios mantido."
        ),
    },
]

for c in condicoes2:
    story.append(Paragraph(f"{c['num']} {c['doenca']}", subtitulo))
    risco_data = [["Nível de Risco", "Categoria", "Marcadores Principais"],
                  [c['risco'], c['categoria'], c['marcadores']]]
    t = Table(risco_data, colWidths=[3*cm, 5*cm, W-8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (0, 1), c['bg']),
        ('TEXTCOLOR', (0, 1), (0, 1), c['cor']),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Descrição Técnica:</b>", label))
    story.append(Paragraph(c['descricao'], tecnico))
    story.append(Paragraph("<b>Recomendação Clínica:</b>", label))
    story.append(Paragraph(c['recomendacao'], tecnico))
    story.append(hr_light())

story.append(PageBreak())

# ── ANCESTRALIDADE ─────────────────────────────────────────────────────────
story.append(Paragraph("3. ANÁLISE DE ANCESTRALIDADE", subtitulo))
story.append(Paragraph(
    "A composição ancestral foi determinada por comparação com painéis de referência de populações globais "
    "(1000 Genomes Project + HGDP), utilizando análise de componentes principais (PCA) e algoritmo ADMIXTURE "
    "com K=7 populações de referência. Os percentuais representam proporções estimadas de ancestralidade "
    "biogeográfica e não correspondem a identidade étnica ou cultural.", corpo))

anc_data = [
    ["Região de Ancestralidade",
        "Percentual (%)", "Intervalo de Confiança (95%)"],
    ["Europa Ibérica (Península Ibérica)", "42,3%", "39,1% – 45,5%"],
    ["Europa do Sul (Itália/Grécia)", "18,7%", "16,2% – 21,2%"],
    ["África Subsaariana (África Ocidental)", "22,1%", "19,4% – 24,8%"],
    ["Ameríndio (América do Sul)", "11,4%", "9,2% – 13,6%"],
    ["Oriente Médio / Norte da África", "3,8%", "2,1% – 5,5%"],
    ["Ásia do Leste", "1,2%", "0,3% – 2,1%"],
    ["Outros / Não determinado", "0,5%", "0,0% – 1,2%"],
]
t_anc = Table(anc_data, colWidths=[8*cm, 4*cm, 7.6*cm])
t_anc.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a5c')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('ALIGN', (1, 0), (2, -1), 'CENTER'),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1),
     [colors.white, colors.HexColor('#f0f4f8')]),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
]))
story.append(t_anc)
story.append(Spacer(1, 8))
story.append(Paragraph(
    "<b>Nota metodológica:</b> A análise de ancestralidade reflete padrões de variação genética em populações "
    "de referência e pode não capturar toda a diversidade genética do paciente. Resultados de ancestralidade "
    "não têm implicações clínicas diretas.", tecnico))
story.append(PageBreak())

# ── METODOLOGIA ────────────────────────────────────────────────────────────
story.append(Paragraph("4. METODOLOGIA E CONTROLE DE QUALIDADE", subtitulo))
story.append(Paragraph(
    "A análise foi realizada utilizando plataforma de genotipagem Illumina Global Screening Array v3.0 "
    "(GSA), com cobertura de 654.027 variantes genômicas distribuídas pelo genoma humano (GRCh38/hg38). "
    "O processo analítico seguiu pipeline bioinformático validado internamente:", corpo))

met_data = [
    ["Etapa", "Ferramenta/Método", "Parâmetro de Qualidade"],
    ["Extração de DNA", "Saliva — kit Oragene OG-500", "Concentração ≥ 50 ng/μL"],
    ["Genotipagem", "Illumina GSA v3.0", "Call rate ≥ 98%"],
    ["Controle de Qualidade", "PLINK v1.9", "MAF ≥ 1%, HWE p > 1×10⁻⁶"],
    ["Imputação", "Michigan Imputation Server (TOPMed r2)", "Rsq ≥ 0,3"],
    ["Análise de Risco",
        "PRSice-2 (Escore Poligênico)", "Baseado em GWAS publicados"],
    ["Ancestralidade", "ADMIXTURE v1.3 + PCA", "K=7, CV error < 0,5%"],
    ["Anotação de Variantes",
        "ANNOVAR + ClinVar (Nov/2024)", "Classificação ACMG/AMP"],
]
t_met = Table(met_data, colWidths=[4.5*cm, 6*cm, 9.1*cm])
t_met.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a5c')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1),
     [colors.white, colors.HexColor('#f0f4f8')]),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
]))
story.append(t_met)
story.append(Spacer(1, 10))

# ── RODAPÉ / ASSINATURA ────────────────────────────────────────────────────
story.append(hr())
story.append(Paragraph(
    "Responsável Técnico: Dr. Ricardo Almeida Souza — CRM/SP 54321 — Especialista em Genética Médica",
    ParagraphStyle('ass', parent=styles['Normal'], fontSize=8, spaceAfter=2)))
story.append(Paragraph(
    "Dasa Genômica Laboratório | CNES: 2078431 | Av. Juruá, 434 — Alphaville, Barueri/SP — CEP 06455-010",
    rodape_style))
story.append(Paragraph(
    "Este documento é confidencial e destinado exclusivamente ao paciente e ao médico solicitante. "
    "Versão do relatório: 3.2.1 | Emitido em: 12/11/2024",
    rodape_style))

doc.build(story)
print("PDF gerado com sucesso: relatorio_genera_simulado.pdf")
