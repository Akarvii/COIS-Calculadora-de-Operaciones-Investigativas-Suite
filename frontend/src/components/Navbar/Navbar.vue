<template>
  <header class="navbar">
    <!-- Brand / Title Row Left -->
    <div class="nav-brand-container">
      <!-- Back button only when inside a module -->
      <button
        v-if="activeModule"
        class="btn-module-switch"
        @click="$emit('back-to-selector')"
        title="Volver al menú de selección de módulos"
      >
        <svg
          width="15"
          height="15"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
        <span>Módulos</span>
      </button>

      <div class="nav-brand">
        <div class="logo-icon">
          <img :src="brandLogo" :alt="brandTitle" class="brand-logo-img" />
        </div>
        <div class="brand-text">
          <div class="brand-title-row">
            <!-- Dynamic Brand Title -->
            <h1 class="nav-title">{{ brandTitle }}</h1>
            <!-- Only COIS (main suite) has version tag -->
            <span v-if="!activeModule" class="brand-tag">v2.0</span>
          </div>
          <span class="nav-subtitle">{{ brandSubtitle }}</span>
        </div>
      </div>
    </div>

    <!-- Center / Right Controls -->
    <div class="nav-controls">
      <!-- SIMPLEX TOOLS (Only when activeModule === 'cims') -->
      <template v-if="activeModule === 'cims'">
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

        <!-- Custom Examples Dropdown -->
        <div class="custom-dropdown" ref="dropdownRef">
          <button
            type="button"
            class="dropdown-trigger"
            :class="{ 'is-open': isOpen, 'is-selected': !!selectedExample }"
            @click="isOpen = !isOpen"
            title="Seleccionar configuraciones o problemas de ejemplo"
          >
            <div class="trigger-content">
              <span class="example-icon-wrapper">
                <svg
                  v-if="selectedExample?.icon === 'settings'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"
                  />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                <svg
                  v-else-if="selectedExample?.icon === 'factory'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"
                  />
                  <path d="M17 18h1" />
                  <path d="M12 18h1" />
                  <path d="M7 18h1" />
                </svg>
                <svg
                  v-else-if="selectedExample?.icon === 'layers'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polygon points="12 2 2 7 12 12 22 7 12 2" />
                  <polyline points="2 17 12 22 22 17" />
                  <polyline points="2 12 12 17 22 12" />
                </svg>
                <svg
                  v-else-if="selectedExample?.icon === 'fraction'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="12" cy="6" r="2" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <circle cx="12" cy="18" r="2" />
                </svg>
                <svg
                  v-else-if="selectedExample?.icon === 'infinity'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M12 12c-2-2.67-4-4-6-4a4 4 0 1 0 0 8c2 0 4-1.33 6-4Zm0 0c2 2.67 4 4 6 4a4 4 0 0 0 0-8c-2 0-4 1.33-6 4Z"
                  />
                </svg>
                <svg
                  v-else-if="selectedExample?.icon === 'alert'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
                </svg>
                <svg
                  v-else
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="m6 14 1.45-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.55 6a2 2 0 0 1-1.94 1.5H4a2 2 0 0 1-2-2V5c0-1.1.9-2 2-2h3.93a2 2 0 0 1 1.66.9l.82 1.2a2 2 0 0 0 1.66.9H18a2 2 0 0 1 2 2v2"
                  />
                </svg>
              </span>
              <span class="trigger-label">
                {{
                  selectedExample
                    ? selectedExample.title
                    : "Seleccionar Configuraciones"
                }}
              </span>
            </div>
            <svg
              class="chevron-icon"
              :class="{ rotate: isOpen }"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
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
                <svg
                  v-if="item.icon === 'settings'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"
                  />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                <svg
                  v-else-if="item.icon === 'factory'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"
                  />
                  <path d="M17 18h1" />
                  <path d="M12 18h1" />
                  <path d="M7 18h1" />
                </svg>
                <svg
                  v-else-if="item.icon === 'layers'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polygon points="12 2 2 7 12 12 22 7 12 2" />
                  <polyline points="2 17 12 22 22 17" />
                  <polyline points="2 12 12 17 22 12" />
                </svg>
                <svg
                  v-else-if="item.icon === 'fraction'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="12" cy="6" r="2" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <circle cx="12" cy="18" r="2" />
                </svg>
                <svg
                  v-else-if="item.icon === 'infinity'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M12 12c-2-2.67-4-4-6-4a4 4 0 1 0 0 8c2 0 4-1.33 6-4Zm0 0c2 2.67 4 4 6 4a4 4 0 0 0 0-8c-2 0-4 1.33-6 4Z"
                  />
                </svg>
                <svg
                  v-else-if="item.icon === 'alert'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
                </svg>
              </div>
              <div class="item-text">
                <span class="item-title">{{ item.title }}</span>
                <span class="item-desc">{{ item.desc }}</span>
              </div>
              <svg
                v-if="selectedExample?.id === item.id"
                class="check-selected"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#38BDF8"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </button>
          </div>
        </div>
      </template>

      <!-- NETWORKS CONTROLS (Only when activeModule === 'networks') -->
      <template v-else-if="activeModule === 'networks'">
        <nav class="nav-networks-tabs">
          <button
            class="net-tab-btn"
            :class="{ active: networksTab === 'assignment', 'is-locked': isTabLocked('assignment') }"
            :disabled="isTabLocked('assignment')"
            @click="!isTabLocked('assignment') && $emit('update:networksTab', 'assignment')"
            :title="isTabLocked('assignment') ? 'Pestaña bloqueada por ejercicio activo. Pulsa Limpiar o selecciona otro ejercicio en el menú superior.' : ''"
          >
            <span>Asignación (Húngaro)</span>
          </button>
          <button
            class="net-tab-btn"
            :class="{ active: networksTab === 'max_flow', 'is-locked': isTabLocked('max_flow') }"
            :disabled="isTabLocked('max_flow')"
            @click="!isTabLocked('max_flow') && $emit('update:networksTab', 'max_flow')"
            :title="isTabLocked('max_flow') ? 'Pestaña bloqueada por ejercicio activo. Pulsa Limpiar o selecciona otro ejercicio en el menú superior.' : ''"
          >
            <span>Flujo Máximo</span>
          </button>
          <button
            class="net-tab-btn"
            :class="{ active: networksTab === 'min_cost_flow', 'is-locked': isTabLocked('min_cost_flow') }"
            :disabled="isTabLocked('min_cost_flow')"
            @click="!isTabLocked('min_cost_flow') && $emit('update:networksTab', 'min_cost_flow')"
            :title="isTabLocked('min_cost_flow') ? 'Pestaña bloqueada por ejercicio activo. Pulsa Limpiar o selecciona otro ejercicio en el menú superior.' : ''"
          >
            <span>Flujo a Costo Mínimo</span>
          </button>
        </nav>

        <!-- Custom Networks Exercises Dropdown (Exact same design and styling as CIMS) -->
        <div class="custom-dropdown" ref="networksDropdownRef">
          <button
            type="button"
            class="dropdown-trigger"
            :class="{ 'is-open': isNetDropdownOpen, 'is-selected': !!selectedNetExercise }"
            @click="isNetDropdownOpen = !isNetDropdownOpen"
            title="Seleccionar ejercicios resueltos de Redes y Optimización"
          >
            <div class="trigger-content">
              <span class="example-icon-wrapper">
                <svg
                  v-if="selectedNetExercise?.icon === 'factory'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/>
                  <path d="M17 18h1"/><path d="M12 18h1"/><path d="M7 18h1"/>
                </svg>
                <svg
                  v-else-if="selectedNetExercise?.icon === 'layers'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polygon points="12 2 2 7 12 12 22 7 12 2"/>
                  <polyline points="2 17 12 22 22 17"/>
                  <polyline points="2 12 12 17 22 12"/>
                </svg>
                <svg
                  v-else-if="selectedNetExercise?.icon === 'fraction'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="12" cy="6" r="2"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                  <circle cx="12" cy="18" r="2"/>
                </svg>
                <svg
                  v-else-if="selectedNetExercise?.icon === 'infinity'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M12 12c-2-2.67-4-4-6-4a4 4 0 1 0 0 8c2 0 4-1.33 6-4Zm0 0c2 2.67 4 4 6 4a4 4 0 0 0 0-8c-2 0-4 1.33-6 4Z"/>
                </svg>
                <svg
                  v-else
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </span>
              <span class="trigger-label">
                {{ selectedNetExercise ? selectedNetExercise.title : "Seleccionar Ejercicio de Redes" }}
              </span>
            </div>
            <svg
              class="chevron-icon"
              :class="{ rotate: isNetDropdownOpen }"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>

          <!-- Dropdown Menu List -->
          <div v-if="isNetDropdownOpen" class="dropdown-menu">
            <div class="dropdown-header">
              <span>Ejercicios de Redes</span>
            </div>

            <!-- Predeterminado arriba sin grupo -->
            <button
              class="dropdown-item"
              :class="{ 'is-active': selectedNetExercise?.id === blankNetworkExercise.id }"
              @click="selectNetworkExercise(blankNetworkExercise)"
            >
              <div class="item-icon-container" :class="blankNetworkExercise.iconClass">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </div>
              <div class="item-text">
                <span class="item-title">{{ blankNetworkExercise.title }}</span>
                <span class="item-desc">{{ blankNetworkExercise.desc }}</span>
              </div>
              <svg
                v-if="selectedNetExercise?.id === blankNetworkExercise.id"
                class="check-selected"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#38BDF8"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </button>

            <!-- Grupos: Asignación, Flujo Máximo, Flujo a Costo Mínimo -->
            <template v-for="group in networkExerciseGroups" :key="group.category">
              <div class="dropdown-category-divider">
                <span>{{ group.category }}</span>
              </div>
              <button
                v-for="item in group.items"
                :key="item.id"
                class="dropdown-item"
                :class="{ 'is-active': selectedNetExercise?.id === item.id }"
                @click="selectNetworkExercise(item)"
              >
                <div class="item-icon-container" :class="item.iconClass">
                  <svg
                    v-if="item.icon === 'factory'"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/>
                    <path d="M17 18h1"/><path d="M12 18h1"/><path d="M7 18h1"/>
                  </svg>
                  <svg
                    v-else-if="item.icon === 'layers'"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <polygon points="12 2 2 7 12 12 22 7 12 2"/>
                    <polyline points="2 17 12 22 22 17"/>
                    <polyline points="2 12 12 17 22 12"/>
                  </svg>
                  <svg
                    v-else-if="item.icon === 'fraction'"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <circle cx="12" cy="6" r="2"/>
                    <line x1="5" y1="12" x2="19" y2="12"/>
                    <circle cx="12" cy="18" r="2"/>
                  </svg>
                  <svg
                    v-else-if="item.icon === 'infinity'"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M12 12c-2-2.67-4-4-6-4a4 4 0 1 0 0 8c2 0 4-1.33 6-4Zm0 0c2 2.67 4 4 6 4a4 4 0 0 0 0-8c-2 0-4 1.33-6 4Z"/>
                  </svg>
                  <svg
                    v-else
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </div>
                <div class="item-text">
                  <span class="item-title">{{ item.title }}</span>
                  <span class="item-desc">{{ item.desc }}</span>
                </div>
                <svg
                  v-if="selectedNetExercise?.id === item.id"
                  class="check-selected"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#38BDF8"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </button>
            </template>
          </div>
        </div>
      </template>

      <!-- BACKEND API STATUS BOX (Always visible on far right) -->
      <div
        class="api-status-box"
        :class="statusBoxClass"
        :title="statusTooltip"
      >
        <span class="status-dot"></span>
        <span class="status-label">{{ statusText }}</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";

const props = defineProps({
  activeModule: {
    type: String,
    default: null, // null = hub selector, 'cims' = COIS-IMS, 'networks' = COIS-Networks
  },
  showFractions: {
    type: Boolean,
    default: true,
  },
  apiStatus: {
    type: String,
    default: "connected", // 'connected', 'disconnected', 'error'
  },
  networksTab: {
    type: String,
    default: "assignment",
  },
  selectedNetworkExerciseId: {
    type: String,
    default: "blank_networks",
  },
});

const emit = defineEmits([
  "update:showFractions",
  "update:networksTab",
  "load-example",
  "select-network-exercise",
  "back-to-selector",
]);

// Dynamic Brand Title & Subtitle
const brandTitle = computed(() => {
  if (!props.activeModule) return "COIS";
  if (props.activeModule === "cims") return "CIMS";
  return "COIS-Networks";
});

const brandSubtitle = computed(() => {
  if (!props.activeModule)
    return "Calculadora de Operaciones Investigativas Suite";
  if (props.activeModule === "cims")
    return "Calculadora Investigativa del Método Simplex";
  return "Optimización en Redes y Algoritmos Combinatorios";
});

const brandLogo = computed(() => {
  if (!props.activeModule) return "/logo_cois.png";
  if (props.activeModule === "cims") return "/logo_cims.png";
  return "/logo_cims_network.png";
});

// Dynamic API Status Badge styling & text
const statusBoxClass = computed(() => {
  if (props.apiStatus === "connected") return "status-connected";
  if (props.apiStatus === "error") return "status-error";
  return "status-disconnected";
});

const statusText = computed(() => {
  if (props.apiStatus === "connected") return "API Conectada";
  if (props.apiStatus === "error") return "Error API";
  return "API Desconectada";
});

const statusTooltip = computed(() => {
  if (props.apiStatus === "connected")
    return "Servidor Backend Python (FastAPI) en línea y listo";
  if (props.apiStatus === "error")
    return "El backend respondió con un código de error";
  return "No se pudo conectar con el servidor (http://localhost:8000)";
});

// Examples Dropdown state
const isOpen = ref(false);
const dropdownRef = ref(null);

const examplesList = [
  {
    id: "blank_config",
    title: "Seleccionar Configuraciones",
    icon: "settings",
    iconClass: "icon-cyan",
    desc: "Campos vacíos para configurar y meter datos desde cero",
  },
  {
    id: "classic_production",
    title: "Producción Clásica (Max 2 var)",
    icon: "factory",
    iconClass: "icon-blue",
    desc: "Max Z = 3x₁ + 5x₂ con restricciones ≤",
  },
  {
    id: "mixed_two_phase",
    title: "Problema Mixto (Dos Fases)",
    icon: "layers",
    iconClass: "icon-indigo",
    desc: "Min Z = 4x₁ + x₂ con operadores =, ≥, ≤",
  },
  {
    id: "fractional_optimum",
    title: "Óptimo Fraccionario (27/2)",
    icon: "fraction",
    iconClass: "icon-emerald",
    desc: "Max Z con soluciones fraccionarias exactas",
  },
  {
    id: "unbounded_example",
    title: "Problema No Acotado",
    icon: "infinity",
    iconClass: "icon-amber",
    desc: "Región factible abierta hacia el infinito",
  },
  {
    id: "infeasible_example",
    title: "Problema Infactible",
    icon: "alert",
    iconClass: "icon-rose",
    desc: "Restricciones contradictorias sin solución",
  },
];

// Dropdown de ejercicios exclusivos de Networks
const blankNetworkExercise = {
  id: "blank_networks",
  tab: "assignment",
  title: "Seleccionar Ejercicios",
  icon: "settings",
  iconClass: "icon-cyan",
  desc: "Campos vacíos para configurar y meter datos desde cero",
};

const networkExerciseGroups = [
  {
    category: "Asignación (Método Húngaro)",
    items: [
      {
        id: "asig_1",
        tab: "assignment",
        title: "Centrales Térmicas (3x3 Min)",
        icon: "layers",
        iconClass: "icon-cyan",
        desc: "Minimizar costos de 3 empresas a 3 centrales (Z* = 17)",
      },
      {
        id: "asig_2",
        tab: "assignment",
        title: "Vendedores a Zonas (3x3 Max)",
        icon: "factory",
        iconClass: "icon-emerald",
        desc: "Maximizar beneficios de 3 vendedores (Z* = 200)",
      },
      {
        id: "asig_3",
        tab: "assignment",
        title: "Caso Desbalanceado (3x4)",
        icon: "settings",
        iconClass: "icon-amber",
        desc: "3 conductores a 4 camiones con agente ficticio (Z* = 500)",
      },
      {
        id: "asig_4",
        tab: "assignment",
        title: "Técnicos a Máquinas (4x4 Min)",
        icon: "layers",
        iconClass: "icon-blue",
        desc: "4 técnicos a 4 máquinas por Algoritmo Húngaro (Z* = 22)",
      },
      {
        id: "asig_5",
        tab: "assignment",
        title: "Vendedores a Zonas (4x4 Max)",
        icon: "factory",
        iconClass: "icon-emerald",
        desc: "4 vendedores a 4 zonas con constante K = 25 (Zmax = 89)",
      },
      {
        id: "asig_6",
        tab: "assignment",
        title: "Operarios a Tareas (3x4 Min)",
        icon: "settings",
        iconClass: "icon-purple",
        desc: "3 operarios a 4 tareas con operario ficticio (Z* = 21)",
      },
    ],
  },
  {
    category: "Flujo Máximo",
    items: [
      {
        id: "max_1",
        tab: "max_flow",
        title: "Red de Distribución (6 Nodos)",
        icon: "infinity",
        iconClass: "icon-purple",
        desc: "Capacidad máxima entre Fuente y Sumidero (Flujo* = 14)",
      },
    ],
  },
  {
    category: "Flujo a Costo Mínimo",
    items: [
      {
        id: "mcfp_1",
        tab: "min_cost_flow",
        title: "Red 4 Nodos Capacitada",
        icon: "fraction",
        iconClass: "icon-blue",
        desc: "Envío de 4 unidades por red capacitada (Z* = 26)",
      },
      {
        id: "mcfp_2",
        tab: "min_cost_flow",
        title: "Modelo de Transporte (2x3)",
        icon: "layers",
        iconClass: "icon-indigo",
        desc: "2 plantas abastecen 3 clientes a costo mínimo (Z* = 350)",
      },
      {
        id: "mcfp_3",
        tab: "min_cost_flow",
        title: "Transbordo Multidestino",
        icon: "infinity",
        iconClass: "icon-purple",
        desc: "Nodo 1 a nodos 4 y 5 mediante transbordo (Z* = 24)",
      },
    ],
  },
];

const allNetworkExercises = [
  blankNetworkExercise,
  ...networkExerciseGroups.flatMap((g) => g.items),
];

const selectedExample = ref(examplesList[0]);

// Estado y referencias para el dropdown de Networks
const isNetDropdownOpen = ref(false);
const networksDropdownRef = ref(null);

const selectedNetExercise = computed(() => {
  return (
    allNetworkExercises.find(
      (ex) => ex.id === props.selectedNetworkExerciseId
    ) || blankNetworkExercise
  );
});

function selectExample(item) {
  selectedExample.value = item;
  isOpen.value = false;
  emit("load-example", item.id);
}

function selectNetworkExercise(item) {
  isNetDropdownOpen.value = false;
  if (item.id !== 'blank_networks') {
    emit("update:networksTab", item.tab);
  }
  emit("select-network-exercise", item.id);
}

function isTabLocked(tabKey) {
  if (!props.selectedNetworkExerciseId || props.selectedNetworkExerciseId === 'blank_networks') {
    return false;
  }
  return selectedNetExercise.value?.tab !== tabKey;
}

function handleClickOutside(event) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false;
  }
  if (
    networksDropdownRef.value &&
    !networksDropdownRef.value.contains(event.target)
  ) {
    isNetDropdownOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});

defineExpose({
  clearSelection: () => {
    selectedExample.value = examplesList[0];
  },
  setSelection: (exampleId) => {
    const found = examplesList.find((e) => e.id === exampleId);
    if (found) selectedExample.value = found;
  },
});
</script>

<style scoped src="./Navbar.css"></style>
