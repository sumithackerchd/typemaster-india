const paragraph = document.getElementById("paragraph");
const input = document.getElementById("typingInput");

const timerElement = document.getElementById("timer");
const wpmElement = document.getElementById("wpm");
const accuracyElement = document.getElementById("accuracy");
const errorsElement = document.getElementById("errors");
const cpmElement = document.getElementById("cpm");

let timer = 60;
let timerStarted = false;
let interval;

function startTimer(){

    interval = setInterval(()=>{

        timer--;

        timerElement.innerText = timer;

        if(timer<=0){

            clearInterval(interval);

            input.disabled=true;

            alert("Test Completed");

        }

    },1000);

}

input.addEventListener("input",()=>{

    if(!timerStarted){

        timerStarted=true;

        startTimer();

    }

    const original = paragraph.innerText;

    const typed = input.value;

    let correct = 0;
    let errors = 0;

    for(let i=0;i<typed.length;i++){

        if(typed[i]===original[i]){

            correct++;

        }

        else{

            errors++;

        }

    }

    const accuracy = typed.length===0
    ?100
    :((correct/typed.length)*100).toFixed(1);

    const minutes=(60-timer)/60;

    const wpm=minutes>0
    ?Math.round((correct/5)/minutes)
    :0;

    const cpm=minutes>0
    ?Math.round(correct/minutes)
    :0;

    accuracyElement.innerText=accuracy+"%";

    errorsElement.innerText=errors;

    wpmElement.innerText=wpm;

    cpmElement.innerText=cpm;

});