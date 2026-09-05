from app.repositories.graph_repository import GraphRepository


def test_add_entity(tmp_path):
    repository = GraphRepository(
        graph_path=tmp_path / "knowledge_graph.json"
    )

    repository.add_entity(
        "Diabetes",
        "disease",
    )

    assert repository.entity_count() == 1
    assert repository.get_entity("Diabetes")["entity_type"] == "disease"


def test_add_relationship(tmp_path):
    repository = GraphRepository(
        graph_path=tmp_path / "knowledge_graph.json"
    )

    repository.add_entity(
        "Diabetes",
        "disease",
    )

    repository.add_entity(
        "Cardiovascular Disease",
        "condition",
    )

    repository.add_relationship(
        "Diabetes",
        "may_increase_risk_of",
        "Cardiovascular Disease",
    )

    relationships = repository.get_relationships(
        "Diabetes"
    )

    assert len(relationships) == 1
    assert relationships[0]["relation"] == "may_increase_risk_of"
    assert relationships[0]["target"] == "Cardiovascular Disease"


def test_duplicate_relationship_is_not_created(tmp_path):
    repository = GraphRepository(
        graph_path=tmp_path / "knowledge_graph.json"
    )

    repository.add_entity(
        "Diabetes",
        "disease",
    )

    repository.add_entity(
        "Cardiovascular Disease",
        "condition",
    )

    repository.add_relationship(
        "Diabetes",
        "may_increase_risk_of",
        "Cardiovascular Disease",
    )

    repository.add_relationship(
        "Diabetes",
        "may_increase_risk_of",
        "Cardiovascular Disease",
    )

    assert repository.relationship_count() == 1


def test_search_entity(tmp_path):
    repository = GraphRepository(
        graph_path=tmp_path / "knowledge_graph.json"
    )

    repository.add_entity(
        "Diabetes",
        "disease",
    )

    repository.add_entity(
        "Cardiovascular Disease",
        "condition",
    )

    repository.add_relationship(
        "Diabetes",
        "may_increase_risk_of",
        "Cardiovascular Disease",
    )

    results = repository.search_entity(
        "diabetes"
    )

    assert len(results) == 1
    assert results[0]["name"] == "Diabetes"
    assert len(results[0]["relationships"]) == 1


def test_graph_persistence(tmp_path):
    graph_path = tmp_path / "knowledge_graph.json"

    repository = GraphRepository(
        graph_path=graph_path
    )

    repository.add_entity(
        "Diabetes",
        "disease",
    )

    repository.add_entity(
        "Cardiovascular Disease",
        "condition",
    )

    repository.add_relationship(
        "Diabetes",
        "may_increase_risk_of",
        "Cardiovascular Disease",
    )

    new_repository = GraphRepository(
        graph_path=graph_path
    )

    assert new_repository.entity_count() == 2
    assert new_repository.relationship_count() == 1

    relationships = new_repository.get_relationships(
        "Diabetes"
    )

    assert relationships[0]["target"] == (
        "Cardiovascular Disease"
    )