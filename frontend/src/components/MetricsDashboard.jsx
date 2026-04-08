import { useState, useEffect } from "react";
import "../Styles/metrics.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

function MetricsDashboard({ onClose }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchMetrics = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/metrics`);
      if (res.ok) {
        const data = await res.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error("Error fetching metrics:", error);
    } finally {
      setLoading(false);
    }
  };

  const resetMetrics = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/metrics/reset`, {
        method: "POST"
      });
      if (res.ok) {
        setMetrics({
          summary: {
            total_messages: 0,
            total_cost: 0,
            total_errors: 0,
            session_duration_seconds: 0
          },
          models: {}
        });
      }
    } catch (error) {
      console.error("Error resetting metrics:", error);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchMetrics();
    }, 3000); // Actualizar cada 3 segundos

    return () => clearInterval(interval);
  }, [autoRefresh]);

  if (loading || !metrics) {
    return <div className="metrics-loading">Cargando métricas...</div>;
  }

  const { summary, models } = metrics;

  return (
    <div className="metrics-dashboard">
      <div className="metrics-header">
        <h2>Panel de metricas</h2>
        <div className="metrics-controls">
          {onClose && (
            <button onClick={onClose} className="btn-close-metrics">
              Cerrar
            </button>
          )}
          <label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-actualizar
          </label>
          <button onClick={fetchMetrics} className="btn-refresh">
            Actualizar
          </button>
          <button onClick={resetMetrics} className="btn-reset">
            Reiniciar
          </button>
        </div>
      </div>

      {/* Resumen general */}
      <div className="metrics-summary">
        <div className="summary-card">
          <div className="summary-label">Mensajes Totales</div>
          <div className="summary-value">{summary.total_messages}</div>
        </div>
        <div className="summary-card">
          <div className="summary-label">Costo Total</div>
          <div className="summary-value">${summary.total_cost.toFixed(4)}</div>
        </div>
        <div className="summary-card">
          <div className="summary-label">Errores</div>
          <div className="summary-value error">{summary.total_errors}</div>
        </div>
        <div className="summary-card">
          <div className="summary-label">Duración Sesión</div>
          <div className="summary-value">{summary.session_duration_seconds}s</div>
        </div>
      </div>

      {/* Métricas por modelo */}
      <div className="metrics-models">
        <h3>Uso por Modelo</h3>
        <div className="models-grid">
          {Object.entries(models).length > 0 ? (
            Object.entries(models).map(([modelName, modelData]) => (
              <div key={modelName} className="model-card">
                <div className="model-name">
                  {modelName.includes("tutor") || modelName.startsWith("ft:")
                    ? "Chat"
                    : modelName.includes("transcribe") || modelName.includes("whisper")
                    ? "Speech-to-Text"
                    : "Text-to-Speech"}
                </div>

                <div className="model-stat">
                  <span>Llamadas:</span>
                  <strong>{modelData.calls}</strong>
                </div>

                <div className="model-stat">
                  <span>Tiempo promedio:</span>
                  <strong>{modelData.avg_response_time_ms}ms</strong>
                </div>

                <div className="model-stat">
                  <span>Tiempo total:</span>
                  <strong>{modelData.total_time_seconds}s</strong>
                </div>

                <div className="model-stat">
                  <span>Costo:</span>
                  <strong>${modelData.total_cost.toFixed(4)}</strong>
                </div>

                {/* Mostrar tokens si existen */}
                {modelData.total_tokens !== undefined && (
                  <>
                    <div className="model-stat">
                      <span>Tokens entrada:</span>
                      <strong>{modelData.tokens_input}</strong>
                    </div>
                    <div className="model-stat">
                      <span>Tokens salida:</span>
                      <strong>{modelData.tokens_output}</strong>
                    </div>
                    <div className="model-stat">
                      <span>Total tokens:</span>
                      <strong>{modelData.total_tokens}</strong>
                    </div>
                  </>
                )}

                {modelData.errors > 0 && (
                  <div className="model-stat error">
                    <span>Errores:</span>
                    <strong>{modelData.errors}</strong>
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="no-data">No hay datos de modelos aún.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default MetricsDashboard;
