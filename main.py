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

def get_answer_for_question(pergunta: str, knowledge_base: dict) -> str | None:
    for i in knowledge_base["perguntas"]:
        if i["perguntas"] == pergunta:
            return i["resposta"]
        
def chat_bot():
    knowledge_base: dict = load_knowledge_base('knowledge_base.json')

    while True:
        user_input: str = input('You: ')

        if user_input.lower() == 'sair':
            break

        best_match: str | None = find_best_match(user_input, [i["pergunta"] for i in knowledge_base["perguntas"]])

        if best_match:
            resposta =  get_answer_for_question(best_match, knowledge_base)
            print(f"TrampoJuá: {resposta}")
        else:
            print('TrampoJuá: Não sei te informar sobre isso. Você pode me ensinar?')
            new_answer: str = input('Digite a resposta ou "pular" para pular: ')

            if new_answer.lower() != 'pular':
                knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
                save_knowledge_base('knowledge_base.json', knowledge_base)
                print('TrampoJuá: Obrigado! Aprendi uma nova informação!')

if __name__ == '__main__':
    chat_bot()

