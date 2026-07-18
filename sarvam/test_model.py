import litert_lm

model_path = "soniq-assistant-v2.litertlm"

try:
    with litert_lm.Engine(model_path, backend=litert_lm.Backend.CPU()) as engine:
        print("Model loaded successfully!")
        with engine.create_conversation() as conversation:
            response = conversation.send_message("Hello, what can you do?")
            print("Response:", response["content"][0]["text"])
except Exception as e:
    print(f"Error: {e}")