from PyQt5.QtCore import QThread, pyqtSignal
from ..core.solver import solve_instance


class VRPThread(QThread):
    result_signal = pyqtSignal(float, dict, dict)
    def __init__(self, test_type="Random Small"):
        super().__init__()
        self.test_type = test_type
    def run(self):
        routes, coords = solve_instance(test_type=self.test_type)

        # calcule distance totale
        total = 0
        for k, route in routes.items():
            for i in range(len(route)-1):
                (x1, y1) = coords[route[i]]
                (x2, y2) = coords[route[i+1]]
                total += ((x1 - x2)**2 + (y1 - y2)**2)**0.5

        self.result_signal.emit(total, routes, coords)
