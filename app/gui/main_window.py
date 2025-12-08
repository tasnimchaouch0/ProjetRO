import sys
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout
)
from .plot_widget import PlotWidget
from ..threads.vrp_thread import VRPThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VRP Santé - Optimisation Infirmiers")
        self.setGeometry(100, 100, 900, 700)

        main_layout = QVBoxLayout()

        # Label pour afficher le type de test sélectionné
        self.label_test_type = QLabel("Sélectionnez un type de test")
        main_layout.addWidget(self.label_test_type)

        # Boutons pour choisir le type de test
        button_layout = QHBoxLayout()
        self.btn_small = QPushButton("Petit test")
        self.btn_medium = QPushButton("Test moyen")
        self.btn_large = QPushButton("Grand test")
        button_layout.addWidget(self.btn_small)
        button_layout.addWidget(self.btn_medium)
        button_layout.addWidget(self.btn_large)
        main_layout.addLayout(button_layout)

        self.btn_small.clicked.connect(lambda: self.run_vrp("small"))
        self.btn_medium.clicked.connect(lambda: self.run_vrp("medium"))
        self.btn_large.clicked.connect(lambda: self.run_vrp("large"))

        # Label résultat
        self.label_result = QLabel("")
        main_layout.addWidget(self.label_result)

        # Widget pour le graphe
        self.plot = PlotWidget()
        main_layout.addWidget(self.plot)

        # Widget central
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def run_vrp(self, test_type):
        self.label_test_type.setText(f"Type de test sélectionné : {test_type}")
        self.label_result.setText("Optimisation en cours...")

        # On passe test_type au thread
        self.thread = VRPThread(test_type)
        self.thread.result_signal.connect(self.show_result)
        self.thread.start()

    def show_result(self, distance, routes, coords):
        self.label_result.setText(f"Distance totale : {distance:.2f}")
        self.plot.update_plot(routes, coords)
