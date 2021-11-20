let board = null;

function openTab(selected) {
  const tabIndices = { '.user-stats': 0, '.productivity': 1};
  ['.user-stats', '.productivity'].forEach(tab => {
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

miro.onReady(async () => {
    console.log('Snart e de ylonz!!');
    const boardInfo = await miro.board.info.get();
    board = boardInfo;
    getInsights();
    setInfo();
    getActivity(board.id);
});


function createTable() {
    var userData = new Array();
    userData.push(["Name", "ID"]);
    userData.push(["Smith Fucker", 123456789]);

    var table = document.createElement("TABLE");
    table.border = "1";
    var columnCount = userData[0].length;

    //Header row.
    var row = table.insertRow(-1);
    for (var i = 0; i < columnCount; i++) {
        var headerCell = document.createElement("TH");
        headerCell.innerHTML = userData[0][i];
        row.appendChild(headerCell);
    }

    //Data rows.
    for (var i = 1; i < userData.length; i++) {
        row = table.insertRow(-1);
        for (var j = 0; j < columnCount; j++) {
            var cell = row.insertCell(-1);
            cell.innerHTML = userData[i][j];
        }
    }

    var userDataTable = document.getElementById("userDataTable");
    userDataTable.innerHTML = "";
    userDataTable.appendChild(table);
}

