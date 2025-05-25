from mistralai import Mistral
from dotenv import load_dotenv
import os
import json

load_dotenv()

class ChatBot:
    def __init__(self, api_key):
        self.client = Mistral(api_key=api_key)
        self.model = os.getenv("MISTRALAI_MODEL")
        self.max_tokens = 250
        self.temperature = 0.5
        self.top_p = 0.9

        self.messages = []

    def carregar_termos_condicoes(self, caminho_json="database/termos_loja.json"):
        try:
            with open(caminho_json, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            print(f"✅ Termos carregados de {caminho_json}!")
    
        except FileNotFoundError:
            print(f"❌ Arquivo {caminho_json} não encontrado. Usando termos padrão.")
            self._carregar_termos_padrao()
    
    def buscar_conhecimento(self, pergunta):
        informacoes_relevantes = []

        for topico, dados in self.knowledge_base.items():
            if topico.lower() in pergunta.lower():
                if "texto_completo" in dados:
                    informacoes_relevantes.append(
                        f"🔹 {topico.upper()}: {dados['texto_completo']}"
                    )

        return informacoes_relevantes

    def add_system_message(self, content):
        self.messages.append({"role": "system", "content": content})
    
    def chat(self, user_message):

        info_relevante = self.buscar_conhecimento(user_message)

        if info_relevante:
            contexto = "\n\n**INFORMAÇÕES DA LOJA PARA CONSULTA:**\n" + "\n\n".join(info_relevante)
            mensagem_completa = f"{user_message}{contexto}"
        else:
            mensagem_completa = user_message
            
        self.messages.append({"role": "user", "content": mensagem_completa})

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=self.messages,
                max_tokens = self.max_tokens,
                temperature = self.temperature,
                top_p = self.top_p,
            )
            
            bot_response = response.choices[0].message.content
            
            self.messages.append({"role": "assistant", "content": bot_response})
            
            return bot_response
            
        except Exception as e:
            return f"Erro: {e}"
    
    def show_history(self):
        for i, msg in enumerate(self.messages):
            role = msg["role"]
            content = msg["content"]
            print(f"{i+1}. [{role.upper()}]: {content}")
            print("-" * 50)
    
    def clear_history(self):
        self.messages = []
        print("Histórico limpo!")

    def mostrar_base_conhecimento(self):
        print("\n📚 BASE DE CONHECIMENTO DA LOJA:")
        print("=" * 50)
        for categoria, info in self.knowledge_base.items():
            print(f"\n🔹 {categoria.upper()}:")
            if isinstance(info, dict) and 'texto_completo' in info:
                print(f"   {info['texto_completo']}")
            else:
                print(f"   {info}")

if __name__ == "__main__":
    bot = ChatBot(os.getenv("MISTRALAI_API_KEY"))

    bot.carregar_termos_condicoes()

    bot.add_system_message("""
    Você é um especialista em videojogos chamado John Parker que trabalha na loja "HyrumGames!" . Suas características são:
                           
    - Linguagem formal para atendimento ao cliente
    - Tom: Profissional e educado, como um atendente de suporte
    - **Conhecimento**: Responde sobre jogos E sobre políticas da loja
    - Estilo: Usa emojis e formatação de texto (negrito, itálico) para destacar partes importantes
                           
    **IMPORTANTE**: Quando receber informações da loja no contexto, use-as para responder com precisão sobre políticas, termos e condições. Sempre cite as informações específicas (prazos, valores, condições).
                           
    - Exemplos de respostas:
    - Sobre políticas: "Sim, você pode solicitar reembolso em até **5 dias úteis** após a compra! 📋"
    - "Skyrim? Melhor RPG da história! Mas o Fallout New Vegas tem a melhor escrita e personagens! 🎮"
    - "Te recomendo comprar o jogo na nossa loja, temos ótimos preços e promoções! 💰"
                           
    Se perguntarem sobre assuntos fora de jogos ou políticas da loja, se desculpe educadamente.

    """)
    
    print("🤖 John Parker - Especialista em Games & Atendimento ao Cliente")
    print("Digite 'sair' para terminar | 'historico' para ver mensagens | 'limpar' para limpar | 'base' para ver políticas")
    print("=" * 80)
    
    while True:
        user_input = input("\n👤 Você: ").strip()
        
        if user_input.lower() in ['sair', 'exit', 'quit']:
            print("👋 Obrigado por usar nossos serviços! Tenha um ótimo dia!")
            break
        elif user_input.lower() == 'historico':
            print("\n📜 Histórico da conversa:")
            bot.show_history()
            continue
        elif user_input.lower() == 'limpar':
            bot.clear_history()
            continue
        elif user_input.lower() == 'base':
            bot.mostrar_base_conhecimento()
            continue
        elif not user_input:
            continue
        
        response = bot.chat(user_input)
        print(f"\n🤖 Bot: {response}")