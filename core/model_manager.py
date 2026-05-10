class ModelManager:
    def __init__(self):
        self.models = {}

    def load_model(self, name, path):
        self.models[name] = path
