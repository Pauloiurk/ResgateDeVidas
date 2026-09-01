import tkinter as tk
import re 
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re # Necessário aqui para evitar erros no Pylance/VS Code

# --- FUNÇÕES DE VALIDAÇÃO E MÁSCARA ---

def formatar_genero(abreviacao: str) -> str:
    """Converte a abreviação do gênero para o nome completo."""
    if abreviacao == 'M':
        return 'Masculino'
    elif abreviacao == 'F':
        return 'Feminino'
    return abreviacao

def validate_number(P):
    """Valida que apenas dígitos ou, em casos como peso/altura, um ponto, sejam inseridos."""
    if P == "":
        return True
    if P.isdigit() or (P.replace('.', '', 1).isdigit() and P.count('.') <= 1):
        return True
    return False

def aplicar_mascara(event, var: tk.StringVar, entry: tk.Entry, formato_tipo: str):
    """Função Única para aplicar máscara e PRESERVAR A POSIÇÃO DO CURSOR."""
    posicao_original = entry.index(tk.INSERT)
    valor_original = var.get()
    conteudo = re.sub(r'[^0-9]', '', valor_original)
    
    formato_novo = ""

    if formato_tipo == 'data':
        if len(conteudo) > 0:
            formato_novo += conteudo[:2]
        if len(conteudo) > 2:
            formato_novo += "/" + conteudo[2:4]
        if len(conteudo) > 4:
            formato_novo += "/" + conteudo[4:8]
        var.set(formato_novo[:10])

    elif formato_tipo == 'cpf':
        if len(conteudo) > 0:
            formato_novo += conteudo[:3]
        if len(conteudo) > 3:
            formato_novo += "." + conteudo[3:6]
        if len(conteudo) > 6:
            formato_novo += "." + conteudo[6:9]
        if len(conteudo) > 9:
            formato_novo += "-" + conteudo[9:11]
        var.set(formato_novo[:14])

    elif formato_tipo == 'fixo':
        if len(conteudo) > 0:
            formato_novo += "(" + conteudo[:2]
        if len(conteudo) > 2:
            formato_novo += ") " + conteudo[2:6]
        if len(conteudo) > 6:
            formato_novo += "-" + conteudo[6:10]
        var.set(formato_novo[:14])
        
    elif formato_tipo == 'celular':
        if len(conteudo) > 0:
            formato_novo += "(" + conteudo[:2]
        if len(conteudo) > 2:
            formato_novo += ") " + conteudo[2:7]
        if len(conteudo) > 7:
            formato_novo += "-" + conteudo[7:11]
        var.set(formato_novo[:15])

    # Correção da posição do cursor 
    entry.icursor(posicao_original + (len(var.get()) - len(valor_original)))
    
# Registro de fonte para o ReportLab
try:
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
except:
    pass