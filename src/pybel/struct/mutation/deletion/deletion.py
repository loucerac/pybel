# -*- coding: utf-8 -*-

"""Functions for deleting nodes and edges in networks."""

from ...filters.edge_filters import filter_edges
from ...filters.edge_predicates import is_associative_relation
from ...filters.node_filters import get_nodes
from ...filters.node_predicate_builders import function_inclusion_filter_builder
from ...pipeline import in_place_transformation
from ....constants import PATHOLOGY

__all__ = [
    'remove_filtered_edges',
    'remove_associations',
    'remove_pathologies',
]


@in_place_transformation
def remove_filtered_edges(graph, edge_predicates=None):
    """Remove edges passing the given edge predicates.

    :param pybel.BELGraph graph: A BEL graph
    :param edge_predicates: A predicate or list of predicates
    :type edge_predicates: Optional[(pybel.BELGraph, tuple, tuple, int) -> bool or iter[(pybel.BELGraph, tuple, tuple, int) -> bool]]
    :return:
    """
    edges = list(filter_edges(graph, edge_predicates=edge_predicates))
    graph.remove_edges_from(edges)


@in_place_transformation
def remove_filtered_nodes(graph, node_predicates=None):
    """Remove nodes passing the given node predicates.

    :param pybel.BELGraph graph: A BEL graph
    """
    nodes = get_nodes(graph, node_predicates=node_predicates)
    graph.remove_nodes_from(nodes)


@in_place_transformation
def remove_associations(graph):
    """Remove all associative relationships from the graph.

    :param pybel.BELGraph graph: A BEL graph
    """
    remove_filtered_edges(graph, is_associative_relation)


@in_place_transformation
def remove_pathologies(graph):
    """Remove pathology nodes from the graph.

    :param pybel.BELGraph graph: A BEL graph
    """
    remove_filtered_nodes(graph, node_predicates=function_inclusion_filter_builder(PATHOLOGY))
