import tkinter as tk
from tkinter import ttk
import os
import configparser
import pyperclip

class ChatLogViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Endless-Online Log View")
        self.root.geometry("1302x983")

        config = configparser.ConfigParser()
        config.read("config.ini")

        self.log_file_path = config.get('DEFAULT', 'ChatLogFilePath')
        self.log_data = []
        self.last_modified = 0  # Initialize last_modified attribute
        self.click_count = 0  # Initialize click count
        self.total_exp = 0  # Initialize total experience

        self.create_widgets()
        self.load_chat_log(self.log_file_path)
        self.start_auto_refresh()  # Start auto-refresh after creating widgets

    def start_auto_refresh(self, interval=1000):
        try:
            last_modified = os.path.getmtime(self.log_file_path)
            if last_modified != self.last_modified:  # Check if file has been modified
                self.last_modified = last_modified
                self.load_chat_log(self.log_file_path)  # Reload chat log if modified
        except FileNotFoundError:
            print("Chat log file not found.")
        
        self.root.after(interval, self.start_auto_refresh)

    def load_chat_log(self, file_path):
        try:
            with open(file_path, "r") as file:
                self.log_data = file.readlines()

                # Calculate total experience
                for log in self.log_data:
                    if "-s" in log and "Gained" in log and "exp" in log:
                        exp_gained = int(log.split("+")[1].split("exp")[0].strip())  # Extract the amount of experience gained
                        self.total_exp += exp_gained  # Add the experience gained to the total
        except FileNotFoundError:
            print("Chat log file not found.")
        finally:
            self.update_widgets()
        
    def create_widgets(self):
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Create tabs
        self.all_tab = ttk.Frame(self.notebook)
        self.global_tab = ttk.Frame(self.notebook)
        self.whisper_tab = ttk.Frame(self.notebook)
        self.system_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.all_tab, text="[ALL]")
        self.notebook.add(self.global_tab, text="[GLOBAL]")
        self.notebook.add(self.whisper_tab, text="[WHISPER]")
        self.notebook.add(self.system_tab, text="[SYSTEM]")

        # Create label for total experience in the system tab
        self.exp_label = tk.Label(self.system_tab, text=f"Total EXP: {self.total_exp}")
        self.exp_label.pack()

        # Create text boxes for each tab
        self.all_text = tk.Text(self.all_tab, wrap="word", state="normal", foreground="black")
        self.all_text.pack(fill="both", expand=True)
        self.all_text.bind("<Double-Button-1>", self.show_sender_messages)  # Bind double click event

        self.global_text = tk.Text(self.global_tab, wrap="word", state="normal", foreground="black")
        self.global_text.pack(fill="both", expand=True)

        self.whisper_text = tk.Text(self.whisper_tab, wrap="word", state="normal", foreground="black")
        self.whisper_text.pack(fill="both", expand=True)

        self.system_text = tk.Text(self.system_tab, wrap="word", state="normal", foreground="black")
        self.system_text.pack(fill="both", expand=True)

        # Populate text boxes with log data
        for log in self.log_data:
            if "-s" in log:  # Check if it's a system message
                self.all_text.insert(tk.END, log, "system")
                self.system_text.insert(tk.END, log, "system")  # Insert system message with yellow color
            elif "-w" in log:  # Check if it's a whisper message
                self.all_text.insert(tk.END, log, "whisper")
                self.whisper_text.insert(tk.END, log, "whisper")
            else:
                self.all_text.insert(tk.END, log)
                self.global_text.insert(tk.END, log)

        # Configure tag for system messages to color them yellow
        self.all_text.tag_configure("system", foreground="blue")
        self.system_text.tag_configure("system", foreground="blue")

        # Configure tag for whisper messages
        self.all_text.tag_configure("whisper", foreground="green")
        self.whisper_text.tag_configure("whisper", foreground="green")
    
    def update_widgets(self):
        # Clear the existing text boxes
        self.all_text.delete(1.0, tk.END)
        self.global_text.delete(1.0, tk.END)
        self.whisper_text.delete(1.0, tk.END)
        self.system_text.delete(1.0, tk.END)

        # Update total experience label
        self.exp_label.config(text=f"Total EXP: {self.total_exp}")

        # Populate text boxes with new log data
        for log in self.log_data:
            if "-s" in log:  # Check if it's a system message
                self.all_text.insert(tk.END, log, "system")
                self.system_text.insert(tk.END, log, "system")
            elif "-w" in log:  # Check if it's a whisper message
                self.all_text.insert(tk.END, log, "whisper")
                self.whisper_text.insert(tk.END, log, "whisper")
            else:
                self.all_text.insert(tk.END, log)
                self.global_text.insert(tk.END, log)

    def show_sender_messages(self, event):
        # Get the line where the double-click occurred
        line_num = int(self.all_text.index(tk.INSERT).split('.')[0])
        line_text = self.all_text.get(f"{line_num}.0", f"{line_num}.end")

        # Extract sender from the line text
        if " > " in line_text:
            sender = line_text.split(" > ")[1].split()[0]
        else:
            return  # If the line text doesn't contain " > ", it's not a valid log message, so return

        # Create a new window to show messages from the sender
        sender_window = tk.Toplevel(self.root)
        sender_window.title(f"Messages from {sender}")
        sender_window.geometry("800x600")
        sender_window.iconbitmap("icon1.ico")
        sender_text = tk.Text(sender_window, wrap="word", state="normal", foreground="black")
        sender_text.pack(fill="both", expand=True)

        # Create and bind the "Copy All" button
        copy_button = tk.Button(sender_window, text="Copy All", command=lambda: self.copy_all(sender_text))
        copy_button.pack()

        # Filter messages from the sender and display them in the new window
        for log in self.log_data:
            if log.split(" > ")[1].startswith(sender + " "):  # Check if the log message starts with the sender's name
                sender_text.insert(tk.END, log)

    def copy_all(self, text_widget):
        """Copy all text from the provided text widget to the system clipboard."""
        copied_text = text_widget.get(1.0, tk.END)
        pyperclip.copy(copied_text)

def main():
    root = tk.Tk()
    app = ChatLogViewer(root)

    icon_path = "icon1.ico"  # Replace "path_to_your_icon.ico" with the path to your icon file
    root.iconbitmap(icon_path)

    root.mainloop()

if __name__ == "__main__":
    main()
