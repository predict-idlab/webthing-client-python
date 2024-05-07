import textwrap
from typing import Optional

from webthing_client.client import WebthingAdminClient


def get_graph(webthing_fqdn: str, graph_iri: Optional[str]=None) -> None:
    """Get a graph from the webthing.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        graph_iri (Optional[str]): The graph IRI to get, if null get default graph.
    """
    client = WebthingAdminClient(webthing_fqdn)
    graph: str = client.get_graph(graph_iri)
    print(f"Graph <{graph_iri}>, length {len(graph)}:")
    print(textwrap.indent(graph, "  "))

def delete_graph(webthing_fqdn: str, graph_iri: Optional[str]=None) -> None:
    """Delete a graph from the webthing.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
        graph_iri (Optional[str]): The graph IRI to delete, if null delete default graph.
    """
    client = WebthingAdminClient(webthing_fqdn)
    client.delete_graph(graph_iri)
    print(f"Deleted Graph <{graph_iri}>")

def reload(webthing_fqdn: str) -> None:
    """Reload the webthing.

    Args:
        webthing_fqdn (str): Fully qualified domain name | 'webthing.example.com'
    """
    client = WebthingAdminClient(webthing_fqdn)
    client.reload()
    print(f"Reloaded Webthing")
