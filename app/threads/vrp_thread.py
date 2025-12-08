from PyQt5.QtCore import QThread, pyqtSignal

from ..core.solver import solve_instance


class VRPThread(QThread):
    result_signal = pyqtSignal(float, dict, dict, dict)

    def __init__(self, test_type="Random Small", num_patients=5, num_agents=3, seed=None, data=None):
        super().__init__()
        self.test_type = test_type
        self.num_patients = num_patients
        self.num_agents = num_agents
        self.seed = seed
        self.data = data

    def run(self):
        result, coords = solve_instance(
            data=self.data,
            test_type=self.test_type,
            num_patients=self.num_patients,
            num_agents=self.num_agents,
            seed=self.seed,
        )

        total = sum(r.get("total_distance", 0.0) for r in result.values())
        self.result_signal.emit(total, result, coords, self.data)
