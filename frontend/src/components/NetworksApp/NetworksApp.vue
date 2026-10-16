<template>
  <div class="networks-root">
    <!-- Main Content Area (Navbar is unified at root) -->
    <main class="networks-body">
      <!-- TAB 1: ASIGNACIÓN (KUHN-MUNKRES) -->
      <section v-if="activeTab === 'assignment'" class="tab-content">
        <div class="tab-header">
          <div>
            <h2 class="section-title">Problema de Asignación — Método de Kuhn-Munkres</h2>
            <p class="section-subtitle">
              Resolución exacta mediante el Algoritmo Húngaro paso a paso. Soporta matrices desbalanceadas, maximización y asignaciones prohibidas (costo M).
            </p>
          </div>
          <div class="quick-stats">
            <span class="pill-tech">Complejidad: O(n³)</span>
            <span class="pill-tech">Bipartito Ponderado</span>
          </div>
        </div>

        <div class="placeholder-card">
          <div class="info-banner">
            <span class="banner-icon">💡</span>
            <div>
              <strong>Espacio de Trabajo Listo:</strong>
              Configura las dimensiones de tu matriz de costos ($n \times m$), selecciona si buscas <em>Minimizar Costo</em> o <em>Maximizar Utilidad</em>, y experimenta con la reducción de filas y columnas.
            </div>
          </div>
          <div class="empty-state">
            <p>La interfaz del Algoritmo Húngaro y los 3 ejercicios integrados se cargarán aquí.</p>
          </div>
        </div>
      </section>

      <!-- TAB 2: FLUJO MÁXIMO -->
      <section v-else-if="activeTab === 'max_flow'" class="tab-content">
        <div class="tab-header">
          <div>
            <h2 class="section-title">Problema de Flujo Máximo</h2>
            <p class="section-subtitle">
              Algoritmos de Ford-Fulkerson y Edmonds-Karp (BFS en red residual). Demostración visual del Teorema de Corte Mínimo (Max-Flow Min-Cut).
            </p>
          </div>
          <div class="quick-stats">
            <span class="pill-tech">Edmonds-Karp: O(V·E²)</span>
            <span class="pill-tech">Grafo Residual</span>
          </div>
        </div>

        <div class="placeholder-card">
          <div class="info-banner">
            <span class="banner-icon">🌊</span>
            <div>
              <strong>Visualizador de Red Residual:</strong>
              Inserta nodos, capacidades $c(u,v)$, define la Fuente ($s$) y el Sumidero ($t$). Observa los caminos de aumento paso a paso.
            </div>
          </div>
          <div class="empty-state">
            <p>El editor interactivo de grafos y cálculo de flujo máximo se cargarán aquí.</p>
          </div>
        </div>
      </section>

      <!-- TAB 3: FLUJO A COSTO MÍNIMO -->
      <section v-else class="tab-content">
        <div class="tab-header">
          <div>
            <h2 class="section-title">Problema de Flujo a Costo Mínimo (Min-Cost Flow)</h2>
            <p class="section-subtitle">
              Generalización de redes: transporte de demanda requerida respetando capacidades máximas al menor costo unitario total posible.
            </p>
          </div>
          <div class="quick-stats">
            <span class="pill-tech">Successive Shortest Path</span>
            <span class="pill-tech">Costos Reducidos Duales</span>
          </div>
        </div>

        <div class="placeholder-card">
          <div class="info-banner">
            <span class="banner-icon">⚡</span>
            <div>
              <strong>Optimización Global:</strong>
              Configura ofertas en nodos generadores, demandas en sumideros y arcos con $(u_{ij}, c_{ij})$.
            </div>
          </div>
          <div class="empty-state">
            <p>El motor de flujo a costo mínimo con los 3 ejercicios prácticos se cargará aquí.</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
defineProps({
  activeTab: {
    type: String,
    default: 'assignment'
  }
})
</script>

<style scoped src="./NetworksApp.css"></style>
