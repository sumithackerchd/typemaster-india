/**
 * TypeMaster India — Unified Typing Engine
 * Supports English + Hindi (Mangal Unicode) via TYPING_CONFIG
 *
 * Features:
 *  - Pause / Resume / Submit / Restart controls (shared across all modes)
 *  - Automatic session recovery (paragraph, typed text, caret, timer)
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
    const typingViewport = document.getElementById("typingViewport");
    const typingInput = document.getElementById("typingInput");
    const typingWrapper = document.getElementById("typingWrapper");

    // Remember the line offset (relative to #paragraph) we last scrolled to,
    // so we only re-translate when the caret actually moves to a new line.
    let lastLineTop = -1;

    // Focus the input WITHOUT letting the browser scroll the page to it.
    function focusInput() {
        try {
            typingInput.focus({ preventScroll: true });
        } catch (e) {
            typingInput.focus();
        }
    }

    // Keep the active character's line visible by translating the paragraph
    // UP inside its fixed-height viewport. The browser window never moves —
    // only the text inside the container does (Monkeytype / TypingBaba style).
    function scrollToCaret() {

        if (!typingViewport) {
            return;
        }

        const caretIndex = prevCurrentIndex >= 0 ? prevCurrentIndex : 0;
        const caret = paragraphSpans[Math.min(caretIndex, paragraphSpans.length - 1)];

        if (!caret) {
            return;
        }

        const lineTop = caret.offsetTop;

        if (lineTop === lastLineTop) {
            return;
        }

        lastLineTop = lineTop;

        const lineHeight = caret.offsetHeight || 0;
        const viewportHeight = typingViewport.clientHeight || 0;

        let offset = lineTop - Math.max(0, (viewportHeight - lineHeight) / 2);

        if (offset < 0) {
            offset = 0;
        }

        paragraphElement.style.transform = "translateY(" + (-offset) + "px)";

    }
    const timerElement = document.getElementById("timer");
    const pageTitleElement = document.getElementById("typingTitle");
    const netWpmElement = document.getElementById("netWpm");
    const grossWpmElement = document.getElementById("grossWpm");
    const liveWpmElement = document.getElementById("liveWpm");
    const accuracyElement = document.getElementById("accuracy");
    const errorsElement = document.getElementById("errors");
    const cpmElement = document.getElementById("cpm");

    const pauseBtn = document.getElementById("pauseBtn");
    const submitBtn = document.getElementById("submitBtn");
    const restartBtn = document.getElementById("restartBtn");

    if (!paragraphElement || !typingInput) {
        return;
    }

    const paragraphCache = {};
    let activeLanguage = config.defaultLanguage;
    let activeLangConfig = config.languages[activeLanguage] || config.languages.english;

    let currentDifficulty = config.initialDifficulty || "easy";
    let currentTimer = config.initialTimer || 60;
    let timer = currentTimer;
    let timerStarted = false;
    let timerInterval = null;
    let testStartTime = null;       // start of the *current running* segment
    let pausedElapsedMs = 0;        // accumulated elapsed time across segments
    let paused = false;
    let restoring = false;
    let totalTyped = 0;
    let correctTyped = 0;
    let wrongTyped = 0;
    let finished = false;
    let currentParagraph = "";
    let paragraphSpans = [];
    let prevTypedLen = 0;
    let prevCurrentIndex = -1;

    // ------------------------------------------------------------------
    // Session persistence key — unique per page (typing / hindi / mock /
    // custom all live on distinct paths, so the pathname is enough).
    // ------------------------------------------------------------------
    const SESSION_KEY = "tm-session:" + window.location.pathname;
    const SESSION_TTL_MS = 1000 * 60 * 60 * 6; // 6 hours

    function getLangConfig(lang) {

        return config.languages[lang] || config.languages.english;

    }

    function targetWordCount(seconds) {

        const secs = Number(seconds) || 60;
        return Math.max(60, Math.ceil((secs / 60) * 280));

    }

    function shuffleCopy(arr) {

        const copy = arr.slice();

        for (let i = copy.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            const tmp = copy[i];
            copy[i] = copy[j];
            copy[j] = tmp;
        }

        return copy;

    }

    function buildText(list, seconds) {

        if (!list || !list.length) {
            return "";
        }

        const target = targetWordCount(seconds);
        const parts = [];
        let words = 0;
        let pool = shuffleCopy(list);
        let idx = 0;

        let guard = 0;
        while (words < target && guard < 10000) {
            guard++;

            if (idx >= pool.length) {
                pool = shuffleCopy(list);
                idx = 0;
            }

            const piece = (pool[idx] || "").trim();
            idx++;

            if (!piece) {
                continue;
            }

            parts.push(piece);
            words += piece.split(/\s+/).length;
        }

        return parts.join(" ");

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

        let ms = pausedElapsedMs;

        if (testStartTime && !paused) {
            ms += (Date.now() - testStartTime);
        }

        return ms / 1000;

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

    // Render the paragraph. When ``fixedText`` is supplied (session restore)
    // we reuse the exact same text instead of building a fresh random one.
    function renderParagraph(fixedText) {

        paragraphElement.className = activeLangConfig.paragraphClass || "";

        if (typeof fixedText === "string" && fixedText.length) {
            currentParagraph = fixedText;
        } else {
            const data = paragraphCache[activeLangConfig.languageKey];
            const languageData = data ? data[activeLangConfig.languageKey] : null;

            if (!languageData || !languageData[currentDifficulty] || !languageData[currentDifficulty].length) {
                paragraphElement.innerText = "No paragraph available for this level.";
                currentParagraph = "";
                paragraphSpans = [];
                return;
            }

            const list = languageData[currentDifficulty];
            currentParagraph = buildText(list, currentTimer);
        }

        paragraphElement.innerHTML = "";
        paragraphElement.style.transform = "translateY(0)";
        lastLineTop = -1;
        prevTypedLen = 0;
        prevCurrentIndex = -1;

        const fragment = document.createDocumentFragment();
        const chars = Array.from(currentParagraph);

        chars.forEach(function (char) {
            const span = document.createElement("span");
            span.textContent = char;
            fragment.appendChild(span);
        });

        paragraphElement.appendChild(fragment);
        paragraphSpans = paragraphElement.querySelectorAll("span");

        if (paragraphSpans[0]) {
            paragraphSpans[0].classList.add("current");
            prevCurrentIndex = 0;
        }

    }

    function resetCounters() {

        totalTyped = 0;
        correctTyped = 0;
        wrongTyped = 0;
        testStartTime = null;
        pausedElapsedMs = 0;

    }

    function stopTimer() {

        clearInterval(timerInterval);
        timerInterval = null;
        timerStarted = false;

    }

    function resetTyping(reloadParagraph) {

        stopTimer();
        finished = false;
        paused = false;
        timer = currentTimer;

        if (timerElement) {
            timerElement.innerText = timer;
        }

        typingInput.disabled = false;
        typingInput.value = "";
        resetCounters();
        clearSession();
        hidePausedOverlay();
        setControlsRunning();

        if (reloadParagraph !== false) {
            renderParagraph();
        } else {
            highlightCharacters("");
        }

        updateStats();
        focusInput();

    }

    function highlightCharacters(typedText) {

        const characters = paragraphSpans;

        totalTyped = typedText.length;
        correctTyped = 0;
        wrongTyped = 0;

        const scanLen = Math.max(typedText.length, prevTypedLen);

        for (let i = 0; i < scanLen; i++) {

            const span = characters[i];

            if (!span) {
                break;
            }

            if (i < typedText.length) {
                if (typedText[i] === currentParagraph[i]) {
                    span.className = "correct";
                } else {
                    span.className = "wrong";
                }
            } else {
                span.className = "";
            }

        }

        for (let i = 0; i < typedText.length; i++) {
            if (!characters[i]) {
                break;
            }
            if (typedText[i] === currentParagraph[i]) {
                correctTyped++;
            } else {
                wrongTyped++;
            }
        }

        if (prevCurrentIndex >= 0 && characters[prevCurrentIndex] &&
            prevCurrentIndex >= typedText.length) {
            characters[prevCurrentIndex].classList.remove("current");
        }

        if (characters[typedText.length]) {
            characters[typedText.length].classList.add("current");
            prevCurrentIndex = typedText.length;
        } else {
            prevCurrentIndex = -1;
        }

        prevTypedLen = typedText.length;

    }

    function checkTyping() {

        if (finished || paused || !currentParagraph) {
            return;
        }

        highlightCharacters(typingInput.value);
        scrollToCaret();
        updateStats();
        persistSession();

        if (typingInput.value.length >= currentParagraph.length) {
            finishTest();
        }

    }

    function tick() {

        if (timer <= 0) {
            stopTimer();
            finishTest();
            return;
        }

        timer--;
        if (timerElement) {
            timerElement.innerText = timer;
        }
        updateStats();
        persistSession();

    }

    function startTimer() {

        if (timerStarted || finished) {
            return;
        }

        timerStarted = true;
        paused = false;
        testStartTime = Date.now();

        clearInterval(timerInterval);
        timerInterval = setInterval(tick, 1000);

    }

    // ------------------------------------------------------------------
    // Pause / Resume / Submit
    // ------------------------------------------------------------------
    function pauseTest() {

        if (!timerStarted || finished || paused) {
            return;
        }

        paused = true;

        if (testStartTime) {
            pausedElapsedMs += (Date.now() - testStartTime);
            testStartTime = null;
        }

        clearInterval(timerInterval);
        timerInterval = null;
        typingInput.disabled = true;

        showPausedOverlay("Paused");
        setControlsPaused();
        persistSession();

    }

    function resumeTest() {

        if (!paused || finished) {
            return;
        }

        paused = false;
        testStartTime = Date.now();
        typingInput.disabled = false;

        clearInterval(timerInterval);
        timerInterval = setInterval(tick, 1000);

        hidePausedOverlay();
        setControlsRunning();
        focusInput();
        persistSession();

    }

    function togglePause() {

        if (paused) {
            resumeTest();
        } else {
            pauseTest();
        }

    }

    // Submit calculates the current result immediately.
    function submitTest() {

        if (finished) {
            return;
        }

        if (!timerStarted && totalTyped === 0) {
            // Nothing typed yet — nothing to submit.
            return;
        }

        finishTest();

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

        // Freeze accumulated time before saving.
        if (testStartTime && !paused) {
            pausedElapsedMs += (Date.now() - testStartTime);
            testStartTime = null;
        }

        finished = true;
        paused = false;
        stopTimer();
        typingInput.disabled = true;
        hidePausedOverlay();
        updateStats();
        clearSession();
        saveResult();

    }

    // ------------------------------------------------------------------
    // Paused overlay + control button states
    // ------------------------------------------------------------------
    let overlayEl = null;

    function ensureOverlay() {

        if (overlayEl || !typingWrapper) {
            return overlayEl;
        }

        overlayEl = document.createElement("div");
        overlayEl.className = "typing-pause-overlay";
        overlayEl.setAttribute("role", "status");
        overlayEl.innerHTML =
            '<div class="tpo-card">' +
            '<div class="tpo-icon"><i class="fa-solid fa-pause"></i></div>' +
            '<h3 class="tpo-title">Paused</h3>' +
            '<p class="tpo-text">Your progress and timer are frozen.</p>' +
            '<button type="button" class="tpo-resume"><i class="fa-solid fa-play me-1"></i> Resume</button>' +
            "</div>";

        const card = typingWrapper.querySelector(".typing-card") || typingWrapper;
        card.style.position = card.style.position || "relative";
        card.appendChild(overlayEl);

        overlayEl.querySelector(".tpo-resume").addEventListener("click", resumeTest);

        return overlayEl;

    }

    function showPausedOverlay(title) {

        ensureOverlay();

        if (!overlayEl) {
            return;
        }

        const t = overlayEl.querySelector(".tpo-title");
        if (t && title) {
            t.textContent = title;
        }

        overlayEl.classList.add("is-visible");

    }

    function hidePausedOverlay() {

        if (overlayEl) {
            overlayEl.classList.remove("is-visible");
        }

    }

    function setControlsPaused() {

        if (pauseBtn) {
            pauseBtn.innerHTML = '<i class="fa-solid fa-play"></i> Resume';
            pauseBtn.classList.add("is-active");
        }

    }

    function setControlsRunning() {

        if (pauseBtn) {
            pauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i> Pause';
            pauseBtn.classList.remove("is-active");
        }

    }

    // ------------------------------------------------------------------
    // Session persistence
    // ------------------------------------------------------------------
    function persistSession() {

        if (restoring || finished || !timerStarted || !currentParagraph) {
            return;
        }

        try {
            const state = {
                v: 1,
                path: window.location.pathname,
                lang: activeLanguage,
                difficulty: currentDifficulty,
                timer: currentTimer,
                remaining: timer,
                paragraph: currentParagraph,
                typed: typingInput.value,
                elapsedMs: getElapsedSeconds() * 1000,
                savedAt: Date.now()
            };
            localStorage.setItem(SESSION_KEY, JSON.stringify(state));
        } catch (e) {
            /* storage full / unavailable — ignore */
        }

    }

    function clearSession() {

        try {
            localStorage.removeItem(SESSION_KEY);
        } catch (e) { /* ignore */ }

    }

    function loadSavedState() {

        try {
            const raw = localStorage.getItem(SESSION_KEY);
            if (!raw) {
                return null;
            }

            const state = JSON.parse(raw);

            if (!state || state.path !== window.location.pathname || !state.paragraph) {
                return null;
            }

            if (!state.typed) {
                // Nothing meaningful typed yet.
                clearSession();
                return null;
            }

            if (Date.now() - (state.savedAt || 0) > SESSION_TTL_MS) {
                clearSession();
                return null;
            }

            if (!config.languages[state.lang]) {
                return null;
            }

            return state;

        } catch (e) {
            return null;
        }

    }

    function updateToggleUI() {

        document.querySelectorAll(".difficulty-btn").forEach(function (btn) {
            btn.classList.toggle("active", btn.dataset.level === currentDifficulty);
        });

        document.querySelectorAll(".timer-btn").forEach(function (btn) {
            btn.classList.toggle("active", Number(btn.dataset.seconds) === currentTimer);
        });

        document.querySelectorAll(".language-btn").forEach(function (btn) {
            btn.classList.toggle("active", btn.dataset.lang === activeLanguage);
        });

    }

    function restoreState(state) {

        restoring = true;

        activeLanguage = state.lang;
        activeLangConfig = getLangConfig(state.lang);
        currentDifficulty = state.difficulty || currentDifficulty;
        currentTimer = state.timer || currentTimer;
        timer = typeof state.remaining === "number" ? state.remaining : currentTimer;

        if (pageTitleElement) {
            pageTitleElement.textContent = activeLangConfig.title;
        }

        if (timerElement) {
            timerElement.innerText = timer;
        }

        updateToggleUI();
        renderParagraph(state.paragraph);

        typingInput.value = state.typed || "";
        pausedElapsedMs = state.elapsedMs || 0;
        testStartTime = null;
        timerStarted = true;
        finished = false;

        highlightCharacters(typingInput.value);
        scrollToCaret();
        updateStats();

        // Restore into a paused state so no time is lost while the page was
        // closed; the user resumes when ready.
        paused = true;
        typingInput.disabled = true;
        showPausedOverlay("Session restored");
        setControlsPaused();

        restoring = false;

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
        paused = false;
        currentTimer = seconds;
        timer = seconds;
        if (timerElement) {
            timerElement.innerText = timer;
        }
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

        if (restartBtn) {
            restartBtn.addEventListener("click", function () {
                resetTyping();
            });
        }

        if (pauseBtn) {
            pauseBtn.addEventListener("click", togglePause);
        }

        if (submitBtn) {
            submitBtn.addEventListener("click", submitTest);
        }

    }

    typingInput.addEventListener("input", function () {

        if (paused) {
            // Ignore stray input while paused (input is disabled anyway).
            return;
        }

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

        if (e.ctrlKey && (e.key === "r" || e.key === "R")) {
            e.preventDefault();
            resetTyping();
            return;
        }

        // Esc toggles pause instead of a hard reset — safer for a live test.
        if (e.key === "Escape") {
            e.preventDefault();
            if (timerStarted && !finished) {
                togglePause();
            }
        }

    });

    // Persist right before the tab is hidden or closed so nothing is lost.
    window.addEventListener("beforeunload", function () {
        persistSession();
    });

    document.addEventListener("visibilitychange", function () {
        if (document.visibilityState === "hidden") {
            persistSession();
        }
    });

    document.body.addEventListener("click", function (e) {
        // Don't steal focus when interacting with the paused overlay button.
        if (paused) {
            return;
        }
        if (e.target && e.target.closest && e.target.closest("button, a, input, select, textarea, .toolbar")) {
            return;
        }
        focusInput();
    });

    window.changeDifficulty = setActiveDifficulty;
    window.changeTimer = setActiveTimer;
    window.changeLanguage = setActiveLanguage;
    window.restartTest = function () { resetTyping(); };
    window.pauseTest = pauseTest;
    window.resumeTest = resumeTest;
    window.submitTest = submitTest;

    async function init() {

        bindControls();
        setControlsRunning();

        try {
            await preloadLanguages();
        } catch (error) {
            console.error(error);
            paragraphElement.innerText = "Unable to load typing paragraphs.";
            return;
        }

        // Read any saved session BEFORE setActiveLanguage() runs, because
        // setActiveLanguage -> resetTyping -> clearSession() would wipe it.
        const saved = loadSavedState();

        await setActiveLanguage(config.defaultLanguage);

        // Attempt to recover an unfinished session for this page.
        if (saved) {
            restoreState(saved);
        } else {
            focusInput();
        }

    }

    init();

})();
