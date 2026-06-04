import os
import sys
import queue
import re
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Importações dos serviços do compilador existentes
from src.parser_service import get_parser
from src.semantic_service import SemanticAnalyzer, SemanticError
from src.generator_service import PythonGenerator

class LatinEditor(tk.Frame):
    """Componente editor de texto com números de linha sincronizados e destaque de sintaxe."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Palavras reservadas da linguagem Latim para o realce
        self.KEYWORDS = [
            "principium", "finis", "numerus", "decimalis", "textus", 
            "veritas", "inanis", "collectio", "si", "aliter", 
            "pro", "usque", "dum", "fac", "lege", "scribe"
        ]

        # Layout do editor (Modo Escuro)
        self.text_area = tk.Text(
            self, undo=True, maxundo=100, wrap="none",
            background="#1e1e1e", foreground="#d4d4d4",
            insertbackground="#ffffff", selectbackground="#264f78",
            font=("Consolas", 12), border=0, padx=5, pady=5
        )
        
        self.line_numbers = tk.Text(
            self, width=4, padx=5, pady=5, takefocus=0, border=0,
            background="#1e1e1e", foreground="#858585",
            state="disabled", wrap="none", font=("Consolas", 12)
        )
        
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self._on_scrollbar)
        self.hsb = ttk.Scrollbar(self, orient="horizontal", command=self.text_area.xview)
        
        self.text_area.configure(yscrollcommand=self._on_textscroll, xscrollcommand=self.hsb.set)
        
        # Grid para posicionar editor, números de linha e barras de rolagem
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        self.text_area.grid(row=0, column=1, sticky="nsew")
        self.vsb.grid(row=0, column=2, sticky="ns")
        self.hsb.grid(row=1, column=0, columnspan=3, sticky="ew")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Configurar cores das tags de sintaxe
        self.text_area.tag_configure("keyword", foreground="#569cd6")  # Azul VSCode
        self.text_area.tag_configure("comment", foreground="#6a9955")  # Verde Comentário
        self.text_area.tag_configure("string", foreground="#ce9178")   # Laranja String
        self.text_area.tag_configure("number", foreground="#b5cea8")   # Verde Claro Número
        
        # Binds de eventos para manter números e sintaxe atualizados
        self.text_area.bind("<<Modified>>", self._on_modified)
        self.text_area.bind("<KeyRelease>", self._update_view)
        self.text_area.bind("<MouseWheel>", self._update_view)
        
        self._update_view()

    def get_code(self) -> str:
        """Retorna o código digitado no editor."""
        return self.text_area.get("1.0", "end-1c")

    def set_code(self, code: str):
        """Define o código no editor."""
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", code)
        self._update_view()

    def _on_scrollbar(self, *args):
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    def _on_textscroll(self, *args):
        self.vsb.set(*args)
        self.line_numbers.yview_moveto(args[0])

    def _on_modified(self, event=None):
        self._update_view()
        self.text_area.edit_modified(False)

    def _update_view(self, event=None):
        self._update_line_numbers()
        self.highlight_syntax()

    def _update_line_numbers(self):
        line_count = int(self.text_area.index('end-1c').split('.')[0])
        lines_content = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", lines_content)
        self.line_numbers.configure(state="disabled")
        
        # Sincroniza rolagem
        self.line_numbers.yview_moveto(self.text_area.yview()[0])

    def highlight_syntax(self):
        """Aplica realce de sintaxe básico usando expressões regulares."""
        content = self.get_code()
        
        # Limpar tags anteriores antes de destacar de novo
        for tag in ["keyword", "comment", "string", "number"]:
            self.text_area.tag_remove(tag, "1.0", "end")
            
        # 1. Destacar Strings
        for match in re.finditer(r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'', content):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.text_area.tag_add("string", start, end)
            
        # 2. Destacar Comentários (// até o final da linha)
        for match in re.finditer(r'//.*$', content, re.MULTILINE):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.text_area.tag_add("comment", start, end)
            
        # 3. Destacar Números decimais e inteiros
        for match in re.finditer(r'\b\d+(?:\.\d+)?\b', content):
            start_idx = match.start()
            char_index = f"1.0 + {start_idx} chars"
            tags = self.text_area.tag_names(char_index)
            if "comment" in tags or "string" in tags:
                continue
            start = char_index
            end = f"1.0 + {match.end()} chars"
            self.text_area.tag_add("number", start, end)

        # 4. Destacar Palavras Reservadas (Keywords)
        keywords_pattern = r'\b(' + '|'.join(self.KEYWORDS) + r')\b'
        for match in re.finditer(keywords_pattern, content):
            start_idx = match.start()
            char_index = f"1.0 + {start_idx} chars"
            tags = self.text_area.tag_names(char_index)
            if "comment" in tags or "string" in tags:
                continue
            start = char_index
            end = f"1.0 + {match.end()} chars"
            self.text_area.tag_add("keyword", start, end)


class IDEApp(tk.Tk):
    """Classe principal da IDE desktop Latim-Python."""
    def __init__(self):
        super().__init__()
        
        self.title("IDE Latim-Python")
        self.geometry("1100x750")
        
        # Paleta de Cores Escuras (VSCode Inspired)
        self.bg_dark = "#1e1e1e"
        self.bg_lighter = "#252526"
        self.bg_selected = "#264f78"
        self.fg_light = "#d4d4d4"
        self.fg_muted = "#858585"
        self.accent_color = "#007acc"
        
        # Variáveis de Controle da Execução
        self.process = None
        self.log_queue = queue.Queue()
        self.script_temp_path = "saida_gui.py"
        self.current_file_path = None
        
        self._apply_styles()
        self._build_layout()
        self._populate_initial_code()

    def _apply_styles(self):
        """Aplica o tema escuro moderno aos widgets da Ttk."""
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(".", background=self.bg_lighter, foreground=self.fg_light)
        style.configure("TFrame", background=self.bg_lighter)
        style.configure("TLabel", background=self.bg_lighter, foreground=self.fg_light)
        
        # Estilo dos botões da barra de ferramentas
        style.configure(
            "TButton", background="#2d2d2d", foreground=self.fg_light, 
            borderwidth=1, focuscolor="none", font=("Segoe UI", 10, "bold")
        )
        style.map("TButton", background=[("active", "#3e3e42"), ("pressed", "#1e1e1e")])
        
        # Estilo do Notebook (Abas)
        style.configure("TNotebook", background=self.bg_lighter, tabmargins=[2, 4, 2, 0])
        style.configure("TNotebook.Tab", background="#2d2d2d", foreground=self.fg_light, padding=[12, 6])
        style.map("TNotebook.Tab", background=[("selected", self.bg_dark)], foreground=[("selected", "#ffffff")])

    def _build_layout(self):
        """Constrói a estrutura de frames da janela."""
        # 1. Barra de Ações (Topo)
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(fill="x", side="top")
        
        self.run_btn = ttk.Button(toolbar, text="▶ Rodar", command=self.compile_and_run)
        self.run_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(toolbar, text="⏹ Parar", state="disabled", command=self.stop_execution)
        self.stop_btn.pack(side="left", padx=5)
        
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=10)
        
        self.open_btn = ttk.Button(toolbar, text="📁 Abrir", command=self.open_file)
        self.open_btn.pack(side="left", padx=5)
        
        self.save_btn = ttk.Button(toolbar, text="💾 Salvar", command=self.save_file)
        self.save_btn.pack(side="left", padx=5)
        
        self.clear_btn = ttk.Button(toolbar, text="🧹 Limpar Console", command=self.clear_console)
        self.clear_btn.pack(side="left", padx=5)
        
        # Label para indicar arquivo ativo
        self.file_label = ttk.Label(toolbar, text="Novo Arquivo (.latim)", foreground=self.fg_muted, font=("Segoe UI", 9, "italic"))
        self.file_label.pack(side="right", padx=10)

        # 2. Painel Principal Dividido (Split)
        main_pane = ttk.PanedWindow(self, orient="horizontal")
        main_pane.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Esquerda: Editor de Código
        editor_frame = ttk.Frame(main_pane)
        main_pane.add(editor_frame, weight=1)
        self.editor = LatinEditor(editor_frame)
        self.editor.pack(fill="both", expand=True)
        
        # Direita: Abas (Saída e Python)
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=1)
        
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Aba 1: Console de Saída
        self.output_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.output_tab, text="Console de Saída")
        
        self.output_text = tk.Text(
            self.output_tab, wrap="word", background="#0c0c0c", foreground="#e6e6e6",
            insertbackground="#ffffff", selectbackground="#264f78",
            font=("Consolas", 11), border=0, padx=10, pady=10, state="disabled"
        )
        self.output_text.pack(fill="both", expand=True, side="left")
        
        output_scrollbar = ttk.Scrollbar(self.output_tab, orient="vertical", command=self.output_text.yview)
        output_scrollbar.pack(fill="y", side="right")
        self.output_text.configure(yscrollcommand=output_scrollbar.set)
        
        # Configurar cores de tags do console
        self.output_text.tag_configure("info", foreground="#569cd6")     # Azul informativo
        self.output_text.tag_configure("error", foreground="#f44747")    # Vermelho para erros
        self.output_text.tag_configure("success", foreground="#b5cea8")  # Verde sucesso
        self.output_text.tag_configure("stderr", foreground="#f44747")   # Vermelho erro de execução
        
        # Aba 2: Código Python Traduzido
        self.python_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.python_tab, text="Python Traduzido")
        
        self.python_text = tk.Text(
            self.python_tab, wrap="none", background="#1e1e1e", foreground="#9cdcfe",
            insertbackground="#ffffff", font=("Consolas", 11), border=0, padx=10, pady=10, state="disabled"
        )
        self.python_text.pack(fill="both", expand=True, side="left")
        
        python_scrollbar = ttk.Scrollbar(self.python_tab, orient="vertical", command=self.python_text.yview)
        python_scrollbar.pack(fill="y", side="right")
        self.python_text.configure(yscrollcommand=python_scrollbar.set)

    def _populate_initial_code(self):
        """Tenta abrir 'programa.latim' ou popula um exemplo interativo inicial."""
        if os.path.exists("programa.latim"):
            try:
                with open("programa.latim", "r", encoding="utf-8") as f:
                    self.editor.set_code(f.read())
                self.current_file_path = os.path.abspath("programa.latim")
                self.file_label.config(text=f"Ativo: {os.path.basename(self.current_file_path)}")
                return
            except Exception:
                pass
                
        # Código inicial padrão se programa.latim não existir
        default_code = """principium
  // Exemplo de Boas-Vindas em Latim
  textus nome.
  numerus idade.

  scribe("Bem-vindo ao Transpilador Latim!").
  scribe("Digite o seu nome: ").
  lege(nome).

  scribe("Digite sua idade: ").
  lege(idade).

  si (idade >= 18) {
    scribe("Ola, ").
    scribe(nome).
    scribe("! Voce e maior de idade.").
  } aliter {
    scribe("Ola, ").
    scribe(nome).
    scribe("! Voce e menor de idade.").
  }
finis"""
        self.editor.set_code(default_code)

    def write_console(self, text: str, tag: str = None):
        """Escreve com segurança na janela do console."""
        self.output_text.config(state="normal")
        self.output_text.insert("end", text, tag)
        self.output_text.see("end")
        self.output_text.config(state="disabled")

    def clear_console(self):
        """Limpa o conteúdo do console."""
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")

    def show_python_code(self, code: str):
        """Insere o código Python gerado na aba correspondente."""
        self.python_text.config(state="normal")
        self.python_text.delete("1.0", "end")
        self.python_text.insert("1.0", code)
        self.python_text.config(state="disabled")

    def open_file(self):
        """Abre uma janela de diálogo para escolher um arquivo .latim."""
        file_path = filedialog.askopenfilename(
            title="Abrir Código Latim",
            filetypes=[("Código Latim", "*.latim"), ("Todos os Arquivos", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.editor.set_code(f.read())
                self.current_file_path = os.path.abspath(file_path)
                self.file_label.config(text=f"Ativo: {os.path.basename(self.current_file_path)}")
                self.clear_console()
                self.write_console(f"[ARQUIVO CARREGADO] {os.path.basename(file_path)}\n\n", "success")
            except Exception as e:
                messagebox.showerror("Erro ao Abrir", f"Não foi possível ler o arquivo:\n{str(e)}")

    def save_file(self):
        """Salva o código atual de volta no arquivo aberto ou cria um novo."""
        if not self.current_file_path:
            file_path = filedialog.asksaveasfilename(
                title="Salvar Código Latim",
                defaultextension=".latim",
                filetypes=[("Código Latim", "*.latim"), ("Todos os Arquivos", "*.*")]
            )
            if not file_path:
                return
            self.current_file_path = os.path.abspath(file_path)
            
        try:
            with open(self.current_file_path, "w", encoding="utf-8") as f:
                f.write(self.editor.get_code())
            self.file_label.config(text=f"Ativo: {os.path.basename(self.current_file_path)}")
            self.write_console(f"[ARQUIVO SALVO] {os.path.basename(self.current_file_path)}\n", "success")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{str(e)}")

    def compile_and_run(self):
        """Realiza todo o processo de análise, compilação e dispara a execução."""
        self.clear_console()
        self.notebook.select(self.output_tab) # Força visualização da aba Console
        
        code = self.editor.get_code().strip()
        if not code:
            self.write_console("O editor está vazio! Digite algum código em Latim para rodar.\n", "error")
            return
            
        self.write_console("1. Analisando gramática (Análise Sintática)...\n", "info")
        
        # 1. Análise Sintática
        try:
            parser = get_parser()
            # O parser espera código em minúsculas como definido em main.py
            ast = parser.parse(code.lower())
        except Exception as err:
            self.write_console(f"\n[ERRO SINTÁTICO DETECTADO]\n{str(err)}\n", "error")
            return
            
        self.write_console("2. Validando regras semânticas...\n", "info")
        
        # 2. Análise Semântica
        try:
            analyzer = SemanticAnalyzer()
            analyzer.validar(ast)
            self.write_console("Análise semântica concluída sem erros!\n", "success")
        except SemanticError as err:
            self.write_console(f"\n[ERRO SEMÂNTICO DE COMPILAÇÃO]\n{str(err)}\n", "error")
            return
        except Exception as err:
            self.write_console(f"\n[ERRO INESPERADO NO ANALISADOR SEMÂNTICO]\n{str(err)}\n", "error")
            return
            
        self.write_console("3. Gerando código equivalente em Python...\n", "info")
        
        # 3. Geração de Código Python
        try:
            generator = PythonGenerator(analyzer.tabela_simbolos)
            python_code = generator.generate(ast)
            self.show_python_code(python_code)
        except Exception as err:
            self.write_console(f"\n[ERRO NA GERAÇÃO DE CÓDIGO]\n{str(err)}\n", "error")
            return
            
        # 4. Injeção da Sobrescrita do input() nativo para Modal Tkinter (lege)
        injected_header = """# -*- coding: utf-8 -*-
# Código gerado automaticamente pelo transpilador Latim-Python para a IDE
import tkinter as tk
from tkinter import simpledialog

_gui_root = tk.Tk()
_gui_root.withdraw() # Oculta janela raiz vazia

def input(prompt=""):
    # Abre pop-up de input para interação nativa com o usuário
    valor = simpledialog.askstring("Entrada de Dados (lege)", prompt or "Digite o valor solicitado:")
    _gui_root.update()
    if valor is None:
        raise KeyboardInterrupt("Execução cancelada pelo usuário")
    return valor

"""
        full_runnable_code = injected_header + python_code
        
        # Salva o arquivo executável temporário
        try:
            with open(self.script_temp_path, "w", encoding="utf-8") as f:
                f.write(full_runnable_code)
        except Exception as err:
            self.write_console(f"\n[ERRO AO CRIAR ARQUIVO EXECUTÁVEL TEMPORÁRIO]\n{str(err)}\n", "error")
            return
            
        # Inicia a Thread para executar o subprocesso de forma não-bloqueante
        self._start_execution_thread()

    def _start_execution_thread(self):
        """Prepara e inicia a execução do subprocesso em segundo plano."""
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.open_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        
        self.write_console("\n[INICIANDO EXECUÇÃO DO PROGRAMA]\n", "success")
        
        # Polling da fila de mensagens a cada 100ms
        self.after(100, self._poll_queue)
        
        # Execução assíncrona do script gerado em outra Thread
        self.execution_thread = threading.Thread(
            target=self._run_subprocess_worker,
            args=(self.script_temp_path,),
            daemon=True
        )
        self.execution_thread.start()

    def _run_subprocess_worker(self, path: str):
        """Método executado na thread de segundo plano."""
        try:
            # -u força a saída padrão e de erro do Python a ser não buferizada (unbuffered)
            self.process = subprocess.Popen(
                [sys.executable, "-u", path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combina stdout e stderr para chronological alignment
                text=True,
                bufsize=1
            )
            
            # Lê cada linha de saída em tempo real e coloca na fila thread-safe
            for line in self.process.stdout:
                self.log_queue.put(("stdout", line))
                
            self.process.wait()
            exit_code = self.process.returncode
            
            self.log_queue.put(("info", f"\n[PROGRAMA FINALIZADO] Código de saída: {exit_code}\n"))
        except Exception as e:
            self.log_queue.put(("error", f"\n[ERRO DE EXECUÇÃO INESPERADO]\n{str(e)}\n"))
        finally:
            self.log_queue.put(("done", None))

    def _poll_queue(self):
        """Verifica periodicamente se há novas saídas produzidas pelo subprocesso."""
        try:
            while True:
                # Tenta ler mensagens na fila sem travar a interface gráfica (block=False)
                msg_type, msg_val = self.log_queue.get_nowait()
                
                if msg_type == "done":
                    self._cleanup_after_execution()
                    return
                elif msg_type == "stdout":
                    self.write_console(msg_val)
                elif msg_type == "error":
                    self.write_console(msg_val, "error")
                elif msg_type == "info":
                    self.write_console(msg_val, "info")
                    
        except queue.Empty:
            # Se a fila estiver vazia no momento, reagenda a verificação para daqui a 100ms
            self.after(100, self._poll_queue)

    def _cleanup_after_execution(self):
        """Restaura o estado normal dos botões após a conclusão do programa e limpa arquivos temporários."""
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.open_btn.config(state="normal")
        self.save_btn.config(state="normal")
        self.process = None
        
        # Remove com segurança o arquivo temporário 'saida_gui.py'
        if os.path.exists(self.script_temp_path):
            try:
                os.remove(self.script_temp_path)
            except OSError:
                pass

    def stop_execution(self):
        """Interrompe forçadamente a execução do subprocesso do programa."""
        if self.process:
            try:
                self.process.terminate()
                # Aguarda até 1 segundo pelo fechamento suave, se não, encerra de vez
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception:
                pass
                
            self.write_console("\n[EXECUÇÃO INTERROMPIDA PELO USUÁRIO]\n", "error")
            self._cleanup_after_execution()


if __name__ == "__main__":
    app = IDEApp()
    app.mainloop()