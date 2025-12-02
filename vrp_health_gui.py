import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# -------------------------------
# Thread pour le calcul Gurobi
# -------------------------------
class VRPThread(QThread):
    result_signal = pyqtSignal(float, dict, dict)  # distance, routes, coords

    def run(self):
        # -------------------------------
        # 1. Génération données
        # -------------------------------
        num_patients = 6
        patients = [0] + list(range(1, num_patients + 1))  # 0 = dépôt

        coords = {0: (0,0)}
        s = {0:0}  # temps de service
        for i in patients[1:]:
            coords[i] = (random.randint(0,10), random.randint(0,10))
            s[i] = random.randint(10, 40)

        # Distances euclidiennes
        d = {}
        for i in patients:
            for j in patients:
                if i != j:
                    xi, yi = coords[i]
                    xj, yj = coords[j]
                    d[i,j] = ((xi - xj)**2 + (yi - yj)**2)**0.5

        M = 1000

        # Agents et compétences
        types_soins = ["Nursing", "WoundCare", "Physio"]
        agents = {
            1: {"skills": ["Nursing", "Physio"]},
            2: {"skills": ["Nursing", "WoundCare"]},
        }

        # Compétences demandées pour chaque patient
        skills_req = {}
        agent_skills_flat = set(skill for ag in agents.values() for skill in ag["skills"])
        for i in patients[1:]:
            skills_req[i] = random.choice(list(agent_skills_flat))  # garantir faisable

        # -------------------------------
        # 2. Modèle Gurobi
        # -------------------------------
        m = Model("VRP_Health_Auto")
        x = {}
        t = {}
        for k in agents:
            for i,j in d.keys():
                x[i,j,k] = m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}")
            for i in patients:
                t[i,k] = m.addVar(vtype=GRB.CONTINUOUS, name=f"t_{i}_{k}")

        # Contraintes d'assignation selon compétences
        for j in patients[1:]:
            eligible = [k for k in agents if skills_req[j] in agents[k]["skills"]]
            m.addConstr(quicksum(x[i,j,k] for i in patients if i!=j for k in eligible) == 1)

        # Objectif : minimiser la distance totale
        m.setObjective(quicksum(d[i,j]*x[i,j,k] for i,j in d.keys() for k in agents), GRB.MINIMIZE)

        # Fenêtres de temps larges
        for k in agents:
            for i,j in d.keys():
                if i != j:
                    m.addConstr(t[j,k] >= t[i,k] + s[i] - M*(1 - x[i,j,k]))
            for i in patients:
                m.addConstr(t[i,k] >= 0)
                m.addConstr(t[i,k] <= 1440)

        # -------------------------------
        # 3. Résolution
        # -------------------------------
        m.optimize()

        routes = {}
        if m.status == GRB.INFEASIBLE:
            print("Modèle infeasible")
            m.computeIIS()
            m.write("model.iis")
        elif m.status == GRB.OPTIMAL:
            distance_totale = m.objVal
            for k in agents:
                route = [0]
                current = 0
                visited = set()
                while len(visited) < len(patients)-1:
                    found = False
                    for j in patients[1:]:
                        if j != current and x[current,j,k].x > 0.5 and j not in visited:
                            route.append(j)
                            visited.add(j)
                            current = j
                            found = True
                            break
                    if not found:
                        break
                route.append(0)
                routes[k] = route
            self.result_signal.emit(distance_totale, routes, coords)

# -------------------------------
# IHM principale
# -------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VRP Santé - Infirmières")
        self.setGeometry(100,100,900,700)
        self.layout = QVBoxLayout()

        # Bouton lancement
        self.btn_run = QPushButton("Calculer tournée optimale")
        self.btn_run.clicked.connect(self.run_vrp)
        self.layout.addWidget(self.btn_run)

        # Label résultat
        self.label_result = QLabel("")
        self.layout.addWidget(self.label_result)

        # Canvas graphique
        self.figure = plt.figure(figsize=(6,5))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Widget central
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def run_vrp(self):
        self.label_result.setText("Calcul en cours...")
        self.thread = VRPThread()
        self.thread.result_signal.connect(self.show_result)
        self.thread.start()

    def show_result(self, distance, routes, coords):
        self.label_result.setText(f"Distance totale minimale : {distance:.2f}")

        colors = ['blue', 'red', 'orange', 'purple', 'brown', 'cyan']

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Tracer les patients et dépôt
        for i, (x_coord, y_coord) in coords.items():
            if i == 0:
                ax.scatter(x_coord, y_coord, c='green', s=200)
                ax.text(x_coord + 0.1, y_coord + 0.1, f'Depot {i}', fontsize=10)
            else:
                ax.scatter(x_coord, y_coord, c='black', s=100)
                ax.text(x_coord + 0.1, y_coord + 0.1, f'P{i}', fontsize=9)

        # Tracer les routes
        for idx, (k, route) in enumerate(routes.items()):
            route_x = [coords[i][0] for i in route]
            route_y = [coords[i][1] for i in route]
            ax.plot(route_x, route_y, color=colors[idx % len(colors)], marker='o', label=f'Agent {k}')

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("Tournée des infirmiers")
        ax.legend()
        ax.grid(True)
        self.canvas.draw()

# -------------------------------
# Lancement application
# -------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
