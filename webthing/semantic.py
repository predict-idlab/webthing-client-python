from __future__ import annotations # Allow referencing enclosing class in typings
from typing import Dict, List
from enum import Enum

from rdflib import Graph, Namespace


class Namespaces(Enum):
    sosa = 'http://www.w3.org/ns/sosa/'
    ssn = 'http://www.w3.org/ns/ssn/'
    ssn_ext = 'http://dynamicdashboard.ilabt.imec.be/broker/ontologies/ssn-extension/'
    dcterms = 'http://purl.org/dc/terms/'
    m3lite = 'http://purl.org/iot/vocab/m3-lite#'
    rdfs = 'http://www.w3.org/2000/01/rdf-schema#'
    qu = 'http://purl.org/NET/ssnx/qu/qu#'
    time = 'http://www.w3.org/2006/time#'
    prov = 'http://www.w3.org/ns/prov#'
    folio = 'http://IBCNServices.github.io/Folio-Ontology/Folio.owl#'
    dashb = 'http://dynamicdashboard.ilabt.imec.be/broker/ontologies/dashboard#'
    metrics = 'http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#'


class SemanticModel:
    """Class for handeling semantic data."""

    def __init__(self, graph: Graph) -> None:
        """Class for handeling semantic data.

        Args:
            graph (Graph): Initial Graph.
        """
        self._graph = graph
        self._bind_namespaces()

    def _bind_namespaces(self) -> None:
        for namespace_enum in SemanticModel.get_namespace_bindings().values():
            self._graph.bind(namespace_enum.name, namespace_enum.value)

    @classmethod
    def from_data_string(cls, data: str, format: str=None, base: str=None) -> SemanticModel:
        """Create from RDF data string.

        Args:
            data (str): RDF data as string.
            format (str, optional): The format of the RDF data string, use rdflib format string e.g. 'json-ld'. Defaults to None.
            base (str, optional): The base URI to be used for relative URI in data. Defaults to None.

        Returns:
            SemanticModel: New Semantic Model.
        """
        graph = Graph()
        graph.parse(data=data, format=format, publicID=base)
        return cls(graph)

    @classmethod
    def from_jsonld_string(cls, jsonld: str, base: str=None) -> SemanticModel:
        """Create from JSON-LD data string.

        Args:
            jsonld (str): JSON-LD data string.
            base (str, optional): The base URI to be used for relative URI in data. Defaults to None.

        Returns:
            SemanticModel: New Semantic Model.
        """
        return cls.from_data_string(jsonld, "json-ld", base)

    @classmethod
    def from_model(cls, model: SemanticModel) -> SemanticModel:
        """Create from existing Semantic Model (deep copy).

        Args:
            model (SemanticModel): The Semantic Model to copy.

        Returns:
            SemanticModel: Copy of Semantic Model.
        """
        return SemanticModel.from_jsonld_string(model.serialize("json-ld"))

    @staticmethod
    def get_namespace_bindings() -> Dict[str, Namespace]:
        """Get the namespace bindings as dictionary.

        Returns:
            Dict[str, Namespace]: Namespace bindings in form prefix, namespace URI.
        """
        return Namespaces.__members__

    def serialize(self, format="json-ld") -> str:
        """Serialize data in a specific format.

        Args:
            format (str, optional): Format to serialize to, use rdflib format string. Defaults to "json-ld".

        Returns:
            str: Data string in provided format.
        """
        return self._graph.serialize(format=format, auto_compact=True)

    def __str__(self) -> str:
        """String representation as JSON-LD.

        Returns:
            str: JSON-LD string.
        """
        return self.serialize()

    def list_query(self, query: str) -> List[Dict[str, str]]:
        """Return list of results for the given SPARQL query. SELECT query only.

        Args:
            query (str): The SPARQL query.

        Returns:
            List[Dict[str, str]]: Results.
        """
        results = self._graph.query(query)
        result_list = []
        for row_bindings in results.bindings:
            result_list.append({str(var): str(value) for var, value in row_bindings.items()})
        return result_list
