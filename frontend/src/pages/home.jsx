import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { searchCompanies } from '../services/api'

export default function Home() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSearch = async (e) => {
    const value = e.target.value
    setQuery(value)
    if (value.length < 1) {
      setResults([])
      return
    }
    setLoading(true)
    try {
      const res = await searchCompanies(value)
      setResults(res.data.data)
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center px-4">
      
      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="text-5xl font-bold text-white mb-3">
           📊 Alpha<span className="text-green-400">Lens</span> AI
        </h1>
        <p className="text-gray-400 text-lg">
          AI Equity Research Terminal for Indian Markets
        </p>
      </div>

      {/* Search */}
      <div className="w-full max-w-2xl relative">
        <input
          type="text"
          value={query}
          onChange={handleSearch}
          placeholder="Search any NSE company... TCS, KPIT, Infosys"
          className="w-full bg-gray-800 border border-gray-700 rounded-xl px-6 py-4 text-white text-lg placeholder-gray-500 focus:outline-none focus:border-green-400"
        />

        {/* Results dropdown */}
        {results.length > 0 && (
          <div className="absolute top-16 left-0 right-0 bg-gray-800 border border-gray-700 rounded-xl overflow-hidden z-10">
            {results.map((company) => (
              <div
                key={company.symbol}
                onClick={() => navigate(`/company/${company.symbol}`)}
                className="px-6 py-4 hover:bg-gray-700 cursor-pointer flex justify-between items-center"
              >
                <div>
                  <div className="font-semibold text-white">{company.symbol}</div>
                  <div className="text-gray-400 text-sm">{company.name}</div>
                </div>
                <div className="text-gray-400 text-sm">{company.sector}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Example queries */}
      <div className="mt-8 text-center">
        <p className="text-gray-500 text-sm mb-3">Try searching for</p>
        <div className="flex gap-3 flex-wrap justify-center">
          {['TCS', 'INFY', 'RELIANCE', 'ICICIBANK', 'SUNPHARMA'].map((s) => (
            <button
              key={s}
              onClick={() => navigate(`/company/${s}`)}
              className="bg-gray-800 border border-gray-700 px-4 py-2 rounded-lg text-gray-300 hover:border-green-400 hover:text-green-400 transition"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

    </div>
  )
}