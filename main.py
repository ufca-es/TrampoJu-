# main.py
import json
import random
from collections import deque, Counter
from datetime import datetime
from difflib import get_close_matches

from data_manager import DataManager
from vagas_manager import VagasManager
from conversation_manager import ConversationManager
from history_manager import HistoryManager

class ChatbotApp:
    def __init__(self):
        self.data_manager = DataManager()
        self.vagas_manager = VagasManager(self.data_manager, "vagas.json")
        self.conv_manager = ConversationManager(self.data_manager, "knowledge_base.json", "novas_perguntas.txt")
        self.history_manager = HistoryManager("historico.txt")
        
        self.nome = "TrampoJuá"
        self.personalidade = "formal"
        self.interacoes = 0
        self.perguntas_sessao = []
        self.personalidades_usadas = Counter({"formal": 0, "orientador": 0, "engraçado": 0})
        self.personalidades_usadas[self.personalidade] += 1
        self.sugestoes_mostradas = False

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
        
        self.personalidades_usadas[self.personalidade] += 1
        print(self.falar(f"Personalidade alterada para '{self.personalidade}'."))

    def gerar_relatorio_estatisticas(self):
        pergunta_mais_frequente = "Nenhuma"
        if self.perguntas_sessao:
            contador = Counter(self.perguntas_sessao)
            perguntas_filtradas = [p for p in self.perguntas_sessao if p.strip()]
            if perguntas_filtradas:
                contador = Counter(perguntas_filtradas)
                pergunta_mais_frequente, _ = contador.most_common(1)[0]
        
        relatorio = [
            f"📊 Relatório de Estatísticas - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "-" * 50,
            f"Número total de interações: {self.interacoes}",
            f"Pergunta mais feita da sessão: {pergunta_mais_frequente}",
            "Uso das personalidades:",
            f"  - Formal: {self.personalidades_usadas['formal']} vezes",
            f"  - Orientador: {self.personalidades_usadas['orientador']} vezes",
            f"  - Engraçado: {self.personalidades_usadas['engraçado']} vezes",
            "-" * 50,
        ]
        
        with open("estatisticas.txt", "w", encoding="utf-8") as f:
            for linha in relatorio:
                f.write(linha + "\n")

        print("\n📁 Relatório de estatísticas gerado com sucesso!")
        print("\n".join(relatorio))

    def mostrar_sugestoes(self):
        if not self.sugestoes_mostradas:
            perguntas_base = [i["pergunta"] for i in self.conv_manager.knowledge_base["perguntas"]]
            perguntas_novas = self.conv_manager.load_perguntas_novas()
            
            todas = perguntas_base + perguntas_novas
            todas = [p for p in todas if p.strip()]

            if todas:
                contador = Counter(todas)
                mais_frequentes = [p for p, _ in contador.most_common(3)]
                print("\n💡 Sugestões de perguntas que você pode fazer:")
                for s in mais_frequentes:
                    print(f"- {s}")
                print("-" * 40)
            self.sugestoes_mostradas = True

    def conversa(self):
        print(self.falar("Você entrou no modo conversa. Digite 'sair' para voltar ao menu."))
        
        while True:
            if not self.sugestoes_mostradas:
                self.mostrar_sugestoes()

            user_input = input("Você: ")
            
            if user_input.lower() == "sair":
                print(self.falar("Saindo do modo conversa..."))
                break

            self.interacoes += 1
            self.perguntas_sessao.append(user_input)

            resposta = self.conv_manager.get_resposta(user_input)
            
            if resposta:
                print(self.falar(resposta))
                self.history_manager.historico.append(f"Você: {user_input}")
                self.history_manager.historico.append(f"{self.nome}: {resposta}")
                self.history_manager.save_historico()
            else:
                print(self.falar("Não sei responder a isso. Você pode me ensinar?"))
                self.conv_manager.save_pergunta_nova(user_input)
                new_answer = input("Digite a resposta ou 'pular' para pular: ")

                if new_answer.lower() != "pular":
                    self.conv_manager.aprender_nova_resposta(user_input, new_answer)
                    print(self.falar("Obrigado! Aprendi uma nova resposta!"))
                    self.history_manager.historico.append(f"Você: {user_input}")
                    self.history_manager.historico.append(f"{self.nome}: {new_answer}")
                    self.history_manager.save_historico()

    def iniciar(self):
        # Primeiro, exibe o histórico
        self.history_manager.mostrar_historico()
        # Em seguida, limpa o histórico para a nova sessão
        self.history_manager.limpar_historico()
        
        print(self.falar("Olá! Sou o TrampoJuá, seu assistente de empregos."))

        while True:
            print("\n--- Menu ---")
            print("1 - Buscar vaga")
            print("2 - Cadastrar vaga")
            print("3 - Listar vagas")
            print("4 - Mudar personalidade")
            print("5 - Conversa livre")
            print("6 - Relatório de estatísticas")
            print("7 - Sair")
            
            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                palavra_chave = input("\nDigite uma palavra-chave: ")
                resultados = self.vagas_manager.buscar_vaga(palavra_chave)
                if resultados:
                    print(self.falar(f"Encontrei {len(resultados)} vaga(s):"))
                    for vaga in resultados:
                        print(f"- {vaga.get('titulo','')} ({vaga.get('segmento','')}) - {vaga.get('descricao','')}")
                else:
                    print(self.falar("Não encontrei vagas com essa palavra-chave."))
            
            elif opcao == "2":
                titulo = input("Título da vaga: ")
                empresa = input("Empresa: ")
                local = input("Local: ")
                requisitos = input("Requisitos: ")
                segmento = input("Segmento (ADM, TI, Limpeza, Vendas): ")
                descricao = input("Descrição da vaga: ")
                self.vagas_manager.cadastrar_vaga(titulo, empresa, local, requisitos, segmento, descricao)
                print(self.falar("Vaga cadastrada com sucesso!"))
            
            elif opcao == "3":
                vagas = self.vagas_manager.listar_vagas()
                if not vagas:
                    print(self.falar("Não há vagas cadastradas no momento."))
                else:
                    print(self.falar(f"Temos {len(vagas)} vaga(s) cadastrada(s):"))
                    for vaga in vagas:
                        print(f"- {vaga.get('titulo','')} ({vaga.get('segmento','')}) - {vaga.get('descricao','')}")
            
            elif opcao == "4":
                self.alterar_personalidade()
            
            elif opcao == "5":
                self.conversa()
            
            elif opcao == "6":
                self.gerar_relatorio_estatisticas()
            
            elif opcao == "7":
                self.gerar_relatorio_estatisticas()
                print(self.falar("Até logo! Boa sorte na sua carreira!"))
                break
            
            else:
                print(self.falar("Opção inválida. Tente novamente."))

if __name__ == "__main__":
    app = ChatbotApp()
    app.iniciar()