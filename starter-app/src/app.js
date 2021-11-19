const { board } = window.miro;

async function init() {
  const stickyNote = await board.createStickyNote({
    content: "Hello, World!",
  });

  await board.viewport.zoomTo(stickyNote);
}

init();
