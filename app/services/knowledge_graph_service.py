import json

from app.repositories.graph_repository import graph_repository
from app.schemas.knowledge_graph import KnowledgeGraph
from app.services.llm_service import llm_service


class KnowledgeGraphService:

    def extract(self, text: str) -> KnowledgeGraph:
        prompt = f"""
Extract the entities and relationships from the text below.

The system is domain-agnostic.

Rules:
- Extract only information explicitly stated in the text.
- Do not use outside knowledge.
- Do not invent entities or relationships.
- Use concise entity names.
- Use short snake_case relationship names.
- Return ONLY valid JSON.
- Do not include markdown.

Required JSON format:

{{
    "entities": [
        {{
            "name": "Entity Name",
            "entity_type": "entity_type"
        }}
    ],
    "relationships": [
        {{
            "source": "Entity A",
            "relation": "relationship",
            "target": "Entity B"
        }}
    ]
}}

TEXT:
{text}
""".strip()

        response = llm_service.generate(prompt)

        try:
            data = json.loads(response)
            return KnowledgeGraph.model_validate(data)
        except (json.JSONDecodeError, ValueError, TypeError):
            return KnowledgeGraph()

    def extract_and_store(self, text: str) -> KnowledgeGraph:
        graph = self.extract(text)

        for entity in graph.entities:
            graph_repository.add_entity(
                name=entity.name,
                entity_type=entity.entity_type,
            )

        for relationship in graph.relationships:
            graph_repository.add_relationship(
                source=relationship.source,
                relation=relationship.relation,
                target=relationship.target,
            )

        return graph

    def extract_query_entities(self, query: str) -> list[str]:
        prompt = f"""
Extract the important entities from the user's question.

Rules:
- Return ONLY a valid JSON array of strings.
- Extract names of people, organizations, places, products,
  technologies, concepts, diseases, events, etc.
- Do not invent entities.
- Do not include generic question words.
- If there are no identifiable entities, return [].

Question:
{query}
""".strip()

        response = llm_service.generate(prompt)

        try:
            entities = json.loads(response)
        except json.JSONDecodeError:
            return []

        if not isinstance(entities, list):
            return []

        return [
            entity.strip()
            for entity in entities
            if isinstance(entity, str) and entity.strip()
        ]

    def get_context(self, query: str) -> str:
        entities = self.extract_query_entities(query)

        if not entities:
            return ""

        matches = []

        for entity in entities:
            matches.extend(
                graph_repository.search_entity(entity)
            )

        if not matches:
            return ""

        context_parts = []

        seen_relationships = set()

        for match in matches:
            context_parts.append(
                f"Entity: {match['name']}"
            )

            for relationship in match["relationships"]:
                relationship_key = (
                    relationship["source"],
                    relationship["relation"],
                    relationship["target"],
                )

                if relationship_key in seen_relationships:
                    continue

                seen_relationships.add(relationship_key)

                context_parts.append(
                    f"- {relationship['source']} "
                    f"{relationship['relation']} "
                    f"{relationship['target']}"
                )

        return "\n".join(context_parts)


knowledge_graph_service = KnowledgeGraphService()