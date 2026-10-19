/**
 * Motor de Resolución Exacto del Algoritmo Húngaro (Kuhn-Munkres)
 * Soporta Minimización, Maximización y Matrices Rectangulares Desbalanceadas (N != M)
 */

export function solveHungarian(inputMatrix, isMax = false, customRowLabels = [], customColLabels = []) {
  if (!inputMatrix || inputMatrix.length === 0 || !inputMatrix[0] || inputMatrix[0].length === 0) {
    throw new Error('La matriz no contiene filas ni columnas válidas.')
  }

  const origRows = inputMatrix.length
  const origCols = inputMatrix[0].length

  // Clona la matriz original numérica
  const original = inputMatrix.map(row => row.map(v => (isNaN(parseFloat(v)) ? 0 : parseFloat(v))))

  // Determinar tamaño cuadrado K = max(origRows, origCols)
  const K = Math.max(origRows, origCols)
  const isBalanced = origRows === origCols

  // Etiquetas por defecto o personalizadas
  const rowLabels = []
  for (let i = 0; i < K; i++) {
    if (i < origRows) {
      rowLabels.push(customRowLabels[i] || `Recurso ${i + 1}`)
    } else {
      rowLabels.push(`Recurso Ficticio ${i + 1} (Ficticio)`)
    }
  }

  const colLabels = []
  for (let j = 0; j < K; j++) {
    if (j < origCols) {
      colLabels.push(customColLabels[j] || `Tarea ${j + 1}`)
    } else {
      colLabels.push(`Tarea Ficticia ${j + 1} (Ficticia)`)
    }
  }

  // 1. Balancear matriz si no es cuadrada (rellena con 0)
  const balanced = []
  for (let i = 0; i < K; i++) {
    const row = []
    for (let j = 0; j < K; j++) {
      if (i < origRows && j < origCols) {
        row.push(original[i][j])
      } else {
        row.push(0)
      }
    }
    balanced.push(row)
  }

  // 2. Si es Maximización: transformar matriz C' = Max_Val - C
  let workingMatrix = []
  let maxVal = -Infinity
  if (isMax) {
    for (let i = 0; i < K; i++) {
      for (let j = 0; j < K; j++) {
        if (balanced[i][j] > maxVal) maxVal = balanced[i][j]
      }
    }
    for (let i = 0; i < K; i++) {
      workingMatrix.push(balanced[i].map(val => maxVal - val))
    }
  } else {
    workingMatrix = balanced.map(row => [...row])
  }

  // PASO 1: Reducción por filas (Restar mínimo de cada fila)
  const rowMins = []
  const afterRowReduction = []
  for (let i = 0; i < K; i++) {
    const minVal = Math.min(...workingMatrix[i])
    rowMins.push(minVal)
    afterRowReduction.push(workingMatrix[i].map(val => val - minVal))
  }

  // PASO 2: Reducción por columnas (Restar mínimo de cada columna)
  const colMins = []
  const afterColReduction = []
  for (let j = 0; j < K; j++) {
    let colMin = Infinity
    for (let i = 0; i < K; i++) {
      if (afterRowReduction[i][j] < colMin) colMin = afterRowReduction[i][j]
    }
    colMins.push(colMin)
  }

  for (let i = 0; i < K; i++) {
    afterColReduction.push(afterRowReduction[i].map((val, j) => val - colMins[j]))
  }

  // PASO 3 y 4: Cubrimiento de ceros y ajuste iterativo
  let currentMat = afterColReduction.map(r => [...r])
  let iterations = 0
  const maxIterations = 20
  let optimalMatching = []
  let finalLines = { rowLines: [], colLines: [], count: 0 }
  let adjustmentSteps = []

  while (iterations < maxIterations) {
    iterations++

    // Encontrar emparejamiento máximo de ceros independientes (Bipartite Matching)
    const matching = findMaxZeroMatching(currentMat, K)

    if (matching.length === K) {
      optimalMatching = matching
      finalLines.count = K
      break
    }

    // Si matching < K, calcular líneas mínimas usando Teorema de König
    const { rowLines, colLines } = findMinCoverLines(currentMat, matching, K)
    finalLines = { rowLines, colLines, count: rowLines.length + colLines.length }

    // Encontrar el menor elemento no cubierto k > 0
    let minUncovered = Infinity
    for (let i = 0; i < K; i++) {
      if (rowLines.includes(i)) continue
      for (let j = 0; j < K; j++) {
        if (colLines.includes(j)) continue
        if (currentMat[i][j] < minUncovered) {
          minUncovered = currentMat[i][j]
        }
      }
    }

    if (minUncovered === Infinity || minUncovered === 0) {
      optimalMatching = matching
      break
    }

    // Guardar para el paso a paso
    adjustmentSteps.push({
      iteration: iterations,
      linesCount: finalLines.count,
      rowLines: [...rowLines],
      colLines: [...colLines],
      minUncovered,
      matrixSnapshot: currentMat.map(r => [...r])
    })

    // Ajustar matriz:
    // - Restar minUncovered a los no cubiertos
    // - Sumar minUncovered a las intersecciones (cubiertos por fila Y columna)
    const nextMat = currentMat.map(r => [...r])
    for (let i = 0; i < K; i++) {
      const isRowCovered = rowLines.includes(i)
      for (let j = 0; j < K; j++) {
        const isColCovered = colLines.includes(j)

        if (!isRowCovered && !isColCovered) {
          nextMat[i][j] -= minUncovered
        } else if (isRowCovered && isColCovered) {
          nextMat[i][j] += minUncovered
        }
      }
    }

    currentMat = nextMat
  }

  // Si no se alcanzó matching completo por alguna razón degenerate, reintentar con el mejor
  if (optimalMatching.length < K) {
    optimalMatching = findMaxZeroMatching(currentMat, K)
  }

  // Filtrar asignaciones y calcular Z* en la matriz original
  const optimalAssignments = []
  let optimalZ = 0
  const optimalPairs = []

  // Ordenar asignaciones por fila
  optimalMatching.sort((a, b) => a[0] - b[0])

  for (const [r, c] of optimalMatching) {
    const isDummy = r >= origRows || c >= origCols
    const origVal = (r < origRows && c < origCols) ? original[r][c] : 0

    optimalPairs.push([r, c])
    if (!isDummy) {
      optimalZ += origVal
    }

    optimalAssignments.push({
      rowIdx: r,
      colIdx: c,
      from: rowLabels[r],
      to: colLabels[c],
      cost: isDummy ? '0 (Ficticio)' : `${origVal}`,
      isDummy
    })
  }

  return {
    isMax,
    isBalanced,
    origRows,
    origCols,
    dimensionK: K,
    rowLabels,
    colLabels,
    originalMatrix: original,
    balancedMatrix: balanced,
    afterRowReduction,
    rowMins,
    afterColReduction,
    colMins,
    adjustmentSteps,
    finalMatrix: currentMat,
    optimalPairs,
    optimalAssignments,
    optimalZ: isMax ? `${optimalZ}` : `${optimalZ}`,
    summary: `Se encontraron ${optimalMatching.length} asignaciones óptimas biunívocas con un valor total Z* = ${optimalZ}.`
  }
}

/**
 * Encuentra un emparejamiento máximo de ceros independientes usando BFS/DFS de caminos aumentantes (Hopcroft-Karp / Kuhn)
 */
function findMaxZeroMatching(matrix, K) {
  const matchR = Array(K).fill(-1) // matchR[col] = row
  const matchL = Array(K).fill(-1) // matchL[row] = col

  function dfs(u, visited) {
    for (let v = 0; v < K; v++) {
      if (matrix[u][v] === 0 && !visited[v]) {
        visited[v] = true
        if (matchR[v] < 0 || dfs(matchR[v], visited)) {
          matchL[u] = v
          matchR[v] = u
          return true
        }
      }
    }
    return false
  }

  for (let u = 0; u < K; u++) {
    const visited = Array(K).fill(false)
    dfs(u, visited)
  }

  const result = []
  for (let u = 0; u < K; u++) {
    if (matchL[u] >= 0) {
      result.push([u, matchL[u]])
    }
  }
  return result
}

/**
 * Determina el conjunto mínimo de líneas horizontales y verticales para cubrir todos los ceros
 * usando el Teorema de König:
 * 1. Marcar filas sin emparejamiento.
 * 2. Si fila marcada tiene cero en columna j, marcar columna j.
 * 3. Si columna j marcada está emparejada con fila i, marcar fila i.
 * 4. Líneas = Filas NO marcadas + Columnas marcadas.
 */
function findMinCoverLines(matrix, matching, K) {
  const matchedRows = new Set(matching.map(m => m[0]))
  const matchMapColToRow = {}
  matching.forEach(([r, c]) => {
    matchMapColToRow[c] = r
  })

  const markedRows = new Set()
  const markedCols = new Set()

  // 1. Marcar filas no emparejadas
  for (let i = 0; i < K; i++) {
    if (!matchedRows.has(i)) {
      markedRows.add(i)
    }
  }

  let changed = true
  while (changed) {
    changed = false

    // 2. Si fila marcada tiene cero en col j, marcar col j
    for (const r of markedRows) {
      for (let j = 0; j < K; j++) {
        if (matrix[r][j] === 0 && !markedCols.has(j)) {
          markedCols.add(j)
          changed = true
        }
      }
    }

    // 3. Si col j marcada está emparejada con fila r, marcar fila r
    for (const c of markedCols) {
      if (matchMapColToRow[c] !== undefined && !markedRows.has(matchMapColToRow[c])) {
        markedRows.add(matchMapColToRow[c])
        changed = true
      }
    }
  }

  // Líneas: filas NO marcadas y columnas marcadas
  const rowLines = []
  for (let i = 0; i < K; i++) {
    if (!markedRows.has(i)) {
      rowLines.push(i)
    }
  }
  const colLines = Array.from(markedCols)

  return { rowLines, colLines }
}
