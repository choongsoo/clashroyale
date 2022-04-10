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
    # row_dist=lambda u, v: np.sqrt(((u-v)**2).sum()),
    # col_dist=lambda u, v: np.sqrt(((u-v)**2).sum()),
    row_dist="jaccard",
    col_dist="jaccard",
    row_labels=cards,
    column_labels=cards,
    height=1300,
    width=1300,
    tick_font={
        "size": 8
    },
    line_width=2,
    display_ratio=[0.2, 0.4],
    color_map=[  # plotly.express.colors.sequential.YlOrRd
        [0.0, 'black'],
        [0.1, 'rgb(61,0,18)'],  # try
        [0.2, 'rgb(128,0,38)'],
        [0.3, 'rgb(189,0,38)'],
        [0.4, 'rgb(227,26,28)'],
        [0.5, 'rgb(252,78,42)'],
        [0.6, 'rgb(253,141,60)'],
        [0.7, 'rgb(254,178,76)'],
        [0.8, 'rgb(254,217,118)'],
        [0.9, 'rgb(255,237,160)'],
        [1.0, 'rgb(255,255,204)'],
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
