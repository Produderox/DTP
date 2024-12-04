import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import MapComponent from './MapComponent.jsx'

createRoot(document.getElementById('Map')).render(
  <StrictMode>
    <MapComponent/>
  </StrictMode>,
)
