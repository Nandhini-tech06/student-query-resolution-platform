import re
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeItem
from app.core.config import settings


STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no",
    "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
    "ours", "ourselves", "out", "over", "own", "same", "she", "should", "shouldn't",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "wasn't", "we", "were", "weren't",
    "what", "when", "where", "which", "while", "who", "whom", "why", "with", "won't",
    "would", "wouldn't", "you", "your", "yours", "yourself", "yourselves", "tell",
    "please", "give", "know", "want"
}


def tokenize(text: str) -> List[str]:
    """
    Convert text into normalized tokens.

    Removes punctuation, converts to lowercase,
    and removes common stopwords.
    """
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())

    return [
        word
        for word in cleaned.split()
        if len(word) > 2 and word not in STOPWORDS
    ]


class RetrievalResult:
    def __init__(
        self,
        items_with_scores: List[Tuple[KnowledgeItem, float]],
        is_confident: bool,
        top_score: float
    ):
        self.items_with_scores = items_with_scores
        self.is_confident = is_confident
        self.top_score = top_score

    @property
    def items(self) -> List[KnowledgeItem]:
        return [
            item
            for item, _ in self.items_with_scores
        ]


def calculate_relevance(
    query_tokens: List[str],
    query_raw: str,
    item: KnowledgeItem,
    category_hint: str | None = None
) -> float:
    """
    Calculate how relevant a knowledge item is to the user's query.
    """

    if not query_tokens:
        return 0.0

    title_text = item.title.lower()
    content_text = item.content.lower()
    tags_text = (item.tags or "").lower()
    item_category = item.category.lower()

    title_tokens = set(tokenize(title_text))
    content_tokens = set(tokenize(content_text))
    tag_tokens = set(tokenize(tags_text))

    # Count matching query terms
    title_matches = sum(
        1 for token in query_tokens
        if token in title_tokens
    )

    tag_matches = sum(
        1 for token in query_tokens
        if token in tag_tokens
    )

    content_matches = sum(
        1 for token in query_tokens
        if token in content_tokens
    )

    # Phrase matching
    raw_lower = query_raw.lower().strip()

    phrase_bonus = 0.0

    if len(raw_lower) > 4:

        if raw_lower in title_text:
            phrase_bonus += 0.4

        elif raw_lower in content_text:
            phrase_bonus += 0.25

    # Bigram matching
    words = raw_lower.split()

    bigrams = [
        f"{words[i]} {words[i + 1]}"
        for i in range(len(words) - 1)
    ]

    bigram_matches = sum(
        1
        for bg in bigrams
        if bg in content_text or bg in title_text
    )

    phrase_bonus += min(
        0.3,
        bigram_matches * 0.1
    )

    # Category matching
    category_bonus = 0.0

    if category_hint:

        hint_clean = category_hint.lower().strip()

        if (
            hint_clean in item_category
            or item_category in hint_clean
        ):
            category_bonus = 0.2

    # Weighted scoring
    total_query_terms = len(query_tokens)

    title_score = (
        title_matches / total_query_terms
    ) * 0.45

    tag_score = (
        tag_matches / total_query_terms
    ) * 0.25

    content_score = (
        content_matches / total_query_terms
    ) * 0.30

    score = (
        title_score
        + tag_score
        + content_score
        + phrase_bonus
        + category_bonus
    )

    return min(
        1.0,
        round(score, 4)
    )


class KnowledgeRetriever:

    def __init__(self, db: Session):
        self.db = db

    def retrieve(
        self,
        query: str,
        category_hint: str | None = None,
        top_k: int = 4
    ) -> RetrievalResult:

        query_tokens = tokenize(query)

        if not query_tokens:
            return RetrievalResult(
                [],
                is_confident=False,
                top_score=0.0
            )

        # Get active knowledge items only
        active_items = (
            self.db
            .query(KnowledgeItem)
            .filter(
                KnowledgeItem.is_active.is_(True)
            )
            .all()
        )

        if not active_items:
            return RetrievalResult(
                [],
                is_confident=False,
                top_score=0.0
            )

        # Calculate relevance score for every active item
        scored_items: List[
            Tuple[KnowledgeItem, float]
        ] = []

        for item in active_items:

            score = calculate_relevance(
                query_tokens,
                query,
                item,
                category_hint
            )

            if score > 0.05:
                scored_items.append(
                    (item, score)
                )

        # Sort highest score first
        scored_items.sort(
            key=lambda x: x[1],
            reverse=True
        )

        # Get initial candidates
        top_candidates = scored_items[:top_k]

        # Find best score
        top_score = (
            top_candidates[0][1]
            if top_candidates
            else 0.0
        )

        # Check confidence threshold
        is_confident = (
            top_score
            >= settings.RAG_MIN_CONFIDENCE
        )

        # Keep only strongly relevant results
        if is_confident and top_candidates:

            relevance_threshold = max(
                0.20,
                top_score * 0.50
            )

            relevant_candidates = [
                (item, score)
                for item, score in top_candidates
                if score >= relevance_threshold
            ]

        else:

            relevant_candidates = []

        return RetrievalResult(
            items_with_scores=relevant_candidates,
            is_confident=is_confident,
            top_score=top_score
        )