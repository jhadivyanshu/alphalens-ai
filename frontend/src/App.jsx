import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/home'
import Company from './pages/company'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/company/:symbol" element={<Company />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App