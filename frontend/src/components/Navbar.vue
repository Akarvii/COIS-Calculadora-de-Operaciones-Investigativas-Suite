<template>
  <header class="navbar">
    <div class="nav-brand">
      <div class="logo-icon">
        <img src="/mathapp.ico" alt="CIMS Logo" class="brand-logo-img" />
      </div>
      <div class="brand-text">
        <div class="brand-title-row">
          <h1 class="nav-title">CIMS</h1>
          <span class="brand-tag">v1.0</span>
        </div>
        <span class="nav-subtitle">Calculadora Investigativa del Método Simplex</span>
      </div>
    </div>

    <div class="nav-controls">
      <!-- Fraction / Decimal Toggle -->
      <div class="toggle-group">
        <span class="toggle-label">Formato:</span>
        <button 
          class="btn-toggle" 
          :class="{ active: showFractions }" 
          @click="$emit('update:showFractions', true)"
          title="Mostrar como fracciones exactas (ej: 4/3)"
        >
          Fracción (½)
        </button>
        <button 
          class="btn-toggle" 
          :class="{ active: !showFractions }" 
          @click="$emit('update:showFractions', false)"
          title="Mostrar como decimales (ej: 1.333)"
        >
          Decimal (0.5)
        </button>
      </div>

      <!-- Custom Examples Dropdown with SVG Icons -->
      <div class="custom-dropdown" ref="dropdownRef">
        <button 
          type="button"
          class="dropdown-trigger" 
          :class="{ 'is-open': isOpen, 'is-selected': !!selectedExample }"
          @click="isOpen = !isOpen"
          title="Seleccionar configuraciones o problemas de ejemplo"
        >
          <div class="trigger-content">
            <!-- Dynamic Icon based on selection -->
            <span class="example-icon-wrapper">
              <svg v-if="selectedExample?.icon === 'settings'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>

              <svg v-else-if="selectedExample?.icon === 'factory'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/>
                <path d="M17 18h1"/>
                <path d="M12 18h1"/>
                <path d="M7 18h1"/>
              </svg>

              <svg v-else-if="selectedExample?.icon === 'layers'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="12 2 2 7 12 12 22 7 12 2" />
                <polyline points="2 17 12 22 22 17" />
                <polyline points="2 12 12 17 22 12" />
              </svg>

              <svg v-else-if="selectedExample?.icon === 'fraction'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="6" r="2" />
                <line x1="5" y1="12" x2="19" y2="12" />
                <circle cx="12" cy="18" r="2" />
              </svg>

              <svg v-else-if="selectedExample?.icon === 'infinity'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 12c-2-2.67-4-4-6-4a4 4 0 1 0 0 8c2 0 4-1.33 6-4Zm0 0c2 2.67 4 4 6 4a4 4 0 0 0 0-8c-2 0-4 1.33-6 4Z"/>
              </svg>

              <svg v-else-if="selectedExample?.icon === 'alert'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
              </svg>

              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m6 14 1.45-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.55 6a2 2 0 0 1-1.94 1.5H4a2 2 0 0 1-2-2V5c0-1.1.9-2 2-2h3.93a2 2 0 0 1 1.66.9l.82 1.2a2 2 0 0 0 1.66.9H18a2 2 0 0 1 2 2v2" />
              </svg>
            </span>

            <span class="trigger-label">
              {{ selectedExample ? selectedExample.title : 'Seleccionar Configuraciones' }}
            </span>
          </div>

          <svg class="chevron-icon" :class="{ 'rotate': isOpen }" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>

        <!-- Dropdown Menu List -->
        <div v-if="isOpen" class="dropdown-menu">
          <div class="dropdown-header">
            <span>Configuración y Modelos</span>
          </div>

          <button 
            v-for="item in examplesList" 
            :key="item.id"
            class="dropdown-item"
            :class="{ 'is-active': selectedExample?.id === item.id }"
            @click="selectExample(item)"
          >
            <div class="item-icon-container" :class="item.iconClass">
              <!-- Settings / Blank icon -->
              <svg v-if="item.icon === 'settings'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>

              <!-- Factory icon -->
              <svg v-else-if="item.icon === 'factory'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/>
                <path d="M17 18h1"/>
                <path d="M12 18h1"/>
                <path d="M7 18h1"/>
              </svg>

              <!-- Layers / Two-phase icon -->
              <svg v-else-if="item.icon === 'layers'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="12 2 2 7 12 12 22 7 12 2" />
                <polyline points="2 17 12 22 22 17" />
                <polyline points="2 12 12 17 22 12" />
              </svg>

              <!-- Fraction icon -->
              <svg v-else-if="item.icon === 'fraction'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="6" r="2" />
                <line x1="5" y1="12" x2="19" y2="12" />
                <circle cx="12" cy="18" r="2" />
              </svg>

              <!-- Infinity / Unbounded icon -->
              <svg v-else-if="item.icon === 'infinity'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 12c-2-2.67-4-4-6-4a4 4 0 1 0 0 8c2 0 4-1.33 6-4Zm0 0c2 2.67 4 4 6 4a4 4 0 0 0 0-8c-2 0-4 1.33-6 4Z"/>
              </svg>

              <!-- Alert / Infeasible icon -->
              <svg v-else-if="item.icon === 'alert'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
              </svg>
            </div>

            <div class="item-text">
              <span class="item-title">{{ item.title }}</span>
              <span class="item-desc">{{ item.desc }}</span>
            </div>

            <svg v-if="selectedExample?.id === item.id" class="check-selected" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Backend Connection Status -->
      <div class="status-indicator" :class="{ online: backendOnline }">
        <span class="status-dot"></span>
        <span class="status-text">{{ backendOnline ? 'API Conectada' : 'Desconectado' }}</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

defineProps({
  showFractions: {
    type: Boolean,
    default: true
  },
  backendOnline: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:showFractions', 'load-example'])

const isOpen = ref(false)
const dropdownRef = ref(null)

const examplesList = [
  {
    id: 'blank_config',
    title: 'Seleccionar Configuraciones',
    icon: 'settings',
    iconClass: 'icon-cyan',
    desc: 'Campos vacíos para configurar y meter datos desde cero'
  },
  {
    id: 'classic_production',
    title: 'Producción Clásica (Max 2 var)',
    icon: 'factory',
    iconClass: 'icon-blue',
    desc: 'Max Z = 3x₁ + 5x₂ con restricciones ≤'
  },
  {
    id: 'mixed_two_phase',
    title: 'Problema Mixto (Dos Fases)',
    icon: 'layers',
    iconClass: 'icon-indigo',
    desc: 'Min Z = 4x₁ + x₂ con operadores =, ≥, ≤'
  },
  {
    id: 'fractional_optimum',
    title: 'Óptimo Fraccionario (27/2)',
    icon: 'fraction',
    iconClass: 'icon-emerald',
    desc: 'Max Z con soluciones fraccionarias exactas'
  },
  {
    id: 'unbounded_example',
    title: 'Problema No Acotado',
    icon: 'infinity',
    iconClass: 'icon-amber',
    desc: 'Región factible abierta hacia el infinito'
  },
  {
    id: 'infeasible_example',
    title: 'Problema Infactible',
    icon: 'alert',
    iconClass: 'icon-rose',
    desc: 'Restricciones contradictorias sin solución'
  }
]

// Default selection is 'Seleccionar Configuraciones' (blank fields)
const selectedExample = ref(examplesList[0])

function selectExample(item) {
  selectedExample.value = item
  isOpen.value = false
  emit('load-example', item.id)
}

function handleClickOutside(event) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

defineExpose({
  clearSelection: () => {
    selectedExample.value = examplesList[0] // Set to 'Seleccionar Configuraciones'
  },
  setSelection: (exampleId) => {
    const found = examplesList.find(e => e.id === exampleId)
    if (found) selectedExample.value = found
  }
})
</script>

<style scoped>
.navbar {
  height: 64px;
  background: #0E1422;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: relative;
  z-index: 50;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  user-select: none;
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%);
  border: 1px solid rgba(56, 189, 248, 0.25);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.logo-icon:hover {
  transform: scale(1.04);
  border-color: rgba(56, 189, 248, 0.45);
}

.brand-logo-img {
  width: 28px;
  height: 28px;
  object-fit: contain;
  display: block;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

.brand-text {
  display: flex;
  flex-direction: column;
  justify-content: center;
  line-height: 1;
  gap: 3px;
}

.brand-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-title {
  font-size: 1.18rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, #FFFFFF 30%, #93C5FD 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
  line-height: 1.1;
}

.brand-tag {
  font-size: 0.65rem;
  font-family: var(--font-mono);
  font-weight: 700;
  color: #38BDF8;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.28);
  padding: 1px 6px;
  border-radius: 4px;
  line-height: 1.2;
}

.nav-subtitle {
  font-size: 0.73rem;
  font-weight: 400;
  color: var(--text-muted);
  letter-spacing: 0.1px;
}

.nav-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toggle-group {
  display: flex;
  align-items: center;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 2px;
}

.toggle-label {
  font-size: 0.75rem;
  color: var(--text-dim);
  padding: 0 6px 0 8px;
}

.btn-toggle {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-toggle.active {
  background: #1E293B;
  color: var(--accent-blue);
  font-weight: 600;
}

/* Custom Dropdown Styling */
.custom-dropdown {
  position: relative;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-main);
  padding: 6px 12px;
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  min-width: 250px;
  transition: all 0.15s ease;
}

.dropdown-trigger:hover,
.dropdown-trigger.is-open {
  border-color: var(--accent-blue);
  background: var(--bg-card-hover);
}

.dropdown-trigger.is-selected {
  border-color: rgba(56, 189, 248, 0.4);
}

.trigger-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.example-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-blue);
}

.trigger-label {
  font-weight: 600;
  color: var(--text-main);
  font-size: 0.82rem;
  white-space: nowrap;
}

.chevron-icon {
  color: var(--text-dim);
  transition: transform 0.2s ease;
}

.chevron-icon.rotate {
  transform: rotate(180deg);
}

/* Dropdown Menu */
.dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  width: 320px;
  background: #131B2C;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 1px rgba(56, 189, 248, 0.2);
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  animation: fadeInDown 0.15s ease-out;
  z-index: 100;
}

.dropdown-header {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-dim);
  padding: 6px 10px 4px;
  font-weight: 600;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 10px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  color: var(--text-main);
  text-align: left;
  cursor: pointer;
  transition: all 0.15s ease;
}

.dropdown-item:hover {
  background: #1B263B;
  border-color: rgba(56, 189, 248, 0.2);
}

.dropdown-item.is-active {
  background: rgba(56, 189, 248, 0.1);
  border-color: rgba(56, 189, 248, 0.3);
}

.item-icon-container {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-cyan {
  background: rgba(6, 182, 212, 0.12);
  color: #22D3EE;
  border: 1px solid rgba(6, 182, 212, 0.25);
}

.icon-blue {
  background: rgba(56, 189, 248, 0.12);
  color: var(--accent-blue);
  border: 1px solid rgba(56, 189, 248, 0.25);
}

.icon-indigo {
  background: rgba(99, 102, 241, 0.12);
  color: var(--accent-indigo);
  border: 1px solid rgba(99, 102, 241, 0.25);
}

.icon-emerald {
  background: rgba(16, 185, 129, 0.12);
  color: var(--accent-emerald);
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.icon-amber {
  background: rgba(245, 158, 11, 0.12);
  color: var(--accent-amber);
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.icon-rose {
  background: rgba(244, 63, 94, 0.12);
  color: var(--accent-rose);
  border: 1px solid rgba(244, 63, 94, 0.25);
}

.item-text {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.item-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.2;
}

.item-desc {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.check-selected {
  flex-shrink: 0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: var(--text-dim);
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent-rose);
}

.status-indicator.online .status-dot {
  background: var(--accent-emerald);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.status-indicator.online .status-text {
  color: var(--text-muted);
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
