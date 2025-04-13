import numpy as np

class SimpleTracker:
    def __init__(self, max_distance=50, max_age=5):
        self.next_id = 0
        self.active = {}  # id: box
        self.lost = {}    # id: (box, frames_missing)
        self.max_distance = max_distance
        self.max_age = max_age

        self.class_history = {}  # id: [classificações anteriores]

    def _get_center(self, box):
        x1, y1, x2, y2 = box
        return (x1 + x2) / 2, (y1 + y2) / 2

    def _get_smoothed_classification(self, obj_id):
        history = self.class_history.get(obj_id, [])
        if not history:
            return None
        return max(set(history), key=history.count)  # classificação mais frequente

    def update(self, detections, classifications=None):
        matched_ids = set()
        updated_active = {}
        updated_class_history = {}

        for i, det in enumerate(detections):
            x1, y1, x2, y2, conf = det
            center = self._get_center([x1, y1, x2, y2])
            matched_id = None
            min_distance = float('inf')

            for obj_id, prev_box in self.active.items():
                prev_center = self._get_center(prev_box)
                distance = np.linalg.norm(np.array(center) - np.array(prev_center))
                if distance < self.max_distance and obj_id not in matched_ids and distance < min_distance:
                    matched_id = obj_id
                    min_distance = distance

            if matched_id is None:
                for obj_id, (prev_box, frames_missing) in self.lost.items():
                    if frames_missing > self.max_age or obj_id in matched_ids:
                        continue
                    prev_center = self._get_center(prev_box)
                    distance = np.linalg.norm(np.array(center) - np.array(prev_center))
                    if distance < self.max_distance and distance < min_distance:
                        matched_id = obj_id
                        min_distance = distance

            if matched_id is not None:
                updated_active[matched_id] = [x1, y1, x2, y2]
                matched_ids.add(matched_id)
                self.lost.pop(matched_id, None)
                if classifications:
                    updated_class_history[matched_id] = self.class_history.get(matched_id, []) + [classifications[i]]
            else:
                updated_active[self.next_id] = [x1, y1, x2, y2]
                matched_ids.add(self.next_id)
                if classifications:
                    updated_class_history[self.next_id] = [classifications[i]]
                self.next_id += 1

        # Atualiza objetos perdidos
        new_lost = {}
        for obj_id, box in self.active.items():
            if obj_id not in matched_ids:
                new_lost[obj_id] = (box, 1)
        for obj_id, (box, age) in self.lost.items():
            if obj_id not in matched_ids:
                if age + 1 <= self.max_age:
                    new_lost[obj_id] = (box, age + 1)

        self.active = updated_active
        self.lost = new_lost

        for obj_id, history in updated_class_history.items():
            self.class_history[obj_id] = history[-5:]  # mantém últimas 5 classificações

        # Retorna lista com ID, caixa e classificação suavizada
        return [(obj_id, *box, self._get_smoothed_classification(obj_id)) for obj_id, box in self.active.items()]
