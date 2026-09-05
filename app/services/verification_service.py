import json
import re

from app.services.llm_service import llm_service


class VerificationService:

    @staticmethod
    def _normalize(text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip().split()

    @staticmethod
    def _keyword_overlap(
        claim: str,
        evidence: str,
    ) -> float:
        claim_words = set(VerificationService._normalize(claim))
        evidence_words = set(VerificationService._normalize(evidence))

        if not claim_words:
            return 0.0

        # Ignore common grammatical words.
        stop_words = {
            "a",
            "an",
            "the",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "may",
            "might",
            "can",
            "could",
            "that",
            "this",
            "it",
            "of",
            "to",
            "in",
            "on",
            "for",
            "and",
        }

        meaningful_claim_words = claim_words - stop_words

        if not meaningful_claim_words:
            return 0.0

        overlap = meaningful_claim_words & evidence_words

        return len(overlap) / len(meaningful_claim_words)

    def verify_claim(
        self,
        claim: str,
        evidence: str,
    ) -> dict:

        overlap = self._keyword_overlap(
            claim,
            evidence,
        )

        # Strong lexical evidence.
        if overlap >= 0.8:
            return {
                "supported": True,
                "evidence": evidence,
            }

        # Otherwise ask Gemini for semantic verification.
        prompt = f"""
You are an evidence verification system.

Determine whether the evidence supports the claim.

Judge ONLY the supplied evidence.

A claim is SUPPORTED if the evidence clearly states
the same fact, even if the wording is different.

A claim is UNSUPPORTED if the evidence does not contain
enough information to establish the claim.

Return ONLY valid JSON.

Format:

{{
    "supported": true,
    "evidence": "relevant evidence"
}}

or:

{{
    "supported": false,
    "evidence": null
}}

CLAIM:
{claim}

EVIDENCE:
{evidence}
""".strip()

        response = llm_service.generate(prompt)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            return {
                "supported": False,
                "evidence": None,
            }

        return {
            "supported": bool(result.get("supported", False)),
            "evidence": result.get("evidence"),
        }


verification_service = VerificationService()