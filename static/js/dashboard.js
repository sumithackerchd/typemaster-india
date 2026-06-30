// ==========================================
// Dashboard V2
// ==========================================

document.addEventListener("DOMContentLoaded", () => {

    animateCounters();

    updateGreeting();

    animateCards();

    animateGoal();

});


// ==========================================
// Greeting
// ==========================================

function updateGreeting(){

    const title=document.querySelector(".hero-dashboard h1");

    if(!title) return;

    const hour=new Date().getHours();

    let greet="Welcome";

    if(hour<12){

        greet="☀️ Good Morning";

    }

    else if(hour<17){

        greet="🌤 Good Afternoon";

    }

    else{

        greet="🌙 Good Evening";

    }

    const badge=document.querySelector(".welcome-badge");

    if(badge){

        badge.innerHTML=greet;

    }

}


// ==========================================
// Counter Animation
// ==========================================

function animateCounters(){

    document.querySelectorAll(".stat-number").forEach(counter=>{

        const txt=counter.innerText.trim();

        const value=parseFloat(txt.replace(/[^\d.]/g,""));

        if(isNaN(value)) return;

        let current=0;

        const step=value/50;

        const timer=setInterval(()=>{

            current+=step;

            if(current>=value){

                current=value;

                clearInterval(timer);

            }

            if(txt.includes("%")){

                counter.innerHTML=current.toFixed(1)+"%";

            }

            else if(txt.includes("#")){

                counter.innerHTML="#"+Math.floor(current);

            }

            else{

                counter.innerHTML=Math.floor(current);

            }

        },20);

    });

}


// ==========================================
// Hover Animation
// ==========================================

function animateCards(){

    document.querySelectorAll(".stat-card,.quick-card,.recent-card,.goal-card")
    .forEach(card=>{

        card.addEventListener("mousemove",e=>{

            const rect=card.getBoundingClientRect();

            const x=e.clientX-rect.left;

            const y=e.clientY-rect.top;

            card.style.setProperty("--x",x+"px");

            card.style.setProperty("--y",y+"px");

        });

    });

}


// ==========================================
// Goal Circle Animation
// ==========================================

function animateGoal(){

    const goal=document.querySelector(".goal-progress h1");

    if(!goal) return;

    const value=parseInt(goal.innerText);

    let current=0;

    const timer=setInterval(()=>{

        current++;

        goal.innerHTML=current+"%";

        if(current>=value){

            clearInterval(timer);

        }

    },18);

}
// ==========================================
// Performance Chart
// ==========================================

// Achievement Animation

document.querySelectorAll(".achievement-card")
.forEach(card=>{

card.addEventListener("mouseenter",()=>{

card.style.transform="translateY(-10px) scale(1.03)";

});

card.addEventListener("mouseleave",()=>{

card.style.transform="";

});

});