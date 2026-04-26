import threading
from socket import *
import os

import customtkinter
from customtkinter import *

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')
        self.title('йооооо')

        self.label = None

        # menu frame
        self.menu_frame = CTkFrame(self, width=30, height=300, fg_color="#05668d")
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        self.is_show_menu = False
        self.speed_animate_menu = -5

        self.btn = CTkButton(self, text='👉', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)

        # чат
        self.chat_field = CTkTextbox(self, font=('Roboto', 14, 'bold'), state='disabled')
        self.chat_field.place(x=0, y=0)

        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення☺️:', height=40,
                                     fg_color="#b4d1dd")
        self.message_entry.place(x=0, y=0)

        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
        self.send_button.place(x=0, y=0)

        # === ІСТОРІЯ ===
        self.history = []
        self.history_dir = "chat_history"
        self.history_file = os.path.join(self.history_dir, "history.txt")
        os.makedirs(self.history_dir, exist_ok=True)

        # кнопка завантаження
        self.load_button = CTkButton(self, text='📂', width=40, command=self.load_history)
        self.load_button.place(x=50, y=0)

        # username + socket
        self.username = 'Artem1'
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 1111))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

        # закриття
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.adaptive_ui()

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='👉')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='👈')
            self.show_menu()

            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack()

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width(),
                                  height=self.winfo_height() - 40)

        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)

        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())

        self.after(50, self.adaptive_ui)

    def add_message(self, text):
        self.history.append(text)
        self.chat_field.configure(state='normal')
        self.chat_field.insert(END, text + '\n')
        self.chat_field.configure(state='disabled')

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                self.add_message(f"{author} надіслав(ла) зображення: {filename}")
        else:
            self.add_message(line)

    # === ЗБЕРЕЖЕННЯ ===
    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                for line in self.history:
                    f.write(line + "\n")
        except Exception as e:
            print("Помилка збереження:", e)

    def load_history(self):
        if not os.path.exists(self.history_file):
            self.add_message("[SYSTEM] Історія відсутня")
            return

        self.chat_field.configure(state='normal')
        self.chat_field.delete("1.0", END)

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.chat_field.insert(END, line + "\n")
            self.chat_field.configure(state='disabled')
        except Exception as e:
            self.add_message(f"[SYSTEM] Помилка завантаження: {e}")

    def on_close(self):
        self.save_history()
        try:
            self.sock.close()
        except:
            pass
        self.destroy()


win = MainWindow()
win.mainloop()