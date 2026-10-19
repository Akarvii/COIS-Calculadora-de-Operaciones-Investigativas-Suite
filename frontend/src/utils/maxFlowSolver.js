/**
 * Edmonds-Karp Max-Flow and Min-Cut Algorithm Solver
 * 
 * Computes exact maximum flow in a directed capacitaded network using BFS
 * on the residual network. Identifies the minimum cut partition (S, T),
 * saturated bottleneck arcs, and step-by-step augmenting path iterations.
 */

export function solveMaxFlow(source, sink, rawArcs) {
  if (!source || !sink) {
    throw new Error('Debes especificar el nodo Fuente (s) y el nodo Sumidero (t).')
  }

  const sStr = String(source).trim()
  const tStr = String(sink).trim()

  if (sStr === tStr) {
    throw new Error('El nodo Fuente (s) y el nodo Sumidero (t) deben ser distintos.')
  }

  // Filtrar y validar arcos
  const validArcs = []
  for (let i = 0; i < rawArcs.length; i++) {
    const arc = rawArcs[i]
    const u = String(arc.from || '').trim()
    const v = String(arc.to || '').trim()
    const cap = Number(arc.capacity)

    if (!u || !v) continue
    if (isNaN(cap) || cap < 0) {
      throw new Error(`La capacidad del arco (${u}, ${v}) debe ser un número positivo o cero.`)
    }
    validArcs.push({
      id: arc.id || `arc_${i}`,
      name: arc.name || `Arco (${u}, ${v})`,
      from: u,
      to: v,
      capacity: cap,
      flow: 0
    })
  }

  if (validArcs.length === 0) {
    throw new Error('Debes ingresar al menos un arco con capacidad válida.')
  }

  // Recolectar nodos únicos
  const nodeSet = new Set()
  nodeSet.add(sStr)
  nodeSet.add(tStr)
  validArcs.forEach(a => {
    nodeSet.add(a.from)
    nodeSet.add(a.to)
  })
  const nodes = Array.from(nodeSet)
  const nodeIndex = new Map()
  nodes.forEach((n, idx) => nodeIndex.set(n, idx))

  const n = nodes.length
  const sIdx = nodeIndex.get(sStr)
  const tIdx = nodeIndex.get(tStr)

  // Matriz de capacidad residual y arcos dirigidos
  // residual[u][v]
  const capacity = Array.from({ length: n }, () => new Array(n).fill(0))
  const flow = Array.from({ length: n }, () => new Array(n).fill(0))

  validArcs.forEach(a => {
    const u = nodeIndex.get(a.from)
    const v = nodeIndex.get(a.to)
    capacity[u][v] += a.capacity
  })

  const iterations = []
  let totalFlow = 0

  // Edmonds-Karp Loop (BFS)
  while (true) {
    const parent = new Array(n).fill(-1)
    parent[sIdx] = sIdx
    const queue = [sIdx]

    while (queue.length > 0 && parent[tIdx] === -1) {
      const curr = queue.shift()
      for (let next = 0; next < n; next++) {
        // En red residual: capacidad residual = capacity[curr][next] - flow[curr][next] + flow[next][curr] (arcos inversos)
        const residual = (capacity[curr][next] - flow[curr][next])
        if (parent[next] === -1 && residual > 0) {
          parent[next] = curr
          queue.push(next)
        }
      }
    }

    // Si no hay camino de s a t, se alcanzó el flujo máximo
    if (parent[tIdx] === -1) break

    // Determinar cuello de botella delta
    let pathDelta = Infinity
    let curr = tIdx
    const pathNodes = []
    while (curr !== sIdx) {
      pathNodes.unshift(nodes[curr])
      const p = parent[curr]
      const res = capacity[p][curr] - flow[p][curr]
      if (res < pathDelta) pathDelta = res
      curr = p
    }
    pathNodes.unshift(nodes[sIdx])

    // Actualizar flujo a lo largo del camino
    curr = tIdx
    while (curr !== sIdx) {
      const p = parent[curr]
      flow[p][curr] += pathDelta
      flow[curr][p] -= pathDelta
      curr = p
    }

    totalFlow += pathDelta
    iterations.push({
      iterationNum: iterations.length + 1,
      pathStr: pathNodes.join(' ➜ '),
      title: `Iteración ${iterations.length + 1} (${pathNodes.join(' ➜ ')})`,
      delta: pathDelta,
      detail: `Camino aumentante encontrado por BFS con cuello de botella δ = ${pathDelta}. Flujo acumulado: ${totalFlow}.`
    })
  }

  // Corte Mínimo (Min-Cut)
  // Búsqueda de nodos alcanzables desde s en red residual final
  const visitedResidual = new Array(n).fill(false)
  const cutQueue = [sIdx]
  visitedResidual[sIdx] = true

  while (cutQueue.length > 0) {
    const curr = cutQueue.shift()
    for (let next = 0; next < n; next++) {
      if (!visitedResidual[next] && (capacity[curr][next] - flow[curr][next]) > 0) {
        visitedResidual[next] = true
        cutQueue.push(next)
      }
    }
  }

  const S_nodes = []
  const T_nodes = []
  for (let i = 0; i < n; i++) {
    if (visitedResidual[i]) S_nodes.push(nodes[i])
    else T_nodes.push(nodes[i])
  }

  // Arcos del corte (de S a T con capacidad original > 0)
  const cutArcs = []
  let cutCapacitySum = 0

  validArcs.forEach(a => {
    const uIdx = nodeIndex.get(a.from)
    const vIdx = nodeIndex.get(a.to)
    if (visitedResidual[uIdx] && !visitedResidual[vIdx]) {
      cutArcs.push({
        name: a.name,
        from: a.from,
        to: a.to,
        capacity: a.capacity
      })
      cutCapacitySum += a.capacity
    }
  })

  // Generar reporte de arcos con flujo y estado
  const arcsResult = validArcs.map(a => {
    const u = nodeIndex.get(a.from)
    const v = nodeIndex.get(a.to)
    const sentFlow = Math.max(0, flow[u][v])
    const res = Math.max(0, a.capacity - sentFlow)
    const isSat = a.capacity > 0 && sentFlow >= a.capacity
    return {
      ...a,
      flow: sentFlow,
      residual: res,
      saturated: isSat
    }
  })

  return {
    source: sStr,
    sink: tStr,
    maxFlow: totalFlow,
    optimalFlow: `${totalFlow} Unidades`,
    arcsResult,
    minCut: {
      capacity: cutCapacitySum,
      minCutCapacity: `${cutCapacitySum} Unidades`,
      partitionS: S_nodes,
      partitionT: T_nodes,
      cutPartition: `S = {${S_nodes.join(', ')}}  |  T = {${T_nodes.join(', ')}}`,
      cutArcsList: cutArcs,
      cutArcsStr: cutArcs.length > 0
        ? cutArcs.map(c => `(${c.from}, ${c.to}) [cap ${c.capacity}]`).join(' + ') + ` = ${cutCapacitySum}`
        : 'Ningún arco cruza el corte'
    },
    iterations: iterations.length > 0 ? iterations : [
      {
        iterationNum: 1,
        title: 'Sin caminos aumentantes',
        detail: 'No existe ningún camino con capacidad positiva entre la Fuente y el Sumidero. El flujo máximo es 0.'
      }
    ]
  }
}
