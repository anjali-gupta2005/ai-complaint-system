setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(-10px)';
        setTimeout(() => el.remove(), 400);
    });
}, 3500);