from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from src.utils.db import save_message, get_messages
from src.utils.exception import handle_error
import asyncio

class DeepSeekAssistant:
    def __init__(self, config):
        self.config = config
        self.model = OllamaLLM(
            model=config['model']['name'],
            temperature=config['model']['temperature'],
            num_ctx=config['model']['num_ctx']
        )
        self.memory = ConversationBufferMemory(return_messages=True)

        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_input}")
        ])

    async def process_input(self, conv_id, user_input):
        try:
            # Save user message
            await save_message(conv_id, "user", user_input)

            # Retrieve past conversation messages
            chat_history = self.memory.load_memory_variables({}).get("chat_history", [])

            # Format the prompt with conversation history
            formatted_prompt = self.prompt.format(chat_history=chat_history, user_input=user_input)

            # Generate response
            response = await asyncio.to_thread(self.model.invoke, formatted_prompt)

            # Save response to memory
            self.memory.save_context({"input": user_input}, {"output": response})
            
            # Save bot response
            await save_message(conv_id, "assistant", response)

            return response

        except Exception as e:
            handle_error(e)
            return "Sorry, I encountered an error processing your request."

    async def get_messages(self, conv_id):
        return await get_messages(conv_id)

    async def get_conversation_list(self):
        return []  # Implement conversation retrieval from DB

    async def clear_conversation(self, conv_id):
        self.memory.clear()  # Clear in-memory conversation

    def update_parameters(self, **kwargs):
        self.model.temperature = kwargs.get("temperature", self.config["model"]["temperature"])
