"""Global context manager for shared objects"""
import server.config as config

context = {}

def get_context(key: str):
    """Get object from context"""
    try:
        return context[key]
    except KeyError:
        if config.VERBOSE:
            print(f"⚠️ Context key not found: {key}")
        return None

def set_context(key: str, value):
    """Set object in context"""
    if key is None or value is None:
        if config.VERBOSE:
            print(f"⚠️ Invalid context key: {key}")
        return
    
    if key in context:
        if config.VERBOSE:
            print(f"⚠️ Context key already exists: {key}")
        return
    
    if config.VERBOSE:
        print(f"📦 Context key added: {key}")
    
    context[key] = value