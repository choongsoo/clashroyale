"use strict";

async function insertSelectEgoFloat(graphVertices) {
    // the multiselect dropdown menu
    const select = document.querySelector("#select-ego");

    // all cards available - need their nicely formatted names
    const cardsResp = await fetch("cards.json");
    const cardsJSON = await cardsResp.json();
    let cards = cardsJSON.items.map((item) => item.name);

    // only keep names for cards that exist in the graph
    cards = cards.filter((card) => graphVertices.includes(cleanUpName(card)));
    cards.sort();

    // each option is a card
    cards.forEach((card) => {
        const option = document.createElement("option");
        option.innerText = card;
        select.appendChild(option);
    });

    return select;
}

async function insertSimilarEgoFloat(
    graph,
    graphVertices,
    mainValue,
    selectedValue
) {
    // a user can select from a list of cards that are similar to the main ego card
    const selectSimilar = document.createElement("select");
    selectSimilar.id = "select-similar";
    selectSimilar.classList.add("form-select", "form-select-sm");

    // get set of adjacent cards of curr ego card
    const mainEgo = cleanUpName(mainValue);
    const mainAdjCards = graph[mainEgo];
    const mainAdjVertices = mainAdjCards.map((card) => cleanUpName(card));

    // iterate through graph (adjacency list) to identify all similar ego cards
    // threshold: having at least 1/2 of the same adjacent cards
    const similarEgos = graphVertices.filter((vertex) => {
        const currAdjVertices = graph[vertex];
        // set intersection
        const mainIntersectCurr = mainAdjVertices.filter((v) =>
            currAdjVertices.includes(v)
        );
        // if similarity size exceeds threshould, filter keeps it
        return mainIntersectCurr.length / mainAdjVertices.length >= 0.5;
    });

    similarEgos.sort();

    const vertexCardMap = await makeVertexCardMap();

    // those similar egos will be the options for select-similar
    similarEgos
        .map((vertex) => vertexCardMap[vertex])
        .forEach((card) => {
            const option = document.createElement("option");
            option.innerText = card;
            selectSimilar.appendChild(option);
        });

    selectSimilar.value = selectedValue;

    // label for select-similar
    const selectSimilarLabel = document.createElement("label");
    selectSimilarLabel.htmlFor = "select-similar";
    selectSimilarLabel.innerText = "Similar Ego Card:";
    selectSimilarLabel.style.fontSize = "0.85rem";
    selectSimilarLabel.classList.add("pb-2");

    // insert floating menu to DOM
    const floating = document.querySelector("#similar-ego-float");
    floating.appendChild(selectSimilarLabel);
    floating.appendChild(selectSimilar);

    // make select-similar responsive
    selectSimilar.addEventListener("change", async () => {
        document.querySelector("#graph-svg").remove();
        insertGraph(selectSimilar.value);
    });
}
