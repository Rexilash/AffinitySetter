import tkinter as tk
from tkinter import ttk
import psutil

class AffinitySetterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Affinity Setter")
        self.root.geometry("380x280")
        self.root.resizable(False, False)

        self.cpu_count = psutil.cpu_count(logical=True) or 4
        self.process_map = {}

        # --- UI Elements ---
        
        # Process Selector Label & Dropdown
        frame_proc = tk.Frame(root)
        frame_proc.pack(pady=(15, 0))
        
        tk.Label(frame_proc, text="Select Running Process:", font=("Arial", 10)).pack(anchor="w")
        
        self.combo_proc = ttk.Combobox(frame_proc, state="readonly", width=28, font=("Arial", 10))
        self.combo_proc.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_refresh = tk.Button(frame_proc, text="🔄", font=("Arial", 10), command=self.refresh_process_list)
        self.btn_refresh.pack(side=tk.LEFT)

        # Core Count Spinbox
        tk.Label(root, text=f"Number of Cores to Use (Max: {self.cpu_count}):", font=("Arial", 10)).pack(pady=(15, 0))
        
        self.spin_cores = tk.Spinbox(root, from_=1, to=self.cpu_count, font=("Arial", 10), width=10, state="normal")
        default_cores = min(8, self.cpu_count)
        self.spin_cores.delete(0, tk.END)
        self.spin_cores.insert(0, str(default_cores))
        self.spin_cores.pack(pady=5)

        # Apply Button
        self.btn_apply = tk.Button(root, text="Set Affinity Now", font=("Arial", 10, "bold"), bg="#d1e7dd", fg="#0f5132", width=22, command=self.apply_affinity)
        self.btn_apply.pack(pady=15)

        # Status Label
        self.lbl_status = tk.Label(root, text="Status: Ready", font=("Arial", 9), fg="#6c757d")
        self.lbl_status.pack(pady=5)

        # Populate process list initially
        self.refresh_process_list()

    def refresh_process_list(self):
        try:
            self.process_map.clear()
            display_list = []
            
            for p in psutil.process_iter(['name', 'pid']):
                try:
                    name = p.info['name']
                    pid = p.info['pid']
                    if name:
                        display_text = f"{name} (PID: {pid})"
                        display_list.append(display_text)
                        self.process_map[display_text] = pid
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            sorted_list = sorted(display_list, key=str.lower)
            self.combo_proc['values'] = sorted_list
            
            self.lbl_status.config(text="Status: Process list refreshed.", fg="#6c757d")
        except Exception as e:
            self.lbl_status.config(text=f"Error refreshing list: {e}", fg="red")

    def apply_affinity(self):
        selected_text = self.combo_proc.get().strip()
        if not selected_text or selected_text not in self.process_map:
            self.lbl_status.config(text="Status: Please select a valid process!", fg="red")
            return

        pid = self.process_map[selected_text]
        
        try:
            count = int(self.spin_cores.get())
            count = max(1, min(count, self.cpu_count))
            target_cores = list(range(count))

            p = psutil.Process(pid)
            p.cpu_affinity(target_cores)
            
            self.lbl_status.config(text=f"Success! Set affinity to {count} cores for PID {pid}.", fg="#0f5132")
        except psutil.NoSuchProcess:
            self.lbl_status.config(text="Status: Process no longer exists. Refresh list.", fg="red")
        except Exception as e:
            self.lbl_status.config(text=f"Status: Error - {e}", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = AffinitySetterApp(root)
    root.mainloop()