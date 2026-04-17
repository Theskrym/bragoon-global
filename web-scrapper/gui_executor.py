"""
GUI MODULAR para execução de pipeline de Web Scraping
Permite executar scripts em ordem sem acoplamento direto
"""

import os
import sys
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime
import json

# ============================================================================
# CONFIGURAÇÃO MODULAR DE PIPELINE
# ============================================================================

class PipelineConfig:
    """Configuração modular do pipeline - fácil de modificar sem quebrar a GUI"""
    
    SCRIPTS = [
        {
            "id": "1_scraper",
            "name": "🔍 Scraper (Coleta de Dados)",
            "description": "Coleta produtos dos sites",
            "file": "scrapper.py",
            "enabled": True,
            "show_output": True,
            "timeout": 3600,  # 1 hora
            "check_output": ["produtos.xlsx"],  # Valida se arquivo foi criado
        },
        {
            "id": "2_classifier",
            "name": "📝 Classificador de Nomes",
            "description": "Simplifica e padroniza nomes de produtos",
            "file": "name_classifier.py",
            "enabled": True,
            "show_output": True,
            "timeout": 600,
            "check_output": [],
        },
        {
            "id": "3_classifier_ml",
            "name": "🤖 Classificador ML (Pós-Pichau)",
            "description": "Classifica com ML e deduplica dados",
            "file": "scrapper -pós-pichau.py",
            "enabled": True,
            "show_output": True,
            "timeout": 600,
            "check_output": [],
        },
        {
            "id": "4_html_generator",
            "name": "🌐 Gerador HTML",
            "description": "Converte dados em pages HTML",
            "file": "Atualizar_SITE.py",
            "enabled": True,
            "show_output": True,
            "timeout": 300,
            "check_output": [],
        },
         {
            "id": "5_sql_importer",
            "name": "📊 Upload para SQL",
            "description": "Envia dados para banco de dados Django",
            "file": "../bragoon-ecommerce/backend/import_products.py",
            "enabled": True,
            "show_output": True,
            "timeout": 600,
            "check_output": [],
        },
    ]
    
    SERVERS = [
        {
            "id": "django_server",
            "name": "🐍 Servidor Django",
            "description": "Inicia servidor Django (localhost:8000)",
            "command": "python manage.py runserver",
            "cwd_relative": "../bragoon-ecommerce/backend",
            "enabled": True,
            "show_output": True,
        },
        {
            "id": "frontend_server",
            "name": "⚛️  Frontend React",
            "description": "Inicia servidor Frontend React (localhost:3000)",
            "command": "npm start",
            "cwd_relative": "../bragoon-ecommerce/frontend",
            "enabled": False,
            "show_output": True,
        },
        {
            "id": "frontend2_server",
            "name": "🌐 Frontend HTML/JS",
            "description": "Inicia servidor Frontend HTML (localhost:3001)",
            "command": "python serve.py",
            "cwd_relative": "../bragoon-ecommerce/frontend2",
            "enabled": False,
            "show_output": True,
        },
    ]


# ============================================================================
# EXECUTOR DE SCRIPTS
# ============================================================================

class ScriptExecutor:
    """Executa scripts Python independentemente"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.process = None
        self.is_running = False
    
    def execute(
        self,
        script_name: str,
        timeout: Optional[int] = None,
        output_callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
    ) -> bool:
        """
        Executa um script e retorna sucesso/fracasso
        
        Args:
            script_name: Nome do arquivo do script
            timeout: Timeout em segundos
            output_callback: Função para capturar output
            error_callback: Função para capturar errors
        """
        try:
            self.is_running = True
            script_path = os.path.join(self.base_path, script_name)
            
            if not os.path.exists(script_path):
                error_msg = f"Script não encontrado: {script_path}"
                if error_callback:
                    error_callback(error_msg)
                return False
            
            # Executar script com output em tempo real
            # PYTHONUNBUFFERED garante que prints apareçam imediatamente
            # PYTHONIOENCODING=utf-8 suporta emojis em Windows
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            env['PYTHONIOENCODING'] = 'utf-8'
            
            self.process = subprocess.Popen(
                [sys.executable, script_path],
                cwd=self.base_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',  # Substitui caracteres inválidos por '?'
                bufsize=1,
                env=env,
            )
            
            # Capturar output linha por linha em tempo real
            try:
                start_time = time.time()
                
                while True:
                    # Ler linha do stdout (inclui stderr redirecionado)
                    line = self.process.stdout.readline()
                    
                    # Se não há mais linhas, script terminou
                    if not line:
                        break
                    
                    # Chamar callback com a linha NO MESMO MOMENTO
                    if output_callback:
                        output_callback(line.rstrip('\n'))
                    
                    # Verificar timeout
                    if timeout and (time.time() - start_time) > timeout:
                        self.process.kill()
                        raise subprocess.TimeoutExpired(script_path, timeout)
                
                # Aguardar finalização do processo
                ret_code = self.process.wait()
                return ret_code == 0
                
            except subprocess.TimeoutExpired:
                self.process.kill()
                error_msg = f"Script timeout após {timeout}s"
                if error_callback:
                    error_callback(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Erro ao executar script: {str(e)}"
            if error_callback:
                error_callback(error_msg)
            return False
        finally:
            self.is_running = False
    
    def stop(self):
        """Para execução do script"""
        if self.process and self.is_running:
            self.process.terminate()
            self.is_running = False
    
    def execute_command(
        self,
        command: str,
        cwd: str,
        timeout: Optional[int] = None,
        output_callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
    ) -> bool:
        """
        Executa um comando arbitrário em um diretório específico
        
        Args:
            command: Comando a executar (ex: "npm run server")
            cwd: Diretório de trabalho para executar
            timeout: Timeout em segundos
            output_callback: Função para capturar output
            error_callback: Função para capturar errors
        """
        try:
            self.is_running = True
            
            # Verificar se diretório existe
            if not os.path.exists(cwd):
                error_msg = f"Diretório não encontrado: {cwd}"
                if error_callback:
                    error_callback(error_msg)
                return False
            
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            env['PYTHONIOENCODING'] = 'utf-8'
            
            self.process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                env=env,
                shell=True,
            )
            
            try:
                start_time = time.time()
                
                while True:
                    line = self.process.stdout.readline()
                    
                    if not line:
                        break
                    
                    if output_callback:
                        output_callback(line.rstrip('\n'))
                    
                    if timeout and (time.time() - start_time) > timeout:
                        self.process.kill()
                        raise subprocess.TimeoutExpired(command, timeout)
                
                ret_code = self.process.wait()
                return ret_code == 0
                
            except subprocess.TimeoutExpired:
                self.process.kill()
                error_msg = f"Comando timeout após {timeout}s"
                if error_callback:
                    error_callback(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Erro ao executar comando: {str(e)}"
            if error_callback:
                error_callback(error_msg)
            return False
        finally:
            self.is_running = False


# ============================================================================
# GUI PRINCIPAL
# ============================================================================

class PipelineGUI:
    """GUI para orquestração do pipeline"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🔧 Bragoon - Pipeline Executor")
        self.root.geometry("1000x700")
        
        # Configurar estilos ttk (Arial 12)
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('TFrame', font=('Arial', 10))
        style.configure('TLabelFrame', font=('Arial', 10))
        style.configure('TCheckbutton', font=('Arial', 10))
        
        # Setup
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.executor = ScriptExecutor(self.base_path)
        self.execution_thread = None
        self.is_executing = False
        self.server_processes = {}  # Armazena processos de servidor
        
        self._setup_ui()
        self._load_config()
    
    def _setup_ui(self):
        """Cria interface do usuário"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ====== HEADER ======
        header_frame = ttk.LabelFrame(main_frame, text="Pipeline de Web Scraping", padding="10")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = ttk.Label(
            header_frame,
            text="Selecione quais scripts executar e clique em 'Iniciar Pipeline'",
            foreground="gray"
        )
        info_text.pack()
        
        # ====== SELEÇÃO DE SCRIPTS ======
        scripts_frame = ttk.LabelFrame(main_frame, text="Scripts", padding="10")
        scripts_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.script_vars = {}
        for script in PipelineConfig.SCRIPTS:
            var = tk.BooleanVar(value=script["enabled"])
            self.script_vars[script["id"]] = var
            
            frame = ttk.Frame(scripts_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            cb = ttk.Checkbutton(
                frame,
                text=f"{script['name']}",
                variable=var,
                state=tk.NORMAL
            )
            cb.pack(side=tk.LEFT)
            
            desc = ttk.Label(
                frame,
                text=script["description"],
                foreground="gray",
                font=("Arial", 9)
            )
            desc.pack(side=tk.LEFT, padx=(20, 0))
        
        # ====== SELEÇÃO DE SERVIDORES ======
        servers_frame = ttk.LabelFrame(main_frame, text="Servidores", padding="10")
        servers_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.server_vars = {}
        for server in PipelineConfig.SERVERS:
            var = tk.BooleanVar(value=server["enabled"])
            self.server_vars[server["id"]] = var
            
            frame = ttk.Frame(servers_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            cb = ttk.Checkbutton(
                frame,
                text=f"{server['name']}",
                variable=var,
                state=tk.NORMAL
            )
            cb.pack(side=tk.LEFT)
            
            desc = ttk.Label(
                frame,
                text=server["description"],
                foreground="gray",
                font=("Arial", 9)
            )
            desc.pack(side=tk.LEFT, padx=(20, 0))
        
        # ====== BOTÕES DE CONTROLE ======
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.btn_run = ttk.Button(
            button_frame,
            text="▶ Iniciar Pipeline",
            command=self._run_pipeline
        )
        self.btn_run.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = ttk.Button(
            button_frame,
            text="⏹ Parar",
            command=self._stop_execution,
            state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🚀 Iniciar Servidores",
            command=self._run_servers
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🛑 Parar Servidores",
            command=self._stop_servers
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📂 Abrir Pasta Output",
            command=self._open_output_folder
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🔄 Limpar Logs",
            command=self._clear_logs
        ).pack(side=tk.LEFT, padx=5)
        
        # ====== OUTPUT ======
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=20,
            bg="black",
            fg="white",
            font=("Arial", 9)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Tags para formatação
        self.output_text.tag_config("header", foreground="cyan")
        self.output_text.tag_config("success", foreground="lime")
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("warning", foreground="yellow")
        self.output_text.tag_config("info", foreground="white")
        
        # ====== STATUS BAR ======
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(
            status_frame,
            text="✅ Pronto",
            foreground="green"
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.progress_label = ttk.Label(status_frame, text="")
        self.progress_label.pack(side=tk.RIGHT)
    
    def _load_config(self):
        """Carrega configuração do arquivo (se existir)"""
        config_path = os.path.join(self.base_path, "pipeline_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    for script_id, enabled in config.items():
                        if script_id in self.script_vars:
                            self.script_vars[script_id].set(enabled)
                        elif script_id in self.server_vars:
                            self.server_vars[script_id].set(enabled)
            except:
                pass
    
    def _save_config(self):
        """Salva configuração do pipeline"""
        config = {k: v.get() for k, v in self.script_vars.items()}
        config.update({k: v.get() for k, v in self.server_vars.items()})
        config_path = os.path.join(self.base_path, "pipeline_config.json")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except:
            pass
    
    def _parse_ansi_colors(self, text: str):
        """
        Parse ANSI color codes e insere no output com tags corretas
        
        Mapeia códigos ANSI para tags tkinter:
        - \033[91m ou \033[31m = vermelho → "error"
        - \033[92m ou \033[32m = verde → "success"
        - \033[93m ou \033[33m = amarelo → "warning"
        - \033[94m ou \033[34m = azul → "header"
        - \033[96m ou \033[36m = ciano → "header"
        - \033[95m ou \033[35m = magenta → "info"
        - \033[0m = reset → "info"
        """
        import re
        
        # Mapa de códigos ANSI para tags
        ansi_to_tag = {
            '\033[91m': 'error',      # Vermelho claro
            '\033[31m': 'error',      # Vermelho
            '\033[92m': 'success',    # Verde claro
            '\033[32m': 'success',    # Verde
            '\033[93m': 'warning',    # Amarelo claro
            '\033[33m': 'warning',    # Amarelo
            '\033[94m': 'header',     # Azul claro
            '\033[34m': 'header',     # Azul
            '\033[96m': 'header',     # Ciano claro
            '\033[36m': 'header',     # Ciano
            '\033[95m': 'info',       # Magenta claro
            '\033[35m': 'info',       # Magenta
            '\033[90m': 'info',       # Cinza
            '\033[37m': 'info',       # Branco
            '\033[0m': 'info',        # Reset
        }
        
        # Split por códigos ANSI
        parts = re.split(r'(\033\[\d+m)', text)
        
        current_tag = 'info'
        for part in parts:
            if part in ansi_to_tag:
                # Atualizar tag atual
                current_tag = ansi_to_tag[part]
            elif part:  # Se não é código ANSI e não está vazio
                # Inserir com a tag atual
                self.output_text.insert(tk.END, part, current_tag)
        
        self.output_text.see(tk.END)
        self.root.update()
    
    def _log_output(self, message: str, tag: str = "info"):
        """Adiciona mensagem ao output com formatação ANSI"""
        if '\033[' in message:
            # Se tem código ANSI, usar parser
            self._parse_ansi_colors(message)
        else:
            # Caso contrário, usar método simples
            self.output_text.insert(tk.END, message, tag)
        
        self.output_text.insert(tk.END, '\n', tag)
        self.output_text.see(tk.END)
        self.root.update()
    
    def _run_pipeline(self):
        """Executa pipeline de scripts"""
        selected_scripts = [
            s for s in PipelineConfig.SCRIPTS
            if self.script_vars.get(s["id"], tk.BooleanVar()).get()
        ]
        
        if not selected_scripts:
            messagebox.showwarning("Aviso", "Selecione pelo menos um script!")
            return
        
        self.execution_thread = threading.Thread(
            target=self._execute_pipeline_thread,
            args=(selected_scripts,),
            daemon=True
        )
        self.execution_thread.start()
    
    def _execute_pipeline_thread(self, scripts: List[Dict]):
        """Thread para execução do pipeline"""
        try:
            self.is_executing = True
            self.btn_run.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            
            self._log_output(
                f"\n{'='*60}\n"
                f"🚀 PIPELINE INICIADO EM {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"{'='*60}\n",
                "header"
            )
            
            total = len(scripts)
            for idx, script in enumerate(scripts, 1):
                if not self.is_executing:
                    self._log_output("⏹ Pipeline interrompido pelo usuário", "warning")
                    break
                
                self.status_label.config(text=f"⏳ Executando: {script['name']}")
                self.progress_label.config(text=f"{idx}/{total}")
                
                self._log_output(
                    f"\n[{idx}/{total}] ▶ {script['name']}\n"
                    f"Arquivo: {script['file']}\n"
                    f"{'-'*60}",
                    "info"
                )
                
                # Executar script
                # Preparar callback apenas se deve mostrar output
                output_callback = (
                    (lambda out: self._log_output(out, "info"))
                    if script.get("show_output") else None
                )
                
                success = self.executor.execute(
                    script["file"],
                    timeout=script.get("timeout"),
                    output_callback=output_callback,
                    error_callback=lambda err: self._log_output(err, "error"),
                )
                
                if success:
                    self._log_output(f"✅ {script['name']} concluído com sucesso!", "success")
                else:
                    self._log_output(
                        f"❌ ERRO: {script['name']} falhou. Pipeline interrompido.",
                        "error"
                    )
                    self.status_label.config(text="❌ Erro na execução")
                    return
            
            self._log_output(
                f"\n{'='*60}\n"
                f"✅ PIPELINE FINALIZADO COM SUCESSO!\n"
                f"{'='*60}\n",
                "success"
            )
            self.status_label.config(text="✅ Pipeline finalizado", foreground="green")
            
        except Exception as e:
            self._log_output(f"❌ Erro crítico: {str(e)}", "error")
            self.status_label.config(text="❌ Erro crítico", foreground="red")
        finally:
            self.is_executing = False
            self.btn_run.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            self._save_config()
    
    def _stop_execution(self):
        """Para execução atual"""
        self.is_executing = False
        self.executor.stop()
        self._log_output("⏹ Parando execução...", "warning")
    
    def _run_servers(self):
        """Inicia servidores selecionados"""
        selected_servers = [
            s for s in PipelineConfig.SERVERS
            if self.server_vars.get(s["id"], tk.BooleanVar()).get()
        ]
        
        if not selected_servers:
            messagebox.showwarning("Aviso", "Selecione pelo menos um servidor!")
            return
        
        self._log_output(
            f"\n{'='*60}\n"
            f"🚀 INICIANDO SERVIDORES\n"
            f"{'='*60}\n",
            "header"
        )
        
        for server in selected_servers:
            self._start_server(server)
    
    def _start_server(self, server: Dict):
        """Inicia um servidor específico em thread separada"""
        def run_server_thread():
            try:
                self._log_output(
                    f"\n[SERVIDOR] ▶ {server['name']}\n"
                    f"Comando: {server['command']}\n"
                    f"Diretório: {server['cwd_relative']}\n"
                    f"{'-'*60}",
                    "info"
                )
                
                # Resolver caminho absoluto
                cwd = os.path.normpath(os.path.join(self.base_path, server['cwd_relative']))
                
                # Criar executor específico para este servidor
                executor = ScriptExecutor(self.base_path)
                
                # Executar comando
                success = executor.execute_command(
                    server["command"],
                    cwd=cwd,
                    output_callback=lambda out: self._log_output(out, "info"),
                    error_callback=lambda err: self._log_output(err, "error"),
                )
                
                if success:
                    self._log_output(f"✅ {server['name']} finalizado", "success")
                else:
                    self._log_output(f"⚠️  {server['name']} interrompido", "warning")
                    
            except Exception as e:
                self._log_output(f"❌ Erro ao iniciar {server['name']}: {str(e)}", "error")
        
        thread = threading.Thread(target=run_server_thread, daemon=True)
        thread.start()
        self.server_processes[server["id"]] = thread
    
    def _stop_servers(self):
        """Para todos os servidores"""
        self._log_output("\n🛑 Parando todos os servidores...", "warning")
        # Os servidores serão interrompidos quando o usuário fechar a GUI
        # ou manualmente via Ctrl+C nos terminais
    
    def _open_output_folder(self):
        """Abre pasta de output"""
        output_path = os.path.join(self.base_path, "output")
        if os.path.exists(output_path):
            os.startfile(output_path)
        else:
            messagebox.showinfo("Info", "Pasta 'output' não encontrada ainda.")
    
    def _clear_logs(self):
        """Limpa logs"""
        self.output_text.delete("1.0", tk.END)
        self._log_output("📋 Logs limpos", "info")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = PipelineGUI(root)
    root.mainloop()
