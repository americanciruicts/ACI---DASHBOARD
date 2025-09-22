'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { LogOut, User as UserIcon, Settings, Home, Users, Menu, X, TrendingUp, ArrowLeftRight, BarChart } from 'lucide-react'
import { User, isSuperUser } from '@/lib/auth'

export default function YToolPage() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('accessToken')
    const userData = localStorage.getItem('user')

    if (!token) {
      router.push('/login')
      return
    }

    if (userData) {
      const parsedUser = JSON.parse(userData)
      setUser(parsedUser)
      
      // Check if user has access to this tool
      const hasYToolAccess = parsedUser.tools?.some((tool: any) => tool.name === 'y_tool') || 
                            parsedUser.roles?.some((role: any) => role.name === 'superuser')
      
      if (!hasYToolAccess) {
        router.push('/dashboard')
        return
      }
    }
    setIsLoading(false)
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('user')
    router.push('/login')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  const menuItems = [
    { icon: Home, label: 'Dashboard', href: '/dashboard', show: true },
    { icon: Users, label: 'User Management', href: '/dashboard/users', show: isSuperUser(user) },
    { icon: Settings, label: 'Settings', href: '/dashboard/settings', show: true },
  ]

  const userTools = user.tools || []

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Top Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="flex justify-between items-center h-16 px-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            >
              {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 relative">
                <Image
                  src="/logo.jpg"
                  alt="ACI DASHBOARD"
                  fill
                  className="object-contain rounded-lg"
                />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 hidden sm:block">ACI DASHBOARD</h1>
            </div>
          </div>
          
          {/* User Profile Section */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3 bg-gray-50 rounded-lg px-3 py-2 shadow-sm">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <UserIcon className="h-4 w-4 text-white" />
              </div>
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
                <p className="text-xs text-gray-500">@{user.username}</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {user.roles.map((role) => (
                    <span
                      key={role.id}
                      className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full"
                    >
                      {role.name}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition duration-200 p-2 rounded-lg hover:bg-gray-100"
            >
              <LogOut className="h-5 w-5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <div className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-30 w-64 bg-white shadow-lg border-r transition-transform duration-300 ease-in-out`}>
          <div className="flex flex-col h-full pt-4">
            <nav className="flex-1 px-4">
              <ul className="space-y-2">
                {menuItems.map((item) => {
                  if (!item.show) return null
                  return (
                    <li key={item.label}>
                      <button
                        onClick={() => router.push(item.href)}
                        className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition duration-200"
                      >
                        <item.icon className="h-5 w-5" />
                        <span>{item.label}</span>
                      </button>
                    </li>
                  )
                })}
                
                {/* Tools Section */}
                {userTools.length > 0 && (
                  <>
                    <li className="pt-4">
                      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 py-2">
                        Tools
                      </p>
                    </li>
                    {userTools.map((tool) => {
                      const isActive = window.location.pathname === tool.route
                      return (
                        <li key={tool.id}>
                          <button
                            onClick={() => router.push(tool.route)}
                            className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition duration-200 ${
                              isActive 
                                ? 'bg-blue-100 text-blue-600 shadow-sm' 
                                : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                            }`}
                          >
                            {tool.icon === 'compare' && <ArrowLeftRight className="h-5 w-5" />}
                            {tool.icon === 'x-circle' && <div className="h-5 w-5 bg-gray-400 rounded-full flex items-center justify-center text-xs text-white font-bold">X</div>}
                            {tool.icon === 'y-circle' && <div className="h-5 w-5 bg-gray-400 rounded-full flex items-center justify-center text-xs text-white font-bold">Y</div>}
                            <span>{tool.display_name}</span>
                          </button>
                        </li>
                      )
                    })}
                  </>
                )}
              </ul>
            </nav>
          </div>
        </div>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div
            className="lg:hidden fixed inset-0 z-20 bg-black bg-opacity-50"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main Content */}
        <main className="flex-1 p-4 lg:p-8">
          <div className="mb-8">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-purple-100 rounded-lg">
                <div className="h-6 w-6 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">Y</div>
              </div>
              <h2 className="text-3xl font-bold text-gray-900">Y Tool</h2>
            </div>
            <p className="text-gray-600">
              Comprehensive Y analysis and trend monitoring tool
            </p>
          </div>

          {/* Dashboard Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Y Metrics</p>
                  <p className="text-2xl font-bold text-gray-900">1,234</p>
                </div>
                <div className="p-2 bg-purple-100 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-purple-600" />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">+12.5%</span>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Processing Rate</p>
                  <p className="text-2xl font-bold text-gray-900">98.7%</p>
                </div>
                <div className="p-2 bg-green-100 rounded-lg">
                  <BarChart className="h-5 w-5 text-green-600" />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded-full">Optimal</span>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Active Sessions</p>
                  <p className="text-2xl font-bold text-gray-900">47</p>
                </div>
                <div className="p-2 bg-orange-100 rounded-lg">
                  <div className="h-5 w-5 bg-orange-600 rounded-full flex items-center justify-center text-white font-bold text-xs">Y</div>
                </div>
              </div>
              <div className="mt-4">
                <span className="text-xs text-orange-600 bg-orange-100 px-2 py-1 rounded-full">Live</span>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Success Rate</p>
                  <p className="text-2xl font-bold text-gray-900">99.2%</p>
                </div>
                <div className="p-2 bg-blue-100 rounded-lg">
                  <div className="h-5 w-5 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xs">✓</div>
                </div>
              </div>
              <div className="mt-4">
                <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">Excellent</span>
              </div>
            </div>
          </div>

          {/* Analysis Controls */}
          <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Y Analysis Controls</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Analysis Type</label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                    <option>Trend Analysis</option>
                    <option>Pattern Recognition</option>
                    <option>Predictive Modeling</option>
                    <option>Anomaly Detection</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Time Period</label>
                  <div className="grid grid-cols-2 gap-3">
                    <input 
                      type="date" 
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                    <input 
                      type="date" 
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Data Source</label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                    <option>Real-time Feed</option>
                    <option>Historical Database</option>
                    <option>Combined Sources</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Sensitivity Level</label>
                  <input 
                    type="range" 
                    min="1" 
                    max="10" 
                    defaultValue="5"
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Low</span>
                    <span>High</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-6 flex justify-center space-x-4">
              <button className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-8 rounded-lg transition duration-200 ease-in-out transform hover:scale-105 shadow-lg">
                Start Y Analysis
              </button>
              <button className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-3 px-8 rounded-lg transition duration-200 ease-in-out transform hover:scale-105 shadow-lg">
                Export Results
              </button>
            </div>
          </div>

          {/* Results Display */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Y Analysis Results</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">Trend Indicators</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Upward Trend</span>
                      <span className="text-sm font-medium text-green-600">85%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Stability Index</span>
                      <span className="text-sm font-medium text-blue-600">92%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Volatility</span>
                      <span className="text-sm font-medium text-orange-600">Low</span>
                    </div>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">Key Insights</h4>
                  <div className="space-y-2 text-sm text-gray-600">
                    <p>• Strong positive correlation detected</p>
                    <p>• Seasonal patterns identified</p>
                    <p>• Forecast confidence: 94%</p>
                    <p>• No anomalies detected</p>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center justify-center h-32 bg-gray-50 rounded-lg">
                <div className="text-center text-gray-500">
                  <TrendingUp className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p className="text-sm">Analysis chart will appear here</p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}