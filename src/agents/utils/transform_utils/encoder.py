from ..loader_utils.load_model import LoadModel


class Encoder:
    # Load the sentence transformer model
    def __init__(self, model_name: str):
        self._model_name = model_name
        self.model = LoadModel(self._model_name).get_model()

    # Encode input text(s) into embeddings
    def encode(
        self,
        ipt: str | list[str],
        batch_size=64,
        show_progress_bar: bool = False,
        conv_to_tensor: bool = False,
    ):
        return self.model.encode(
            inputs=ipt,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            convert_to_tensor=conv_to_tensor,
        )
