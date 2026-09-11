const input=document.getElementById("searchInput");
if(input){
  input.addEventListener("input",()=>{
    const q=input.value.toLowerCase().trim();
    document.querySelectorAll(".card").forEach(card=>{
      card.style.display=card.dataset.title.includes(q)?"block":"none";
    });
  });
}
document.querySelectorAll(".category").forEach(link=>{
  link.addEventListener("click",e=>{
    e.preventDefault();
    const category=link.dataset.category.toLowerCase();
    document.querySelectorAll(".card").forEach(card=>{
      card.style.display=card.dataset.category.includes(category)?"block":"none";
    });
  });
});
