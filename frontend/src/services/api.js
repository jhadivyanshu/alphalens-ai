import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000/api'

const api = axios.create({
  baseURL: API_BASE
})

export const searchCompanies = (q) => api.get(`/search?q=${q}`)
export const getCompany = (symbol) => api.get(`/company/${symbol}`)
export const getCompanyPrices = (symbol, period = '1y') => api.get(`/company/${symbol}/prices?period=${period}`)
export const getCompanyFinancials = (symbol) => api.get(`/company/${symbol}/financials`)
export const getCompanyScore = (symbol) => api.get(`/company/${symbol}/score`)
export const getCompanySummary = (symbol) => api.get(`/company/${symbol}/summary`)
export const getCompanyNews = (symbol) => api.get(`/company/${symbol}/news`)
export const sendChat = (question, symbol) => api.post(`/chat`, { question, symbol })