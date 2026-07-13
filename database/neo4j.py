"""Graph storage for entity relationships (victim -> suspect -> case).

For the hackathon MVP this defaults to a simple in-memory graph so the demo
runs with zero infrastructure. If NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD
environment variables are set, it transparently uses a real Neo4j instance
instead via the official driver.
"""

import os
from collections import defaultdict

_NEO4J_URI = os.environ.get("NEO4J_URI")
_NEO4J_USER = os.environ.get("NEO4J_USER")
_NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")


class InMemoryGraphStore:
    """A minimal stand-in for Neo4j: entity -> set of case_ids."""

    def __init__(self):
        self._entity_cases = defaultdict(set)

    def link(self, entity: str, case_id: str):
        self._entity_cases[entity].add(case_id)

    def related_cases(self, entity: str):
        return sorted(self._entity_cases.get(entity, set()))

    def all_links(self):
        return {
            entity: sorted(cases)
            for entity, cases in self._entity_cases.items()
            if len(cases) > 1  # only entities that actually connect >1 case are interesting
        }


class Neo4jGraphStore:
    """Thin wrapper around the real neo4j-driver, same interface as InMemoryGraphStore."""

    def __init__(self, uri: str, user: str, password: str):
        from neo4j import GraphDatabase  # imported lazily so it's optional

        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def link(self, entity: str, case_id: str):
        with self._driver.session() as session:
            session.run(
                """
                MERGE (e:Entity {name: $entity})
                MERGE (c:Case {id: $case_id})
                MERGE (e)-[:LINKED_TO]->(c)
                """,
                entity=entity,
                case_id=case_id,
            )

    def related_cases(self, entity: str):
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (:Entity {name: $entity})-[:LINKED_TO]->(c:Case)
                RETURN c.id AS case_id
                """,
                entity=entity,
            )
            return sorted(r["case_id"] for r in result)

    def all_links(self):
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (e:Entity)-[:LINKED_TO]->(c:Case)
                RETURN e.name AS entity, collect(c.id) AS case_ids
                """
            )
            return {
                r["entity"]: sorted(r["case_ids"])
                for r in result
                if len(r["case_ids"]) > 1
            }


def get_graph_store():
    """Returns a Neo4j-backed store if credentials are configured, else an in-memory one."""
    if _NEO4J_URI and _NEO4J_USER and _NEO4J_PASSWORD:
        return Neo4jGraphStore(_NEO4J_URI, _NEO4J_USER, _NEO4J_PASSWORD)
    return InMemoryGraphStore()


# Module-level singleton so all agents/tools in one process share the same graph.
graph_store = get_graph_store()
