<template>
  <div class="process-container">
    <!-- Header -->
    <div class="panel-header">
      <div class="header-left">
        <h2 class="panel-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
          Panel de Procesos y Resultados
        </h2>
        <p class="panel-subtitle">Desglose analítico paso a paso de cada iteración y matrices.</p>
      </div>

      <div v-if="hasResults" class="header-badges">
        <span class="badge" :class="statusBadgeClass">
          {{ response.status }}
        </span>
        <span class="badge badge-blue">
          {{ response.execution_time_ms }} ms
        </span>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!hasResults && !isLoading" class="empty-state">
      <div class="empty-icon-svg">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.41 2.41 0 0 1 0-3.4l2.6-2.6a2.41 2.41 0 0 1 3.4 0Z"/>
          <path d="m14.5 12.5 2-2"/>
          <path d="m11.5 9.5 2-2"/>
          <path d="m8.5 6.5 2-2"/>
          <path d="m17.5 15.5 2-2"/>
        </svg>
      </div>
      <h3>Listo para optimizar</h3>
      <p>Configure los coeficientes del problema en el panel izquierdo y presione <strong>"Resolver Modelo"</strong> para visualizar el proceso detallado paso a paso.</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Calculando matrices y pasos del Simplex...</p>
    </div>

    <!-- Results Display -->
    <div v-if="hasResults && !isLoading" class="results-content">
      <!-- 1. Executive Summary Card -->
      <div class="card summary-card">
        <div class="summary-grid">
          <div class="summary-item">
            <span class="summary-label">Valor Óptimo (Z*):</span>
            <span class="summary-val text-emerald">
              {{ formatVal(response.optimal_value) }}
            </span>
          </div>

          <div v-for="varName in response.variable_names" :key="varName" class="summary-item">
            <span class="summary-label">{{ varName }}:</span>
            <span class="summary-val">
              {{ formatVal(response.solution?.[varName]) }}
            </span>
          </div>
        </div>

        <div class="summary-message">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <span>{{ response.message }}</span>
        </div>
      </div>

      <!-- 2. Sub-Tabs Bar -->
      <div class="tabs-bar">
        <button 
          v-if="hasTabularSteps"
          class="tab-btn" 
          :class="{ active: activeTab === 'TABULAR' }" 
          @click="activeTab = 'TABULAR'"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="18" height="18" x="3" y="3" rx="2" />
            <path d="M3 9h18" />
            <path d="M3 15h18" />
            <path d="M9 3v18" />
            <path d="M15 3v18" />
          </svg>
          <span>Simplex Tabular</span>
        </button>

        <button 
          v-if="hasRevisedSteps"
          class="tab-btn" 
          :class="{ active: activeTab === 'REVISED' }" 
          @click="activeTab = 'REVISED'"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="12 2 2 7 12 12 22 7 12 2" />
            <polyline points="2 17 12 22 22 17" />
            <polyline points="2 12 12 17 22 12" />
          </svg>
          <span>Simplex Revisado (B⁻¹)</span>
        </button>

        <button 
          v-if="response.sensitivity_report"
          class="tab-btn" 
          :class="{ active: activeTab === 'SENSITIVITY' }" 
          @click="activeTab = 'SENSITIVITY'"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
            <polyline points="16 7 22 7 22 13" />
          </svg>
          <span>Sensibilidad & Precios Sombra</span>
        </button>

        <button 
          v-if="is2DProblem"
          class="tab-btn" 
          :class="{ active: activeTab === 'PLOT_2D' }" 
          @click="activeTab = 'PLOT_2D'"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 3v18h18" />
            <circle cx="9" cy="9" r="2" />
            <circle cx="17" cy="13" r="2" />
            <path d="m9 9 8 4" />
          </svg>
          <span>Gráfico 2D</span>
        </button>
      </div>

      <!-- 3. TABULAR SIMPLEX VIEW -->
      <div v-if="activeTab === 'TABULAR' && currentTabularStep" class="tab-view">
        <!-- Step Navigation Bar -->
        <div class="step-player">
          <div class="step-controls">
            <button class="btn btn-secondary btn-sm" @click="currentStepIndex = 0" :disabled="currentStepIndex === 0" title="Primera iteración">
              ⏮ Inicio
            </button>
            <button class="btn btn-secondary btn-sm" @click="prevStep" :disabled="currentStepIndex === 0">
              ◀ Anterior
            </button>
            
            <!-- Quick Step Buttons -->
            <div class="step-pills">
              <button 
                v-for="(step, idx) in response.tabular_iterations" 
                :key="'pill_' + idx"
                class="step-pill"
                :class="{ active: currentStepIndex === idx }"
                @click="currentStepIndex = idx"
              >
                {{ idx + 1 }}
              </button>
            </div>

            <button class="btn btn-primary btn-sm" @click="nextStep" :disabled="currentStepIndex >= totalSteps - 1">
              Siguiente ▶
            </button>
            <button class="btn btn-secondary btn-sm" @click="currentStepIndex = totalSteps - 1" :disabled="currentStepIndex >= totalSteps - 1" title="Última iteración">
              Fin ⏭
            </button>
          </div>

          <div class="phase-indicators">
            <span 
              class="phase-badge" 
              :class="{ 
                'phase-active': (currentTabularStep.phase || 1) === 1,
                'phase-completed': (currentTabularStep.phase || 1) > 1
              }"
            >
              <span v-if="(currentTabularStep.phase || 1) > 1" class="check-icon">✓</span>
              Fase 1
            </span>

            <span 
              class="phase-badge" 
              :class="{ 
                'phase-active': currentTabularStep.phase === 2,
                'phase-disabled': !hasPhase2Tabular
              }"
              :title="!hasPhase2Tabular ? 'Fase 2 desactivada (no requerida para restricciones ≤)' : 'Fase 2: Optimización de Z'"
            >
              Fase 2
            </span>
          </div>
        </div>

        <!-- Step Narrative Explanation -->
        <div class="step-narrative">
          <strong>Explicación del Paso:</strong>
          <p>{{ currentTabularStep.description }}</p>
        </div>

        <!-- Simplex Table -->
        <div class="card overflow-x">
          <div class="card-header">
            <span class="card-title">Tabla Simplex - Iteración {{ currentTabularStep.iteration }}</span>
            <div class="table-legend">
              <span class="legend-box pivot-col-box">Entrante</span>
              <span class="legend-box pivot-row-box">Saliente</span>
              <span class="legend-box pivot-elem-box">Pivote</span>
            </div>
          </div>

          <table class="matrix-table">
            <thead>
              <tr>
                <th class="th-basic">Base</th>
                <th 
                  v-for="(header, colIdx) in currentTabularStep.headers" 
                  :key="header"
                  :class="{ 'pivot-col': colIdx === currentTabularStep.pivot_col }"
                >
                  {{ header }}
                </th>
              </tr>
            </thead>
            <tbody>
              <!-- Constraint Rows -->
              <tr 
                v-for="(row, rowIdx) in currentTabularStep.matrix.slice(0, -1)" 
                :key="'r_' + rowIdx"
                :class="{ 'pivot-row': rowIdx === currentTabularStep.pivot_row }"
              >
                <td class="td-basic">{{ currentTabularStep.basic_vars[rowIdx] }}</td>
                <td 
                  v-for="(val, colIdx) in row" 
                  :key="'c_' + rowIdx + '_' + colIdx"
                  :class="{
                    'pivot-col': colIdx === currentTabularStep.pivot_col,
                    'pivot-element': rowIdx === currentTabularStep.pivot_row && colIdx === currentTabularStep.pivot_col
                  }"
                >
                  {{ formatVal(val) }}
                </td>
                <!-- RHS -->
                <td>{{ formatVal(currentTabularStep.rhs[rowIdx]) }}</td>
              </tr>

              <!-- Objective Row(s) -->
              <tr class="obj-row">
                <td class="td-basic">Z</td>
                <td 
                  v-for="(val, colIdx) in currentTabularStep.matrix[currentTabularStep.matrix.length - 1]" 
                  :key="'obj_' + colIdx"
                  :class="{ 'pivot-col': colIdx === currentTabularStep.pivot_col }"
                >
                  {{ formatVal(val) }}
                </td>
                <td>{{ formatVal(currentTabularStep.rhs[currentTabularStep.rhs.length - 1]) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Ratios Table -->
        <div v-if="currentTabularStep.ratios && currentTabularStep.ratios.length > 0" class="card">
          <div class="card-header">
            <span class="card-title">Prueba de la Razón Mínima (θ = bᵢ / aᵢₖ)</span>
          </div>

          <table class="matrix-table">
            <thead>
              <tr>
                <th>Fila</th>
                <th>Variable Básica</th>
                <th>Lado Derecho (bᵢ)</th>
                <th>Elemento Columna (aᵢₖ)</th>
                <th>Razón (bᵢ / aᵢₖ)</th>
                <th>Decisión</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="r in currentTabularStep.ratios" 
                :key="'ratio_' + r.row_index"
                :class="{ 'pivot-row': r.is_minimum }"
              >
                <td class="text-center">Fila {{ r.row_index + 1 }}</td>
                <td class="text-center font-bold text-blue">{{ r.basic_var }}</td>
                <td>{{ formatVal(r.rhs) }}</td>
                <td>{{ formatVal(r.pivot_col_val) }}</td>
                <td class="font-mono">
                  {{ r.is_valid ? formatVal(r.ratio) : '— (aᵢₖ ≤ 0)' }}
                </td>
                <td>
                  <span v-if="r.is_minimum" class="badge badge-amber">Mínima (Variable Saliente)</span>
                  <span v-else-if="r.is_valid" class="text-dim">Factible</span>
                  <span v-else class="text-dim">No aplica</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 4. REVISED SIMPLEX VIEW -->
      <div v-if="activeTab === 'REVISED' && currentRevisedStep" class="tab-view">
        <!-- Step Navigation Bar -->
        <div class="step-player">
          <div class="step-controls">
            <button class="btn btn-secondary btn-sm" @click="currentStepIndex = 0" :disabled="currentStepIndex === 0">
              ⏮ Inicio
            </button>
            <button class="btn btn-secondary btn-sm" @click="prevStep" :disabled="currentStepIndex === 0">
              ◀ Anterior
            </button>

            <!-- Quick Step Buttons -->
            <div class="step-pills">
              <button 
                v-for="(step, idx) in response.revised_iterations" 
                :key="'rev_pill_' + idx"
                class="step-pill"
                :class="{ active: currentStepIndex === idx }"
                @click="currentStepIndex = idx"
              >
                {{ idx + 1 }}
              </button>
            </div>

            <button class="btn btn-primary btn-sm" @click="nextStep" :disabled="currentStepIndex >= totalSteps - 1">
              Siguiente ▶
            </button>
            <button class="btn btn-secondary btn-sm" @click="currentStepIndex = totalSteps - 1" :disabled="currentStepIndex >= totalSteps - 1">
              Fin ⏭
            </button>
          </div>

          <div class="phase-indicators">
            <span 
              class="phase-badge" 
              :class="{ 
                'phase-active': (currentRevisedStep.phase || 1) === 1,
                'phase-completed': (currentRevisedStep.phase || 1) > 1
              }"
            >
              <span v-if="(currentRevisedStep.phase || 1) > 1" class="check-icon">✓</span>
              Fase 1
            </span>

            <span 
              class="phase-badge" 
              :class="{ 
                'phase-active': currentRevisedStep.phase === 2,
                'phase-disabled': !hasPhase2Revised
              }"
              :title="!hasPhase2Revised ? 'Fase 2 desactivada (no requerida para restricciones ≤)' : 'Fase 2: Optimización de Z'"
            >
              Fase 2
            </span>
          </div>
        </div>

        <div class="step-narrative">
          <strong>Estado de la Base:</strong>
          <p>{{ currentRevisedStep.description }}</p>
        </div>

        <!-- Matrix Cards Grid -->
        <div class="revised-grid">
          <!-- B Inverted Matrix -->
          <div class="card">
            <div class="card-header">
              <span class="card-title">Matriz Inversa de la Base (B⁻¹)</span>
            </div>
            <div class="matrix-box">
              <table class="matrix-table text-center">
                <tbody>
                  <tr v-for="(row, r) in currentRevisedStep.B_inv" :key="'binv_' + r">
                    <td v-for="(val, c) in row" :key="'binv_c_' + r + '_' + c">
                      {{ formatVal(val) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="matrix-footer">
              Variables Básicas: <strong>[{{ currentRevisedStep.basic_vars.join(', ') }}]</strong>
            </div>
          </div>

          <!-- Dual Multipliers Vector pi -->
          <div class="card">
            <div class="card-header">
              <span class="card-title">Multiplicadores Duales (πᵀ = c_Bᵀ · B⁻¹)</span>
            </div>
            <div class="vector-display">
              <div v-for="(piVal, i) in currentRevisedStep.pi_multipliers" :key="'pi_' + i" class="vector-item">
                <span class="vector-sub">π{{ i + 1 }}</span>
                <span class="vector-val">{{ formatVal(piVal) }}</span>
              </div>
            </div>
            <div class="matrix-footer">
              Valor actual Z = <strong>{{ formatVal(currentRevisedStep.current_Z) }}</strong>
            </div>
          </div>
        </div>

        <!-- Reduced Costs Pricing Table -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Costos Reducidos Bajo Demanda (c̄ⱼ = cⱼ − πᵀ · Aⱼ)</span>
          </div>
          <table class="matrix-table">
            <thead>
              <tr>
                <th>Variable No Básica</th>
                <th>Costo Reducido (c̄ⱼ)</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(rcVal, varName) in currentRevisedStep.reduced_costs" :key="'rc_' + varName">
                <td class="font-bold text-blue">{{ varName }}</td>
                <td class="font-mono">{{ formatVal(rcVal) }}</td>
                <td>
                  <span v-if="varName === currentRevisedStep.entering_var" class="badge badge-green">
                    Variable Entrante (Mejora Z)
                  </span>
                  <span v-else-if="rcVal.decimal <= 0" class="text-dim">
                    Óptimo local (c̄ ≤ 0)
                  </span>
                  <span v-else class="text-muted">
                    Candidato factible
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Transformed Column d = B^-1 * Ak -->
        <div v-if="currentRevisedStep.transformed_col_d" class="card">
          <div class="card-header">
            <span class="card-title">Columna Transformada del Entrante (d = B⁻¹ · Aₖ)</span>
            <span class="badge badge-blue">Entra: {{ currentRevisedStep.entering_var }}</span>
          </div>

          <div class="vector-display">
            <div v-for="(dVal, i) in currentRevisedStep.transformed_col_d" :key="'d_' + i" class="vector-item">
              <span class="vector-sub">d{{ i + 1 }} (fila {{ currentRevisedStep.basic_vars[i] }})</span>
              <span class="vector-val">{{ formatVal(dVal) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 5. SENSITIVITY REPORT VIEW -->
      <div v-if="activeTab === 'SENSITIVITY' && response.sensitivity_report" class="tab-view">
        <!-- Decision Variables Sensitivity -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Análisis de Variables de Decisión (Coeficientes cⱼ)</span>
          </div>

          <table class="matrix-table">
            <thead>
              <tr>
                <th>Variable</th>
                <th>Valor Final</th>
                <th>Costo Reducido</th>
                <th>Coef. Actual (cⱼ)</th>
                <th>Límite Inferior</th>
                <th>Límite Superior</th>
                <th>Tipo</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="v in response.sensitivity_report.variables" :key="'sen_v_' + v.name">
                <td class="font-bold text-blue">{{ v.name }}</td>
                <td>{{ formatVal(v.final_value) }}</td>
                <td>{{ formatVal(v.reduced_cost) }}</td>
                <td class="font-bold">{{ formatVal(v.objective_coefficient) }}</td>
                <td>{{ v.allowable_min ? formatVal(v.allowable_min) : '−∞' }}</td>
                <td>{{ v.allowable_max ? formatVal(v.allowable_max) : '+∞' }}</td>
                <td>
                  <span class="badge" :class="v.status === 'BASIC' ? 'badge-blue' : 'badge-amber'">
                    {{ v.status === 'BASIC' ? 'Básica' : 'No Básica' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Constraints Sensitivity & Shadow Prices -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Análisis de Restricciones & Precios Sombra (Lado Derecho bᵢ)</span>
          </div>

          <table class="matrix-table">
            <thead>
              <tr>
                <th>Restricción</th>
                <th>Holgura / Exceso</th>
                <th>Precio Sombra (Dual)</th>
                <th>Lado Der. (bᵢ)</th>
                <th>Mínimo Permisible</th>
                <th>Máximo Permisible</th>
                <th>Condición</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in response.sensitivity_report.constraints" :key="'sen_c_' + c.index">
                <td class="font-bold">{{ c.name }}</td>
                <td>{{ formatVal(c.slack_surplus_value) }}</td>
                <td class="font-bold text-emerald">{{ formatVal(c.shadow_price) }}</td>
                <td>{{ formatVal(c.rhs_value) }}</td>
                <td>{{ c.allowable_min ? formatVal(c.allowable_min) : '−∞' }}</td>
                <td>{{ c.allowable_max ? formatVal(c.allowable_max) : '+∞' }}</td>
                <td>
                  <span class="badge" :class="c.status === 'BINDING' ? 'badge-rose' : 'badge-green'">
                    {{ c.status === 'BINDING' ? 'Activa (Agotada)' : 'Inactiva (Sobrante)' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 6. 2D PLOT VIEW -->
      <div v-if="activeTab === 'PLOT_2D' && is2DProblem" class="tab-view">
        <Plot2D 
          :request="lastRequest" 
          :response="response" 
          :var-names="response.variable_names" 
          :current-step-index="currentStepIndex"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Plot2D from '../Plot2D/Plot2D.vue'

const props = defineProps({
  response: {
    type: Object,
    default: null
  },
  lastRequest: {
    type: Object,
    default: null
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  showFractions: {
    type: Boolean,
    default: true
  }
})

const activeTab = ref('TABULAR')
const currentStepIndex = ref(0)

const hasResults = computed(() => !!props.response && props.response.status !== 'ERROR')
const hasTabularSteps = computed(() => props.response?.tabular_iterations?.length > 0)
const hasRevisedSteps = computed(() => props.response?.revised_iterations?.length > 0)
const is2DProblem = computed(() => props.lastRequest?.c?.length === 2)

const hasPhase2Tabular = computed(() => {
  return props.response?.tabular_iterations?.some(s => s.phase === 2) || false
})

const hasPhase2Revised = computed(() => {
  return props.response?.revised_iterations?.some(s => s.phase === 2) || false
})

const totalSteps = computed(() => {
  if (activeTab.value === 'TABULAR') {
    return props.response?.tabular_iterations?.length || 0
  } else if (activeTab.value === 'REVISED') {
    return props.response?.revised_iterations?.length || 0
  }
  return 0
})

const currentTabularStep = computed(() => {
  return props.response?.tabular_iterations?.[currentStepIndex.value] || null
})

const currentRevisedStep = computed(() => {
  return props.response?.revised_iterations?.[currentStepIndex.value] || null
})

const statusBadgeClass = computed(() => {
  switch (props.response?.status) {
    case 'OPTIMAL': return 'badge-green'
    case 'MULTIPLE_OPTIMAL': return 'badge-blue'
    case 'UNBOUNDED': return 'badge-amber'
    case 'INFEASIBLE': return 'badge-rose'
    default: return 'badge-amber'
  }
})

function formatVal(val) {
  if (!val) return '0'
  if (typeof val === 'number') return props.showFractions ? val.toString() : val.toFixed(4)
  if (props.showFractions) {
    return val.fraction || '0'
  } else {
    return typeof val.decimal === 'number' ? val.decimal.toFixed(4) : val.decimal
  }
}

function nextStep() {
  if (currentStepIndex.value < totalSteps.value - 1) {
    currentStepIndex.value++
  }
}

function prevStep() {
  if (currentStepIndex.value > 0) {
    currentStepIndex.value--
  }
}

watch(() => props.response, (newResp) => {
  currentStepIndex.value = 0
  if (newResp) {
    if (newResp.tabular_iterations?.length > 0) {
      activeTab.value = 'TABULAR'
    } else if (newResp.revised_iterations?.length > 0) {
      activeTab.value = 'REVISED'
    }
  }
})

watch(activeTab, () => {
  currentStepIndex.value = 0
})
</script>

<style scoped src="./ProcessPanel.css"></style>
