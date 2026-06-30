/* Mock Test setup screen — selection state + launch */
(function () {
    "use strict";

    const selection = {
        language: "english",
        mode: "practice",
        category: "random_paragraph",
        difficulty: "easy",
        duration: "60",
    };

    const labels = {};

    function initGroup(group) {
        const container = document.querySelector('[data-group="' + group + '"]');
        if (!container) return;

        const cards = container.querySelectorAll(".opt-card");

        cards.forEach(function (card) {
            if (card.classList.contains("selected")) {
                selection[group] = card.dataset.value;
                labels[group] = cardLabel(card);
            }

            card.addEventListener("click", function () {
                cards.forEach(function (c) { c.classList.remove("selected"); });
                card.classList.add("selected");
                selection[group] = card.dataset.value;
                labels[group] = cardLabel(card);

                if (group === "duration") {
                    toggleCustom(card.dataset.value === "custom");
                }

                renderSummary();
            });
        });
    }

    function cardLabel(card) {
        const t = card.querySelector(".opt-title");
        return t ? t.textContent.trim() : card.dataset.value;
    }

    function toggleCustom(show) {
        const box = document.getElementById("customDuration");
        if (box) box.classList.toggle("show", show);
    }

    function resolvedDuration() {
        if (selection.duration === "custom") {
            const input = document.getElementById("customSeconds");
            let val = parseInt(input && input.value, 10);
            if (isNaN(val)) val = 60;
            if (val < 10) val = 10;
            if (val > 3600) val = 3600;
            return val;
        }
        return parseInt(selection.duration, 10) || 60;
    }

    function durationLabel() {
        const secs = resolvedDuration();
        if (secs % 60 === 0) {
            const m = secs / 60;
            return m === 1 ? "1 Minute" : m + " Minutes";
        }
        return secs + " Seconds";
    }

    function renderSummary() {
        const summary = document.getElementById("mockSummary");
        if (!summary) return;

        const items = [
            { icon: "fa-language", text: labels.language },
            { icon: "fa-file-pen", text: labels.mode },
            { icon: "fa-layer-group", text: labels.category },
            { icon: "fa-signal", text: labels.difficulty },
            { icon: "fa-clock", text: durationLabel() },
        ];

        summary.innerHTML = items.map(function (it) {
            return '<span class="pill"><i class="fa-solid ' + it.icon + '"></i>' + it.text + "</span>";
        }).join("");
    }

    function start() {
        const params = new URLSearchParams({
            language: selection.language,
            mode: selection.mode,
            category: selection.category,
            difficulty: selection.difficulty,
            duration: String(resolvedDuration()),
        });
        window.location.href = window.MOCK_RUN_URL + "?" + params.toString();
    }

    ["language", "mode", "category", "difficulty", "duration"].forEach(initGroup);
    renderSummary();

    const customInput = document.getElementById("customSeconds");
    if (customInput) customInput.addEventListener("input", renderSummary);

    const startBtn = document.getElementById("startMockBtn");
    if (startBtn) startBtn.addEventListener("click", start);

})();
