<template>
  <div class="app-root">
    <!-- Transición fluida de escena completa (Navbar + Contenido) -->
    <Transition name="screen-fade" mode="out-in">
      <!-- PANTALLA 1: HUB PRINCIPAL (COIS) -->
      <div v-if="!activeModule" key="hub" class="full-screen-scene">
        <Navbar 
          :active-module="null"
          :api-status="apiStatus"
        />
        <div class="scene-body">
          <ModuleSelector @select="handleSelectModule" />
        </div>
      </div>

      <!-- PANTALLA 2: MÓDULO I - COIS-IMS (Simplex) -->
      <div v-else-if="activeModule === 'cims'" key="cims" class="full-screen-scene">
        <Navbar 
          ref="navbarRef"
          active-module="cims"
          :api-status="apiStatus"
          v-model:showFractions="showFractions" 
          @load-example="loadExample"
          @back-to-selector="activeModule = null"
        />
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

      <!-- PANTALLA 3: MÓDULO II - COIS-Networks (Redes) -->
      <div v-else-if="activeModule === 'networks'" key="networks" class="full-screen-scene">
        <Navbar 
          active-module="networks"
          :api-status="apiStatus"
          v-model:networksTab="networksTab"
          @back-to-selector="activeModule = null"
        />
        <div class="scene-body">
          <NetworksApp :active-tab="networksTab" />
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import confetti from 'canvas-confetti'
import ModuleSelector from './components/ModuleSelector/ModuleSelector.vue'
import NetworksApp from './components/NetworksApp/NetworksApp.vue'
import Navbar from './components/Navbar/Navbar.vue'
import CalculatorPanel from './components/CalculatorPanel/CalculatorPanel.vue'
import ProcessPanel from './components/ProcessPanel/ProcessPanel.vue'

const API_BASE_URL = 'http://localhost:8000'

// Estado del módulo activo: null = selector COIS, 'cims' = COIS-IMS, 'networks' = COIS-Networks
const activeModule = ref(null)
const networksTab = ref('assignment')

// Estado reactivo de la API: 'connected' | 'disconnected' | 'error'
const apiStatus = ref('connected')
const showFractions = ref(true)
const isLoading = ref(false)

const navbarRef = ref(null)
const calcPanelRef = ref(null)
const currentProblem = ref(null)
const lastSolvedRequest = ref(null)
const solverResponse = ref(null)

function handleSelectModule(moduleKey) {
  activeModule.value = moduleKey
}

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
    if (res.ok) {
      apiStatus.value = 'connected'
    } else {
      apiStatus.value = 'error'
    }
  } catch {
    apiStatus.value = 'disconnected'
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
      apiStatus.value = 'error'
      const errorMsg = data.message || (data.details ? data.details.join(', ') : 'Error en el cálculo')
      calcPanelRef.value?.setErrorMessage(errorMsg)
      solverResponse.value = null
    } else {
      apiStatus.value = 'connected'
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
    apiStatus.value = 'disconnected'
    calcPanelRef.value?.setErrorMessage('No se pudo conectar con el servidor backend en Python (http://localhost:8000). Asegúrese de que FastAPI esté ejecutándose.')
  } finally {
    isLoading.value = false
  }
}

let healthInterval = null

onMounted(() => {
  checkHealth()
  healthInterval = setInterval(checkHealth, 8000)
})

onUnmounted(() => {
  if (healthInterval) clearInterval(healthInterval)
})
</script>

<style scoped>
.app-root {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background: var(--bg-primary);
  overflow: hidden;
  position: relative;
}

.full-screen-scene {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  position: absolute;
  top: 0;
  left: 0;
}

.scene-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: calc(100vh - 64px);
  width: 100%;
}

/* Transición cinemática y orgánica para la pantalla completa (Navbar + Cuerpo) */
.screen-fade-enter-active,
.screen-fade-leave-active {
  transition: opacity 0.28s cubic-bezier(0.25, 1, 0.5, 1), transform 0.28s cubic-bezier(0.25, 1, 0.5, 1);
}

.screen-fade-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.994);
}

.screen-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(1.006);
}
</style>
