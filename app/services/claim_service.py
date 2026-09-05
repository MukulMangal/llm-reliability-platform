import json

from app.services.llm_service import llm_service


class ClaimService:
    def extract_claims(self, answer: str) -> list[str]:
        prompt = f"""
Extract the factual claims from the answer below.

A claim is a single factual statement that can be checked against evidence.

Rules:
- Extract only factual claims.
- Do not extract opinions, questions, or instructions.
- Keep each claim concise.
- Return ONLY a valid JSON array of strings.
- Do not include markdown.
- Do not add explanations.

Answer:
{answer}
""".strip()

        response = llm_service.generate(prompt)

        try:
            claims = json.loads(response)
        except json.JSONDecodeError:
            return []

        if not isinstance(claims, list):
            return []

        return [
            claim.strip()
            for claim in claims
            if isinstance(claim, str) and claim.strip()
        ]


claim_service = ClaimService()