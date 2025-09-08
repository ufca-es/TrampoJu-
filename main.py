import json
from difflib import get_close_matches

class ChatBot:
    def __init__(self, nome: str, arquivo_base: str, personalidade: str = "padrão"):
        self.nome = nome
        self.arquivo_base = arquivo_base
        self.personalidade = personalidade
        self.knowledge_base = self.load_knowledge_base()

    # Carregar base de conhecimento
    def load_knowledge_base(self) -> dict:
        try:
            with open(self.arquivo_base, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"perguntas": []}

    # Salvar base de conhecimento
    def save_knowledge_base(self):
        with open(self.arquivo_base, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)

    # Encontrar melhor correspondência
    def find_best_match(self, user_question: str) -> str | None:
        perguntas = [i["pergunta"] for i in self.knowledge_base["perguntas"]]
        matches = get_close_matches(user_question, perguntas, n=1, cutoff=0.6)
        return matches[0] if matches else None

    # Pegar resposta para pergunta
    def get_answer_for_question(self, pergunta: str) -> str | None:
        for i in self.knowledge_base["perguntas"]:
            if i["pergunta"] == pergunta:
                return i["resposta"]

    # Estilo da personalidade
    def falar(self, mensagem: str) -> str:
        if self.personalidade == "formal":
            return f"{self.nome}: Prezado usuário, {mensagem}"
        elif self.personalidade == "amigável":
            return f"{self.nome}: 😃 {mensagem}"
        elif self.personalidade == "motivacional":
            return f"{self.nome}: 💪 {mensagem}! Você consegue!"
        else:
            return f"{self.nome}: {mensagem}"

    # Alterar personalidade durante execução
    def alterar_personalidade(self, nova: str):
        if nova in ["formal", "amigável", "motivacional", "padrão"]:
            self.personalidade = nova
            print(self.falar(f"Personalidade alterada para '{nova}'."))
        else:
            print(self.falar("Não conheço essa personalidade."))

    # Loop de interação
    def iniciar(self):
        while True:
            user_input = input("Você: ")

            if user_input.lower() == "sair":
                print(self.falar("Até logo!"))
                break

            # Comando para mudar personalidade
            if user_input.lower().startswith("mudar personalidade"):
                _, _, nova = user_input.partition(" ")
                nova = nova.replace("personalidade", "").strip()
                self.alterar_personalidade(nova)
                continue

            best_match = self.find_best_match(user_input)

            if best_match:
                resposta = self.get_answer_for_question(best_match)
                print(self.falar(resposta))
            else:
                print(self.falar("Não sei te informar sobre isso. Você pode me ensinar?"))
                new_answer = input("Digite a resposta ou 'pular' para pular: ")

                if new_answer.lower() != "pular":
                    self.knowledge_base["perguntas"].append(
                        {"pergunta": user_input, "resposta": new_answer}
                    )
                    self.save_knowledge_base()
                    print(self.falar("Obrigado! Aprendi uma nova informação!"))

if __name__ == "__main__":
    bot = ChatBot(nome="TrampoJuá", arquivo_base="knowledge_base.json", personalidade="padrão")
    bot.iniciar()