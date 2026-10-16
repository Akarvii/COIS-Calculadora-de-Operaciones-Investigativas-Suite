<template>
  <div class="selector-container">
    <!-- Main Split Screen Area -->
    <div class="split-viewport">
      <!-- PANEL A: COIS-IMS (Simplex) -->
      <section 
        class="split-panel panel-cims"
        :class="{ 'is-hovered': hoveredPanel === 'cims', 'is-dimmed': hoveredPanel === 'networks' }"
        @mouseenter="hoveredPanel = 'cims'"
        @mouseleave="hoveredPanel = null"
        @click="selectModule('cims')"
      >
        <!-- Background Ambient Glow & Uniform Technical Grid -->
        <div class="ambient-glow glow-cyan"></div>
        <div class="mesh-grid mesh-grid-quad mesh-cims"></div>

        <div class="panel-content">
          <div class="badge-row">
            <span class="module-badge badge-cims">MÓDULO I</span>
            <span class="module-category">Programación Lineal</span>
          </div>

          <div class="logo-wrapper cims-logo-box">
            <img src="/logo_cims.png" alt="COIS-IMS Logo" class="panel-logo-img" />
          </div>

          <h2 class="panel-title">COIS-IMS</h2>
          <p class="panel-tagline">Investigación Métodos Simplex</p>
          <p class="panel-description">
            Plataforma didáctica y exacta de programación lineal continua con aritmética fraccionaria pura, análisis matricial y resolución paso a paso.
          </p>

          <!-- Feature Pills -->
          <ul class="feature-list">
            <li>
              <span class="feature-icon">❖</span>
              <span>Simplex Tabular Estándar & 2 Fases</span>
            </li>
            <li>
              <span class="feature-icon">❖</span>
              <span>Método Simplex Revisado (Inversa B⁻¹)</span>
            </li>
            <li>
              <span class="feature-icon">❖</span>
              <span>Análisis de Sensibilidad & Precios Sombra</span>
            </li>
            <li>
              <span class="feature-icon">❖</span>
              <span>Visualización Geométrica 2D Interactiva</span>
            </li>
            <li>
              <span class="feature-icon">❖</span>
              <span>Prevención de Ciclado (Regla de Bland)</span>
            </li>
          </ul>

          <div class="cta-wrapper">
            <button class="btn-launch btn-launch-cims">
              <span>Iniciar COIS-IMS</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
            </button>
          </div>
        </div>
      </section>

      <!-- Center Clean Dividing Line (WITHOUT the "OR" badge as requested) -->
      <div class="split-divider">
        <div class="divider-line"></div>
      </div>

      <!-- PANEL B: COIS-NETWORKS (Redes & Asignación) -->
      <section 
        class="split-panel panel-networks"
        :class="{ 'is-hovered': hoveredPanel === 'networks', 'is-dimmed': hoveredPanel === 'cims' }"
        @mouseenter="hoveredPanel = 'networks'"
        @mouseleave="hoveredPanel = null"
        @click="selectModule('networks')"
      >
        <!-- Background Ambient Glow & Uniform Technical Grid -->
        <div class="ambient-glow glow-emerald"></div>
        <div class="mesh-grid mesh-grid-quad mesh-networks"></div>

        <div class="panel-content">
          <div class="badge-row">
            <span class="module-badge badge-networks">MÓDULO II</span>
            <span class="module-category">Optimización en Redes</span>
          </div>

          <div class="logo-wrapper networks-logo-box">
            <img src="/logo_cims_network.png" alt="COIS-Networks Logo" class="panel-logo-img" />
          </div>

          <h2 class="panel-title title-networks">COIS-Networks</h2>
          <p class="panel-tagline">Optimización en Redes & Algoritmos de Grafos</p>
          <p class="panel-description">
            Laboratorio de modelos de transporte combinatorio, emparejamiento óptimo de recursos y circulación de flujos en redes complejas.
          </p>

          <!-- Feature Pills -->
          <ul class="feature-list">
            <li>
              <span class="feature-icon icon-emerald">❖</span>
              <span>Problema de Asignación (Kuhn-Munkres / Húngaro)</span>
            </li>
            <li>
              <span class="feature-icon icon-emerald">❖</span>
              <span>Casos Especiales: Desbalance, Maximización y Prohibidos</span>
            </li>
            <li>
              <span class="feature-icon icon-emerald">❖</span>
              <span>Flujo Máximo (Algoritmo de Edmonds-Karp / Ford-Fulkerson)</span>
            </li>
            <li>
              <span class="feature-icon icon-emerald">❖</span>
              <span>Teorema de Corte Mínimo (Max-Flow Min-Cut)</span>
            </li>
            <li>
              <span class="feature-icon icon-emerald">❖</span>
              <span>Flujo a Costo Mínimo (Min-Cost Flow / Successive Path)</span>
            </li>
          </ul>

          <div class="cta-wrapper">
            <button class="btn-launch btn-launch-networks">
              <span>Iniciar COIS-Networks</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
            </button>
          </div>
        </div>
      </section>
    </div>

    <!-- Bottom Action Dock: Disclaimer (?) & WhatsApp -->
    <footer class="hub-footer">
      <div class="footer-actions">
        <!-- Disclaimer Button (?) -->
        <button 
          class="btn-footer-action btn-disclaimer" 
          @click.stop="openDisclaimer" 
          title="Ver Aviso Académico y Metodológico"
        >
          <span class="btn-q-icon">?</span>
          <span class="btn-action-text">Aviso Académico</span>
        </button>

        <!-- WhatsApp Direct Contact Button -->
        <a 
          href="https://wa.me/573028530092" 
          target="_blank" 
          rel="noopener noreferrer" 
          class="btn-footer-action btn-whatsapp" 
          title="Contactar al desarrollador por WhatsApp (+57 302 853 0092)"
          @click.stop
        >
          <!-- Custom WhatsApp SVG Icon -->
          <svg class="whatsapp-svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51l-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.885-9.886 9.885m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L0 24l6.335-1.662c1.746.953 3.71 1.456 5.711 1.457h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
          </svg>
          <span class="btn-action-text">WhatsApp</span>
        </a>
      </div>
    </footer>

    <!-- DISCLAIMER MODAL WINDOW CHILD -->
    <Teleport to="body">
      <Transition name="modal-scale">
        <div 
          v-if="isDisclaimerOpen" 
          class="modal-backdrop" 
          @click="closeDisclaimer"
        >
          <div 
            class="modal-window-child" 
            @click.stop
            role="dialog"
            aria-modal="true"
          >
            <!-- Title Bar -->
            <header class="window-title-bar">
              <div class="window-info">
                <span class="window-icon">⚖️</span>
                <span class="window-title">Aviso Académico & Metodológico</span>
              </div>
              <button 
                class="window-btn-close" 
                @click="closeDisclaimer" 
                title="Cerrar ventana (Esc)"
              >
                ✕
              </button>
            </header>

            <!-- Window Content -->
            <div class="window-body">
              <div class="disclaimer-callout">
                <div class="callout-badge-row">
                  <span class="callout-pill">Investigación de Operaciones</span>
                  <span class="callout-status">Uso Académico & Experimental</span>
                </div>
                <p class="disclaimer-text-content">
                  <strong>Aviso Académico:</strong> Plataforma pedagógica experimental desarrollada para implementaciones y demostraciones en <strong>Investigación de Operaciones</strong>. Los métodos desglosan el álgebra matricial y modelos de redes con fines formativos y de verificación analítica.
                </p>
              </div>

              <div class="disclaimer-points">
                <div class="point-item">
                  <span class="point-bullet">❖</span>
                  <p><strong>Trazabilidad Didáctica:</strong> Se prioriza la visualización paso a paso de matrices, tablas y redes sobre cajas negras automatizadas.</p>
                </div>
                <div class="point-item">
                  <span class="point-bullet">❖</span>
                  <p><strong>Precisión Exacta:</strong> Cálculos desarrollados con aritmética fraccionaria pura para eliminar errores de redondeo en coma flotante.</p>
                </div>
              </div>

              <!-- Bottom Confirm Action -->
              <div class="window-action-row">
                <button class="btn-window-confirm" @click="closeDisclaimer">
                  Entendido
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['select'])
const hoveredPanel = ref(null)

function selectModule(moduleKey) {
  emit('select', moduleKey)
}

// Modal State & Controls
const isDisclaimerOpen = ref(false)

function openDisclaimer() {
  isDisclaimerOpen.value = true
}

function closeDisclaimer() {
  isDisclaimerOpen.value = false
}

function handleKeyDown(e) {
  if (e.key === 'Escape' && isDisclaimerOpen.value) {
    closeDisclaimer()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped src="./ModuleSelector.css"></style>
