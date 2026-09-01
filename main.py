import tkinter as tk
from tkinter import messagebox
import sys
import os

# --- Ajuste de PATH para encontrar módulos locais ---
projeto_dir = os.path.dirname(os.path.abspath(__file__))
if projeto_dir not in sys.path:
    sys.path.insert(0, projeto_dir)
# ----------------------------------------------------

try:
    from gui_app import App
    from PIL import Image as PilImage, ImageTk  # opcional, mas útil p/ checagens
except ImportError as e:
    messagebox.showerror(
        "Erro de Inicialização",
        f"Falha ao carregar módulos: {e}.\n"
        f"Verifique se as dependências estão instaladas: tkinter, sqlite3, pillow (PIL), reportlab."
    )
    sys.exit(1)

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
        # Fecha conexão do DB com segurança
        if hasattr(app, "db"):
            app.db.fechar_conexao()
    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Ocorreu um erro fatal na aplicação: {e}")
        try:
            if 'app' in locals() and hasattr(app, 'db'):
                app.db.fechar_conexao()
        finally:
            sys.exit(1)
