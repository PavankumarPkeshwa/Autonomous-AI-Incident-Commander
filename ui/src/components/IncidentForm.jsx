import { useState } from 'react'
import '../styles/IncidentForm.css'

const API_URL = 'http://localhost:8000'

function IncidentForm({ onIncidentCreated, loading }) {
  const [alertMessage, setAlertMessage] = useState(
    'CRITICAL: Checkout service experiencing high error rate (12.5%) and elevated P99 latency (5234ms). Payment processing degraded. Database connection pool near exhaustion (98/100).'
  )
  const [severity, setSeverity] = useState('critical')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const response = await fetch(`${API_URL}/incidents/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          alert_message: alertMessage,
          severity: severity
        })
      })

      const data = await response.json()
      const newIncidentId = data.incident_id

      if (onIncidentCreated) {
        onIncidentCreated(newIncidentId)
      }

      setAlertMessage('')
      setSeverity('critical')
    } catch (error) {
      alert('Error creating incident: ' + error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="incident-form-container">
      <h2 className="form-title">Create Alert</h2>
      <form onSubmit={handleSubmit} className="incident-form">
        <div className="form-group">
          <label htmlFor="alert-message">Alert Message</label>
          <textarea
            id="alert-message"
            value={alertMessage}
            onChange={(e) => setAlertMessage(e.target.value)}
            placeholder="Describe the incident..."
            disabled={isSubmitting}
            className="form-textarea"
          />
        </div>

        <div className="form-group">
          <label htmlFor="severity">Severity</label>
          <select
            id="severity"
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            disabled={isSubmitting}
            className="form-select"
          >
            <option value="critical">🔴 Critical</option>
            <option value="high">🟠 High</option>
            <option value="medium">🟡 Medium</option>
            <option value="low">🟢 Low</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="submit-button"
        >
          {isSubmitting ? (
            <>
              <span className="spinner-small"></span>
              Creating...
            </>
          ) : (
            <>
              <span className="button-icon">⚡</span>
              Trigger Incident
            </>
          )}
        </button>
      </form>
    </div>
  )
}

export default IncidentForm
