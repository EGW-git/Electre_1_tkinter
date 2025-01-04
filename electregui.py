import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from decimal import Decimal
import operator
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

entries_alt = []  # list of alts

def calculate():
    try:
        global alt_len
        alt_len = int(entry_alt_len.get())
        weights = list(map(float, entry_weights.get().split()))
        dis_weights = list(map(float, entry_dis_weights.get().split()))
        ts_conc = float(entry_ts_conc.get())
        ts_disc = float(entry_ts_disc.get())

        if not entries_alt or len(entries_alt) != alt_len:
            messagebox.showerror("Error", "Please, generate boxes for alternatives")
            return

        alternatives = []
        for i in range(alt_len):
            values = entries_alt[i].get().split()
            if len(values) != len(weights):
                messagebox.showerror("Error", f"Enter {len(weights)} the values for {i + 1} alternative.")
                return
            alternatives.append(list(map(float, values)))

        alternatives_np = np.array(alternatives)
        n = len(alternatives_np)
        concordance_matrix = []

        for i in range(n):
            concordance_matrix.append([])
            for j in range(n):
                if i == j:
                    concordance_matrix[i].append(0)
                    continue
                concordance_index = 0
                equal_index = 0
                for k in range(len(weights)):
                    if alternatives_np[i][k] > alternatives_np[j][k]:
                        concordance_index += weights[k]
                    elif alternatives_np[i][k] == alternatives_np[j][k]:
                        equal_index += weights[k]
                s = concordance_index + 0.5 * equal_index
                concordance_matrix[i].append(float(Decimal(s).quantize(Decimal("1.00"))))

        discordance_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                r_max = 0
                for k in range(len(dis_weights)):
                    if alternatives_np[j][k] > alternatives_np[i][k]:
                        difference = alternatives_np[j][k] - alternatives_np[i][k]
                        r = difference * dis_weights[k]
                        if r > r_max:
                            r_max = r
                if r_max > 0:
                    discordance_matrix[i][j] = r_max

        G = nx.DiGraph()
        for i in range(len(concordance_matrix)):
            for j in range(len(concordance_matrix)):
                if concordance_matrix[i][j] >= ts_conc and discordance_matrix[i][j] <= ts_disc:
                    G.add_edge(f"A{i + 1}", f"A{j + 1}")

        if len(G.nodes) == 0:
            messagebox.showerror("Error", "Please, try different tresholds.")
            return

        pr = nx.pagerank(G)
        sort = sorted(pr.items(), key=operator.itemgetter(1), reverse=True)
        rounded_sort = []
        for i, j in sort:
            rounded_sort.append(i)
            rounded_sort.append(round(j, 3))
        variables = [discordance_matrix, concordance_matrix, sort]
        with open("Result.txt", 'w') as write_res:
            for ln in variables:
                write_res.write(str(ln))
                write_res.write('\n')

        # characteristic of graph
        plt.figure(figsize=(9, 7))
        pos = nx.circular_layout(G)
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_size=2500,
            node_color="skyblue",
            font_size=12,
            arrows=True,
            arrowsize=16,
            width=1.5
        )
        plt.show()

        # Отображение результатов в текстовом поле
        text_result.delete(1.0, tk.END)
        text_result.insert(tk.END, "Discordance matrix:\n")
        text_result.insert(tk.END, str(discordance_matrix) + "\n\n")
        text_result.insert(tk.END, "concordance matrix:\n")
        text_result.insert(tk.END, str(np.array(concordance_matrix)) + "\n\n")
        text_result.insert(tk.END, "PageRank:\n")
        text_result.insert(tk.END, str(rounded_sort))

    except ValueError:
        messagebox.showerror("Error", "Please, check your values")


root = tk.Tk()
root.title("ELECTRE I")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# enter number of alts
ttk.Label(frame, text="Number of alternatives").grid(row=0, column=0, sticky=tk.W)
entry_alt_len = ttk.Entry(frame)
entry_alt_len.grid(row=0, column=1, sticky=tk.W)

# enter alts
frame_alternatives = ttk.Frame(frame, padding="5")
frame_alternatives.grid(row=1, column=0, columnspan=2, sticky=tk.W)


def generate_alternative_entries():
    for widget in frame_alternatives.winfo_children():
        widget.destroy()
    try:
        alt_len = int(entry_alt_len.get())
        global entries_alt
        entries_alt = []
        for i in range(alt_len):
            ttk.Label(frame_alternatives, text=f"Alternative {i + 1}:").grid(row=i, column=0, sticky=tk.W)
            entry = ttk.Entry(frame_alternatives, width=50)
            entry.grid(row=i, column=1, sticky=tk.W)
            entries_alt.append(entry)
    except ValueError:
        messagebox.showerror("Error", "Please, insert correct number of values")


ttk.Button(frame, text="Create input field", command=generate_alternative_entries).grid(row=2, column=0,
                                                                                                  columnspan=2, pady=5)

# enter weights
ttk.Label(frame, text="Weights of criteria\n(use space and use dot as separator):").grid(row=3, column=0, sticky=tk.W)
entry_weights = ttk.Entry(frame, width=50)
entry_weights.grid(row=3, column=1, sticky=tk.W)

# enter discordance weights
ttk.Label(frame, text="Weights of discordance\n(use space and use dot as separator):").grid(row=4, column=0, sticky=tk.W)
entry_dis_weights = ttk.Entry(frame, width=50)
entry_dis_weights.grid(row=4, column=1, sticky=tk.W)

# enter tresholds
ttk.Label(frame, text="Concordance index treshold:").grid(row=5, column=0, sticky=tk.W)
entry_ts_conc = ttk.Entry(frame)
entry_ts_conc.grid(row=5, column=1, sticky=tk.W)

ttk.Label(frame, text="Discordance index treshold:").grid(row=6, column=0, sticky=tk.W)
entry_ts_disc = ttk.Entry(frame)
entry_ts_disc.grid(row=6, column=1, sticky=tk.W)

ttk.Button(frame, text="Calculate", command=calculate).grid(row=7, column=0, columnspan=2, pady=10)

# Result field
ttk.Label(frame, text="Result:").grid(row=8, column=0, sticky=tk.W)
text_result = tk.Text(frame, width=50, height=30)
text_result.grid(row=8, column=0, columnspan=2, pady=5)
root.mainloop()
