let currentDifficulty = "easy";

async function loadParagraph() {

    const response = await fetch("/static/data/paragraphs.json");

    const data = await response.json();

    const list = data.english[currentDifficulty];

    const random = Math.floor(Math.random() * list.length);

    paragraphText = list[random];

    renderParagraph();

}

window.addEventListener("load", loadParagraph);
function changeDifficulty(level){

    currentDifficulty = level;

    resetEngine();

    loadParagraph();

}