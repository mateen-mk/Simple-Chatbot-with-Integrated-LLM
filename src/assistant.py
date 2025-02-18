from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import asyncio
from src.utils.db import save_message, get_messages
from src.utils.exception import handle_error

class DeepSeekAssistant:
    def __init__(self, config):
        self.config = config
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(config['model']['name'], trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(config['model']['name'], trust_remote_code=True)

        # Move model to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        # Store chat history
        self.chat_history = []

    async def process_input(self, conv_id, user_input):
        try:
            # Save user message
            await save_message(conv_id, "user", user_input)

            # Format chat history as text
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.chat_history])

            # Construct input text for the model
            input_text = f"System: You are a helpful AI assistant.\n{history_text}\nUser: {user_input}\nAssistant:"

            # Tokenize input
            inputs = self.tokenizer(input_text, return_tensors="pt", truncation=True, max_length=1024).to(self.device)

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_new_tokens=200, temperature=self.config['model']['temperature'])

            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True).split("Assistant:")[-1].strip()

            # Save response to chat history
            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": response})

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
        self.chat_history = []  # Clear conversation history

    def update_parameters(self, **kwargs):
        # Update model parameters dynamically
        self.config["model"]["temperature"] = kwargs.get("temperature", self.config["model"]["temperature"])
