<template>
  <div class="networks-root">
    <!-- Main Content Area -->
    <main class="networks-body">
      <!-- ============================================================== -->
      <!-- TAB 1: ASIGNACIÓN (KUHN-MUNKRES / HÚNGARO) — MODO CALCULADORA   -->
      <!-- ============================================================== -->
      <section v-if="activeTab === 'assignment'" class="tab-content">
        <!-- Header -->
        <div class="tab-header">
          <div>
            <h2 class="section-title">Problema de Asignación — Método de Kuhn-Munkres</h2>
            <p class="section-subtitle">
              Calculadora interactiva del Algoritmo Húngaro con aritmética exacta. Modifica las dimensiones, los costos en la matriz o selecciona un ejercicio del menú superior para resolver paso a paso.
            </p>
          </div>
          <div class="quick-stats">
            <span class="pill-tech">Complejidad: O(n³)</span>
            <span class="pill-tech">Bipartito Ponderado</span>
            <span v-if="selectedExerciseId && selectedExerciseId.startsWith('asig_')" class="pill-tech pill-purple">
              Modo Ejercicio Activo
            </span>
            <span v-else class="pill-tech pill-green">Modo Libre Desbloqueado</span>
          </div>
        </div>

        <!-- Panel de Control y Configuración de Entrada -->
        <div class="calc-control-card">
          <div class="control-row">
            <!-- Selector de Objetivo: Min / Max -->
            <div class="control-group">
              <label class="control-label">Objetivo de Optimización:</label>
              <div class="opt-toggle-group">
                <button
                  type="button"
                  class="btn-opt-mode"
                  :class="{ active: !assignIsMax }"
                  @click="setOptMode(false)"
                  title="Minimizar costo total o consumo"
                >
                  Minimizar (Costo)
                </button>
                <button
                  type="button"
                  class="btn-opt-mode"
                  :class="{ active: assignIsMax }"
                  @click="setOptMode(true)"
                  title="Maximizar ganancia o rendimiento total"
                >
                  Maximizar (Ganancia)
                </button>
              </div>
            </div>

            <!-- Selector de Filas N -->
            <div class="control-group">
              <label class="control-label">Recursos (Filas):</label>
              <div class="stepper-box">
                <button
                  type="button"
                  class="btn-step"
                  :disabled="assignRows <= 2"
                  @click="changeDimensions(assignRows - 1, assignCols)"
                  title="Reducir filas"
                >
                  -
                </button>
                <span class="step-value">{{ assignRows }}</span>
                <button
                  type="button"
                  class="btn-step"
                  :disabled="assignRows >= 6"
                  @click="changeDimensions(assignRows + 1, assignCols)"
                  title="Aumentar filas"
                >
                  +
                </button>
              </div>
            </div>

            <!-- Selector de Columnas M -->
            <div class="control-group">
              <label class="control-label">Tareas (Columnas):</label>
              <div class="stepper-box">
                <button
                  type="button"
                  class="btn-step"
                  :disabled="assignCols <= 2"
                  @click="changeDimensions(assignRows, assignCols - 1)"
                  title="Reducir columnas"
                >
                  -
                </button>
                <span class="step-value">{{ assignCols }}</span>
                <button
                  type="button"
                  class="btn-step"
                  :disabled="assignCols >= 6"
                  @click="changeDimensions(assignRows, assignCols + 1)"
                  title="Aumentar columnas"
                >
                  +
                </button>
              </div>
            </div>

            <!-- Dim Status Badge -->
            <div class="dim-status-badge" :class="{ 'is-rect': assignRows !== assignCols }">
              <span class="badge-size-text">{{ assignRows }} × {{ assignCols }}</span>
              <small v-if="assignRows !== assignCols">Desbalanceado (auto-ficticio)</small>
              <small v-else>Cuadrada balanceada</small>
            </div>
          </div>

          <!-- Matriz Editable Interactiva -->
          <div class="matrix-input-container">
            <div class="matrix-input-header">
              <span class="matrix-caption">Ingresa o modifica los coeficientes de la matriz:</span>
              <div class="action-buttons-group">
                <button
                  type="button"
                  class="btn-action btn-solve"
                  @click="calculateAssignment"
                  title="Calcular solución óptima mediante Algoritmo Húngaro"
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                  <span>Calcular Asignación</span>
                </button>
                <button
                  type="button"
                  class="btn-action btn-clear"
                  @click="clearAssignMatrix"
                  title="Limpiar todas las celdas"
                >
                  Limpiar
                </button>
              </div>
            </div>

            <!-- Tabla Editable -->
            <div class="table-container matrix-table-wrap">
              <table class="editable-matrix-table">
                <thead>
                  <tr>
                    <th class="corner-header">Recursos \ Tareas</th>
                    <th v-for="(colLabel, cIdx) in assignColLabels" :key="cIdx">
                      <input
                        type="text"
                        class="header-name-input"
                        v-model="assignColLabels[cIdx]"
                        :title="'Nombre de columna ' + (cIdx + 1)"
                      />
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(rowLabel, rIdx) in assignRowLabels" :key="rIdx">
                    <td class="row-label-cell">
                      <input
                        type="text"
                        class="header-name-input"
                        v-model="assignRowLabels[rIdx]"
                        :title="'Nombre de fila ' + (rIdx + 1)"
                      />
                    </td>
                    <td
                      v-for="(val, cIdx) in assignMatrix[rIdx]"
                      :key="cIdx"
                      class="matrix-cell-td"
                      :class="{ 'cell-optimal': isCellOptimal(rIdx, cIdx) }"
                    >
                      <div class="cell-wrapper">
                        <input
                          type="number"
                          step="any"
                          class="matrix-cell-input"
                          v-model.number="assignMatrix[rIdx][cIdx]"
                          @input="handleCellInput"
                          placeholder="0"
                        />
                        <span v-if="isCellOptimal(rIdx, cIdx)" class="check-mark" title="Asignación óptima">✓</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ALERTA DE ERROR SI EXISTE -->
        <div v-if="calcError" class="calc-error-banner">
          ⚠️ {{ calcError }}
        </div>

        <!-- SECCIÓN DE RESULTADOS ANALÍTICOS -->
        <div v-if="calculationResult" class="results-container">
          <div class="exercise-card result-summary-card">
            <div class="exercise-header">
              <div>
                <div class="badge-tag-row">
                  <span class="type-badge" :class="calculationResult.isMax ? 'badge-emerald' : 'badge-blue'">
                    {{ calculationResult.isMax ? 'Maximización' : 'Minimización' }}
                  </span>
                  <span class="dim-badge">{{ calculationResult.origRows }} × {{ calculationResult.origCols }}</span>
                  <span v-if="!calculationResult.isBalanced" class="dim-badge badge-amber">
                    +{{ Math.abs(calculationResult.origRows - calculationResult.origCols) }} Ficticia(s)
                  </span>
                </div>
                <h3 class="exercise-title">Solución Óptima Obtenida (Kuhn-Munkres)</h3>
              </div>
              <div class="solution-highlight">
                <span class="sol-label">{{ calculationResult.isMax ? 'Ganancia Máxima (Z*):' : 'Costo Mínimo (Z*):' }}</span>
                <span class="sol-value" :class="{ 'val-green': calculationResult.isMax }">{{ calculationResult.optimalZ }}</span>
              </div>
            </div>

            <!-- Asignaciones Óptimas Resumen -->
            <div class="optimal-result-box">
              <div class="result-header">
                <span class="res-icon">🎯</span>
                <div>
                  <strong>Emparejamiento Óptimo Asignado (Uno a Uno)</strong>
                  <p>{{ calculationResult.summary }}</p>
                </div>
              </div>
              <div class="assignments-pills-list">
                <div
                  v-for="(asig, aIdx) in calculationResult.optimalAssignments"
                  :key="aIdx"
                  class="asig-pill"
                  :class="{ 'asig-dummy': asig.isDummy }"
                >
                  <span class="asig-pair">{{ asig.from }} ➜ {{ asig.to }}</span>
                  <span class="asig-cost">{{ calculationResult.isMax ? '+' : '' }}{{ asig.cost }}</span>
                </div>
              </div>
            </div>

            <!-- Pestañas del Procedimiento Paso a Paso -->
            <div class="procedure-box">
              <div class="proc-nav-tabs">
                <button
                  type="button"
                  class="proc-tab-btn"
                  :class="{ active: activeStepTab === 'step0' }"
                  v-if="!calculationResult.isBalanced"
                  @click="activeStepTab = 'step0'"
                >
                  Paso 0: Balanceo
                </button>
                <button
                  type="button"
                  class="proc-tab-btn"
                  :class="{ active: activeStepTab === 'step1' }"
                  @click="activeStepTab = 'step1'"
                >
                  Paso 1: Reducción Filas
                </button>
                <button
                  type="button"
                  class="proc-tab-btn"
                  :class="{ active: activeStepTab === 'step2' }"
                  @click="activeStepTab = 'step2'"
                >
                  Paso 2: Reducción Columnas
                </button>
                <button
                  type="button"
                  class="proc-tab-btn"
                  :class="{ active: activeStepTab === 'step3' }"
                  @click="activeStepTab = 'step3'"
                >
                  Paso 3: Matriz Reducida & Ceros
                </button>
              </div>

              <!-- Contenido del Paso Seleccionado -->
              <div class="proc-tab-body">
                <!-- Paso 0: Balanceo -->
                <div v-if="activeStepTab === 'step0' && !calculationResult.isBalanced" class="step-view">
                  <p class="step-desc">
                    Dado que la matriz es de {{ calculationResult.origRows }} × {{ calculationResult.origCols }}, se balancea a una dimensión cuadrada de {{ calculationResult.dimensionK }} × {{ calculationResult.dimensionK }} añadiendo filas o columnas ficticias con costo 0:
                  </p>
                  <div class="table-container">
                    <table class="data-table">
                      <thead>
                        <tr>
                          <th>Recurso \ Tarea</th>
                          <th v-for="c in calculationResult.colLabels" :key="c">{{ c }}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(rLabel, rI) in calculationResult.rowLabels" :key="rLabel">
                          <td class="row-label">{{ rLabel }}</td>
                          <td v-for="(v, cI) in calculationResult.balancedMatrix[rI]" :key="cI">
                            {{ v }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Paso 1: Reducción de Filas -->
                <div v-if="activeStepTab === 'step1'" class="step-view">
                  <p class="step-desc">
                    Se resta el menor elemento de cada fila (uᵢ) a todos los elementos de esa fila para asegurar al menos un cero por fila:
                  </p>
                  <div class="table-container">
                    <table class="data-table">
                      <thead>
                        <tr>
                          <th>Recurso \ Tarea</th>
                          <th v-for="c in calculationResult.colLabels" :key="c">{{ c }}</th>
                          <th class="th-min">Mínimo Fila (uᵢ)</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(rLabel, rI) in calculationResult.rowLabels" :key="rLabel">
                          <td class="row-label">{{ rLabel }}</td>
                          <td v-for="(v, cI) in calculationResult.afterRowReduction[rI]" :key="cI" :class="{ 'zero-cell': v === 0 }">
                            {{ v }}
                          </td>
                          <td class="td-min-val">- {{ calculationResult.rowMins[rI] }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Paso 2: Reducción de Columnas -->
                <div v-if="activeStepTab === 'step2'" class="step-view">
                  <p class="step-desc">
                    Se resta el valor mínimo de cada columna (vⱼ) para obtener la matriz de costos relativos de oportunidad:
                  </p>
                  <div class="table-container">
                    <table class="data-table">
                      <thead>
                        <tr>
                          <th>Recurso \ Tarea</th>
                          <th v-for="c in calculationResult.colLabels" :key="c">{{ c }}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(rLabel, rI) in calculationResult.rowLabels" :key="rLabel">
                          <td class="row-label">{{ rLabel }}</td>
                          <td v-for="(v, cI) in calculationResult.afterColReduction[rI]" :key="cI" :class="{ 'zero-cell': v === 0 }">
                            {{ v }}
                          </td>
                        </tr>
                        <tr class="tr-col-mins">
                          <td class="row-label">Mínimo Col (vⱼ)</td>
                          <td v-for="(minV, cI) in calculationResult.colMins" :key="cI" class="td-min-val">
                            - {{ minV }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Paso 3: Matriz Reducida & Asignaciones de Ceros -->
                <div v-if="activeStepTab === 'step3'" class="step-view">
                  <p class="step-desc">
                    Matriz final resultante con los ceros asignados en la combinación óptima que satisface la igualdad de líneas mínimas de König (L = n):
                  </p>
                  <div class="table-container">
                    <table class="data-table">
                      <thead>
                        <tr>
                          <th>Recurso \ Tarea</th>
                          <th v-for="c in calculationResult.colLabels" :key="c">{{ c }}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(rLabel, rI) in calculationResult.rowLabels" :key="rLabel">
                          <td class="row-label">{{ rLabel }}</td>
                          <td
                            v-for="(v, cI) in calculationResult.finalMatrix[rI]"
                            :key="cI"
                            :class="{ 'cell-optimal': isCellOptimal(rI, cI), 'zero-cell': v === 0 && !isCellOptimal(rI, cI) }"
                          >
                            <span class="cell-val">{{ v }}</span>
                            <span v-if="isCellOptimal(rI, cI)" class="check-mark">✓</span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ============================================================== -->
      <!-- TAB 2: FLUJO MÁXIMO (EDMONDS-KARP) — MODO CALCULADORA INTERACTIVA -->
      <!-- ============================================================== -->
      <section v-else-if="activeTab === 'max_flow'" class="tab-content">
        <div class="tab-header">
          <div>
            <h2 class="section-title">Problema de Flujo Máximo — Algoritmo de Edmonds-Karp</h2>
            <p class="section-subtitle">
              Calculadora interactiva de flujo en redes capacitadas y Teorema de Corte Mínimo. Configura la Fuente, el Sumidero y la lista de arcos, o selecciona un ejercicio preconfigurado del menú superior para resolver mediante búsqueda en anchura (BFS) en la red residual.
            </p>
          </div>
          <div class="quick-stats">
            <span class="pill-tech">Edmonds-Karp: O(V·E²)</span>
            <span class="pill-tech">Grafo Residual</span>
            <span v-if="selectedExerciseId === 'max_1'" class="pill-tech pill-purple">
              Modo Ejercicio Activo
            </span>
            <span v-else class="pill-tech pill-green">Modo Libre Desbloqueado</span>
          </div>
        </div>

        <!-- Panel de Control y Configuración de Entrada -->
        <div class="calc-control-card">
          <div class="control-row">
            <!-- Selector de Fuente (s) -->
            <div class="control-group">
              <label class="control-label">Nodo Fuente (s):</label>
              <input
                type="text"
                class="calc-text-input"
                v-model="maxFlowSource"
                placeholder="1"
                title="Nodo origen del flujo total"
              />
            </div>

            <!-- Selector de Sumidero (t) -->
            <div class="control-group">
              <label class="control-label">Nodo Sumidero (t):</label>
              <input
                type="text"
                class="calc-text-input"
                v-model="maxFlowSink"
                placeholder="6"
                title="Nodo destino del flujo total"
              />
            </div>

            <!-- Total de Arcos -->
            <div class="dim-status-badge">
              <span class="badge-size-text">{{ maxFlowArcs.length }} Arcos</span>
              <small>Dirigidos y capacitados</small>
            </div>
          </div>

          <!-- Tabla Editable de Arcos -->
          <div class="matrix-input-container">
            <div class="matrix-input-header">
              <span class="matrix-caption">Ingresa o modifica los arcos y sus capacidades máximas:</span>
              <div class="action-buttons-group">
                <button
                  type="button"
                  class="btn-action btn-solve"
                  @click="calculateMaxFlow"
                  title="Calcular el flujo máximo y corte mínimo"
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                  <span>Calcular Flujo Máximo</span>
                </button>
                <button
                  type="button"
                  class="btn-action btn-add-row"
                  @click="addMaxFlowArc"
                  title="Agregar un nuevo arco a la red"
                >
                  + Agregar Arco
                </button>
                <button
                  type="button"
                  class="btn-action btn-clear"
                  @click="clearMaxFlow"
                  title="Limpiar arcos y reiniciar"
                >
                  Limpiar
                </button>
              </div>
            </div>

            <div class="table-container">
              <table class="editable-matrix-table">
                <thead>
                  <tr>
                    <th style="width: 50px;">#</th>
                    <th>Nodo Origen (u)</th>
                    <th>Nodo Destino (v)</th>
                    <th>Capacidad Máxima (cᵤᵥ)</th>
                    <th style="width: 60px;">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(arc, idx) in maxFlowArcs" :key="idx">
                    <td class="row-label-cell" style="text-align: center;">{{ idx + 1 }}</td>
                    <td>
                      <input
                        type="text"
                        class="table-input"
                        v-model="arc.from"
                        placeholder="Origen (u)"
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        class="table-input"
                        v-model="arc.to"
                        placeholder="Destino (v)"
                      />
                    </td>
                    <td>
                      <input
                        type="number"
                        min="0"
                        step="any"
                        class="table-input"
                        v-model.number="arc.capacity"
                        placeholder="Capacidad"
                      />
                    </td>
                    <td style="text-align: center;">
                      <button
                        type="button"
                        class="btn-del-row"
                        @click="removeMaxFlowArc(idx)"
                        title="Eliminar este arco"
                      >
                        ✕
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Alerta de Error -->
        <div v-if="maxFlowError" class="calc-error-banner">
          <span class="err-icon">⚠️</span>
          <span>{{ maxFlowError }}</span>
        </div>

        <!-- Tarjeta de Resultados de Flujo Máximo -->
        <div v-if="maxFlowResult" class="exercise-card">
          <div class="exercise-header">
            <div>
              <div class="badge-tag-row">
                <span class="type-badge badge-purple">Flujo Máximo Óptimo</span>
                <span class="dim-badge">{{ maxFlowResult.source }} ➜ {{ maxFlowResult.sink }}</span>
              </div>
              <h3 class="exercise-title">Solución Óptima de la Red</h3>
            </div>
            <div class="solution-highlight">
              <span class="sol-label">Flujo Máximo Circulante:</span>
              <span class="sol-value val-green">{{ maxFlowResult.optimalFlow }}</span>
            </div>
          </div>

          <!-- Tabla de Arcos, Capacidades y Flujo Enviado -->
          <div class="matrix-section">
            <h4 class="sub-title">Distribución de Flujo por Arco y Capacidades Residuales</h4>
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Arco Dirigido (u, v)</th>
                    <th>Capacidad Máxima (cᵤᵥ)</th>
                    <th>Flujo Enviado (fᵤᵥ)</th>
                    <th>Capacidad Residual (c - f)</th>
                    <th>Estado del Canal</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="arc in maxFlowResult.arcsResult" :key="arc.name">
                    <td class="row-label">{{ arc.name }}</td>
                    <td>{{ arc.capacity }}</td>
                    <td :class="{ 'cell-optimal': arc.flow > 0 }">
                      <strong>{{ arc.flow }}</strong>
                    </td>
                    <td>{{ arc.residual }}</td>
                    <td>
                      <span v-if="arc.saturated" class="sat-badge sat-danger">SATURADO (Cuello de Botella)</span>
                      <span v-else class="sat-badge sat-ok">Disponible (+{{ arc.residual }})</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Teorema de Corte Mínimo -->
          <div class="min-cut-box">
            <div class="result-header">
              <span class="res-icon">✂️</span>
              <div>
                <strong>Teorema de Flujo Máximo y Corte Mínimo (Max-Flow = Min-Cut)</strong>
                <p>El corte que separa la Fuente del Sumidero con menor capacidad suma exactamente: <strong>{{ maxFlowResult.minCut.minCutCapacity }}</strong></p>
              </div>
            </div>
            <div class="cut-details">
              <div class="cut-item">
                <span class="cut-label">Partición de Nodos:</span>
                <span class="cut-code">{{ maxFlowResult.minCut.cutPartition }}</span>
              </div>
              <div class="cut-item">
                <span class="cut-label">Arcos que cruzan el corte:</span>
                <span class="cut-code">{{ maxFlowResult.minCut.cutArcsStr }}</span>
              </div>
            </div>
          </div>

          <!-- Iteraciones de Caminos Aumentantes -->
          <div class="procedure-box">
            <h4 class="sub-title">Caminos Aumentantes Encontrados por BFS (Edmonds-Karp)</h4>
            <div class="steps-list">
              <div v-for="(it, itIdx) in maxFlowResult.iterations" :key="itIdx" class="step-item">
                <span class="step-num">{{ itIdx + 1 }}</span>
                <div class="step-content">
                  <strong>{{ it.title }}:</strong>
                  <span>{{ it.detail }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ============================================================== -->
      <!-- TAB 3: FLUJO A COSTO MÍNIMO (MCFP) — MODO CALCULADORA           -->
      <!-- ============================================================== -->
      <section v-else class="tab-content">
        <div class="tab-header">
          <div>
            <h2 class="section-title">Problema de Flujo a Costo Mínimo (Min-Cost Flow)</h2>
            <p class="section-subtitle">
              Calculadora interactiva del modelo general de redes con demandas netas en nodos y costos unitarios en arcos. Configura los balances netos bᵢ (Σ bᵢ = 0) y arcos capacitados, o selecciona un modelo preconfigurado.
            </p>
          </div>
          <div class="quick-stats">
            <span class="pill-tech">Successive Shortest Path</span>
            <span class="pill-tech">Potenciales Duales</span>
            <span v-if="['mcfp_1', 'mcfp_2', 'mcfp_3'].includes(selectedExerciseId)" class="pill-tech pill-purple">
              Modo Ejercicio Activo
            </span>
            <span v-else class="pill-tech pill-green">Modo Libre Desbloqueado</span>
          </div>
        </div>

        <!-- Panel de Control y Configuración de Entrada -->
        <div class="calc-control-card">
          <!-- 1. Configuración de Nodos y Balances -->
          <div class="calc-subheading">
            <span>1. Nodos de la Red y Vector de Balances Netos (bᵢ)</span>
            <div class="balance-status-box" :class="mcfpTotalBalance === 0 ? 'badge-balanced' : 'badge-unbalanced'">
              <span>Balance Global: Σ b = {{ mcfpTotalBalance > 0 ? '+' : '' }}{{ mcfpTotalBalance }}</span>
              <small v-if="mcfpTotalBalance === 0">(Factible: Oferta = Demanda)</small>
              <small v-else>(Desbalanceado: Σ b debe ser 0)</small>
            </div>
          </div>

          <div class="table-container nodes-table-wrap">
            <table class="editable-matrix-table">
              <thead>
                <tr>
                  <th style="width: 50px;">#</th>
                  <th>ID / Nombre del Nodo</th>
                  <th>Balance Neto bᵢ (+oferta, -demanda, 0 transbordo)</th>
                  <th>Rol Calculado</th>
                  <th style="width: 60px;">Acción</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(node, idx) in mcfpNodes" :key="idx">
                  <td class="row-label-cell" style="text-align: center;">{{ idx + 1 }}</td>
                  <td>
                    <input
                      type="text"
                      class="table-input"
                      v-model="node.name"
                      placeholder="Nombre del nodo"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="any"
                      class="table-input"
                      v-model.number="node.b"
                      placeholder="0"
                    />
                  </td>
                  <td style="text-align: center;">
                    <span class="node-role" :class="node.b > 0 ? 'role-origin' : (node.b < 0 ? 'role-dest' : 'role-trans')">
                      {{ node.b > 0 ? 'Oferta (+' + node.b + ')' : (node.b < 0 ? 'Demanda (' + node.b + ')' : 'Transbordo (0)') }}
                    </span>
                  </td>
                  <td style="text-align: center;">
                    <button
                      type="button"
                      class="btn-del-row"
                      :disabled="mcfpNodes.length <= 2"
                      @click="removeMcfpNode(idx)"
                      title="Eliminar este nodo"
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style="margin-bottom: 20px;">
            <button
              type="button"
              class="btn-action btn-add-row"
              @click="addMcfpNode"
              title="Agregar un nuevo nodo"
            >
              + Agregar Nodo
            </button>
          </div>

          <!-- 2. Configuración de Arcos -->
          <div class="matrix-input-header">
            <span class="matrix-caption">2. Topología de Arcos, Costos Unitarios (cᵢⱼ) y Capacidades (uᵢⱼ):</span>
            <div class="action-buttons-group">
              <button
                type="button"
                class="btn-action btn-solve"
                @click="calculateMcfp"
                title="Calcular el flujo a costo mínimo"
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                <span>Calcular Costo Mínimo</span>
              </button>
              <button
                type="button"
                class="btn-action btn-add-row"
                @click="addMcfpArc"
                title="Agregar un nuevo arco"
              >
                + Agregar Arco
              </button>
              <button
                type="button"
                class="btn-action btn-clear"
                @click="clearMcfp"
                title="Limpiar y reiniciar modelo"
              >
                Limpiar
              </button>
            </div>
          </div>

          <div class="table-container">
            <table class="editable-matrix-table">
              <thead>
                <tr>
                  <th style="width: 50px;">#</th>
                  <th>Nodo Origen (i)</th>
                  <th>Nodo Destino (j)</th>
                  <th>Costo Unitario (cᵢⱼ)</th>
                  <th>Capacidad Máxima (uᵢⱼ o ∞)</th>
                  <th style="width: 60px;">Acción</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(arc, idx) in mcfpArcs" :key="idx">
                  <td class="row-label-cell" style="text-align: center;">{{ idx + 1 }}</td>
                  <td>
                    <select class="table-input" v-model="arc.from">
                      <option v-for="n in mcfpNodes" :key="n.id" :value="n.id">{{ n.name }}</option>
                    </select>
                  </td>
                  <td>
                    <select class="table-input" v-model="arc.to">
                      <option v-for="n in mcfpNodes" :key="n.id" :value="n.id">{{ n.name }}</option>
                    </select>
                  </td>
                  <td>
                    <input
                      type="number"
                      step="any"
                      class="table-input"
                      v-model.number="arc.cost"
                      placeholder="Costo"
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      class="table-input"
                      v-model="arc.capacity"
                      placeholder="∞"
                      title="Ingresa un número o deja vacío / ∞ para ilimitado"
                    />
                  </td>
                  <td style="text-align: center;">
                    <button
                      type="button"
                      class="btn-del-row"
                      @click="removeMcfpArc(idx)"
                      title="Eliminar este arco"
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Alerta de Error -->
        <div v-if="mcfpError" class="calc-error-banner">
          <span class="err-icon">⚠️</span>
          <span>{{ mcfpError }}</span>
        </div>

        <!-- Ficha de Solución Óptima de Flujo a Costo Mínimo -->
        <div v-if="mcfpResult" class="exercise-card">
          <div class="exercise-header">
            <div>
              <div class="badge-tag-row">
                <span class="type-badge badge-indigo">Costo Mínimo Óptimo</span>
                <span class="dim-badge">{{ mcfpNodes.length }} Nodos, {{ mcfpArcs.length }} Arcos</span>
              </div>
              <h3 class="exercise-title">Solución Global de Flujo a Costo Mínimo</h3>
            </div>
            <div class="solution-highlight">
              <span class="sol-label">Costo Mínimo Total (Z*):</span>
              <span class="sol-value">{{ mcfpResult.optimalZDisplay }}</span>
            </div>
          </div>

          <!-- Tabla de Arcos y Flujo Óptimo -->
          <div class="matrix-section">
            <h4 class="sub-title">Topología de la Red: Arcos, Costos Unitarios y Flujo Óptimo Circulante</h4>
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Arco (i, j)</th>
                    <th>Costo Unitario (cᵢⱼ)</th>
                    <th>Capacidad Máxima (uᵢⱼ)</th>
                    <th>Flujo Óptimo (xᵢⱼ*)</th>
                    <th>Subtotal de Costo</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="arc in mcfpResult.arcsResult" :key="arc.name">
                    <td class="row-label">{{ arc.name }}</td>
                    <td>{{ arc.cost }}</td>
                    <td>{{ arc.capacityDisplay }}</td>
                    <td :class="{ 'cell-optimal': arc.flow > 0 }">
                      <strong>{{ arc.flow }}</strong>
                    </td>
                    <td>{{ arc.subtotal }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Balance de Nodos Verificados -->
          <div class="node-balance-box">
            <h4 class="sub-title">Vector de Balance en Nodos (Σ bᵢ = 0)</h4>
            <div class="node-pills-row">
              <div v-for="node in mcfpResult.nodeBalances" :key="node.name" class="node-pill">
                <span class="node-id">{{ node.name }}</span>
                <span class="node-role" :class="node.roleClass">{{ node.role }}</span>
                <span class="node-val">b = {{ node.bDisplay }}</span>
              </div>
            </div>
          </div>

          <!-- Pasos de la Solución (Caminos Mínimos Sucesivos) -->
          <div class="procedure-box">
            <h4 class="sub-title">Iteraciones: Caminos Mínimos Sucesivos</h4>
            <div class="steps-list">
              <div v-for="(it, itIdx) in mcfpResult.iterations" :key="itIdx" class="step-item">
                <span class="step-num">It {{ itIdx + 1 }}</span>
                <div class="step-content">
                  <strong>{{ it.title }}:</strong>
                  <span>{{ it.detail }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { solveHungarian } from '../../utils/hungarianSolver.js'
import { solveMaxFlow } from '../../utils/maxFlowSolver.js'
import { solveMinCostFlow } from '../../utils/minCostFlowSolver.js'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'assignment'
  },
  selectedExerciseId: {
    type: String,
    default: 'blank_networks'
  }
})

const emit = defineEmits(['clear-exercise', 'select-exercise-preset'])

// =========================================================================
// TAB 1: CALCULADORA INTERACTIVA DE ASIGNACIÓN (KUHN-MUNKRES)
// =========================================================================
const assignRows = ref(3)
const assignCols = ref(3)
const assignIsMax = ref(false)
const assignRowLabels = ref(['Recurso 1', 'Recurso 2', 'Recurso 3'])
const assignColLabels = ref(['Tarea 1', 'Tarea 2', 'Tarea 3'])
const assignMatrix = ref([
  ['', '', ''],
  ['', '', ''],
  ['', '', '']
])

const calculationResult = ref(null)
const calcError = ref(null)
const activeStepTab = ref('step1')

function setOptMode(isMax) {
  assignIsMax.value = isMax
  // No auto-calcular ni mostrar alertas: el usuario presiona "Calcular Asignación" cuando termine
  calculationResult.value = null
  calcError.value = null
}

function changeDimensions(newRows, newCols) {
  if (newRows < 2 || newRows > 6 || newCols < 2 || newCols > 6) return

  const oldMatrix = assignMatrix.value
  const newMatrix = []

  for (let i = 0; i < newRows; i++) {
    const row = []
    for (let j = 0; j < newCols; j++) {
      if (oldMatrix[i] && oldMatrix[i][j] !== undefined && oldMatrix[i][j] !== null) {
        row.push(oldMatrix[i][j])
      } else {
        row.push('')
      }
    }
    newMatrix.push(row)
  }

  const newRowLabels = []
  for (let i = 0; i < newRows; i++) {
    newRowLabels.push(assignRowLabels.value[i] || `Recurso ${i + 1}`)
  }

  const newColLabels = []
  for (let j = 0; j < newCols; j++) {
    newColLabels.push(assignColLabels.value[j] || `Tarea ${j + 1}`)
  }

  assignRows.value = newRows
  assignCols.value = newCols
  assignRowLabels.value = newRowLabels
  assignColLabels.value = newColLabels
  assignMatrix.value = newMatrix

  // Al alterar dimensiones, no se resuelve automáticamente:
  // se limpia el resultado previo para que el usuario presione "Calcular Asignación" cuando termine de ingresar datos
  calculationResult.value = null
  calcError.value = null
}

function handleCellInput() {
  const isCompletelyEmpty = assignMatrix.value.every(row =>
    row.every(val => val === '' || val === null || val === undefined)
  )
  if (isCompletelyEmpty) {
    calculationResult.value = null
    calcError.value = null
    emit('clear-exercise')
    return
  }
  // Al escribir o editar celdas, invalidamos el cálculo previo sin disparar advertencias mientras el usuario escribe
  calculationResult.value = null
  calcError.value = null
}

function calculateAssignment() {
  calcError.value = null
  const hasAnyValue = assignMatrix.value.some(row => row.some(val => val !== '' && val !== null && !isNaN(val)))
  if (!hasAnyValue) {
    calcError.value = 'Ingresa los coeficientes de la matriz o selecciona un ejercicio preconfigurado para calcular.'
    calculationResult.value = null
    return
  }
  try {
    const result = solveHungarian(
      assignMatrix.value,
      assignIsMax.value,
      assignRowLabels.value,
      assignColLabels.value
    )
    calculationResult.value = result
    if (!result.isBalanced && activeStepTab.value !== 'step0') {
      activeStepTab.value = 'step0'
    } else if (result.isBalanced && activeStepTab.value === 'step0') {
      activeStepTab.value = 'step1'
    }
  } catch (err) {
    calcError.value = err.message || 'Error al calcular el algoritmo Húngaro.'
    calculationResult.value = null
  }
}

function clearAssignMatrix() {
  assignMatrix.value = assignMatrix.value.map(row => row.map(() => ''))
  calculationResult.value = null
  calcError.value = null
  emit('clear-exercise')
}

function isCellOptimal(rowIdx, colIdx) {
  if (!calculationResult.value || !calculationResult.value.optimalPairs) return false
  return calculationResult.value.optimalPairs.some(([r, c]) => r === rowIdx && c === colIdx)
}

// =========================================================================
// TAB 2: CALCULADORA INTERACTIVA DE FLUJO MÁXIMO (EDMONDS-KARP)
// =========================================================================
const maxFlowSource = ref('1')
const maxFlowSink = ref('4')
const maxFlowArcs = ref([
  { from: '1', to: '2', capacity: '' },
  { from: '1', to: '3', capacity: '' },
  { from: '2', to: '4', capacity: '' },
  { from: '3', to: '4', capacity: '' }
])
const maxFlowResult = ref(null)
const maxFlowError = ref(null)

function addMaxFlowArc() {
  maxFlowArcs.value.push({
    from: '',
    to: '',
    capacity: ''
  })
  maxFlowResult.value = null
  maxFlowError.value = null
}

function removeMaxFlowArc(index) {
  maxFlowArcs.value.splice(index, 1)
  maxFlowResult.value = null
  maxFlowError.value = null
}

function calculateMaxFlow() {
  maxFlowError.value = null
  try {
    const res = solveMaxFlow(maxFlowSource.value, maxFlowSink.value, maxFlowArcs.value)
    maxFlowResult.value = res
  } catch (err) {
    maxFlowError.value = err.message || 'Error al calcular el flujo máximo.'
    maxFlowResult.value = null
  }
}

function clearMaxFlow() {
  maxFlowSource.value = '1'
  maxFlowSink.value = '4'
  maxFlowArcs.value = [
    { from: '1', to: '2', capacity: '' },
    { from: '2', to: '3', capacity: '' },
    { from: '3', to: '4', capacity: '' }
  ]
  maxFlowResult.value = null
  maxFlowError.value = null
  emit('clear-exercise')
}

// =========================================================================
// TAB 3: CALCULADORA INTERACTIVA DE FLUJO A COSTO MÍNIMO (MCFP)
// =========================================================================
const mcfpNodes = ref([
  { id: '1', name: 'Nodo 1', b: '' },
  { id: '2', name: 'Nodo 2', b: '' },
  { id: '3', name: 'Nodo 3', b: '' }
])

const mcfpArcs = ref([
  { from: '1', to: '2', cost: '', capacity: '' },
  { from: '2', to: '3', cost: '', capacity: '' }
])

const mcfpResult = ref(null)
const mcfpError = ref(null)

const mcfpTotalBalance = computed(() => {
  return mcfpNodes.value.reduce((acc, n) => acc + (Number(n.b) || 0), 0)
})

function addMcfpNode() {
  const nextId = String(mcfpNodes.value.length + 1)
  mcfpNodes.value.push({
    id: nextId,
    name: `Nodo ${nextId}`,
    b: ''
  })
  mcfpResult.value = null
  mcfpError.value = null
}

function removeMcfpNode(index) {
  if (mcfpNodes.value.length <= 2) return
  const removed = mcfpNodes.value[index]
  mcfpNodes.value.splice(index, 1)
  mcfpArcs.value = mcfpArcs.value.filter(a => a.from !== removed.id && a.to !== removed.id)
  mcfpResult.value = null
  mcfpError.value = null
}

function addMcfpArc() {
  const defaultFrom = mcfpNodes.value[0]?.id || '1'
  const defaultTo = mcfpNodes.value[1]?.id || '2'
  mcfpArcs.value.push({
    from: defaultFrom,
    to: defaultTo,
    cost: '',
    capacity: ''
  })
  mcfpResult.value = null
  mcfpError.value = null
}

function removeMcfpArc(index) {
  mcfpArcs.value.splice(index, 1)
  mcfpResult.value = null
  mcfpError.value = null
}

function calculateMcfp() {
  mcfpError.value = null
  try {
    const res = solveMinCostFlow(mcfpNodes.value, mcfpArcs.value)
    mcfpResult.value = res
  } catch (err) {
    mcfpError.value = err.message || 'Error al calcular flujo a costo mínimo.'
    mcfpResult.value = null
  }
}

function clearMcfp() {
  mcfpNodes.value = [
    { id: '1', name: 'Nodo 1', b: '' },
    { id: '2', name: 'Nodo 2', b: '' }
  ]
  mcfpArcs.value = [
    { from: '1', to: '2', cost: '', capacity: '' }
  ]
  mcfpResult.value = null
  mcfpError.value = null
  emit('clear-exercise')
}

// =========================================================================
// DATA: EJERCICIOS PREDEFINIDOS DE ASIGNACIÓN
// =========================================================================
const assignmentExercises = {
  asig_1: {
    rows: 3,
    cols: 3,
    isMax: false,
    rowLabels: ['Empresa A', 'Empresa B', 'Empresa C'],
    colLabels: ['Central 1', 'Central 2', 'Central 3'],
    matrix: [
      [10, 9, 5],
      [9, 8, 3],
      [6, 4, 7]
    ]
  },
  asig_2: {
    rows: 3,
    cols: 3,
    isMax: true,
    rowLabels: ['Vendedor 1', 'Vendedor 2', 'Vendedor 3'],
    colLabels: ['Zona 1', 'Zona 2', 'Zona 3'],
    matrix: [
      [40, 60, 50],
      [70, 30, 60],
      [50, 80, 40]
    ]
  },
  asig_3: {
    rows: 3,
    cols: 4,
    isMax: false,
    rowLabels: ['Conductor A', 'Conductor B', 'Conductor C'],
    colLabels: ['Camión 1', 'Camión 2', 'Camión 3', 'Camión 4'],
    matrix: [
      [180, 150, 200, 200],
      [250, 305, 450, 500],
      [200, 208, 320, 100]
    ]
  },
  asig_4: {
    rows: 4,
    cols: 4,
    isMax: false,
    rowLabels: ['Técnico 1', 'Técnico 2', 'Técnico 3', 'Técnico 4'],
    colLabels: ['Máquina 1', 'Máquina 2', 'Máquina 3', 'Máquina 4'],
    matrix: [
      [5, 11, 10, 4],
      [7, 11, 9, 12],
      [11, 3, 11, 2],
      [9, 6, 10, 5]
    ]
  },
  asig_5: {
    rows: 4,
    cols: 4,
    isMax: true,
    rowLabels: ['Vendedor 1', 'Vendedor 2', 'Vendedor 3', 'Vendedor 4'],
    colLabels: ['Zona 1', 'Zona 2', 'Zona 3', 'Zona 4'],
    matrix: [
      [24, 15, 17, 23],
      [8, 10, 22, 16],
      [21, 25, 10, 16],
      [18, 15, 24, 17]
    ]
  },
  asig_6: {
    rows: 3,
    cols: 4,
    isMax: false,
    rowLabels: ['Operario 1', 'Operario 2', 'Operario 3'],
    colLabels: ['Tarea 1', 'Tarea 2', 'Tarea 3', 'Tarea 4'],
    matrix: [
      [11, 13, 14, 10],
      [10, 12, 14, 4],
      [15, 6, 10, 11]
    ]
  }
}

// =========================================================================
// WATCHER: Sincronización reactiva con selección de ejercicios desde el Navbar
// =========================================================================
watch(() => props.selectedExerciseId, (newId) => {
  if (!newId) return

  // Si es la preconfiguración vacía por defecto:
  if (newId === 'blank_networks') {
    // 1. Reset Asignación
    assignRows.value = 3
    assignCols.value = 3
    assignIsMax.value = false
    assignRowLabels.value = ['Recurso 1', 'Recurso 2', 'Recurso 3']
    assignColLabels.value = ['Tarea 1', 'Tarea 2', 'Tarea 3']
    assignMatrix.value = [
      ['', '', ''],
      ['', '', ''],
      ['', '', '']
    ]
    calculationResult.value = null
    calcError.value = null

    // 2. Reset Flujo Máximo
    maxFlowSource.value = '1'
    maxFlowSink.value = '4'
    maxFlowArcs.value = [
      { from: '1', to: '2', capacity: '' },
      { from: '1', to: '3', capacity: '' },
      { from: '2', to: '4', capacity: '' },
      { from: '3', to: '4', capacity: '' }
    ]
    maxFlowResult.value = null
    maxFlowError.value = null

    // 3. Reset Flujo a Costo Mínimo
    mcfpNodes.value = [
      { id: '1', name: 'Nodo 1', b: '' },
      { id: '2', name: 'Nodo 2', b: '' },
      { id: '3', name: 'Nodo 3', b: '' }
    ]
    mcfpArcs.value = [
      { from: '1', to: '2', cost: '', capacity: '' },
      { from: '2', to: '3', cost: '', capacity: '' }
    ]
    mcfpResult.value = null
    mcfpError.value = null
    return
  }

  // Si es un ejercicio de Asignación:
  if (assignmentExercises[newId]) {
    const ex = assignmentExercises[newId]
    assignRows.value = ex.rows
    assignCols.value = ex.cols
    assignIsMax.value = ex.isMax
    assignRowLabels.value = [...ex.rowLabels]
    assignColLabels.value = [...ex.colLabels]
    assignMatrix.value = ex.matrix.map(row => [...row])
    calculationResult.value = null
    calcError.value = null
  }

  // Si es el ejercicio de Flujo Máximo:
  if (newId === 'max_1') {
    maxFlowSource.value = '1'
    maxFlowSink.value = '6'
    maxFlowArcs.value = [
      { from: '1', to: '2', capacity: 10 },
      { from: '1', to: '3', capacity: 8 },
      { from: '2', to: '3', capacity: 2 },
      { from: '2', to: '4', capacity: 5 },
      { from: '2', to: '5', capacity: 4 },
      { from: '3', to: '5', capacity: 9 },
      { from: '4', to: '6', capacity: 7 },
      { from: '5', to: '6', capacity: 10 }
    ]
    maxFlowResult.value = null
    maxFlowError.value = null
  }

  // Si es un ejercicio de Flujo a Costo Mínimo:
  if (newId === 'mcfp_1') {
    mcfpNodes.value = [
      { id: '1', name: 'Nodo 1', b: 4 },
      { id: '2', name: 'Nodo 2', b: 0 },
      { id: '3', name: 'Nodo 3', b: 0 },
      { id: '4', name: 'Nodo 4', b: -4 }
    ]
    mcfpArcs.value = [
      { from: '1', to: '2', cost: 2, capacity: 3 },
      { from: '1', to: '3', cost: 4, capacity: 2 },
      { from: '2', to: '3', cost: 1, capacity: 2 },
      { from: '2', to: '4', cost: 5, capacity: 2 },
      { from: '3', to: '4', cost: 3, capacity: 4 }
    ]
    mcfpResult.value = null
    mcfpError.value = null
  } else if (newId === 'mcfp_2') {
    mcfpNodes.value = [
      { id: '1', name: 'Planta 1', b: 40 },
      { id: '2', name: 'Planta 2', b: 30 },
      { id: '3', name: 'Cliente A', b: -20 },
      { id: '4', name: 'Cliente B', b: -25 },
      { id: '5', name: 'Cliente C', b: -25 }
    ]
    mcfpArcs.value = [
      { from: '1', to: '3', cost: 4, capacity: '∞' },
      { from: '1', to: '4', cost: 6, capacity: '∞' },
      { from: '1', to: '5', cost: 8, capacity: '∞' },
      { from: '2', to: '3', cost: 5, capacity: '∞' },
      { from: '2', to: '4', cost: 3, capacity: '∞' },
      { from: '2', to: '5', cost: 7, capacity: '∞' }
    ]
    mcfpResult.value = null
    mcfpError.value = null
  } else if (newId === 'mcfp_3') {
    mcfpNodes.value = [
      { id: '1', name: 'Nodo 1', b: 6 },
      { id: '2', name: 'Nodo 2', b: 0 },
      { id: '3', name: 'Nodo 3', b: 0 },
      { id: '4', name: 'Nodo 4', b: -2 },
      { id: '5', name: 'Nodo 5', b: -4 }
    ]
    mcfpArcs.value = [
      { from: '1', to: '2', cost: 1, capacity: 4 },
      { from: '1', to: '3', cost: 3, capacity: 3 },
      { from: '2', to: '3', cost: 1, capacity: 2 },
      { from: '2', to: '4', cost: 4, capacity: 3 },
      { from: '2', to: '5', cost: 6, capacity: 2 },
      { from: '3', to: '4', cost: 2, capacity: 2 },
      { from: '3', to: '5', cost: 1, capacity: 4 }
    ]
    mcfpResult.value = null
    mcfpError.value = null
  }
}, { immediate: true })

onMounted(() => {
  // Paradigma CIMS: al cargar la vista o seleccionar ejercicios preconfigurados,
  // únicamente se preconfiguran los campos del formulario. El usuario decide cuándo presionar "Calcular" o modificar a su gusto.
})
</script>

<style scoped src="./NetworksApp.css"></style>
