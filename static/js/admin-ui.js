/**
 * Admin UI helpers — tables, charts, sidebar, counters, bulk actions.
 */
(function () {
    "use strict";

    function initDataTable(tableId, opts) {
        var table = document.getElementById(tableId);
        if (!table) return;

        opts = opts || {};
        var pageSize = opts.pageSize || 12;
        var searchInput = document.getElementById(opts.searchId);
        var filterSelect = document.getElementById(opts.filterId);
        var pagerInfo = document.getElementById(opts.pagerInfoId);
        var pagerBtns = document.getElementById(opts.pagerBtnsId);
        var tbody = table.querySelector("tbody");
        if (!tbody) return;

        var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr"));
        if (rows.length === 1 && rows[0].querySelector("td[colspan]")) return;

        var filtered = rows.slice();
        var page = 1;

        function applyFilter() {
            var q = (searchInput && searchInput.value || "").trim().toLowerCase();
            var role = filterSelect ? filterSelect.value : "all";
            var langFilter = opts.langFilterId ? document.getElementById(opts.langFilterId) : null;
            var lang = langFilter ? langFilter.value : "all";
            var statusFilter = opts.statusFilterId ? document.getElementById(opts.statusFilterId) : null;
            var status = statusFilter ? statusFilter.value : "all";
            filtered = rows.filter(function (tr) {
                var text = tr.textContent.toLowerCase();
                if (q && text.indexOf(q) === -1) return false;
                if (role === "admin" && !tr.dataset.admin) return false;
                if (role === "user" && tr.dataset.admin) return false;
                if (lang !== "all" && tr.dataset.lang !== lang) return false;
                if (status !== "all" && tr.dataset.status !== status) return false;
                return true;
            });
            page = 1;
            render();
        }

        function render() {
            var totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
            if (page > totalPages) page = totalPages;
            rows.forEach(function (tr) { tr.style.display = "none"; });
            var start = (page - 1) * pageSize;
            filtered.slice(start, start + pageSize).forEach(function (tr) { tr.style.display = ""; });

            if (pagerInfo) {
                pagerInfo.textContent = filtered.length
                    ? "Showing " + (start + 1) + "–" + Math.min(start + pageSize, filtered.length) + " of " + filtered.length
                    : "No rows match";
            }

            if (!pagerBtns) return;
            pagerBtns.innerHTML = "";
            function btn(label, p, disabled, active) {
                var b = document.createElement("button");
                b.type = "button";
                b.textContent = label;
                b.disabled = disabled;
                if (active) b.className = "active";
                if (!disabled && !active) {
                    b.addEventListener("click", function () { page = p; render(); });
                }
                pagerBtns.appendChild(b);
            }
            btn("‹", page - 1, page === 1, false);
            for (var i = 1; i <= totalPages; i += 1) {
                if (totalPages > 7 && Math.abs(i - page) > 2 && i !== 1 && i !== totalPages) continue;
                btn(String(i), i, false, i === page);
            }
            btn("›", page + 1, page === totalPages, false);
        }

        if (searchInput) {
            var t;
            searchInput.addEventListener("input", function () {
                clearTimeout(t);
                t = setTimeout(applyFilter, 180);
            });
        }
        if (filterSelect) filterSelect.addEventListener("change", applyFilter);
        if (opts.langFilterId) {
            var lf = document.getElementById(opts.langFilterId);
            if (lf) lf.addEventListener("change", applyFilter);
        }
        if (opts.statusFilterId) {
            var sf = document.getElementById(opts.statusFilterId);
            if (sf) sf.addEventListener("change", applyFilter);
        }

        table.querySelectorAll("th[data-sort]").forEach(function (th) {
            th.style.cursor = "pointer";
            th.addEventListener("click", function () {
                var idx = Array.prototype.indexOf.call(th.parentNode.children, th);
                var asc = th.dataset.sortDir !== "asc";
                th.dataset.sortDir = asc ? "asc" : "desc";
                filtered.sort(function (a, b) {
                    var av = (a.children[idx] && a.children[idx].textContent.trim()) || "";
                    var bv = (b.children[idx] && b.children[idx].textContent.trim()) || "";
                    var an = parseFloat(av.replace(/[^\d.-]/g, ""));
                    var bn = parseFloat(bv.replace(/[^\d.-]/g, ""));
                    if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
                    return asc ? av.localeCompare(bv) : bv.localeCompare(av);
                });
                filtered.forEach(function (tr) { tbody.appendChild(tr); });
                render();
            });
        });

        render();
    }

    function initBulkActions(prefix) {
        var form = document.getElementById(prefix + "BulkForm");
        var selectAll = document.getElementById(prefix + "SelectAll");
        var deleteBtn = document.getElementById(prefix + "BulkDelete");
        if (!form) return;

        function updateBulk() {
            var checked = form.querySelectorAll(".row-check:checked");
            if (deleteBtn) deleteBtn.disabled = checked.length === 0;
        }

        form.addEventListener("change", function (e) {
            if (e.target.classList.contains("row-check")) updateBulk();
        });

        if (selectAll) {
            selectAll.addEventListener("change", function () {
                form.querySelectorAll(".row-check").forEach(function (cb) {
                    var tr = cb.closest("tr");
                    if (tr && tr.style.display !== "none") cb.checked = selectAll.checked;
                });
                updateBulk();
            });
        }

        if (deleteBtn) {
            deleteBtn.addEventListener("click", function () {
                var n = form.querySelectorAll(".row-check:checked").length;
                if (!n) return;
                if (confirm("Delete " + n + " selected item(s)?")) form.submit();
            });
        }
    }

    function initCounters() {
        document.querySelectorAll(".counter[data-target]").forEach(function (el) {
            var target = parseInt(el.getAttribute("data-target"), 10) || 0;
            var duration = 900;
            var start = performance.now();
            function tick(now) {
                var p = Math.min(1, (now - start) / duration);
                var eased = 1 - Math.pow(1 - p, 3);
                el.textContent = Math.round(target * eased).toLocaleString();
                if (p < 1) requestAnimationFrame(tick);
            }
            requestAnimationFrame(tick);
        });
    }

    function initSidebarSearch() {
        var input = document.getElementById("sidebarSearch");
        if (!input) return;
        input.addEventListener("input", function () {
            var q = input.value.trim().toLowerCase();
            document.querySelectorAll(".admin-nav[data-menu-group] > li").forEach(function (li) {
                var text = li.textContent.toLowerCase();
                li.style.display = !q || text.indexOf(q) !== -1 ? "" : "none";
            });
        });
    }

    function initSidebarTooltips() {
        var shell = document.getElementById("adminShell");
        if (!shell) return;
        document.querySelectorAll(".admin-nav a[data-tooltip]").forEach(function (a) {
            a.addEventListener("mouseenter", function () {
                if (!shell.classList.contains("collapsed")) return;
                var tip = document.createElement("div");
                tip.className = "sidebar-tooltip";
                tip.textContent = a.getAttribute("data-tooltip");
                document.body.appendChild(tip);
                var r = a.getBoundingClientRect();
                tip.style.top = (r.top + r.height / 2 - tip.offsetHeight / 2) + "px";
                tip.style.left = (r.right + 10) + "px";
                a._tip = tip;
            });
            a.addEventListener("mouseleave", function () {
                if (a._tip) { a._tip.remove(); a._tip = null; }
            });
        });
    }

    function initSettingsHash() {
        if (!window.ADMIN_SETTINGS_TABS) return;
        var hash = window.location.hash.replace("#", "");
        if (!hash) return;
        var btn = document.querySelector('.settings-nav button[data-section="' + hash + '"]');
        if (btn) btn.click();
    }

    window.AdminUI = { initDataTable: initDataTable };

    document.addEventListener("DOMContentLoaded", function () {
        if (window.ADMIN_USERS_TABLE) {
            initDataTable("usersTable", {
                searchId: "usersSearch",
                filterId: "usersRoleFilter",
                statusFilterId: "usersStatusFilter",
                pagerInfoId: "usersPagerInfo",
                pagerBtnsId: "usersPagerBtns",
                pageSize: 10
            });
            if (window.ADMIN_USERS_TABLE.bulk) initBulkActions("users");
        }
        if (window.ADMIN_RESULTS_TABLE) {
            initDataTable("resultsTable", Object.assign({
                searchId: "resultsSearch",
                filterId: null,
                pagerInfoId: "resultsPagerInfo",
                pagerBtnsId: "resultsPagerBtns",
                pageSize: 15
            }, typeof window.ADMIN_RESULTS_TABLE === "object" ? window.ADMIN_RESULTS_TABLE : {}));
            if (window.ADMIN_RESULTS_TABLE.bulk) initBulkActions("results");
        }
        if (window.ADMIN_DOWNLOADS_SEARCH) {
            var si = document.getElementById("downloadsSearch");
            var cards = document.querySelectorAll(".download-card");
            if (si && cards.length) {
                si.addEventListener("input", function () {
                    var q = si.value.trim().toLowerCase();
                    cards.forEach(function (c) {
                        c.style.display = !q || c.textContent.toLowerCase().indexOf(q) !== -1 ? "" : "none";
                    });
                });
            }
        }
        if (window.ADMIN_SETTINGS_TABS) {
            document.querySelectorAll(".settings-nav button").forEach(function (btn) {
                btn.addEventListener("click", function () {
                    document.querySelectorAll(".settings-nav button").forEach(function (b) { b.classList.remove("active"); });
                    document.querySelectorAll(".settings-section").forEach(function (s) { s.classList.remove("active"); });
                    btn.classList.add("active");
                    var sec = document.getElementById(btn.getAttribute("data-section"));
                    if (sec) sec.classList.add("active");
                    history.replaceState(null, "", "#" + btn.getAttribute("data-section").replace("sec-", ""));
                });
            });
            initSettingsHash();
        }
        if (window.ADMIN_CHARTS) initCharts(window.ADMIN_CHARTS);
        if (window.ADMIN_COUNTERS) initCounters();
        initSidebarSearch();
        initSidebarTooltips();

        document.addEventListener("keydown", function (e) {
            if ((e.ctrlKey || e.metaKey) && e.key === "b") {
                e.preventDefault();
                if (typeof window.toggleAdminSidebar === "function") window.toggleAdminSidebar();
            }
        });
    });

    function initCharts(data) {
        if (typeof Chart === "undefined") return;
        Chart.defaults.color = "#94a3b8";
        Chart.defaults.borderColor = "rgba(255,255,255,0.08)";
        Chart.defaults.font.family = "'Poppins', sans-serif";

        var activity = document.getElementById("chartActivity");
        if (activity) {
            new Chart(activity, {
                type: "line",
                data: {
                    labels: data.activityLabels,
                    datasets: [{
                        label: "Tests",
                        data: data.activityCounts,
                        borderColor: "#818cf8",
                        backgroundColor: "rgba(99,102,241,0.15)",
                        fill: true,
                        tension: 0.35,
                        pointRadius: 4,
                        pointBackgroundColor: "#6366f1"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.06)" } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        var wpm = document.getElementById("chartWpm");
        if (wpm) {
            new Chart(wpm, {
                type: "bar",
                data: {
                    labels: data.wpmLabels,
                    datasets: [{
                        label: "Avg Net WPM",
                        data: data.wpmValues,
                        backgroundColor: "rgba(34,211,238,0.55)",
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.06)" } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }
    }
})();
