import json
import numpy as np
import dash_bio as dashbio
import plotly


# read in weighted graph
with open("graph_lasso_0.001.json") as f:
    weighted_graph = json.load(f)

weights = weighted_graph["wgt"]

# get all unique cards used in interactions
cards = set()

for pair in weights.keys():
    card1 = pair.split(":")[0]
    if card1 not in cards:
        cards.add(card1)

cards = sorted(list(cards))

# build interaction matrix from weights
matrix = []

for card1 in cards:
    row = []
    for card2 in cards:
        pair = card1 + ":" + card2
        if pair in weights:
            val = weights[pair]
        else:
            val = 0
        row.append(val)
    matrix.append(row)

# clustergram
clustergram = dashbio.Clustergram(
    data=np.array(matrix),
    row_labels=cards,
    column_labels=cards,
    height=1300,
    width=1300,
    tick_font={
        "size": 8
    },
    line_width=2,
    display_ratio=[0.2, 0.4],
    color_map=[  # plotly.express.colors.sequential.Greys
        [0.0, 'rgb(255,255,255)'],
        [0.1, 'rgb(250,250,250)'],
        [0.2, 'rgb(240,240,240)'],
        [0.3, 'rgb(217,217,217)'],
        [0.4, 'rgb(189,189,189)'],
        [0.5, 'rgb(150,150,150)'],
        [0.6, 'rgb(115,115,115)'],
        [0.7, 'rgb(82,82,82)'],
        [0.8, 'rgb(37,37,37)'],
        [0.9, 'rgb(22,22,22)'],
        [1.0, 'rgb(0,0,0)']
    ]
)

clustergram.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
))

# save plot as div
with open("clustergram_div.txt", "w") as f:
    div = plotly.offline.plot(
        clustergram, include_plotlyjs=False, output_type="div")
    f.write(div)
