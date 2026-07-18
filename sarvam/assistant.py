from ai_model import FunctionGemmaModel
import json

class Assistant:
    def __init__(self):
        self.model = FunctionGemmaModel()
        self.model.load()
        self.model.start_conversation()
        
        # Define available functions
        self.functions = {
            "enableFlashlight": self.enable_flashlight,
            "createContact": self.create_contact,
            "sendEmail": self.send_email,
            "openMaps": self.open_maps,
            "setAlarm": self.set_alarm,
        }
    
    def enable_flashlight(self, args):
        """Enable flashlight function"""
        # In your actual project, you'd control hardware here
        return "Flashlight enabled"
    
    def create_contact(self, args):
        """Create a contact"""
        name = args.get('name', 'Unknown')
        phone = args.get('phone', '')
        return f"Created contact: {name} with phone: {phone}"
    
    def send_email(self, args):
        """Send an email"""
        to = args.get('to', '')
        subject = args.get('subject', '')
        body = args.get('body', '')
        return f"Email sent to {to}: {subject}"
    
    def open_maps(self, args):
        """Open maps"""
        location = args.get('location', 'home')
        return f"Opening maps for: {location}"
    
    def set_alarm(self, args):
        """Set an alarm"""
        time = args.get('time', '')
        return f"Alarm set for: {time}"
    
    def process(self, user_input):
        """Process user input and execute functions if needed"""
        # Get model response
        response = self.model.send_message(user_input)
        
        # Try to parse function call
        func_name, args = self.model.parse_function_call(response)
        
        if func_name and func_name in self.functions:
            # Execute the function
            result = self.functions[func_name](args)
            
            # Return the result with the model's response
            return {
                "model_response": response,
                "function_called": func_name,
                "function_result": result
            }
        
        return {
            "model_response": response,
            "function_called": None,
            "function_result": None
        }
    
    def chat(self):
        """Interactive chat loop"""
        print("🤖 TwinForge Assistant (type 'quit' to exit)")
        print("-" * 50)
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            result = self.process(user_input)
            print(f"Assistant: {result['model_response']}")
            
            if result['function_called']:
                print(f"🔧 Executed: {result['function_called']}")
                print(f"📋 Result: {result['function_result']}")

if __name__ == "__main__":
    assistant = Assistant()
    assistant.chat()