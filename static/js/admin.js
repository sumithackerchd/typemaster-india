document.addEventListener("DOMContentLoaded", function () {

    const config = window.PARAGRAPH_ADMIN;
    if (!config) {
        return;
    }

    const urls = config.urls || {};
    const SAVE_URL = urls.save || "/admin/paragraphs/save";
    const IMPORT_URL = urls.import || "/admin/paragraphs/import";
    const CLEAR_URL = urls.clear || "/admin/paragraphs/clear";
    const PAGE_SIZE = 8;

    const difficultySelect = document.getElementById("difficultySelect");
    const newParagraph = document.getElementById("newParagraph");
    const addBtn = document.getElementById("addParagraphBtn");
    const listEl = document.getElementById("paragraphList");
    const searchEl = document.getElementById("paragraphSearch");
    const pagerEl = document.getElementById("paragraphPager");
    const countEl = document.getElementById("paragraphCount");

    const importFile = document.getElementById("importFile");
    const importDrop = document.getElementById("importDrop");
    const importStatus = document.getElementById("importStatus");
    const importProgress = document.getElementById("importProgress");

    let paragraphs = config.initialData || {};
    let currentPage = 1;

    function currentDifficulty() {
        return difficultySelect ? difficultySelect.value : "medium";
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.innerText = text;
        return div.innerHTML;
    }

    function filteredItems() {
        const level = currentDifficulty();
        const items = paragraphs[level] || [];
        const query = (searchEl ? searchEl.value : "").trim().toLowerCase();
        const mapped = items.map(function (text, index) {
            return { text: text, index: index };
        });
        if (!query) {
            return mapped;
        }
        return mapped.filter(function (item) {
            return item.text.toLowerCase().indexOf(query) !== -1;
        });
    }

    function updateCount() {
        if (!countEl) return;
        const level = currentDifficulty();
        const total = (paragraphs[level] || []).length;
        countEl.textContent = total + " " + level + " passage" + (total === 1 ? "" : "s");
    }

    function renderPager(totalPages) {
        if (!pagerEl) return;
        pagerEl.innerHTML = "";
        if (totalPages <= 1) return;

        function pageBtn(label, page, disabled, active) {
            const btn = document.createElement("button");
            btn.type = "button";
            if (active) btn.className = "active";
            btn.textContent = label;
            btn.disabled = disabled;
            if (!disabled && !active) {
                btn.addEventListener("click", function () {
                    currentPage = page;
                    renderList();
                    listEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
                });
            }
            return btn;
        }
        pagerEl.appendChild(pageBtn("‹", currentPage - 1, currentPage === 1, false));
        for (let p = 1; p <= totalPages; p += 1) {
            pagerEl.appendChild(pageBtn(String(p), p, false, p === currentPage));
        }
        pagerEl.appendChild(pageBtn("›", currentPage + 1, currentPage === totalPages, false));
    }

    function renderList() {
        updateCount();
        const items = filteredItems();
        const totalPages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
        if (currentPage > totalPages) currentPage = totalPages;

        listEl.innerHTML = "";

        if (!items.length) {
            listEl.innerHTML =
                '<div class="pm-empty"><i class="fa-regular fa-folder-open"></i>' +
                "<p>No paragraphs match this view.</p></div>";
            renderPager(1);
            return;
        }

        const level = currentDifficulty();
        const start = (currentPage - 1) * PAGE_SIZE;
        const pageItems = items.slice(start, start + PAGE_SIZE);

        pageItems.forEach(function (item) {
            const card = document.createElement("div");
            card.className = "admin-paragraph-card";
            const number = item.index + 1;
            const words = item.text.trim().split(/\s+/).length;

            card.innerHTML =
                '<div class="pc-head">' +
                '<span class="pc-badge ' + level + '">#' + number + " · " + level + "</span>" +
                '<span class="pc-actions">' +
                '<button class="edit" title="Edit"><i class="fa-solid fa-pen"></i></button>' +
                '<button class="del" title="Delete"><i class="fa-solid fa-trash"></i></button>' +
                "</span></div>" +
                '<p class="pc-text">' + escapeHtml(item.text) + "</p>" +
                '<div class="pc-head" style="margin-top:10px;margin-bottom:0">' +
                '<small class="text-muted-2">' + item.text.length + " chars · " + words + " words</small>" +
                "</div>";

            card.querySelector(".del").addEventListener("click", function () {
                deleteParagraph(item.index);
            });
            card.querySelector(".edit").addEventListener("click", function () {
                startEdit(card, item);
            });
            listEl.appendChild(card);
        });

        renderPager(totalPages);
    }

    function startEdit(card, item) {
        card.innerHTML =
            '<textarea class="form-control mb-3 apc-editor" rows="4"></textarea>' +
            '<div class="pc-actions">' +
            '<button class="pm-btn primary apc-save"><i class="fa-solid fa-check"></i> Save</button>' +
            '<button class="pm-btn apc-cancel">Cancel</button>' +
            "</div>";
        const editor = card.querySelector(".apc-editor");
        editor.value = item.text;
        editor.focus();
        card.querySelector(".apc-cancel").addEventListener("click", renderList);
        card.querySelector(".apc-save").addEventListener("click", function () {
            const value = editor.value.trim();
            if (!value) {
                alert("Paragraph cannot be empty.");
                return;
            }
            saveParagraph("edit", { index: item.index, content: value });
        });
    }

    async function saveParagraph(action, extra) {
        const payload = Object.assign({
            language: config.language,
            difficulty: currentDifficulty(),
            action: action
        }, extra || {});

        const response = await fetch(SAVE_URL, {
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
            newParagraph.focus();
            return;
        }
        const ok = await saveParagraph("add", { content: content });
        if (ok) {
            newParagraph.value = "";
            setStatus('<i class="fa-solid fa-circle-check me-2"></i>Paragraph added.', "ok");
        }
    }

    async function deleteParagraph(index) {
        if (!confirm("Delete this paragraph?")) return;
        await saveParagraph("delete", { index: index });
    }

    async function clearDifficulty(level) {
        level = level || currentDifficulty();
        if (!confirm('Delete ALL "' + level + '" paragraphs? This cannot be undone.')) return;
        const response = await fetch(CLEAR_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ language: config.language, difficulty: level })
        });
        const data = await response.json();
        if (!data.success) {
            alert(data.message || "Could not clear paragraphs.");
            return;
        }
        paragraphs = data.paragraphs;
        currentPage = 1;
        renderList();
        setStatus('<i class="fa-solid fa-broom me-2"></i>Cleared all ' + level + " paragraphs.", "ok");
    }

    function setStatus(message, kind) {
        if (!importStatus) return;
        importStatus.hidden = false;
        importStatus.className = "cp-status " + (kind || "info");
        importStatus.innerHTML = message;
    }

    function setProgress(pct) {
        if (!importProgress) return;
        const bar = importProgress.firstElementChild;
        if (pct === null) {
            importProgress.hidden = true;
            if (bar) bar.style.width = "0%";
            return;
        }
        importProgress.hidden = false;
        if (bar) bar.style.width = Math.max(4, Math.min(100, pct)) + "%";
    }

    // XHR-based import so we can show real upload progress.
    function importFileUpload(file) {
        if (!file) return;
        setStatus('<i class="fa-solid fa-spinner fa-spin me-2"></i>Uploading "' +
            escapeHtml(file.name) + '"...', "info");
        setProgress(0);

        const form = new FormData();
        form.append("file", file);
        form.append("language", config.language);
        form.append("difficulty", currentDifficulty());

        const xhr = new XMLHttpRequest();
        xhr.open("POST", IMPORT_URL, true);

        xhr.upload.onprogress = function (e) {
            if (e.lengthComputable) {
                setProgress((e.loaded / e.total) * 100);
            }
        };
        xhr.upload.onload = function () {
            setStatus('<i class="fa-solid fa-spinner fa-spin me-2"></i>Processing &amp; extracting paragraphs...', "info");
            setProgress(100);
        };
        xhr.onload = function () {
            setProgress(null);
            let data;
            try { data = JSON.parse(xhr.responseText); } catch (e) { data = null; }
            if (!data || !data.success) {
                setStatus('<i class="fa-solid fa-triangle-exclamation me-2"></i>' +
                    escapeHtml((data && data.message) || "Import failed."), "err");
                return;
            }
            paragraphs = data.paragraphs;
            currentPage = 1;
            renderList();
            let msg = '<i class="fa-solid fa-circle-check me-2"></i>Added ' + data.added +
                " paragraph(s) to " + currentDifficulty() + ".";
            if (data.duplicates) msg += " Skipped " + data.duplicates + " duplicate(s).";
            setStatus(msg, "ok");
        };
        xhr.onerror = function () {
            setProgress(null);
            setStatus('<i class="fa-solid fa-triangle-exclamation me-2"></i>Upload error. Please try again.', "err");
        };
        xhr.send(form);
    }

    // ---------------- Events ----------------
    if (addBtn) addBtn.addEventListener("click", addParagraph);
    if (difficultySelect) {
        difficultySelect.addEventListener("change", function () {
            currentPage = 1;
            renderList();
        });
    }
    if (searchEl) {
        let t;
        searchEl.addEventListener("input", function () {
            clearTimeout(t);
            t = setTimeout(function () { currentPage = 1; renderList(); }, 180);
        });
    }

    // Per-difficulty clear buttons: <button data-clear-difficulty="easy">
    document.querySelectorAll("[data-clear-difficulty]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            clearDifficulty(btn.getAttribute("data-clear-difficulty"));
        });
    });

    // Typed import triggers: <button data-import-accept=".pdf">
    document.querySelectorAll("[data-import-accept]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            if (!importFile) return;
            importFile.setAttribute("accept", btn.getAttribute("data-import-accept"));
            importFile.click();
        });
    });

    // Jump to the add form.
    document.querySelectorAll("[data-focus-form]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            if (newParagraph) {
                newParagraph.scrollIntoView({ behavior: "smooth", block: "center" });
                newParagraph.focus();
            }
        });
    });

    if (importDrop && importFile) {
        importDrop.addEventListener("click", function () {
            importFile.removeAttribute("accept");
            importFile.click();
        });
        importFile.addEventListener("change", function () {
            if (importFile.files.length) {
                importFileUpload(importFile.files[0]);
                importFile.value = "";
            }
        });
        ["dragenter", "dragover"].forEach(function (evt) {
            importDrop.addEventListener(evt, function (e) {
                e.preventDefault();
                importDrop.classList.add("dragover");
            });
        });
        ["dragleave", "drop"].forEach(function (evt) {
            importDrop.addEventListener(evt, function (e) {
                e.preventDefault();
                importDrop.classList.remove("dragover");
            });
        });
        importDrop.addEventListener("drop", function (e) {
            if (e.dataTransfer.files.length) {
                importFileUpload(e.dataTransfer.files[0]);
            }
        });
    }

    renderList();
});
