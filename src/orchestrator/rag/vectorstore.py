# Placeholder: in-memory list as vectorstore mock
class VectorStore:
    def __init__(self): self.items = []
    def add(self, item): self.items.append(item)
    def search(self, q): return self.items