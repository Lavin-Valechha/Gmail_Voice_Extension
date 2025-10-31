import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
import time
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Add this helper class for terminal output redirection
class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget
        
    def write(self, text):
        self.widget.configure(state="normal")
        self.widget.insert("end", text)
        self.widget.see("end")
        self.widget.configure(state="disabled")
    
    def flush(self):
        pass

# Ensure the src path is added to import the assistant
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

try:
    from main import VoiceDesktopAssistant
except Exception as e:
    VoiceDesktopAssistant = None
    startup_error = str(e)
else:
    startup_error = None

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-grey")


class AssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gmail Voice Assistant")
        self.root.geometry("900x850")

        self.assistant = None
        self.running = False

        self.build_ui()
        sys.stdout = TextRedirector(self.terminal_box)
        self.safe_initialize_assistant()

    def build_ui(self):
        self.title_label = ctk.CTkLabel(self.root, text="Gmail Voice Assistant", font=("Orbitron", 28))
        self.title_label.pack(pady=20)

        self.theme_switch = ctk.CTkSwitch(self.root, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.pack(pady=5)
        self.theme_switch.select()

        self.status_label = ctk.CTkLabel(self.root, text="Status: 💤 Idle", font=("Consolas", 16))
        self.status_label.pack(pady=5)

        self.command_label = ctk.CTkLabel(self.root, text="🧠 Last Command: None", font=("Consolas", 14))
        self.command_label.pack(pady=5)

        self.transcript_box = ctk.CTkTextbox(self.root, height=60, font=("Consolas", 12))
        self.transcript_box.insert("1.0", "...")
        self.transcript_box.configure(state="disabled")
        self.transcript_box.pack(pady=10, padx=20, fill="x")
        # Terminal Output Box
        self.terminal_box = ctk.CTkTextbox(self.root, height=100, font=("Consolas", 10))
        self.terminal_box.pack(pady=5, padx=20, fill="x")
        self.terminal_box.configure(state="disabled")

        self.log_box = ctk.CTkTextbox(self.root, height=200, font=("Courier", 12))
        self.log_box.insert("1.0", "System Ready. Waiting for interaction.\n")
        self.log_box.configure(state="disabled")
        self.log_box.pack(pady=10, padx=20, fill="both", expand=True)

        self.button_frame = ctk.CTkFrame(self.root)
        self.button_frame.pack(pady=10)

        self.start_button = ctk.CTkButton(self.button_frame, text="▶ Start Assistant", command=self.start_assistant)
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ctk.CTkButton(self.button_frame, text="■ Stop Assistant", command=self.stop_assistant)
        self.stop_button.grid(row=0, column=1, padx=10)

        self.quit_button = ctk.CTkButton(self.button_frame, text="✖ Quit", command=self.root.quit)
        self.quit_button.grid(row=0, column=2, padx=10)

        self.graph_button = ctk.CTkButton(self.root, text="📊 Show Email Count Graph", command=self.show_graph)
        self.graph_button.pack(pady=10)

    def safe_initialize_assistant(self):
        if VoiceDesktopAssistant is None:
            self.log(f"❌ Failed to load assistant: {startup_error}")
            messagebox.showerror("Startup Error", f"VoiceDesktopAssistant could not be initialized.\n\n{startup_error}")
        else:
            try:
                self.assistant = VoiceDesktopAssistant()
                self.log("✅ Assistant initialized successfully.")
            except Exception as e:
                self.assistant = None
                self.log(f"❌ Assistant crashed on init: {e}")
                messagebox.showerror("Initialization Error", f"Failed to start assistant:\n{e}")

    def get_real_email_counts(self):
        """Fetch actual email counts from Gmail labels"""
        if not self.assistant:
            return {}
        
        labels = {
            "INBOX": "Inbox",
            "CATEGORY_PROMOTIONS": "Promotions",
            "CATEGORY_SOCIAL": "Social",
            "CATEGORY_UPDATES": "Updates",
            "TRASH": "Trash",
            "SPAM": "Spam"
        }
        
        counts = {}
        try:
            for label_id, label_name in labels.items():
                # Get count using your existing email reader
                emails = self.assistant.label_reader.fetch_label_emails(label_id)
                counts[label_name] = len(emails) if emails else 0
        except Exception as e:
            print(f"Error fetching email counts: {e}")
            return {}
        
        return counts

    def toggle_theme(self):
        mode = "Dark" if self.theme_switch.get() else "Light"
        ctk.set_appearance_mode(mode)

    def start_assistant(self):
        if self.assistant and not self.running:
            self.running = True
            self.update_status("🟢 Listening")
            self.log("Assistant started. Awaiting commands...")
            threading.Thread(target=self.run_assistant, daemon=True).start()
        elif not self.assistant:
            self.log("❗ Assistant not available. Please check logs.")
            messagebox.showwarning("Not Ready", "Assistant is not initialized correctly.")

    def stop_assistant(self):
        self.running = False
        if self.assistant:
            self.assistant.running = False
        self.update_status("🛑 Stopped")
        self.log("Assistant stopped.")

    def run_assistant(self):
        while self.running and self.assistant and self.assistant.running:
            try:
                command = self.assistant.get_input()
                if command:
                    self.root.after(0, self.update_transcript, command)
                    self.root.after(0, self.command_label.configure, text=f"🧠 Last Command: {command}")
                    self.root.after(0, self.log, f"🗣 {command}")
                    self.assistant.process_command(command)
            except Exception as e:
                self.root.after(0, self.log, f"⚠️ Error during command processing: {e}")
                self.root.after(0, self.update_status, "⚠️ Error")
                break

    def update_status(self, status):
        self.status_label.configure(text=f"Status: {status}")

    def update_transcript(self, text):
        self.transcript_box.configure(state="normal")
        self.transcript_box.delete("1.0", "end")
        self.transcript_box.insert("1.0", text)
        self.transcript_box.configure(state="disabled")

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def show_graph(self):
        """Show real email count graph"""
        if not self.assistant:
            messagebox.showerror("Error", "Assistant not initialized")
            return
        
        # Get real data instead of random
        email_counts = self.get_real_email_counts()
        
        if not email_counts:
            messagebox.showerror("Error", "Could not fetch email data")
            return
        
        # Prepare data for plotting
        labels = list(email_counts.keys())
        counts = list(email_counts.values())
        
        # Create the figure
        fig, ax = plt.subplots()
        bars = ax.bar(labels, counts, color='#3b82f6')
        
        # Add count labels on each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        ax.set_title("Real-Time Email Count by Label")
        ax.set_ylabel("Number of Emails")
        plt.xticks(rotation=45)
        fig.tight_layout()
        
        # Display in Tkinter window
        graph_win = ctk.CTkToplevel(self.root)
        graph_win.geometry("800x500")
        graph_win.title("Email Statistics")
        
        chart = FigureCanvasTkAgg(fig, graph_win)
        chart.get_tk_widget().pack(fill="both", expand=True)
        chart.draw()



if __name__ == "__main__":
    root = ctk.CTk()
    app = AssistantApp(root)
    root.mainloop()
