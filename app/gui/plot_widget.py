import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins

        self.figure = plt.figure(figsize=(4, 3))  # Reduced from (5, 4)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def update_plot(self, routes, coords, patients_info=None):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Emojis pour les skills
        skill_emojis = {
            "Nursing": "💉",
            "WoundCare": "🩹",
            "Pediatrics": "👶",
            "Diabetes": "🍬",
            "Physio": "🏃"
        }

        for i, (x, y) in coords.items():
            if i == 0:
                ax.scatter(x, y, c="green", s=150)
                ax.text(x + 0.1, y + 0.1, "Dépôt", fontsize=8, fontweight='bold')
            else:
                ax.scatter(x, y, c="black", s=60)
                # Afficher le numéro du patient
                ax.text(x + 0.1, y + 0.1, f"P{i}", fontsize=8)
                
                # Afficher le skill requis sous le patient
                if patients_info and i in patients_info:
                    skill = patients_info[i].get("skill", "")
                    emoji = skill_emojis.get(skill, "")
                    if emoji:
                        ax.text(x, y - 0.3, emoji, fontsize=10, ha='center')

        colors = ["red", "blue", "orange", "purple"]

        for idx, (agent, route) in enumerate(routes.items()):
            r_x = [coords[i][0] for i in route]
            r_y = [coords[i][1] for i in route]
            ax.plot(r_x, r_y, color=colors[idx % len(colors)], marker="o", markersize=4, linewidth=1.5)

        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=8)
        self.figure.tight_layout()
        self.canvas.draw()
