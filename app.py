import gradio as gr
from data_manager import DataManager
from vagas_manager import VagasManager
from conversation_manager import ConversationManager
from history_manager import HistoryManager
import json
import random
from collections import deque, Counter
from datetime import datetime
from difflib import get_close_matches

# A classe ChatbotApp completa do seu arquivo main.py
class ChatbotApp:
    def __init__(self):
        self.data_manager = DataManager()
        # VagasManager e HistoryManager não foram fornecidos, mas a estrutura completa está aqui.
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
            
    def gerar_relatorio_estatisticas(self):
        pergunta_mais_frequente = "Nenhuma"
        perguntas_frequentes_texto = "Nenhuma pergunta comum na sessão."
        if self.perguntas_sessao:
            contador = Counter(self.perguntas_sessao)
            perguntas_filtradas = [p for p in self.perguntas_sessao if p.strip()]
            if perguntas_filtradas:
                contador = Counter(perguntas_filtradas)
                pergunta_mais_frequente, _ = contador.most_common(1)[0]
                
                top_perguntas = contador.most_common(5)
                if top_perguntas:
                    perguntas_frequentes_texto = "\n".join([f" - {p[0]} ({p[1]} vezes)" for p in top_perguntas])

        relatorio = [
            f"📊 Relatório de Estatísticas - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "-" * 50,
            f"Número total de interações: {self.interacoes}",
            f"Pergunta mais feita da sessão: {pergunta_mais_frequente}",
            "Uso das personalidades:",
            f" - Formal: {self.personalidades_usadas['formal']} vezes",
            f" - Orientador: {self.personalidades_usadas['orientador']} vezes",
            f" - Engraçado: {self.personalidades_usadas['engraçado']} vezes",
            "-" * 50,
            "\n💡 Sugestões de perguntas baseadas na sessão:",
            perguntas_frequentes_texto,
            "-" * 50,
        ]
        
        with open("estatisticas.txt", "w", encoding="utf-8") as f:
            for linha in relatorio:
                f.write(linha + "\n")

# Instancie a classe completa
app = ChatbotApp()

# ---------- Funções de Ajuda para a Interface (agora com formato consistente) ----------
def _bot_responder(mensagem, chat_history):
    chat_history = chat_history or []
    mensagem = (mensagem or "").strip()
    if not mensagem:
        return chat_history, ""
    
    resposta = app.conv_manager.get_resposta(mensagem)
    if resposta:
        bot_text = app.falar(resposta)
    else:
        bot_text = app.falar("Não sei essa. Pode me ensinar? (Digite a resposta aqui mesmo)")
        app.conv_manager.save_pergunta_e_resposta_nova(mensagem, "Ainda não sei a resposta.")
    
    # FORMATO CORRETO: lista de listas
    chat_history.append([mensagem, bot_text])
    return chat_history, ""

def teach_inline(mensagem, chat_history):
    chat_history = chat_history or []
    if not chat_history:
        return _bot_responder(mensagem, chat_history)
    
    last_user, last_bot = chat_history[-1]
    if "Pode me ensinar?" in last_bot:
        app.conv_manager.aprender_nova_resposta(last_user, mensagem)
        # FORMATO CORRETO: lista de listas
        chat_history[-1] = [last_user, mensagem]
        chat_history.append([None, app.falar("Aprendi! Obrigado!")])
        return chat_history, ""
    else:
        return _bot_responder(mensagem, chat_history)

def make_faq_handler(pergunta):
    def handler(chat_history):
        chat_history = chat_history or []
        resposta = app.conv_manager.get_resposta(pergunta)
        if not resposta:
            resposta = "Não sei responder ainda."
            app.conv_manager.save_pergunta_e_resposta_nova(pergunta, "Não sei a resposta.")
        # FORMATO CORRETO: lista de listas
        chat_history.append([pergunta, app.falar(resposta)])
        return chat_history
    return handler

def listar_vagas():
    vagas = app.vagas_manager.listar_vagas()
    if not vagas:
        return app.falar("Nenhuma vaga cadastrada.")
    texto = ""
    for v in vagas:
        texto += f"- {v.get('titulo','')} | {v.get('empresa','')} | {v.get('local','')} | {v.get('segmento','')}<br>"
    return f"<div style='font-size:15px; line-height:1.8; color:#f0f0f0'>{texto}</div>"

def buscar_vagas(chave):
    if not chave.strip():
        return app.falar("Digite uma palavra-chave.")
    resultados = app.vagas_manager.buscar_vaga(chave)
    if not resultados:
        return app.falar("Nenhuma vaga encontrada.")
    texto = ""
    for v in resultados:
        texto += f"- {v.get('titulo','')} | {v.get('empresa','')} | {v.get('local','')} | {v.get('segmento','')}<br>"
    return f"<div style='font-size:15px; line-height:1.8; color:#f0f0f0'>{texto}</div>"

def set_personalidade(p):
    app.personalidade = p
    return f"Personalidade atual: {p}"

def gerar_relatorio_gradio():
    app.gerar_relatorio_estatisticas()
    novos_aprendizados = app.conv_manager.load_perguntas_e_respostas_novas()
    mensagem = "Relatório de estatísticas gerado com sucesso! 🎉\n\n"
    if novos_aprendizados:
        mensagem += "Novos aprendizados desta sessão:\n"
        for item in novos_aprendizados:
            mensagem += f"- Pergunta: '{item['pergunta']}' -> Resposta: '{item['resposta']}'\n"
    else:
        mensagem += "Nenhum novo aprendizado nesta sessão."
    
    return mensagem

# ---------- CSS e Interface do Gradio ----------
css = """
body {
    background:#000;
    color:#f0f0f0;
    font-family: Inter, sans-serif;
}
.chat-column {
    display: flex;
    flex-direction: column;
    height: 85vh;
}
.chatbox {
    flex-grow: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px;
    background: #111;
    border-radius: 10px;
}
.chatbox .message {
    display: inline-block !important;
    max-width: 75% !important;
    min-width: 80px;
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    text-align: left !important;
    padding: 10px 14px;
    font-size: 15px;
    line-height: 1.4;
}
.chatbox .message.bot {
    background:#262d31 !important;
    color:#e9edef !important;
    border-radius:18px 18px 18px 6px !important;
    align-self: flex-start !important;
}
.chatbox .message.user {
    background:#056162 !important;
    color:#fff !important;
    border-radius:18px 18px 6px 18px !important;
    align-self: flex-end !important;
}
.message-box {
    display: flex;
    gap: 10px;
    margin-top: 10px;
}
.sidebar {
    background:#1c1c1c !important;
    border-radius:8px;
    padding:10px;
}
.gr-button {
    background:#222 !important;
    color:#f0f0f0 !important;
    margin-bottom:5px;
    border-radius:8px !important;
    border:1px solid #333;
}
.gr-button:hover {
    background:#444 !important;
}
.logo-container {
    display:flex;
    align-items:center;
    justify-content:center;
    gap:10px;
    margin-bottom:20px;
}
.logo-text {
    color:#f0f0f0;
    font-size:24px;
    font-weight:bold;
}
"""

with gr.Blocks(css=css, title="TrampoJuá - Full Dark") as demo:
    with gr.Tab("💬 Conversa Livre"):
        with gr.Row(elem_classes="logo-container"):
            gr.Markdown("""
            <div style="display:flex; align-items:center; justify-content:center; gap:10px;">
                🌳 <span class="logo-text">TrampoJuá</span>
            </div>
            """)
        with gr.Row():
            with gr.Column(scale=5, elem_classes="chat-column"):
                chat = gr.Chatbot([], elem_classes="chatbox", bubble_full_width=False)
                with gr.Row(elem_classes="message-box"):
                    msg = gr.Textbox(placeholder="Digite aqui...", lines=1)
                    enviar = gr.Button("Enviar")
            with gr.Column(scale=2, elem_classes="sidebar"):
                gr.Markdown("Perguntas Frequentes:")
                for p in ["Bom dia", "Boa tarde", "Tchau", "Currículo", "LinkedIn"]:
                    b = gr.Button(p)
                    b.click(fn=make_faq_handler(p), inputs=[chat], outputs=[chat])
                perso = gr.Dropdown(["formal","orientador","engraçado"], value=getattr(app,"personalidade","formal"), label="Bot Personalidade")
                perso_status = gr.Markdown(f"Personalidade atual: {getattr(app,'personalidade','formal')}")
                perso.change(fn=set_personalidade, inputs=[perso], outputs=[perso_status])
                
                # Botão para gerar relatório final
                relatorio_btn = gr.Button("📊 Gerar Relatório")
                relatorio_btn.click(fn=gerar_relatorio_gradio, inputs=None, outputs=perso_status)

        enviar.click(fn=teach_inline, inputs=[msg, chat], outputs=[chat, msg])
        msg.submit(fn=teach_inline, inputs=[msg, chat], outputs=[chat, msg])

    with gr.Tab("📋 Vagas"):
        with gr.Column():
            chave = gr.Textbox(label="🔎 Buscar palavra-chave")
            buscar_btn = gr.Button("Buscar")
            listar_btn = gr.Button("Listar todas")
            vagas_out = gr.HTML("<div style='color:#f0f0f0'>Resultados aparecerão aqui...</div>")
            buscar_btn.click(fn=buscar_vagas, inputs=[chave], outputs=[vagas_out])
            listar_btn.click(fn=listar_vagas, inputs=None, outputs=[vagas_out])

demo.launch(share=False, inbrowser=True)