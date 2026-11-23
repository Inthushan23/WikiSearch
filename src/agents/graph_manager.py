from .graph_agent import build_graph


class GraphManager:
    def __init__(self):
        self.graphs: dict = {}

    def _graph_exist(self, graph_name: str):
        if graph_name in self.graphs.keys():
            return True
        return False

    def build_load_graph(self, username: str, model_name: str, url: str, memory):
        graph_name = username + "-" + model_name

        if not self._graph_exist(graph_name=graph_name):
            graph = build_graph(username=username, model=model_name, url=url).compile(
                checkpointer=memory
            )
            self.graphs[graph_name] = graph
            return graph
        else:
            return self.graphs[graph_name]

    def get_graph(self, graph_name: str):
        return self.graphs[graph_name]

    def remove_graph(self, graph_name: str, thread_id: str, memory):
        memory.delete_thread(thread_id)
        self.graphs.pop(graph_name, None)
