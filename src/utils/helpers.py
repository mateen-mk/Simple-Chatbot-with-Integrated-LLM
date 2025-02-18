import yaml
import time
import hashlib

def load_config():
    with open('assets/config.yaml') as f:
        return yaml.safe_load(f)

def get_conversation_id():
    return hashlib.sha256(str(time.time()).encode()).hexdigest()[:10]

def sanitize_input(text):
    return text.strip().replace('<', '&lt;').replace('>', '&gt;')