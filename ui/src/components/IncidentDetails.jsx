import '../styles/IncidentDetails.css'

function IncidentDetails({ incident }) {
  return (
    <div className="incident-details">
      <div className="details-header">
        <div>
          <h2>Incident #{incident.incident_id}</h2>
          <p className="incident-timestamp">{new Date(incident.timestamp).toLocaleString()}</p>
        </div>
        <div className={`status-badge ${incident.status === 'RESOLVED' ? 'resolved' : incident.status === 'FAILED' ? 'failed' : 'processing'}`}>
          {incident.status}
        </div>
      </div>

      <div className="details-grid">
        {/* Commander Analysis */}
        {incident.commander_analysis && (
          <section className="detail-section">
            <h3 className="section-title">
              <span className="section-icon">🎯</span>
              Commander Analysis
            </h3>
            <p className="section-content">{incident.commander_analysis}</p>
          </section>
        )}

        {/* Logs Findings */}
        {incident.logs_findings && incident.logs_findings.length > 0 && (
          <section className="detail-section">
            <h3 className="section-title">
              <span className="section-icon">📋</span>
              Log Findings
            </h3>
            <ul className="findings-list">
              {incident.logs_findings.map((finding, i) => (
                <li key={i}>{finding}</li>
              ))}
            </ul>
          </section>
        )}

        {/* Metrics Findings */}
        {incident.metrics_findings && incident.metrics_findings.length > 0 && (
          <section className="detail-section">
            <h3 className="section-title">
              <span className="section-icon">📊</span>
              Metrics Analysis
            </h3>
            <ul className="findings-list">
              {incident.metrics_findings.map((finding, i) => (
                <li key={i}>{finding}</li>
              ))}
            </ul>
          </section>
        )}

        {/* Deploy Findings */}
        {incident.deploy_findings && incident.deploy_findings.length > 0 && (
          <section className="detail-section">
            <h3 className="section-title">
              <span className="section-icon">🚀</span>
              Deployment Correlation
            </h3>
            <ul className="findings-list">
              {incident.deploy_findings.map((finding, i) => (
                <li key={i}>{finding}</li>
              ))}
            </ul>
          </section>
        )}

        {/* Resolver Suggestions */}
        {incident.resolver_suggestions && incident.resolver_suggestions.length > 0 && (
          <section className="detail-section highlight">
            <h3 className="section-title">
              <span className="section-icon">💡</span>
              Resolution Recommendations
            </h3>
            <ul className="findings-list">
              {incident.resolver_suggestions.map((suggestion, i) => (
                <li key={i}>{suggestion}</li>
              ))}
            </ul>
          </section>
        )}

        {/* Executed Actions */}
        {incident.executed_actions && incident.executed_actions.length > 0 && (
          <section className="detail-section success">
            <h3 className="section-title">
              <span className="section-icon">✅</span>
              Executed Actions
            </h3>
            <div className="actions-content">
              {incident.executed_actions.map((action, i) => (
                <pre key={i} className="action-log">{action}</pre>
              ))}
            </div>
          </section>
        )}

        {/* Root Cause */}
        {incident.root_cause && (
          <section className="detail-section root-cause">
            <h3 className="section-title">
              <span className="section-icon">🔍</span>
              Root Cause
            </h3>
            <p className="section-content">{incident.root_cause}</p>
          </section>
        )}
      </div>

      {incident.status === 'PROCESSING' && (
        <div className="processing-indicator">
          <span className="spinner-large"></span>
          <p>Analyzing incident...</p>
        </div>
      )}
    </div>
  )
}

export default IncidentDetails
