function postData(endpoint, data) {
    fetch("https://hittatilltf.com/" + endpoint, {
        method: "POST",
        headers: {},
        body: JSON.stringify(data)
    }).then(res => {
        console.log(res.status)
    });
};

async function handleUsersChangedEvent(event) {
    let board = await miro.board.info.get();
    let data = {
        board: board.id,
        users: event.data
    };
    postData("update_users", data);
};

async function handleClickEvent(event) {
    let board = await miro.board.info.get();
    let userId = await miro.currentUser.getId();
    let data = {
        type: "CLICK",
        board: board.id,
        user: userId
    };
    postData("add_event", data);
};        

async function handleWidgetsCreatedEvent(event) {
    let board = await miro.board.info.get();
    let userId = await miro.currentUser.getId();
    let data = {
        eventType: "WIDGETS_CREATED",
        board: board.id,
        user: userId
    };
    postData("add_event", data);
};

async function handleWidgetsDeletedEvent(event) {
    let board = await miro.board.info.get();
    let userId = await miro.currentUser.getId();
    let data = {
        eventType: "WIDGETS_DELETED",
        board: board.id,
        user: userId
    };
    postData("add_event", data);
};

async function handleWidgetsUpdatedEvent(event) {
    let board = await miro.board.info.get();
    let userId = await miro.currentUser.getId();
    let data = {
        eventType: "WIDGETS_UPDATED",
        board: board.id,
        user: userId
    };
    postData("add_event", data);
};

async function handleCommentCreatedEvent(event) {
    let board = await miro.board.info.get();
    let userId = await miro.currentUser.getId();
    let data = {
        eventType: "COMMENT_CREATED",
        board: board.id,
        user: userId
    };
    postData("add_event", data);
};

async function handleSelectionUpdatedEvent(event) {
    let board = await miro.board.info.get();
    let userId = await miro.currentUser.getId();
    let data = {
        eventType: "SELECTION_UPDATED",
        board: board.id,
        user: userId
    };
    postData("add_event", data);
};

miro.onReady(() => {
    miro.addListener("ONLINE_USERS_CHANGED", handleUsersChangedEvent);
    miro.addListener("CANVAS_CLICKED", handleClickEvent);
    miro.addListener("WIDGETS_CREATED", handleWidgetsCreatedEvent);
    miro.addListener("WIDGETS_DELETED", handleWidgetsDeletedEvent);
    miro.addListener("WIDGETS_TRANSFORMATION_UPDATED", handleWidgetsUpdatedEvent);
    miro.addListener("COMMENT_CREATED", handleCommentCreatedEvent);
    miro.addListener("SELECTION_UPDATED", handleSelectionUpdatedEvent);

    miro.initialize({
        extensionPoints: {
          bottomBar: {
            title: 'analytics toolkit',
            svgIcon: '<circle cx="12" cy="12" r="9" fill="none" fill-rule="evenodd" stroke="currentColor" stroke-width="2"></circle>',
            onClick: () => {
                console.log("lol");
            },
          },
        },
      })
});
