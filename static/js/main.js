console.log("Alunan Amerta Loaded");

document.addEventListener(
"DOMContentLoaded",
function(){

document.querySelectorAll("tr").forEach(
row=>{
row.addEventListener(
"mouseenter",
()=>{
row.style.transform="scale(1.01)";
});
}
);

});
