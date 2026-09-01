# --- 1. Constantes e Configurações ---
import os
import sys

# ==============================================================================
# FUNÇÕES PARA ENCONTRAR ARQUIVOS (PARA O .EXE FUNCIONAR)
# ==============================================================================

def resource_path(relative_path: str) -> str:
    """
    Obtém o caminho absoluto para RECURSOS EMBUTIDOS (como a logo).
    Funciona para dev e também quando empacotado com PyInstaller.
    """
    try:
        # PyInstaller cria uma pasta temp e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        # Se não estiver compilado, usa o caminho do script
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


def app_path(relative_path: str) -> str:
    """
    Obtém o caminho absoluto para ARQUIVOS DE DADOS (como o DB).
    Salva na mesma pasta do .exe (e não na pasta temporária).
    """
    if getattr(sys, "frozen", False):
        # Se estiver compilado (frozen), usa o diretório do executável
        base_path = os.path.dirname(sys.executable)
    else:
        # Se estiver em modo de desenvolvimento, usa o diretório do script
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# ==============================================================================

# Nomes dos arquivos (sem caminho)
NOME_ARQUIVO_LOGO = "logo.png"
NOME_BANCO_DADOS = "inscricoes.db"

# --- CAMINHOS DINÂMICOS (FUNCIONAM NO .EXE) ---
# 1. Caminho para a LOGO (lida de dentro do .exe, se empacotado)
CAMINHO_FINAL_LOGO = resource_path(NOME_ARQUIVO_LOGO)
# 2. Caminho para o BANCO DE DADOS (salvo ao lado do .exe)
CAMINHO_BANCO_DADOS = app_path(NOME_BANCO_DADOS)

# Lista de Cidades de Rondônia para o Combobox (sem acentos)
CIDADES_RO = [
    "Alta Floresta D'Oeste", "Ariquemes", "Cabixi", "Cacoal", "Cerejeiras",
    "Colorado do Oeste", "Corumbiara", "Costa Marques", "Espigao D'Oeste",
    "Guajara-Mirim", "Jaru", "Ji-Parana", "Machadinho D'Oeste", "Nova Brasilandia D'Oeste",
    "Ouro Preto do Oeste", "Pimenta Bueno",
    "Porto Velho", "Presidente Medici", "Rio Crespo", "Rolim de Moura",
    "Santa Luzia D'Oeste", "Sao Felipe D'Oeste", "Sao Francisco do Guapore",
    "Sao Miguel do Guapore", "Seringueiras", "Teixeiropolis", "Theobroma",
    "Urupa", "Vale do Anari", "Vale do Paraiso", "Vilhena",
]
CIDADES_RO.sort()

# ------------------------------------------------------------------------------
# Definição das colunas da tabela principal 'pessoas'
# Observação importante:
#   NÃO incluímos 'status_usuario' aqui para não quebrar as posições esperadas
#   nos SELECTs atuais. Essa coluna é criada por migração e manipulada
#   separadamente no INSERT/UPDATE/SELECT quando necessário.
# ------------------------------------------------------------------------------
COLUNAS_PESSOAS = [
    "nome", "nascimento", "idade", "genero", "cpf", "rg", "endereco",
    "bairro", "cidade", "estado", "telefone", "celular", "email",
    "peso", "altura", "responsavel",
]

# ------------------------------------------------------------------------------
# Campos binários (SEPARADOS)
# Inclui SCFV como benefício adicional
# ------------------------------------------------------------------------------
CAMPOS_BENEFICIOS = ["bolsa_familia", "cesta_basica", "scfv"]
NOMES_BENEFICIOS = ["Bolsa Família", "Cesta Básica", "SCFV"]

CAMPOS_PROJETOS = ["futebol", "judo", "jiu_jitsu", "leitura"]
NOMES_PROJETOS = ["Futebol", "Judô", "Jiu Jitsu", "Leitura"]

# ------------------------------------------------------------------------------
# Opções para Situação do usuário (usadas na GUI e relatórios)
# ------------------------------------------------------------------------------
STATUS_USUARIO_OPCOES = ("Ativo", "Inativo")

# ------------------------------------------------------------------------------
# Colunas de exibição na Treeview (aba Consulta/Edição)
# ------------------------------------------------------------------------------
COLUNAS_TREEVIEW = (
    "id", "nome", "idade", "genero", "cidade", "cpf", "celular", "beneficios", "projetos"
)
