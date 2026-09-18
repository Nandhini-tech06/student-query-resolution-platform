import logging
from typing import List

from app.models.knowledge import KnowledgeItem
from app.services.llm.base import (
    BaseLLMProvider,
    LLMResult,
    FALLBACK_UNAVAILABLE_MESSAGE,
)
from app.services.llm.direct import DirectGroundingProvider


logger = logging.getLogger("uvicorn.error")


SYSTEM_INSTRUCTION = """
You are the official Student Query Resolution Assistant.

Your primary directive is to provide clear, helpful, and factually grounded
answers to university students.

CRITICAL OPERATIONAL RULES:

1. Base your answer EXCLUSIVELY on the provided institutional context chunks.

2. DO NOT make up, assume, extrapolate, or hallucinate policies, dates,
fees, grades, administrative procedures, or other university information.

3. If the provided context does NOT contain enough information to answer
the question reliably, state:

"The specific information for this query is not available in the current
verified university records. Please check with the respective department office."

4. Always cite the relevant document title and source name at the conclusion
of your explanation.

5. Maintain a professional, polite, and reassuring academic tone.

6. Do not use general world knowledge to answer university-specific questions.

7. Treat the retrieved institutional documents as the only authoritative
source of university-specific information.
"""


class GeminiLLMProvider(BaseLLMProvider):
    """
    Generative AI provider using Google's Gemini API.

    The provider receives documents retrieved by the RAG system and asks
    Gemini to generate an answer strictly from those documents.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-3.6-flash",
    ):
        self.api_key = api_key
        self.model_name = model_name

        # Kept for compatibility with the existing project.
        # Gemini errors are NOT silently passed to this provider.
        self.fallback_provider = DirectGroundingProvider()

    # ============================================================
    # GENERATE ANSWER
    # ============================================================

    def generate_answer(
        self,
        query: str,
        retrieved_docs: List[KnowledgeItem],
    ) -> LLMResult:

        # --------------------------------------------------------
        # STEP 1: Validate retrieved documents
        # --------------------------------------------------------

        if not retrieved_docs:
            return LLMResult(
                text=FALLBACK_UNAVAILABLE_MESSAGE,
                model_name=self.model_name,
                provider_name="gemini-genai",
                is_grounded=False,
                sources_cited=[],
            )

        # --------------------------------------------------------
        # STEP 2: Validate API key
        # --------------------------------------------------------

        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "GEMINI_API_KEY is missing or empty. "
                "Check the .env file."
            )

        try:
            # ----------------------------------------------------
            # STEP 3: Import Gemini SDK
            # ----------------------------------------------------

            from google import genai
            from google.genai import types

            logger.info(
                "Initializing Gemini provider: model=%s",
                self.model_name,
            )

            # ----------------------------------------------------
            # STEP 4: Create Gemini client
            # ----------------------------------------------------

            client = genai.Client(
                api_key=self.api_key.strip()
            )

            # ----------------------------------------------------
            # STEP 5: Build institutional context
            # ----------------------------------------------------

            context_blocks = []
            sources = []

            for idx, doc in enumerate(
                retrieved_docs,
                start=1,
            ):
                source_name = getattr(
                    doc,
                    "source_name",
                    None,
                )

                source_url = getattr(
                    doc,
                    "source_url",
                    None,
                )

                category = getattr(
                    doc,
                    "category",
                    None,
                )

                title = getattr(
                    doc,
                    "title",
                    "Untitled Document",
                )

                content = getattr(
                    doc,
                    "content",
                    "",
                )

                if source_name is None:
                    source_name = "Institutional Knowledge Base"

                sources.append(
                    f"{title} ({source_name})"
                )

                context_blocks.append(
                    f"[Document {idx}]\n"
                    f"Title: {title}\n"
                    f"Category: {category}\n"
                    f"Authority Source: {source_name}\n"
                    f"Source URL: {source_url}\n"
                    f"Content:\n{content}\n"
                )

            full_context = "\n---\n".join(
                context_blocks
            )

            # ----------------------------------------------------
            # STEP 6: Build grounded prompt
            # ----------------------------------------------------

            prompt = (
                "Student Question:\n"
                f"{query}\n\n"
                "Official Institutional Knowledge Context:\n"
                f"{full_context}\n\n"
                "Instructions:\n"
                "Answer the student's question strictly using "
                "the official institutional context above. "
                "Do not introduce information that is not present "
                "in the supplied context."
            )

            # ----------------------------------------------------
            # STEP 7: Call Gemini
            # ----------------------------------------------------

            logger.info(
                "Sending request to Gemini API: model=%s",
                self.model_name,
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                ),
            )

            # ----------------------------------------------------
            # STEP 8: Extract generated response
            # ----------------------------------------------------

            generated_text = None

            if response is not None:
                generated_text = getattr(
                    response,
                    "text",
                    None,
                )

            if generated_text:
                generated_text = generated_text.strip()

            if not generated_text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            # ----------------------------------------------------
            # STEP 9: Successful Gemini response
            # ----------------------------------------------------

            logger.info(
                "Gemini successfully generated an answer "
                "using model=%s",
                self.model_name,
            )

            return LLMResult(
                text=generated_text,
                model_name=self.model_name,
                provider_name="gemini-genai",
                is_grounded=True,
                sources_cited=sources,
            )

        # --------------------------------------------------------
        # GEMINI ERROR
        # --------------------------------------------------------

        except Exception as exc:

            logger.exception(
                "============================================================"
            )

            logger.exception(
                "GEMINI API CALL FAILED"
            )

            logger.exception(
                "Model: %s",
                self.model_name,
            )

            logger.exception(
                "Error type: %s",
                type(exc).__name__,
            )

            logger.exception(
                "Error message: %s",
                str(exc),
            )

            logger.exception(
                "============================================================"
            )

            # IMPORTANT:
            # Do NOT silently use DirectGroundingProvider here.
            #
            # If Gemini fails, the actual error must be visible so
            # that the Gemini configuration can be fixed.

            raise