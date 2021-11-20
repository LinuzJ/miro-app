async function loadUsers() {

    const p = document.querySelector('.users');

    let res = await fetch('https://hittatilltf.com/users/' + 'o9J_lhl9hPw=');
    const users = await res.json();

    res = await fetch('https://hittatilltf.com/managers/' + 'o9J_lhl9hPw=');
    const managers = await res.json();

    for (user of users) {

        const row = document.createElement('div');
        row.className = 'grid m2';

        const a = document.createElement('div');
        a.className = 'cs2 ce8';
        a.appendChild(document.createTextNode(user.name));

        const b = document.createElement('button');
        if (managers.map(manager => manager.id).includes(user.id)) {
          b.className = 'button button-primary';
        } else {
          b.className = 'button button-danger';
        }
        
        b.appendChild(document.createTextNode('Kappa'));

        row.appendChild(a);
        row.appendChild(b);

        p.appendChild(row);
    }
}

miro.onReady(async () => {
  await loadUsers();
});
