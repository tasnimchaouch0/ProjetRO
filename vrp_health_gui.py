import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView
from PyQt5.QtCore import QThread, pyqtSignal
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# -------------------------------
# Thread pour le calcul Gurobi
# -------------------------------
class VRPThread(QThread):
    result_signal = pyqtSignal(float, dict)

    def run(self):
        # -------------------------------
        # 1. Données simplifiées
        # -------------------------------
        patients = [0,1,2,3,4,5]  # 0 = dépôt
        s = {0:0, 1:20, 2:30, 3:15, 4:25, 5:20}  # temps de service
        d = {
            (0,1):10,(0,2):5,(0,3):14,(0,4):7,(0,5):18,
            (1,0):10,(1,2):6,(1,3):12,(1,4):8,(1,5):15,
            (2,0):5,(2,1):6,(2,3):10,(2,4):7,(2,5):12,
            (3,0):14,(3,1):12,(3,2):10,(3,4):5,(3,5):8,
            (4,0):7,(4,1):8,(4,2):7,(4,3):5,(4,5):10,
            (5,0):18,(5,1):15,(5,2):12,(5,3):8,(5,4):10
        }
        M = 1000

        agents = {
    1: {"skills": ["Nursing"]},  # Agent 1
    2: {"skills": ["Nursing", "WoundCare"]}  # Agent 2
}
        agents_test = {1: agents[1], 2: agents[2]}
        skills_req = {1:"Nursing", 2:"Nursing", 3:"WoundCare", 4:"Nursing", 5:"Nursing"}
        

        # -------------------------------
        # 2. Modèle
        # -------------------------------
        m = Model("VRP_Health_OneAgent")
        x = {}
        t = {}
        for k in agents_test:
            for i,j in d.keys():
                x[i,j,k] = m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}")
            for i in patients:
                t[i,k] = m.addVar(vtype=GRB.CONTINUOUS, name=f"t_{i}_{k}")
        for j in patients[1:]:
            eligible = [k for k in agents_test if skills_req[j] in agents_test[k]["skills"]]
            m.addConstr(quicksum(x[i,j,k] for i in patients if i!=j for k in eligible) == 1)
        # Objectif : minimiser la distance totale
        m.setObjective(quicksum(d[i,j]*x[i,j,k] for i,j in d.keys() for k in agents_test), GRB.MINIMIZE)
      
        # Fenêtres de temps très larges
        for k in agents_test:
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
            print("Modèle encore infeasible (improbable ici)")
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
            self.result_signal.emit(distance_totale, routes)

# 4. IHM principale
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

    def show_result(self, distance, routes):
        self.label_result.setText(f"Distance totale minimale : {distance:.2f}")
        # Coordonnées fictives pour plot
        coords = {0:(0,0), 1:(2,5), 2:(5,2), 3:(6,6), 4:(8,3), 5:(1,7)}
        colors = {1:'blue',2:'red'}

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        for i in coords:
            if i==0:
                ax.scatter(*coords[i], c='green', s=200)
                ax.text(coords[i][0]+0.1, coords[i][1]+0.1, f'Depot {i}')
            else:
                ax.scatter(*coords[i], c='black', s=100)
                ax.text(coords[i][0]+0.1, coords[i][1]+0.1, f'P{i}')

        for k, route in routes.items():
            x_vals = [coords[i][0] for i in route]
            y_vals = [coords[i][1] for i in route]
            ax.plot(x_vals, y_vals, color=colors[k], marker='o', label=f'Agent {k}')

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.legend()
        ax.grid(True)
        self.canvas.draw()

# -------------------------------
# 5. Lancement application
# -------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
