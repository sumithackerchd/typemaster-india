// TypeMaster India — global app helpers
document.addEventListener("DOMContentLoaded", function () {
    console.log("TypeMaster India loaded");
});
function togglePassword(){

const input=document.getElementById("password");

const icon=document.getElementById("eyeIcon");

if(input.type==="password"){

input.type="text";

icon.classList.remove("fa-eye");

icon.classList.add("fa-eye-slash");

}else{

input.type="password";

icon.classList.remove("fa-eye-slash");

icon.classList.add("fa-eye");

}

}
function checkPasswordMatch() {

    const password = document.getElementById("password");
    const confirm = document.getElementById("confirmPassword");
    const text = document.getElementById("matchText");

    if (!password || !confirm || !text) return;

    if (confirm.value.length === 0) {
        text.innerHTML = "";
        return;
    }

    if (password.value === confirm.value) {
        text.innerHTML = "✔ Passwords Match";
        text.style.color = "#22c55e";
    } else {
        text.innerHTML = "✖ Passwords Do Not Match";
        text.style.color = "#ef4444";
    }
}
function checkPasswordStrength(){

const password=document.getElementById("password").value;

const bar=document.getElementById("strengthBar");

const text=document.getElementById("strengthText");

let strength=0;

if(password.length>=8) strength++;

if(/[A-Z]/.test(password)) strength++;

if(/[0-9]/.test(password)) strength++;

if(/[!@#$%^&*]/.test(password)) strength++;

if(strength===0){

bar.style.width="0";

text.innerHTML="";

return;

}

if(strength===1){

bar.style.width="25%";

bar.style.background="#ef4444";

text.innerHTML="Weak Password";

text.style.color="#ef4444";

}

if(strength===2){

bar.style.width="50%";

bar.style.background="#f59e0b";

text.innerHTML="Medium Password";

text.style.color="#f59e0b";

}

if(strength===3){

bar.style.width="75%";

bar.style.background="#3b82f6";

text.innerHTML="Good Password";

text.style.color="#3b82f6";

}

if(strength===4){

bar.style.width="100%";

bar.style.background="#22c55e";

text.innerHTML="Strong Password";

text.style.color="#22c55e";

}

}

function checkPasswordMatch(){

const p=document.getElementById("password").value;

const c=document.getElementById("confirmPassword").value;

const text=document.getElementById("matchText");

if(c===""){

text.innerHTML="";

return;

}

if(p===c){

text.innerHTML="✔ Passwords Match";

text.style.color="#22c55e";

}else{

text.innerHTML="✖ Passwords Do Not Match";

text.style.color="#ef4444";

}

}