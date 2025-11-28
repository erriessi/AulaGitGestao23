# -*- coding: utf-8 -*-
import threading
import socket
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime


# ====================================================
# BROADCAST GLOBAL (usado para anunciar entrada)
# ====================================================
def broadcast(msg, ignorar=None):
    """Envia mensagem para todos os clientes EXCETO o ignorado."""
    try:
        for client in app.clients:
            if client != ignorar:
                client.send(msg.encode("utf-8"))
    except:
        pass


class ChatServer:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Server")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')

        self.server = None
        self.clients = []
        self.username_connection = {}
        self.running = False

        self.create_widgets()

    # ---------------------------------------------------------
    # INTERFACE
    # ---------------------------------------------------------
    def create_widgets(self):
        header = tk.Frame(self.root, bg='#34495e', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title = tk.Label(header, text="🖥️ Servidor de Chat",
                         font=('Arial', 18, 'bold'), bg='#34495e', fg='white')
        title.pack(pady=10)

        control_frame = tk.Frame(header, bg='#34495e')
        control_frame.pack(fill='x', padx=20)

        tk.Label(control_frame, text="Porta:", font=('Arial', 10),
                 bg='#34495e', fg='white').pack(side='left', padx=(0, 5))

        self.port_entry = tk.Entry(control_frame, font=('Arial', 10), width=10)
        self.port_entry.insert(0, "7777")
        self.port_entry.pack(side='left', padx=(0, 10))

        self.start_btn = tk.Button(control_frame, text="▶️ Iniciar Servidor",
                                   font=('Arial', 10, 'bold'),
                                   bg='#27ae60', fg='white',
                                   cursor='hand2', padx=15, pady=5,
                                   command=self.start_server)
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = tk.Button(control_frame, text="⏹️ Parar Servidor",
                                  font=('Arial', 10, 'bold'),
                                  bg='#e74c3c', fg='white',
                                  cursor='hand2', padx=15, pady=5,
                                  state='disabled',
                                  command=self.stop_server)
        self.stop_btn.pack(side='left', padx=5)

        self.status_label = tk.Label(control_frame, text="⚫ Offline",
                                     font=('Arial', 10, 'bold'),
                                     bg='#34495e', fg='#e74c3c')
        self.status_label.pack(side='right')

        main_container = tk.Frame(self.root, bg='#2c3e50')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_container, bg='#2c3e50')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        tk.Label(left_frame, text="📋 Log do Servidor", font=('Arial', 12, 'bold'),
                 bg='#2c3e50', fg='white').pack(anchor='w', pady=(0, 5))

        self.log_area = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD,
                                                  font=('Courier', 9),
                                                  bg='#1a1a1a', fg='#00ff00',
                                                  state='disabled')
        self.log_area.pack(fill='both', expand=True)

        right_frame = tk.Frame(main_container, bg='#34495e', width=200)
        right_frame.pack(side='right', fill='y', padx=(5, 0))
        right_frame.pack_propagate(False)

        tk.Label(right_frame, text="👥 Usuários Online", font=('Arial', 11, 'bold'),
                 bg='#34495e', fg='white').pack(pady=10)

        self.users_listbox = tk.Listbox(right_frame, font=('Arial', 10),
                                        bg='#ecf0f1', fg='#2c3e50',
                                        selectmode=tk.SINGLE)
        self.users_listbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.user_count_label = tk.Label(right_frame, text="Total: 0",
                                         font=('Arial', 9), bg='#34495e', fg='#95a5a6')
        self.user_count_label.pack(pady=(0, 10))

    # ---------------------------------------------------------
    # LOG
    # ---------------------------------------------------------
    def log(self, message, msg_type="info"):
        self.log_area.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")

        icons = {
            "info": "ℹ️",
            "message": "💬",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }

        prefix = icons.get(msg_type, "📝")
        self.log_area.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.log_area.config(state='disabled')
        self.log_area.see(tk.END)

    def update_users_list(self):
        self.users_listbox.delete(0, tk.END)
        for username in self.username_connection.keys():
            self.users_listbox.insert(tk.END, f"🟢 {username}")
        self.user_count_label.config(text=f"Total: {len(self.username_connection)}")

    # ---------------------------------------------------------
    # SERVIDOR
    # ---------------------------------------------------------
    def start_server(self):
        try:
            port = int(self.port_entry.get())
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(("0.0.0.0", port))
            self.server.listen()

            self.running = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.port_entry.config(state='disabled')
            self.status_label.config(text="🟢 Online", fg='#27ae60')

            self.log(f"Servidor iniciado na porta {port}", "success")

            threading.Thread(target=self.accept_connections, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Erro", str(e))
            self.log(str(e), "error")

    def stop_server(self):
        self.running = False

        for c in self.clients:
            try: c.close()
            except: pass

        try:
            self.server.close()
        except:
            pass

        self.clients.clear()
        self.username_connection.clear()
        self.update_users_list()
        self.status_label.config(text="⚫ Offline", fg="#e74c3c")
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.port_entry.config(state='normal')

        self.log("Servidor parado", "warning")

    def accept_connections(self):
        while self.running:
            try:
                client, addr = self.server.accept()
                self.clients.append(client)
                self.log(f"Conectado: {addr}", "success")

                threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()

            except:
                continue

    # ---------------------------------------------------------
    # LIDAR COM CLIENTE
    # ---------------------------------------------------------
    def handle_client(self, client):
        username = None
        try:
            usr = client.recv(2048).decode('utf-8')
            username = usr.strip()
            self.username_connection[username] = client

            self.update_users_list()
            self.log(f"Usuário conectado: {username}")

            # ANÚNCIO DE ENTRADA
            broadcast(f"{username} entrou na sala !", ignorar=client)

            while self.running:
                msg = client.recv(2048).decode('utf-8')
                if not msg:
                    break

                # 🔥 AQUI CONSERTEI O LOG DE MENSAGENS
                self.log(f"{username}: {msg}", "message")

                # Envia a todos menos para o remetente
                self.broadcast(f"{username}: {msg}".encode("utf-8"), client)

        except:
            pass

        self.remove_client(client, username)

    # ---------------------------------------------------------
    # ENVIO
    # ---------------------------------------------------------
    def broadcast(self, msg, sender):
        """Broadcast interno do servidor"""
        for client in self.clients:
            if client != sender:
                try:
                    client.send(msg)
                except:
                    self.remove_client(client, None)

    def remove_client(self, client, username):
        if client in self.clients:
            self.clients.remove(client)

        if username in self.username_connection:
            del self.username_connection[username]
            self.log(f"{username} saiu.", "warning")
            broadcast(f"{username} saiu da sala.")
            self.update_users_list()

        try:
            client.close()
        except:
            pass


# ====================================================
# EXECUÇÃO
# ====================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatServer(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_server(), root.destroy()))
    root.mainloop()
