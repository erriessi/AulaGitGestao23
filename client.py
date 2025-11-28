# -*- coding: utf-8 -*-
import threading
import socket
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime


class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")
        self.root.geometry("700x600")
        self.root.configure(bg='#2c3e50')
        
        self.client = None
        self.connected = False
        self.username = ""
        
        self.create_connection_frame()
        self.create_chat_frame()
        
    def create_connection_frame(self):
        self.connection_frame = tk.Frame(self.root, bg='#34495e', padx=20, pady=20)
        self.connection_frame.pack(fill='both', expand=True)
        
        title = tk.Label(self.connection_frame, text="🔌 Conectar ao Servidor", 
                        font=('Arial', 18, 'bold'), bg='#34495e', fg='white')
        title.pack(pady=(0, 20))
        
        tk.Label(self.connection_frame, text="IP do Servidor:", 
                font=('Arial', 11), bg='#34495e', fg='white').pack(anchor='w', pady=(0, 5))
        self.ip_entry = tk.Entry(self.connection_frame, font=('Arial', 11), width=40)
        self.ip_entry.insert(0, "192.168.10.52")
        self.ip_entry.pack(pady=(0, 15))
        
        tk.Label(self.connection_frame, text="Porta:", 
                font=('Arial', 11), bg='#34495e', fg='white').pack(anchor='w', pady=(0, 5))
        self.port_entry = tk.Entry(self.connection_frame, font=('Arial', 11), width=40)
        self.port_entry.insert(0, "7777")
        self.port_entry.pack(pady=(0, 15))
        
        tk.Label(self.connection_frame, text="Nome de Usuário:", 
                font=('Arial', 11), bg='#34495e', fg='white').pack(anchor='w', pady=(0, 5))
        self.username_entry = tk.Entry(self.connection_frame, font=('Arial', 11), width=40)
        self.username_entry.pack(pady=(0, 20))
        
        self.connect_btn = tk.Button(self.connection_frame, text="Conectar", 
                                     font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                                     cursor='hand2', padx=30, pady=10,
                                     command=self.connect_to_server)
        self.connect_btn.pack()
        
        self.username_entry.bind('<Return>', lambda e: self.connect_to_server())
        
    def create_chat_frame(self):
        self.chat_frame = tk.Frame(self.root, bg='#2c3e50')
        
        header = tk.Frame(self.chat_frame, bg='#34495e', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        self.user_label = tk.Label(header, text="", font=('Arial', 14, 'bold'), 
                                   bg='#34495e', fg='white')
        self.user_label.pack(side='left', padx=20, pady=15)
        
        disconnect_btn = tk.Button(header, text="🔌 Desconectar", 
                                  font=('Arial', 10), bg='#e74c3c', fg='white',
                                  cursor='hand2', command=self.disconnect)
        disconnect_btn.pack(side='right', padx=10)
        
        msg_frame = tk.Frame(self.chat_frame, bg='#2c3e50')
        msg_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.chat_area = scrolledtext.ScrolledText(msg_frame, wrap=tk.WORD, 
                                                   font=('Arial', 10), 
                                                   bg='#ecf0f1', fg='#2c3e50',
                                                   state='disabled')
        self.chat_area.pack(fill='both', expand=True)
        
        input_frame = tk.Frame(self.chat_frame, bg='#34495e', height=80)
        input_frame.pack(fill='x', padx=10, pady=(0, 10))
        input_frame.pack_propagate(False)
        
        msg_input_frame = tk.Frame(input_frame, bg='#34495e')
        msg_input_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.msg_entry = tk.Entry(msg_input_frame, font=('Arial', 11))
        self.msg_entry.pack(side='left', fill='both', expand=True, padx=(0, 10))
        self.msg_entry.bind('<Return>', lambda e: self.send_message())
        self.msg_entry.focus()
        
        send_btn = tk.Button(msg_input_frame, text="Enviar", 
                           font=('Arial', 11, 'bold'), bg='#27ae60', fg='white',
                           cursor='hand2', padx=20, command=self.send_message)
        send_btn.pack(side='right')
        
    def connect_to_server(self):
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        username = self.username_entry.get().strip()
        
        if not username:
            messagebox.showerror("Erro", "Digite um nome de usuário!")
            return
            
        try:
            port = int(port)
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((ip, port))
            
            self.username = username
            self.client.send(f'{username}'.encode('utf-8'))
            
            self.connected = True
            self.connection_frame.pack_forget()
            self.chat_frame.pack(fill='both', expand=True)
            self.user_label.config(text=f"👤 {username}")
            
            thread = threading.Thread(target=self.receive_messages, daemon=True)
            thread.start()
            
            self.display_message("Sistema", "Conectado ao servidor!", "system")
            
        except Exception as e:
            messagebox.showerror("Erro de Conexão", 
                               f"Não foi possível se conectar ao servidor!\n\nDetalhes: {str(e)}")
            
    def receive_messages(self):
        while self.connected:
            try:
                msg = self.client.recv(2048).decode('utf-8')
                
                if msg:

                    # detecta mensagens privadas recebidas
                    if msg.startswith("PRIVATE"):
                        _, payload = msg.split(" ", 1)
                        sender, message = payload.split("|", 1)
                        self.display_message(f"{sender} (privado)", message, "received_private")
                    else:
                        self.display_message("", msg, "received")

            except:
                if self.connected:
                    self.display_message("Sistema", 
                                       "Não foi possível permanecer conectado no servidor!", 
                                       "error")
                    self.connected = False
                break
                
    def send_message(self):
        msg = self.msg_entry.get().strip()

        if not msg:
            return

        try:
            # mensagem privada no formato: @nome mensagem
            if msg.startswith("@") and " " in msg:
                target, content = msg.split(" ", 1)
                target = target[1:]  # remove o @

                full_msg = f"PRIVATE {target}|{self.username} {content}"
                self.client.send(full_msg.encode('utf-8'))

                self.display_message(f"Para {target} (privado)", content, "sent_private")

            else:
                full_msg = f'{self.username} {msg}'
                self.client.send(full_msg.encode('utf-8'))

                self.display_message(self.username, msg, "sent")

            self.msg_entry.delete(0, tk.END)

        except:
            messagebox.showerror("Erro", "Não foi possível enviar a mensagem!")
            self.display_message("Sistema", "Erro ao enviar mensagem!", "error")
                
    def display_message(self, sender, msg, msg_type):
        self.chat_area.config(state='normal')
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if msg_type == "system":
            self.chat_area.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.chat_area.insert(tk.END, f"⚙️ {msg}\n\n", 'system')

        elif msg_type == "error":
            self.chat_area.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.chat_area.insert(tk.END, f"❌ {msg}\n\n", 'error')

        elif msg_type == "sent":
            self.chat_area.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.chat_area.insert(tk.END, f"{sender}: ", 'sender_me')
            self.chat_area.insert(tk.END, f"{msg}\n\n", 'sent')

        elif msg_type == "sent_private":
            self.chat_area.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.chat_area.insert(tk.END, f"{sender}: ", 'private_me')
            self.chat_area.insert(tk.END, f"{msg}\n\n", 'private_msg')

        elif msg_type == "received_private":
            self.chat_area.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.chat_area.insert(tk.END, f"{sender}: ", 'private_from')
            self.chat_area.insert(tk.END, f"{msg}\n\n", 'private_msg')

        else:  # broadcast normal
            self.chat_area.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.chat_area.insert(tk.END, f"{msg}\n\n", 'received')
            
        # Tags de estilo
        self.chat_area.tag_config('timestamp', foreground='#7f8c8d', font=('Arial', 8))
        self.chat_area.tag_config('system', foreground='#3498db', font=('Arial', 10, 'italic'))
        self.chat_area.tag_config('error', foreground='#e74c3c', font=('Arial', 10, 'bold'))
        self.chat_area.tag_config('sender_me', foreground='#27ae60', font=('Arial', 10, 'bold'))
        self.chat_area.tag_config('sent', foreground='#27ae60', font=('Arial', 10))
        self.chat_area.tag_config('received', foreground='#2c3e50', font=('Arial', 10))

        # privado
        self.chat_area.tag_config('private_me', foreground='#8e44ad', font=('Arial', 10, 'bold'))
        self.chat_area.tag_config('private_from', foreground='#9b59b6', font=('Arial', 10, 'bold'))
        self.chat_area.tag_config('private_msg', foreground='#8e44ad', font=('Arial', 10))

        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)
        
    def disconnect(self):
        if self.connected:
            self.connected = False
            try:
                self.client.close()
            except:
                pass
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", app.disconnect)
    root.mainloop()
