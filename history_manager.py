# history_manager.py
from collections import deque

class HistoryManager:
    def __init__(self, filename: str):
        self.filename = filename
        self.historico = self.load_historico()

    def load_historico(self):
        historico = deque(maxlen=10)
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                for linha in f:
                    historico.append(linha.strip())
        except FileNotFoundError:
            pass
        return historico

    def save_historico(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            for linha in self.historico:
                f.write(linha + "\n")

    def mostrar_historico(self):
        if self.historico:
            print("\n📜 Últimas interações (até 5):")
            for i in range(0, len(self.historico), 2):
                try:
                    print(self.historico[i])
                    print(self.historico[i + 1])
                except IndexError:
                    pass
            print("-" * 40)