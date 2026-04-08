# Guía Rápida - Sistema de Métricas

## Iniciar el Proyecto

### 1. Backend
```bash
cd backend
python app.py
```
El servidor estará en `http://localhost:5000`

### 2. Frontend
```bash
cd frontend
npm run dev
```

## Usar las Métricas

### En el Chat
1. Abre la aplicación en el navegador
2. Haz clic en el botón **"📊 Mostrar Métricas"** en la esquina superior derecha
3. Envía un mensaje y verás:
   - Los tokens consumidos (entrada/salida)
   - El tiempo de respuesta en ms
   - El costo estimado

### Dashboard de Métricas
Cuando actives las métricas ves:
- **Resumen General**: Total mensajes, costo acumulado, errores, duración
- **Por Modelo**:
  - 🎓 Chat: tokens entrada/salida
  - 🎤 Speech-to-Text: duración y costo por minuto
  - 🔊 Text-to-Speech: costo por caracteres

### API (cURL)
```bash
# Ver todas las métricas
curl http://localhost:5000/metrics

# Reiniciar métricas
curl -X POST http://localhost:5000/metrics/reset
```

## Precios Configurados
- **Chat**: $0.075 por 1M tokens entrada, $0.30 por 1M tokens salida
- **STT**: $0.006 por minuto
- **TTS**: $0.015 por 1,000 caracteres

## Actualizar Precios
Edita `backend/app.py`, sección `PRICING` (línea ~88)

## Notas
- Las métricas se reinician al reiniciar el servidor
- Para persistencia, necesitarías agregar una BD
- El tiempo incluye latencia de red

¡Listo para usar! 🚀
