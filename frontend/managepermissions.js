async function loadUsers() {

    const board = await miro.board.getInfo();

    const p = document.querySelector('.users');

    let res = await fetch('https://hittatilltf.com/users/' + board.id);
    const users = await res.json();

    res = await fetch('https://hittatilltf.com/managers/' + board.id);
    const managers = await res.json();

    for (user of users) {

        const row = document.createElement('div');
        row.className = 'grid m2';

        const a = document.createElement('div');
        a.className = 'cs2 ce8';
        a.appendChild(document.createTextNode(user.name));

        const b = document.createElement('button');
        if (managers.map(manager => manager.id).includes(user.id)) {
          b.className = 'button button-danger';
          b.setAttribute('onclick', "miro.showNotification('Removing managers is not supported in the demo')")
        } else {
          b.className = 'button button-primary';
          b.setAttribute('onclick', "miro.showNotification('Removing managers is not supported in the demo')")
        }

       
        b.appendChild(document.createTextNode(''));

        row.appendChild(a);
        row.appendChild(b);

        p.appendChild(row);
    }
}

miro.onReady(async () => {
  console.log('Fest2');
  await loadUsers();
});
