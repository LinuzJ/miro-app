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
          b.setAttribute('onclick', "removeManager(" + user.id + ")")
        } else {
          b.className = 'button button-primary';
          b.setAttribute('onclick', "addManager(" + user.id + ")")
        }

       
        b.appendChild(document.createTextNode(''));

        row.appendChild(a);
        row.appendChild(b);

        p.appendChild(row);
    }
}

async function addManager(user) {

  const board = await miro.board.getInfo();

  const data = {
    board: board.id,
    user: user
  };

  await fetch('https://hittatilltf.com/managers', {
    method: 'POST',
    headers: {},
    body: JSON.stringify(data)
  });

  const p = document.querySelector('.users');
  p.innerHTML = '';

  await loadUsers();

}

async function removeManager(user) {

  const board = await miro.board.getInfo();

  const data = {
    board: board.id,
    user: user
  };

  await fetch('https://hittatilltf.com/managers', {
    method: 'DELETE',
    headers: {},
    body: JSON.stringify(data)
  });

  const p = document.querySelector('.users');
  p.innerHTML = '';

  await loadUsers();

}

miro.onReady(async () => {
  console.log('lol');
  await loadUsers();
});
