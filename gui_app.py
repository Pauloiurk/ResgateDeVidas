import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, filedialog
import os
import re
from PIL import Image as PilImage, ImageTk

from constants import (
    CIDADES_RO, COLUNAS_TREEVIEW, COLUNAS_PESSOAS,
    CAMPOS_BENEFICIOS, CAMPOS_PROJETOS,
    NOMES_BENEFICIOS, NOMES_PROJETOS,
    CAMINHO_FINAL_LOGO, NOME_ARQUIVO_LOGO,
)
from database import BancoDeDados
from utils import aplicar_mascara, validate_number, formatar_genero
from pdf_reports import gerar_ficha_pdf_func, gerar_relatorio_pdf_func
from styles import apply_custom_styles


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Associação Resgate de Vidas")
        self.geometry("1200x750")

        # Estilos (tema)
        apply_custom_styles(self)

        # ---------------- Variáveis de estado ----------------
        # Cadastro/Edição
        self.genero_var = tk.StringVar()
        self.var_cidade = tk.StringVar()

        # Benefícios (cadastro)
        self.var_bolsa_cadastro = tk.IntVar()
        self.var_cesta_cadastro = tk.IntVar()
        self.var_scfv = tk.IntVar()  # NOVO

        # Projetos (cadastro)
        self.var_futebol = tk.IntVar()
        self.var_judo = tk.IntVar()
        self.var_jiu = tk.IntVar()
        self.var_leitura = tk.IntVar()

        # Situação (cadastro)
        self.var_status_usuario = tk.StringVar(value="Ativo")

        # Filtros relatórios
        self.var_filtro_bolsa = tk.IntVar()
        self.var_filtro_cesta = tk.IntVar()
        self.var_filtro_scfv = tk.IntVar()

        self.var_filtro_futebol = tk.IntVar()
        self.var_filtro_judo = tk.IntVar()
        self.var_filtro_jiu = tk.IntVar()
        self.var_filtro_leitura = tk.IntVar()

        self.var_filtro_status_ativo = tk.IntVar(value=1)
        self.var_filtro_status_inativo = tk.IntVar(value=1)

        # Máscaras
        self.var_nascimento = tk.StringVar()
        self.var_cpf = tk.StringVar()
        self.var_telefone = tk.StringVar()
        self.var_celular = tk.StringVar()

        # Login/Cadastro de usuário do sistema
        self.login_email_var = tk.StringVar()
        self.login_senha_var = tk.StringVar()
        self.cad_nome_var = tk.StringVar()
        self.cad_cpf_var = tk.StringVar()
        self.cad_telefone_var = tk.StringVar()
        self.cad_email_var = tk.StringVar()
        self.cad_senha_var = tk.StringVar()
        self.cad_confirmar_senha_var = tk.StringVar()

        self.db = BancoDeDados()
        self.janela_edicao_aberta = None
        self.dados_originais_edicao = None
        self._edit_fields = {}
        self.tk_logo_login = None

        vcmd = (self.register(validate_number), "%P")
        self.vcmd_number = vcmd

        # Container para login/cadastro
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.mostrar_tela_login()

        # Rodapé
        frame_rodape = ttk.Frame(self)
        frame_rodape.pack(side="bottom", fill="x", pady=5)
        ttk.Label(
            frame_rodape,
            text="Sistema desenvolvido por Paulo Justus Iurk Neto ®\nAtravés do bom uso da inteligência artificial",
            font=("Arial", 8),
            foreground="gray",
            justify="center",
        ).pack(fill="x")

    # -----------------------------------------------------------
    # Utilidades
    # -----------------------------------------------------------
    def _get_logo_path(self, file_name):
        if os.path.exists(CAMINHO_FINAL_LOGO):
            return CAMINHO_FINAL_LOGO
        path_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
        if os.path.exists(path_script):
            return path_script
        return None

    def on_tab_change(self, event):
        # Consulta somente quando o usuário aciona o botão Consultar
        pass

    # -----------------------------------------------------------
    # Login / Cadastro de usuários do sistema
    # -----------------------------------------------------------
    def mostrar_tela_login(self):
        for w in self.container.winfo_children():
            w.destroy()

        frame_login = ttk.Frame(self.container, padding="20")
        frame_login.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        caminho_logo_tk = self._get_logo_path(NOME_ARQUIVO_LOGO)
        if caminho_logo_tk and os.path.exists(caminho_logo_tk):
            try:
                logo_img = PilImage.open(caminho_logo_tk).resize((120, 120))
                self.tk_logo_login = ImageTk.PhotoImage(logo_img)
                ttk.Label(frame_login, image=self.tk_logo_login).grid(row=0, column=0, columnspan=2, pady=(0, 5))
            except Exception:
                pass

        ttk.Label(frame_login, text="ASSOCIAÇÃO RESGATE DE VIDAS", font=("Arial", 14, "bold")).grid(
            row=1, column=0, columnspan=2, pady=(0, 20)
        )

        ttk.Label(frame_login, text="Email:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(frame_login, textvariable=self.login_email_var, width=30).grid(row=2, column=1, pady=5)

        ttk.Label(frame_login, text="Senha:").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(frame_login, textvariable=self.login_senha_var, show="*", width=30).grid(row=3, column=1, pady=5)

        ttk.Button(frame_login, text="Login", command=self.processar_login, style="Principal.TButton").grid(
            row=4, column=0, columnspan=2, pady=15, ipadx=10, sticky="ew"
        )

        frame_cadastro_link = ttk.Frame(frame_login)
        frame_cadastro_link.grid(row=5, column=0, columnspan=2, pady=(10, 5), sticky="ew")
        ttk.Label(frame_cadastro_link, text="Não tem conta?").pack(side="left", padx=(50, 5))
        ttk.Button(frame_cadastro_link, text="Cadastrar", command=self.mostrar_tela_cadastro, width=15).pack(
            side="right", padx=(5, 50)
        )

    def mostrar_tela_cadastro(self):
        for w in self.container.winfo_children():
            w.destroy()

        frame_cadastro = ttk.Frame(self.container, padding="20")
        frame_cadastro.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(frame_cadastro, text="CADASTRO DE NOVO USUÁRIO", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=15
        )

        ttk.Label(frame_cadastro, text="Nome Completo:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(frame_cadastro, textvariable=self.cad_nome_var, width=40).grid(row=1, column=1, pady=2)

        ttk.Label(frame_cadastro, text="CPF:").grid(row=2, column=0, sticky="w", pady=2)
        cpf_entry = ttk.Entry(frame_cadastro, textvariable=self.cad_cpf_var, width=40)
        cpf_entry.grid(row=2, column=1, pady=2)
        cpf_entry.bind("<KeyRelease>", lambda e, w=cpf_entry: aplicar_mascara(e, self.cad_cpf_var, w, "cpf"))

        ttk.Label(frame_cadastro, text="Telefone:").grid(row=3, column=0, sticky="w", pady=2)
        tel_entry = ttk.Entry(frame_cadastro, textvariable=self.cad_telefone_var, width=40)
        tel_entry.grid(row=3, column=1, pady=2)
        tel_entry.bind("<KeyRelease>", lambda e, w=tel_entry: aplicar_mascara(e, self.cad_telefone_var, w, "celular"))

        ttk.Label(frame_cadastro, text="Email:").grid(row=4, column=0, sticky="w", pady=2)
        ttk.Entry(frame_cadastro, textvariable=self.cad_email_var, width=40).grid(row=4, column=1, pady=2)

        ttk.Label(frame_cadastro, text="Senha:").grid(row=5, column=0, sticky="w", pady=2)
        ttk.Entry(frame_cadastro, textvariable=self.cad_senha_var, show="*", width=40).grid(row=5, column=1, pady=2)

        ttk.Label(frame_cadastro, text="Confirmação:").grid(row=6, column=0, sticky="w", pady=2)
        ttk.Entry(frame_cadastro, textvariable=self.cad_confirmar_senha_var, show="*", width=40).grid(
            row=6, column=1, pady=2
        )

        ttk.Button(frame_cadastro, text="Cadastrar", command=self.processar_cadastro, style="Principal.TButton").grid(
            row=7, column=0, columnspan=2, pady=20, ipadx=10
        )
        ttk.Button(frame_cadastro, text="Voltar ao Login", command=self.mostrar_tela_login, width=15).grid(
            row=8, column=0, columnspan=2
        )

    def processar_login(self):
        email = self.login_email_var.get().strip()
        senha = self.login_senha_var.get()
        if self.db.verificar_login(email, senha):
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            self.mostrar_ui_principal()
        else:
            messagebox.showerror("Erro de Login", "Email ou Senha inválidos.")

    def processar_cadastro(self):
        nome = self.cad_nome_var.get().strip()
        cpf = re.sub(r"[^0-9]", "", self.cad_cpf_var.get())
        telefone = re.sub(r"[^0-9]", "", self.cad_telefone_var.get())
        email = self.cad_email_var.get().strip()
        senha = self.cad_senha_var.get()
        confirmar_senha = self.cad_confirmar_senha_var.get()

        if not all([nome, cpf, email, senha, confirmar_senha]):
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return
        if len(cpf) != 11:
            messagebox.showwarning("Aviso", "O CPF deve ter 11 dígitos.")
            return
        if senha != confirmar_senha:
            messagebox.showwarning("Aviso", "As senhas não coincidem.")
            return

        if self.db.inserir_usuario(cpf, nome, telefone, email, senha):
            self.cad_nome_var.set("")
            self.cad_cpf_var.set("")
            self.cad_telefone_var.set("")
            self.cad_email_var.set("")
            self.cad_senha_var.set("")
            self.cad_confirmar_senha_var.set("")
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso! Use suas credenciais para fazer login.")
            self.mostrar_tela_login()

    # -----------------------------------------------------------
    # UI principal (3 abas)
    # -----------------------------------------------------------
    def mostrar_ui_principal(self):
        for w in self.container.winfo_children():
            w.destroy()
        self.container.destroy()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.aba_cadastro = ttk.Frame(self.notebook, padding=10)
        self.aba_consulta = ttk.Frame(self.notebook, padding=10)
        self.aba_relatorios = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.aba_cadastro, text="1. Cadastro")
        self.notebook.add(self.aba_consulta, text="2. Consulta e Edição")
        self.notebook.add(self.aba_relatorios, text="3. Relatórios (PDF)")

        self.criar_aba_cadastro()
        self.criar_aba_consulta()
        self.criar_aba_relatorios()

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    # -----------------------------------------------------------
    # Aba Cadastro
    # -----------------------------------------------------------
    def criar_aba_cadastro(self):
        root_cad = ttk.Frame(self.aba_cadastro, padding=10)
        root_cad.pack(fill="both", expand=True)

        # Header
        header = ttk.Frame(root_cad)
        header.pack(fill="x", pady=(5, 10))
        ttk.Label(header, text="Associação Resgate De Vidas", font=("Arial", 18, "bold")).pack(
            side="left", expand=True
        )

        caminho_logo_tk = self._get_logo_path(NOME_ARQUIVO_LOGO)
        right_logo = ttk.Frame(header)
        right_logo.pack(side="right")
        if caminho_logo_tk and os.path.exists(caminho_logo_tk):
            try:
                logo_img = PilImage.open(caminho_logo_tk).resize((96, 96))
                self.tk_logo_display = ImageTk.PhotoImage(logo_img)
                ttk.Label(right_logo, image=self.tk_logo_display).pack()
            except Exception:
                ttk.Button(right_logo, text="Adicionar Logo", command=self.selecionar_e_salvar_logo).pack(pady=2)
        else:
            ttk.Button(right_logo, text="Adicionar Logo", command=self.selecionar_e_salvar_logo).pack(pady=2)

        # --------- GRID principal com 3 linhas: [form+lado], [botões], [spacer] ----------
        body = ttk.Frame(root_cad)
        body.pack(fill="both", expand=True)

        body.columnconfigure(0, weight=3)   # coluna do formulário
        body.columnconfigure(1, weight=2)   # coluna do painel lateral
        body.rowconfigure(0, weight=0)      # linha do formulário (não expande)
        body.rowconfigure(1, weight=0)      # linha dos botões (fica colada no form)
        body.rowconfigure(2, weight=1)      # <<< SPACER: absorve o espaço sobrando

        # Esquerda - formulário
        frame_form = ttk.LabelFrame(body, text="Dados Pessoais e Inscrição")
        frame_form.grid(row=0, column=0, sticky="nw", padx=(0, 8), pady=5)

        self.entries = {}
        self.var_cidade.set("Ji-Parana")

        form_layout = [
            ("Nome completo:", 0, 0, "nome", None),
            ("Data de Nascimento (DD/MM/AAAA):", 1, 0, "nascimento", self.var_nascimento),
            ("Idade (apenas números):", 1, 2, "idade", self.vcmd_number),
            ("Gênero:", 2, 0, None, None),
            ("CPF (999.999.999-99):", 3, 0, "cpf", self.var_cpf),
            ("RG (apenas números):", 3, 2, "rg", self.vcmd_number),
            ("Endereço:", 4, 0, "endereco", None),
            ("Bairro:", 5, 0, "bairro", None),
            ("Cidade (RO):", 5, 2, "cidade", None),
            ("Estado (RO):", 6, 0, "estado", None),
            ("Telefone Fixo (Padrão: (99) 9999-9999):", 7, 0, "telefone", self.var_telefone),
            ("Celular (Padrão: (99) 99999-9999):", 7, 2, "celular", self.var_celular),
            ("E-mail:", 8, 0, "email", None),
            ("Peso (kg - apenas números):", 9, 0, "peso", self.vcmd_number),
            ("Altura (cm - apenas números):", 9, 2, "altura", self.vcmd_number),
            ("Responsável (menor de idade):", 10, 0, "responsavel", None),
        ]

        for text, row, col, name, validation_or_var in form_layout:
            ttk.Label(frame_form, text=text).grid(row=row, column=col, sticky="w", padx=5, pady=2)
            if name == "cidade":
                cb = ttk.Combobox(frame_form, textvariable=self.var_cidade, values=CIDADES_RO, state="readonly")
                cb.grid(row=row, column=col + 1, sticky="ew", padx=5, pady=2)
                self.entries[name] = cb
            elif name == "estado":
                e = ttk.Entry(frame_form)
                e.insert(0, "RO")
                e.configure(state="readonly", width=5)
                e.grid(row=row, column=col + 1, sticky="w", padx=5, pady=2)
                self.entries[name] = e
            elif name:
                e = ttk.Entry(
                    frame_form, textvariable=validation_or_var if isinstance(validation_or_var, tk.StringVar) else None
                )
                if validation_or_var == self.vcmd_number:
                    e.configure(validate="key", validatecommand=self.register(validate_number))
                if name == "nascimento":
                    e.bind("<KeyRelease>", lambda ev, w=e: aplicar_mascara(ev, self.var_nascimento, w, "data"))
                elif name == "cpf":
                    e.bind("<KeyRelease>", lambda ev, w=e: aplicar_mascara(ev, self.var_cpf, w, "cpf"))
                elif name == "telefone":
                    e.bind("<KeyRelease>", lambda ev, w=e: aplicar_mascara(ev, self.var_telefone, w, "fixo"))
                elif name == "celular":
                    e.bind("<KeyRelease>", lambda ev, w=e: aplicar_mascara(ev, self.var_celular, w, "celular"))
                e.grid(row=row, column=col + 1, sticky="ew", padx=5, pady=2)
                self.entries[name] = e

        # Mesclas
        self.entries["nome"].grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=2)
        self.entries["endereco"].grid(row=4, column=1, columnspan=3, sticky="ew", padx=5, pady=2)
        self.entries["email"].grid(row=8, column=1, columnspan=3, sticky="ew", padx=5, pady=2)
        self.entries["responsavel"].grid(row=10, column=1, columnspan=3, sticky="ew", padx=5, pady=2)

        # Gênero
        ttk.Radiobutton(frame_form, text="Masculino (M)", variable=self.genero_var, value="M").grid(
            row=2, column=1, sticky="w", padx=5
        )
        ttk.Radiobutton(frame_form, text="Feminino (F)", variable=self.genero_var, value="F").grid(
            row=2, column=2, sticky="w", padx=5
        )

        # Direita - painel lateral
        side = ttk.LabelFrame(body, text="Benefícios, Projetos e Situação")
        side.grid(row=0, column=1, sticky="ne", padx=(8, 0), pady=5)

        box_benef = ttk.LabelFrame(side, text="Benefícios Sociais")
        box_benef.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Checkbutton(box_benef, text="Bolsa Família", variable=self.var_bolsa_cadastro).pack(
            anchor="w", padx=6, pady=2
        )
        ttk.Checkbutton(box_benef, text="Cesta Básica", variable=self.var_cesta_cadastro).pack(
            anchor="w", padx=6, pady=2
        )
        ttk.Checkbutton(box_benef, text="SCFV", variable=self.var_scfv).pack(anchor="w", padx=6, pady=2)

        box_proj = ttk.LabelFrame(side, text="Inscrição em Projetos")
        box_proj.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Checkbutton(box_proj, text="Futebol", variable=self.var_futebol).pack(anchor="w", padx=6, pady=2)
        ttk.Checkbutton(box_proj, text="Judô", variable=self.var_judo).pack(anchor="w", padx=6, pady=2)
        ttk.Checkbutton(box_proj, text="Jiu Jitsu", variable=self.var_jiu).pack(anchor="w", padx=6, pady=2)
        ttk.Checkbutton(box_proj, text="Leitura", variable=self.var_leitura).pack(anchor="w", padx=6, pady=2)

        box_status = ttk.LabelFrame(side, text="Situação do Usuário")
        box_status.pack(fill="x", padx=8, pady=(8, 8))
        ttk.Radiobutton(box_status, text="Ativo", variable=self.var_status_usuario, value="Ativo").pack(
            anchor="w", padx=6, pady=2
        )
        ttk.Radiobutton(box_status, text="Inativo", variable=self.var_status_usuario, value="Inativo").pack(
            anchor="w", padx=6, pady=2
        )

        # Botões (CENTRALIZADOS + colados ao formulário)
        frame_botoes = ttk.Frame(body)
        frame_botoes.grid(row=1, column=0, columnspan=2, sticky="n", pady=(12, 4))

        wrap = ttk.Frame(frame_botoes)
        wrap.pack()  # centraliza
        ttk.Button(
            wrap, text="Salvar Cadastro", command=self.salvar_dados, style="Principal.TButton"
        ).pack(side="left", padx=10, ipadx=10, ipady=6)
        ttk.Button(wrap, text="Limpar Campos", command=self.limpar_campos).pack(
            side="left", padx=10, ipadx=10, ipady=6
        )

        # Linha 2 “spacer” absorve o espaço extra (elimina o vão)
        ttk.Frame(body).grid(row=2, column=0, columnspan=2, sticky="nsew")

    def selecionar_e_salvar_logo(self):
        caminho_origem = filedialog.askopenfilename(
            title="Selecione a Logo da Associação",
            filetypes=(("Arquivos de Imagem", "*.png;*.jpg;*.jpeg"), ("Todos os arquivos", "*.*")),
        )
        if not caminho_origem:
            return

        caminho_destino = CAMINHO_FINAL_LOGO
        try:
            os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)
            logo_img = PilImage.open(caminho_origem)
            logo_img.save(caminho_destino)
            messagebox.showinfo("Sucesso", "Logo salva com sucesso!\nReinicie o sistema para atualizar a tela.")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar Logo", f"Não foi possível salvar a logo.\nErro: {e}")

    def coletar_dados_cadastro(self):
        return {
            "nome": self.entries["nome"].get(),
            "nascimento": self.var_nascimento.get(),
            "idade": self.entries["idade"].get(),
            "genero": self.genero_var.get(),
            "cpf": self.var_cpf.get(),
            "rg": self.entries["rg"].get(),
            "endereco": self.entries["endereco"].get(),
            "bairro": self.entries["bairro"].get(),
            "cidade": self.var_cidade.get(),
            "estado": self.entries["estado"].get(),
            "telefone": self.var_telefone.get(),
            "celular": self.var_celular.get(),
            "email": self.entries["email"].get(),
            "peso": self.entries["peso"].get(),
            "altura": self.entries["altura"].get(),
            "responsavel": self.entries["responsavel"].get(),
            # Benefícios
            "bolsa_familia": self.var_bolsa_cadastro.get(),
            "cesta_basica": self.var_cesta_cadastro.get(),
            "scfv": self.var_scfv.get(),
            # Projetos
            "futebol": self.var_futebol.get(),
            "judo": self.var_judo.get(),
            "jiu_jitsu": self.var_jiu.get(),
            "leitura": self.var_leitura.get(),
            # Situação
            "status_usuario": self.var_status_usuario.get(),
        }

    def salvar_dados(self):
        dados = self.coletar_dados_cadastro()
        if not dados.get("nome") or not dados.get("cpf") or not dados.get("cidade"):
            messagebox.showwarning("Aviso", "Os campos Nome, CPF e Cidade são obrigatórios.")
            return

        cpf_dig = re.sub(r"[^0-9]", "", dados.get("cpf", ""))
        if cpf_dig not in ("", None) and len(cpf_dig) != 11:
            messagebox.showwarning("Aviso", "O CPF deve ter 11 dígitos.")
            return

        if self.db.inserir_dados(dados):
            messagebox.showinfo("Sucesso", "Cadastro salvo com sucesso!")
            self.limpar_campos()

    def limpar_campos(self):
        vars_to_clear = [
            self.genero_var,
            self.var_cidade,
            self.var_bolsa_cadastro,
            self.var_cesta_cadastro,
            self.var_scfv,
            self.var_futebol,
            self.var_judo,
            self.var_jiu,
            self.var_leitura,
            self.var_nascimento,
            self.var_cpf,
            self.var_telefone,
            self.var_celular,
            self.var_filtro_futebol,
            self.var_filtro_judo,
            self.var_filtro_jiu,
            self.var_filtro_leitura,
            self.var_filtro_bolsa,
            self.var_filtro_cesta,
            self.var_filtro_scfv,
            self.var_filtro_status_ativo,
            self.var_filtro_status_inativo,
            self.var_status_usuario,
        ]

        for name, widget in self.entries.items():
            if name in ("estado", "cidade"):
                continue
            widget.delete(0, tk.END)

        for var in vars_to_clear:
            if var == self.var_cidade:
                var.set("Ji-Parana")
            elif var == self.var_status_usuario:
                var.set("Ativo")
            elif isinstance(var, tk.StringVar):
                var.set("")
            elif isinstance(var, tk.IntVar):
                var.set(0)

    # -----------------------------------------------------------
    # Aba Consulta e Edição
    # -----------------------------------------------------------
    def criar_aba_consulta(self):
        frame_pesquisa = ttk.Frame(self.aba_consulta)
        frame_pesquisa.pack(fill="x", pady=5)
        ttk.Label(frame_pesquisa, text="Pesquisar (Nome, CPF, Celular, Cidade):").pack(side="left", padx=5)

        self.entry_pesquisa = ttk.Entry(frame_pesquisa)
        self.entry_pesquisa.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_pesquisa.bind("<Return>", self.filtrar_dados)

        ttk.Button(frame_pesquisa, text="Consultar", command=self.filtrar_dados).pack(side="right", padx=10)

        self.tree = ttk.Treeview(self.aba_consulta, columns=COLUNAS_TREEVIEW, show="headings")
        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.editar_dado_atalho)

        headings = {
            "id": "ID",
            "nome": "Nome Completo",
            "idade": "Idade",
            "genero": "Gênero",
            "cidade": "Cidade",
            "cpf": "CPF",
            "celular": "Celular",
            "beneficios": "Benefícios Ativos",
            "projetos": "Projetos Ativos",
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text)

        self.tree.column("id", width=30, anchor="center", stretch=False)
        self.tree.column("idade", width=50, anchor="center", stretch=False)
        self.tree.column("genero", width=70, anchor="center", stretch=False)
        self.tree.column("cpf", width=110, anchor="center", stretch=False)
        self.tree.column("celular", width=110, anchor="center", stretch=False)

        self.tree.column("nome", width=220, anchor="w", stretch=True)
        self.tree.column("cidade", width=120, anchor="center", stretch=True)
        self.tree.column("beneficios", width=220, anchor="center", stretch=True)
        self.tree.column("projetos", width=320, anchor="w", stretch=True)

        frame_consulta_botoes = ttk.Frame(self.aba_consulta)
        frame_consulta_botoes.pack(pady=10)
        ttk.Button(frame_consulta_botoes, text="Excluir Selecionado", command=self.excluir_dado).pack(
            side="left", padx=10, ipadx=10
        )
        ttk.Button(frame_consulta_botoes, text="Editar Selecionado", command=self.editar_dado).pack(
            side="left", padx=10, ipadx=10
        )
        ttk.Button(frame_consulta_botoes, text="Gerar Ficha (PDF)", command=self.gerar_ficha_pdf).pack(
            side="left", padx=10, ipadx=10
        )

    def filtrar_dados(self, event=None):
        filtro = self.entry_pesquisa.get()
        if not filtro.strip():
            messagebox.showwarning("Aviso", "Por favor, insira informações para pesquisar.")
            for item in self.tree.get_children():
                self.tree.delete(item)
            return
        self.listar_dados_na_treeview(filtro)

    def listar_dados_na_treeview(self, filtro=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if filtro is None:
            return

        registros = self.db.listar_todos_dados(filtro)
        # Montagem dinâmica: id + 16 colunas + benefícios + projetos
        qtd_texto = 1 + len(COLUNAS_PESSOAS)
        qtd_benef = len(CAMPOS_BENEFICIOS)
        qtd_proj = len(CAMPOS_PROJETOS)

        for row in registros:
            try:
                id_pessoa = row[0]
                nome = row[1]
                idade = row[3]
                genero_abrev = row[4]
                cidade = row[9]
                cpf = row[5]
                celular = row[12]

                # fatia dinâmica
                bin_start = qtd_texto
                benef_status = row[bin_start : bin_start + qtd_benef]
                proj_status = row[bin_start + qtd_benef : bin_start + qtd_benef + qtd_proj]
            except Exception:
                messagebox.showerror(
                    "Erro de Leitura", "Estrutura do DB diferente do esperado. Verifique o banco ou recadastre."
                )
                return

            beneficios_ativos = [nome for nome, v in zip(NOMES_BENEFICIOS, benef_status) if int(v) == 1]
            projetos_ativos = [nome for nome, v in zip(NOMES_PROJETOS, proj_status) if int(v) == 1]

            genero_completo = formatar_genero(genero_abrev)
            self.tree.insert(
                "",
                "end",
                values=(
                    id_pessoa,
                    nome,
                    idade,
                    genero_completo,
                    cidade,
                    cpf,
                    celular,
                    ", ".join(beneficios_ativos),
                    ", ".join(projetos_ativos),
                ),
            )

    def excluir_dado(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um registro para excluir.")
            return
        item_values = self.tree.item(selected_item, "values")
        pessoa_id = item_values[0]
        nome = item_values[1]
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o cadastro de {nome}?"):
            if self.db.excluir_dado(pessoa_id):
                messagebox.showinfo("Sucesso", "Cadastro excluído com sucesso.")
                filtro_atual = self.entry_pesquisa.get()
                self.listar_dados_na_treeview(filtro_atual)
            else:
                messagebox.showerror("Erro", "Falha ao excluir o cadastro.")

    def editar_dado_atalho(self, event):
        self.editar_dado()

    def editar_dado(self):
        if self.janela_edicao_aberta and self.janela_edicao_aberta.winfo_exists():
            self.janela_edicao_aberta.lift()
            return
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um registro para editar.")
            return
        item_values = self.tree.item(selected_item, "values")
        pessoa_id = item_values[0]
        dados = self.db.buscar_dados_por_id(pessoa_id)
        if dados:
            self.abrir_janela_edicao(pessoa_id, dados)
        else:
            messagebox.showerror("Erro", "Registro não encontrado.")

    def abrir_janela_edicao(self, pessoa_id, dados):
        self.janela_edicao_aberta = Toplevel(self)
        self.janela_edicao_aberta.title(f"Editar Cadastro (ID: {pessoa_id})")
        self.janela_edicao_aberta.geometry("900x620")

        self.dados_originais_edicao = {k: str(v).strip() for k, v in dados.items()}

        frame = ttk.Labelframe(self.janela_edicao_aberta, text="Editar Dados")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Vars
        edit_genero_var = tk.StringVar(value=dados.get("genero", ""))
        edit_var_cidade = tk.StringVar(value=dados.get("cidade", ""))

        def get_binary_value(key):
            try:
                return int(dados.get(key) or 0)
            except (ValueError, TypeError):
                return 0

        edit_var_bolsa = tk.IntVar(value=get_binary_value("bolsa_familia"))
        edit_var_cesta = tk.IntVar(value=get_binary_value("cesta_basica"))
        edit_var_scfv = tk.IntVar(value=get_binary_value("scfv"))

        edit_var_futebol = tk.IntVar(value=get_binary_value("futebol"))
        edit_var_judo = tk.IntVar(value=get_binary_value("judo"))
        edit_var_jiu = tk.IntVar(value=get_binary_value("jiu_jitsu"))
        edit_var_leitura = tk.IntVar(value=get_binary_value("leitura"))

        edit_status_var = tk.StringVar(value=dados.get("status_usuario", "Ativo"))

        edit_var_nascimento = tk.StringVar(value=dados.get("nascimento", ""))
        edit_var_cpf = tk.StringVar(value=dados.get("cpf", ""))
        edit_var_telefone = tk.StringVar(value=dados.get("telefone", ""))
        edit_var_celular = tk.StringVar(value=dados.get("celular", ""))

        edit_entries = {}

        container = ttk.Frame(frame)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)

        form = ttk.LabelFrame(container, text="Dados Pessoais")
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=5)

        side = ttk.LabelFrame(container, text="Benefícios, Projetos e Situação")
        side.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=5)

        layout = [
            ("Nome completo:", 0, 0, "nome", None),
            ("Data Nasc:", 1, 0, "nascimento", edit_var_nascimento),
            ("Idade (só números):", 1, 2, "idade", self.vcmd_number),
            ("Gênero:", 2, 0, "genero_radio", None),
            ("CPF:", 3, 0, "cpf", edit_var_cpf),
            ("RG (só números):", 3, 2, "rg", self.vcmd_number),
            ("Endereço:", 4, 0, "endereco", None),
            ("Bairro:", 5, 0, "bairro", None),
            ("Cidade:", 5, 2, "cidade", None),
            ("Estado:", 6, 0, "estado", None),
            ("Telefone Fixo:", 7, 0, "telefone", edit_var_telefone),
            ("Celular:", 7, 2, "celular", edit_var_celular),
            ("E-mail:", 8, 0, "email", None),
            ("Peso (kg):", 9, 0, "peso", self.vcmd_number),
            ("Altura (cm):", 9, 2, "altura", self.vcmd_number),
            ("Responsável:", 10, 0, "responsavel", None),
        ]

        for text, row, col, name, validation_or_var in layout:
            ttk.Label(form, text=text).grid(row=row, column=col, sticky="w", padx=5, pady=2)
            if name == "cidade":
                cb = ttk.Combobox(form, textvariable=edit_var_cidade, values=CIDADES_RO, state="readonly")
                cb.set(dados.get("cidade", ""))
                cb.grid(row=row, column=col + 1, sticky="ew", padx=5, pady=2)
                edit_entries[name] = cb
            elif name == "estado":
                e = ttk.Entry(form)
                e.insert(0, dados.get("estado", "RO"))
                e.configure(state="readonly", width=5)
                e.grid(row=row, column=col + 1, sticky="w", padx=5, pady=2)
                edit_entries[name] = e
            elif name and name != "genero_radio":
                e = ttk.Entry(form, textvariable=validation_or_var if isinstance(validation_or_var, tk.StringVar) else None)
                if validation_or_var == self.vcmd_number:
                    e.configure(validate="key", validatecommand=self.vcmd_number)
                if not isinstance(validation_or_var, tk.StringVar):
                    e.insert(0, dados.get(name, ""))
                if name == "nascimento":
                    e.bind("<KeyRelease>", lambda ev, w=e: aplicar_mascara(ev, edit_var_nascimento, w, "data"))
                elif name == "cpf":
                    e.bind("<KeyRelease>", lambda ev, w=e: aplicar_mascara(ev, edit_var_cpf, w, "cpf"))
                elif name == "telefone":
                    e.bind("<KeyRelease>", lambda ev, w=e: aplicar_mascara(ev, edit_var_telefone, w, "fixo"))
                elif name == "celular":
                    e.bind("<KeyRelease>", lambda ev, w=e: aplicar_mascara(ev, edit_var_celular, w, "celular"))
                e.grid(row=row, column=col + 1, sticky="ew", padx=5, pady=2)
                edit_entries[name] = e

        edit_entries["nome"].grid(columnspan=3, sticky="ew")
        edit_entries["endereco"].grid(columnspan=3, sticky="ew")
        edit_entries["email"].grid(columnspan=3, sticky="ew")
        edit_entries["responsavel"].grid(columnspan=3, sticky="ew")

        ttk.Radiobutton(form, text="Masculino (M)", variable=edit_genero_var, value="M").grid(
            row=2, column=1, sticky="w", padx=5
        )
        ttk.Radiobutton(form, text="Feminino (F)", variable=edit_genero_var, value="F").grid(
            row=2, column=2, sticky="w", padx=5
        )

        box_benef = ttk.LabelFrame(side, text="Benefícios Sociais")
        box_benef.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Checkbutton(box_benef, text="Bolsa Família", variable=edit_var_bolsa).pack(anchor="w", padx=6, pady=2)
        ttk.Checkbutton(box_benef, text="Cesta Básica", variable=edit_var_cesta).pack(anchor="w", padx=6, pady=2)
        ttk.Checkbutton(box_benef, text="SCFV", variable=edit_var_scfv).pack(anchor="w", padx=6, pady=2)

        box_proj = ttk.LabelFrame(side, text="Inscrição em Projetos")
        box_proj.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Checkbutton(box_proj, text="Futebol", variable=edit_var_futebol).pack(anchor="w", padx=6, pady=2)
        ttk.Checkbutton(box_proj, text="Judô", variable=edit_var_judo).pack(anchor="w", padx=6, pady=2)
        ttk.Checkbutton(box_proj, text="Jiu Jitsu", variable=edit_var_jiu).pack(anchor="w", padx=6, pady=2)
        ttk.Checkbutton(box_proj, text="Leitura", variable=edit_var_leitura).pack(anchor="w", padx=6, pady=2)

        box_status = ttk.LabelFrame(side, text="Situação do Usuário")
        box_status.pack(fill="x", padx=8, pady=(8, 8))
        ttk.Radiobutton(box_status, text="Ativo", variable=edit_status_var, value="Ativo").pack(
            anchor="w", padx=6, pady=2
        )
        ttk.Radiobutton(box_status, text="Inativo", variable=edit_status_var, value="Inativo").pack(
            anchor="w", padx=6, pady=2
        )

        vars_binarias_edicao = {
            "bolsa_familia": edit_var_bolsa,
            "cesta_basica": edit_var_cesta,
            "scfv": edit_var_scfv,
            "futebol": edit_var_futebol,
            "judo": edit_var_judo,
            "jiu_jitsu": edit_var_jiu,
            "leitura": edit_var_leitura,
        }

        self._edit_fields = {
            "entries_dict": edit_entries,
            "genero_var": edit_genero_var,
            "cidade_var": edit_var_cidade,
            "vars_binarias": vars_binarias_edicao,
            "nasc_var": edit_var_nascimento,
            "cpf_var": edit_var_cpf,
            "tel_var": edit_var_telefone,
            "cel_var": edit_var_celular,
            "status_var": edit_status_var,
        }

        ttk.Button(
            frame,
            text="Salvar Alterações",
            command=lambda: self.salvar_edicao(pessoa_id, **self._edit_fields),
            style="Principal.TButton",
        ).pack(pady=12)

        self.janela_edicao_aberta.protocol(
            "WM_DELETE_WINDOW", lambda: self.fechar_janela_edicao_com_aviso(self.janela_edicao_aberta)
        )

    def _coletar_dados_atuais_edicao(
        self, entries_dict, genero_var, cidade_var, vars_binarias, nasc_var, cpf_var, tel_var, cel_var, status_var
    ):
        dados = {}
        for col in COLUNAS_PESSOAS:
            if col == "nascimento":
                dados[col] = nasc_var.get()
            elif col == "cpf":
                dados[col] = cpf_var.get()
            elif col == "telefone":
                dados[col] = tel_var.get()
            elif col == "celular":
                dados[col] = cel_var.get()
            elif col == "genero":
                dados[col] = genero_var.get()
            elif col == "cidade":
                dados[col] = cidade_var.get()
            elif col == "estado":
                dados[col] = self.dados_originais_edicao.get("estado", "RO")
            elif col in entries_dict:
                dados[col] = entries_dict[col].get()
            else:
                dados[col] = ""

        for k, v in vars_binarias.items():
            dados[k] = str(v.get())

        dados["status_usuario"] = status_var.get()
        return {k: str(v).strip() for k, v in dados.items()}

    def dados_foram_modificados(self):
        if self.dados_originais_edicao is None or not hasattr(self, "_edit_fields"):
            return False
        dados_atuais = self._coletar_dados_atuais_edicao(**self._edit_fields)
        for key, valor_original in self.dados_originais_edicao.items():
            valor_atual = dados_atuais.get(key)
            if str(valor_atual).strip() != str(valor_original).strip():
                return True
        return False

    def fechar_janela_edicao_com_aviso(self, janela):
        if self.dados_foram_modificados():
            if messagebox.askyesno("Aviso", "Tem certeza que deseja fechar a edição sem salvar as alterações?"):
                self.fechar_janela_edicao(janela)
            else:
                janela.lift()
        else:
            self.fechar_janela_edicao(janela)

    def fechar_janela_edicao(self, janela):
        self.dados_originais_edicao = None
        self._edit_fields = {}
        self.janela_edicao_aberta = None
        janela.destroy()

    def salvar_edicao(
        self, pessoa_id, entries_dict, genero_var, cidade_var, vars_binarias, nasc_var, cpf_var, tel_var, cel_var, status_var
    ):
        dados_atualizados = {}
        for col in COLUNAS_PESSOAS:
            if col == "nascimento":
                dados_atualizados[col] = nasc_var.get()
            elif col == "cpf":
                dados_atualizados[col] = cpf_var.get()
            elif col == "telefone":
                dados_atualizados[col] = tel_var.get()
            elif col == "celular":
                dados_atualizados[col] = cel_var.get()
            elif col == "genero":
                dados_atualizados[col] = genero_var.get()
            elif col == "cidade":
                dados_atualizados[col] = cidade_var.get()
            elif col == "estado":
                dados_atualizados[col] = entries_dict[col].get()
            else:
                dados_atualizados[col] = entries_dict[col].get()

        for k, v in vars_binarias.items():
            dados_atualizados[k] = v.get()

        dados_atualizados["status_usuario"] = status_var.get()

        cpf_dig = re.sub(r"[^0-9]", "", dados_atualizados.get("cpf", ""))
        if cpf_dig not in ("", None) and len(cpf_dig) != 11:
            messagebox.showwarning("Aviso", "O CPF deve ter 11 dígitos.")
            return

        sucesso = self.db.atualizar_dados(dados_atualizados, pessoa_id)
        if sucesso:
            messagebox.showinfo("Sucesso", "Cadastro atualizado com sucesso!")
            self.dados_originais_edicao = self._coletar_dados_atuais_edicao(
                entries_dict, genero_var, cidade_var, vars_binarias, nasc_var, cpf_var, tel_var, cel_var, status_var
            )
            if self.janela_edicao_aberta:
                self.janela_edicao_aberta.destroy()
                self.janela_edicao_aberta = None
            filtro_atual = self.entry_pesquisa.get()
            self.listar_dados_na_treeview(filtro_atual)
        else:
            if messagebox.askyesno(
                "Falha na Atualização",
                "Ocorreu uma falha ao salvar as alterações. Deseja fechar a janela de edição mesmo assim?",
            ):
                if self.janela_edicao_aberta:
                    self.janela_edicao_aberta.destroy()
                    self.janela_edicao_aberta = None

    # -----------------------------------------------------------
    # Aba Relatórios
    # -----------------------------------------------------------
    def criar_aba_relatorios(self):
        ttk.Label(self.aba_relatorios, text="Geração de Relatórios e Exportação de Dados").pack(pady=10)

        frame_relatorio = ttk.LabelFrame(self.aba_relatorios, text="Exportação de Fichas Individuais")
        frame_relatorio.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_relatorio, text="1. Vá para a aba 'Consulta e Edição'.").pack(pady=5, padx=10, anchor="w")
        ttk.Label(frame_relatorio, text="2. Selecione um cadastro na tabela.").pack(pady=5, padx=10, anchor="w")
        ttk.Label(frame_relatorio, text="3. Clique no botão 'Gerar Ficha (PDF)'.").pack(pady=5, padx=10, anchor="w")

        ttk.Separator(self.aba_relatorios, orient="horizontal").pack(fill="x", padx=10, pady=20)

        frame_geral = ttk.LabelFrame(self.aba_relatorios, text="Exportação Geral e por Filtro")
        frame_geral.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_geral, text="Selecione os Projetos, Benefícios e Situação para o Relatório:").pack(pady=10)

        linha1 = ttk.Frame(frame_geral)
        linha1.pack()
        ttk.Checkbutton(linha1, text="Bolsa Família", variable=self.var_filtro_bolsa).pack(side="left", padx=10, pady=8)
        ttk.Checkbutton(linha1, text="Cesta Básica", variable=self.var_filtro_cesta).pack(side="left", padx=10, pady=8)
        ttk.Checkbutton(linha1, text="SCFV", variable=self.var_filtro_scfv).pack(side="left", padx=10, pady=8)

        linha2 = ttk.Frame(frame_geral)
        linha2.pack()
        ttk.Checkbutton(linha2, text="Futebol", variable=self.var_filtro_futebol).pack(side="left", padx=10, pady=8)
        ttk.Checkbutton(linha2, text="Judô", variable=self.var_filtro_judo).pack(side="left", padx=10, pady=8)
        ttk.Checkbutton(linha2, text="Jiu Jitsu", variable=self.var_filtro_jiu).pack(side="left", padx=10, pady=8)
        ttk.Checkbutton(linha2, text="Leitura", variable=self.var_filtro_leitura).pack(side="left", padx=10, pady=8)

        linha3 = ttk.Frame(frame_geral)
        linha3.pack()
        ttk.Checkbutton(linha3, text="Ativo", variable=self.var_filtro_status_ativo).pack(side="left", padx=10, pady=8)
        ttk.Checkbutton(linha3, text="Inativo", variable=self.var_filtro_status_inativo).pack(side="left", padx=10, pady=8)

        ttk.Button(
            frame_geral, text="Gerar PDF de Cadastros Filtrados", command=self.gerar_relatorio_pdf, style="Principal.TButton"
        ).pack(pady=12, ipadx=20)

    # -----------------------------------------------------------
    # PDF (chamadas helpers)
    # -----------------------------------------------------------
    def gerar_ficha_pdf(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um registro na tabela para gerar a ficha.")
            return
        pessoa_id = self.tree.item(selected_item, "values")[0]
        tree_selection = (pessoa_id,)
        gerar_ficha_pdf_func(self.db, tree_selection)

    def gerar_relatorio_pdf(self):
        gerar_relatorio_pdf_func(
            self.db,
            self.var_filtro_bolsa,
            self.var_filtro_cesta,
            self.var_filtro_scfv,
            self.var_filtro_futebol,
            self.var_filtro_judo,
            self.var_filtro_jiu,
            self.var_filtro_leitura,
            self.var_filtro_status_ativo,
            self.var_filtro_status_inativo,
        )
