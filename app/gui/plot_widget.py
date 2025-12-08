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

    def update_plot(self, routes, coords):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        for i, (x, y) in coords.items():
            if i == 0:
                ax.scatter(x, y, c="green", s=150)  # Reduced from 200
            else:
                ax.scatter(x, y, c="black", s=60)  # Reduced from 80
            ax.text(x + 0.1, y + 0.1, f"P{i}", fontsize=8)  # Smaller text

        colors = ["red", "blue", "orange", "purple"]

        for idx, (agent, route) in enumerate(routes.items()):
            r_x = [coords[i][0] for i in route]
            r_y = [coords[i][1] for i in route]
            ax.plot(r_x, r_y, color=colors[idx % len(colors)], marker="o", markersize=4, linewidth=1.5)  # Thinner lines

        ax.grid(True, alpha=0.3)  # Lighter grid
        ax.tick_params(labelsize=8)  # Smaller axis labels
        self.figure.tight_layout()  # Compact layout
        self.canvas.draw()
