import json
import os
import tempfile
import time
from pathlib import Path
from threading import Lock
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# Inicializar cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuración de rutas de archivos
system_prompt_path = Path(__file__).resolve().parent / "data" / "system" / "system_promt.json"
with system_prompt_path.open(encoding="utf-8") as system_prompt_file:
    system_prompt_data = json.load(system_prompt_file)

history_lock = Lock()

def build_system_prompt(prompt_data: dict) -> str:
    if "system_prompt" in prompt_data and isinstance(prompt_data["system_prompt"], str):
        return prompt_data["system_prompt"]

    sections = [
        prompt_data.get("title", ""),
        prompt_data.get("context", ""),
        "TU FUNCION PRINCIPAL",
        prompt_data.get("main_function", ""),
        "REGLAS DE CONTENIDO Y SEGURIDAD (CRITICO)",
    ]

    rules = prompt_data.get("rules", [])
    sections.extend([f"{idx + 1}. {rule}" for idx, rule in enumerate(rules)])
    
    sections.extend([
        "",
        "RESPUESTA OBLIGATORIA CUANDO PIDEN CODIGO",
        prompt_data.get("code_request_response", ""),
        "",
        "RESPUESTA OBLIGATORIA PARA TEMAS FUERA DE CONTENIDO",
        prompt_data.get("out_of_scope_response", ""),
        "",
        "ESTRATEGIA PEDAGOGICA",
    ])
    
    pedagogy = prompt_data.get("pedagogical_strategy", [])
    sections.extend([f"- {item}" for item in pedagogy])
    
    tone = prompt_data.get("tone_and_style", [])
    sections.extend(["", "TONO Y ESTILO"])
    sections.extend([f"- {item}" for item in tone])
    
    knowledge = prompt_data.get("knowledge", [])
    sections.extend(["", "---", "CONOCIMIENTO ESPECÍFICO DEL CURSO", ""])
    sections.extend([f"- {item}" for item in knowledge])

    return "\n".join([line for line in sections if line is not None])

system_promt = build_system_prompt(system_prompt_data)
chat_history: list[dict] = []

# ============================================
# SISTEMA DE MÉTRICAS (CORREGIDO)
# ============================================

# Precios reales por unidad de medida
PRICING = {
    # Los modelos Fine-Tuning (ft) suelen costar el doble que el base
    "ft:gpt-4o-mini-2024-07-18:personal:tutor-robjas:DRueFPtg": {
        "input": 0.30 / 1_000_000,   # $0.30 por 1M tokens
        "output": 1.20 / 1_000_000   # $1.20 por 1M tokens
    },
    "whisper-1": {
        "type": "audio",
        "price_per_minute": 0.006    # $0.006 por minuto
    },
    "tts-1": {
        "type": "tts",
        "price_per_thousand_chars": 0.015 / 1000 # $0.015 por cada 1,000 caracteres
    }
}

metrics_lock = Lock()
session_metrics = {
    "total_messages": 0,
    "total_cost": 0.0,
    "models": {},
    "errors": 0,
    "start_time": time.time()
}

def initialize_model_metrics(model_name: str, include_tokens: bool = False):
    if model_name not in session_metrics["models"]:
        base_metrics = {
            "calls": 0,
            "total_cost": 0.0,
            "total_time": 0.0,
            "response_times": [],
            "errors": 0
        }

        if include_tokens:
            base_metrics.update({
                "tokens_input": 0,
                "tokens_output": 0,
                "total_tokens": 0
            })

        session_metrics["models"][model_name] = base_metrics

def record_chat_metrics(model_name: str, usage, response_time: float):
    with metrics_lock:
        initialize_model_metrics(model_name, include_tokens=True)
        metrics = session_metrics["models"][model_name]
        
        metrics["calls"] += 1
        metrics["tokens_input"] += usage.prompt_tokens
        metrics["tokens_output"] += usage.completion_tokens
        metrics["total_tokens"] += usage.total_tokens
        metrics["response_times"].append(response_time)
        metrics["total_time"] += response_time
        
        if model_name in PRICING:
            p = PRICING[model_name]
            cost = (usage.prompt_tokens * p["input"]) + (usage.completion_tokens * p["output"])
            metrics["total_cost"] += cost
            session_metrics["total_cost"] += cost
        
        session_metrics["total_messages"] += 1

def record_audio_metrics(model_name: str, duration_seconds: float):
    with metrics_lock:
        initialize_model_metrics(model_name, include_tokens=False)
        metrics = session_metrics["models"][model_name]
        metrics["calls"] += 1
        metrics["total_time"] += duration_seconds
        
        if model_name in PRICING:
            p = PRICING[model_name]
            cost = (duration_seconds / 60) * p["price_per_minute"]
            metrics["total_cost"] += cost
            session_metrics["total_cost"] += cost

def record_tts_metrics(model_name: str, text: str):
    with metrics_lock:
        initialize_model_metrics(model_name, include_tokens=False)
        metrics = session_metrics["models"][model_name]
        metrics["calls"] += 1
        
        if model_name in PRICING:
            p = PRICING[model_name]
            cost = len(text) * p["price_per_thousand_chars"]
            metrics["total_cost"] += cost
            session_metrics["total_cost"] += cost

# ============================================
# RUTAS
# ============================================

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = (data.get("message", "") or "").strip()
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        with history_lock:
            history_snapshot = list(chat_history)

        start_time = time.time()
        model_name = "ft:gpt-4o-mini-2024-07-18:personal:tutor-robjas:DRueFPtg"

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_promt},
                *history_snapshot,
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.5
        )

        response_time = time.time() - start_time
        answer = response.choices[0].message.content

        record_chat_metrics(model_name, response.usage, response_time)

        with history_lock:
            chat_history.append({"role": "user", "content": user_message})
            chat_history.append({"role": "assistant", "content": answer})

        return jsonify({
            "response": answer,
            "metrics": {
                "tokens_input": response.usage.prompt_tokens,
                "tokens_output": response.usage.completion_tokens,
                "response_time_ms": round(response_time * 1000, 2)
            }
        })
    except Exception as e:
        with metrics_lock: session_metrics["errors"] += 1
        return jsonify({"error": str(e)}), 500

@app.route('/tts', methods=['POST'])
def tts():
    data = request.json or {}
    text = (data.get("text", "") or "").strip()
    if not text: return jsonify({"error": "No text provided"}), 400

    tts_model = "tts-1"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name

        with client.audio.speech.with_streaming_response.create(
            model=tts_model,
            voice="onyx",
            input=text
        ) as tts_response:
            tts_response.stream_to_file(temp_path)

        record_tts_metrics(tts_model, text)

        with open(temp_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        return Response(audio_bytes, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if temp_path and os.path.exists(temp_path): os.remove(temp_path)

@app.route('/stt', methods=['POST'])
def stt():
    audio_file = request.files.get("audio")
    if not audio_file: return jsonify({"error": "No audio file"}), 400

    stt_model = "whisper-1"
    temp_audio_path = None
    try:
        start_time = time.time()
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_audio_file:
            temp_audio_file.write(audio_file.read())
            temp_audio_path = temp_audio_file.name

        with open(temp_audio_path, "rb") as audio_stream:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_stream,
                language="es"
            )

        response_time = time.time() - start_time
        record_audio_metrics(stt_model, response_time)
        return jsonify({"text": transcription.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path): os.remove(temp_audio_path)

@app.route('/metrics', methods=['GET'])
def get_metrics():
    with metrics_lock:
        metrics_response = {
            "summary": {
                "total_messages": session_metrics["total_messages"],
                "total_cost": round(session_metrics["total_cost"], 6),
                "total_errors": session_metrics["errors"],
                "session_duration_seconds": round(time.time() - session_metrics["start_time"], 2)
            },
            "models": {}
        }
        for name, data in session_metrics["models"].items():
            avg_time = (data["total_time"] / data["calls"] if data["calls"] > 0 else 0)
            metrics_response["models"][name] = {
                "calls": data["calls"],
                "total_cost": round(data["total_cost"], 6),
                "avg_response_time_ms": round(avg_time * 1000, 2),
                "total_time_seconds": round(data["total_time"], 2),
                "errors": data["errors"]
            }

            if all(k in data for k in ("tokens_input", "tokens_output", "total_tokens")):
                metrics_response["models"][name].update({
                    "tokens_input": data["tokens_input"],
                    "tokens_output": data["tokens_output"],
                    "total_tokens": data["total_tokens"]
                })
        return jsonify(metrics_response)

@app.route('/metrics/reset', methods=['POST'])
def reset_metrics():
    with metrics_lock:
        session_metrics.update({
            "total_messages": 0, "total_cost": 0.0, "models": {}, "errors": 0, "start_time": time.time()
        })
    return jsonify({"message": "Metrics reset successfully"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)