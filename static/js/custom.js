/**
 * Custom Practice — paste / upload / OCR, save & manage paragraphs.
 */
(function () {
    "use strict";

    var CFG = window.CUSTOM_PRACTICE;
    if (!CFG) { return; }

    var U = CFG.urls;

    // Elements
    var tabs = document.querySelectorAll(".cp-tab");
    var uploader = document.getElementById("cpUploader");
    var drop = document.getElementById("cpDrop");
    var dropLabel = document.getElementById("cpDropLabel");
    var dropHint = document.getElementById("cpDropHint");
    var fileInput = document.getElementById("cpFileInput");
    var ocrStatus = document.getElementById("cpOcrStatus");
    var statusEl = document.getElementById("cpStatus");

    var contentEl = document.getElementById("cpContent");
    var titleEl = document.getElementById("cpTitle");
    var languageEl = document.getElementById("cpLanguage");
    var difficultyEl = document.getElementById("cpDifficulty");
    var wordCountEl = document.getElementById("cpWordCount");

    var startBtn = document.getElementById("cpStartBtn");
    var saveBtn = document.getElementById("cpSaveBtn");
    var clearBtn = document.getElementById("cpClearBtn");

    var libTabs = document.querySelectorAll(".cp-lib-tab");
    var libraryEl = document.getElementById("cpLibrary");

    var currentSource = "paste";
    var libraryData = { saved: [], recent: [], favorites: [] };
    var currentView = "saved";

    // ---------------------------------------------------------------
    // Utilities
    // ---------------------------------------------------------------
    function escapeHtml(t) {
        var d = document.createElement("div");
        d.innerText = t == null ? "" : t;
        return d.innerHTML;
    }

    function countWords(t) {
        t = (t || "").trim();
        return t ? t.split(/\s+/).length : 0;
    }

    function updateWordCount() {
        wordCountEl.innerText = countWords(contentEl.value);
    }

    function showStatus(msg, kind) {
        if (!statusEl) { return; }
        statusEl.hidden = false;
        statusEl.className = "cp-status " + (kind || "info");
        statusEl.innerHTML = msg;
    }

    function clearStatus() {
        if (statusEl) { statusEl.hidden = true; statusEl.innerHTML = ""; }
    }

    function toast(msg, kind) {
        // lightweight inline toast reusing the status region
        showStatus(msg, kind);
        if (kind === "success") {
            setTimeout(clearStatus, 2500);
        }
    }

    // ---------------------------------------------------------------
    // Source tabs
    // ---------------------------------------------------------------
    function setSource(source) {
        currentSource = source;
        tabs.forEach(function (t) {
            t.classList.toggle("active", t.dataset.source === source);
        });

        if (source === "paste") {
            uploader.hidden = true;
            contentEl.focus();
        } else {
            uploader.hidden = false;
            clearStatus();
            if (source === "ocr") {
                dropLabel.innerText = "Click to choose an image or drag & drop";
                dropHint.innerText = "PNG, JPG, JPEG, WEBP";
                fileInput.accept = ".png,.jpg,.jpeg,.webp";
                // Always surface the OCR status (green when ready, guide when not).
                if (ocrStatus) { ocrStatus.hidden = false; }
            } else {
                dropLabel.innerText = "Click to choose a file or drag & drop";
                dropHint.innerText = "TXT, DOCX, PDF, CSV, XLSX, JSON";
                fileInput.accept = ".txt,.docx,.pdf,.csv,.xlsx,.xls,.json";
                if (ocrStatus) { ocrStatus.hidden = true; }
            }
        }
    }

    tabs.forEach(function (t) {
        t.addEventListener("click", function () { setSource(t.dataset.source); });
    });

    // ---------------------------------------------------------------
    // File upload + extraction
    // ---------------------------------------------------------------
    function handleFile(file) {
        if (!file) { return; }

        showStatus('<i class="fa-solid fa-spinner fa-spin"></i> Extracting text from <b>'
            + escapeHtml(file.name) + '</b>...', "info");

        var fd = new FormData();
        fd.append("file", file);
        fd.append("language", languageEl.value);

        fetch(U.extract, { method: "POST", body: fd, credentials: "same-origin" })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    showStatus('<i class="fa-solid fa-circle-exclamation"></i> '
                        + escapeHtml(data.message || "Could not read that file."), "error");
                    return;
                }
                contentEl.value = data.text || "";
                if (data.language) { languageEl.value = data.language; }
                updateWordCount();
                showStatus('<i class="fa-solid fa-circle-check"></i> Extracted '
                    + data.word_count + ' words. Review or edit below, then practice or save.',
                    "success");
                setTimeout(clearStatus, 3500);
            })
            .catch(function () {
                showStatus('<i class="fa-solid fa-circle-exclamation"></i> '
                    + 'Something went wrong reading that file.', "error");
            });
    }

    if (drop) {
        drop.addEventListener("click", function () { fileInput.click(); });
        drop.addEventListener("dragover", function (e) {
            e.preventDefault(); drop.classList.add("dragover");
        });
        drop.addEventListener("dragleave", function () { drop.classList.remove("dragover"); });
        drop.addEventListener("drop", function (e) {
            e.preventDefault();
            drop.classList.remove("dragover");
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", function () {
            if (fileInput.files && fileInput.files[0]) {
                handleFile(fileInput.files[0]);
                fileInput.value = "";
            }
        });
    }

    // ---------------------------------------------------------------
    // Start practice (ad-hoc / unsaved text)
    // ---------------------------------------------------------------
    function startPractice() {
        var content = contentEl.value.trim();
        if (countWords(content) < 3) {
            toast('<i class="fa-solid fa-circle-exclamation"></i> Enter at least a few words to practice.', "error");
            return;
        }
        fetch(U.start, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({ content: content, title: titleEl.value.trim() || "Custom Practice" })
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.success && data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    toast(escapeHtml(data.message || "Could not start practice."), "error");
                }
            });
    }

    // ---------------------------------------------------------------
    // Save paragraph
    // ---------------------------------------------------------------
    function savePara() {
        var content = contentEl.value.trim();
        if (countWords(content) < 3) {
            toast('<i class="fa-solid fa-circle-exclamation"></i> Enter at least a few words to save.', "error");
            return;
        }
        fetch(U.save, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({
                content: content,
                title: titleEl.value.trim(),
                language: languageEl.value,
                difficulty: difficultyEl.value
            })
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.success) {
                    toast('<i class="fa-solid fa-circle-check"></i> Saved to your library.', "success");
                    loadLibrary();
                } else {
                    toast(escapeHtml(data.message || "Save failed."), "error");
                }
            });
    }

    // ---------------------------------------------------------------
    // Library
    // ---------------------------------------------------------------
    function loadLibrary() {
        fetch(U.list, { credentials: "same-origin" })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                libraryData = {
                    saved: data.saved || [],
                    recent: data.recent || [],
                    favorites: data.favorites || []
                };
                renderLibrary();
            });
    }

    function renderLibrary() {
        var items = libraryData[currentView] || [];
        if (!items.length) {
            var empty = {
                saved: "No saved paragraphs yet. Save one to build your library.",
                recent: "No recent practice yet.",
                favorites: "No favorites yet. Tap the star on a paragraph."
            };
            libraryEl.innerHTML = '<p class="text-muted cp-empty">' + empty[currentView] + '</p>';
            return;
        }

        libraryEl.innerHTML = "";
        items.forEach(function (p) {
            var card = document.createElement("div");
            card.className = "cp-card";
            var preview = p.content.length > 120 ? p.content.slice(0, 120) + "…" : p.content;
            card.innerHTML =
                '<div class="cp-card-top">' +
                    '<h5 class="cp-card-title">' + escapeHtml(p.title) + '</h5>' +
                    '<button class="cp-fav ' + (p.favorite ? "on" : "") + '" title="Favorite" data-id="' + p.id + '">' +
                        '<i class="fa-' + (p.favorite ? "solid" : "regular") + ' fa-star"></i></button>' +
                '</div>' +
                '<p class="cp-card-body">' + escapeHtml(preview) + '</p>' +
                '<div class="cp-card-meta">' +
                    '<span>' + escapeHtml(p.language) + '</span>' +
                    '<span>' + escapeHtml(p.difficulty) + '</span>' +
                    '<span>' + p.word_count + ' words</span>' +
                '</div>' +
                '<div class="cp-card-actions">' +
                    '<a class="btn btn-sm btn-brand" href="' + U.practice + p.id + '"><i class="fa-solid fa-play"></i> Practice</a>' +
                    '<button class="btn btn-sm btn-ghost cp-load" data-id="' + p.id + '"><i class="fa-solid fa-pen"></i> Edit</button>' +
                    '<button class="btn btn-sm btn-ghost cp-ren" data-id="' + p.id + '"><i class="fa-solid fa-i-cursor"></i> Rename</button>' +
                    '<button class="btn btn-sm btn-danger cp-del" data-id="' + p.id + '"><i class="fa-solid fa-trash"></i></button>' +
                '</div>';
            libraryEl.appendChild(card);
        });

        bindCardEvents();
    }

    function findItem(id) {
        var all = libraryData.saved || [];
        for (var i = 0; i < all.length; i++) {
            if (String(all[i].id) === String(id)) { return all[i]; }
        }
        return null;
    }

    function bindCardEvents() {
        libraryEl.querySelectorAll(".cp-fav").forEach(function (b) {
            b.addEventListener("click", function () {
                fetch(U.favorite + b.dataset.id, { method: "POST", credentials: "same-origin" })
                    .then(function (r) { return r.json(); })
                    .then(function () { loadLibrary(); });
            });
        });
        libraryEl.querySelectorAll(".cp-del").forEach(function (b) {
            b.addEventListener("click", function () {
                if (!confirm("Delete this paragraph?")) { return; }
                fetch(U.del + b.dataset.id, { method: "POST", credentials: "same-origin" })
                    .then(function (r) { return r.json(); })
                    .then(function () { loadLibrary(); });
            });
        });
        libraryEl.querySelectorAll(".cp-load").forEach(function (b) {
            b.addEventListener("click", function () {
                var item = findItem(b.dataset.id);
                if (!item) { return; }
                contentEl.value = item.content;
                titleEl.value = item.title;
                languageEl.value = item.language;
                difficultyEl.value = item.difficulty;
                updateWordCount();
                setSource("paste");
                window.scrollTo({ top: 0, behavior: "smooth" });
            });
        });
        libraryEl.querySelectorAll(".cp-ren").forEach(function (b) {
            b.addEventListener("click", function () {
                var item = findItem(b.dataset.id);
                var name = prompt("Rename paragraph:", item ? item.title : "");
                if (name == null || !name.trim()) { return; }
                fetch(U.rename + b.dataset.id, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    credentials: "same-origin",
                    body: JSON.stringify({ title: name.trim() })
                })
                    .then(function (r) { return r.json(); })
                    .then(function () { loadLibrary(); });
            });
        });
    }

    libTabs.forEach(function (t) {
        t.addEventListener("click", function () {
            currentView = t.dataset.view;
            libTabs.forEach(function (x) { x.classList.toggle("active", x === t); });
            renderLibrary();
        });
    });

    // ---------------------------------------------------------------
    // Wire up
    // ---------------------------------------------------------------
    contentEl.addEventListener("input", updateWordCount);
    startBtn.addEventListener("click", startPractice);
    saveBtn.addEventListener("click", savePara);
    clearBtn.addEventListener("click", function () {
        contentEl.value = ""; titleEl.value = ""; updateWordCount(); clearStatus();
    });

    updateWordCount();
    loadLibrary();

})();
