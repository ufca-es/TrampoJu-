import gradio as gr
from data_manager import DataManager
from conversation_manager import ConversationManager

# Substitua ChatbotApp e VagasManager por classes reais
# Se você tiver os arquivos, pode remover este trecho
class VagasManager:
    def __init__(self):
        pass
    def listar_vagas(self):
        return [{"titulo": "Vaga de Exemplo", "empresa": "Empresa Fictícia", "local": "Juazeiro do Norte", "segmento": "Tecnologia"}]
    def buscar_vaga(self, chave):
        return [{"titulo": "Vaga de Exemplo", "empresa": "Empresa Fictícia", "local": "Juazeiro do Norte", "segmento": "Tecnologia"}]

class ChatbotApp:
    def __init__(self):
        self.data_manager = DataManager()
        self.conv_manager = ConversationManager(
            data_manager=self.data_manager,
            conhecimento_file="knowledge_base.json",
            perguntas_file="perguntas_novas.txt"
        )
        self.vagas_manager = VagasManager()
        self.personalidade = "formal"

app = ChatbotApp()

# ---------- Funções de Ajuda ----------
def _bot_responder(mensagem, chat_history):
    chat_history = chat_history or []
    mensagem = (mensagem or "").strip()
    if not mensagem:
        return chat_history, ""
    
    resposta = app.conv_manager.get_resposta(mensagem)
    if resposta:
        bot_text = resposta
    else:
        bot_text = "Não sei essa. Pode me ensinar? (Digite a resposta aqui mesmo)"
        app.conv_manager.save_pergunta_e_resposta_nova(mensagem, "Ainda não sei a resposta.")
    
    # Adiciona a mensagem do usuário e a resposta do bot na ordem correta
    chat_history.append([mensagem, bot_text])
    
    return chat_history, ""

def teach_inline(mensagem, chat_history):
    chat_history = chat_history or []
    if not chat_history:
        return _bot_responder(mensagem, chat_history)
    
    last_user, last_bot = chat_history[-1]
    if "Pode me ensinar?" in last_bot:
        app.conv_manager.aprender_nova_resposta(last_user, mensagem)
        chat_history[-1] = (last_user, mensagem)
        chat_history.append(["BOT", "Aprendi! Obrigado!"])
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
        chat_history.append([pergunta, resposta])
        return chat_history
    return handler

def listar_vagas():
    vagas = app.vagas_manager.listar_vagas()
    if not vagas:
        return "Nenhuma vaga cadastrada."
    texto = ""
    for v in vagas:
        texto += f"- {v.get('titulo','')} | {v.get('empresa','')} | {v.get('local','')} | {v.get('segmento','')}<br>"
    return f"<div style='font-size:15px; line-height:1.8; color:#f0f0f0'>{texto}</div>"

def buscar_vagas(chave):
    if not chave.strip():
        return "Digite uma palavra-chave."
    resultados = app.vagas_manager.buscar_vaga(chave)
    if not resultados:
        return "Nenhuma vaga encontrada."
    texto = ""
    for v in resultados:
        texto += f"- {v.get('titulo','')} | {v.get('empresa','')} | {v.get('local','')} | {v.get('segmento','')}<br>"
    return f"<div style='font-size:15px; line-height:1.8; color:#f0f0f0'>{texto}</div>"

# Correção para a função set_personalidade no seu arquivo interface.py
def set_personalidade(p):
    app.personalidade = p
    return f"Personalidade atual: {p}"

# ---------- CSS e Interface do Gradio ----------
css = """
body {
    background:#000;
    color:#f0f0f0;
    font-family: Inter, sans-serif;
}
/* ... resto do seu CSS ... */
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