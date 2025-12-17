"""
Domain models for VRP Healthcare Optimization System.
Uses Object-Oriented Programming to represent patients, agents, and VRP instances.
"""

from typing import List, Tuple, Optional


class Depot:
    """Représente le dépôt (point de départ/retour des infirmiers)."""
    
    def __init__(self, id: int = 0, lat: float = 0.0, lon: float = 0.0):
        self.id = id
        self.lat = lat
        self.lon = lon
    
    def get_coords(self) -> Tuple[float, float]:
        """Retourne les coordonnées (lat, lon)."""
        return (self.lat, self.lon)
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour compatibilité."""
        return {
            "id": self.id,
            "lat": self.lat,
            "lon": self.lon
        }
    
    def __repr__(self):
        return f"Depot(id={self.id}, lat={self.lat}, lon={self.lon})"


class Patient:
    """Représente un patient nécessitant une visite à domicile."""
    
    def __init__(
        self,
        id: int,
        required_skill: str,
        lat: float,
        lon: float,
        duration: int,
        time_window: Optional[List[int]] = None
    ):
        self.id = id
        self.required_skill = required_skill
        self.lat = lat
        self.lon = lon
        self.duration = duration
        self.time_window = time_window or [0, 300]
    
    def get_coords(self) -> Tuple[float, float]:
        """Retourne les coordonnées (lat, lon)."""
        return (self.lat, self.lon)
    
    def set_coords(self, lat: float, lon: float):
        """Modifie les coordonnées du patient."""
        self.lat = lat
        self.lon = lon
    
    def set_skill(self, skill: str):
        """Modifie la compétence requise."""
        self.required_skill = skill
    
    def set_duration(self, duration: int):
        """Modifie la durée du service."""
        self.duration = duration
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour compatibilité."""
        return {
            "id": self.id,
            "required_skill": self.required_skill,
            "lat": self.lat,
            "lon": self.lon,
            "duration": self.duration,
            "time_window": self.time_window
        }
    
    def __repr__(self):
        return f"Patient(id={self.id}, skill={self.required_skill}, coords=({self.lat}, {self.lon}))"


class Agent:
    """Représente un infirmier avec ses compétences et contraintes."""
    
    def __init__(
        self,
        id: int,
        name: str,
        skills: List[str],
        lat: float = 0.0,
        lon: float = 0.0,
        max_patients: int = 8,
        shift_duration: int = 300
    ):
        self.id = id
        self.name = name
        self.skills = sorted(skills)  # Tri pour cohérence
        self.lat = lat
        self.lon = lon
        self.max_patients = max_patients
        self.shift_duration = shift_duration
    
    def has_skill(self, skill: str) -> bool:
        """Vérifie si l'agent possède une compétence."""
        return skill in self.skills
    
    def add_skill(self, skill: str):
        """Ajoute une compétence à l'agent."""
        if skill not in self.skills:
            self.skills.append(skill)
            self.skills.sort()
    
    def get_coords(self) -> Tuple[float, float]:
        """Retourne les coordonnées (lat, lon)."""
        return (self.lat, self.lon)
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour compatibilité."""
        return {
            "id": self.id,
            "name": self.name,
            "skills": self.skills,
            "lat": self.lat,
            "lon": self.lon,
            "max_patients": self.max_patients,
            "shift_duration": self.shift_duration
        }
    
    def __repr__(self):
        skills_str = ", ".join(self.skills)
        return f"Agent(id={self.id}, name='{self.name}', skills=[{skills_str}])"


class VRPInstance:
    """Représente une instance complète du problème VRP."""
    
    def __init__(self, depot: Depot, agents: List[Agent], patients: List[Patient]):
        self.depot = depot
        self.agents = agents
        self.patients = patients
    
    def get_patient_by_id(self, patient_id: int) -> Optional[Patient]:
        """Récupère un patient par son ID."""
        for patient in self.patients:
            if patient.id == patient_id:
                return patient
        return None
    
    def get_agent_by_id(self, agent_id: int) -> Optional[Agent]:
        """Récupère un agent par son ID."""
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None
    
    def get_all_coords(self) -> dict:
        """Retourne toutes les coordonnées (dépôt + patients)."""
        coords = {self.depot.id: self.depot.get_coords()}
        for patient in self.patients:
            coords[patient.id] = patient.get_coords()
        return coords
    
    def get_all_available_skills(self) -> set:
        """Retourne toutes les compétences disponibles parmi les agents."""
        all_skills = set()
        for agent in self.agents:
            all_skills.update(agent.skills)
        return all_skills
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour compatibilité avec code existant."""
        return {
            "depot": self.depot.to_dict(),
            "agents": [agent.to_dict() for agent in self.agents],
            "patients": [patient.to_dict() for patient in self.patients]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VRPInstance':
        """Crée une instance VRPInstance à partir d'un dictionnaire."""
        depot = Depot(**data["depot"])
        agents = [Agent(**agent_data) for agent_data in data["agents"]]
        patients = [Patient(**patient_data) for patient_data in data["patients"]]
        return cls(depot=depot, agents=agents, patients=patients)
    
    def __repr__(self):
        return f"VRPInstance(depot={self.depot}, {len(self.agents)} agents, {len(self.patients)} patients)"
