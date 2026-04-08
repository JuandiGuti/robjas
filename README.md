# Proyecto Tutor IA - Programación Avanzada

Aplicación web de tutor virtual para la clase de Programación Avanzada del Ing. Rojas. Combina un frontend en React con un backend en Flask, y usa la API de OpenAI para generar respuestas, transcribir audio y convertir texto a voz. También incluye un panel de métricas separado en modal para revisar uso, tokens, costos y tiempos sin mezclar esa información con el chat.

## Descripción general

La aplicación funciona como un chat educativo. El usuario puede escribir preguntas o grabarlas por micrófono, y el sistema responde únicamente con el contenido cargado en el prompt del curso. Además, puede reproducir la respuesta en audio. Las métricas de uso se consultan en una vista aparte para no ensuciar el chat.

El proyecto está dividido en dos partes:

1. Frontend: interfaz en React + Vite.
2. Backend: API en Flask que conecta con OpenAI y expone los endpoints del chat, la transcripción, la voz y las métricas.

## Tecnologías usadas

### Frontend

- React 19: construye la interfaz del chat por componentes.
- Vite: servidor de desarrollo y build del proyecto.
- `react-markdown`: renderiza la respuesta del bot con formato Markdown.
- `MediaRecorder` y Web Audio API del navegador: capturan audio del micrófono y reproducen la voz generada.
- CSS puro: estilos del chat, modal de métricas, responsividad y animaciones.

### Backend

- Python 3: lenguaje del servidor.
- Flask: crea la API HTTP.
- Flask-CORS: permite que el frontend llame al backend desde otro puerto.
- OpenAI Python SDK: genera respuestas, transcribe audio y produce audio sintetizado.
- `python-dotenv`: carga variables de entorno desde el archivo `.env`.

## Arquitectura del proyecto

El flujo principal es el siguiente:

1. El usuario escribe un mensaje o habla desde el navegador.
2. El frontend envía la consulta al backend en `POST /chat`.
3. El backend carga el prompt del sistema desde `backend/data/system/system_promt.json`.
4. Ese prompt define la personalidad del tutor, las reglas de respuesta y la base de conocimiento del curso.
5. El backend llama a OpenAI con el modelo fine-tuned `ft:gpt-4o-mini-2024-07-18:personal:tutor-robjas:DRueFPtg` para generar la respuesta.
6. La respuesta regresa al frontend como JSON y se muestra en el chat.
7. Si el usuario pulsa el botón de voz, el frontend llama a `POST /tts` y recibe un MP3 para reproducir la respuesta.
8. Si el usuario usa el micrófono, el frontend graba el audio y lo manda a `POST /stt`, donde el backend lo transcribe y devuelve texto.
9. Las métricas se consultan en un modal aparte con `GET /metrics` y se pueden reiniciar con `POST /metrics/reset`.

## Estructura de carpetas

```text
package.json
README.md
backend/
    app.py
    data/
        system/
            system_promt.json
frontend/
    package.json
    vite.config.js
    src/
        App.jsx
        main.jsx
        components/
            ChatContainer.jsx
            ChatInput.jsx
            MessageBubble.jsx
            MetricsDashboard.jsx
        Styles/
            chat.css
            metrics.css
```

## Cómo funciona el backend

El backend vive en [backend/app.py](backend/app.py). Ahí se inicializa Flask, se activa CORS y se crea el cliente de OpenAI con la variable `OPENAI_API_KEY`.

### Carga del prompt

Al iniciar, el backend lee [backend/data/system/system_promt.json](backend/data/system/system_promt.json). Ese archivo contiene:

- Título e identidad del tutor.
- Función principal.
- Reglas estrictas de comportamiento.
- Estrategia pedagógica.
- Tono y estilo.
- Lista de conocimientos permitidos del curso.

Luego, `build_system_prompt()` transforma ese JSON en un prompt de texto listo para enviarse al modelo.

### Endpoint `POST /chat`

Este es el endpoint principal del tutor.

- Entrada: JSON con la forma `{ "message": "..." }`.
- Validación: si no viene mensaje, responde `400`.
- Proceso: concatena el prompt del sistema, el historial de chat y el mensaje nuevo.
- Modelo usado: `ft:gpt-4o-mini-2024-07-18:personal:tutor-robjas:DRueFPtg`.
- Salida: JSON con `{ "response": "..." }` y un bloque de métricas con `tokens_input`, `tokens_output` y `response_time_ms`.

El backend guarda un historial en memoria mientras el servidor sigue corriendo. Eso le permite conservar contexto entre mensajes dentro de la misma sesión.

### Endpoint `POST /tts`

Convierte texto a audio.

- Entrada: JSON con `{ "text": "..." }`.
- Modelo por defecto: `tts-1`.
- Voz por defecto: `onyx`.
- Salida: archivo MP3 en la respuesta HTTP.

### Endpoint `POST /stt`

Convierte voz a texto.

- Entrada: `multipart/form-data` con el archivo `audio`.
- Modelo por defecto: `whisper-1`.
- Idioma por defecto: `es`.
- Salida: JSON con `{ "text": "..." }`.

### Métricas del backend

El backend registra por sesión:

- total de mensajes procesados,
- total de errores,
- costo acumulado,
- tiempo acumulado por modelo,
- llamadas por modelo,
- tokens de entrada, salida y totales para el modelo de chat.

Los endpoints de métricas son:

- `GET /metrics`: devuelve resumen general y detalle por modelo.
- `POST /metrics/reset`: reinicia las métricas de la sesión.

## Cómo funciona el frontend

El frontend arranca desde [frontend/src/main.jsx](frontend/src/main.jsx) y renderiza [frontend/src/App.jsx](frontend/src/App.jsx).

### `App.jsx`

- Mantiene el estado de los mensajes.
- Envía cada pregunta al backend con `fetch(`${API_BASE_URL}/chat`)`.
- Usa `VITE_API_BASE_URL` y, si no existe, toma `http://localhost:5000`.
- Muestra una respuesta de error si la conexión falla.
- Abre un modal independiente para ver las métricas.

### `ChatContainer.jsx`

- Muestra el historial de mensajes.
- Hace scroll automático hacia el último mensaje.
- Enseña un estado inicial cuando el chat todavía está vacío.

### `ChatInput.jsx`

- Permite escribir preguntas manualmente.
- Permite grabar audio con `MediaRecorder`.
- Envía el audio al backend en `POST /stt`.
- Inserta el texto transcrito en el input para que el usuario lo envíe o edite.

### `MessageBubble.jsx`

- Renderiza mensajes del bot con `react-markdown`.
- Incluye el botón para escuchar la respuesta.
- Envía el texto al backend en `POST /tts`.
- Reproduce el audio devuelto por el servidor.

### `MetricsDashboard.jsx`

- Muestra métricas en una vista separada tipo modal.
- Tiene auto-actualización opcional.
- Permite reiniciar las métricas.
- Muestra resumen general y detalle por modelo.

## Conexión entre frontend y backend

La conexión se hace por HTTP usando fetch.

- Frontend -> Backend: `POST /chat`, `POST /tts`, `POST /stt`, `GET /metrics`, `POST /metrics/reset`.
- Backend -> OpenAI: generación de texto, síntesis de voz y transcripción.
- Backend -> Frontend: respuestas JSON o audio MP3.

La variable `VITE_API_BASE_URL` permite cambiar la URL del backend sin modificar el código del frontend. Si no se define, el frontend usa `http://localhost:5000`.

## Variables de entorno

### Backend

Crear un archivo `.env` dentro de `backend/` con, al menos:

```env
OPENAI_API_KEY=tu_clave_aqui
```

Opcionalmente también puedes definir:

```env
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=onyx
OPENAI_STT_MODEL=whisper-1
OPENAI_STT_LANGUAGE=es
```

### Frontend

Si el backend no corre en `http://localhost:5000`, crea un archivo `.env` dentro de `frontend/` con:

```env
VITE_API_BASE_URL=http://localhost:5000
```

## Instalación y ejecución

### 1. Instalar el backend

Desde la carpeta raíz del proyecto:

```bash
cd backend
pip install flask flask-cors openai python-dotenv
```

Si prefieres trabajar con un entorno virtual, actívalo primero y luego instala esas dependencias.

### 2. Ejecutar el backend

```bash
cd backend
python app.py
```

El servidor corre en `http://localhost:5000` con `debug=True`.

### 3. Instalar el frontend

En otra terminal:

```bash
cd frontend
npm install
```

### 4. Ejecutar el frontend

```bash
cd frontend
npm run dev
```

Vite normalmente arranca en `http://localhost:5173`.

## Uso de la aplicación

1. Abre el frontend en el navegador.
2. Escribe una pregunta sobre Programación Avanzada o usa el botón de micrófono.
3. El frontend enviará la consulta al backend.
4. El backend generará una respuesta basada en el prompt del curso.
5. Si quieres escuchar la respuesta, usa el botón de audio en el mensaje del bot.
6. Si quieres revisar uso, abre el panel de métricas desde el botón correspondiente.

## Regla de contenido del tutor

- El tutor está limitado al conocimiento cargado en `system_promt.json`.
- No debe entregar código fuente completo.
- Debe responder con enfoque pedagógico y en español.
- Si el usuario pregunta algo fuera del curso, debe redirigir o negarse según las reglas del prompt.

## Notas técnicas

- El historial del chat vive en memoria RAM del servidor; al reiniciar el backend se pierde.
- El proyecto usa llamadas separadas para chat, voz y transcripción, lo que simplifica el mantenimiento.
- El backend está preparado para trabajar con audio temporal; después de procesarlo, borra los archivos generados.
- La interfaz del chat está pensada para funcionar tanto en escritorio como en móvil.
- El panel de métricas está separado del chat para evitar mezclar contenido de conversación con datos técnicos.

## Métricas disponibles

El panel de métricas muestra:

- Mensajes totales.
- Costo total.
- Errores.
- Duración de la sesión.
- Llamadas por modelo.
- Tiempo promedio por modelo.
- Tiempo total por modelo.
- Tokens de entrada, salida y totales del modelo de chat.

## Posibles mejoras futuras

- Guardar historial persistente por usuario.
- Agregar autenticación.
- Indexar el contenido del curso por temas para responder con más precisión.
- Mejorar la restricción de temas fuera del contenido del curso.
- Añadir selección de voz y controles de audio más completos.





