import '../styles/Header.css'

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-section">
          <div className="logo">🚨</div>
          <div>
            <h1 className="title">Autonomous Incident Commander</h1>
            <p className="subtitle">AI-Powered Incident Response Platform</p>
          </div>
        </div>
        <div className="status-indicator">
          <div className="status-dot online"></div>
          <span>System Online</span>
        </div>
      </div>
    </header>
  )
}

export default Header
