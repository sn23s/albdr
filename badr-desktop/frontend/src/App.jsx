import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import LoginPage from './components/LoginPage'
import Dashboard from './components/Dashboard'
import Sidebar from './components/Sidebar'
import ProductsPage from './components/ProductsPage'
import CustomersPage from './components/CustomersPage'
import SalesPage from './components/SalesPage'
import ExpensesPage from './components/ExpensesPage'
import ReportsPage from './components/ReportsPage'
import UsersPage from './components/UsersPage'
import TelegramSettings from './components/TelegramSettings'
import OrdersPage from './components/OrdersPage'
import WarrantyPage from './components/WarrantyPage'
import PrintSettings from './components/PrintSettings'

// Page transition variants
const pageVariants = {
  initial: {
    opacity: 0,
    x: 20
  },
  in: {
    opacity: 1,
    x: 0
  },
  out: {
    opacity: 0,
    x: -20
  }
}

const pageTransition = {
  type: "tween",
  ease: "anticipate",
  duration: 0.3
}

// Loading component
const LoadingScreen = () => (
  <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
    <div className="text-center">
      <div className="relative">
        <div className="w-20 h-20 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
        <div className="absolute inset-0 w-20 h-20 border-4 border-transparent border-r-blue-400 rounded-full animate-pulse mx-auto"></div>
      </div>
      <h2 className="text-2xl font-bold text-blue-800 mb-2">البدر للإنارة</h2>
      <p className="text-blue-600 animate-pulse">جاري التحميل...</p>
    </div>
  </div>
)

// Animated page wrapper
const AnimatedPage = ({ children }) => {
  const location = useLocation()
  
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial="initial"
        animate="in"
        exit="out"
        variants={pageVariants}
        transition={pageTransition}
        className="w-full"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}

// Main app content
const AppContent = () => {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in
    const savedUser = localStorage.getItem('currentUser')
    if (savedUser) {
      setUser(JSON.parse(savedUser))
    }
    
    // Simulate loading time
    setTimeout(() => {
      setIsLoading(false)
    }, 1500)
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
    localStorage.setItem('currentUser', JSON.stringify(userData))
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('currentUser')
    setCurrentPage('dashboard')
  }

  if (isLoading) {
    return <LoadingScreen />
  }

  if (!user) {
    return <LoginPage onLogin={handleLogin} />
  }

  return (
    <div className="flex h-screen bg-gray-50" dir="rtl">
      <Sidebar 
        currentPage={currentPage} 
        setCurrentPage={setCurrentPage}
        user={user}
        onLogout={handleLogout}
      />
      <main className="flex-1 overflow-hidden">
        <AnimatedPage>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/customers" element={<CustomersPage />} />
            <Route path="/sales" element={<SalesPage />} />
            <Route path="/expenses" element={<ExpensesPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/telegram" element={<TelegramSettings />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/warranties" element={<WarrantyPage />} />
            <Route path="/print-settings" element={<PrintSettings />} />
          </Routes>
        </AnimatedPage>
      </main>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App

