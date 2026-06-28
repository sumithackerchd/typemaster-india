// ======================================
// TypeMaster India Result Engine
// Version 1.0
// ======================================


// ------------------------------
// Save Result in LocalStorage
// ------------------------------

function saveResult(result){

    localStorage.setItem(

        "typingResult",

        JSON.stringify(result)

    );

}


// ------------------------------
// Load Result
// ------------------------------

function loadResult(){

    const data = localStorage.getItem("typingResult");

    if(!data){

        return null;

    }

    return JSON.parse(data);

}


// ------------------------------
// Show Result
// ------------------------------

function displayResult(){

    const result = loadResult();

    if(result==null){

        return;

    }

    setValue("netWpm",result.net_wpm);

    setValue("grossWpm",result.gross_wpm);

    setValue("accuracyResult",

        result.accuracy+"%"

    );

    setValue("errorsResult",

        result.errors

    );

    setValue("charactersTyped",

        result.typed

    );

    setValue("cpmResult",

        result.cpm

    );

    setValue("durationResult",

        result.duration+" sec"

    );

    setValue("languageResult",

        result.language

    );

}


// ------------------------------
// Helper
// ------------------------------

function setValue(id,value){

    const el=document.getElementById(id);

    if(el){

        el.innerText=value;

    }

}


// ------------------------------
// Clear Result
// ------------------------------

function clearTypingResult(){

    localStorage.removeItem(

        "typingResult"

    );

}


// ------------------------------
// Restart
// ------------------------------

function restartTyping(){

    clearTypingResult();

    window.location="/typing";

}


// ------------------------------
// Dashboard
// ------------------------------

function goDashboard(){

    window.location="/dashboard";

}


// ------------------------------
// Export JSON (Future)
// ------------------------------

function exportResult(){

    const result=loadResult();

    if(!result){

        return;

    }

    console.log(result);

}


// ------------------------------
// Auto Load
// ------------------------------

window.addEventListener(

    "DOMContentLoaded",

    displayResult

);