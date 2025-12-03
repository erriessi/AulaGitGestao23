# -*- coding: utf-8 -*-
import threading
import socket

# Lista de clientes conectados ao servidor
clients = []
username_conection = {}

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
        
        
    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg='#34495e', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🖥️ Servidor de Chat", 
                        font=('Arial', 18, 'bold'), bg='#34495e', fg='white')
        title.pack(pady=10)
        
        # Frame de controle
        control_frame = tk.Frame(header, bg='#34495e')
        control_frame.pack(fill='x', padx=20)
        
        tk.Label(control_frame, text="Porta:", font=('Arial', 10), 
                bg='#34495e', fg='white').pack(side='left', padx=(0, 5))
        
        self.port_entry = tk.Entry(control_frame, font=('Arial', 10), width=10)
        self.port_entry.insert(0, "7777")
        self.port_entry.pack(side='left', padx=(0, 10))
        
        self.start_btn = tk.Button(control_frame, text="▶️ Iniciar Servidor", 
                                   font=('Arial', 10, 'bold'), bg='#27ae60', fg='white',
                                   cursor='hand2', padx=15, pady=5,
                                   command=self.start_server)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Parar Servidor", 
                                 font=('Arial', 10, 'bold'), bg='#e74c3c', fg='white',
                                 cursor='hand2', padx=15, pady=5, state='disabled',
                                 command=self.stop_server)
        self.stop_btn.pack(side='left', padx=5)
        
        self.status_label = tk.Label(control_frame, text="⚫ Offline", 
                                     font=('Arial', 10, 'bold'), bg='#34495e', fg='#e74c3c')
        self.status_label.pack(side='right')
        
        # Container principal
        main_container = tk.Frame(self.root, bg='#2c3e50')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame esquerdo - Logs
        left_frame = tk.Frame(main_container, bg='#2c3e50')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        tk.Label(left_frame, text="📋 Log do Servidor", font=('Arial', 12, 'bold'), 
                bg='#2c3e50', fg='white').pack(anchor='w', pady=(0, 5))
        
        self.log_area = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, 
                                                  font=('Courier', 9), 
                                                  bg='#1a1a1a', fg='#00ff00',
                                                  state='disabled')
        self.log_area.pack(fill='both', expand=True)
        
        # Frame direito - Usuários conectados
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
        
    def log(self, message, msg_type="info"):
        """Exibe mensagens no log"""
        self.log_area.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if msg_type == "info":
            prefix = "ℹ️"
        elif msg_type == "warning":
            prefix = "⚠️"
        elif msg_type == "error":
            prefix = "❌"
        elif msg_type == "success":
            prefix = "✅"
        else:
            prefix = "📝"
            
        self.log_area.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.log_area.config(state='disabled')
        self.log_area.see(tk.END)
        
    def update_users_list(self):
        """Atualiza a lista de usuários online"""
        self.users_listbox.delete(0, tk.END)
        for username in self.username_connection.keys():
            self.users_listbox.insert(tk.END, f"🟢 {username}")
        self.user_count_label.config(text=f"Total: {len(self.username_connection)}")
        
    def start_server(self):
        """Inicia o servidor"""
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
            
            self.log(f"Iniciou o servidor de bate-papo na porta {port}", "success")
            
            # Thread para aceitar conexões
            thread = threading.Thread(target=self.accept_connections, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível iniciar o servidor!\n\n{str(e)}")
            self.log(f"Erro ao iniciar: {str(e)}", "error")
            
    def stop_server(self):
        """Para o servidor"""
        self.running = False
        
        for client in self.clients[:]:
            try:
                client.close()
            except:
                pass
                
        if self.server:
            try:
                self.server.close()
            except:
                pass
                
        self.clients.clear()
        self.username_connection.clear()
        self.update_users_list()
        
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.port_entry.config(state='normal')
        self.status_label.config(text="⚫ Offline", fg='#e74c3c')
        
        self.log("Servidor parado", "warning")
        
    def accept_connections(self):
        """Aceita novas conexões de clientes"""
        while self.running:
            try:
                self.server.settimeout(1.0)
                client, addr = self.server.accept()
                self.clients.append(client)
                
                self.log(f"Cliente conectado. IP: {addr}", "success")
                
                # Thread para lidar com o cliente
                thread = threading.Thread(target=self.handle_client, args=(client,), daemon=True)
                thread.start()
                
            except socket.timeout:
                continue
            except:
                if self.running:
                    self.log("Erro ao aceitar conexão", "error")
                break
                
    def handle_client(self, client):
        """Gerencia mensagens de um cliente"""
        username = None
        try:
            usr = client.recv(2048).decode('utf-8')
            username = usr.strip('')
            self.username_connection[username] = client

            self.log(f"Novo usuário: {username}", "info")
            self.update_users_list()

            while self.running:
                msg = client.recv(2048).decode('utf-8')
                if not msg:
                    break

                self.log(f"Recebido: {msg}", "message")

                # -----------------------------------
                #  DETECTA MENSAGEM PRIVADA
                # -----------------------------------
                if msg.startswith("PRIVATE "):
                    try:
                        _, payload = msg.split(" ", 1)
                        target, content = payload.split("|", 1)
                        sender, message_text = content.split(" ", 1)

                        self.send_private_message(sender, target, message_text)

                    except Exception as e:
                        self.log(f"Erro ao processar mensagem privada: {e}", "error")
                    continue

                # Mensagem normal (broadcast)
                parts = msg.split(' ', 1)
                if len(parts) < 2:
                    continue

                src = parts[0]
                message_content = parts[1]

                self.broadcast(f'{src}: {message_content}'.encode('utf-8'), client)

        except:
            pass
        finally:
            self.remove_client(client, username)
            
    def send_private_message(self, sender, target, message):
        """Envia mensagem privada"""
        if target not in self.username_connection:
            self.log(f"Privado falhou: {target} não está online.", "warning")
            return

        try:
            dst_conn = self.username_connection[target]
            formatted = f"PRIVATE {sender}|{message}"
            dst_conn.send(formatted.encode('utf-8'))

            self.log(f"[PRIVADO] {sender} -> {target}: {message}", "info")

        except:
            self.log(f"Erro ao enviar privado para {target}", "error")
                
    def broadcast(self, msg, sender):
        """Transmite para todos menos o remetente"""
        for client in self.clients:
            if client != sender:
                try:
                    client.send(msg)
                except:
                    self.remove_client(client, None)
                    
    def remove_client(self, client, username):
        """Remove cliente desconectado"""
        if client in self.clients:
            self.clients.remove(client)
            
        if username and username in self.username_connection:
            del self.username_connection[username]
            self.log(f"Usuário '{username}' desconectado", "warning")
            self.update_users_list()
            
        try:
            client.close()
        except:
            pass

# Função para transmitir mensagens para todos os clientes
def send_to_user(src, dst, msg, sender):
  if(dst in username_conection.keys()):
    dst_conn = username_conection[dst]
    try:
      dst_conn.send(f'<{src}> {msg}'.encode('utf-8'))
    except:
      pass
  
# Função para transmitir mensagens para todos os clientes
def broadcast(msg, sender):
  for client in clients:
      if client != sender:
          try:
              client.send(msg)
          except:
              remove_client(client)

# Função para enviar a lista de usuários
def send_user_list(client):
   print("debug")
   users = '\n'.join(username_conection.keys())
   client.send(f'{users}'.encode('utf-8'))
   

# Função para remover um cliente da lista
def remove_client(client):
  clients.remove(client)

# Função principal
def main():
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  print("Iniciou o servidor de bate-papo")

  try:
      server.bind(("0.0.0.0", 7777))
      server.listen()
  except:
      return print('\nNão foi possível iniciar o servidor!\n')

  while True:
      client, addr = server.accept()
      clients.append(client)
      print(f'Cliente conectado com sucesso. IP: {addr}')

      # Inicia uma nova thread para lidar com as mensagens do cliente
      thread = threading.Thread(target=handle_client, args=(client,))
      thread.start()

# Executa o programa
main()
