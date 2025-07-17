import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Home, 
  Package, 
  Users, 
  ShoppingCart, 
  DollarSign, 
  BarChart3, 
  Settings, 
  LogOut, 
  ChevronLeft,
  ChevronRight,
  User,
  Send,
  ShoppingBag,
  Shield,
  Printer
} from 'lucide-react'

const Sidebar = ({ user, onLogout }) => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const hasPermission = (requiredRole) => {
    if (!user) return false
    
    const roleHierarchy = {
      'admin': 4,
      'sales': 3,
      'warehouse': 2,
      'employee': 1
    }
    
    return roleHierarchy[user.role] >= roleHierarchy[requiredRole]
  }

  const navItems = [
    { name: 'لوحة التحكم', icon: Home, path: '/', role: 'employee', color: 'from-blue-500 to-cyan-500' },
    { name: 'المنتجات', icon: Package, path: '/products', role: 'warehouse', color: 'from-green-500 to-emerald-500' },
    { name: 'الزبائن', icon: Users, path: '/customers', role: 'sales', color: 'from-purple-500 to-violet-500' },
    { name: 'المبيعات', icon: ShoppingCart, path: '/sales', role: 'sales', color: 'from-orange-500 to-red-500' },
    { name: 'الطلبات', icon: ShoppingBag, path: '/orders', role: 'sales', color: 'from-teal-500 to-cyan-500' },
    { name: 'الضمانات', icon: Shield, path: '/warranties', role: 'sales', color: 'from-indigo-500 to-purple-500' },
    { name: 'المصروفات', icon: DollarSign, path: '/expenses', role: 'admin', color: 'from-pink-500 to-rose-500' },
    { name: 'التقارير', icon: BarChart3, path: '/reports', role: 'sales', color: 'from-indigo-500 to-blue-500' },
    { name: 'المستخدمون', icon: Settings, path: '/users', role: 'admin', color: 'from-gray-500 to-slate-500' },
    { name: 'إعدادات التليجرام', icon: Send, path: '/telegram', role: 'admin', color: 'from-blue-500 to-cyan-500' },
    { name: 'إعدادات الطباعة', icon: Printer, path: '/print-settings', role: 'admin', color: 'from-purple-500 to-pink-500' },
  ]

  const filteredNavItems = navItems.filter(item => hasPermission(item.role))

  const handleNavigation = (path) => {
    navigate(path === '/' ? '/dashboard' : path)
  }

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/' || location.pathname === '/dashboard'
    }
    return location.pathname === path
  }

  return (
    <motion.div 
      className={`bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-white transition-all duration-300 ease-in-out ${
        isCollapsed ? 'w-16' : 'w-64'
      } flex flex-col shadow-2xl border-r border-slate-700`}
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="p-4 border-b border-slate-700">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <motion.div 
              className="flex items-center gap-3"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center shadow-lg">
                <Package className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                  البدر للإنارة
                </h1>
                <p className="text-xs text-slate-400">نظام إدارة المحل</p>
              </div>
            </motion.div>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors duration-200 shadow-lg"
          >
            {isCollapsed ? (
              <ChevronLeft className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* User Info */}
      {!isCollapsed && user && (
        <motion.div 
          className="p-4 border-b border-slate-700 bg-gradient-to-r from-slate-800 to-slate-700"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center shadow-lg">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user.name}</p>
              <p className="text-xs text-slate-400 truncate">
                {user.role === 'admin' ? 'مدير' : 
                 user.role === 'sales' ? 'موظف مبيعات' : 
                 user.role === 'warehouse' ? 'موظف مخزن' : 'موظف'}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {filteredNavItems.map((item, index) => {
          const Icon = item.icon
          const active = isActive(item.path)
          
          return (
            <motion.button
              key={item.name}
              onClick={() => handleNavigation(item.path)}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group relative overflow-hidden ${
                active 
                  ? 'bg-gradient-to-r ' + item.color + ' text-white shadow-lg transform scale-105' 
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
              whileHover={{ scale: active ? 1.05 : 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {/* Background gradient effect */}
              {!active && (
                <div className={`absolute inset-0 bg-gradient-to-r ${item.color} opacity-0 group-hover:opacity-20 transition-opacity duration-200 rounded-xl`} />
              )}
              
              {/* Active indicator */}
              {active && (
                <motion.div
                  className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full"
                  layoutId="activeIndicator"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
              
              <Icon className={`w-5 h-5 flex-shrink-0 ${active ? 'text-white' : 'text-slate-400 group-hover:text-white'} transition-colors duration-200`} />
              
              {!isCollapsed && (
                <span className="font-medium text-sm truncate">
                  {item.name}
                </span>
              )}

              {/* Tooltip for collapsed state */}
              {isCollapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                  {item.name}
                </div>
              )}
            </motion.button>
          )
        })}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-slate-700">
        <motion.button
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-3 py-3 rounded-xl text-slate-300 hover:text-white hover:bg-red-600 transition-all duration-200 group"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {!isCollapsed && (
            <span className="font-medium text-sm">تسجيل الخروج</span>
          )}

          {/* Tooltip for collapsed state */}
          {isCollapsed && (
            <div className="absolute left-full ml-2 px-2 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
              تسجيل الخروج
            </div>
          )}
        </motion.button>
      </div>
    </motion.div>
  )
}

export default Sidebar

