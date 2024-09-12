import tkinter as tk
from tkinter import messagebox
import subprocess

class ServiceManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Service Manager")

        # Service Files Paths
        self.service_files = {
            'file_consumer': '/etc/systemd/system/file_consumer.service',
            'ultrassonic_file_producer': '/etc/systemd/system/ultrassonic_file_producer.service',
            'image_file_producer': '/etc/systemd/system/image_file_producer.service',
        }

        # Buttons
        tk.Button(root, text="Copy Service Files", command=self.copy_service_files).pack(pady=5)
        tk.Button(root, text="Enable Services", command=self.enable_services).pack(pady=5)
        tk.Button(root, text="Start Services", command=self.start_services).pack(pady=5)
        tk.Button(root, text="Stop Services", command=self.stop_services).pack(pady=5)
        tk.Button(root, text="Status of Services", command=self.check_status).pack(pady=5)

    def run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            messagebox.showinfo("Success", result.stdout.decode())
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", e.stderr.decode())

    def copy_service_files(self):
        try:
            for service_name, dest_path in self.service_files.items():
                source_path = f"./{service_name}.service"
                subprocess.run(f"sudo cp {source_path} {dest_path}", shell=True, check=True)
            messagebox.showinfo("Success", "Service files copied successfully.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", e.stderr.decode())

    def enable_services(self):
        services = ' '.join(self.service_files.keys())
        self.run_command(f"sudo systemctl enable {services}")

    def start_services(self):
        services = ' '.join(self.service_files.keys())
        self.run_command(f"sudo systemctl start {services}")

    def stop_services(self):
        services = ' '.join(self.service_files.keys())
        self.run_command(f"sudo systemctl stop {services}")

    def check_status(self):
        statuses = []
        for service_name in self.service_files.keys():
            status = subprocess.run(f"sudo systemctl status {service_name}", shell=True, capture_output=True, text=True)
            statuses.append(status.stdout)
        messagebox.showinfo("Service Status", "\n\n".join(statuses))

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceManagerApp(root)
    root.mainloop()
