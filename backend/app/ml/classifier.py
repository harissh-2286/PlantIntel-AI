from app.ml.model import ai_model

class Classifier:
    @staticmethod
    def predict(image_bytes: bytes):
        return ai_model.predict(image_bytes)
        
    @staticmethod
    def get_metadata():
        return ai_model.get_metadata()
        
    @staticmethod
    def is_ready():
        return ai_model.is_ready
