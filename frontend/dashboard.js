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
        
     async function getActivity() {
            const boardId = 'o9J_lhl9hPw=';
            const resp = await fetch('https://hittatilltf.com/stats/productivity');
            productivityData = await resp.json();
            const list = document.querySelector('.productivity-list');
            Object.entries(productivityData[boardId]).forEach(([user, productivityScore]) => {
              const li = document.createElement('li');
              li.appendChild(document.createTextNode(`${user} --- ${productivityScore.toFixed(3)}`));
              list.appendChild(li);
            });

          }
getActivity()