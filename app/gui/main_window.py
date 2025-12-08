import sys
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QSpinBox, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QGroupBox, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from .plot_widget import PlotWidget
from ..threads.vrp_thread import VRPThread
from ..gui.data_generator import generate_instance

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏥 VRP Santé - Optimisation des Tournées Infirmiers")
        self.setGeometry(100, 100, 1400, 800)
        
        # Style moderne
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #34495e;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                color: #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            QSpinBox {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
                background-color: white;
            }
            QSpinBox:focus {
                border: 2px solid #3498db;
            }
        """)

        self.patients_info = {}  # stocke info de chaque patient
        self.coords = {}          # coordonnées utilisées pour le graphe
        self.last_routes = {}     # dernières routes calculées pour le rafraîchissement
        self.current_dataset = None  # dataset actuel pour relancer l'optimisation

        # Layout principal avec sidebar et graphe
        main_layout = QHBoxLayout()
        
        # === SIDEBAR GAUCHE ===
        sidebar = QVBoxLayout()
        sidebar.setSpacing(15)
        
        # Groupe Paramètres
        params_group = QGroupBox("Paramètres")
        params_layout = QVBoxLayout()
        
        # Nombre de patients
        patients_label = QLabel("Nombre de patients :")
        patients_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        params_layout.addWidget(patients_label)
        self.spin_patients = QSpinBox()
        self.spin_patients.setMinimum(1)
        self.spin_patients.setMaximum(10)
        self.spin_patients.setValue(5)
        params_layout.addWidget(self.spin_patients)
        
        # Nombre d'agents
        agents_label = QLabel("Nombre d'infirmiers :")
        agents_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        params_layout.addWidget(agents_label)
        self.spin_agents = QSpinBox()
        self.spin_agents.setMinimum(1)
        self.spin_agents.setMaximum(10)
        self.spin_agents.setValue(2)
        params_layout.addWidget(self.spin_agents)
        
        params_group.setLayout(params_layout)
        sidebar.addWidget(params_group)
        
        # Bouton optimisation
        self.btn_run = QPushButton("Lancer l'optimisation")
        self.btn_run.clicked.connect(self.run_vrp)
        self.btn_run.setMinimumHeight(50)
        sidebar.addWidget(self.btn_run)
        
        # Groupe Infirmiers
        agents_group = QGroupBox("Équipe d'infirmiers")
        agents_group.setMaximumHeight(180)
        agents_layout = QVBoxLayout()
        
        agents_scroll = QScrollArea()
        agents_scroll.setWidgetResizable(True)
        agents_scroll.setStyleSheet("border: none;")
        
        self.label_agents = QLabel("En attente...")
        self.label_agents.setWordWrap(True)
        self.label_agents.setStyleSheet("padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        agents_scroll.setWidget(self.label_agents)
        agents_layout.addWidget(agents_scroll)
        agents_group.setLayout(agents_layout)
        sidebar.addWidget(agents_group)
        
        # Groupe Résultat
        result_group = QGroupBox("Résultat")
        result_layout = QVBoxLayout()
        self.label_result = QLabel("Aucune optimisation lancée")
        self.label_result.setWordWrap(True)
        self.label_result.setStyleSheet("""
            padding: 15px;
            background-color: #e8f8f5;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            color: #16a085;
        """)
        result_layout.addWidget(self.label_result)
        result_group.setLayout(result_layout)
        sidebar.addWidget(result_group)
        
        # Groupe Circuits
        circuits_group = QGroupBox("Circuits détaillés")
        circuits_layout = QVBoxLayout()
        
        self.label_circuits = QLabel("Aucun circuit calculé")
        self.label_circuits.setWordWrap(True)
        self.label_circuits.setStyleSheet("""
            padding: 8px;
            background-color: #fef9e7;
            border-radius: 5px;
            font-size: 11px;
        """)
        circuits_layout.addWidget(self.label_circuits)
        circuits_group.setLayout(circuits_layout)
        sidebar.addWidget(circuits_group)
        
        sidebar.addStretch()
        
        # Sidebar widget
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setMaximumWidth(400)
        sidebar_widget.setMinimumWidth(350)
        
        # === GRAPHE DROITE ===
        graph_layout = QVBoxLayout()
        graph_label = QLabel("Carte des tournées")
        graph_label.setStyleSheet("font-size: 11px; color: #2c3e50; padding: 2px;")
        graph_label.setAlignment(Qt.AlignCenter)
        graph_label.setMaximumHeight(20)
        graph_layout.addWidget(graph_label)
        
        self.plot = PlotWidget()
        graph_layout.addWidget(self.plot)
        
        graph_widget = QWidget()
        graph_widget.setLayout(graph_layout)
        
        # Assemblage
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(graph_widget, stretch=1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # connecter le click sur le graphe
        self.plot.canvas.mpl_connect("button_press_event", self.on_click)

    def run_vrp(self):
        num_patients = self.spin_patients.value()
        num_agents = self.spin_agents.value()
        
        if num_patients > 10 or num_agents > 10:
            self.label_result.setText("Limites : max 10 patients, 10 infirmiers")
            self.label_result.setStyleSheet("""
                padding: 15px;
                background-color: #fadbd8;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #c0392b;
            """)
            return
        
        self.label_result.setText("Optimisation en cours...")
        self.label_result.setStyleSheet("""
            padding: 15px;
            background-color: #fff3cd;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
            color: #856404;
        """)

        # Génération unique de l'instance pour GUI + solver
        dataset = generate_instance(test_type="Random Small", num_patients=num_patients, num_agents=num_agents, seed=42)
        
        # Sauvegarder le dataset pour pouvoir le modifier plus tard
        self.current_dataset = dataset

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

        # Afficher les infirmiers et leurs compétences avec émojis
        agents_html = ""
        skill_emojis = {
            "Nursing": "💉",
            "WoundCare": "🩹",
            "Pediatrics": "👶",
            "Diabetes": "🍬",
            "Physio": "🏃"
        }
        for a in dataset["agents"]:
            skills_with_emoji = [f"{skill_emojis.get(s, '✓')} {s}" for s in a['skills']]
            agents_html += f"<b>{a['name']}</b><br>"
            agents_html += f"<span style='color: #7f8c8d; font-size: 11px;'>{', '.join(skills_with_emoji)}</span><br><br>"
        
        self.label_agents.setText(agents_html)

        # Désactiver le bouton pendant l'optimisation
        self.btn_run.setEnabled(False)
        
        # Lancer thread VRP avec dataset fixe
        self.thread = VRPThread(
            test_type="Random Small",
            num_patients=num_patients,
            num_agents=num_agents,
            seed=42,
            data=dataset,
        )
        self.thread.result_signal.connect(lambda total, routes, coords, ds: self.show_result(total, routes, coords))
        self.thread.finished.connect(lambda: self.btn_run.setEnabled(True))
        self.thread.start()

    def show_result(self, distance, routes, coords):
        self.label_result.setText(f"Distance totale : {distance:.2f} km")
        self.label_result.setStyleSheet("""
            padding: 15px;
            background-color: #d5f4e6;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            color: #27ae60;
        """)
        
        self.coords = coords
        # Sauvegarder les routes pour pouvoir rafraîchir après modification
        self.last_routes = routes
        
        # Afficher les circuits détaillés
        circuits_html = ""
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22", "#34495e", "#16a085", "#d35400"]
        
        for idx, (agent_id, route_info) in enumerate(routes.items()):
            route = route_info.get("route", [])
            total_dist = route_info.get("total_distance", 0)
            color = colors[idx % len(colors)]
            
            if len(route) > 2:  # A une vraie route (plus que dépôt→dépôt)
                route_str = " → ".join([f"<b>D</b>" if node == 0 else f"P{node}" for node in route])
                circuits_html += f"<div style='margin-bottom: 8px; padding: 6px; background-color: {color}22; border-left: 3px solid {color}; border-radius: 4px;'>"
                circuits_html += f"<b style='color: {color}; font-size: 12px;'>Inf. {agent_id}</b> "
                circuits_html += f"<span style='color: #7f8c8d; font-size: 10px;'>({total_dist:.1f} km)</span><br>"
                circuits_html += f"<span style='color: #2c3e50; font-size: 11px;'>{route_str}</span>"
                circuits_html += "</div>"
            else:
                circuits_html += f"<div style='margin-bottom: 6px; padding: 5px; background-color: #ecf0f1; border-radius: 4px;'>"
                circuits_html += f"<span style='color: #95a5a6; font-size: 11px;'>Inf. {agent_id} : Non assigné</span>"
                circuits_html += "</div>"
        
        self.label_circuits.setText(circuits_html if circuits_html else "Aucun circuit calculé")
        
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
        dialog.setWindowTitle(f" Édition Patient {pid}")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel {
                font-size: 12px;
                color: #2c3e50;
                font-weight: bold;
            }
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        dialog.setMinimumWidth(350)
        
        layout = QFormLayout(dialog)
        layout.setSpacing(15)

        coord_x = QLineEdit(str(info["coords"][0]))
        coord_y = QLineEdit(str(info["coords"][1]))
        service = QLineEdit(str(info["service"]))
        skill = QLineEdit(info["skill"])

        layout.addRow("📍 Coordonnée X:", coord_x)
        layout.addRow("📍 Coordonnée Y:", coord_y)
        layout.addRow("⏱️ Temps de service:", service)
        layout.addRow("🎯 Compétence requise:", skill)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def save():
            new_x = float(coord_x.text())
            new_y = float(coord_y.text())
            new_service = float(service.text())
            new_skill = skill.text()
            
            # Mettre à jour les structures locales
            self.patients_info[pid]["coords"] = (new_x, new_y)
            self.coords[pid] = (new_x, new_y)
            self.patients_info[pid]["service"] = new_service
            self.patients_info[pid]["skill"] = new_skill
            
            # Mettre à jour le dataset pour relancer l'optimisation
            if self.current_dataset is not None:
                # Mettre à jour le patient dans le dataset
                for p in self.current_dataset["patients"]:
                    if p["id"] == pid:
                        p["lat"] = new_x
                        p["lon"] = new_y
                        p["duration"] = new_service
                        p["required_skill"] = new_skill
                        break
                
                # Relancer l'optimisation avec le dataset modifié
                self.label_result.setText("Ré-optimisation en cours...")
                self.label_result.setStyleSheet("""
                    padding: 15px;
                    background-color: #fff3cd;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #856404;
                """)
                self.btn_run.setEnabled(False)
                
                self.thread = VRPThread(
                    test_type="Random Small",
                    num_patients=len(self.current_dataset["patients"]),
                    num_agents=len(self.current_dataset["agents"]),
                    seed=42,
                    data=self.current_dataset,
                )
                self.thread.result_signal.connect(lambda total, routes, coords, ds: self.show_result(total, routes, coords))
                self.thread.finished.connect(lambda: self.btn_run.setEnabled(True))
                self.thread.start()
            
            dialog.accept()

        buttons.accepted.connect(save)
        buttons.rejected.connect(dialog.reject)

        dialog.exec_()
