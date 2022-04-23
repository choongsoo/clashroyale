"use strict";

async function insertSelectEgoFloat(graphVertices, container) {
    // make multiselect dropdown menu
    const select = document.createElement("select");
    select.classList.add("form-select", "form-select-sm");
    // const parser = new DOMParser();
    // const select = parser.parseFromString(
    //     `<select class="select" multiple data-mdb-clear-button="true" id="multi"></select>`,
    //     "text/html"
    // ).body.firstElementChild;

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

    console.log(select);

    // make a fixed floating div to contain nav-ego-select's div and potentially select-similar's div
    const floatingDiv = document.createElement("div");
    floatingDiv.id = "floating-div";
    floatingDiv.style.position = "fixed";

    // a div for nav-ego-select
    const navEgoSelectDiv = document.createElement("div");
    navEgoSelectDiv.classList.add(
        "bg-primary",
        "text-light",
        "light",
        "p-2",
        "mt-3",
        "ms-2",
        "rounded"
    );
    navEgoSelectDiv.style.float = "left";
    navEgoSelectDiv.style.clear = "left";

    // select dropdown is ready to be inserted to DOM
    navEgoSelectDiv.appendChild(select);
    floatingDiv.appendChild(navEgoSelectDiv);
    container.appendChild(floatingDiv);

    return select;
}

async function insertSimilarEgoFloat(
    graph,
    graphVertices,
    mainValue,
    selectedValue,
    container
) {
    const floating = document.createElement("div");
    floating.id = "similar-ego-float";
    floating.classList.add(
        "bg-primary",
        "text-light",
        "p-2",
        "mt-3",
        "ms-2",
        "rounded"
    );
    floating.style.float = "left";
    floating.style.clear = "left";

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
    floating.appendChild(selectSimilarLabel);
    floating.appendChild(selectSimilar);

    container.querySelector("#floating-div").appendChild(floating);

    // make select-similar responsive
    selectSimilar.addEventListener("change", async () => {
        document.querySelector("#graph-svg").remove();
        insertGraph(selectSimilar.value);
    });
}
