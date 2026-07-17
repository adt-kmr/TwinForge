class FunctionGemma:
    def __init__(self, model_path: str = "models/function_gemma"):
        self.model_path = model_path

    def generate(self, prompt: str) -> str:
        return f"function_gemma_output({prompt})"
