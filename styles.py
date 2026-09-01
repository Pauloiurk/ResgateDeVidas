import tkinter as tk
from tkinter import ttk

def apply_custom_styles(root):
    """
    Aplica estilos personalizados e configurações de tema
    para toda a aplicação Tkinter/Ttk.
    """

    style = ttk.Style(root)
    # Tenta um tema mais flexível
    try:
        style.theme_use('clam')
    except tk.TclError:
        style.theme_use('default')

    # ---------------- Paleta ----------------
    COR_FUNDO           = "#FFFFFF"   # fundo principal
    COR_TEXTO           = "#111111"   # texto padrão
    COR_DESTAQUE        = "#005A9C"   # azul institucional
    COR_DESTAQUE_HOVER  = "#007ACC"   # azul hover
    COR_BORDA_INPUT     = "#B5C7D3"   # borda leve de inputs
    COR_SELECT_BG       = "#E6F2FA"   # destaque leve em seleção
    COR_HEADER_BG       = "#0A66B2"   # cabeçalho de tabela
    COR_HEADER_TXT      = "#FFFFFF"   # texto no cabeçalho
    COR_BTN_TXT         = "#FFFFFF"
    COR_BTN_BG          = COR_DESTAQUE
    COR_BTN_BG_ACTIVE   = COR_DESTAQUE_HOVER

    # ------------- Fundos & Labels -------------
    style.configure(".", background=COR_FUNDO, foreground=COR_TEXTO)
    style.configure("TFrame", background=COR_FUNDO)
    style.configure("TLabel", background=COR_FUNDO, foreground=COR_TEXTO)
    style.configure("Large.TLabel", font=("Helvetica", 16, "bold"), background=COR_FUNDO)

    # ------------- Notebook / Abas -------------
    style.configure("TNotebook", background=COR_FUNDO, borderwidth=0)
    style.configure("TNotebook.Tab",
                    font=("Arial", 10, "bold"),
                    padding=(14, 8),
                    background="#F7F9FB")
    style.map("TNotebook.Tab",
              background=[("selected", "#FFFFFF"), ("active", "#FFFFFF")],
              foreground=[("selected", COR_TEXTO)])

    # ------------- Entradas & Combobox ----------
    # Observação: Ttk não possui "border-radius"; focamos em cores e padding
    style.configure("TEntry",
                    padding=6,
                    fieldbackground="#FFFFFF",
                    bordercolor=COR_BORDA_INPUT,
                    lightcolor=COR_DESTAQUE,
                    darkcolor=COR_BORDA_INPUT,
                    relief="flat")
    style.map("TEntry",
              fieldbackground=[("disabled", "#F3F4F6")],
              bordercolor=[("focus", COR_DESTAQUE)],
              lightcolor=[("focus", COR_DESTAQUE)])

    style.configure("TCombobox",
                    padding=4,
                    fieldbackground="#FFFFFF",
                    bordercolor=COR_BORDA_INPUT,
                    arrowcolor=COR_DESTAQUE)
    style.map("TCombobox",
              fieldbackground=[("readonly", "#FFFFFF")],
              bordercolor=[("focus", COR_DESTAQUE)],
              arrowcolor=[("active", COR_DESTAQUE_HOVER)])

    # ------------- Check / Radio ----------------
    style.configure("TCheckbutton", background=COR_FUNDO, foreground=COR_TEXTO, padding=(2, 2))
    style.configure("TRadiobutton", background=COR_FUNDO, foreground=COR_TEXTO, padding=(2, 2))

    # ------------- Botões -----------------------
    # Botão principal (Login, Cadastrar, Salvar, etc.)
    style.configure("Principal.TButton",
                    font=("Helvetica", 11, "bold"),
                    padding=(16, 10),
                    foreground=COR_BTN_TXT,
                    background=COR_BTN_BG,
                    borderwidth=0)
    style.map("Principal.TButton",
              background=[("active", COR_BTN_BG_ACTIVE), ("pressed", COR_DESTAQUE)],
              foreground=[("disabled", "#DDDDDD")])

    # Botão padrão
    style.configure("TButton",
                    font=("Arial", 10),
                    padding=(12, 8),
                    background="#F0F2F5",
                    foreground=COR_TEXTO,
                    borderwidth=0)
    style.map("TButton",
              background=[("active", "#E6E9EF"), ("pressed", "#DDE3EA")])

    # ------------- Treeview (Tabela) ------------
    style.configure("Treeview",
                    background="#FFFFFF",
                    foreground=COR_TEXTO,
                    rowheight=26,
                    fieldbackground="#FFFFFF",
                    bordercolor="#E5E7EB",
                    borderwidth=1)
    style.map("Treeview",
              background=[("selected", COR_SELECT_BG)],
              foreground=[("selected", COR_TEXTO)])

    style.configure("Treeview.Heading",
                    font=("Arial", 10, "bold"),
                    background=COR_HEADER_BG,
                    foreground=COR_HEADER_TXT,
                    bordercolor=COR_HEADER_BG)
    style.map("Treeview.Heading",
              background=[("active", "#0B72C3")])

    # ------------- Scrollbar --------------------
    style.configure("Vertical.TScrollbar",
                    background="#EAECEF",
                    bordercolor="#EAECEF",
                    troughcolor="#F6F7F9")
    style.configure("Horizontal.TScrollbar",
                    background="#EAECEF",
                    bordercolor="#EAECEF",
                    troughcolor="#F6F7F9")

    # ------------- Labelframe -------------------
    style.configure("TLabelframe", background=COR_FUNDO, bordercolor="#E5E7EB")
    style.configure("TLabelframe.Label", background=COR_FUNDO, foreground=COR_DESTAQUE, font=("Arial", 10, "bold"))

    # ------------- Hints úteis ------------------
    # Alternância de linhas na Treeview (zebra):
    #   A zebra em Treeview é aplicada via "tags" por item (no código que insere linhas).
    #   Exemplo de uso no app:
    #       self.tree.tag_configure("oddrow", background="#FAFBFC")
    #       self.tree.tag_configure("evenrow", background="#FFFFFF")
    #       self.tree.insert(..., tags=("oddrow",))  # alternar conforme índice
    #
    # Como seu código atual não usa tags, mantemos apenas o estilo base aqui.
