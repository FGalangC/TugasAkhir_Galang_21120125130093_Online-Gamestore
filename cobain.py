import tkinter as tk
from tkinter import ttk, messagebox
import json, os, time

HISTORY_FILE = "history.json"

# ===============================
# QUEUE & STACK
# ===============================

class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.pop(0)

    def is_empty(self):
        return len(self.items) == 0

    def show_all(self):
        return list(self.items)


class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def show_all(self):
        return list(self.items)


# ===============================
# CLASS DOMAIN
# ===============================

class Route:
    def __init__(self, code, name):
        self.code = code
        self.name = name

    def __str__(self):
        return f"{self.code} - {self.name}"


class Driver:
    def __init__(self, did, name):
        self.id = did
        self.name = name
        self.status = "Idle"
        self.current_report = None

    def assign(self, report):
        if self.status != "Idle":
            return False
        self.current_report = report
        self.status = "Handling"
        return True

    def finish(self):
        if not self.current_report:
            return None
        finished = self.current_report
        self.current_report = None
        self.status = "Idle"
        return finished


# ===============================
# DELAY MANAGER
# ===============================

class DelayManager(Queue, Stack):
    def __init__(self):
        Queue.__init__(self)
        Stack.__init__(self)
        self.routes = []
        self.drivers = []
        self.next_driver_id = 1

    def add_route(self, code, name):
        r = Route(code, name)
        self.routes.append(r)

    def add_driver(self, name):
        d = Driver(self.next_driver_id, name)
        self.next_driver_id += 1
        self.drivers.append(d)

    def get_driver(self, did):
        for d in self.drivers:
            if d.id == did:
                return d
        return None

    def auto_assign(self):
        if self.is_empty():
            return False, "No reports in queue"

        idle = [d for d in self.drivers if d.status == "Idle"]
        if not idle:
            return False, "No idle drivers"

        driver = idle[0]
        report = self.dequeue()
        driver.assign(report)

        return True, f"{driver.name} assigned to {report['route_code']}"

    def driver_finish(self, did):
        driver = self.get_driver(did)
        if not driver:
            return False, "Driver not found"

        finished = driver.finish()
        if not finished:
            return False, "Driver has no job"

        rec = {
            "driver": driver.name,
            "report": finished,
            "timestamp": time.time()
        }

        self.push(rec)
        self._save_history(rec)

        return True, rec

    def _save_history(self, rec):
        arr = []
        if os.path.exists(HISTORY_FILE):
            try:
                arr = json.load(open(HISTORY_FILE))
            except:
                arr = []

        arr.append(rec)
        json.dump(arr, open(HISTORY_FILE, "w"), indent=2)


# ===============================
# GUI APP
# ===============================

class App:
    def __init__(self, root):
        self.root = root
        root.title("Transport Delay Manager")
        root.geometry("1000x650")
        root.configure(bg="#0F172A")

        self.dm = DelayManager()

        self.setup_style()

        # HEADER
        tk.Label(root,
            text="🚍 Transport Delay Manager",
            bg="#0F172A",
            fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=10)

        main = tk.Frame(root, bg="#0F172A")
        main.pack(fill="both", expand=True)

        left = tk.Frame(main, bg="#0F172A")
        left.pack(side="left", fill="y", padx=10)

        right = tk.Frame(main, bg="#0F172A")
        right.pack(side="right", fill="both", expand=True, padx=10)

        self.card_add_route(left)
        self.card_report(left)
        self.card_driver(left)

        self.card_queue(right)
        self.card_driver_list(right)
        self.card_history(right)

        self.update_routes_menu()
        self.update_ui()

    # ================= PLACEHOLDER FUNCTION =================
    def add_placeholder(self, entry, text):
        entry.insert(0, text)
        entry.config(foreground="gray")

        def on_focus_in(event):
            if entry.get() == text:
                entry.delete(0, tk.END)
                entry.config(foreground="black")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, text)
                entry.config(foreground="gray")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    # ================= STYLE =================
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            background="#2563EB",
            foreground="white")

        style.configure("TLabel",
            background="#1E293B",
            foreground="white",
            font=("Segoe UI", 10))

        style.configure("TFrame", background="#1E293B")

        style.configure("Treeview",
            background="white",
            foreground="black",
            rowheight=25,
            fieldbackground="white")

    def card(self, parent, title):
        frame = tk.Frame(parent, bg="#1E293B", padx=10, pady=10)
        frame.pack(fill="x", pady=8)
        tk.Label(frame, text=title, font=("Segoe UI", 12, "bold"),
                 bg="#1E293B", fg="white").pack(anchor="w", pady=3)
        return frame

    # ================= ADD ROUTE =================
    def card_add_route(self, parent):
        card = self.card(parent, "Add Route")

        self.entry_route_code = ttk.Entry(card)
        self.entry_route_code.pack(fill="x", pady=4)
        self.add_placeholder(self.entry_route_code, "Code")

        self.entry_route_name = ttk.Entry(card)
        self.entry_route_name.pack(fill="x", pady=4)
        self.add_placeholder(self.entry_route_name, "Route Name")

        ttk.Button(card, text="Add Route", command=self.add_route).pack(fill="x")

    # ================= REPORT =================
    def card_report(self, parent):
        card = self.card(parent, "Report Delay")

        self.sel_route_var = tk.StringVar(value="")
        self.route_menu = ttk.Combobox(card, textvariable=self.sel_route_var)
        self.route_menu.pack(fill="x", pady=4)

        self.entry_delay = ttk.Entry(card)
        self.entry_delay.pack(fill="x", pady=4)
        self.add_placeholder(self.entry_delay, "Delay (min)")

        self.entry_reason = ttk.Entry(card)
        self.entry_reason.pack(fill="x", pady=4)
        self.add_placeholder(self.entry_reason, "Reason")

        ttk.Button(card, text="Add to Queue", command=self.report_delay).pack(fill="x")

    # ================= DRIVER =================
    def card_driver(self, parent):
        card = self.card(parent, "Add Driver")

        self.entry_driver = ttk.Entry(card)
        self.entry_driver.pack(fill="x", pady=4)
        self.add_placeholder(self.entry_driver, "Driver Name")

        ttk.Button(card, text="Add Driver", command=self.add_driver).pack(fill="x")

    # ================= QUEUE =================
    def card_queue(self, parent):
        card = self.card(parent, "Queue List")

        self.qbox = tk.Listbox(card, height=6, font=("Consolas", 10))
        self.qbox.pack(fill="x", pady=4)

        ttk.Button(card, text="Auto Assign", command=self.auto_assign).pack(fill="x")

    # ================= DRIVER LIST =================
    def card_driver_list(self, parent):
        card = self.card(parent, "Drivers")

        self.dbox = tk.Listbox(card, height=6, font=("Consolas", 10))
        self.dbox.pack(fill="x", pady=4)

        ttk.Button(card, text="Finish Selected Driver", command=self.finish_driver).pack(fill="x")

    # ================= HISTORY =================
    def card_history(self, parent):
        card = self.card(parent, "History")

        self.hbox = tk.Listbox(card, height=6, font=("Consolas", 10))
        self.hbox.pack(fill="x", pady=4)

    # ================= LOGIC =================

    def add_route(self):
        code = self.entry_route_code.get().strip()
        name = self.entry_route_name.get().strip()

        if code and name and code != "Code" and name != "Route Name":
            self.dm.add_route(code, name)
            self.update_routes_menu()
            self.entry_route_code.delete(0, tk.END)
            self.entry_route_name.delete(0, tk.END)
            self.add_placeholder(self.entry_route_code, "Code")
            self.add_placeholder(self.entry_route_name, "Route Name")

    def update_routes_menu(self):
        values = [r.code for r in self.dm.routes]
        self.route_menu["values"] = values
        if values:
            self.sel_route_var.set(values[0])

    def report_delay(self):
        code = self.sel_route_var.get()

        try:
            delay = int(self.entry_delay.get())
        except:
            messagebox.showerror("Error", "Delay must be number")
            return

        reason = self.entry_reason.get().strip()

        if reason == "Reason" or reason == "":
            messagebox.showerror("Error", "Enter valid reason")
            return

        data = {
            "route_code": code,
            "est_delay_min": delay,
            "reason": reason,
            "reported_at": time.time()
        }

        self.dm.enqueue(data)
        self.entry_delay.delete(0, tk.END)
        self.entry_reason.delete(0, tk.END)

        self.add_placeholder(self.entry_delay, "Delay (min)")
        self.add_placeholder(self.entry_reason, "Reason")

        self.update_ui()

    def add_driver(self):
        name = self.entry_driver.get().strip()

        if name and name != "Driver Name":
            self.dm.add_driver(name)
            self.entry_driver.delete(0, tk.END)
            self.add_placeholder(self.entry_driver, "Driver Name")
            self.update_ui()

    def auto_assign(self):
        ok, msg = self.dm.auto_assign()
        if not ok:
            messagebox.showwarning("Info", msg)
        self.update_ui()

    def finish_driver(self):
        sel = self.dbox.curselection()
        if not sel:
            return

        did = int(self.dbox.get(sel[0]).split(" | ")[0])
        self.dm.driver_finish(did)

        self.update_ui()

    def update_ui(self):
        self.qbox.delete(0, tk.END)
        for r in self.dm.show_all():
            self.qbox.insert(tk.END, f"{r['route_code']} - {r['est_delay_min']} min")

        self.dbox.delete(0, tk.END)
        for d in self.dm.drivers:
            task = d.current_report["route_code"] if d.current_report else "-"
            self.dbox.insert(tk.END, f"{d.id} | {d.name} | {d.status} | {task}")

        self.hbox.delete(0, tk.END)
        for h in reversed(self.dm.items[-10:]):
            t = time.strftime("%H:%M", time.localtime(h["timestamp"]))
            self.hbox.insert(tk.END,
                             f"{h['report']['route_code']} - {h['driver']} @ {t}")


# ===============================
# RUN
# ===============================

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()