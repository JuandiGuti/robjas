# 📊 Documentación del Sistema de Métricas

## Descripción General

El sistema de métricas está completamente implementado en tu proyecto. Ahora puedes:

- ✅ Rastrear **tokens entrada/salida** de cada modelo
- ✅ Medir **tiempo de respuesta** en cada llamada
- ✅ Calcular **costo estimado** por uso
- ✅ Ver estatísticas en **tiempo real** en el frontend
- ✅ Analizar uso por **cada modelo**

---

## 🔧 Backend - Endpoints

### 1. `/metrics` (GET)
Devuelve todas las métricas acumuladas de la sesión.

**Respuesta de ejemplo:**
```json
{
  "summary": {
    "total_messages": 5,
    "total_cost": 0.0234,
    "total_errors": 0,
    "session_duration_seconds": 125.43
  },
  "models": {
    "ft:gpt-4o-mini-2024-07-18:personal:tutor-robjas:DRueFPtg": {
      "calls": 5,
      "tokens_input": 850,
      "tokens_output": 420,
      "total_tokens": 1270,
      "total_cost": 0.0234,
      "total_time_seconds": 8.75,
      "avg_response_time_ms": 1750,
      "errors": 0
    },
    "gpt-4o-mini-transcribe": { ... },
    "gpt-4o-mini-tts": { ... }
  }
}
```

### 2. `/metrics/reset` (POST)
Reinicia todas las métricas a cero (útil para comenzar una nueva sesión).

**Respuesta:**
```json
{
  "message": "Metrics reset successfully"
}
```

### 3. `/chat` (POST) - Actualizado
Ahora devuelve información de métricas en cada respuesta.

**Nueva respuesta:**
```json
{
  "response": "Tu respuesta aquí...",
  "metrics": {
    "tokens_input": 150,
    "tokens_output": 45,
    "response_time_ms": 1543.25
  }
}
```

---

## 📱 Frontend - Componente Dashboard

### Ubicación
`frontend/src/components/MetricsDashboard.jsx`

### Características

1. **Botón "Mostrar Métricas"** en el encabezado del chat
2. **Auto-actualización cada 3 segundos** (puede desactivarse)
3. **Resumen General:**
   - Total de mensajes
   - Costo acumulado
   - Errores
   - Duración de sesión

4. **Métricas por Modelo:**
   - Número de llamadas
   - Tiempo promedio de respuesta
   - Tokens entrada/salida (para chat)
   - Costo por modelo

---

## 💰 Estructura de Precios

Los precios están configurados en `backend/app.py`:

### Chat (ft:gpt-4o-mini)
- **Input:** $0.075 por 1M tokens
- **Output:** $0.30 por 1M tokens

### Transcripción (gpt-4o-mini-transcribe)
- **Price:** $0.006 por minuto de audio

### Text-to-Speech (gpt-4o-mini-tts)
- **Price:** $0.015 por 1000 caracteres

> **Nota:** Estos precios son aproximados. Actualiza `PRICING` en `app.py` si hay cambios.

---

## 📊 Métricas Disponibles por Modelo

### Para Chat
- `tokens_input`: Número de tokens en el prompt
- `tokens_output`: Número de tokens en la respuesta
- `total_tokens`: Suma total
- `avg_response_time_ms`: Tiempo promedio de respuesta

### Para Audio (STT)
- `calls`: Número de transcripciones
- `total_time_seconds`: Tiempo total procesado
- `avg_response_time_ms`: Tiempo promedio

### Para Audio (TTS)
- `calls`: Número de generaciones de audio
- `total_cost`: Costo total (basado en caracteres)

---

## 🛠️ Cómo Usar

### 1. **Ver Métricas en el Chat**
- Haz clic en **"Mostrar Métricas"** en la esquina superior derecha del chat
- Verás un panel con todas las estadísticas en tiempo real

### 2. **API Directa**
Desde Terminal o Postman:

**Obtener métricas:**
```bash
curl http://localhost:5000/metrics
```

**Reiniciar métricas:**
```bash
curl -X POST http://localhost:5000/metrics/reset
```

### 3. **Datos en Cada Respuesta**
Cada mensaje del bot ahora incluye:
```
📊 Tokens entrada: 150 | Tokens salida: 45 | Tiempo: 1543ms
```

---

## 🔍 Ejemplo Completo de Uso

1. **Inicia el servidor:** `python app.py`
2. **Abre el chat en el navegador**
3. **Haz clic en "Mostrar Métricas"**
4. **Envía un mensaje** 
5. **Observa:**
   - Los tokens de entrada/salida
   - El tiempo de respuesta
   - El costo estimado
   - El número total de llamadas por modelo

---

## 📈 Casos de Uso

### Monitoreo de Costos
Usa el dashboard para:
- Ver cuánto cuesta cada sesión
- Identificar qué modelo es más económico
- Establecer alertas de gasto

### Optimización de Rendimiento
- Identifica qué modelos son más rápidos
- Varía los prompts para reducir tokens
- Ajusta `max_tokens` según el análisis

### Debugging
- Detecta si hay demasiados errores
- Analiza el ratio entrada/salida
- Verifica si las llamadas son innecesarias

---

## 🚀 Mejoras Futuras

Aquí hay ideas para expandir el sistema:

1. **Exportar métricas a CSV**
   ```python
   @app.route('/metrics/export')
   def export_metrics():
       # Convierte a CSV y descarga
   ```

2. **Gráficos en tiempo real**
   - Usar Chart.js o Plotly en el frontend
   - Mostrar tendencias de costo y tiempo

3. **Base de datos persistente**
   - Guardar métricas en SQLite o PostgreSQL
   - Analizar historial de sesiones

4. **Alertas automáticas**
   - Notificar si el costo supera un límite
   - Aviso si hay muchos errores

---

## ⚠️ Notas Importantes

- Las métricas se reinician cada vez que **reinicas el servidor**
- Para persistencia, necesitarías una base de datos
- Los precios son **estimaciones** - verifica con OpenAI
- El tiempo de respuesta incluye tiempo de red

---

## 📞 Support

Si necesitas:
- Cambiar precios → Edita `PRICING` en `app.py`
- Agregar nuevas métricas → Modifica `record_*_metrics()` en `app.py`
- Personalizar el dashboard → Edita `MetricsDashboard.jsx`
