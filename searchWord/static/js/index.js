// function to trigger animation
document.querySelector('.button').addEventListener('click', () => {
  document.querySelector('.menu__list')
    .classList.toggle('menu__list--animate');
});