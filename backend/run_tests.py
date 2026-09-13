import sys
import os

# Set UTF-8 encoding for standard output on Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

def main():
    print("=" * 70)
    print(" [TESTS] EJECUTANDO SUITE DE PRUEBAS UNITARIAS - SIMPLEX & SIMPLEX REVISADO")
    print("=" * 70)
    print(" Modulos evaluados:")
    print("   1. Validacion estricta y seguridad de entradas (Pydantic / Dimensiones / Tipos)")
    print("   2. Prevencion de colapsos matematicos (Division por cero, Bland's Rule, No Acotados, Infactibles)")
    print("   3. Simplex Tabular Tradicional (Pivoteo Gauss-Jordan exacto)")
    print("   4. Simplex Revisado (Inversa B^-1, Multiplicadores duales pi, Costos reducidos bajo demanda)")
    print("   5. Consistencia cruzada (Estandar vs. Revisado producen identico valor Z y solucion)")
    print("   6. Analisis de Sensibilidad (Precios Sombra y Rangos permisibles)")
    print("   7. Endpoints REST de FastAPI e integracion")
    print("=" * 70)
    
    exit_code = pytest.main([
        "-v",
        "-s",
        os.path.join(os.path.dirname(__file__), "tests")
    ])
    
    if exit_code == 0:
        print("\n" + "=" * 70)
        print(" [OK] TODAS LAS PRUEBAS UNITARIAS PASARON EXITOSAMENTE (100% EFECTIVIDAD)")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print(" [FAIL] ALGUNAS PRUEBAS FALLARON. REVISE EL LOG SUPERIOR.")
        print("=" * 70)

if __name__ == "__main__":
    main()
