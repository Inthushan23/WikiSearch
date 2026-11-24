from .graph_agent import build_graph


class GraphManager:
    def __init__(self):
        self.graphs: dict = {}
        self.build_load_graph(model_name="qwen3.5:4b")

    def _graph_exist(self, model_name: str):
        if model_name in self.graphs.keys():
            return True
        return False

    def build_load_graph(self, model_name: str):
        if not self._graph_exist(model_name=model_name):
            graph = build_graph(model=model_name)
            self.graphs[model_name] = graph

    def get_graph(self, model_name: str):
        return self.graphs[model_name]
