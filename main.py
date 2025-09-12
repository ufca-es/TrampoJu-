import json
import random
from difflib import get_close_matches
from collections import deque
import os

class ChatBotEmpregos:
    def __init__(self, nome, arquivo_vagas, arquivo_conhecimento, arquivo_historico, arquivo_estatisticas, personalidade="formal"):
        self.nome = nome
        self.arquivo_vagas = arquivo_vagas
        self.arquivo_conhecimento = arquivo_conhecimento
        self.arquivo_historico = arquivo_historico
        self.arquivo_estatisticas = arquivo_estatisticas
        self.personalidade = personalidade

        self.criar_arquivos_iniciais()
        self.vagas = self.load_database(self.arquivo_vagas, "vagas")
        self.knowledge_base = self.load_database(self.arquivo_conhecimento, "perguntas")
        self.historico = self.load_historico()
        self.estatisticas = self.load_database(self.arquivo_estatisticas, "estatisticas")

    # ---------------- CRIAÇÃO DE ARQUIVOS ----------------
    def criar_arquivos_iniciais(self):
        if not os.path.exists(self.arquivo_vagas):
            with open(self.arquivo_vagas, "w", encoding="utf-8") as f:
                json.dump({"vagas": []}, f, indent=2, ensure_ascii=False)
        if not os.path.exists(self.arquivo_conhecimento):
            with open(self.arquivo_conhecimento, "w", encoding="utf-8") as f:
                json.dump({"perguntas": []}, f, indent=2, ensure_ascii=False)
        if not os.path.exists(self.arquivo_estatisticas):
            with open(self.arquivo_estatisticas, "w", encoding="utf-8") as f:
                json.dump({"estatisticas": {"total_interacoes":0,"perguntas":{},"personalidades_usadas":{}}}, f, indent=2, ensure_ascii=False)

    # ---------------- LOAD / SAVE ----------------
    def load_database(self, arquivo, chave):
        try:
            if not os.path.exists(arquivo):
                data = {chave: []} if chave != "estatisticas" else {chave: {"total_interacoes":0,"perguntas":{},"personalidades_usadas":{}}}
                with open(arquivo, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return data
            with open(arquivo, "r", encoding="utf-8") as f:
                data = json.load(f)
                if chave not in data:
                    data[chave] = [] if chave != "estatisticas" else {"total_interacoes":0,"perguntas":{},"personalidades_usadas":{}}
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            data = {chave: []} if chave != "estatisticas" else {chave: {"total_interacoes":0,"perguntas":{},"personalidades_usadas":{}}}
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return data

    def save_database(self, arquivo, data):
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ---------------- HISTÓRICO ----------------
    def load_historico(self):
        historico = deque(maxlen=10)
        if os.path.exists(self.arquivo_historico):
            with open(self.arquivo_historico, "r", encoding="utf-8") as f:
                for linha in f:
                    historico.append(linha.strip())
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
                    print(self.historico[i])
                    print(self.historico[i+1])
                except IndexError:
                    pass
            print("-"*40)

    # ---------------- ESTATÍSTICAS ----------------
    def registrar_interacao(self, pergunta=None):
        stats = self.estatisticas["estatisticas"]
        stats["total_interacoes"] += 1
        if pergunta:
            stats["perguntas"][pergunta] = stats["perguntas"].get(pergunta,0)+1
        self.save_database(self.arquivo_estatisticas, self.estatisticas)

    def registrar_personalidade(self):
        stats = self.estatisticas["estatisticas"]
        stats["personalidades_usadas"][self.personalidade] = stats["personalidades_usadas"].get(self.personalidade,0)+1
        self.save_database(self.arquivo_estatisticas, self.estatisticas)

    def mostrar_estatisticas(self):
        stats = self.estatisticas["estatisticas"]
        print("\n📊 Estatísticas:")
        print(f"- Total de interações: {stats['total_interacoes']}")
        if stats["perguntas"]:
            mais_feita = max(stats["perguntas"], key=stats["perguntas"].get)
            print(f"- Pergunta mais feita: '{mais_feita}' ({stats['perguntas'][mais_feita]} vezes)")
        else:
            print("- Nenhuma pergunta registrada ainda.")
        if stats["personalidades_usadas"]:
            print("- Personalidades usadas:")
            for p,qtd in stats["personalidades_usadas"].items():
                print(f"   {p}: {qtd} vez(es)")
        else:
            print("- Nenhuma personalidade usada ainda.")

    # ---------------- PERSONALIDADE ----------------
    def falar(self, mensagem):
        if self.personalidade=="formal":
            return f"{self.nome}: Prezado usuário, {mensagem}"
        elif self.personalidade=="orientador":
            return f"{self.nome}: 📘 Veja bem, {mensagem}. Continue se preparando para entrevistas!"
        elif self.personalidade=="engraçado":
            return f"{self.nome}: 😂 {mensagem} (e se não conseguir emprego, sempre tem vaga de degustador de café!)"
        else:
            return f"{self.nome}: {mensagem}"

    def alterar_personalidade(self):
        print("\nEscolha uma personalidade:")
        print("1 - Formal")
        print("2 - Orientador")
        print("3 - Engraçado")
        opc = input("Opção: ")
        if opc=="1": self.personalidade="formal"
        elif opc=="2": self.personalidade="orientador"
        elif opc=="3": self.personalidade="engraçado"
        else: print(self.falar("Opção inválida, mantendo personalidade."))
        print(self.falar(f"Personalidade alterada para {self.personalidade}"))
        self.registrar_personalidade()

    # ---------------- VAGAS ----------------
    def cadastrar_vaga(self):
        print("\n--- Cadastro de Vaga ---")
        titulo = input("Título da vaga: ")
        empresa = input("Empresa: ")
        local = input("Local: ")
        requisitos = input("Requisitos: ")
        segmento = input("Segmento (ADM, TI, Limpeza, Vendas): ")
        descricao = input("Descrição: ")
        self.vagas["vagas"].append({
            "titulo":titulo,"empresa":empresa,"local":local,"requisitos":requisitos,
            "segmento":segmento,"descricao":descricao
        })
        self.save_database(self.arquivo_vagas, self.vagas)
        self.registrar_interacao("cadastrar_vaga")
        print(self.falar("Vaga cadastrada com sucesso!"))

    def listar_vagas(self):
        if not self.vagas["vagas"]:
            print(self.falar("Não há vagas cadastradas."))
            return
        print(self.falar(f"Temos {len(self.vagas['vagas'])} vaga(s):"))
        for v in self.vagas["vagas"]:
            print(f"- {v.get('titulo','')} ({v.get('segmento','')}) - {v.get('descricao','')}")
        self.registrar_interacao("listar_vagas")

    def buscar_vaga(self):
        palavra = input("\nDigite palavra-chave ou segmento: ")
        res = [v for v in self.vagas["vagas"] if palavra.lower() in ' '.join([str(v.get(k,'')) for k in v]).lower()]
        if res:
            print(self.falar(f"Encontrei {len(res)} vaga(s):"))
            for v in res:
                print(f"- {v.get('titulo','')} ({v.get('segmento','')}) - {v.get('descricao','')}")
        else:
            print(self.falar("Nenhuma vaga encontrada."))
        self.registrar_interacao("buscar_vaga")

    # ---------------- CONVERSA ----------------
    def conversa(self):
        print(self.falar("Modo conversa. Digite 'sair' para voltar ao menu."))
        while True:
            user_input = input("Você: ")
            if user_input.lower() == "sair":
                print(self.falar("Saindo do modo conversa..."))
                break

            perguntas = [p["pergunta"] for p in self.knowledge_base["perguntas"]]
            best = get_close_matches(user_input, perguntas, n=1, cutoff=0.6)

            if best:
                respostas = next(p["respostas"] for p in self.knowledge_base["perguntas"] if p["pergunta"] == best[0])
                ultima_resposta = self.historico[-1].replace(f"{self.nome}: ", "") if self.historico else ""
                possiveis_respostas = [r for r in respostas if r != ultima_resposta]
                if not possiveis_respostas:
                    possiveis_respostas = respostas
                r = random.choice(possiveis_respostas)

                if r == "listagem":
                    self.listar_vagas()
                elif r in ["ADM", "TI", "Limpeza", "Vendas"]:
                    seg = [v for v in self.vagas["vagas"] if v.get("segmento", "") == r]
                    if seg:
                        print(self.falar(f"Vagas do segmento {r}:"))
                        for v in seg:
                            print(f"- {v.get('titulo','')} - {v.get('descricao','')}")
                    else:
                        print(self.falar(f"Não há vagas em {r}"))
                else:
                    print(self.falar(r))

                self.historico.append(f"Você: {user_input}")
                self.historico.append(f"{self.nome}: {r}")
                self.save_historico()
            else:
                print(self.falar("Não sei responder. Pode me ensinar?"))
                resp = input("Resposta ou 'pular': ")
                if resp.lower() != "pular":
                    self.knowledge_base["perguntas"].append({"pergunta": user_input, "respostas": [resp]})
                    self.save_database(self.arquivo_conhecimento, self.knowledge_base)
                    print(self.falar("Aprendi uma nova resposta!"))
                    self.historico.append(f"Você: {user_input}")
                    self.historico.append(f"{self.nome}: {resp}")
                    self.save_historico()

            self.registrar_interacao(user_input)

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
            print("7 - Ver estatísticas")
            opc = input("Escolha: ")
            if opc=="1": self.buscar_vaga()
            elif opc=="2": self.cadastrar_vaga()
            elif opc=="3": self.listar_vagas()
            elif opc=="4": self.alterar_personalidade()
            elif opc=="5": self.conversa()
            elif opc=="6": break
            elif opc=="7": self.mostrar_estatisticas()
            else: print(self.falar("Opção inválida."))

if __name__=="__main__":
    bot = ChatBotEmpregos(
        nome="TrampoJuá",
        arquivo_vagas="vagas.json",
        arquivo_conhecimento="knowledge_base.json",
        arquivo_historico="historico.txt",
        arquivo_estatisticas="estatisticas.json",
        personalidade="formal"
    )
    bot.iniciar()
