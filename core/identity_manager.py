import numpy as np

class IdentityManager:
    def __init__(self):
        self.embeddings = {}

    def save_embedding(self, slot_id, embedding):
        self.embeddings[slot_id] = embedding

    def export_embedding(self, slot_id, path):
        np.save(path, self.embeddings[slot_id])
