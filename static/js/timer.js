// ===============================
// TypeMaster India Timer v1.0
// ===============================

let totalTime = 60;
let timeLeft = totalTime;
let timerInterval = null;

// -------------------------------
// Start Timer
// -------------------------------

function startTimer() {

    if (timerInterval) return;

    timerInterval = setInterval(() => {

        timeLeft--;

        document.getElementById("timer").innerText = timeLeft;

        calculateSpeed();

        if (timeLeft <= 0) {

            clearInterval(timerInterval);

            finishTest();

        }

    }, 1000);

}

// -------------------------------
// WPM + CPM
// -------------------------------

function calculateSpeed() {

    const typed = typingInput.value.length;

    const minutes = (totalTime - timeLeft) / 60;

    if (minutes <= 0) return;

    const correct = typed - errors;

    const wpm = Math.round((correct / 5) / minutes);

    const cpm = Math.round(correct / minutes);

    document.getElementById("wpm").innerText =

        wpm > 0 ? wpm : 0;

    document.getElementById("cpm").innerText =

        cpm > 0 ? cpm : 0;

}

// -------------------------------
// Finish Test
// -------------------------------

function finishTest() {

    typingInput.disabled = true;

    alert("Typing Test Completed!");

}

// -------------------------------
// Reset Timer
// -------------------------------

function resetTimer() {

    clearInterval(timerInterval);

    timerInterval = null;

    totalTime = 60;

    timeLeft = 60;

    document.getElementById("timer").innerText = 60;

}