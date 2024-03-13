import tkinter as tk
from tkinter import ttk
import os
import configparser
import pyperclip
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime
class ChatLogViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Endless-Online Log View")
        self.root.geometry("1800x983")

        config = configparser.ConfigParser()
        config.read("config.ini")

        self.log_file_path = config.get('DEFAULT', 'ChatLogFilePath')
        self.log_data = []
        self.last_modified = 0  # Initialize last_modified attribute
        self.click_count = 0  # Initialize click count
        self.total_exp = 0  # Initialize total experience
        self.monsters_killed = Counter()  # Counter to track monsters killed

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

                # Calculate total experience and monsters killed
                for log in self.log_data:
                    if "-s" in log and "Gained" in log and "exp" in log:
                        exp_gained = int(log.split("+")[1].split("exp")[0].strip())  # Extract the amount of experience gained
                        self.total_exp += exp_gained  # Add the experience gained to the total
                        if "from" in log:
                            parts = log.split("from")[1].split(",")
                            monster = parts[0].strip()
                            self.monsters_killed[monster] += 1  # Increment kill count for the monster
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
        self.kills_tab = ttk.Frame(self.notebook)  # New tab for kills

    # Add tabs to notebook
        self.notebook.add(self.all_tab, text="[ALL]")
        self.notebook.add(self.global_tab, text="[GLOBAL]")
        self.notebook.add(self.whisper_tab, text="[WHISPER]")
        self.notebook.add(self.system_tab, text="[SYSTEM]")
        self.notebook.add(self.kills_tab, text="[Kills]")  # New tab for kills

    # Create label for total experience in the system tab
        self.exp_label = tk.Label(self.system_tab, text=f"Total EXP: {self.total_exp}")
        self.exp_label.pack()

    # Create text boxes for each tab
        self.all_text = tk.Text(self.all_tab, wrap="word", state="normal", foreground="black")
        self.all_text.pack(fill="both", expand=True)

        self.global_text = tk.Text(self.global_tab, wrap="word", state="normal", foreground="black")
        self.global_text.pack(fill="both", expand=True)

        self.whisper_text = tk.Text(self.whisper_tab, wrap="word", state="normal", foreground="black")
        self.whisper_text.pack(fill="both", expand=True)

        self.system_text = tk.Text(self.system_tab, wrap="word", state="normal", foreground="black")
        self.system_text.pack(fill="both", expand=True)

        self.kills_text = tk.Text(self.kills_tab, wrap="word", state="normal", foreground="black")  # Text widget for kills
        self.kills_text.pack(fill="both", expand=True)

        self.import_button = tk.Button(self.root, text="Import Chat Logs", command=self.import_chat_logs)
        self.import_button.pack()
    # Populate text boxes with log data
        self.update_widgets()


    def update_widgets(self):
        # Clear the existing text boxes
        if hasattr(self, 'all_text'):
            self.all_text.delete(1.0, tk.END)
        if hasattr(self, 'global_text'):
            self.global_text.delete(1.0, tk.END)
        if hasattr(self, 'whisper_text'):
            self.whisper_text.delete(1.0, tk.END)
        if hasattr(self, 'system_text'):
            self.system_text.delete(1.0, tk.END)
        if hasattr(self, 'kills_text'):
            self.kills_text.delete(1.0, tk.END)

        # Update total experience label
        self.exp_label.config(text=f"Total EXP: {self.total_exp}")

        # Populate text boxes with new log data
        for log in self.log_data:
            if "-s" in log:  # Check if it's a system message
                if hasattr(self, 'all_text'):
                    self.all_text.insert(tk.END, log, "system")
                if hasattr(self, 'system_text'):
                    self.system_text.insert(tk.END, log, "system")
            elif "-w" in log:  # Check if it's a whisper message
                if hasattr(self, 'all_text'):
                    self.all_text.insert(tk.END, log, "whisper")
                if hasattr(self, 'whisper_text'):
                    self.whisper_text.insert(tk.END, log, "whisper")
            else:
                if hasattr(self, 'all_text'):
                    self.all_text.insert(tk.END, log)
                if hasattr(self, 'global_text'):
                    self.global_text.insert(tk.END, log)

        # Generate top 10 monsters killed list and plot
        self.generate_top_10_monsters_killed()

    def generate_top_10_monsters_killed(self):
        # Get top 10 monsters killed
        top_10 = self.monsters_killed.most_common(10)

        # Clear existing text in the kills tab
        self.kills_text.delete(1.0, tk.END)

        # Display top 10 monsters killed in the kills tab
        self.kills_text.insert(tk.END, "Top 10 Monsters Killed:\n")
        for monster, count in top_10:
            self.kills_text.insert(tk.END, f"{monster}: {count}\n")

        # Plot top 10 monsters killed
        if top_10:
            plt.figure(figsize=(10, 6))
            monsters, counts = zip(*top_10)
            plt.barh(range(len(top_10)), counts, tick_label=monsters, color='skyblue')
            plt.xlabel('Number of Kills')
            plt.ylabel('Monsters')
            plt.title('Top 10 Monsters Killed')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.show()

    
    
    def import_chat_logs(self):
        # Open a file dialog to select chat log files for import
        file_paths = tk.filedialog.askopenfilenames(title="Select Chat Log Files", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
        
        if file_paths:
            imported_logs = []

            # Read and append logs from each selected file
            for file_path in file_paths:
                try:
                    with open(file_path, "r") as file:
                        imported_logs.extend(file.readlines())
                except FileNotFoundError:
                    print(f"File not found: {file_path}")

            # Combine the imported logs with the current log data
            combined_logs = self.log_data + imported_logs

            # Sort the combined logs by timestamp (oldest to newest)
            combined_logs.sort(key=lambda x: datetime.strptime(x.split(" ")[0], "%m/%d/%Y"))

            # Save the combined logs to the chat log file
            with open(self.log_file_path, "w") as file:
                file.writelines(combined_logs)

            # Reload chat log with combined data
            self.load_chat_log(self.log_file_path)



    
def main():
    root = tk.Tk()
    root.iconbitmap("icon1.ico")

    app = ChatLogViewer(root)
    app.import_chat_logs()

    root.mainloop()

if __name__ == "__main__":
    main()
