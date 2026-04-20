# Autonomous Incident Commander UI

Modern React web interface for the Autonomous Incident Commander system.

## 📁 Project Structure

```
ui/
├── src/
│   ├── components/           # Reusable React components
│   │   ├── Header.jsx        # Navigation header with branding
│   │   ├── IncidentForm.jsx  # Form to create new incidents
│   │   ├── IncidentList.jsx  # List of active incidents
│   │   └── IncidentDetails.jsx # Detailed incident analysis view
│   │
│   ├── styles/              # CSS stylesheets (one per component + global)
│   │   ├── index.css        # Global styles & CSS variables
│   │   ├── App.css          # Main app layout
│   │   ├── Header.css       # Header component styles
│   │   ├── IncidentForm.css # Form component styles
│   │   ├── IncidentList.css # List component styles
│   │   └── IncidentDetails.css # Details component styles
│   │
│   ├── App.jsx              # Main app component
│   └── main.jsx             # Entry point
│
├── index.html               # HTML template
├── vite.config.js           # Vite configuration
├── package.json             # Dependencies & scripts
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🎨 Component Architecture

```
App (state management)
├── Header (branding & status)
├── Sidebar
│   ├── IncidentForm (create new incidents)
│   └── IncidentList (view active incidents)
└── MainContent
    └── IncidentDetails (view selected incident)
```

### Components

| Component | Purpose | Props |
|-----------|---------|-------|
| **Header** | Top navigation with branding | - |
| **IncidentForm** | Create new incidents | `onIncidentCreated`, `loading` |
| **IncidentList** | Display active incidents | `incidents`, `selectedId`, `onSelect` |
| **IncidentDetails** | Show detailed analysis | `incident` |

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ (or use `nvm`)
- npm or yarn

### Installation

```bash
cd ui
npm install
```

### Development

Run the dev server with hot reload:

```bash
npm run dev
```

Opens on `http://localhost:5173`

The Vite dev server proxies API calls to `http://localhost:8000`.

### Build for Production

```bash
npm run build
```

Creates optimized build in `dist/` folder.

### Preview Production Build

```bash
npm run preview
```

## 🎨 Styling System

### CSS Variables (in styles/index.css)

```css
/* Colors */
--primary-color: #667eea
--success-color: #10b981
--warning-color: #f59e0b
--error-color: #ef4444

/* Spacing */
--spacing-sm: 1rem
--spacing-md: 1.5rem
--spacing-lg: 2rem

/* Shadows */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1)

/* Transitions */
--transition-normal: 300ms ease-in-out
```

### Modifying Styles

1. **Global styles** → Edit `styles/index.css`
2. **Component styles** → Edit component-specific CSS file
3. **Color scheme** → Change CSS variables in `index.css`

## 📱 Responsive Design

- **Desktop** (1024px+): Full 2-column layout
- **Tablet** (768px-1024px): Single column layout
- **Mobile** (<768px): Optimized for small screens

## 🔌 API Integration

The app communicates with the backend API at `http://localhost:8000`:

```javascript
// Create incident
POST /incidents/trigger
Body: { alert_message: string, severity: string }

// Get all incidents
GET /incidents

// Get incident details
GET /incidents/{incident_id}
```

## 📊 Data Flow

```
User Input (Form)
       ↓
Create Incident (API POST)
       ↓
Incident Stored in State
       ↓
Auto-Polling Every 1s
       ↓
Update IncidentDetails Component
       ↓
Render Analysis Results
```

## ✨ Features

✅ Create new incident alerts
✅ Real-time incident polling
✅ Multi-source analysis display
✅ Root cause identification
✅ Remediation recommendations
✅ Beautiful modern UI
✅ Responsive design
✅ Dark/Light mode ready (CSS variables)

## 🛠️ Adding New Components

1. Create file in `src/components/YourComponent.jsx`:
```jsx
import '../styles/YourComponent.css'

function YourComponent({ prop1, prop2 }) {
  return (
    <div className="your-component">
      {/* Component content */}
    </div>
  )
}

export default YourComponent
```

2. Create styles in `src/styles/YourComponent.css`

3. Import and use in `App.jsx`:
```jsx
import YourComponent from './components/YourComponent'

// In App component:
<YourComponent prop1={value1} prop2={value2} />
```

## 🎯 Future Enhancements

- [ ] Dark mode toggle
- [ ] Real-time WebSocket updates (instead of polling)
- [ ] Incident history/archival
- [ ] Export RCA reports as PDF
- [ ] User authentication
- [ ] Incident filtering & search
- [ ] Performance metrics dashboard
- [ ] Automated alerts/notifications

## 📚 Tech Stack

- **React 18**: UI library
- **Vite 4**: Build tool
- **CSS3**: Styling with variables
- **JavaScript (ES6+)**: Core language

## 🤝 Contributing

To modify the UI:

1. Edit component files in `src/components/`
2. Update styles in `src/styles/`
3. Run `npm run dev` to test
4. Run `npm run build` for production

## 📄 License

Part of the Autonomous Incident Commander project.
