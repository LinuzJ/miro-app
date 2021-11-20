let board = null;
let usernames = {};

function openTab(selected) {
  const tabIndices = { '.user-stats': 0, '.productivity': 1, '.misc-stats': 2 };
  ['.user-stats', '.productivity', '.misc-stats'].forEach(tab => {
    if (selected === tab) {
      document.querySelector(tab).style = 'display: flex;'
      document.querySelector(`[tabindex = "${tabIndices[tab]}"`).classList.add('tab-active')
    } else {
      document.querySelector(tab).style = 'display: none;'
      document.querySelector(`[tabindex = "${tabIndices[tab]}"`).classList.remove('tab-active')
    };
  });
  if (selected === '.misc-stats') {
      document.querySelector('.insight').style = 'display: grid;'
  } else {
      document.querySelector('.insight').style = 'display: none;'
  }
}

async function getActivity(boardId) {
  const resp = await fetch(`https://hittatilltf.com/stats/productivity/${boardId}`);
  productivityData = await resp.json();
  const list = document.querySelector('.productivity-list');
  Object.entries(productivityData[boardId]).forEach(([user, productivityScore]) => {
    const tr = document.createElement('tr');
    const userName = document.createElement('td');
    const score = document.createElement('td');
    userName.appendChild(document.createTextNode(user));
    score.appendChild(document.createTextNode(productivityScore.toFixed(3)));
    tr.appendChild(userName);
    tr.appendChild(score);
    list.appendChild(tr);
  });

}

async function getInsights(boardId) {
  try {
    const resp = await feteh(`https://hittatilltf.com/insight/${boardId}`);
    data = await resp.json();
    const p = document.querySelector('.insight-text');
    p.appendChild(document.createTextNode(data));
    const insight = document.querySelector('.insight');
  } catch {
    console.log('error')
    const insight = document.querySelector('.insight');
    insight.style = 'display: none;';
  }
};


function setInfo() {
  if (board) {
    try {
      const p = document.querySelector('.board-info');
      const boardId = document.createElement('td');
      boardId.appendChild(document.createTextNode(board.title));
      const created = document.createElement('td');
      created.appendChild(document.createTextNode(board.createdAt));
      const modified = document.createElement('td');
      modified.appendChild(document.createTextNode(board.updatedAt));
      const owner = document.createElement('td');
      owner.appendChild(document.createTextNode(board.owner.name));
      const row = document.createElement('tr')
      const body = document.createElement('tbody');
      row.appendChild(boardId);
      row.appendChild(created);
      row.appendChild(modified);
      row.appendChild(owner);
      body.appendChild(row);
      p.appendChild(body);
    } catch (e) {
      console.log(e)
    }
  } else {
    setTimeout(setInfo, 100000);
  }
}

async function getUserNames() {
  const resp = await fetch('https://hittatilltf.com/username');
  usernames = await resp.json();
}

async function showUserChart() {
  const scan = (values, fn, initial) => values.reduce((total, n) => [...total, fn(total[total.length - 1], n)], [initial])
  const resp = await fetch('https://hittatilltf.com/events')
  const events = await resp.json()
  labels = []
  pointColor = []
  join_leave_events = events
    .filter((event) => ['USER_JOINED', 'USER_LEFT'].includes(event[1]))
    .filter(event => event[2] === board.id);
  const datapoints = scan(join_leave_events, (total, n) => {
        if (n[1] === 'USER_JOINED') {
          pointColor.push('#77cc66')
          labels.push(`${usernames[n[3]] || n[3]} joined at ${n[5]}`)
          return { x: n[5], y: total.y + 1, user: usernames[n[3]] || n[3] }
        } else {
          pointColor.push('#b80d0d')
          labels.push(`${usernames[n[3]] || n[3]} left at ${n[5]}`)
          return { x: n[5], y: total.y - 1, user: usernames[n[3]] || n[3] }
        }
      }, { x: join_leave_events[0][5], y: 0 });
  const series = {}
  datapoints.forEach(event => {
    if (series[event.user]) {
      series[event.user].push(event);
    } else {
      series[event.user] = [event];
    }
  })
  const data = {
    datasets: Object.entries(series).map(([user, events]) => ({
      label: user,
      data: events,
      pointBackgroundColor: pointColor,
    })),
  };
  const config = {
    type: 'scatter',
    data: data,
    options: {
      responsive: true,
      scales: {
        x: {
          type: 'timeseries',
          position: 'bottom'
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              return labels[context.dataIndex];
            }
          }
        }
      }

    }
  };
  const myChart = new Chart(
    document.querySelector('#userChart'),
    config
  );
}

miro.onReady(async () => {
    console.log('Snart e de ylonz!!');
    const boardInfo = await miro.board.info.get();
    board = boardInfo;
    await getUserNames();
    getInsights(board.id);
    setInfo();
    getActivity(board.id);
    showUserChart();
});
