import pydecode.hyper as ph
from pydecode.semiring import *
INF = 1e8


class ChartBuilder:
    """
    A dynamic programming chart parameterized by semiring.


    """

    def __init__(self, score_fn, semiring=ProbSemiRing,
                 build_hypergraph=False):
        """
        Initialize the dynamic programming chart.

        Parameters
        ------------

        score_fn :  label -> "score"
           A function from edge label to score.

        semiring : :py:class:`SemiRing`
           The semiring class to use.

        build_hypergraph : bool
           Should we build a hypergraph in the chart.

        """
        self._builder = build_hypergraph
        self._chart = {}
        self._semiring = semiring
        self._scorer = score_fn
        self._hypergraph = ph.Hypergraph()
        self._build = self._hypergraph.builder()
        self._build.__enter__()
        self._done = False
        self._last = None

    def finish(self):
        if self._done:
            raise Exception("Hypergraph not constructed")
        if self._builder:
            self._done = True
            self._build.__exit__(None, None, None)
            return self._hypergraph
        else:
            return self._chart[self._last].unpack()

    def sr(self, label):
        return self._semiring.make(self._scorer(label))

    def init(self, node_label):
        if self._builder:
            print "start"
            node = self._build.add_node([], label=node_label)
            self._chart[node_label] = HypergraphSemiRing([], [node], None)
        else:
            self._chart[node_label] = self._semiring.one()

    def sum(self, edges):
        return sum(edges, self._semiring.zero())

    def __setitem__(self, label, val):
        if label in self._chart:
            raise Exception(
                "Chart already has label {}".format(label))
        print label, val
        if self._builder:
            if not val.is_zero():
                print val.edge_list
                node = self._build.add_node(val.edge_list,
                                             label=label)
                self._chart[label] = \
                    HypergraphSemiRing([], [node], None)
        else:
            if not val.is_zero():
                self._chart[label] = val
        self._last = label

    def __contains__(self, label):
        return label in self._chart

    def __getitem__(self, label):
        return self._chart.get(label, self._semiring.zero())
