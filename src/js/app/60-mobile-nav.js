const mobileNav = $('#mobile-nav');
$('#mobile-nav-open').addEventListener('click', () => {
  openDialog(mobileNav);
  /* Joriy bobni ro‘yxat o‘rtasida ko‘rsatamiz. */
  const current = $('#mobile-chapter-links a.active');
  if (current) current.scrollIntoView({ block: 'center', behavior: 'instant' });
});
$('#mobile-nav-close').addEventListener('click', () => closeDialog(mobileNav));
$('#mobile-chapter-links').addEventListener('click', e => {
  if (e.target.closest('a')) closeDialog(mobileNav);
});
/* Panelning tashqarisini bosish yopadi. */
mobileNav.addEventListener('click', e => {
  if (e.target !== mobileNav) return;
  const r = mobileNav.getBoundingClientRect();
  if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom)
    closeDialog(mobileNav);
});
/* Pastki varaq: yuqoridagi "tutqich"dan pastga tortib yopiladi. */
(() => {
  let startY = 0,
    dy = 0,
    dragging = false;
  const grip = mobileNav.querySelector('.sheet-grab'),
    head = mobileNav.querySelector('.dialog-top');
  const down = e => {
    if (e.button || e.target.closest('button') || !matchMedia('(max-width: 767px)').matches) return;
    dragging = true;
    startY = e.clientY;
    dy = 0;
    mobileNav.style.transition = 'none';
    e.currentTarget.setPointerCapture?.(e.pointerId);
  };
  const move = e => {
    if (!dragging) return;
    dy = Math.max(0, e.clientY - startY);
    mobileNav.style.transform = `translateY(${dy}px)`;
  };
  const up = () => {
    if (!dragging) return;
    dragging = false;
    if (dy > 90) {
      closeDialog(mobileNav);
    } else {
      mobileNav.style.transition = 'transform .3s cubic-bezier(.28,.11,.32,1)';
      mobileNav.style.transform = '';
    }
  };
  [grip, head].forEach(el => {
    el.addEventListener('pointerdown', down);
    el.addEventListener('pointermove', move);
    el.addEventListener('pointerup', up);
    el.addEventListener('pointercancel', up);
  });
  mobileNav.addEventListener('close', () => {
    dragging = false;
    mobileNav.style.transition = '';
    mobileNav.style.transform = '';
  });
})();
