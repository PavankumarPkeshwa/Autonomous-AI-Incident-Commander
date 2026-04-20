import '../styles/IncidentList.css'

function IncidentList({ incidents, selectedId, onSelect }) {
  if (incidents.length === 0) {
    return (
      <div className="incident-list-container">
        <h2 className="list-title">Active Incidents</h2>
        <div className="empty-list">
          <p>No incidents yet</p>
          <small>Create one to get started</small>
        </div>
      </div>
    )
  }

  return (
    <div className="incident-list-container">
      <h2 className="list-title">
        <span>Active Incidents</span>
        <span className="count">{incidents.length}</span>
      </h2>
      <div className="incident-list">
        {incidents.map((incident) => (
          <div
            key={incident.incident_id}
            className={`incident-item ${selectedId === incident.incident_id ? 'active' : ''}`}
            onClick={() => onSelect(incident.incident_id)}
          >
            <div className="incident-header">
              <span className="incident-id">#{incident.incident_id}</span>
              <span className={`severity-badge ${incident.severity}`}>
                {incident.severity.toUpperCase()}
              </span>
            </div>
            <div className="incident-status">{incident.status || 'Analyzing...'}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default IncidentList
