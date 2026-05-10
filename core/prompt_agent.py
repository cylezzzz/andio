import ollama

class PromptAgent:
    def generate_prompt(self, data):
        response = ollama.chat(
            model="llama3",
            messages=[
                {
                    "role": "user",
                    "content": str(data)
                }
            ]
        )

        return response["message"]["content"]
