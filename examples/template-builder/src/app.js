const { board } = window.miro;

const colors = [
    '#B2EEE4',
    '#B2DAEE',
    '#B2BCEE',
    '#C6B2EE',
    '#E4B2EE',
    '#EEB2DA',
    '#25CED1',
    '#FFFFFF',
    '#FCDCC7',
    '#FF8A5B',
    '#EA526F',
  ]
  const workDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
  const columnWidth = 150
  const rowHeight = 100
  const fontSize = 36
  
  async function drawTemplate(labels) {
    for (let rowIdx = 0; rowIdx < labels.length; rowIdx++) {
      const rowY = rowIdx * rowHeight + 10 * rowIdx
      const rowLabel = labels[rowIdx]
      const rowColor = getRowColor(rowIdx)
      if (rowLabel) {
        await createRowLabel(rowLabel, rowY, rowColor)
      }
      for (let colIdx = 0; colIdx < workDays.length; colIdx++) {
        const colX = colIdx * columnWidth + 2 * colIdx
        if (rowIdx === 0) {
          await createColumnLabel(colIdx, colX)
        }
        await createShape(colX, rowY, rowColor)
      }
    }
  }
  
  async function createShape(x, y, color) {
    return board.createShape({
      x: x,
      y: y,
      width: columnWidth,
      height: rowHeight,
      style: {
        fillColor: color,
      },
    })
  }
  
  async function createRowLabel(text, y, color) {
    return board.createText({
      x: -(columnWidth / 2 + fontSize),
      y: y,
      content: text,
      width: columnWidth,
      height: fontSize,
      rotation: 270,
      style: {
        fillColor: color,
      },
    })
  }
  
  async function createColumnLabel(colIdx, x) {
    return board.createText({
      x: x,
      y: -(rowHeight / 2 + fontSize),
      content: workDays[colIdx],
      width: columnWidth,
      height: fontSize,
    })
  }
  
  function getRowColor(index) {
    return colors[index % colors.length]
  }