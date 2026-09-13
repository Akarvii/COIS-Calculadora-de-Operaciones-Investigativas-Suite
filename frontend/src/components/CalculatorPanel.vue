<template>
  <div class="calculator-container">
    <div class="panel-header">
      <div class="header-left">
        <h2 class="panel-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="16" height="20" x="4" y="2" rx="2" />
            <line x1="8" x2="16" y1="6" y2="6" />
            <line x1="16" x2="16" y1="14" y2="18" />
            <path d="M16 10h.01" />
            <path d="M12 10h.01" />
            <path d="M8 10h.01" />
            <path d="M12 14h.01" />
            <path d="M8 14h.01" />
            <path d="M12 18h.01" />
            <path d="M8 18h.01" />
          </svg>
          Definición del Problema Lineal
        </h2>
        <p class="panel-subtitle">Ingrese coeficientes exactos (enteros, decimales o fracciones como 3/4).</p>
      </div>
      <button class="btn btn-clear-all" @click="resetToDefault" title="Vaciar todos los campos para un nuevo problema">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 6h18"/>
          <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
          <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
          <line x1="10" x2="10" y1="11" y2="17"/>
          <line x1="14" x2="14" y1="11" y2="17"/>
        </svg>
        <span>Limpiar Campos</span>
      </button>
    </div>

    <!-- 1. Dimensiones & Configuración Básica -->
    <div class="card">
      <div class="grid-controls">
        <!-- Objetivo -->
        <div class="control-col">
          <label class="form-label">Objetivo:</label>
          <div class="segmented-control">
            <button 
              type="button"
              class="seg-btn" 
              :class="{ active: model.objective_type === 'MAXIMIZE' }" 
              @click="model.objective_type = 'MAXIMIZE'"
            >
              Maximizar (Max)
            </button>
            <button 
              type="button"
              class="seg-btn" 
              :class="{ active: model.objective_type === 'MINIMIZE' }" 
              @click="model.objective_type = 'MINIMIZE'"
            >
              Minimizar (Min)
            </button>
          </div>
        </div>

        <!-- Método de Resolución -->
        <div class="control-col">
          <label class="form-label">Método a Evaluar:</label>
          <select class="select-box w-full" v-model="selectedMethod">
            <option value="STANDARD">Simplex Tabular Tradicional</option>
            <option value="REVISED">Simplex Revisado (Matricial B⁻¹)</option>
            <option value="COMPARE">Comparativa (Ambos Métodos)</option>
          </select>
        </div>

        <!-- Número de Variables -->
        <div class="control-col-compact">
          <label class="form-label">Variables (n):</label>
          <div class="counter-control">
            <button class="btn-counter" @click="removeVariable" :disabled="numVars <= 1">−</button>
            <span class="counter-value">{{ numVars }}</span>
            <button class="btn-counter" @click="addVariable" :disabled="numVars >= 10">+</button>
          </div>
        </div>

        <!-- Número de Restricciones -->
        <div class="control-col-compact">
          <label class="form-label">Restricciones (m):</label>
          <div class="counter-control">
            <button class="btn-counter" @click="removeConstraint" :disabled="numConstraints <= 1">−</button>
            <span class="counter-value">{{ numConstraints }}</span>
            <button class="btn-counter" @click="addConstraint" :disabled="numConstraints >= 12">+</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. Función Objetivo (Z) -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">Función Objetivo (Z)</span>
        <span class="badge badge-blue">{{ model.objective_type }}</span>
      </div>

      <div class="equation-row">
        <span class="obj-symbol">{{ model.objective_type === 'MAXIMIZE' ? 'Max Z =' : 'Min Z =' }}</span>
        <div class="terms-container">
          <div v-for="(cVal, j) in model.c" :key="'c_' + j" class="term-box">
            <input 
              type="text" 
              class="input-number input-coeff" 
              v-model="model.c[j]" 
              placeholder="0"
              @keydown.enter="triggerSolve"
            />
            <span class="var-label">{{ varNames[j] }}</span>
            <span v-if="j < model.c.length - 1" class="plus-sign">+</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Matriz de Restricciones -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">Restricciones Tecnológicas</span>
        <button class="btn btn-add-row" @click="addConstraint" :disabled="numConstraints >= 12" title="Agregar una nueva restricción">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span>Agregar Fila</span>
        </button>
      </div>

      <div class="constraints-table-wrapper">
        <table class="constraints-input-table">
          <thead>
            <tr>
              <th class="th-num">#</th>
              <th v-for="j in numVars" :key="'hdr_v_' + j" class="th-var">
                {{ varNames[j - 1] }}
              </th>
              <th class="th-op">Op</th>
              <th class="th-rhs">Lado Der. (b)</th>
              <th class="th-del"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in model.A" :key="'row_' + i">
              <td class="td-num">R{{ i + 1 }}</td>
              <td v-for="(val, j) in row" :key="'cell_' + i + '_' + j">
                <input 
                  type="text" 
                  class="input-number w-full" 
                  v-model="model.A[i][j]" 
                  placeholder="0"
                  @keydown.enter="triggerSolve"
                />
              </td>
              <td class="td-op">
                <select class="select-box select-op" v-model="model.constraint_types[i]">
                  <option value="<=">&le; (Menor o igual)</option>
                  <option value=">=">&ge; (Mayor o igual)</option>
                  <option value="=">= (Igualdad estricta)</option>
                </select>
              </td>
              <td class="td-rhs">
                <input 
                  type="text" 
                  class="input-number w-full" 
                  v-model="model.b[i]" 
                  placeholder="0"
                  @keydown.enter="triggerSolve"
                />
              </td>
              <td class="td-del">
                <button 
                  class="btn-icon text-rose" 
                  @click="deleteSpecificConstraint(i)" 
                  :disabled="numConstraints <= 1"
                  title="Eliminar esta restricción"
                >
                  ✕
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Non-negativity condition label -->
      <div class="non-negativity">
        Condición de No Negatividad: 
        <strong>{{ varNames.join(', ') }} &ge; 0</strong>
      </div>
    </div>

    <!-- 4. Opciones Avanzadas & Seguridad -->
    <div class="card security-card">
      <div class="card-header">
        <span class="card-title">Protección y Control</span>
      </div>
      <div class="options-row">
        <label class="checkbox-label">
          <input type="checkbox" v-model="model.use_blands_rule" />
          <span>Regla de Bland (Anti-ciclado por degeneración)</span>
        </label>
        <div class="max-iter-box">
          <span class="form-label-inline">Máx. Iteraciones:</span>
          <input type="number" class="input-number input-iter" v-model.number="model.max_iterations" min="5" max="300" />
        </div>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="errorMessage" class="error-banner">
      <div class="error-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
      </div>
      <div class="error-content">
        <strong>Error en el Modelo:</strong>
        <p>{{ errorMessage }}</p>
      </div>
      <button class="error-close" @click="errorMessage = ''">✕</button>
    </div>

    <!-- Action Button -->
    <div class="action-footer">
      <button 
        class="btn btn-primary btn-solve" 
        @click="triggerSolve" 
        :disabled="isLoading"
      >
        <svg v-if="!isLoading" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
        <div v-else class="spinner"></div>
        <span>{{ isLoading ? 'Optimizando modelo...' : 'Resolver Modelo' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch } from 'vue'

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  },
  initialProblem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['solve', 'clear'])

const selectedMethod = ref('STANDARD')
const errorMessage = ref('')

const model = reactive({
  objective_type: 'MAXIMIZE',
  c: ['', ''],
  A: [
    ['', ''],
    ['', '']
  ],
  constraint_types: ['<=', '<='],
  b: ['', ''],
  max_iterations: 100,
  use_blands_rule: true
})

const numVars = computed(() => model.c.length)
const numConstraints = computed(() => model.A.length)
const varNames = computed(() => Array.from({ length: numVars.value }, (_, i) => `x${i + 1}`))

function addVariable() {
  if (numVars.value >= 10) return
  model.c.push('0')
  for (let i = 0; i < model.A.length; i++) {
    model.A[i].push('0')
  }
}

function removeVariable() {
  if (numVars.value <= 1) return
  model.c.pop()
  for (let i = 0; i < model.A.length; i++) {
    model.A[i].pop()
  }
}

function addConstraint() {
  if (numConstraints.value >= 12) return
  const newRow = Array(numVars.value).fill('0')
  model.A.push(newRow)
  model.constraint_types.push('<=')
  model.b.push('0')
}

function removeConstraint() {
  if (numConstraints.value <= 1) return
  model.A.pop()
  model.constraint_types.pop()
  model.b.pop()
}

function deleteSpecificConstraint(index) {
  if (numConstraints.value <= 1) return
  model.A.splice(index, 1)
  model.constraint_types.splice(index, 1)
  model.b.splice(index, 1)
}

function resetToDefault() {
  // Empty all fields for a fresh problem from scratch
  model.objective_type = 'MAXIMIZE'
  model.c = ['', '']
  model.A = [
    ['', ''],
    ['', '']
  ]
  model.constraint_types = ['<=', '<=']
  model.b = ['', '']
  errorMessage.value = ''
  emit('clear')
}

function loadPreset(preset) {
  if (!preset) return
  model.objective_type = preset.objective_type || 'MAXIMIZE'
  model.c = preset.c.map(v => String(v))
  model.A = preset.A.map(row => row.map(v => String(v)))
  model.constraint_types = [...preset.constraint_types]
  model.b = preset.b.map(v => String(v))
  errorMessage.value = ''
}

watch(() => props.initialProblem, (newVal) => {
  if (newVal) {
    loadPreset(newVal)
  }
}, { deep: true })

function triggerSolve() {
  errorMessage.value = ''
  
  // Basic pre-validation
  for (let j = 0; j < model.c.length; j++) {
    if (!model.c[j] || model.c[j].trim() === '') {
      errorMessage.value = `El coeficiente de ${varNames.value[j]} en la función objetivo no puede estar vacío.`
      return
    }
  }

  for (let i = 0; i < model.A.length; i++) {
    for (let j = 0; j < model.A[i].length; j++) {
      if (!model.A[i][j] || model.A[i][j].trim() === '') {
        errorMessage.value = `El coeficiente R${i + 1}, ${varNames.value[j]} no puede estar vacío.`
        return
      }
    }
    if (!model.b[i] || model.b[i].trim() === '') {
      errorMessage.value = `El lado derecho de la restricción R${i + 1} no puede estar vacío.`
      return
    }
  }

  emit('solve', {
    method: selectedMethod.value,
    payload: {
      objective_type: model.objective_type,
      c: model.c,
      A: model.A,
      constraint_types: model.constraint_types,
      b: model.b,
      variable_names: varNames.value,
      max_iterations: model.max_iterations,
      use_blands_rule: model.use_blands_rule
    }
  })
}

defineExpose({
  loadPreset,
  setErrorMessage: (msg) => { errorMessage.value = msg }
})
</script>

<style scoped>
.calculator-container {
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.grid-controls {
  display: grid;
  grid-template-columns: 1fr 1fr auto auto;
  gap: 14px;
  align-items: flex-end;
}

.control-col {
  display: flex;
  flex-direction: column;
}

.control-col-compact {
  display: flex;
  flex-direction: column;
}

.w-full {
  width: 100%;
}

.segmented-control {
  display: flex;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 2px;
}

.seg-btn {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 500;
  padding: 5px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.seg-btn.active {
  background: #1E293B;
  color: var(--accent-blue);
  font-weight: 600;
}

.counter-control {
  display: flex;
  align-items: center;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
}

.btn-counter {
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  color: var(--text-main);
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-counter:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.btn-counter:hover:not(:disabled) {
  background: var(--bg-card-hover);
}

.counter-value {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0 8px;
  color: var(--accent-blue);
}

/* Equation row styling */
.equation-row {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow-x: auto;
  padding: 8px 4px;
}

.obj-symbol {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--accent-blue);
  white-space: nowrap;
}

.terms-container {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.term-box {
  display: flex;
  align-items: center;
  gap: 6px;
}

.input-coeff {
  width: 60px;
}

.var-label {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-main);
}

.plus-sign {
  color: var(--text-dim);
  font-weight: 600;
  margin-left: 2px;
}

/* Constraints Table */
.constraints-table-wrapper {
  overflow-x: auto;
  margin-bottom: 10px;
}

.constraints-input-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 6px;
}

.constraints-input-table th {
  font-size: 0.76rem;
  color: var(--text-muted);
  font-weight: 600;
  padding: 4px;
  text-align: center;
}

.th-num {
  width: 36px;
}

.th-op {
  width: 120px;
}

.th-rhs {
  width: 80px;
}

.th-del {
  width: 30px;
}

.td-num {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--text-dim);
  text-align: center;
}

.select-op {
  width: 100%;
  font-size: 0.8rem;
  padding: 6px 4px;
}

.text-rose {
  color: var(--accent-rose);
}

.non-negativity {
  font-size: 0.78rem;
  color: var(--text-dim);
  padding-top: 6px;
  border-top: 1px dashed var(--border-color);
}

.non-negativity strong {
  color: var(--text-muted);
  font-family: var(--font-mono);
}

/* Security card */
.security-card {
  padding: 12px 16px;
  margin-bottom: 16px;
}

.options-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--text-muted);
  cursor: pointer;
}

.max-iter-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-label-inline {
  font-size: 0.78rem;
  color: var(--text-dim);
}

.input-iter {
  width: 65px;
}

/* Error Banner */
.error-banner {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.35);
  border-radius: var(--radius-md);
  padding: 12px 16px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.error-icon {
  font-size: 1.2rem;
}

.error-content {
  flex: 1;
  font-size: 0.82rem;
  color: #FCA5A5;
}

.error-content strong {
  display: block;
  margin-bottom: 2px;
  color: #EF4444;
}

.error-close {
  background: transparent;
  border: none;
  color: #FCA5A5;
  font-size: 1rem;
  cursor: pointer;
}

/* Action & Clear Buttons */
.btn-add-row {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(16, 185, 129, 0.08);
  color: #34D399;
  border: 1px solid rgba(16, 185, 129, 0.25);
  padding: 5px 11px;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-add-row:hover:not(:disabled) {
  background: rgba(16, 185, 129, 0.18);
  border-color: rgba(16, 185, 129, 0.45);
  color: #6EE7B7;
  transform: translateY(-1px);
}

.btn-add-row:active:not(:disabled) {
  transform: translateY(0);
}

.btn-add-row:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-clear-all {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(244, 63, 94, 0.08);
  color: #FB7185;
  border: 1px solid rgba(244, 63, 94, 0.25);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-clear-all:hover {
  background: rgba(244, 63, 94, 0.18);
  border-color: rgba(244, 63, 94, 0.45);
  color: #FECDD3;
  transform: translateY(-1px);
}

.btn-clear-all:active {
  transform: translateY(0);
}

.action-footer {
  margin-top: 4px;
}

.btn-solve {
  width: 100%;
  padding: 12px 18px;
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: 0.3px;
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-solve:hover:not(:disabled) {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45);
  transform: translateY(-1px);
}

.btn-solve:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFFFFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
