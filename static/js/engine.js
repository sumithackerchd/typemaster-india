// ==============================================
// TypeMaster India Engine v2.0
// Part 1 - Core Engine Foundation
// ==============================================

// ---------- DOM ----------
const paragraphElement = document.getElementById("paragraph");
const typingInput = document.getElementById("typingInput");

const accuracyElement = document.getElementById("accuracy");
const errorsElement = document.getElementById("errors");
const wpmElement = document.getElementById("wpm");
const cpmElement = document.getElementById("cpm");

// ---------- Default Paragraph ----------
let paragraphText = `The quick brown fox jumps over the lazy dog. Practice every day to improve your typing speed and accuracy. Consistency is the key to success.`;

// ---------- Engine Variables ----------
let characterSpans = [];

let currentIndex = 0;

let totalErrors = 0;

let totalCorrect = 0;

let typingStarted = false;

let finished = false;

// ==============================================
// Render Paragraph
// ==============================================

function renderParagraph() {

    paragraphElement.innerHTML = "";

    characterSpans = [];

    [...paragraphText].forEach((character) => {

        const span = document.createElement("span");

        span.innerText = character;

        span.classList.add("char");

        paragraphElement.appendChild(span);

        characterSpans.push(span);

    });

    if(characterSpans.length>0){

        characterSpans[0].classList.add("current");

    }

}

renderParagraph();


// ==============================================
// Auto Focus
// ==============================================

document.addEventListener("click",()=>{

    typingInput.focus();

});

window.onload=()=>{

    typingInput.focus();

}


// ==============================================
// Reset Character Colors
// ==============================================

function resetCharacters(){

    characterSpans.forEach((span)=>{

        span.classList.remove(

            "correct",

            "wrong",

            "current"

        );

    });

}


// ==============================================
// Update Character UI
// ==============================================

function updateCharacters(){

    resetCharacters();

    totalErrors=0;

    totalCorrect=0;

    const typed=typingInput.value;

    for(let i=0;i<characterSpans.length;i++){

        const expected=paragraphText[i];

        const entered=typed[i];

        if(entered==null){

            break;

        }

        if(entered===expected){

            characterSpans[i].classList.add("correct");

            totalCorrect++;

        }

        else{

            characterSpans[i].classList.add("wrong");

            totalErrors++;

        }

    }

    currentIndex=typed.length;

    if(currentIndex<characterSpans.length){

        characterSpans[currentIndex]

        .classList.add("current");

    }

}


// ==============================================
// Typing Event
// ==============================================

typingInput.addEventListener("input",()=>{

    if(finished){

        return;

    }

    if(!typingStarted){

        typingStarted=true;

        if(typeof startTimer==="function"){

            startTimer();

        }

    }

    updateCharacters();

    updateBasicStats();

});


// ==============================================
// Basic Stats
// ==============================================

function updateBasicStats(){

    const typed=typingInput.value.length;

    let accuracy=100;

    if(typed>0){

        accuracy=((totalCorrect/typed)*100)

        .toFixed(1);

    }

    accuracyElement.innerText=accuracy+"%";

    errorsElement.innerText=totalErrors;

}


// ==============================================
// Engine Reset
// ==============================================

function resetEngine(){

    typingInput.value="";

    currentIndex=0;

    totalErrors=0;

    totalCorrect=0;

    typingStarted=false;

    finished=false;

    renderParagraph();

    accuracyElement.innerText="100%";

    errorsElement.innerText="0";

    wpmElement.innerText="0";

    cpmElement.innerText="0";

}
// ==============================================
// Part 2 - Keyboard + Word + Finish Engine
// Paste this BELOW Part 1
// ==============================================


// ---------- Prevent Paste ----------
typingInput.addEventListener("paste", function (e) {
    e.preventDefault();
});


// ---------- Prevent Drop ----------
typingInput.addEventListener("drop", function (e) {
    e.preventDefault();
});


// ---------- Prevent Right Click ----------
typingInput.addEventListener("contextmenu", function (e) {
    e.preventDefault();
});


// ---------- Auto Focus ----------
document.addEventListener("click", function () {
    typingInput.focus();
});


// ---------- Highlight Current Word ----------
function highlightCurrentWord() {

    characterSpans.forEach(span => {

        span.classList.remove("active-word");

    });

    let start = currentIndex;

    while (start > 0 && paragraphText[start - 1] !== " ") {

        start--;

    }

    let end = currentIndex;

    while (end < paragraphText.length && paragraphText[end] !== " ") {

        end++;

    }

    for (let i = start; i < end; i++) {

        if (characterSpans[i]) {

            characterSpans[i].classList.add("active-word");

        }

    }

}


// ---------- Auto Scroll ----------
function autoScrollCurrentCharacter() {

    const current = document.querySelector(".current");

    if (!current) return;

    current.scrollIntoView({

        behavior: "smooth",

        block: "center"

    });

}


// ---------- Finish Check ----------
function checkTypingFinished() {

    if (typingInput.value.length >= paragraphText.length) {

        finished = true;

        typingInput.blur();

        if (typeof finishTest === "function") {

            finishTest();

        }

    }

}


// ---------- Engine Extension ----------
function afterCharacterUpdate() {

    highlightCurrentWord();

    autoScrollCurrentCharacter();

    checkTypingFinished();

}


// ---------- Attach Extension ----------

typingInput.addEventListener("input", function () {

    if (finished) return;

    afterCharacterUpdate();

});


// ---------- Restart Focus ----------
function focusTypingArea() {

    if (!finished) {

        typingInput.focus();

    }

}

window.addEventListener("load", focusTypingArea);

document.addEventListener("keydown", focusTypingArea);
// ==============================================
// TypeMaster India Engine v2.0
// Part 3 - WPM + Result + Finish
// ==============================================


// -----------------------------
// Calculate WPM / CPM
// -----------------------------

function calculateStatistics() {

    let typed = typingInput.value.length;

    let elapsed = totalTime - timeLeft;

    if (elapsed <= 0) elapsed = 1;

    let minutes = elapsed / 60;

    let grossWPM = Math.round((typed / 5) / minutes);

    let netWPM = Math.round(((typed - totalErrors) / 5) / minutes);

    if (grossWPM < 0) grossWPM = 0;

    if (netWPM < 0) netWPM = 0;

    let cpm = Math.round(typed / minutes);

    document.getElementById("wpm").innerText = netWPM;

    document.getElementById("cpm").innerText = cpm;

}


// -----------------------------
// Update Live Statistics
// -----------------------------

typingInput.addEventListener("input", function () {

    if (finished) return;

    calculateStatistics();

});


// -----------------------------
// Result Object
// -----------------------------

function buildResultObject() {

    let typed = typingInput.value.length;

    let elapsed = totalTime - timeLeft;

    if (elapsed <= 0) elapsed = 1;

    let minutes = elapsed / 60;

    let grossWPM = Math.round((typed / 5) / minutes);

    let netWPM = Math.round(((typed - totalErrors) / 5) / minutes);

    if (grossWPM < 0) grossWPM = 0;

    if (netWPM < 0) netWPM = 0;

    let accuracy = 100;

    if (typed > 0) {

        accuracy = ((totalCorrect / typed) * 100).toFixed(2);

    }

    return {

        gross_wpm: grossWPM,

        net_wpm: netWPM,

        cpm: Math.round(typed / minutes),

        accuracy: accuracy,

        errors: totalErrors,

        correct: totalCorrect,

        typed: typed,

        total: paragraphText.length,

        language: "English",

        difficulty: "Easy",

        duration: totalTime

    };

}


// -----------------------------
// Finish Typing
// -----------------------------

function completeTypingTest() {

    finished = true;

    typingInput.disabled = true;

    calculateStatistics();

    const result = buildResultObject();

    console.log(result);

    // Future
    // fetch("/save-result", {...})

    // Future
    // window.location="/result"

}


// -----------------------------
// Override Finish Test
// -----------------------------

if (typeof finishTest === "function") {

    const oldFinish = finishTest;

    finishTest = function () {

        oldFinish();

        completeTypingTest();

    }

}


// -----------------------------
// Restart Engine
// -----------------------------

function restartTypingTest() {

    resetEngine();

    typingInput.disabled = false;

    typingInput.focus();

    if (typeof resetTimer === "function") {

        resetTimer();

    }

}