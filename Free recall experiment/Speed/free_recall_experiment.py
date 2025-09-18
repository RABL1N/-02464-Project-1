import random
import csv
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ------------------------------ Config ------------------------------ #
SIMILAR_POOL = ["B","D","G","P","T","V"]
DISSIMILAR_POOL = ["K","L","R","Y","Q","H","M","N","Z"]
DEFAULT_POOL = list(set(SIMILAR_POOL + DISSIMILAR_POOL))

LIST_LEN_MIN = 10
LIST_LEN_MAX = 12
FIXATION_MS = 500
ON_MS = 400
BLANK_MS = 100
RETENTION_MS = 1000

# Chunking parameters
USE_CHUNKS_DEFAULT = True
CHUNK_SIZE = 3
INTERCHUNK_GAP_MS = 400  # extra blank between groups when chunked

# Simple phonological confusion map (symmetric)
PHONO_PAIRS = {("B","P"), ("D","T"), ("G","K"), ("F","S"), ("M","N"), ("V","B"), ("V","F")}

# ------------------------------ Helpers ------------------------------ #
def overlaps_ignoring_order(target_letters, resp_letters):
    """Return count of correctly recalled unique items, ignoring order and duplicates in response."""
    t = list(target_letters)
    count = 0
    for r in resp_letters:
        if r in t:
            t.remove(r)
            count += 1
    return count

def estimate_phono_confusions(target_letters, resp_letters):
    """Heuristic: count responses that are not in target but are a phonological neighbor of some target."""
    tset = set(target_letters)
    conf = 0
    for r in resp_letters:
        if r not in tset:
            for a,b in PHONO_PAIRS:
                if (r==a and b in tset) or (r==b and a in tset):
                    conf += 1
                    break
    return conf

# ------------------------------ App ------------------------------ #
class FreeRecallApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Free Recall Experiment")
        self.geometry("900x560")
        self.configure(bg="white")
        self.resizable(False, False)

        # State
        self.participant = tk.StringVar(value="P01")
        self.condition = tk.StringVar(value="silent")  # silent|suppression|tapping
        self.similarity = tk.StringVar(value="mixed")  # similar|dissimilar|mixed
        self.chunked = tk.BooleanVar(value=USE_CHUNKS_DEFAULT)
        self.n_trials = tk.IntVar(value=20)

        self.trial_index = 0
        self.letters = []
        self.response = ""
        self.log_rows = []

        # UI
        self.center = tk.Frame(self, bg="white")
        self.center.place(relx=0.5, rely=0.5, anchor="center")
        self.label = tk.Label(self.center, text="", font=("Helvetica", 48), bg="white")
        self.sub = tk.Label(self.center, text="", font=("Helvetica", 16), bg="white")
        self.entry = tk.Entry(self.center, font=("Consolas", 24), width=40, justify="center")
        self.btn = ttk.Button(self.center, text="", command=self._on_button)

        self._build_menu()

        self.bind("<Return>", lambda e: self._on_enter())
        self.bind("<BackSpace>", self._block_backspace)

    # -------------------------- Menu -------------------------- #
    def _build_menu(self):
        for w in self.center.winfo_children():
            w.destroy()
        tk.Label(self.center, text="Free Recall Experiment", font=("Helvetica", 28, "bold"), bg="white").pack(pady=8)

        frm = tk.Frame(self.center, bg="white")
        frm.pack(pady=4)
        row = 0
        tk.Label(frm, text="Participant ID:", bg="white").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(frm, textvariable=self.participant, width=12, justify="center").grid(row=row, column=1, padx=6, pady=4)
        row += 1

        tk.Label(frm, text="Condition:", bg="white").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        ttk.Combobox(frm, textvariable=self.condition, values=["silent","suppression","tapping"], width=14, state="readonly").grid(row=row, column=1, padx=6, pady=4)
        row += 1

        tk.Label(frm, text="Similarity:", bg="white").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        ttk.Combobox(frm, textvariable=self.similarity, values=["mixed","similar","dissimilar"], width=14, state="readonly").grid(row=row, column=1, padx=6, pady=4)
        row += 1

        tk.Label(frm, text="Chunked groups:", bg="white").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        ttk.Checkbutton(frm, variable=self.chunked).grid(row=row, column=1, padx=6, pady=4, sticky="w")
        row += 1

        tk.Label(frm, text="# trials:", bg="white").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        tk.Spinbox(frm, from_=1, to=500, textvariable=self.n_trials, width=8, justify="center").grid(row=row, column=1, padx=6, pady=4)
        row += 1

        ttk.Button(self.center, text="Start", command=self._start_block).pack(pady=16)
        ttk.Button(self.center, text="Save log…", command=self._save_csv).pack(pady=4)

        info = (
            "Timing: fixation 500 ms → letters 800 ms on + 200 ms blank → retention 1000 ms → recall\n"
            "Suppression: whisper 'the-the-the' at ~120 BPM from fixation to end of recall.\n"
            "Tapping: tap index finger at same tempo; do not speak."
        )
        tk.Label(self.center, text=info, font=("Helvetica", 11), fg="#333", bg="white").pack(pady=8)

    def _start_block(self):
        self.trial_index = 0
        self.log_rows.clear()
        self._next_trial()

    # -------------------------- Trial flow -------------------------- #
    def _next_trial(self):
        if self.trial_index >= self.n_trials.get():
            messagebox.showinfo("Block complete", f"Completed {self.n_trials.get()} trials. Save log to export CSV.")
            self._build_menu()
            return
        self.trial_index += 1
        self.letters = self._make_list()
        self.response = ""
        self._show_fixation()

    def _show_fixation(self):
        self._clear_center()
        self.label.config(text="+", font=("Helvetica", 72))
        self.label.pack(pady=40)
        cond = self.condition.get()
        if cond == "suppression":
            self.sub.config(text=f"Trial {self.trial_index}/{self.n_trials.get()} — Whisper 'the-the-the' @120 BPM now, keep going until recall ends.")
        elif cond == "tapping":
            self.sub.config(text=f"Trial {self.trial_index}/{self.n_trials.get()} — Tap your index finger @120 BPM now, continue until recall ends.")
        else:
            self.sub.config(text=f"Trial {self.trial_index}/{self.n_trials.get()} — Focus on the cross.")
        self.sub.pack()
        self.after(FIXATION_MS, self._show_sequence)

    def _show_sequence(self):
        self._clear_center()
        self.label.pack(pady=40)
        self.sub.pack()
        chunked = self.chunked.get()
        letters = list(self.letters)

        def present_next(i=0):
            if i >= len(letters):
                self.after(RETENTION_MS, self._recall_screen)
                return
            self.label.config(text=letters[i])
            gap = BLANK_MS
            # add inter-chunk gap
            if chunked and i>0 and (i % CHUNK_SIZE == 0):
                gap = INTERCHUNK_GAP_MS
            self.after(ON_MS, lambda: self._blank_then_next(i, gap, present_next))
        present_next(0)

    def _blank_then_next(self, i, blank_ms, cont_fn):
        self.label.config(text="")
        self.after(blank_ms, lambda: cont_fn(i+1))

    def _recall_screen(self):
        self._clear_center()
        self.label.config(text="Type all letters you remember (any order)")
        self.label.pack(pady=20)
        self.entry.delete(0, tk.END)
        self.entry.pack(pady=10)
        self.entry.focus_set()
        self.sub.config(text="No backspace. Use single letters (A–Z) without spaces. Press Enter to submit.")
        self.sub.pack(pady=6)
        self.btn.config(text="Submit", command=self._submit_response)
        self.btn.pack(pady=10)

    # -------------------------- Data & scoring -------------------------- #
    def _submit_response(self):
        self._on_enter()

    def _on_enter(self):
        if not self.entry.winfo_ismapped():
            return
        resp = self.entry.get().strip().upper().replace(" ", "")
        # keep only A-Z
        resp = ''.join([c for c in resp if 'A' <= c <= 'Z'])
        targ = list(self.letters)
        resp_list = list(resp)
        n_correct = overlaps_ignoring_order(targ, resp_list)
        prop_correct = n_correct / len(targ)
        phono_conf = estimate_phono_confusions(targ, resp_list)

        row = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "participant": self.participant.get(),
            "trial_index": self.trial_index,
            "condition": self.condition.get(),
            "similarity": self.similarity.get(),
            "chunked": int(self.chunked.get()),
            "list_items": ''.join(self.letters),
            "response": resp,
            "n_correct": n_correct,
            "proportion_correct": f"{prop_correct:.3f}",
            "phonological_confusions": phono_conf,
        }
        self.log_rows.append(row)
        self._next_trial()

    def _make_list(self):
        L = random.randint(LIST_LEN_MIN, LIST_LEN_MAX)
        sim = self.similarity.get()
        if sim == "similar":
            pool = SIMILAR_POOL
        elif sim == "dissimilar":
            pool = DISSIMILAR_POOL
        else:
            pool = DEFAULT_POOL
        # sample without replacement; if pool shorter than length, extend by sampling with replacement after unique exhaustion
        if L <= len(pool):
            return random.sample(pool, L)
        else:
            base = random.sample(pool, len(pool))
            extra = [random.choice(pool) for _ in range(L - len(pool))]
            # avoid immediate repeats
            letters = base + extra
            for i in range(1, len(letters)):
                if letters[i] == letters[i-1]:
                    letters[i] = random.choice([x for x in pool if x != letters[i-1]])
            return letters

    def _save_csv(self):
        if not self.log_rows:
            messagebox.showwarning("No data", "No trials to save yet.")
            return
        fname = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], initialfile=f"free_recall_{self.participant.get()}_{int(time.time())}.csv")
        if not fname:
            return
        fieldnames = list(self.log_rows[0].keys())
        with open(fname, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.log_rows)
        messagebox.showinfo("Saved", f"Data saved to\n{fname}")

    def _save_before_exit(self):
        if self.log_rows:
            if messagebox.askyesno("Save data?", "You have unsaved data. Save CSV before exiting?"):
                self._save_csv()
        self.destroy()

    def _block_backspace(self, event):
        if self.entry.winfo_ismapped():
            return "break"

    def _clear_center(self):
        for w in self.center.winfo_children():
            w.destroy()
        self.label = tk.Label(self.center, text="", font=("Helvetica", 48), bg="white")
        self.sub = tk.Label(self.center, text="", font=("Helvetica", 16), bg="white")
        self.entry = tk.Entry(self.center, font=("Consolas", 24), width=40, justify="center")
        self.btn = ttk.Button(self.center, text="", command=self._on_button)

    def _on_button(self):
        pass


if __name__ == "__main__":
    app = FreeRecallApp()
    app.protocol("WM_DELETE_WINDOW", app._save_before_exit)
    app.mainloop()
