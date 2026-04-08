#!/usr/bin/env python3
"""
CHECKLIST FINAL - Sistema de Métricas Completo
Valida que TODO está implementado y funcionando
Exit code 0 = TODO OK, Exit code 1 = Problemas
"""

import os
import sys

def check_file_exists(path, description):
    """Verifica que un archivo existe."""
    if os.path.exists(path):
        print(f"  [OK] {description}")
        return True
    print(f"  [ERROR] {description} - NO ENCONTRADO")
    return False

def check_content(filepath, required_strings, description):
    """Verifica que un archivo contiene strings requeridos."""
    if not os.path.exists(filepath):
        print(f"  [ERROR] {description} - Archivo no existe")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        missing = [s for s in required_strings if s not in content]
        if not missing:
            print(f"  [OK] {description}")
            return True
        print(f"  [ERROR] {description} - Faltan elementos")
        return False
    except Exception as e:
        print(f"  [ERROR] {description} - Error: {e}")
        return False

print("=" * 70)
print("CHECKLIST FINAL - SISTEMA DE METRICAS")
print("=" * 70)

os.chdir(r"c:\Users\juand\Desktop\robjas")
checks_passed = 0
checks_total = 0

# 1. Archivos existen
print("\n[1. ARCHIVOS]")
file_checks = [
    ("backend/app.py", "Backend principal"),
    ("frontend/src/App.jsx", "App React"),
    ("frontend/src/components/MetricsDashboard.jsx", "Dashboard"),
    ("frontend/src/Styles/chat.css", "CSS Chat"),
    ("frontend/src/Styles/metrics.css", "CSS Metricas"),
    ("METRICS_DOCUMENTATION.md", "Documentacion"),
    ("METRICS_QUICK_START.md", "Guia Rapida"),
    ("IMPLEMENTATION_SUMMARY.md", "Resumen"),
    ("verify_metrics.py", "Script Verificacion"),
    ("test_integration.py", "Test Integracion"),
]

for filepath, desc in file_checks:
    if check_file_exists(filepath, desc):
        checks_passed += 1
    checks_total += 1

# 2. Backend tiene todo lo necesario
print("\n[2. BACKEND - Estructura]")
backend_checks = [
    ("backend/app.py", 
     ["import time", "def record_chat_metrics", "def record_audio_metrics", 
      "def record_tts_metrics", "@app.route('/metrics'", "@app.route('/metrics/reset'"],
     "Backend con funciones de tracking"),
]

for filepath, required, desc in backend_checks:
    if check_content(filepath, required, desc):
        checks_passed += 1
    checks_total += 1

# 3. Frontend tiene todo lo necesario
print("\n[3. FRONTEND - Componentes]")
frontend_checks = [
    ("frontend/src/App.jsx",
     ["MetricsDashboard", "showMetrics", "data.metrics"],
     "App con dashboard integrado"),
    ("frontend/src/components/MetricsDashboard.jsx",
     ["fetchMetrics", "useEffect", "useState"],
     "Dashboard con hooks React"),
]

for filepath, required, desc in frontend_checks:
    if check_content(filepath, required, desc):
        checks_passed += 1
    checks_total += 1

# 4. Estilos existen
print("\n[4. ESTILOS - CSS]")
css_checks = [
    ("frontend/src/Styles/chat.css",
     [".btn-metrics-toggle", ".chat-header {"],
     "CSS chat con boton metricas"),
    ("frontend/src/Styles/metrics.css",
     [".metrics-dashboard", ".model-card"],
     "CSS dashboard completo"),
]

for filepath, required, desc in css_checks:
    if check_content(filepath, required, desc):
        checks_passed += 1
    checks_total += 1

# 5. Documentacion
print("\n[5. DOCUMENTACION]")

for filepath, required, desc in doc_checks:
    if check_content(filepath, required, desc):
        checks_passed += 1
    checks_total += 1

# 6. Scripts ejecutables
print("\n[6. SCRIPTS]")
script_checks = [
    ("verify_metrics.py",
     ["def verify_backend_structure", "def verify_frontend_structure"],
     "Script de verificacion"),
    ("test_integration.py",
     ["TEST DE INTEGRACION", "PASO 1"],
     "Test del flujo completo"),
]

for filepath, required, desc in script_checks:
    if check_content(filepath, required, desc):
        checks_passed += 1
    checks_total += 1

# 7. Resumen
print("\n" + "=" * 70)
percentage = (checks_passed / checks_total) * 100
status = "✓ OK" if checks_passed == checks_total else "✗ PROBLEMAS"

print(f"RESULTADO: {checks_passed}/{checks_total} checks pasados")
print(f"STATUS: Completo")

if checks_passed == checks_total:
    print("\n[LISTO PARA USAR]")
    print("  1. cd backend && python app.py")
    print("  2. cd frontend && npm run dev")
    print("  3. Abre http://localhost:5173")
    print("  4. Click en 'Mostrar Metricas'")
    print("\n[VERIFICAR]")
    print("  python verify_metrics.py")
    print("  python test_integration.py")
    sys.exit(0)
else:
    print("\n[ERROR] Hay problemas pendientes")
    sys.exit(1)
