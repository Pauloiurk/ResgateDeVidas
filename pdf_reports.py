import os
import tempfile
import sqlite3
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from constants import (
    CAMINHO_FINAL_LOGO, COLUNAS_PESSOAS,
    CAMPOS_BENEFICIOS, CAMPOS_PROJETOS,
    NOMES_BENEFICIOS, NOMES_PROJETOS
)
from utils import formatar_genero

# ======================================================================
# Cabeçalho comum dos PDFs
# ======================================================================
def setup_pdf_header(story, title_text):
    styles = getSampleStyleSheet()
    font_bold = 'Arial-Bold' if 'Arial-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'

    style_titulo = ParagraphStyle(
        'TituloPrincipal',
        parent=styles['h1'],
        alignment=1,
        fontSize=20,
        spaceAfter=10,
        fontName=font_bold
    )

    if os.path.exists(CAMINHO_FINAL_LOGO):
        try:
            img = Image(CAMINHO_FINAL_LOGO, width=1.0 * inch, height=1.0 * inch)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 0.1 * inch))
        except Exception:
            pass

    story.append(Paragraph("ASSOCIAÇÃO RESGATE DE VIDAS", style_titulo))

    style_subtitulo = ParagraphStyle(
        'SubtituloPDF',
        parent=styles['h2'],
        alignment=1,
        fontSize=14,
        spaceAfter=15,
        fontName=font_bold,
        textColor=colors.black
    )
    story.append(Paragraph(title_text, style_subtitulo))
    story.append(Spacer(1, 0.1 * inch))


# ======================================================================
# Ficha Individual (usa buscar_dados_por_id => já traz SCFV e status)
# ======================================================================
def gerar_ficha_pdf_func(db_instance, tree_selection):
    """Gera um PDF detalhado para o registro selecionado (Ficha Individual)."""
    if not tree_selection:
        messagebox.showwarning("Aviso", "Selecione um registro na tabela para gerar a ficha.")
        return

    pessoa_id = tree_selection[0]
    dados_dict = db_instance.buscar_dados_por_id(pessoa_id)
    if not dados_dict:
        messagebox.showerror("Erro", "Registro não encontrado.")
        return

    dados_dict["ID"] = pessoa_id

    temp_dir = tempfile.gettempdir()
    filename = os.path.join(temp_dir, f"ficha_cadastral_{dados_dict['ID']}.pdf")

    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        font_name = 'Arial' if 'Arial' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        font_bold = 'Arial-Bold' if 'Arial-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'

        style_nome_pessoa = ParagraphStyle(
            'NomePessoa', parent=styles['Normal'], alignment=0,
            fontSize=14, spaceBefore=10, spaceAfter=5, fontName=font_bold, textColor=colors.blue
        )
        style_dados = ParagraphStyle(
            'DadosPessoa', parent=styles['Normal'], alignment=0,
            fontSize=11, leading=16, fontName=font_name
        )

        story = []
        setup_pdf_header(story, "FICHA CADASTRAL INDIVIDUAL")

        story.append(Paragraph(f"<b>Nome Completo:</b> {dados_dict.get('nome','')}", style_nome_pessoa))

        genero_completo = formatar_genero(dados_dict.get('genero', ''))
        info_pessoal = [
            f"<b>Nascimento:</b> {dados_dict.get('nascimento','')}",
            f"<b>Idade:</b> {dados_dict.get('idade','')}",
            f"<b>Gênero:</b> {genero_completo}",
            f"<b>CPF:</b> {dados_dict.get('cpf','')}",
            f"<b>RG:</b> {dados_dict.get('rg','')}",
            f"<b>Telefone Fixo:</b> {dados_dict.get('telefone','')}",
            f"<b>Celular:</b> {dados_dict.get('celular','')}",
            f"<b>E-mail:</b> {dados_dict.get('email','')}",
            f"<b>Peso (kg):</b> {dados_dict.get('peso','')}",
            f"<b>Altura (cm):</b> {dados_dict.get('altura','')}",
            f"<b>Responsável:</b> {dados_dict.get('responsavel','')}",
            f"<b>Situação do usuário:</b> {dados_dict.get('status_usuario','Ativo')}",
        ]
        for item in info_pessoal:
            story.append(Paragraph(item, style_dados))

        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph(f"<b>Endereço:</b> {dados_dict.get('endereco', '')}", style_dados))
        story.append(Paragraph(f"<b>Bairro:</b> {dados_dict.get('bairro', '')}", style_dados))
        story.append(Paragraph(f"<b>Cidade/UF:</b> {dados_dict.get('cidade', '')} - {dados_dict.get('estado', '')}", style_dados))

        story.append(Spacer(1, 0.3 * inch))

        # Benefícios e Projetos (dinâmico)
        itens_binarios = {}
        for col in CAMPOS_BENEFICIOS + CAMPOS_PROJETOS:
            itens_binarios[col] = dados_dict.get(col, 0)

        projetos = [NOMES_PROJETOS[i] for i, col in enumerate(CAMPOS_PROJETOS) if itens_binarios.get(col, 0) == 1]
        beneficios = [NOMES_BENEFICIOS[i] for i, col in enumerate(CAMPOS_BENEFICIOS) if itens_binarios.get(col, 0) == 1]

        story.append(Paragraph(f"<b>Benefícios Sociais:</b> {', '.join(beneficios) or 'Nenhum'}", style_nome_pessoa))
        story.append(Paragraph(f"<b>Inscrição em Projetos:</b> {', '.join(projetos) or 'Nenhum'}", style_nome_pessoa))

        doc.build(story)
        try:
            os.startfile(filename)  # Windows
        except Exception:
            pass
        messagebox.showinfo("PDF Gerado", f"Ficha cadastral de {dados_dict.get('nome','')} gerada com sucesso e aberta em seu leitor de PDF.")

    except Exception as e:
        messagebox.showerror("Erro ao Gerar PDF", f"Falha ao gerar o PDF. Erro: {e}")


# ======================================================================
# Relatório Geral/Filtrado
# - Filtros de benefícios/projetos: OR inclusivo
# - Filtros de situação: AND com (Ativo/Inativo)
# - SCFV suportado (vem de CAMPOS_BENEFICIOS)
# ======================================================================
def gerar_relatorio_pdf_func(
    db_instance,
    var_filtro_bolsa, var_filtro_cesta, var_filtro_scfv,
    var_filtro_futebol, var_filtro_judo, var_filtro_jiu, var_filtro_leitura,
    var_filtro_status_ativo, var_filtro_status_inativo
):
    """
    Gera um PDF listando os cadastros.

    Lógica:
      - Benefícios/Projetos: 'OR' inclusivo (traz quem tem QUALQUER um dos marcados).
      - Situação: se marcar apenas Ativo ou apenas Inativo, filtra por esse(s) status com 'AND'.
                  Se marcar ambos ou nenhum, não restringe por status.
    """

    # Map com ordem exatamente como CAMPOS_* para manter coerência de nomes
    mapa_filtros_beneficios = {
        "bolsa_familia": {"var": var_filtro_bolsa, "nome": "Bolsa Família"},
        "cesta_basica": {"var": var_filtro_cesta, "nome": "Cesta Básica"},
        "scfv": {"var": var_filtro_scfv, "nome": "SCFV"},
    }
    mapa_filtros_projetos = {
        "futebol": {"var": var_filtro_futebol, "nome": "Futebol"},
        "judo": {"var": var_filtro_judo, "nome": "Judô"},
        "jiu_jitsu": {"var": var_filtro_jiu, "nome": "Jiu Jitsu"},
        "leitura": {"var": var_filtro_leitura, "nome": "Leitura"},
    }

    # Construção do SELECT dinâmico para evitar desalinhamento
    select_pessoas = ", ".join([f"p.{c}" for c in COLUNAS_PESSOAS])
    select_beneficios = ", ".join([f"COALESCE(ba.{c}, 0)" for c in CAMPOS_BENEFICIOS])
    select_projetos = ", ".join([f"COALESCE(pa.{c}, 0)" for c in CAMPOS_PROJETOS])

    query = f"""
        SELECT
            p.id, {select_pessoas},
            {select_beneficios},
            {select_projetos}
        FROM pessoas p
        LEFT JOIN beneficios_ativos ba ON p.id = ba.pessoa_id
        LEFT JOIN projetos_ativos pa ON p.id = pa.pessoa_id
    """

    condicoes_or = []   # qualquer um (benefícios/projetos)
    nomes_filtros = []

    # Benefícios
    for col in CAMPOS_BENEFICIOS:
        item = mapa_filtros_beneficios.get(col)
        if item and item["var"].get():
            condicoes_or.append(f"COALESCE(ba.{col}, 0) = 1")
            nomes_filtros.append(item["nome"])

    # Projetos
    for col in CAMPOS_PROJETOS:
        item = mapa_filtros_projetos.get(col)
        if item and item["var"].get():
            condicoes_or.append(f"COALESCE(pa.{col}, 0) = 1")
            nomes_filtros.append(item["nome"])

    # Situação
    status_ativo = bool(var_filtro_status_ativo.get())
    status_inativo = bool(var_filtro_status_inativo.get())
    condicoes_and = []
    if status_ativo ^ status_inativo:
        # Apenas um marcado => filtra por esse status
        status_alvo = "Ativo" if status_ativo else "Inativo"
        condicoes_and.append("p.status_usuario = ?")
        params_and = [status_alvo]
    elif status_ativo and status_inativo:
        # Ambos => não restringe
        params_and = []
    else:
        # Nenhum => não restringe
        params_and = []

    where_clauses = []
    params = []

    if condicoes_or:
        where_clauses.append("(" + " OR ".join(condicoes_or) + ")")
    if condicoes_and:
        where_clauses.extend(condicoes_and)
        params.extend(params_and)

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    query += " ORDER BY p.nome ASC"

    # Execução
    conn = sqlite3.connect(db_instance.db_nome)
    cursor = conn.cursor()
    cursor.execute(query, params)
    registros = cursor.fetchall()
    conn.close()

    if not registros:
        filtros_str = ", ".join(nomes_filtros) or "Geral (sem filtros de projetos/benefícios)"
        if status_ativo and not status_inativo:
            filtros_str += " | Situação: Ativo"
        elif status_inativo and not status_ativo:
            filtros_str += " | Situação: Inativo"
        messagebox.showinfo("Relatório", f"Nenhum registro encontrado com os filtros selecionados.\n{filtros_str}")
        return

    # Montagem do PDF
    caminho_pdf = os.path.join(tempfile.gettempdir(), "Relatorio_Associacao_Resgate_Vidas.pdf")
    doc = SimpleDocTemplate(caminho_pdf, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()
    font_name = 'Arial' if 'Arial' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    font_bold = 'Arial-Bold' if 'Arial-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'

    # Texto de filtros exibido no cabeçalho
    filtros_str = ", ".join(nomes_filtros) or "Geral (sem filtros de projetos/benefícios)"
    if status_ativo and not status_inativo:
        filtros_str += " | Situação: Ativo"
    elif status_inativo and not status_ativo:
        filtros_str += " | Situação: Inativo"
    else:
        filtros_str += " | Situação: (Ativo e Inativo)"

    setup_pdf_header(story, f"RELATÓRIO DE INSCRITOS - Filtros: {filtros_str}")

    style_nome_pessoa = ParagraphStyle('NomePessoa', parent=styles['Normal'], alignment=0,
                                       fontSize=14, spaceBefore=15, spaceAfter=3,
                                       fontName=font_bold, textColor=colors.black)
    style_dados = ParagraphStyle('DadosPessoa', parent=styles['Normal'], alignment=0,
                                 fontSize=11, leading=14, fontName=font_name)

    # Índices fixos para os campos textuais (id + 16 colunas pessoas)
    IDX_ID = 0
    # pessoas começam em 1 e vão até 16 posições (len(COLUNAS_PESSOAS))
    # Benefícios começam no índice 1 + len(COLUNAS_PESSOAS) => 17
    BENEFICIOS_START = 1 + len(COLUNAS_PESSOAS)
    PROJETOS_START = BENEFICIOS_START + len(CAMPOS_BENEFICIOS)

    for row in registros:
        nome = row[1]
        nascimento = row[2]
        idade = row[3]
        genero = formatar_genero(row[4])
        cpf = row[5]
        rg = row[6]
        endereco = row[7]
        bairro = row[8]
        cidade = row[9]
        estado = row[10]
        telefone = row[11]
        celular = row[12]
        email = row[13]
        responsavel = row[16]  # último textual

        story.append(Paragraph(f"{nome}", style_nome_pessoa))

        dados_principais = [
            f"<b>Nascimento:</b> {nascimento} | <b>Idade:</b> {idade} | <b>Gênero:</b> {genero}",
            f"<b>CPF:</b> {cpf} | <b>RG:</b> {rg}",
            f"<b>Endereço:</b> {endereco}, {bairro} | <b>Cidade:</b> {cidade} - {estado}",
            f"<b>Telefone:</b> {telefone} | <b>Celular:</b> {celular}",
            f"<b>E-mail:</b> {email} | <b>Responsável:</b> {responsavel}",
        ]
        for item in dados_principais:
            story.append(Paragraph(item, style_dados))

        # Extrai status binários de forma dinâmica
        beneficios_status = list(row[BENEFICIOS_START:BENEFICIOS_START + len(CAMPOS_BENEFICIOS)])
        projetos_status = list(row[PROJETOS_START:PROJETOS_START + len(CAMPOS_PROJETOS)])

        beneficios_ativos = [NOMES_BENEFICIOS[i] for i, v in enumerate(beneficios_status) if v == 1]
        projetos_ativos = [NOMES_PROJETOS[i] for i, v in enumerate(projetos_status) if v == 1]

        story.append(Paragraph(f"<b>Benefícios:</b> {', '.join(beneficios_ativos) or 'Nenhum'}", style_dados))
        story.append(Paragraph(f"<b>Projetos:</b> {', '.join(projetos_ativos) or 'Nenhum'}", style_dados))
        story.append(Spacer(1, 0.2 * inch))

    try:
        doc.build(story)
        try:
            os.startfile(caminho_pdf)  # Windows
        except Exception:
            pass
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o relatório: {e}")
