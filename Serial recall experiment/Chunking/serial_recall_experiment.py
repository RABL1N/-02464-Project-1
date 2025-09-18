"""
Serial Recall Experiment (Tkinter, single-file)

Features
- Implements the course §1.8 serial-recall design in one script
- Choose: presentation rate (slow/fast) and post-list phase (immediate/pause/wm-task)
- Trial flow: fixation (500 ms) → sequence (12 letters; timing by rate) → post-list phase → recall entry
- Scoring: proportion correct-in-position; CSV logging
- Minimal dependencies: standard library + tkinter only

How to run
$ python serial_recall_experiment.py

Notes
- "WM task" follows the brief exactly: on-screen prompt to count backwards aloud by 3s for 5 seconds. We do not record audio; the aim is to occupy rehearsal.
- For stricter control, supervise participants to ensure they speak during the 5 s interval.
"""

import random
import string
import csv
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ------------------------------ Config ------------------------------ #
POOL = ["B","D","G","K","L","M","P","Q","R","S","T","V","Y","Z"]  # consonant pool
# LIST_LENGTH will be randomly chosen from 4-9 for each experiment run
FIXATION_MS = 500
IMMEDIATE_BLANK_MS = 1000
PAUSE_MS = 5000
WM_TASK_MS = 5000

CHUNK_SIZE = 3

# Presentation rates
RATES = {
    "slow": {"on_ms": 800, "blank_ms": 200},   # ~1 Hz
    "fast": {"on_ms": 500, "blank_ms": 0},     # ~2 Hz
}

# ------------------------------ App ------------------------------ #
class SerialRecallApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Serial Recall Experiment")
        self.geometry("820x520")
        self.configure(bg="white")
        self.resizable(False, False)

        # State
        self.participant = tk.StringVar(value="P01")
        self.rate = tk.StringVar(value="slow")
        self.post_phase = tk.StringVar(value="immediate")  # immediate|pause|wm
        self.n_trials = tk.IntVar(value=20)
        self.chunking = tk.BooleanVar(value=False)  # Chunking option
        self.trial_index = 0
        self.letters = []
        self.response = ""
        self.phase = "menu"
        self.log_rows = []
        self.list_length = 0  # Will be set randomly for each trial

        # UI containers
        self.center = tk.Frame(self, bg="white")
        self.center.place(relx=0.5, rely=0.5, anchor="center")

        self.label = tk.Label(self.center, text="", font=("Helvetica", 48), bg="white")
        self.sub = tk.Label(self.center, text="", font=("Helvetica", 16), bg="white")
        self.entry = tk.Entry(self.center, font=("Consolas", 24), width=32, justify="center")
        self.btn = ttk.Button(self.center, text="", command=self._on_button)

        self._build_menu()

        # key bindings
        self.bind("<Return>", lambda e: self._on_enter())
        self.bind("<BackSpace>", self._block_backspace)

    # -------------------------- Screens -------------------------- #
    def _build_menu(self):
        for w in self.center.winfo_children():
            w.destroy()

        tk.Label(self.center, text="Serial Recall Experiment", font=("Helvetica", 28, "bold"), bg="white").pack(pady=8)

        frm = tk.Frame(self.center, bg="white")
        frm.pack(pady=4)
        tk.Label(frm, text="Participant ID:", bg="white").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(frm, textvariable=self.participant, width=12, justify="center").grid(row=0, column=1, padx=6, pady=4)

        tk.Label(frm, text="Presentation rate:", bg="white").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        ttk.Combobox(frm, textvariable=self.rate, values=["slow","fast"], width=10, state="readonly").grid(row=1, column=1, padx=6, pady=4)

        tk.Label(frm, text="Post-list phase:", bg="white").grid(row=2, column=0, sticky="e", padx=6, pady=4)
        ttk.Combobox(frm, textvariable=self.post_phase, values=["immediate","pause","wm"], width=10, state="readonly").grid(row=2, column=1, padx=6, pady=4)

        tk.Label(frm, text="# trials:", bg="white").grid(row=3, column=0, sticky="e", padx=6, pady=4)
        tk.Spinbox(frm, from_=1, to=500, textvariable=self.n_trials, width=8, justify="center").grid(row=3, column=1, padx=6, pady=4)

        tk.Label(frm, text="Chunking:", bg="white").grid(row=4, column=0, sticky="e", padx=6, pady=4)
        tk.Checkbutton(frm, variable=self.chunking, bg="white").grid(row=4, column=1, sticky="w", padx=6, pady=4)

        ttk.Button(self.center, text="Start", command=self._start_block).pack(pady=16)
        ttk.Button(self.center, text="Save log…", command=self._save_csv).pack(pady=4)

        info = (
            "Rate slow = 800 ms on + 200 ms blank (≈1 Hz)\n"
            "Rate fast = 500 ms on + 0 ms blank (≈2 Hz)\n"
            "Post-list: immediate (1 s blank) | pause (5 s blank) | wm (5 s count-backwards aloud)\n"
            "Chunking: Show letters in groups of 3 instead of individually"
        )
        tk.Label(self.center, text=info, font=("Helvetica", 11), fg="#333", bg="white").pack(pady=8)

    def _start_block(self):
        self.trial_index = 0
        self.log_rows.clear()
        self._next_trial()

    def _next_trial(self):
        if self.trial_index >= self.n_trials.get():
            messagebox.showinfo("Block complete", f"Completed {self.n_trials.get()} trials. Choose Save log… to export CSV.")
            self._build_menu()
            return

        self.trial_index += 1
        # Set list length based on chunking setting
        if self.chunking.get():
            # Use fixed length of 9 for chunking (3 complete chunks of 3 letters each)
            self.list_length = 9
        else:
            # Generate a new random list length for this trial (4-9)
            self.list_length = random.randint(4, 9)
        self.letters = self._sample_letters()
        self.response = ""
        self._show_fixation()

    # ------------------------ Trial phases ------------------------ #
    def _show_fixation(self):
        self._clear_center()
        self.label.config(text="+", font=("Helvetica", 72))
        self.label.pack(pady=40)
        self.sub.config(text=f"Trial {self.trial_index}/{self.n_trials.get()} — Participant {self.participant.get()}\nFocus on the cross.")
        self.sub.pack()
        self.after(FIXATION_MS, self._show_sequence)

    def _show_sequence(self):
        self._clear_center()
        self.label.pack(pady=40)
        self.sub.pack()
        self.sub.config(text="Remember the letters in order.")
        timing = RATES[self.rate.get()]
        on_ms = timing["on_ms"]
        blank_ms = timing["blank_ms"]

        if self.chunking.get():
            # Present letters in chunks of CHUNK_SIZE
            self._present_chunked(seq=list(self.letters), on_ms=on_ms, blank_ms=blank_ms)
        else:
            # Present letters one by one (original behavior)
            seq = list(self.letters)
            def present_next(i=0):
                if i >= len(seq):
                    # Go to post-list phase
                    self.after(0, self._post_list_phase)
                    return
                self.label.config(text=seq[i])
                self.after(on_ms, lambda: self._blank_then_next(i, blank_ms, present_next))
            present_next(0)

    def _blank_then_next(self, i, blank_ms, cont_fn):
        self.label.config(text="")
        if blank_ms > 0:
            self.after(blank_ms, lambda: cont_fn(i+1))
        else:
            cont_fn(i+1)

    def _present_chunked(self, seq, on_ms, blank_ms):
        """Present letters in chunks of CHUNK_SIZE"""
        chunks = []
        for i in range(0, len(seq), CHUNK_SIZE):
            chunk = seq[i:i+CHUNK_SIZE]
            chunks.append(' '.join(chunk))
        
        def present_chunk(chunk_idx=0):
            if chunk_idx >= len(chunks):
                # Go to post-list phase
                self.after(0, self._post_list_phase)
                return
            self.label.config(text=chunks[chunk_idx])
            self.after(on_ms, lambda: self._blank_then_next(chunk_idx, blank_ms, present_chunk))
        present_chunk(0)

    def _post_list_phase(self):
        phase = self.post_phase.get()
        self._clear_center()
        self.label.pack(pady=40)
        self.sub.pack()
        if phase == "immediate":
            self.label.config(text=" ")
            self.sub.config(text="Prepare to recall…")
            self.after(IMMEDIATE_BLANK_MS, self._recall_screen)
        elif phase == "pause":
            self.label.config(text=" ")
            self._countdown(PAUSE_MS, headline="Pause", subtitle="Stay quiet. Do not rehearse aloud.", callback=self._recall_screen)
        elif phase == "wm":
            # WM task: on-screen prompt to count backwards aloud by 3s
            self._countdown(WM_TASK_MS, headline="Working-memory task", subtitle="Count backwards aloud by 3s (e.g., 100, 97, 94, …)", callback=self._recall_screen)
        else:
            self._recall_screen()

    def _recall_screen(self):
        self._clear_center()
        self.label.config(text="Type the letters in order")
        self.label.pack(pady=20)
        self.entry.delete(0, tk.END)
        self.entry.pack(pady=10)
        self.entry.focus_set()
        self.sub.config(text="Press Enter to submit. Backspace is disabled; use '?' if unsure.")
        self.sub.pack(pady=6)
        self.btn.config(text="Submit", command=self._submit_response)
        self.btn.pack(pady=10)

    # ------------------------ Helpers ------------------------ #
    def _countdown(self, duration_ms, headline="", subtitle="", callback=None):
        self.label.config(text=headline)
        self.sub.config(text=f"{subtitle}\n")
        countdown_lbl = tk.Label(self.center, text="", font=("Helvetica", 28), bg="white")
        countdown_lbl.pack(pady=6)

        start = time.time()
        def tick():
            elapsed = int((time.time() - start) * 1000)
            remain = max(0, duration_ms - elapsed)
            countdown_lbl.config(text=f"{remain//1000 + (1 if remain % 1000 else 0)} s")
            if remain > 0:
                self.after(50, tick)
            else:
                countdown_lbl.destroy()
                if callback:
                    callback()
        tick()

    def _submit_response(self):
        self._on_enter()

    def _on_enter(self):
        if not self.entry.winfo_ismapped():
            return
        resp = self.entry.get().strip().upper().replace(" ", "")
        self.response = resp
        acc_prop, per_pos = self._score(self.letters, resp)
        row = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "participant": self.participant.get(),
            "trial_index": self.trial_index,
            "rate": self.rate.get(),
            "post_phase": self.post_phase.get(),
            "chunking": self.chunking.get(),
            "list_length": self.list_length,
            "list_items": ''.join(self.letters),
            "response": resp,
            "proportion_correct_in_position": f"{acc_prop:.3f}",
            "per_position_binary": ''.join(str(int(x)) for x in per_pos),
        }
        self.log_rows.append(row)
        self._next_trial()

    def _sample_letters(self):
        return random.sample(POOL, self.list_length)

    def _score(self, letters, resp):
        # Compare per position up to list_length (pad response with '-')
        resp_list = list(resp)
        correct_flags = []
        for i, target in enumerate(letters):
            got = resp_list[i] if i < len(resp_list) else None
            correct_flags.append(got == target)
        acc = sum(correct_flags) / len(letters)
        return acc, correct_flags

    def _save_csv(self):
        if not self.log_rows:
            messagebox.showwarning("No data", "No trials to save yet.")
            return
        fname = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], initialfile=f"serial_recall_{self.participant.get()}_{int(time.time())}.csv")
        if not fname:
            return
        with open(fname, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(self.log_rows[0].keys()))
            writer.writeheader()
            for r in self.log_rows:
                writer.writerow(r)
        messagebox.showinfo("Saved", f"Data saved to\n{fname}")

    def _block_backspace(self, event):
        # Disable backspace during recall to match spec
        if self.entry.winfo_ismapped():
            return "break"

    def _clear_center(self):
        for w in self.center.winfo_children():
            w.destroy()
        # recreate common widgets
        self.label = tk.Label(self.center, text="", font=("Helvetica", 48), bg="white")
        self.sub = tk.Label(self.center, text="", font=("Helvetica", 16), bg="white")
        self.entry = tk.Entry(self.center, font=("Consolas", 24), width=32, justify="center")
        self.btn = ttk.Button(self.center, text="", command=self._on_button)

    def _on_button(self):
        # placeholder for button actions assigned elsewhere
        pass


if __name__ == "__main__":
    app = SerialRecallApp()
    app.mainloop()
