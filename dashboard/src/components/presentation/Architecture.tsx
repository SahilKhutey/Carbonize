import { useReveal } from '../../hooks/useReveal';

export default function Architecture() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="architecture" className="section" ref={ref}>
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="section-eyebrow">Reference Architecture</span>
          <h2 className="section-title">Production-ready from day one</h2>
          <p className="section-subtitle">
            Helm chart deployment, SOC 2 Type II in progress, multi-AZ HA, 99.9% uptime SLA.
          </p>
        </div>

        <div className={`arch-diagram reveal ${isVisible ? 'visible' : ''}`}>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 460" className="arch-svg">
            {/* Layer labels */}
            <text x="500" y="30" textAnchor="middle" fontSize="11" fontWeight="600" fill="#10b981">EDGE</text>
            <text x="500" y="160" textAnchor="middle" fontSize="11" fontWeight="600" fill="#10b981">STREAM PROCESSING</text>
            <text x="500" y="280" textAnchor="middle" fontSize="11" fontWeight="600" fill="#10b981">ML / AI</text>
            <text x="500" y="455" textAnchor="middle" fontSize="11" fontWeight="600" fill="#fbbf24">STORAGE</text>

            {/* Edge */}
            <rect className="critical" x="20" y="180" width="120" height="80" rx="8" />
            <text x="80" y="215" textAnchor="middle" fill="white" fontWeight="600">Edge Gateway</text>
            <text x="80" y="240" textAnchor="middle" fontSize="10">MQTT/OPC-UA</text>

            {/* Kafka */}
            <rect className="critical" x="180" y="180" width="130" height="80" rx="8" />
            <text x="245" y="215" textAnchor="middle" fill="white" fontWeight="600">Apache Kafka</text>
            <text x="245" y="240" textAnchor="middle" fontSize="10">3 brokers, 12 partitions</text>

            {/* Flink */}
            <rect className="critical" x="350" y="180" width="130" height="80" rx="8" />
            <text x="415" y="215" textAnchor="middle" fill="white" fontWeight="600">Apache Flink</text>
            <text x="415" y="240" textAnchor="middle" fontSize="10">Windowed aggregation</text>

            {/* ML Inference */}
            <rect className="critical" x="520" y="60" width="130" height="80" rx="8" />
            <text x="585" y="95" textAnchor="middle" fill="white" fontWeight="600">ML Inference</text>
            <text x="585" y="120" textAnchor="middle" fontSize="10">YOLO, Anomaly, GPT</text>

            {/* ML Training */}
            <rect className="critical" x="520" y="180" width="130" height="80" rx="8" />
            <text x="585" y="215" textAnchor="middle" fill="white" fontWeight="600">ML Training</text>
            <text x="585" y="240" textAnchor="middle" fontSize="10">Celery + GPU</text>

            {/* MLflow */}
            <rect className="critical" x="520" y="300" width="130" height="80" rx="8" />
            <text x="585" y="335" textAnchor="middle" fill="white" fontWeight="600">MLflow</text>
            <text x="585" y="360" textAnchor="middle" fontSize="10">Model Registry</text>

            {/* WebSocket */}
            <rect className="critical" x="690" y="60" width="120" height="80" rx="8" />
            <text x="750" y="95" textAnchor="middle" fill="white" fontWeight="600">WebSocket</text>
            <text x="750" y="120" textAnchor="middle" fontSize="10">10k+ clients</text>

            {/* FastAPI */}
            <rect className="critical" x="690" y="180" width="120" height="80" rx="8" />
            <text x="750" y="215" textAnchor="middle" fill="white" fontWeight="600">FastAPI</text>
            <text x="750" y="240" textAnchor="middle" fontSize="10">REST + WebSocket</text>

            {/* Frontend */}
            <rect className="critical" x="850" y="180" width="130" height="80" rx="8" />
            <text x="915" y="215" textAnchor="middle" fill="white" fontWeight="600">React Dashboard</text>
            <text x="915" y="240" textAnchor="middle" fontSize="10">Operator + Demo UI</text>

            {/* PostgreSQL */}
            <rect className="data-store" x="180" y="350" width="130" height="80" rx="8" />
            <text x="245" y="385" textAnchor="middle" fontWeight="600">PostgreSQL</text>
            <text x="245" y="410" textAnchor="middle" fontSize="10">Primary + Replica</text>

            {/* InfluxDB */}
            <rect className="data-store" x="350" y="350" width="130" height="80" rx="8" />
            <text x="415" y="385" textAnchor="middle" fontWeight="600">InfluxDB</text>
            <text x="415" y="410" textAnchor="middle" fontSize="10">Time-series</text>

            {/* Redis */}
            <rect className="data-store" x="520" y="350" width="130" height="80" rx="8" />
            <text x="585" y="385" textAnchor="middle" fontWeight="600">Redis</text>
            <text x="585" y="410" textAnchor="middle" fontSize="10">Cache + Queue</text>

            {/* S3 */}
            <rect className="data-store" x="690" y="350" width="130" height="80" rx="8" />
            <text x="755" y="385" textAnchor="middle" fontWeight="600">S3 / MinIO</text>
            <text x="755" y="410" textAnchor="middle" fontSize="10">Models + Logs</text>

            {/* Monitoring */}
            <rect className="box" x="850" y="350" width="130" height="80" rx="8" />
            <text x="915" y="385" textAnchor="middle" fill="white" fontWeight="600">Prometheus</text>
            <text x="915" y="410" textAnchor="middle" fontSize="10">+ Grafana</text>

            {/* Connection lines */}
            <path className="line" d="M 140 220 L 180 220" />
            <path className="line" d="M 310 220 L 350 220" />
            <path className="line" d="M 480 220 L 520 100" />
            <path className="line" d="M 480 220 L 520 220" />
            <path className="line" d="M 480 220 L 520 340" />
            <path className="line" d="M 650 100 L 690 100" />
            <path className="line" d="M 650 220 L 690 220" />
            <path className="line" d="M 810 100 L 850 220" />
            <path className="line" d="M 810 220 L 850 220" />

            {/* Data lines (from services to storage) */}
            <path className="data-line" d="M 245 260 L 245 350" />
            <path className="data-line" d="M 415 260 L 415 350" />
            <path className="data-line" d="M 585 260 L 585 350" />
            <path className="data-line" d="M 755 260 L 755 350" />
            <path className="data-line" d="M 915 260 L 915 350" />
          </svg>
        </div>
      </div>
    </section>
  );
}
