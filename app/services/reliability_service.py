from app.services.claim_service import claim_service
from app.services.verification_service import verification_service


class ReliabilityService:

    def calculate_score(
        self,
        verified_claims: list[dict],
        retrieval_score: float = 0.0,
    ) -> dict:

        if not verified_claims:
            return {
                "reliability_score": 0.0,
                "claim_support_score": 0.0,
                "retrieval_score": round(
                    retrieval_score,
                    2,
                ),
                "reliability_status": "unsupported",
                "confidence_level": "low",
                "claims": [],
                "supported_claims": 0,
                "total_claims": 0,
            }

        total_claims = len(verified_claims)

        supported_claims = sum(
            1
            for claim in verified_claims
            if claim["supported"]
        )

        claim_support_score = (
            supported_claims / total_claims
        )

        retrieval_score = max(
            0.0,
            min(1.0, retrieval_score),
        )

        reliability_score = (
            claim_support_score * 0.7
            + retrieval_score * 0.3
        )

        if claim_support_score >= 0.9:
            reliability_status = "highly_supported"
        elif claim_support_score > 0:
            reliability_status = "partially_supported"
        else:
            reliability_status = "unsupported"

        if reliability_score >= 0.8:
            confidence_level = "high"
        elif reliability_score >= 0.5:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        return {
            "reliability_score": round(
                reliability_score,
                2,
            ),
            "claim_support_score": round(
                claim_support_score,
                2,
            ),
            "retrieval_score": round(
                retrieval_score,
                2,
            ),
            "reliability_status": reliability_status,
            "confidence_level": confidence_level,
            "claims": verified_claims,
            "supported_claims": supported_claims,
            "total_claims": total_claims,
        }

    def analyze(
        self,
        answer: str,
        evidence: str,
        retrieval_score: float = 0.0,
    ) -> dict:

        claims = claim_service.extract_claims(answer)

        if not claims:
            return self.calculate_score(
                verified_claims=[],
                retrieval_score=retrieval_score,
            )

        verified_claims = []

        for claim in claims:
            verification = verification_service.verify_claim(
                claim=claim,
                evidence=evidence,
            )

            verified_claims.append(
                {
                    "text": claim,
                    "supported": verification["supported"],
                    "evidence": verification["evidence"],
                }
            )

        return self.calculate_score(
            verified_claims=verified_claims,
            retrieval_score=retrieval_score,
        )


reliability_service = ReliabilityService()