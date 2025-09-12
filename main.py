import json
import random
from difflib import get_close_matches
from collections import deque


class ChatBotEmpregos:
    def __init__(self, nome: str, arquivo_vagas: str, arquivo_conhecimento: str, arquivo_historico: str, arquivo_perguntas: str, personalidade: str = "formal"):
        self.nome = nome
        self.arquivo_vagas = arquivo_vagas
        self.arquivo_conhecimento = arquivo_conhecimento
        self.arquivo_historico = arquivo_historico
        self.arquivo_perguntas = arquivo_perguntas  # novo arquivo
        self.personalidade = personalidade
        self.vagas = self.load_database(self.arquivo_vagas, "vagas")
        self.knowledge_base = self.load_database(self.arquivo_conhecimento, "perguntas")
        self.historico = self.load_historico()

    # ---------------- HISTÓRICO ----------------
    def load_historico(self):
        historico = deque(maxlen=10)  # 5 interações completas
        try:
            with open(self.arquivo_historico, "r", encoding="utf-8") as f:
                for linha in f:
                    historico.append(linha.strip())
        except FileNotFoundError:
            pass
        return historico

    def save_historico(self):
        with open(self.arquivo_historico, "w", encoding="utf-8") as f:
            for linha in self.historico:
                f.write(linha + "\n")

    def mostrar_historico(self):
        if self.historico:
            print("\n📜 Últimas interações (até 5):")
            for i in range(0, len(self.historico), 2):
                try:
                    print(self.historico[i])       # Você
                    print(self.historico[i + 1])   # Bot
                except IndexError:
                    pass
            print("-" * 40)

    # ---------------- NOVAS PERGUNTAS ----------------
    def save_pergunta_nova(self, pergunta: str):
        with open(self.arquivo_perguntas, "a", encoding="utf-8") as f:
            f.write(pergunta + "\n")

    # ---------------- BANCOS DE DADOS ----------------
    def load_database(self, arquivo: str, chave: str) -> dict:
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                data = json.load(f)
                if chave not in data:
                    data[chave] = []
                return data
        except FileNotFoundError:
            return {chave: []}

    def save_database(self, arquivo: str, data: dict):
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ---------------- PERSONALIDADES ----------------
    def falar(self, mensagem: str) -> str:
        if self.personalidade == "formal":
            return f"{self.nome}: Prezado usuário, {mensagem}"
        elif self.personalidade == "orientador":
            return f"{self.nome}: 📘 Veja bem, {mensagem}. Continue se preparando para as entrevistas!"
        elif self.personalidade == "engraçado":
            return f"{self.nome}: 😂 {mensagem} (e se não conseguir emprego, sempre tem vaga de degustador de café!)"
        else:
            return f"{self.nome}: {mensagem}"

    def alterar_personalidade(self):
        print("\nEscolha uma personalidade:")
        print("1 - Formal")
        print("2 - Orientador")
        print("3 - Engraçado")
        escolha = input("Opção: ")

        if escolha == "1":
            self.personalidade = "formal"
        elif escolha == "2":
            self.personalidade = "orientador"
        elif escolha == "3":
            self.personalidade = "engraçado"
        else:
            print(self.falar("Opção inválida. Mantendo a personalidade atual."))
            return

        print(self.falar(f"Personalidade alterada para '{self.personalidade}'."))

    # ---------------- VAGAS ----------------
    def cadastrar_vaga(self):
        print("\n--- Cadastro de Vaga ---")
        titulo = input("Título da vaga: ")
        empresa = input("Empresa: ")
        local = input("Local: ")
        requisitos = input("Requisitos: ")
        segmento = input("Segmento (ADM, TI, Limpeza, Vendas): ")
        descricao = input("Descrição da vaga: ")

        self.vagas["vagas"].append({
            "titulo": titulo,
            "empresa": empresa,
            "local": local,
            "requisitos": requisitos,
            "segmento": segmento,
            "descricao": descricao
        })

        self.save_database(self.arquivo_vagas, self.vagas)
        print(self.falar("Vaga cadastrada com sucesso!"))

    def buscar_vaga(self):
        palavra = input("\nDigite uma palavra-chave ou segmento (ADM, TI, Limpeza, Vendas): ")
        resultados = []

        for vaga in self.vagas["vagas"]:
            texto = f"{vaga.get('titulo','')} {vaga.get('empresa','')} {vaga.get('local','')} {vaga.get('requisitos','')} {vaga.get('segmento','')}".lower()
            if palavra.lower() in texto:
                resultados.append(vaga)

        if resultados:
            print(self.falar(f"Encontrei {len(resultados)} vaga(s):"))
            for vaga in resultados:
                print(f"- {vaga.get('titulo','')} ({vaga.get('segmento','')}) - {vaga.get('descricao', vaga.get('local',''))}")
        else:
            print(self.falar("Não encontrei vagas com essa palavra-chave ou segmento."))

    def listar_vagas(self):
        if not self.vagas["vagas"]:
            print(self.falar("Não há vagas cadastradas no momento."))
            return

        print(self.falar(f"Temos {len(self.vagas['vagas'])} vaga(s) cadastrada(s):"))
        for vaga in self.vagas["vagas"]:
            print(f"- {vaga.get('titulo','')} ({vaga.get('segmento','')}) - {vaga.get('descricao', vaga.get('local',''))}")

    # ---------------- CONVERSA ----------------
    def conversa(self):
        print(self.falar("Você entrou no modo conversa. Digite 'sair' para voltar ao menu."))

        while True:
            user_input = input("Você: ")

            if user_input.lower() == "sair":
                print(self.falar("Saindo do modo conversa..."))
                break

            perguntas = [i["pergunta"] for i in self.knowledge_base["perguntas"]]
            best_match = get_close_matches(user_input, perguntas, n=1, cutoff=0.6)

            if best_match:
                respostas = next(i["respostas"] for i in self.knowledge_base["perguntas"] if i["pergunta"] == best_match[0])
                resposta = random.choice(respostas)

                if resposta == "listagem":
                    self.listar_vagas()
                elif resposta in ["ADM", "TI", "Limpeza", "Vendas"]:
                    resultados = [v for v in self.vagas["vagas"] if v.get("segmento", "") == resposta]
                    if resultados:
                        print(self.falar(f"Vagas do segmento {resposta}:"))
                        for vaga in resultados:
                            print(f"- {vaga.get('titulo','')} ({vaga.get('segmento','')}) - {vaga.get('descricao','')}")
                    else:
                        print(self.falar(f"Não há vagas cadastradas no segmento {resposta}."))
                else:
                    print(self.falar(resposta))

                # Salvar interação no histórico
                self.historico.append(f"Você: {user_input}")
                self.historico.append(f"{self.nome}: {resposta}")
                self.save_historico()

            else:
                print(self.falar("Não sei responder a isso. Você pode me ensinar?"))
                self.save_pergunta_nova(user_input)  # salva pergunta desconhecida
                new_answer = input("Digite a resposta ou 'pular' para pular: ")

                if new_answer.lower() != "pular":
                    encontrado = False
                    for i in self.knowledge_base["perguntas"]:
                        if i["pergunta"] == user_input:
                            i["respostas"].append(new_answer)
                            encontrado = True
                            break
                    if not encontrado:
                        self.knowledge_base["perguntas"].append({"pergunta": user_input, "respostas": [new_answer]})

                    self.save_database(self.arquivo_conhecimento, self.knowledge_base)
                    print(self.falar("Obrigado! Aprendi uma nova resposta!"))

                    # Salvar no histórico
                    self.historico.append(f"Você: {user_input}")
                    self.historico.append(f"{self.nome}: {new_answer}")
                    self.save_historico()

    # ---------------- MENU ----------------
    def iniciar(self):
        print(self.falar("Olá! Sou o TrampoJuá, seu assistente de empregos."))
        self.mostrar_historico()

        while True:
            print("\n--- Menu ---")
            print("1 - Buscar vaga")
            print("2 - Cadastrar vaga")
            print("3 - Listar vagas")
            print("4 - Mudar personalidade")
            print("5 - Conversa livre")
            print("6 - Sair")

            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                self.buscar_vaga()
            elif opcao == "2":
                self.cadastrar_vaga()
            elif opcao == "3":
                self.listar_vagas()
            elif opcao == "4":
                self.alterar_personalidade()
            elif opcao == "5":
                self.conversa()
            elif opcao == "6":
                print(self.falar("Até logo! Boa sorte na sua carreira!"))
                break
            else:
                print(self.falar("Opção inválida. Tente novamente."))


# Execução principal
if __name__ == "__main__":
    bot = ChatBotEmpregos(
        nome="TrampoJuá",
        arquivo_vagas="vagas.json",
        arquivo_conhecimento="knowledge_base.json",
        arquivo_historico="historico.txt",
        arquivo_perguntas="novas_perguntas.txt",  # novo arquivo
        personalidade="formal"
    )
    bot.iniciar()
