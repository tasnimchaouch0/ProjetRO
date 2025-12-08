import sys
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, 
    QSpinBox, QDialog, QFormLayout, QLineEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from .plot_widget import PlotWidget
from ..threads.vrp_thread import VRPThread
from ..gui.data_generator import generate_instance

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VRP Santé - Optimisation Infirmiers")
        self.setGeometry(100, 100, 1000, 700)

        self.patients_info = {}  # stocke info de chaque patient
        self.coords = {}          # coordonnées utilisées pour le graphe

        layout = QVBoxLayout()

        # Choix nombre de patients
        layout.addWidget(QLabel("Nombre de patients :"))
        self.spin_patients = QSpinBox()
        self.spin_patients.setMinimum(1)
        self.spin_patients.setMaximum(20)
        self.spin_patients.setValue(5)
        layout.addWidget(self.spin_patients)

        # Choix nombre d'agents
        layout.addWidget(QLabel("Nombre d'agents :"))
        self.spin_agents = QSpinBox()
        self.spin_agents.setMinimum(1)
        self.spin_agents.setMaximum(10)
        self.spin_agents.setValue(2)
        layout.addWidget(self.spin_agents)

        # Bouton optimisation
        self.btn_run = QPushButton("Lancer optimisation")
        self.btn_run.clicked.connect(self.run_vrp)
        layout.addWidget(self.btn_run)

        # Affichage des infirmiers et compétences
        self.label_agents = QLabel("")
        layout.addWidget(self.label_agents)

        # Label résultat
        self.label_result = QLabel("")
        layout.addWidget(self.label_result)

        # Canvas graphe
        self.plot = PlotWidget()
        layout.addWidget(self.plot)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # connecter le click sur le graphe
        self.plot.canvas.mpl_connect("button_press_event", self.on_click)

    def run_vrp(self):
        num_patients = self.spin_patients.value()
        num_agents = self.spin_agents.value()
        self.label_result.setText("Optimisation en cours...")

        # Génération unique de l'instance pour GUI + solver
        dataset = generate_instance(test_type="Random Small", num_patients=num_patients, num_agents=num_agents, seed=42)

        # Stockage info patients
        self.patients_info = {
            p["id"]: {
                "coords": (p["lat"], p["lon"]),
                "service": p.get("duration", 0),
                "skill": p.get("required_skill", ""),
            }
            for p in dataset["patients"]
        }
        self.coords = {0: (dataset["depot"]["lat"], dataset["depot"]["lon"])}
        self.coords.update({p["id"]: (p["lat"], p["lon"]) for p in dataset["patients"]})

        # Afficher les infirmiers et leurs compétences
        agents_lines = [f"{a['name']} : {', '.join(a['skills'])}" for a in dataset["agents"]]
        self.label_agents.setText("<br>".join(agents_lines))

        # Lancer thread VRP avec dataset fixe
        self.thread = VRPThread(
            test_type="Random Small",
            num_patients=num_patients,
            num_agents=num_agents,
            seed=42,
            data=dataset,
        )
        self.thread.result_signal.connect(lambda total, routes, coords, ds: self.show_result(total, routes, coords))
        self.thread.start()

    def show_result(self, distance, routes, coords):
        self.label_result.setText(f"Distance totale : {distance:.2f}")
        self.coords = coords
        # routes arrive now as dict agent -> {route: [...], visited_patients: [...]}
        formatted_routes = {k: v.get("route", []) for k, v in routes.items()}
        self.plot.update_plot(formatted_routes, coords)

    def on_click(self, event):
        if event.xdata is None or event.ydata is None:
            return
        for pid, (x, y) in self.coords.items():
            if abs(event.xdata - x) < 0.5 and abs(event.ydata - y) < 0.5:
                self.open_info_dialog(pid)
                break

    def open_info_dialog(self, pid):
        info = self.patients_info[pid]

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Informations Patient {pid}")
        layout = QFormLayout(dialog)

        coord_x = QLineEdit(str(info["coords"][0]))
        coord_y = QLineEdit(str(info["coords"][1]))
        service = QLineEdit(str(info["service"]))
        skill = QLineEdit(info["skill"])

        layout.addRow("X:", coord_x)
        layout.addRow("Y:", coord_y)
        layout.addRow("Temps service:", service)
        layout.addRow("Compétence:", skill)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def save():
            self.patients_info[pid]["coords"] = (float(coord_x.text()), float(coord_y.text()))
            self.patients_info[pid]["service"] = float(service.text())
            self.patients_info[pid]["skill"] = skill.text()
            self.plot.update_plot({}, self.coords)  # rafraîchit le graphe
            dialog.accept()

        buttons.accepted.connect(save)
        buttons.rejected.connect(dialog.reject)

        dialog.exec_()
