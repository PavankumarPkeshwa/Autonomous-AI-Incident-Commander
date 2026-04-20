# Quick Setup & Run Guide

Complete instructions for running the Autonomous Incident Commander (Backend + Frontend)

## 📋 Prerequisites

- **Python 3.10+**
- **Node.js 16+** (for UI)
- **npm** or **yarn**

## 🚀 Quick Start (3 Steps)

### 1️⃣ Backend Setup

```bash
# Navigate to project root
cd autonomous_incident_commander

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Configure Groq API Key
# Edit .env file:
# GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 2️⃣ Frontend Setup

```bash
# Navigate to UI folder
cd ui

# Install Node dependencies
npm install
```

### 3️⃣ Run Both Services

**Terminal 1 - Start Backend API:**
```bash
cd autonomous_incident_commander
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Start Frontend Dev Server:**
```bash
cd autonomous_incident_commander/ui
npm run dev
```

Expected output:
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

Then open browser: **http://localhost:5173**

---

## 🎯 How to Use the System

### Creating an Incident

1. Open UI dashboard at `http://localhost:5173`
2. Fill in the alert message (or use default)
3. Select severity level
4. Click "Trigger Incident" button
5. Watch real-time analysis on the right panel

### Monitoring Incident Resolution

- **Status**: Shows PROCESSING → RESOLVED
- **Analysis**: Updates as each agent completes
- **Timeline**: Scroll through findings from all agents
- **Actions**: See what remediation was executed

---

## 📋 File Locations & What Each Does

| Component | Location | Purpose | Command to Start |
|-----------|----------|---------|-------------------|
| **Backend API** | `api.py` | REST backend + incident workflow | `python -m uvicorn api:app --port 8000` |
| **CLI Demo** | `main.py` | Run full workflow in terminal | `python main.py` |
| **Frontend UI** | `ui/` | React web dashboard | `npm run dev` (in ui folder) |
| **Output Reports** | `output/` | RCA reports & logs | Generated automatically |

---

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                  YOUR LOCAL SYSTEM SETUP                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Terminal 1:                    Terminal 2:                     │
│  ┌──────────────────┐          ┌──────────────────┐             │
│  │  Backend API     │          │  Frontend UI     │             │
│  │  ─────────────   │          │  ─────────────   │             │
│  │ python -m        │◄────────►│  npm run dev     │             │
│  │ uvicorn api:app  │ HTTP     │                  │             │
│  │                  │ (port 8000) │ (port 5173) │             │
│  │ ✅ 0.0.0.0:8000  │          │ ✅ localhost:5173│             │
│  └──────────────────┘          └──────────────────┘             │
│           ▲                              ▲                       │
│           │                              │                       │
│           └──► Browser ◄────────────────┘                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Available Commands

### Backend Commands

```bash
# Run full workflow in CLI (no web UI needed)
python main.py

# Start REST API server
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# View generated reports
cat output/rca_report.md
cat output/chain_of_thought.json
```

### Frontend Commands

```bash
# Development (hot reload)
npm run dev

# Production build
npm run build

# Preview production build locally
npm run preview
```

---

## ❓ Troubleshooting

### Port Already in Use

**Backend port 8000 taken:**
```bash
python -m uvicorn api:app --port 8001
# Then update UI vite.config.js proxy to 8001
```

**Frontend port 5173 taken:**
```bash
cd ui
npm run dev -- --port 5174
```

### Module Not Found (Python)

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Module Not Found (Node)

```bash
# Clear node_modules and reinstall
cd ui
rm -rf node_modules package-lock.json
npm install
```

### API Not Responding

Check if backend is running:
```bash
curl http://localhost:8000/
# Should return: {"service": "Autonomous Incident Commander API", ...}
```

---

## 📊 Project Structure

```
autonomous_incident_commander/
├── main.py                 # CLI entry point
├── api.py                  # REST API server
├── agents/                 # AI agents
├── tools/                  # Agent tools
├── config/                 # Configuration
├── mock_data/              # Test data
├── output/                 # Generated reports
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
│
└── ui/                     # ✨ NEW: React Frontend
    ├── src/
    │   ├── components/     # Reusable components
    │   ├── styles/        # Component-specific CSS
    │   ├── App.jsx        # Main app component
    │   └── main.jsx       # Entry point
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── README.md          # UI-specific docs
```

---

## 🎨 UI Component Structure

The `ui/` folder now contains a professionally organized React project:

- **components/** - Modular, reusable components (Header, Form, List, Details)
- **styles/** - CSS files with modern variables & design system
- **Easy to extend** - Add new components by creating .jsx and .css file pair

See `ui/README.md` for detailed component documentation.

---

## 🚨 Running the Full Example

```bash
# 1. Open Terminal 1 (Backend)
cd ~/Desktop/"Practice Projects"/autonomous_incident_commander
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# 2. Open Terminal 2 (Frontend)
cd ~/Desktop/"Practice Projects"/autonomous_incident_commander/ui
npm run dev

# 3. Open Browser
# -> http://localhost:5173

# 4. Create an Incident
# -> Fill form, click "Trigger Incident"

# 5. Watch It Analyze
# -> See results update in real-time on dashboard
```

---

## 📚 Next Steps

1. **Explore the UI** - Click around, create incidents
2. **Check the code** - Read components, understand architecture
3. **Modify styles** - Edit CSS variables for custom theme
4. **Add components** - Create new React components as needed
5. **Explore backend** - Study agent system and LLM integration

---

## 🎓 Learning Resources

- **Backend**: See `README.md` for multi-agent architecture
- **Frontend**: See `ui/README.md` for component structure
- **React**: https://react.dev
- **Vite**: https://vitejs.dev
- **CSS Variables**: https://developer.mozilla.org/en-US/docs/Web/CSS/--*

---

**Happy incident commanding! 🚀**
