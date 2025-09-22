'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { LogOut, User as UserIcon, Settings, Home, Users, Menu, X, Zap, ArrowLeftRight } from 'lucide-react'
import { User, isSuperUser } from '@/lib/auth'

export default function XToolPage() {
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
      const hasXToolAccess = parsedUser.tools?.some((tool: any) => tool.name === 'x_tool') || 
                            parsedUser.roles?.some((role: any) => role.name === 'superuser')
      
      if (!hasXToolAccess) {
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
              <div className="p-2 bg-orange-100 rounded-lg">
                <div className="h-6 w-6 bg-orange-600 rounded-full flex items-center justify-center text-white font-bold text-sm">X</div>
              </div>
              <h2 className="text-3xl font-bold text-gray-900">X Tool</h2>
            </div>
            <p className="text-gray-600">
              Advanced X functionality for enhanced processing
            </p>
          </div>

          {/* Tool Features */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <Zap className="h-5 w-5 text-orange-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-800">X Processing</h3>
              </div>
              <p className="text-gray-600 text-sm mb-4">
                High-speed X data processing with advanced algorithms
              </p>
              <button className="w-full bg-orange-600 hover:bg-orange-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200">
                Start Processing
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-green-100 rounded-lg">
                  <div className="h-5 w-5 bg-green-600 rounded-full flex items-center justify-center text-white font-bold text-xs">X</div>
                </div>
                <h3 className="text-lg font-semibold text-gray-800">X Analysis</h3>
              </div>
              <p className="text-gray-600 text-sm mb-4">
                Comprehensive X pattern analysis and insights
              </p>
              <button className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200">
                Run Analysis
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <div className="h-5 w-5 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xs">X</div>
                </div>
                <h3 className="text-lg font-semibold text-gray-800">X Reports</h3>
              </div>
              <p className="text-gray-600 text-sm mb-4">
                Generate detailed X performance reports
              </p>
              <button className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200">
                Generate Report
              </button>
            </div>
          </div>

          {/* Configuration Panel */}
          <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">X Tool Configuration</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">X Parameter Settings</label>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Processing Speed</span>
                    <select className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-orange-500">
                      <option>Normal</option>
                      <option>Fast</option>
                      <option>Ultra Fast</option>
                    </select>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Accuracy Level</span>
                    <select className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-orange-500">
                      <option>Standard</option>
                      <option>High</option>
                      <option>Maximum</option>
                    </select>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Output Format</span>
                    <select className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-orange-500">
                      <option>JSON</option>
                      <option>CSV</option>
                      <option>XML</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Advanced Options</label>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input type="checkbox" className="rounded border-gray-300 text-orange-600 shadow-sm focus:border-orange-300 focus:ring focus:ring-orange-200 focus:ring-opacity-50" />
                    <span className="ml-2 text-sm text-gray-600">Enable X Optimization</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="rounded border-gray-300 text-orange-600 shadow-sm focus:border-orange-300 focus:ring focus:ring-orange-200 focus:ring-opacity-50" />
                    <span className="ml-2 text-sm text-gray-600">Auto-save Results</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="rounded border-gray-300 text-orange-600 shadow-sm focus:border-orange-300 focus:ring focus:ring-orange-200 focus:ring-opacity-50" />
                    <span className="ml-2 text-sm text-gray-600">Send Notifications</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Status Panel */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">X Tool Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">System Status</p>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <p className="text-sm font-medium text-gray-900">Online</p>
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Active Jobs</p>
                <p className="text-lg font-semibold text-gray-900">0</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Queue Length</p>
                <p className="text-lg font-semibold text-gray-900">0</p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}