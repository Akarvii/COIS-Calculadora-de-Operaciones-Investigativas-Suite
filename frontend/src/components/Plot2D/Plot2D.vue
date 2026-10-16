<template>
  <div class="plot-container">
    <div class="plot-header">
      <div class="plot-info">
        <span class="plot-title">Región Factible y Trayectoria Simplex (2D)</span>
        <span class="plot-desc">Plano Cartesiano de variables {{ varNames[0] || 'x1' }} y {{ varNames[1] || 'x2' }}</span>
      </div>
      <div class="plot-legend">
        <span class="legend-item"><span class="dot dot-feasible"></span> Región Factible</span>
        <span class="legend-item"><span class="dot dot-path"></span> Trayectoria Simplex</span>
        <span class="legend-item"><span class="dot dot-optimal"></span> Óptimo Z*</span>
      </div>
    </div>

    <div class="canvas-wrapper" ref="wrapperRef">
      <canvas ref="canvasRef" class="plot-canvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps({
  request: {
    type: Object,
    default: () => ({})
  },
  response: {
    type: Object,
    default: () => ({})
  },
  varNames: {
    type: Array,
    default: () => ['x1', 'x2']
  },
  currentStepIndex: {
    type: Number,
    default: 0
  }
})

const canvasRef = ref(null)
const wrapperRef = ref(null)

function drawPlot() {
  const canvas = canvasRef.value
  if (!canvas || !props.request || !props.request.A || props.request.A[0]?.length !== 2) return

  const ctx = canvas.getContext('2d')
  const width = canvas.width
  const height = canvas.height
  const padding = 45

  ctx.clearRect(0, 0, width, height)

  // 1. Determine bounds
  let maxX = 10
  let maxY = 10

  const A = props.request.A.map(row => row.map(v => parseFloat(eval(v))))
  const b = props.request.b.map(v => parseFloat(eval(v)))
  const c = props.request.c.map(v => parseFloat(eval(v)))
  const types = props.request.constraint_types

  // Find intercepts to scale canvas nicely
  for (let i = 0; i < A.length; i++) {
    const a1 = A[i][0]
    const a2 = A[i][1]
    const bi = b[i]
    if (a1 > 0) maxX = Math.max(maxX, (bi / a1) * 1.25)
    if (a2 > 0) maxY = Math.max(maxY, (bi / a2) * 1.25)
  }

  // Include optimal vertex in bounds
  if (props.response?.solution) {
    const solX = props.response.solution[props.varNames[0]]?.decimal || 0
    const solY = props.response.solution[props.varNames[1]]?.decimal || 0
    maxX = Math.max(maxX, solX * 1.35)
    maxY = Math.max(maxY, solY * 1.35)
  }

  maxX = Math.max(maxX, 8)
  maxY = Math.max(maxY, 8)

  const scaleX = (width - 2 * padding) / maxX
  const scaleY = (height - 2 * padding) / maxY

  function toCanvasX(x) {
    return padding + x * scaleX
  }

  function toCanvasY(y) {
    return height - padding - y * scaleY
  }

  // 2. Draw Grid & Axes
  ctx.strokeStyle = '#1E293B'
  ctx.lineWidth = 1

  // Vertical grid
  const stepX = Math.max(1, Math.ceil(maxX / 8))
  for (let x = 0; x <= maxX; x += stepX) {
    const cx = toCanvasX(x)
    ctx.beginPath()
    ctx.moveTo(cx, padding)
    ctx.lineTo(cx, height - padding)
    ctx.stroke()

    ctx.fillStyle = '#64748B'
    ctx.font = '10px JetBrains Mono'
    ctx.textAlign = 'center'
    ctx.fillText(x.toString(), cx, height - padding + 15)
  }

  // Horizontal grid
  const stepY = Math.max(1, Math.ceil(maxY / 8))
  for (let y = 0; y <= maxY; y += stepY) {
    const cy = toCanvasY(y)
    ctx.beginPath()
    ctx.moveTo(padding, cy)
    ctx.lineTo(width - padding, cy)
    ctx.stroke()

    ctx.fillStyle = '#64748B'
    ctx.font = '10px JetBrains Mono'
    ctx.textAlign = 'right'
    ctx.fillText(y.toString(), padding - 8, cy + 3)
  }

  // Main Axes
  ctx.strokeStyle = '#475569'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(padding, padding)
  ctx.lineTo(padding, height - padding)
  ctx.lineTo(width - padding, height - padding)
  ctx.stroke()

  // Axis Labels
  ctx.fillStyle = '#94A3B8'
  ctx.font = 'bold 12px Inter'
  ctx.textAlign = 'right'
  ctx.fillText(props.varNames[0] || 'x1', width - padding, height - padding + 30)
  ctx.fillText(props.varNames[1] || 'x2', padding - 10, padding - 10)

  // 3. Draw Feasible Region (Point Sampling / Polygon)
  const imgData = ctx.createImageData(width, height)
  for (let px = padding; px < width - padding; px += 2) {
    const mathX = (px - padding) / scaleX
    if (mathX < 0) continue

    for (let py = padding; py < height - padding; py += 2) {
      const mathY = (height - padding - py) / scaleY
      if (mathY < 0) continue

      let isFeasible = true
      for (let i = 0; i < A.length; i++) {
        const lhs = A[i][0] * mathX + A[i][1] * mathY
        const rhs = b[i]
        const type = types[i]
        if ((type === '<=' || type === '<') && lhs > rhs + 0.001) isFeasible = false
        if ((type === '>=' || type === '>') && lhs < rhs - 0.001) isFeasible = false
        if (type === '=' && Math.abs(lhs - rhs) > 0.1) isFeasible = false
        if (!isFeasible) break
      }

      if (isFeasible) {
        ctx.fillStyle = 'rgba(56, 189, 248, 0.18)'
        ctx.fillRect(px, py, 2, 2)
      }
    }
  }

  // 4. Draw Constraint Boundary Lines
  const colors = ['#38BDF8', '#F59E0B', '#A855F7', '#EC4899', '#14B8A6']
  for (let i = 0; i < A.length; i++) {
    const a1 = A[i][0]
    const a2 = A[i][1]
    const bi = b[i]
    ctx.strokeStyle = colors[i % colors.length]
    ctx.lineWidth = 1.5

    ctx.beginPath()
    if (Math.abs(a2) > 0.0001) {
      const y0 = bi / a2
      const yMaxX = (bi - a1 * maxX) / a2
      ctx.moveTo(toCanvasX(0), toCanvasY(y0))
      ctx.lineTo(toCanvasX(maxX), toCanvasY(yMaxX))
    } else if (Math.abs(a1) > 0.0001) {
      const x0 = bi / a1
      ctx.moveTo(toCanvasX(x0), toCanvasY(0))
      ctx.lineTo(toCanvasX(x0), toCanvasY(maxY))
    }
    ctx.stroke()
  }

  // 5. Draw Simplex Trajectory Path
  const iterations = props.response?.tabular_iterations || []
  const pathPoints = []

  // Collect (x1, x2) for each iteration
  for (const step of iterations) {
    let x1 = 0
    let x2 = 0
    for (let r = 0; r < step.basic_vars.length; r++) {
      const bv = step.basic_vars[r]
      const val = step.rhs[r]?.decimal || 0
      if (bv === props.varNames[0] || bv === 'x1') x1 = val
      if (bv === props.varNames[1] || bv === 'x2') x2 = val
    }
    pathPoints.push({ x: x1, y: x2, iter: step.iteration })
  }

  // Draw Path Line
  if (pathPoints.length > 1) {
    ctx.strokeStyle = '#F59E0B'
    ctx.lineWidth = 2.5
    ctx.setLineDash([5, 4])
    ctx.beginPath()
    ctx.moveTo(toCanvasX(pathPoints[0].x), toCanvasY(pathPoints[0].y))
    for (let i = 1; i < pathPoints.length; i++) {
      ctx.lineTo(toCanvasX(pathPoints[i].x), toCanvasY(pathPoints[i].y))
    }
    ctx.stroke()
    ctx.setLineDash([])
  }

  // Draw Vertices on Path
  for (let i = 0; i < pathPoints.length; i++) {
    const pt = pathPoints[i]
    const cx = toCanvasX(pt.x)
    const cy = toCanvasY(pt.y)

    ctx.fillStyle = '#0F172A'
    ctx.strokeStyle = '#F59E0B'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.arc(cx, cy, 5, 0, Math.PI * 2)
    ctx.fill()
    ctx.stroke()

    // Step index label
    ctx.fillStyle = '#F59E0B'
    ctx.font = 'bold 10px JetBrains Mono'
    ctx.fillText(`v${pt.iter}`, cx + 8, cy - 8)
  }

  // 6. Draw Optimal Point
  if (props.response?.solution && props.response.status === 'OPTIMAL') {
    const optX = props.response.solution[props.varNames[0]]?.decimal || 0
    const optY = props.response.solution[props.varNames[1]]?.decimal || 0
    const optCx = toCanvasX(optX)
    const optCy = toCanvasY(optY)

    // Glowing circle
    ctx.fillStyle = '#10B981'
    ctx.beginPath()
    ctx.arc(optCx, optCy, 7, 0, Math.PI * 2)
    ctx.fill()

    ctx.strokeStyle = '#FFFFFF'
    ctx.lineWidth = 2
    ctx.stroke()

    ctx.fillStyle = '#34D399'
    ctx.font = 'bold 11px Inter'
    ctx.fillText(`Óptimo (${optX.toFixed(2)}, ${optY.toFixed(2)})`, optCx + 10, optCy - 10)
  }
}

function resizeCanvas() {
  if (wrapperRef.value && canvasRef.value) {
    const rect = wrapperRef.value.getBoundingClientRect()
    canvasRef.value.width = rect.width || 450
    canvasRef.value.height = 360
    drawPlot()
  }
}

onMounted(() => {
  nextTick(() => {
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)
  })
})

watch(() => [props.request, props.response, props.currentStepIndex], () => {
  nextTick(() => drawPlot())
}, { deep: true })
</script>

<style scoped src="./Plot2D.css"></style>
