from google import genai

from app.core.config import settings


class LLMService:
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )

    def generate(
        self,
        prompt: str,
    ) -> str:
        interaction = self.client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
        )

        return interaction.output_text


llm_service = LLMService()