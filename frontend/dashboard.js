let board = null;

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
}

async function getActivity(boardId) {
  const resp = await fetch(`https://hittatilltf.com/stats/productivity/${boardId}`);
  productivityData = await resp.json();
  const list = document.querySelector('.productivity-list');
  Object.entries(productivityData[boardId]).forEach(([user, productivityScore]) => {
    const li = document.createElement('li');
    li.appendChild(document.createTextNode(`${user} --- ${productivityScore.toFixed(3)}`));
    list.appendChild(li);
  });

}

async function getInsights() {
  try {
    const resp = await fetch('https://hittatilltf.com/insight');
    data = await resp.json();
    const p = document.querySelector('.insight-text');
    p.appendChild(document.createTextNode(data));
    const insight = document.querySelector('.insight');
    insight.style = 'display: grid;';
  } catch {
    console.log('error')
    const insight = document.querySelector('.insight');
    insight.style = 'display: none;';
  }
};


function setInfo() {
  if (board) {
    const p = document.querySelector('.board-info');
    p.appendChild(document.createTextNode(`Board: ${board.id}\nCreated at: ${board.createdAt}\nLast modified: ${board.updatedAt}\nOwner: ${board.owner.name}`));
  } else {
    setTimeout(setInfo, 100000);
  }
}

async function showUserChart() {
  const scan = (values, fn, initial) => values.reduce((total, n) => [...total, fn(total[total.length - 1], n)], [initial])
  const resp = await fetch('https://hittatilltf.com/events')
  const events = await resp.json()
  labels = []
  join_leave_events = events.filter((event) => ['USER_JOINED', 'USER_LEFT'].includes(event[1]));
  console.log(scan(join_leave_events, (total, n) => {
    if (n[1] === 'USER_JOINED') {
      labels.push(n[3])
      return { x: n[5], y: total.y + 1 }
    } else {
      labels.push(n[3])
      return { x: n[5], y: total.y - 1 }
    }
  }, { x: join_leave_events[0][5], y: 0 }));
  const data = {
    datasets: [{
      label: 'User online activity',
      labels,
      data: scan(join_leave_events, (total, n) => {
        if (n[1] === 'USER_JOINED') {
          return { x: n[5], y: total.y + 1, label: n[3] }
        } else {
          return { x: n[5], y: total.y - 1, label: n[3] }
        }
      }, { x: join_leave_events[0][5], y: 0 }),
      backgroundColor: 'rgb(255, 99, 132)',
      borderColor: 'rgb(255, 99, 132)',
    }]
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
showUserChart();

miro.onReady(async () => {
    console.log('Snart e de ylonz!!');
    const boardInfo = await miro.board.info.get();
    board = boardInfo;
    getInsights();
    setInfo();
    getActivity(board.id);
    showUserChart();
});
