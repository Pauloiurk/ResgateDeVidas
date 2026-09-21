import sqlite3
from tkinter import messagebox
import hashlib
from constants import COLUNAS_PESSOAS, CAMPOS_PROJETOS, CAMPOS_BENEFICIOS, CAMINHO_BANCO_DADOS

# Mantém compatibilidade com consultas existentes
COLUNAS_PESSOAS_QUERY = [f"p.{col}" for col in COLUNAS_PESSOAS]


class BancoDeDados:
    def __init__(self, db_nome=CAMINHO_BANCO_DADOS):
        self.db_nome = db_nome
        self.conn = None
        self.cursor = None
        self.conectar()
        self.criar_tabela()
        self.migrar_esquema()  # garante colunas novas sem perder dados

    # ---------------- Conexão ----------------
    def conectar(self):
        try:
            self.conn = sqlite3.connect(self.db_nome, timeout=10)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao conectar: {e}")
            self.conn = None

    def fechar_conexao(self):
        if self.conn:
            self.conn.close()

    # ---------------- Criação/Migração ----------------
    def criar_tabela(self):
        if not self.cursor:
            return

        colunas_pessoas_sql = ", ".join([f"{col} TEXT" for col in COLUNAS_PESSOAS])

        # tabela principal
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {colunas_pessoas_sql}
            )
        """)

        # projetos
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS projetos_ativos (
                pessoa_id INTEGER PRIMARY KEY,
                {", ".join([f"{col} INTEGER DEFAULT 0" for col in CAMPOS_PROJETOS])},
                FOREIGN KEY(pessoa_id) REFERENCES pessoas(id) ON DELETE CASCADE
            )
        """)

        # benefícios
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS beneficios_ativos (
                pessoa_id INTEGER PRIMARY KEY,
                {", ".join([f"{col} INTEGER DEFAULT 0" for col in CAMPOS_BENEFICIOS])},
                FOREIGN KEY(pessoa_id) REFERENCES pessoas(id) ON DELETE CASCADE
            )
        """)

        # usuários (login)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT UNIQUE NOT NULL,
                nome_completo TEXT NOT NULL,
                telefone TEXT,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL
            )
        """)

        self.conn.commit()

    def migrar_esquema(self):
        """Adiciona colunas que não existirem:
           - pessoas.status_usuario (TEXT NOT NULL DEFAULT 'Ativo')
           - beneficios_ativos.scfv (INTEGER DEFAULT 0)
        """
        if not self.cursor:
            return

        def colunas_da_tabela(nome):
            self.cursor.execute(f"PRAGMA table_info({nome})")
            return {linha[1] for linha in self.cursor.fetchall()}

        # pessoas.status_usuario
        cols_pessoas = colunas_da_tabela("pessoas")
        if "status_usuario" not in cols_pessoas:
            self.cursor.execute(
                "ALTER TABLE pessoas ADD COLUMN status_usuario TEXT NOT NULL DEFAULT 'Ativo'"
            )

        # beneficios_ativos.scfv
        cols_beneficios = colunas_da_tabela("beneficios_ativos")
        if "scfv" not in cols_beneficios:
            try:
                self.cursor.execute("ALTER TABLE beneficios_ativos ADD COLUMN scfv INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass

        self.conn.commit()

    # ---------------- Autenticação ----------------
    def inserir_usuario(self, cpf, nome_completo, telefone, email, senha) -> bool:
        if not self.cursor:
            return False

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        try:
            self.cursor.execute("""
                INSERT INTO usuarios (cpf, nome_completo, telefone, email, senha_hash)
                VALUES (?, ?, ?, ?, ?)
            """, (cpf, nome_completo, telefone, email, senha_hash))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Erro de Cadastro", "CPF ou E-mail já cadastrado no sistema.")
            else:
                messagebox.showerror("Erro de Cadastro", f"Erro: {e}")
            return False
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Cadastro", f"Erro ao inserir usuário: {e}")
            return False

    def verificar_login(self, email, senha) -> bool:
        if not self.cursor:
            return False

        self.cursor.execute("SELECT senha_hash FROM usuarios WHERE email=?", (email,))
        r = self.cursor.fetchone()
        if r:
            return hashlib.sha256(senha.encode()).hexdigest() == r[0]
        return False

    # ---------------- CRUD Pessoas ----------------
    def inserir_dados(self, dados: dict) -> bool:
        """Insere nas 3 tabelas. 'status_usuario' é salvo à parte (coluna extra)."""
        if not self.cursor:
            return False

        try:
            # 1) pessoas
            valores_pessoas = tuple(dados.get(col, "") for col in COLUNAS_PESSOAS)
            placeholders = ", ".join(["?"] * len(COLUNAS_PESSOAS))
            cols_str = ", ".join(COLUNAS_PESSOAS)

            self.cursor.execute(
                f"INSERT INTO pessoas ({cols_str}) VALUES ({placeholders})",
                valores_pessoas
            )
            pessoa_id = self.cursor.lastrowid

            # status_usuario (não faz parte de COLUNAS_PESSOAS para não quebrar índices)
            status = dados.get("status_usuario", "Ativo") or "Ativo"
            self.cursor.execute(
                "UPDATE pessoas SET status_usuario=? WHERE id=?",
                (status, pessoa_id)
            )

            # 2) projetos
            valores_proj = tuple(dados.get(col, 0) for col in CAMPOS_PROJETOS)
            placeholders_proj = ", ".join(["?"] * len(CAMPOS_PROJETOS))
            cols_proj = ", ".join(CAMPOS_PROJETOS)
            self.cursor.execute(
                f"INSERT INTO projetos_ativos (pessoa_id, {cols_proj}) VALUES (?, {placeholders_proj})",
                (pessoa_id,) + valores_proj
            )

            # 3) benefícios
            valores_ben = tuple(dados.get(col, 0) for col in CAMPOS_BENEFICIOS)
            placeholders_ben = ", ".join(["?"] * len(CAMPOS_BENEFICIOS))
            cols_ben = ", ".join(CAMPOS_BENEFICIOS)
            self.cursor.execute(
                f"INSERT INTO beneficios_ativos (pessoa_id, {cols_ben}) VALUES (?, {placeholders_ben})",
                (pessoa_id,) + valores_ben
            )

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Erro ao Salvar (DB)", f"Falha ao inserir dados: {e}")
            self.conn.rollback()
            return False

    def listar_todos_dados(self, filtro=None):
        """Lista dados para a Treeview (sem incluir status_usuario para não quebrar índices)."""
        if not self.cursor:
            return []

        beneficios_select = ", ".join([f"COALESCE(ba.{col}, 0)" for col in CAMPOS_BENEFICIOS])
        projetos_select = ", ".join([f"COALESCE(pa.{col}, 0)" for col in CAMPOS_PROJETOS])
        campos_principais_select = "p.id, " + ", ".join([f"p.{c}" for c in COLUNAS_PESSOAS])

        query = f"""
            SELECT
                {campos_principais_select},
                {beneficios_select},
                {projetos_select}
            FROM pessoas p
            LEFT JOIN beneficios_ativos ba ON p.id = ba.pessoa_id
            LEFT JOIN projetos_ativos pa ON p.id = pa.pessoa_id
        """

        params = []
        if filtro:
            filtro_like = f"%{filtro}%"
            query += """
                WHERE p.nome LIKE ? OR p.cpf LIKE ? OR p.celular LIKE ? OR p.cidade LIKE ?
            """
            params = [filtro_like] * 4

        query += " ORDER BY p.nome ASC"
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def buscar_dados_por_id(self, pessoa_id: int):
        """Retorna dict com pessoas + projetos + beneficios + status_usuario."""
        if not self.cursor:
            return None

        # pessoa (inclui status_usuario)
        self.cursor.execute("SELECT * FROM pessoas WHERE id=?", (pessoa_id,))
        dados_pessoa = self.cursor.fetchone()
        if not dados_pessoa:
            return None

        # projetos
        self.cursor.execute(f"SELECT {', '.join(CAMPOS_PROJETOS)} FROM projetos_ativos WHERE pessoa_id=?", (pessoa_id,))
        dados_proj = self.cursor.fetchone() or (0,) * len(CAMPOS_PROJETOS)

        # benefícios
        self.cursor.execute(f"SELECT {', '.join(CAMPOS_BENEFICIOS)} FROM beneficios_ativos WHERE pessoa_id=?", (pessoa_id,))
        dados_ben = self.cursor.fetchone() or (0,) * len(CAMPOS_BENEFICIOS)

        # monta dicionário
        dados_dict = {col: dados_pessoa[i+1] for i, col in enumerate(COLUNAS_PESSOAS)}
        # status_usuario é a última coluna após as de COLUNAS_PESSOAS
        try:
            idx_status = 1 + len(COLUNAS_PESSOAS)  # coluna após o último campo da lista
            dados_dict["status_usuario"] = dados_pessoa[idx_status]
        except Exception:
            dados_dict["status_usuario"] = "Ativo"

        for i, col in enumerate(CAMPOS_PROJETOS):
            dados_dict[col] = dados_proj[i]
        for i, col in enumerate(CAMPOS_BENEFICIOS):
            dados_dict[col] = dados_ben[i]

        return dados_dict

    def atualizar_dados(self, dados: dict, pessoa_id: int) -> bool:
        """Atualiza pessoas, projetos, benefícios. 'status_usuario' atualizado separado."""
        if not self.cursor:
            return False
        try:
            # pessoas
            campos_update = ", ".join([f"{col}=?" for col in COLUNAS_PESSOAS])
            valores = tuple(dados.get(col, "") for col in COLUNAS_PESSOAS)
            self.cursor.execute(
                f"UPDATE pessoas SET {campos_update} WHERE id=?",
                valores + (pessoa_id,)
            )

            # status_usuario
            if "status_usuario" in dados:
                self.cursor.execute(
                    "UPDATE pessoas SET status_usuario=? WHERE id=?",
                    (dados.get("status_usuario") or "Ativo", pessoa_id)
                )

            # projetos
            campos_proj = ", ".join([f"{col}=?" for col in CAMPOS_PROJETOS])
            valores_proj = tuple(dados.get(col, 0) for col in CAMPOS_PROJETOS)
            self.cursor.execute(
                f"UPDATE projetos_ativos SET {campos_proj} WHERE pessoa_id=?",
                valores_proj + (pessoa_id,)
            )

            # benefícios
            campos_ben = ", ".join([f"{col}=?" for col in CAMPOS_BENEFICIOS])
            valores_ben = tuple(dados.get(col, 0) for col in CAMPOS_BENEFICIOS)
            self.cursor.execute(
                f"UPDATE beneficios_ativos SET {campos_ben} WHERE pessoa_id=?",
                valores_ben + (pessoa_id,)
            )

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Erro ao Atualizar (DB)", f"Falha ao atualizar dados: {e}")
            self.conn.rollback()
            return False

    def excluir_dado(self, pessoa_id: int) -> bool:
        if not self.cursor:
            return False
        try:
            self.cursor.execute("DELETE FROM pessoas WHERE id=?", (pessoa_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Erro ao Excluir", f"Erro: {e}")
            return False
