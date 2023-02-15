import pickle
import networkx as nx
from pprint import PrettyPrinter

with open("./webtoon_graph.pkl", "rb") as f:
    graphDict: dict = pickle.load(f)

pp = PrettyPrinter()

pp.pprint(graphDict)

graph: nx.Graph = graphDict["헤어지면 죽음"]["66. 1인칭 연우 시점"][0]

nx.write_gexf(graph, "sample_graph.gexf")
