import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import Home from './Home.jsx'

const currentPath = window.location.pathname.replace(/\/+$/, '') || '/'
const page = currentPath === '/workspace' ? <App /> : <Home />

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {page}
  </StrictMode>,
)
