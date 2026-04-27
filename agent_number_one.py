# from agno.models.groq import Groq # Importar modelo Gratuito da Groq
# from agno.models.message import Message
# from dotenv import load_dotenv # Carregar variáveis de ambiente do arquivo .env

# load_dotenv() 

# model = Groq(id="llama-3.3-70b-versatile") 

# # Mensagem do usuário 
# user_message = Message(
#                         role="user", 
#                        content="Atue como um Head em FP&A e me responda de maneira simples e completa: O que considerar em uma organização de centro de Custo?"
#                        ) 

# # Mensagem assistente 
# assistant_message = Message(role="assistant", content="") 

# # Invocar 
# response = model.invoke( 
# 	messages=[user_message], 
# 	assistant_message=assistant_message ) 

# print(response.content)

# from agno.agent import Agent # Genrencia o “pensar → agir → observar”. Combina o LLM com ferramentas Tools
# from agno.models.groq import Groq # Essa classe encapsula a API da Groq (plataforma de inferência ultrarrápida)
# from dotenv import load_dotenv # Carrega variáveis de ambiente de um arquivo
# from agno.tools.tavily import TavilyTools # permite ao agente buscar informações na web via API da Tavily



# response = client.search(
#     query="O que é FP&A e M&A",
#     include_answer="basic",
#     search_depth="advanced"
# )
# print(response)

#Research model

# English Professor
from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv
import streamlit as st

st.set_page_config(
                    layout="wide",
                   page_icon="🗣️",
                   page_title="Tutor English"
                   )

st.title("The Tutor English")
st.caption("Aprenda inglês conversando com um tutor paciente e encorajador")

load_dotenv()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "theme_set" not in st.session_state:
    st.session_state.theme_set = False
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False


def create_agent(tema:str):

    instrucoes = f"""
            Você é um tutor de idiomas paciente e encorajador. O tema da conversa é: {tema}.
        
            #### FORMA DE INTERAÇÃO
            NO FORMATO DE DIALOGO, OU SEJA, VOCÊ INCIA A CONVERSA COM PERGUNTAS, NO MÁXIMA 10 PERGUNTAS, O USUÁRIO RESPONDE E CASO ESTEJA CORRETO VOCÊ CONTINUA A INTERAÇÃO, 
            SE A RESPOSTA FOR INCORRETA VOCÊ CORRIGI. 
            ####

            Regras obrigatórias:
            1. Sempre responda em inglês.
            2. Para cada mensagem do usuário, você DEVE fornecer uma correção detalhada.
            3. Mantenha a resposta natural e amigável, como um professor particular.
        
            Formato de saída será como dialogos simples, já definido pelo modelo TutorResponse.
                """
    return Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        instructions=instrucoes,
        debug_mode= True)

if not st.session_state.theme_set:
    st.markdown("### 👋 Welcome to your English Tutor!")
    st.markdown("I'll help you practice real-life conversations.")
    
    tema = st.text_input(
        "What topic would you like to practice?",
        placeholder="e.g., expressions used in a restaurant, ordering coffee, job interview..."
    )
    
    if st.button("Start lesson", type="primary"):
        if tema.strip():
            # Cria o agente com o tema informado
            st.session_state.agent = create_agent(tema)
            st.session_state.theme_set = True
            st.rerun()
        else:
            st.warning("Please enter a topic.")

else:
    # Exibe o histórico de mensagens
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


                # Se a conversa ainda não começou, faz o tutor dar a primeira pergunta automaticamente
    if not st.session_state.conversation_started:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # O tutor se apresenta e já inicia com a primeira pergunta sobre o tema
                response = st.session_state.agent.run(
                    "Introduce yourself briefly as a tutor, then ask the first question related to the chosen topic."
                )
                first_msg = response.content
                st.markdown(first_msg)
        # Adiciona a mensagem inicial ao histórico
        st.session_state.messages.append({"role": "assistant", "content": first_msg})
        st.session_state.conversation_started = True
        st.rerun()
    
    # Input do usuário (aparece depois que a primeira mensagem já foi mostrada)
    if prompt := st.chat_input("Type your answer in English..."):
        # Adiciona mensagem do usuário ao histórico e exibe
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Gera resposta do tutor
        with st.chat_message("assistant"):
            with st.spinner("Tutor is thinking..."):
                response = st.session_state.agent.run(prompt)
                reply = response.content
                st.markdown(reply)
        
        # Adiciona resposta ao histórico
        st.session_state.messages.append({"role": "assistant", "content": reply})
