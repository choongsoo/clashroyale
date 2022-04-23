"use strict";

/**
 * a function that produces an svg as an interactive graph
 *
 * ego: null produces full graph, else produces ego network given a card
 */
async function constructGraph(ego = null) {
    // create list of card-URL mappings for vertex icons
    const cardsResp = await fetch("cards.json");
    const cardsJSON = await cardsResp.json();
    const cardsArray = cardsJSON.items.map((card) => {
        const id = cleanUpName(card.name);
        const obj = {};
        obj[id] = { name: card.name, url: card.iconUrls.medium };
        return obj;
    });
    const allCards = cardsArray.reduce((r, c) => Object.assign(r, c), {});

    // read in graph json
    const graphResp = await fetch("graph_lasso_0.001.json?0");
    const weightedGraph = await graphResp.json();
    let graph = weightedGraph.adj;
    const weights = weightedGraph.wgt;
    const maxWeight = Math.max(...Object.values(weights));

    // build ego network if specified
    if (ego) {
        const mainCard = cleanUpName(ego);
        const mainAdj = graph[mainCard];

        const egoNetwork = {};
        egoNetwork[mainCard] = mainAdj;

        mainAdj.forEach((adj) => {
            const adjAdj = graph[adj];
            egoNetwork[adj] = mainAdj.filter((adj) => adjAdj.includes(adj)); // set intersection
            egoNetwork[adj].push(mainCard);
        });

        graph = egoNetwork;
    }

    // transform graph data into D3-compliant format
    const vertices = Object.keys(graph),
        nodes = vertices.map((d) => {
            const card = allCards[d];
            return {
                id: d,
                name: card.name,
                url: card.url,
                group: 1,
            };
        }),
        links = d3.merge(
            vertices.map((source) => {
                return graph[source].map((target) => {
                    return {
                        source: source,
                        target: target,
                        weight:
                            (weights[source + ":" + target] / maxWeight) * 30, // quantile, standardize
                    };
                });
            })
        );

    // construct forces
    const forceNode = d3.forceManyBody();
    const forceLink = d3.forceLink(links).id(({ index: i }) => vertices[i]);

    // note: full graph and ego network nodes have different charges
    let distance = 200,
        strength = -150;
    if (ego) {
        distance = 100;
        strength = -1000;
    }

    const simulation = d3
        .forceSimulation(nodes)
        .force("link", forceLink.distance(distance))
        .force("charge", forceNode.strength(strength))
        .force("center", d3.forceCenter())
        .on("tick", ticked);

    // create DOM elements
    const width = getViewportWidth(), // helper vars - old: 1400 x 700
        height = getViewportHeight() - 40;

    const svg = d3
        .create("svg")
        .attr("id", "graph-svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

    const link = svg
        .append("g")
        .attr("stroke", "#ccc")
        // .attr("stroke-width", 1.5)
        .selectAll("line")
        .data(links)
        .join("line")
        .attr("stroke-width", (d) => d.weight) // edge width by synergy strength
        .attr("class", (d) => makeEdgeId(d.source.id, d.target.id));
    // note: using class instead of id because edges contain duplicates

    const imgWidth = 32, // helper vars
        imgHeight = imgWidth,
        imgX = (-1 * imgWidth) / 2,
        imgY = imgX;

    const node = svg
        .append("g")
        .selectAll("image")
        .data(nodes)
        .join("image")
        .attr("id", (d) => d.id)
        .attr("xlink:href", (d) => d.url)
        .attr("x", imgX)
        .attr("y", imgY)
        .attr("width", imgWidth)
        .attr("height", imgHeight)
        .call(drag(simulation));

    // add hover effects to nodes
    node.on("mouseover", function (d, i) {
        updateAdjacencyOutline(this, "red", "red", graph);
    }).on("mouseout", function (d, i) {
        updateAdjacencyOutline(this, "none", "#ccc", graph);
    });

    // animation logic
    function ticked() {
        link.attr("x1", (d) => d.source.x)
            .attr("y1", (d) => d.source.y)
            .attr("x2", (d) => d.target.x)
            .attr("y2", (d) => d.target.y);

        node.attr("transform", (d) => {
            // restrict node coordinates to be within container boundaries
            const newX = restrictCoordinate(d.x, width, imgWidth);
            const newY = restrictCoordinate(d.y, height, imgHeight);
            d.x = newX; // important: update source data so that edges (links) can be updated
            d.y = newY;
            return "translate(" + newX + "," + newY + ")";
        });
    }

    // node drag logic
    function drag(simulation) {
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = restrictCoordinate(event.x, width, imgWidth);
            event.subject.fy = restrictCoordinate(event.y, height, imgHeight);
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        return d3
            .drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
    }

    return svg.node();
}

// inserts graph svg into DOM
function insertGraph(ego = null) {
    constructGraph(ego).then((graph) =>
        document.querySelector("#container").appendChild(graph)
    );
}
