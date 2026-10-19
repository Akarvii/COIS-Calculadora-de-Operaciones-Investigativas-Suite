/**
 * Min-Cost Flow (MCFP) Solver — Successive Shortest Path Algorithm
 * 
 * Satisface los balances netos b_i (ofertas > 0, demandas < 0, transbordos = 0)
 * al menor costo unitario global respetando capacidades finitas o infinitas.
 */

export function solveMinCostFlow(rawNodes, rawArcs) {
  if (!rawNodes || rawNodes.length === 0) {
    throw new Error('Debes definir al menos 2 nodos con sus balances.')
  }
  if (!rawArcs || rawArcs.length === 0) {
    throw new Error('Debes ingresar al menos un arco con costo y capacidad.')
  }

  // Parsear nodos
  const nodes = rawNodes.map((n, idx) => {
    const id = String(n.id || n.name || `Nodo ${idx + 1}`).trim()
    const b = Number(n.b || 0)
    if (isNaN(b)) {
      throw new Error(`El balance del nodo "${id}" debe ser numérico.`)
    }
    let role = 'Transbordo'
    let roleClass = 'role-trans'
    if (b > 0) {
      role = 'Origen / Oferta'
      roleClass = 'role-origin'
    } else if (b < 0) {
      role = 'Destino / Demanda'
      roleClass = 'role-dest'
    }
    return { id, name: id, b, role, roleClass }
  })

  // Validar balance global sum(bᵢ) = 0
  const totalBalance = nodes.reduce((sum, n) => sum + n.b, 0)
  if (Math.abs(totalBalance) > 1e-6) {
    throw new Error(`La suma de balances netos debe ser cero: Σ bᵢ = 0. Actualmente la suma es ${totalBalance > 0 ? '+' : ''}${totalBalance}. Ajusta la oferta o la demanda.`)
  }

  const nodeMap = new Map()
  nodes.forEach((n, idx) => nodeMap.set(n.id, idx))
  const numNodes = nodes.length

  // Parsear arcos
  const arcs = []
  for (let i = 0; i < rawArcs.length; i++) {
    const a = rawArcs[i]
    const u = String(a.from || '').trim()
    const v = String(a.to || '').trim()
    if (!u || !v) continue

    if (!nodeMap.has(u)) {
      throw new Error(`El nodo de origen "${u}" no existe en la lista de nodos.`)
    }
    if (!nodeMap.has(v)) {
      throw new Error(`El nodo de destino "${v}" no existe en la lista de nodos.`)
    }

    const cost = Number(a.cost)
    if (isNaN(cost)) {
      throw new Error(`El costo del arco (${u}, ${v}) debe ser un número válido.`)
    }

    let cap = Infinity
    if (a.capacity !== '∞' && a.capacity !== 'inf' && a.capacity !== '' && a.capacity !== null && a.capacity !== undefined) {
      cap = Number(a.capacity)
      if (isNaN(cap) || cap < 0) {
        throw new Error(`La capacidad del arco (${u}, ${v}) debe ser un número no negativo o ∞.`)
      }
    }

    arcs.push({
      id: a.id || `m_arc_${i}`,
      name: a.name || `Arco (${u}, ${v})`,
      from: u,
      to: v,
      uIdx: nodeMap.get(u),
      vIdx: nodeMap.get(v),
      cost,
      capacity: cap,
      capacityDisplay: cap === Infinity ? '∞' : cap,
      flow: 0
    })
  }

  if (arcs.length === 0) {
    throw new Error('No hay arcos válidos configurados.')
  }

  // Successive Shortest Path Implementation
  // Estructura residual: arcos directos e inversos
  const adj = Array.from({ length: numNodes }, () => [])
  const residualEdges = []

  function addResidualEdge(fromIdx, toIdx, cap, cost, originalArcIdx) {
    const e1 = { from: fromIdx, to: toIdx, cap, flow: 0, cost, originalArcIdx, isReverse: false }
    const e2 = { from: toIdx, to: fromIdx, cap: 0, flow: 0, cost: -cost, originalArcIdx, isReverse: true }
    e1.rev = e2
    e2.rev = e1
    adj[fromIdx].push(e1)
    adj[toIdx].push(e2)
    residualEdges.push(e1)
  }

  arcs.forEach((a, aIdx) => {
    addResidualEdge(a.uIdx, a.vIdx, a.capacity, a.cost, aIdx)
  })

  // Vector de balance restante
  const remainingB = nodes.map(n => n.b)
  const iterations = []

  // Bucle: mientras haya un nodo con oferta restante (remainingB > 0)
  while (true) {
    const sourceCandidates = []
    const sinkCandidates = []

    for (let i = 0; i < numNodes; i++) {
      if (remainingB[i] > 1e-6) sourceCandidates.push(i)
      else if (remainingB[i] < -1e-6) sinkCandidates.push(i)
    }

    if (sourceCandidates.length === 0 || sinkCandidates.length === 0) {
      break // Todos los balances satisfechos
    }

    const s = sourceCandidates[0]

    // SPFA / Bellman-Ford para camino de menor costo desde s
    const dist = new Array(numNodes).fill(Infinity)
    const parentEdge = new Array(numNodes).fill(null)
    const inQueue = new Array(numNodes).fill(false)
    dist[s] = 0
    const queue = [s]
    inQueue[s] = true

    while (queue.length > 0) {
      const u = queue.shift()
      inQueue[u] = false

      for (const edge of adj[u]) {
        const residualCap = edge.cap - edge.flow
        if (residualCap > 1e-6 && dist[edge.to] > dist[u] + edge.cost + 1e-9) {
          dist[edge.to] = dist[u] + edge.cost
          parentEdge[edge.to] = edge
          if (!inQueue[edge.to]) {
            queue.push(edge.to)
            inQueue[edge.to] = true
          }
        }
      }
    }

    // Elegir el mejor sumidero alcanzable
    let bestT = -1
    let bestCost = Infinity
    for (const t of sinkCandidates) {
      if (dist[t] < bestCost) {
        bestCost = dist[t]
        bestT = t
      }
    }

    if (bestT === -1) {
      throw new Error(`Red infactible: No existe camino disponible para enviar el flujo restante desde "${nodes[s].name}". Verifica capacidades y conectividad.`)
    }

    // Determinar delta de aumento
    let delta = Math.min(remainingB[s], -remainingB[bestT])
    let curr = bestT
    const pathNodes = []
    while (curr !== s) {
      pathNodes.unshift(nodes[curr].name)
      const edge = parentEdge[curr]
      delta = Math.min(delta, edge.cap - edge.flow)
      curr = edge.from
    }
    pathNodes.unshift(nodes[s].name)

    // Aumentar flujo
    curr = bestT
    while (curr !== s) {
      const edge = parentEdge[curr]
      edge.flow += delta
      edge.rev.flow -= delta
      curr = edge.from
    }

    remainingB[s] -= delta
    remainingB[bestT] += delta

    iterations.push({
      iterationNum: iterations.length + 1,
      title: `Iteración ${iterations.length + 1}: Envío desde ${nodes[s].name} hacia ${nodes[bestT].name}`,
      pathStr: pathNodes.join(' ➜ '),
      delta,
      unitCost: bestCost,
      subtotalCost: delta * bestCost,
      detail: `Camino mínimo: ${pathNodes.join(' ➜ ')} (costo unitario = ${bestCost}). Se enviaron δ = ${delta} unidades. Costo parcial: ${delta * bestCost}.`
    })
  }

  // Asignar flujos a arcos originales
  residualEdges.forEach(re => {
    if (!re.isReverse) {
      arcs[re.originalArcIdx].flow = Math.max(0, re.flow)
    }
  })

  // Calcular costo total Z*
  let totalZ = 0
  const arcsResult = arcs.map(a => {
    const subtotal = a.flow * a.cost
    totalZ += subtotal
    return {
      ...a,
      subtotal
    }
  })

  return {
    optimalZ: totalZ,
    optimalZDisplay: String(totalZ),
    arcsResult,
    nodeBalances: nodes.map(n => ({
      ...n,
      bDisplay: n.b > 0 ? `+${n.b}` : String(n.b)
    })),
    iterations
  }
}
