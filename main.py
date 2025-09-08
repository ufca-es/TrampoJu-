import json
from difflib import get_close_matches

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent = 2)

def find_best_match(user_question: str, perguntas: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, perguntas, n = 1, cutoff = 0.6)
    return matches[0] if matches else None

def resposta_para_pergunta(pergunta: str, knowledge_base: dict, tipo_resposta: str) -> str | None:
    for i in knowledge_base["perguntas"]:
        if i["pergunta"] == pergunta:
            return i[tipo_resposta]
        
def chat_bot():
    knowledge_base: dict = load_knowledge_base('knowledge_base.json')

    while True:

        personalidade_resposta = int(input('1 - Formal\n2 - Orientador\n3 - Engraçado\nPersonalidade: '))
        user_input: str = input('You: ')

        if user_input.lower() == 'sair':
            break
        
        if personalidade_resposta == 1:
            tipo_resposta = "resposta_formal"
            best_match: str | None = find_best_match(user_input, [i["pergunta"] for i in knowledge_base["perguntas"]])
        
            if best_match:
                personalidade_formal = Personalidades(knowledge_base, best_match, tipo_resposta)
                personalidade_formal.resposta_formal()
        
            else:
                print('TrampoJuá: Não sei te informar sobre isso. Você pode me ensinar?')
                new_answer: str = input('Digite a resposta ou "pular" para pular: ')

                if new_answer.lower() != 'pular':
                    knowledge_base["perguntas"].append({"pergunta": user_input, "resposta_formal": new_answer})
                    save_knowledge_base('knowledge_base.json', knowledge_base)
                    print('TrampoJuá: Obrigado! Aprendi uma nova informação!')

class Personalidades:
    def __init__(self, knowledge_base, best_match, tipo_resposta):
        self.resposta = resposta_para_pergunta(best_match, knowledge_base, tipo_resposta)
    def resposta_formal(self):
        print(f"TrampoJuá (Formal): {self.resposta}")
    def resposta_orientador(self):
        print(f"TrampoJuá (Orientador): {self.resposta}")


if __name__ == '__main__':
    chat_bot()




