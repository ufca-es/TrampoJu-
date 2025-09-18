# conversation_manager.py
import random
from difflib import get_close_matches
from data_manager import DataManager

class ConversationManager:
    def __init__(self, data_manager: DataManager, conhecimento_file: str, perguntas_file: str):
        self.data_manager = data_manager
        self.conhecimento_file = conhecimento_file
        self.perguntas_file = perguntas_file
        self.knowledge_base = self.data_manager.load_json(self.conhecimento_file, "perguntas")

    def get_resposta(self, user_input: str):
        perguntas = [i["pergunta"] for i in self.knowledge_base["perguntas"]]
        best_match = get_close_matches(user_input, perguntas, n=1, cutoff=0.6)

        if best_match:
            respostas = next(i["respostas"] for i in self.knowledge_base["perguntas"] if i["pergunta"] == best_match[0])
            return random.choice(respostas)
        return None

    def aprender_nova_resposta(self, user_input: str, new_answer: str):
        encontrado = False
        for i in self.knowledge_base["perguntas"]:
            if i["pergunta"] == user_input:
                i["respostas"].append(new_answer)
                encontrado = True
                break
        if not encontrado:
            self.knowledge_base["perguntas"].append({"pergunta": user_input, "respostas": [new_answer]})

        self.data_manager.save_json(self.conhecimento_file, self.knowledge_base)

    def save_pergunta_e_resposta_nova(self, pergunta: str, resposta: str):
        with open(self.perguntas_file, "a", encoding="utf-8") as f:
            f.write(f"Q: {pergunta} | A: {resposta}\n")

    def load_perguntas_e_respostas_novas(self):
        perguntas_e_respostas = []
        try:
            with open(self.perguntas_file, "r", encoding="utf-8") as f:
                for linha in f:
                    partes = linha.strip().split(" | A: ")
                    if len(partes) == 2:
                        pergunta = partes[0].replace("Q: ", "").strip()
                        resposta = partes[1].strip()
                        perguntas_e_respostas.append({"pergunta": pergunta, "resposta": resposta})
        except FileNotFoundError:
            pass
        return perguntas_e_respostas

    def limpar_perguntas_novas(self):
        with open(self.perguntas_file, "w", encoding="utf-8") as f:
            f.write("")