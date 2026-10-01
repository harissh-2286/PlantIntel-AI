import { BrowserRouter, Routes, Route } from "react-router-dom"
import { useState, useEffect } from "react"
import Sidebar from "./components/Sidebar"
import Home from "./pages/Home"
import Analyze from "./pages/Analyze"
import Results from "./pages/Results"
import Explainability from "./pages/Explainability"
import Research from "./pages/Research"
import History from "./pages/History"
import AnalysisDetail from "./pages/AnalysisDetail"
import PlantCare from "./pages/PlantCare"
import About from "./pages/About"
import Guidance from "./pages/Guidance"
import Monitoring from "./pages/Monitoring"

function App() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')

  useEffect(() => {
    const savedTheme = localStorage.getItem('plantintel-theme') as 'dark' | 'light' | null
    if (savedTheme) {
      setTheme(savedTheme)
    }
  }, [])

  useEffect(() => {
    localStorage.setItem('plantintel-theme', theme)
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [theme])

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark')
  }

  return (
    <BrowserRouter>
      <div className={`flex min-h-screen ${theme === 'dark' ? 'dark bg-[#1a1f24] text-gray-100' : 'bg-gray-50 text-gray-900'}`}>
        <Sidebar theme={theme} toggleTheme={toggleTheme} />
        <main className="flex-1 overflow-y-auto lg:pl-64">
          <div className="container mx-auto p-4 lg:p-8 max-w-6xl">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/analyze" element={<Analyze />} />
              <Route path="/results" element={<Results />} />
              <Route path="/explainability" element={<Explainability />} />
              <Route path="/research" element={<Research />} />
              <Route path="/history" element={<History />} />
              <Route path="/analysis/:analysis_id" element={<AnalysisDetail />} />
              <Route path="/plant-care" element={<PlantCare />} />
              <Route path="/guidance/:analysis_id" element={<Guidance />} />
              <Route path="/monitoring" element={<Monitoring />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
