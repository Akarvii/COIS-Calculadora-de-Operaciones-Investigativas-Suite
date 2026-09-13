<template>
  <div class="app-root">
    <!-- Navbar Header -->
    <Navbar 
      ref="navbarRef"
      v-model:showFractions="showFractions" 
      :backend-online="backendOnline" 
      @load-example="loadExample"
    />

    <!-- Main 50 / 50 Split Layout -->
    <main class="app-layout">
      <!-- Left Panel: Calculator / Input -->
      <section class="panel panel-left">
        <CalculatorPanel 
          ref="calcPanelRef"
          :is-loading="isLoading"
          :initial-problem="currentProblem"
          @solve="handleSolve"
          @clear="handleClear"
        />
      </section>

      <!-- Right Panel: Processes, Matrices & Step Player -->
      <section class="panel panel-right">
        <ProcessPanel 
          :response="solverResponse"
          :last-request="lastSolvedRequest"
          :is-loading="isLoading"
          :show-fractions="showFractions"
        />
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import confetti from 'canvas-confetti'
import Navbar from './components/Navbar.vue'
import CalculatorPanel from './components/CalculatorPanel.vue'
import ProcessPanel from './components/ProcessPanel.vue'

const API_BASE_URL = 'http://localhost:8000'

const showFractions = ref(true)
const backendOnline = ref(true)
const isLoading = ref(false)

const navbarRef = ref(null)
const calcPanelRef = ref(null)
const currentProblem = ref(null)
const lastSolvedRequest = ref(null)
const solverResponse = ref(null)

// Preset problems catalogue
const presets = {
  classic_production: {
    objective_type: 'MAXIMIZE',
    c: ['3', '5'],
    A: [
      ['1', '0'],
      ['0', '2'],
      ['3', '2']
    ],
    constraint_types: ['<=', '<=', '<='],
    b: ['4', '12', '18']
  },
  mixed_two_phase: {
    objective_type: 'MINIMIZE',
    c: ['4', '1'],
    A: [
      ['3', '1'],
      ['4', '3'],
      ['1', '2']
    ],
    constraint_types: ['=', '>=', '<='],
    b: ['3', '6', '4']
  },
  fractional_optimum: {
    objective_type: 'MAXIMIZE',
    c: ['2', '3'],
    A: [
      ['1', '2'],
      ['3', '2']
    ],
    constraint_types: ['<=', '<='],
    b: ['8', '14']
  },
  unbounded_example: {
    objective_type: 'MAXIMIZE',
    c: ['2', '1'],
    A: [
      ['1', '-1'],
      ['2', '0']
    ],
    constraint_types: ['<=', '<='],
    b: ['10', '40']
  },
  infeasible_example: {
    objective_type: 'MAXIMIZE',
    c: ['3', '2'],
    A: [
      ['1', '1'],
      ['1', '1']
    ],
    constraint_types: ['<=', '>='],
    b: ['2', '4']
  }
}

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`)
    backendOnline.value = res.ok
  } catch {
    backendOnline.value = false
  }
}

function loadExample(exampleId) {
  if (exampleId === 'blank_config') {
    currentProblem.value = {
      objective_type: 'MAXIMIZE',
      c: ['', ''],
      A: [
        ['', ''],
        ['', '']
      ],
      constraint_types: ['<=', '<='],
      b: ['', '']
    }
    solverResponse.value = null
    lastSolvedRequest.value = null
  } else if (presets[exampleId]) {
    currentProblem.value = { ...presets[exampleId] }
  }
}

function handleClear() {
  solverResponse.value = null
  lastSolvedRequest.value = null
  navbarRef.value?.setSelection('blank_config')
}

async function handleSolve({ method, payload }) {
  isLoading.value = true
  lastSolvedRequest.value = payload

  let endpoint = '/api/solve/standard'
  if (method === 'REVISED') {
    endpoint = '/api/solve/revised'
  } else if (method === 'COMPARE') {
    endpoint = '/api/solve/compare'
  }

  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    const data = await res.json()

    if (!res.ok) {
      const errorMsg = data.message || (data.details ? data.details.join(', ') : 'Error en el cálculo')
      calcPanelRef.value?.setErrorMessage(errorMsg)
      solverResponse.value = null
    } else {
      if (method === 'COMPARE') {
        solverResponse.value = data.standard_result
      } else {
        solverResponse.value = data
      }

      // Celebratory confetti every time a model is resolved
      confetti({
        particleCount: 50,
        spread: 70,
        origin: { y: 0.8 }
      })
    }
  } catch (err) {
    calcPanelRef.value?.setErrorMessage('No se pudo conectar con el servidor backend en Python (http://localhost:8000). Asegúrese de que FastAPI esté ejecutándose.')
    backendOnline.value = false
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  checkHealth()
})
</script>

<style scoped>
.app-root {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background: var(--bg-primary);
}
</style>
