/**
 * TypeMaster India — Unified Typing Engine
 * Supports English + Hindi (Mangal Unicode) via TYPING_CONFIG
 */
(function () {

    "use strict";

    const DEFAULT_CONFIG = {
        defaultLanguage: "english",
        redirectUrl: "/result",
        saveResultUrl: "/save-result",
        languages: {
            english: {
                languageKey: "english",
                dataUrl: "/static/data/paragraphs.json",
                saveLanguage: "English",
                title: "English Typing Test",
                paragraphClass: ""
            },
            hindi: {
                languageKey: "hindi",
                dataUrl: "/static/data/hindi_mangal.json",
                saveLanguage: "Hindi",
                title: "Hindi Mangal Typing Test",
                paragraphClass: "hindi-paragraph"
            }
        }
    };

    const config = Object.assign({}, DEFAULT_CONFIG, window.TYPING_CONFIG || {});

    const paragraphElement = document.getElementById("paragraph");
    const typingInput = document.getElementById("typingInput");
    const timerElement = document.getElementById("timer");
    const pageTitleElement = document.getElementById("typingTitle");
    const netWpmElement = document.getElementById("netWpm");
    const grossWpmElement = document.getElementById("grossWpm");
    const liveWpmElement = document.getElementById("liveWpm");
    const accuracyElement = document.getElementById("accuracy");
    const errorsElement = document.getElementById("errors");
    const cpmElement = document.getElementById("cpm");

    if (!paragraphElement || !typingInput) {
        return;
    }

    const paragraphCache = {};
    let activeLanguage = config.defaultLanguage;
    let activeLangConfig = config.languages[activeLanguage] || config.languages.english;

    let currentDifficulty = "easy";
    let currentTimer = 60;
    let timer = 60;
    let timerStarted = false;
    let timerInterval = null;
    let testStartTime = null;
    let totalTyped = 0;
    let correctTyped = 0;
    let wrongTyped = 0;
    let finished = false;
    let currentParagraph = "";

    function getLangConfig(lang) {

        return config.languages[lang] || config.languages.english;

    }

    async function fetchParagraphData(langConfig) {

        if (paragraphCache[langConfig.languageKey]) {
            return paragraphCache[langConfig.languageKey];
        }

        const response = await fetch(langConfig.dataUrl);

        if (!response.ok) {
            throw new Error("Failed to load " + langConfig.saveLanguage + " paragraphs");
        }

        const data = await response.json();
        paragraphCache[langConfig.languageKey] = data;

        return data;

    }

    async function preloadLanguages() {

        const loads = Object.keys(config.languages).map(function (lang) {
            return fetchParagraphData(getLangConfig(lang));
        });

        await Promise.all(loads);

    }

    function getElapsedSeconds() {

        if (!testStartTime) {
            return 0;
        }

        return (Date.now() - testStartTime) / 1000;

    }

    function getElapsedMinutes() {

        const seconds = getElapsedSeconds();

        if (seconds <= 0) {
            return 0;
        }

        return seconds / 60;

    }

    function calculateGrossWPM() {

        const minutes = getElapsedMinutes();

        if (minutes <= 0) {
            return 0;
        }

        return Math.round((totalTyped / 5) / minutes);

    }

    function calculateNetWPM() {

        const minutes = getElapsedMinutes();

        if (minutes <= 0) {
            return 0;
        }

        return Math.max(0, Math.round(((correctTyped - wrongTyped) / 5) / minutes));

    }

    function calculateCPM() {

        const minutes = getElapsedMinutes();

        if (minutes <= 0) {
            return 0;
        }

        return Math.round(correctTyped / minutes);

    }

    function calculateAccuracy() {

        if (totalTyped <= 0) {
            return 100;
        }

        return (correctTyped / totalTyped) * 100;

    }

    function updateStats() {

        const accuracy = calculateAccuracy();
        const net = calculateNetWPM();
        const gross = calculateGrossWPM();
        const cpm = calculateCPM();

        if (netWpmElement) {
            netWpmElement.innerText = net;
        }

        if (grossWpmElement) {
            grossWpmElement.innerText = gross;
        }

        if (liveWpmElement) {
            liveWpmElement.innerText = net;
        }

        if (accuracyElement) {
            accuracyElement.innerText = accuracy.toFixed(1) + "%";
        }

        if (errorsElement) {
            errorsElement.innerText = wrongTyped;
        }

        if (cpmElement) {
            cpmElement.innerText = cpm;
        }

    }

    function renderParagraph() {

        const data = paragraphCache[activeLangConfig.languageKey];
        const languageData = data ? data[activeLangConfig.languageKey] : null;

        paragraphElement.className = activeLangConfig.paragraphClass || "";

        if (!languageData || !languageData[currentDifficulty] || !languageData[currentDifficulty].length) {
            paragraphElement.innerText = "No paragraph available for this level.";
            currentParagraph = "";
            return;
        }

        const list = languageData[currentDifficulty];
        currentParagraph = list[Math.floor(Math.random() * list.length)];

        paragraphElement.innerHTML = "";

        Array.from(currentParagraph).forEach(function (char) {

            const span = document.createElement("span");
            span.textContent = char;
            paragraphElement.appendChild(span);

        });

    }

    function resetCounters() {

        totalTyped = 0;
        correctTyped = 0;
        wrongTyped = 0;
        testStartTime = null;

    }

    function stopTimer() {

        clearInterval(timerInterval);
        timerInterval = null;
        timerStarted = false;

    }

    function resetTyping(reloadParagraph) {

        stopTimer();
        finished = false;
        timer = currentTimer;

        if (timerElement) {
            timerElement.innerText = timer;
        }

        typingInput.disabled = false;
        typingInput.value = "";
        resetCounters();

        if (reloadParagraph !== false) {
            renderParagraph();
        } else {
            highlightCharacters("");
        }

        updateStats();
        typingInput.focus();

    }

    function highlightCharacters(typedText) {

        const characters = paragraphElement.querySelectorAll("span");

        totalTyped = typedText.length;
        correctTyped = 0;
        wrongTyped = 0;

        characters.forEach(function (span) {
            span.className = "";
        });

        for (let i = 0; i < typedText.length; i++) {

            if (!characters[i]) {
                break;
            }

            if (typedText[i] === currentParagraph[i]) {
                characters[i].classList.add("correct");
                correctTyped++;
            } else {
                characters[i].classList.add("wrong");
                wrongTyped++;
            }

        }

        if (characters[typedText.length]) {
            characters[typedText.length].classList.add("current");
        }

    }

    function checkTyping() {

        if (finished || !currentParagraph) {
            return;
        }

        highlightCharacters(typingInput.value);
        updateStats();

        if (typingInput.value.length >= currentParagraph.length) {
            finishTest();
        }

    }

    function startTimer() {

        if (timerStarted || finished) {
            return;
        }

        timerStarted = true;
        testStartTime = Date.now();

        clearInterval(timerInterval);

        timerInterval = setInterval(function () {

            if (timer <= 0) {
                stopTimer();
                finishTest();
                return;
            }

            timer--;
            timerElement.innerText = timer;
            updateStats();

        }, 1000);

    }

    function buildResultPayload() {

        const minutes = Math.max(getElapsedMinutes(), 1 / 60);
        const accuracy = calculateAccuracy();

        return {
            language: activeLangConfig.saveLanguage,
            difficulty: currentDifficulty.charAt(0).toUpperCase() + currentDifficulty.slice(1),
            duration: currentTimer,
            gross_wpm: Math.max(0, Math.round((totalTyped / 5) / minutes)),
            net_wpm: Math.max(0, Math.round(((correctTyped - wrongTyped) / 5) / minutes)),
            cpm: Math.round(correctTyped / minutes),
            accuracy: Number(accuracy.toFixed(2)),
            errors: wrongTyped
        };

    }

    async function saveResult() {

        const payload = buildResultPayload();

        try {

            const response = await fetch(config.saveResultUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "same-origin",
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.message || "Result save failed");
            }

            window.location.href = config.redirectUrl;

        } catch (error) {

            console.error(error);
            alert(error.message || "Result save failed");

        }

    }

    function finishTest() {

        if (finished) {
            return;
        }

        finished = true;
        stopTimer();
        typingInput.disabled = true;
        updateStats();
        saveResult();

    }

    function setActiveDifficulty(level) {

        currentDifficulty = level;

        document.querySelectorAll(".difficulty-btn").forEach(function (btn) {
            btn.classList.toggle("active", btn.dataset.level === level);
        });

        resetTyping();

    }

    function setActiveTimer(seconds) {

        stopTimer();
        finished = false;
        currentTimer = seconds;
        timer = seconds;
        timerElement.innerText = timer;
        typingInput.disabled = false;

        document.querySelectorAll(".timer-btn").forEach(function (btn) {
            btn.classList.toggle("active", Number(btn.dataset.seconds) === seconds);
        });

        resetTyping();

    }

    async function setActiveLanguage(lang) {

        if (!config.languages[lang]) {
            return;
        }

        activeLanguage = lang;
        activeLangConfig = getLangConfig(lang);

        document.querySelectorAll(".language-btn").forEach(function (btn) {
            btn.classList.toggle("active", btn.dataset.lang === lang);
        });

        if (pageTitleElement) {
            pageTitleElement.textContent = activeLangConfig.title;
        }

        if (!paragraphCache[activeLangConfig.languageKey]) {
            await fetchParagraphData(activeLangConfig);
        }

        resetTyping();

    }

    function bindControls() {

        document.querySelectorAll(".difficulty-btn").forEach(function (btn) {
            btn.addEventListener("click", function () {
                setActiveDifficulty(btn.dataset.level);
            });
        });

        document.querySelectorAll(".timer-btn").forEach(function (btn) {
            btn.addEventListener("click", function () {
                setActiveTimer(Number(btn.dataset.seconds));
            });
        });

        document.querySelectorAll(".language-btn").forEach(function (btn) {
            btn.addEventListener("click", function () {
                setActiveLanguage(btn.dataset.lang);
            });
        });

        const restartBtn = document.getElementById("restartBtn");

        if (restartBtn) {
            restartBtn.addEventListener("click", function () {
                resetTyping();
            });
        }

    }

    typingInput.addEventListener("input", function () {

        if (!timerStarted && !finished) {
            startTimer();
        }

        checkTyping();

    });

    typingInput.addEventListener("paste", function (e) { e.preventDefault(); });
    typingInput.addEventListener("copy", function (e) { e.preventDefault(); });
    typingInput.addEventListener("cut", function (e) { e.preventDefault(); });

    typingInput.addEventListener("keydown", function (e) {

        if (e.key === "Enter") {
            e.preventDefault();
        }

    });

    document.addEventListener("keydown", function (e) {

        if (e.ctrlKey && e.key === "r") {
            e.preventDefault();
            resetTyping();
        }

        if (e.key === "Escape") {
            resetTyping();
        }

    });

    document.body.addEventListener("click", function () {
        typingInput.focus();
    });

    window.changeDifficulty = setActiveDifficulty;
    window.changeTimer = setActiveTimer;
    window.changeLanguage = setActiveLanguage;
    window.restartTest = function () { resetTyping(); };

    async function init() {

        bindControls();

        try {
            await preloadLanguages();
        } catch (error) {
            console.error(error);
            paragraphElement.innerText = "Unable to load typing paragraphs.";
            return;
        }

        await setActiveLanguage(config.defaultLanguage);
        typingInput.focus();

    }

    init();

})();
