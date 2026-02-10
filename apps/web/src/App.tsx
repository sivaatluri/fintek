import { useState, useEffect } from 'react'
import './App.css'

interface ServiceStatus {
  name: string;
  status: string;
  url: string;
}

function App() {
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Placeholder for service health checks
    const mockServices: ServiceStatus[] = [
      { name: 'Gateway', status: 'healthy', url: 'http://localhost:8000' },
      { name: 'Auth', status: 'healthy', url: 'http://localhost:8001' },
      { name: 'Tenant', status: 'healthy', url: 'http://localhost:8002' },
      { name: 'Ingestion', status: 'healthy', url: 'http://localhost:8003' },
      { name: 'Workflows', status: 'healthy', url: 'http://localhost:8004' },
      { name: 'Budgets', status: 'healthy', url: 'http://localhost:8005' },
      { name: 'Query', status: 'healthy', url: 'http://localhost:8006' },
      { name: 'Integrations', status: 'healthy', url: 'http://localhost:8007' },
    ];
    
    setServices(mockServices);
    setLoading(false);
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>🚀 Fintek</h1>
        <p>Multi-Tenant FinOps SaaS Platform</p>
      </header>
      
      <main className="main">
        <section className="section">
          <h2>Platform Overview</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Microservices</h3>
              <p className="stat-value">8</p>
            </div>
            <div className="stat-card">
              <h3>Tech Stack</h3>
              <p className="stat-value">FastAPI + React</p>
            </div>
            <div className="stat-card">
              <h3>Status</h3>
              <p className="stat-value">✅ Running</p>
            </div>
          </div>
        </section>

        <section className="section">
          <h2>Services Status</h2>
          {loading ? (
            <p>Loading services...</p>
          ) : (
            <div className="services-grid">
              {services.map((service) => (
                <div key={service.name} className="service-card">
                  <h3>{service.name}</h3>
                  <p className="service-status">
                    {service.status === 'healthy' ? '✅' : '❌'} {service.status}
                  </p>
                  <a href={`${service.url}/health`} target="_blank" rel="noopener noreferrer" className="service-link">
                    Health Check →
                  </a>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="section">
          <h2>Infrastructure</h2>
          <div className="infra-grid">
            <div className="infra-card">PostgreSQL</div>
            <div className="infra-card">Redis</div>
            <div className="infra-card">Kafka</div>
            <div className="infra-card">Trino</div>
            <div className="infra-card">MinIO</div>
          </div>
        </section>

        <section className="section">
          <h2>Features</h2>
          <ul className="features-list">
            <li>✅ Multi-tenant architecture</li>
            <li>✅ Cost ingestion & analytics</li>
            <li>✅ Budget management & alerts</li>
            <li>✅ Cloud provider integrations (AWS, Azure, GCP)</li>
            <li>✅ Workflow orchestration</li>
            <li>✅ Query service with Trino</li>
            <li>✅ RBAC placeholders</li>
            <li>✅ Health check endpoints</li>
          </ul>
        </section>
      </main>
    </div>
  )
}

export default App
