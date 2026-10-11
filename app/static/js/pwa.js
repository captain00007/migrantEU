if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then((reg) => console.log('ServiceWorker migrantEU registrado com sucesso:', reg.scope))
      .catch((err) => console.log('Falha ao registrar ServiceWorker:', err));
  });
}
