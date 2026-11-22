from langgraph.checkpoint.memory import MemorySaver


class MemoryManager:
    def __init__(self):
        self.memory_manager: dict = {}


    def create_memory(self, graph_name: str):
        memory = MemorySaver()
        self.memory_manager[graph_name] = memory
        return memory

    def get_memory(self, graph_name: str):
        return self.memory_manager[graph_name]

    def delete_memory(self, graph_name):
        self.memory_manager[graph_name] = None
