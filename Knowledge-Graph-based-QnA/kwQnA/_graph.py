import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from kwQnA._getentitypair import GetEntity


class GraphEnt:
    """docstring for graphEnt."""

    def __init__(self):
        super(GraphEnt, self).__init__()
        self.x = GetEntity()

    def createGraph(self, dataEntities):
        entity_list = dataEntities.values.tolist()
        #print('entity list _graph.py: ', entity_list)
        source, relations, target = [],[],[]

        filtered_list = [[item for item in sublist if item != ''] for sublist in entity_list]

        for i in filtered_list:

            ### burada sikinti var !!!

            source.append(i[0])
            relations.append(i[1])
            target.append(i[2])
            #aux_relations = i[2]
            #time = i[4]
            #place = i[5]


        kg_df = pd.DataFrame({'source':source, 'target':target, 'edge':relations})
        G=nx.from_pandas_edgelist(kg_df, "source", "target", edge_attr=True, create_using=nx.MultiDiGraph())

        fig, ax = plt.subplots(figsize=(12, 12))
        pos = nx.spring_layout(G, k = 2) # k regulates the distance between nodes
        nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos=pos, ax=ax)

        # Add edge labels
        edge_labels = {(edge[0], edge[1]): edge[2]['edge'] for edge in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, font_color='red', ax=ax)


        plt.show()

if __name__ == '__main__':
    test = GraphEnt()
    print("Can't Test directly")
