import json

# the purpose of this script is to produce graphs (networks) of card interaction terms

# read in data
with open("int_lasso.txt") as f:
    interactions = f.read().splitlines()

# build a graph of all interaction terms in the form of an adjacency list
graph = dict()

for pair in interactions:
    card1, card2 = pair.split(":")

    # FIXME: card Fire Spirits has been changed to Fire Spirit - change old data

    if card1 not in graph:
        graph[card1] = []
    if card2 not in graph:
        graph[card2] = []

    graph[card1].append(card2)
    graph[card2].append(card1)

# save to json file
with open("graph_lasso.json", "w") as outfile:
    json.dump(graph, outfile)
