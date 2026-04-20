import { useState, useEffect } from 'react'
import Header from './components/Header'
import IncidentForm from './components/IncidentForm'
import IncidentList from './components/IncidentList'
import IncidentDetails from './components/IncidentDetails'
import './styles/App.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [incidents, setIncidents] = useState([])
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [incidentDetails, setIncidentDetails] = useState(null)
  const [loading, setLoading] = useState(false)
  const [pollingId, setPollingId] = useState(null)

  const handleIncidentCreated = (newIncidentId) => {
    setSelectedIncident(newIncidentId)
    startPollingIncident(newIncidentId)
  }

  const startPollingIncident = (incidentId) => {
    // Clear existing polling
    if (pollingId) clearInterval(pollingId)

    // Fetch immediately
    fetchIncidentDetails(incidentId)

    // Then poll
    const id = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/incidents/${incidentId}`)
        const data = await response.json()
        setIncidentDetails(data)

        // Stop polling if resolved
        if (data.status === 'RESOLVED' || data.status === 'FAILED') {
          clearInterval(id)
          setPollingId(null)
        }
      } catch (error) {
        console.error('Polling error:', error)
      }
    }, 1000)

    setPollingId(id)
  }

  const fetchIncidentDetails = async (incidentId) => {
    try {
      const response = await fetch(`${API_URL}/incidents/${incidentId}`)
      const data = await response.json()
      setIncidentDetails(data)
    } catch (error) {
      console.error('Error fetching incident details:', error)
    }
  }

  const handleSelectIncident = (incidentId) => {
    setSelectedIncident(incidentId)
    fetchIncidentDetails(incidentId)
  }

  return (
    <div className="app">
      <Header />
      <main className="main-container">
        <div className="content-wrapper">
          <aside className="sidebar">
            <IncidentForm onIncidentCreated={handleIncidentCreated} loading={loading} />
            <IncidentList
              incidents={incidents}
              selectedId={selectedIncident}
              onSelect={handleSelectIncident}
            />
          </aside>
          <section className="main-content">
            {incidentDetails ? (
              <IncidentDetails incident={incidentDetails} />
            ) : selectedIncident ? (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>Loading incident details...</p>
              </div>
            ) : (
              <div className="empty-state">
                <svg className="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M12 6v6l4 2"></path>
                </svg>
                <h3>Select or create an incident</h3>
                <p>Choose an incident from the list or create a new one to get started</p>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  )
}

export default App
