from sentence_transformers import SentenceTransformer


class LoadModel:
    def __init__(self, model_name):
        self.model_name = model_name
    
    # Return the model instance, load if not already loaded
    def get_model(self):
        try:
            model = SentenceTransformer(self.model_name)
        except Exception as e:
            print(f"Error when loading the model - {e}")
            return None
        return model