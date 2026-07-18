import litert_lm
import json
import re

class FunctionGemmaModel:
    def __init__(self, model_path="soniq-assistant-v2.litertlm"):
        """Initialize the model"""
        self.model_path = model_path
        self.engine = None
        self.conversation = None
        
    def load(self):
        """Load the model engine"""
        if self.engine is None:
            self.engine = litert_lm.Engine(
                self.model_path,
                backend=litert_lm.Backend.CPU()
            )
        return self
    
    def start_conversation(self):
        """Start a new conversation"""
        if self.engine is None:
            self.load()
        self.conversation = self.engine.create_conversation()
        return self.conversation
    
    def send_message(self, message):
        """Send a message and get response"""
        if self.conversation is None:
            self.start_conversation()
        response = self.conversation.send_message(message)
        return response["content"][0]["text"]
    
    def parse_function_call(self, text):
        """Extract function call from model response"""
        # Pattern: <start_function_call>call:function_name{arg1:value1,arg2:value2}<end_function_call>
        pattern = r'<start_function_call>call:(\w+)\{([^}]*)\}<end_function_call>'
        match = re.search(pattern, text)
        
        if match:
            function_name = match.group(1)
            args_str = match.group(2)
            
            # Parse arguments
            args = {}
            if args_str:
                for pair in args_str.split(','):
                    if ':' in pair:
                        key, value = pair.split(':', 1)
                        args[key.strip()] = value.strip()
            
            return function_name, args
        return None, None
    
    def close(self):
        """Clean up resources"""
        if self.conversation:
            # Handle cleanup
            pass
        if self.engine:
            # Handle cleanup
            pass

# Example usage
if __name__ == "__main__":
    model = FunctionGemmaModel()
    model.load()
    model.start_conversation()
    
    # Test with a simple query
    response = model.send_message("What can you help me with?")
    print("Response:", response)
    
    # Test with a function call
    response = model.send_message("Turn on the flashlight")
    print("Raw response:", response)
    
    # Parse function call
    func_name, args = model.parse_function_call(response)
    if func_name:
        print(f"Function call detected: {func_name} with args: {args}")
    else:
        print("No function call detected")