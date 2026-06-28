// ===============================
// TypeMaster India Dashboard JS
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    console.log("Dashboard Loaded Successfully");

    animateCards();

    showGreeting();

});

// -------------------------------
// Animate Dashboard Cards
// -------------------------------

function animateCards() {

    const cards = document.querySelectorAll(".stat-card, .quick-card");

    cards.forEach((card, index) => {

        card.style.opacity = "0";
        card.style.transform = "translateY(30px)";

        setTimeout(() => {

            card.style.transition = "0.5s ease";

            card.style.opacity = "1";

            card.style.transform = "translateY(0)";

        }, index * 120);

    });

}

// -------------------------------
// Greeting
// -------------------------------

function showGreeting() {

    const hour = new Date().getHours();

    let greeting = "Welcome";

    if (hour < 12) {

        greeting = "🌅 Good Morning";

    } else if (hour < 17) {

        greeting = "☀️ Good Afternoon";

    } else {

        greeting = "🌙 Good Evening";

    }

    const heading = document.querySelector(".welcome-card h2");

    if (heading) {

        const username = heading.innerText.replace("👋 Welcome", "").trim();

        heading.innerHTML = `${greeting} ${username} 👋`;

    }

}

// -------------------------------
// Future Functions
// -------------------------------

// updateStatistics()
// loadRecentActivity()
// loadLeaderboard()
// loadProgressGraph()
// loadDailyGoal()