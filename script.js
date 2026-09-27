
const menuToggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('nav');
if(menuToggle){
  menuToggle.addEventListener('click',()=>nav.classList.toggle('active'));
}
document.querySelectorAll('nav a').forEach(a=>{
  a.addEventListener('click',()=>{
    if(window.innerWidth<900) nav.classList.remove('active');
  });
});
