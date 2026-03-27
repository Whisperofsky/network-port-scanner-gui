import socket
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Dictionary of common ports
COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
    443: "HTTPS", 3306: "MySQL", 3389: "RDP",
    5900: "VNC", 8080: "HTTP-Alt"
}

class PortScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Port Scanner GUI")

        # Input fields
        tk.Label(root, text="Target Host/IP:").grid(row=0, column=0, sticky="w")
        self.target_entry = tk.Entry(root, width=30)
        self.target_entry.grid(row=0, column=1)

        tk.Label(root, text="Start Port:").grid(row=1, column=0, sticky="w")
        self.start_port_entry = tk.Entry(root, width=10)
        self.start_port_entry.insert(0, "1")
        self.start_port_entry.grid(row=1, column=1)

        tk.Label(root, text="End Port:").grid(row=2, column=0, sticky="w")
        self.end_port_entry = tk.Entry(root, width=10)
        self.end_port_entry.insert(0, "1024")
        self.end_port_entry.grid(row=2, column=1)

        # Buttons
        self.start_button = tk.Button(root, text="Start Scan", command=self.start_scan)
        self.start_button.grid(row=3, column=0, pady=5)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_scan)
        self.stop_button.grid(row=3, column=1, pady=5)

        self.save_button = tk.Button(root, text="Save Results", command=self.save_results)
        self.save_button.grid(row=3, column=2, pady=5)

        # Results pane
        self.results = tk.Text(root, height=15, width=60)
        self.results.grid(row=4, column=0, columnspan=3)

        # Progress bar
        self.progress = ttk.Progressbar(root, length=300, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, pady=5)

        self.stop_flag = False
        self.open_ports = []

    def scan_port(self, host, port):
        if self.stop_flag:
            return
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((host, port))
            if result == 0:
                service = COMMON_PORTS.get(port, "Unknown")
                self.results.insert(tk.END, f"Port {port}: OPEN ({service})\n")
                self.open_ports.append((port, service))
            sock.close()
        except Exception:
            pass
        finally:
            self.progress.step(1)

    def start_scan(self):
        self.results.delete(1.0, tk.END)
        self.open_ports.clear()
        self.stop_flag = False

        host = self.target_entry.get()
        start_port = int(self.start_port_entry.get())
        end_port = int(self.end_port_entry.get())

        total_ports = end_port - start_port + 1
        self.progress["maximum"] = total_ports
        self.progress["value"] = 0

        for port in range(start_port, end_port + 1):
            t = threading.Thread(target=self.scan_port, args=(host, port))
            t.start()

    def stop_scan(self):
        self.stop_flag = True
        messagebox.showinfo("Stopped", "Scan stopped by user.")

    def save_results(self):
        if not self.open_ports:
            messagebox.showwarning("No Results", "No open ports to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, "w") as f:
                for port, service in self.open_ports:
                    f.write(f"Port {port}: OPEN ({service})\n")
            messagebox.showinfo("Saved", f"Results saved to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PortScannerGUI(root)
    root.mainloop()