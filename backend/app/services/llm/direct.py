from typing import List
from app.models.knowledge import KnowledgeItem
from app.services.llm.base import BaseLLMProvider, LLMResult, FALLBACK_UNAVAILABLE_MESSAGE


class DirectGroundingProvider(BaseLLMProvider):
    """
    High-fidelity, deterministic grounding synthesizer.
    Extracts facts and procedures directly from retrieved verified knowledge items
    and formats an authorized response citing exact sources.
    """

    def generate_answer(self, query: str, retrieved_docs: List[KnowledgeItem]) -> LLMResult:
        if not retrieved_docs:
            return LLMResult(
                text=FALLBACK_UNAVAILABLE_MESSAGE,
                model_name="institutional-grounding-engine",
                provider_name="direct-grounding",
                is_grounded=False,
                sources_cited=[]
            )

        sources = [f"{doc.title} ({doc.source_name})" for doc in retrieved_docs]

        # Primary document is the top-ranked match
        top_doc = retrieved_docs[0]
        
        paragraphs = [p.strip() for p in top_doc.content.split("\n\n") if p.strip()]
        lead_summary = paragraphs[0] if paragraphs else top_doc.content

        additional_points = []
        if len(paragraphs) > 1:
            additional_points = paragraphs[1:4]
        elif len(retrieved_docs) > 1:
            for extra_doc in retrieved_docs[1:3]:
                first_p = extra_doc.content.split("\n\n")[0].strip()
                additional_points.append(f"**Regarding {extra_doc.title}**: {first_p}")

        response_parts = [
            f"Based on official institutional records from **{top_doc.source_name}**:",
            "",
            lead_summary,
        ]

        if additional_points:
            response_parts.append("")
            response_parts.append("### Key Details & Procedures:")
            for pt in additional_points:
                response_parts.append(f"- {pt}")

        response_parts.append("")
        response_parts.append(f"**Verified Source:** [{top_doc.title}]({top_doc.source_url or '#'}) — *Issued by {top_doc.source_name}*")

        return LLMResult(
            text="\n".join(response_parts),
            model_name="grounded-synthesizer-v1",
            provider_name="direct-grounding",
            is_grounded=True,
            sources_cited=sources
        )
