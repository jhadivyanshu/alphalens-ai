import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCompany, getCompanyScore, getCompanySummary, getCompanyNews, getCompanyFinancials, getCompanyPrices, sendChat, getCompanyChanges } from '../services/api'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function Company() {
  const { symbol } = useParams()
  const navigate = useNavigate()

  const [company, setCompany] = useState(null)
  const [score, setScore] = useState(null)
  const [summary, setSummary] = useState(null)
  const [news, setNews] = useState([])
  const [financials, setFinancials] = useState([])
  const [prices, setPrices] = useState([])
  const [changes, setChanges] = useState(null)
  const [chat, setChat] = useState({ question: '', answer: '', loading: false })
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    fetchData()
  }, [symbol])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [companyRes, scoreRes, newsRes, financialsRes, pricesRes, changesRes] = await Promise.all([
        getCompany(symbol),
        getCompanyScore(symbol),
        getCompanyNews(symbol),
        getCompanyFinancials(symbol),
        getCompanyPrices(symbol),
        getCompanyChanges(symbol)
      ])
      setCompany(companyRes.data.data)
      setScore(scoreRes.data.data)
      setNews(newsRes.data.data)
      setFinancials(financialsRes.data.data)
      setPrices(pricesRes.data.data)
      setChanges(changesRes.data.data)
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const fetchSummary = async () => {
    try {
      const res = await getCompanySummary(symbol)
      setSummary(res.data.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleChat = async () => {
    if (!chat.question) return
    setChat(c => ({ ...c, loading: true }))
    try {
      const res = await sendChat(chat.question, symbol)
      setChat(c => ({ ...c, answer: res.data.data.answer, loading: false }))
    } catch (err) {
      setChat(c => ({ ...c, loading: false }))
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  if (loading) return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
      <div className="text-green-400 text-xl">Loading {symbol}...</div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-950 text-white">

      {/* Navbar */}
      <div className="border-b border-gray-800 px-6 py-4 flex items-center gap-4">
        <button onClick={() => navigate('/')} className="text-green-400 hover:text-green-300">← Back</button>
       <h1 className="text-xl font-bold">📊 Alpha<span className="text-green-400">Lens</span> AI</h1>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">

        {/* Company Header */}
        {company && (
          <div className="flex justify-between items-start mb-8">
            <div>
              <h2 className="text-3xl font-bold">{company.symbol}</h2>
              <p className="text-gray-400 mt-1">{company.name}</p>
              <p className="text-gray-500 text-sm mt-1">{company.sector} · {company.exchange}</p>
            </div>
            <div className="text-right">
              {company.price && (
                <div className="text-3xl font-bold text-white">₹{company.price.current}</div>
              )}
              {score && (
                <div className={`text-2xl font-bold mt-1 ${getScoreColor(score.overall)}`}>
                  Alpha Score: {score.overall}/100
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-4 border-b border-gray-800 mb-8">
          {['overview', 'financials', 'ai summary', 'news', 'chat', 'qoq'].map(tab => (
            <button
              key={tab}
              onClick={() => {
                setActiveTab(tab)
                if (tab === 'ai summary' && !summary) fetchSummary()
              }}
              className={`pb-3 px-2 capitalize text-sm font-medium transition ${
                activeTab === tab
                  ? 'border-b-2 border-green-400 text-green-400'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {score && (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {Object.entries(score.engines).map(([key, data]) => (
                  <div key={key} className="bg-gray-800 rounded-xl p-4 text-center">
                    <div className={`text-2xl font-bold ${getScoreColor(data.score)}`}>{data.score}</div>
                    <div className="text-gray-400 text-sm capitalize mt-1">{key}</div>
                  </div>
                ))}
              </div>
            )}

            {prices.length > 0 && (
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-4">Price History</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={prices.slice(-180)}>
                    <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 10 }} tickFormatter={d => d.slice(5)} />
                    <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} domain={['auto', 'auto']} />
                    <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} />
                    <Line type="monotone" dataKey="close" stroke="#4ade80" dot={false} strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            {score && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(score.engines).map(([key, data]) => (
                  <div key={key} className="bg-gray-800 rounded-xl p-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="font-semibold capitalize">{key}</h4>
                      <span className={`font-bold ${getScoreColor(data.score)}`}>{data.score}/100</span>
                    </div>
                    {data.reasons.map((r, i) => (
                      <div key={i} className="text-green-400 text-sm mb-1">✓ {r}</div>
                    ))}
                    {data.warnings.map((w, i) => (
                      <div key={i} className="text-yellow-400 text-sm mb-1">⚠ {w}</div>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Financials Tab */}
        {activeTab === 'financials' && (
          <div className="bg-gray-800 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left px-4 py-3 text-gray-400">Period</th>
                  <th className="text-right px-4 py-3 text-gray-400">Revenue (Cr)</th>
                  <th className="text-right px-4 py-3 text-gray-400">PAT (Cr)</th>
                  <th className="text-right px-4 py-3 text-gray-400">PAT Margin</th>
                  <th className="text-right px-4 py-3 text-gray-400">EBITDA Margin</th>
                </tr>
              </thead>
              <tbody>
                {financials.map((f, i) => (
                  <tr key={i} className="border-b border-gray-700 hover:bg-gray-700">
                    <td className="px-4 py-3 font-medium">{f.period}</td>
                    <td className="px-4 py-3 text-right">{f.revenue ? f.revenue.toLocaleString() : '-'}</td>
                    <td className="px-4 py-3 text-right">{f.pat ? f.pat.toLocaleString() : '-'}</td>
                    <td className="px-4 py-3 text-right text-green-400">{f.pat_margin ? `${f.pat_margin}%` : '-'}</td>
                    <td className="px-4 py-3 text-right text-blue-400">{f.ebitda_margin ? `${f.ebitda_margin}%` : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* AI Summary Tab */}
        {activeTab === 'ai summary' && (
          <div className="space-y-6">
            {!summary ? (
              <div className="text-center text-gray-400 py-12">
                <div className="text-4xl mb-4">🤖</div>
                <p>Loading AI Summary...</p>
              </div>
            ) : (
              <>
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-green-400 font-semibold mb-2">Business</h3>
                  <p className="text-gray-300">{summary.business}</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-green-400 font-semibold mb-3">Strengths</h3>
                    {summary.strengths.map((s, i) => <p key={i} className="text-gray-300 text-sm mb-2">✓ {s}</p>)}
                  </div>
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-yellow-400 font-semibold mb-3">Weaknesses</h3>
                    {summary.weaknesses.map((w, i) => <p key={i} className="text-gray-300 text-sm mb-2">⚠ {w}</p>)}
                  </div>
                </div>
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-blue-400 font-semibold mb-2">Future Outlook</h3>
                  <p className="text-gray-300">{summary.future_outlook}</p>
                </div>
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-red-400 font-semibold mb-3">Risks</h3>
                  {summary.risks.map((r, i) => <p key={i} className="text-gray-300 text-sm mb-2">⚠ {r}</p>)}
                </div>
                <div className="bg-green-900 border border-green-700 rounded-xl p-6">
                  <h3 className="text-green-400 font-semibold mb-2">AI Verdict</h3>
                  <p className="text-white font-medium">{summary.ai_verdict}</p>
                </div>
              </>
            )}
          </div>
        )}

        {/* News Tab */}
        {activeTab === 'news' && (
          <div className="space-y-4">
            {news.map((n, i) => (
              <div key={i} className="bg-gray-800 rounded-xl p-5">
                <div className="flex justify-between items-start gap-4">
                  <a href={n.url} target="_blank" rel="noreferrer" className="text-white font-medium hover:text-green-400">
                    {n.title}
                  </a>
                  <span className={`text-xs px-2 py-1 rounded-full shrink-0 ${
                    n.sentiment === 'positive' ? 'bg-green-900 text-green-400' :
                    n.sentiment === 'negative' ? 'bg-red-900 text-red-400' :
                    'bg-gray-700 text-gray-400'
                  }`}>
                    {n.sentiment}
                  </span>
                </div>
                <p className="text-gray-400 text-sm mt-2">{n.summary}</p>
                <p className="text-gray-600 text-xs mt-2">{n.published_at?.slice(0, 10)}</p>
              </div>
            ))}
          </div>
        )}

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="space-y-4">
            <div className="bg-gray-800 rounded-xl p-6">
              <h3 className="font-semibold mb-4">Ask anything about {symbol}</h3>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={chat.question}
                  onChange={e => setChat(c => ({ ...c, question: e.target.value }))}
                  onKeyDown={e => e.key === 'Enter' && handleChat()}
                  placeholder={`Why is ${symbol} interesting?`}
                  className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-green-400"
                />
                <button
                  onClick={handleChat}
                  disabled={chat.loading}
                  className="bg-green-500 hover:bg-green-600 text-black font-semibold px-6 py-3 rounded-lg transition"
                >
                  {chat.loading ? '...' : 'Ask'}
                </button>
              </div>
              {chat.answer && (
                <div className="mt-4 p-4 bg-gray-700 rounded-lg text-gray-300">
                  {chat.answer}
                </div>
              )}
            </div>
          </div>
        )}

        {/* QoQ Tab */}
        {activeTab === 'qoq' && (
          <div className="space-y-6">
            {!changes ? (
              <div className="text-center text-gray-400 py-12">Loading...</div>
            ) : (
              <>
                <div className="flex gap-2 text-gray-400 text-sm mb-2">
                  <span>{changes.from}</span>
                  <span>→</span>
                  <span className="text-white">{changes.to}</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {changes.changes.map((c, i) => (
                    <div key={i} className="bg-gray-800 rounded-xl p-4">
                      <div className="text-gray-400 text-sm mb-1">{c.metric}</div>
                      <div className={`text-2xl font-bold ${c.direction === 'up' ? 'text-green-400' : 'text-red-400'}`}>
                        {c.direction === 'up' ? '+' : ''}{c.change_percent}%
                      </div>
                      <div className="text-gray-500 text-xs mt-1">
                        {c.from} → {c.to} {c.unit}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-green-400 font-semibold mb-3">AI Explanation</h3>
                  <p className="text-gray-300 leading-relaxed">{changes.ai_explanation}</p>
                </div>
              </>
            )}
          </div>
        )}

      </div>
    </div>
  )
}