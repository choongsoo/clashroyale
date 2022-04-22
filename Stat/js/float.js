"use strict";

// select similar ego floating menu
async function insertFloatingMenu(
    graph,
    graphVertices,
    mainValue,
    selectedValue,
    container
) {
    const floating = document.createElement("div");
    floating.style.zIndex = 100; // this needs to be the highest amongst all elements to float
    floating.style.position = "fixed";
    floating.classList.add(
        "bg-primary",
        "text-light",
        "p-2",
        "mt-3",
        "ms-2",
        "rounded"
    );

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

    container.appendChild(floating);

    // make select-similar responsive
    selectSimilar.addEventListener("change", async () => {
        const currSelectSimilarValue = selectSimilar.value;
        container.innerHTML = "";
        await insertFloatingMenu(
            graph,
            graphVertices,
            mainValue,
            currSelectSimilarValue,
            container
        );
        insertGraph(currSelectSimilarValue);
    });
}