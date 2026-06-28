document.addEventListener("DOMContentLoaded", function () {

    const config = window.PARAGRAPH_ADMIN;

    if (!config) {
        return;
    }

    const difficultySelect = document.getElementById("difficultySelect");
    const newParagraph = document.getElementById("newParagraph");
    const addBtn = document.getElementById("addParagraphBtn");
    const listEl = document.getElementById("paragraphList");

    let paragraphs = config.initialData || {};

    function currentDifficulty() {
        return difficultySelect.value;
    }

    function renderList() {

        const level = currentDifficulty();
        const items = paragraphs[level] || [];

        listEl.innerHTML = "";

        if (!items.length) {
            listEl.innerHTML = '<p class="text-muted">No paragraphs for this difficulty.</p>';
            return;
        }

        items.forEach(function (text, index) {

            const card = document.createElement("div");
            card.className = "admin-paragraph-card";

            card.innerHTML =
                '<p class="mb-3">' + escapeHtml(text) + '</p>' +
                '<button class="btn btn-sm btn-danger" data-index="' + index + '">Delete</button>';

            card.querySelector("button").addEventListener("click", function () {
                deleteParagraph(index);
            });

            listEl.appendChild(card);

        });

    }

    function escapeHtml(text) {

        const div = document.createElement("div");
        div.innerText = text;
        return div.innerHTML;

    }

    async function saveParagraph(action, extra) {

        const payload = Object.assign({
            language: config.language,
            difficulty: currentDifficulty(),
            action: action
        }, extra || {});

        const response = await fetch("/admin/paragraphs/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!data.success) {
            alert(data.message || "Save failed");
            return false;
        }

        paragraphs = data.paragraphs;
        renderList();
        return true;

    }

    async function addParagraph() {

        const content = newParagraph.value.trim();

        if (!content) {
            alert("Enter paragraph text");
            return;
        }

        const ok = await saveParagraph("add", { content: content });

        if (ok) {
            newParagraph.value = "";
        }

    }

    async function deleteParagraph(index) {

        if (!confirm("Delete this paragraph?")) {
            return;
        }

        await saveParagraph("delete", { index: index });

    }

    addBtn.addEventListener("click", addParagraph);
    difficultySelect.addEventListener("change", renderList);

    renderList();

});
