import json
from pathlib import Path

import networkx as nx


class GraphRepository:
    GRAPH_PATH = Path("data/knowledge_graph.json")

    def __init__(
        self,
        graph_path: Path | str | None = None,
    ):
        self.GRAPH_PATH = (
            Path(graph_path)
            if graph_path is not None
            else self.GRAPH_PATH
        )

        self.graph = nx.DiGraph()
        self._load()

    def _load(self) -> None:
        if not self.GRAPH_PATH.exists():
            return

        try:
            data = json.loads(
                self.GRAPH_PATH.read_text(
                    encoding="utf-8"
                )
            )

            self.graph = nx.node_link_graph(
                data,
                directed=True,
            )

        except (json.JSONDecodeError, ValueError):
            self.graph = nx.DiGraph()

    def _save(self) -> None:
        self.GRAPH_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = nx.node_link_data(self.graph)

        self.GRAPH_PATH.write_text(
            json.dumps(
                data,
                indent=2,
            ),
            encoding="utf-8",
        )

    def add_entity(
        self,
        name: str,
        entity_type: str = "unknown",
    ) -> None:
        self.graph.add_node(
            name,
            entity_type=entity_type,
        )

        self._save()

    def add_relationship(
        self,
        source: str,
        relation: str,
        target: str,
    ) -> None:
        self.graph.add_edge(
            source,
            target,
            relation=relation,
        )

        self._save()

    def get_entity(self, name: str):
        return self.graph.nodes.get(name)

    def get_relationships(self, name: str):
        relationships = []

        if name not in self.graph:
            return relationships

        for source, target, data in self.graph.out_edges(
            name,
            data=True,
        ):
            relationships.append(
                {
                    "source": source,
                    "relation": data["relation"],
                    "target": target,
                }
            )

        return relationships

    def search_entity(self, name: str):
        matches = []

        name_lower = name.lower()

        for node, data in self.graph.nodes(data=True):
            if name_lower in node.lower():
                matches.append(
                    {
                        "name": node,
                        "entity_type": data.get(
                            "entity_type",
                            "unknown",
                        ),
                        "relationships": self.get_relationships(
                            node
                        ),
                    }
                )

        return matches

    def entity_count(self) -> int:
        return self.graph.number_of_nodes()

    def relationship_count(self) -> int:
        return self.graph.number_of_edges()


graph_repository = GraphRepository()