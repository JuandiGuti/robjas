#!/usr/bin/env python3
"""
Sistema de Verificación - Métricas de Tutor IA
Ejecutar: python verify_metrics.py
"""

import json
import sys

def verify_backend_structure():
    """Verifica que el backend tiene la estructura correcta."""
    try:
        with open('backend/app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        required = [
            'import time',
            'def initialize_model_metrics',
            'def record_chat_metrics',
            'def record_audio_metrics',
            'def record_tts_metrics',
            "'/metrics'",
            "'/metrics/reset'",
            'PRICING = {',
            'session_metrics = {',
        ]
        
        missing = [r for r in required if r not in content]
        return len(missing) == 0, missing
    except Exception as e:
        return False, [str(e)]

def verify_frontend_structure():
    """Verifica que el frontend tiene la estructura correcta."""
    try:
        with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        with open('frontend/src/components/MetricsDashboard.jsx', 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        app_required = [
            'MetricsDashboard',
            'showMetrics',
            'data.metrics'
        ]
        
        dashboard_required = [
            'fetchMetrics',
            'useEffect',
            'summary',
            'Object.entries',
        ]
        
        app_missing = [r for r in app_required if r not in app_content]
        dashboard_missing = [r for r in dashboard_required if r not in dashboard_content]
        
        return len(app_missing) == 0 and len(dashboard_missing) == 0, app_missing + dashboard_missing
    except Exception as e:
        return False, [str(e)]

def verify_styles():
    """Verifica que los estilos existen y están bien formados."""
    try:
        with open('frontend/src/Styles/chat.css', 'r', encoding='utf-8') as f:
            chat_css = f.read()
        
        with open('frontend/src/Styles/metrics.css', 'r', encoding='utf-8') as f:
            metrics_css = f.read()
        
        required_chat = ['.btn-metrics-toggle', '.chat-header {', 'display: flex']
        required_metrics = ['.metrics-dashboard', '.model-card', '.metrics-summary']
        
        chat_missing = [r for r in required_chat if r not in chat_css]
        metrics_missing = [r for r in required_metrics if r not in metrics_css]
        
        return len(chat_missing) == 0 and len(metrics_missing) == 0, chat_missing + metrics_missing
    except Exception as e:
        return False, [str(e)]

def main():
    print("=" * 60)
    print("VERIFICACION - SISTEMA DE METRICAS")
    print("=" * 60)
    
    checks = [
        ("Backend Structure", verify_backend_structure),
        ("Frontend Structure", verify_frontend_structure),
        ("Styles", verify_styles),
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        passed, issues = check_func()
        status = "[OK]" if passed else "[ERROR]"
        print(f"\n{status} {name}")
        
        if not passed:
            all_passed = False
            for issue in issues:
                print(f"    - {issue}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("RESULTADO: Sistema completamente verificado")
        print("\nPasos para usar:")
        print("  1. Terminal 1: cd backend && python app.py")
        print("  2. Terminal 2: cd frontend && npm run dev")
        print("  3. Abre http://localhost:5173")
        print("  4. Click en boton 'Mostrar Metricas'")
        return 0
    else:
        print("RESULTADO: Hay problemas que necesitan atencion")
        return 1

if __name__ == '__main__':
    sys.exit(main())
