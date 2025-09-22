'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { LogOut, User as UserIcon, Settings, Home, Users, Menu, X, ChevronDown, ChevronRight, ArrowLeftRight, Shield, Activity, BarChart3, TrendingUp } from 'lucide-react'
import { User, isSuperUser, getAllUsers } from '@/lib/auth'

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [toolsExpanded, setToolsExpanded] = useState(true)
  const [adminStats, setAdminStats] = useState<{totalUsers: number, activeUsers: number, totalTools: number} | null>(null)
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
      
      // Fetch admin stats if superuser
      if (isSuperUser(parsedUser)) {
        fetchAdminStats(token)
      }
    }
    setIsLoading(false)
  }, [router])

  const fetchAdminStats = async (token: string) => {
    try {
      const users = await getAllUsers(token)
      const activeUsers = users.filter(u => u.is_active).length
      const allTools = new Set()
      users.forEach(u => u.tools.forEach(t => allTools.add(t.id)))
      
      setAdminStats({
        totalUsers: users.length,
        activeUsers: activeUsers,
        totalTools: allTools.size
      })
    } catch (error) {
      console.error('Failed to fetch admin stats:', error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('user')
    router.push('/login')
  }

  const navigateToUserManagement = () => {
    router.push('/dashboard/users')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center gradient-primary">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
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
    <div className="min-h-screen gradient-primary">
      {/* Top Header */}
      <header className="bg-white/95 backdrop-blur-sm shadow-lg border-b border-white/20 sticky top-0 z-40">
        <div className="flex justify-between items-center h-16 px-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 rounded-xl text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-all"
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
              <h1 className="text-2xl font-bold text-gradient hidden sm:block">ACI DASHBOARD</h1>
            </div>
          </div>
          
          {/* User Profile Section */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3 bg-white/80 backdrop-blur-sm rounded-xl px-4 py-2 shadow-lg border border-white/20">
              <div className="w-8 h-8 gradient-blue rounded-full flex items-center justify-center">
                <UserIcon className="h-4 w-4 text-white" />
              </div>
              <div className="text-right hidden sm:block">
                <p className="text-sm font-semibold text-gray-900">{user.full_name}</p>
                <p className="text-xs text-gray-500">@{user.username}</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {user.roles.map((role) => (
                    <span
                      key={role.id}
                      className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-medium"
                    >
                      {role.name}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 text-white hover:text-gray-200 transition duration-200 p-3 rounded-xl hover:bg-white/10 backdrop-blur-sm"
            >
              <LogOut className="h-5 w-5" />
              <span className="hidden sm:inline font-medium">Logout</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <div className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-30 w-72 bg-white/95 backdrop-blur-md shadow-2xl border-r border-white/20 transition-transform duration-300 ease-in-out`}>
          <div className="flex flex-col h-full pt-6">
            <nav className="flex-1 px-6">
              <ul className="space-y-3">
                {menuItems.map((item) => {
                  if (!item.show) return null
                  const isActive = window.location.pathname === item.href
                  return (
                    <li key={item.label}>
                      <button
                        onClick={() => router.push(item.href)}
                        className={`nav-item w-full ${isActive ? 'active' : ''}`}
                      >
                        <item.icon className="h-5 w-5" />
                        <span className="font-medium">{item.label}</span>
                      </button>
                    </li>
                  )
                })}
                
                {/* Tools Section */}
                {userTools.length > 0 && (
                  <>
                    <li className="pt-6">
                      <button
                        onClick={() => setToolsExpanded(!toolsExpanded)}
                        className="w-full flex items-center justify-between px-4 py-3 text-sm font-bold text-gray-500 uppercase tracking-wider hover:text-gray-700 transition duration-200"
                      >
                        <span>Tools</span>
                        {toolsExpanded ? (
                          <ChevronDown className="h-4 w-4" />
                        ) : (
                          <ChevronRight className="h-4 w-4" />
                        )}
                      </button>
                    </li>
                    {toolsExpanded && userTools.map((tool) => (
                      <li key={tool.id} className="ml-4">
                        <button
                          onClick={() => router.push(tool.route)}
                          className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition duration-200 font-medium"
                        >
                          {tool.icon === 'compare' && <ArrowLeftRight className="h-4 w-4" />}
                          {tool.icon === 'x-circle' && <div className="h-4 w-4 bg-orange-500 rounded-full flex items-center justify-center text-xs text-white font-bold">X</div>}
                          {tool.icon === 'y-circle' && <div className="h-4 w-4 bg-purple-500 rounded-full flex items-center justify-center text-xs text-white font-bold">Y</div>}
                          <span className="text-sm">{tool.display_name}</span>
                        </button>
                      </li>
                    ))}
                  </>
                )}
              </ul>
            </nav>
          </div>
        </div>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div
            className="lg:hidden fixed inset-0 z-20 bg-black bg-opacity-50 backdrop-blur-sm"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main Content */}
        <main className="flex-1 p-6 lg:p-8 overflow-y-auto">
          <div className="mb-8">
            <h2 className="text-4xl font-bold text-white mb-2">
              Welcome back, {user.full_name}!
            </h2>
            <p className="text-white/80 text-lg">
              Here's your personalized dashboard overview
            </p>
          </div>

          {/* Admin Summary for Super Users */}
          {isSuperUser(user) && adminStats && (
            <div className="mb-8">
              <h3 className="text-2xl font-semibold text-white mb-4 flex items-center space-x-2">
                <Shield className="h-6 w-6" />
                <span>Admin Overview</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-card p-6 card-hover">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-500 mb-1">Total Users</p>
                      <p className="text-3xl font-bold text-gray-900">{adminStats.totalUsers}</p>
                    </div>
                    <div className="p-3 gradient-blue rounded-xl">
                      <Users className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="mt-4">
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-medium">
                      System-wide
                    </span>
                  </div>
                </div>

                <div className="glass-card p-6 card-hover">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-500 mb-1">Active Users</p>
                      <p className="text-3xl font-bold text-gray-900">{adminStats.activeUsers}</p>
                    </div>
                    <div className="p-3 bg-green-500 rounded-xl">
                      <Activity className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="mt-4">
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium">
                      Currently Online
                    </span>
                  </div>
                </div>

                <div className="glass-card p-6 card-hover">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-500 mb-1">Available Tools</p>
                      <p className="text-3xl font-bold text-gray-900">{adminStats.totalTools}</p>
                    </div>
                    <div className="p-3 bg-purple-500 rounded-xl">
                      <BarChart3 className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="mt-4">
                    <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full font-medium">
                      In Use
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* User Role Summary */}
          <div className="mb-8">
            <h3 className="text-2xl font-semibold text-white mb-4">Your Roles & Permissions</h3>
            <div className="glass-card p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-800 mb-3 flex items-center space-x-2">
                    <Shield className="h-5 w-5 text-blue-600" />
                    <span>Assigned Roles</span>
                  </h4>
                  <div className="space-y-3">
                    {user.roles.map((role) => (
                      <div key={role.id} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                        <div>
                          <p className="font-semibold text-blue-900 capitalize">{role.name}</p>
                          <p className="text-sm text-blue-700">{role.description}</p>
                        </div>
                        <div className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                          Active
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-lg font-semibold text-gray-800 mb-3 flex items-center space-x-2">
                    <TrendingUp className="h-5 w-5 text-green-600" />
                    <span>Access Level</span>
                  </h4>
                  <div className="space-y-3">
                    <div className="p-3 bg-green-50 rounded-lg">
                      <p className="font-semibold text-green-900">Tool Access</p>
                      <p className="text-sm text-green-700">{userTools.length} tools available</p>
                    </div>
                    {isSuperUser(user) && (
                      <div className="p-3 bg-purple-50 rounded-lg">
                        <p className="font-semibold text-purple-900">Admin Privileges</p>
                        <p className="text-sm text-purple-700">Full system access granted</p>
                      </div>
                    )}
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="font-semibold text-gray-900">Account Status</p>
                      <p className="text-sm text-gray-700">{user.is_active ? 'Active & Verified' : 'Inactive'}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Tools Overview */}
          {userTools.length > 0 && (
            <div className="mb-8">
              <h3 className="text-2xl font-semibold text-white mb-4">Your Tools</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {userTools.map((tool) => (
                  <div
                    key={tool.id}
                    onClick={() => router.push(tool.route)}
                    className="glass-card p-6 card-hover cursor-pointer"
                  >
                    <div className="flex items-center space-x-4 mb-4">
                      <div className="p-3 gradient-blue rounded-xl">
                        {tool.icon === 'compare' && <ArrowLeftRight className="h-6 w-6 text-white" />}
                        {tool.icon === 'x-circle' && <div className="h-6 w-6 bg-orange-600 rounded-full flex items-center justify-center text-white font-bold text-sm">X</div>}
                        {tool.icon === 'y-circle' && <div className="h-6 w-6 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">Y</div>}
                      </div>
                      <div>
                        <h4 className="text-lg font-semibold text-gray-900">{tool.display_name}</h4>
                        <p className="text-sm text-gray-600">{tool.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium">
                        Ready to use
                      </span>
                      <span className="text-blue-600 font-medium text-sm hover:text-blue-800 transition-colors">
                        Launch →
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="mb-8">
            <h3 className="text-2xl font-semibold text-white mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="glass-card p-6 card-hover">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-800 mb-2">Profile Settings</h4>
                    <p className="text-gray-600 text-sm">Update your account information</p>
                  </div>
                  <UserIcon className="h-8 w-8 text-blue-600" />
                </div>
              </div>

              {isSuperUser(user) && (
                <div 
                  className="glass-card p-6 card-hover cursor-pointer"
                  onClick={navigateToUserManagement}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-lg font-semibold text-gray-800 mb-2">User Management</h4>
                      <p className="text-gray-600 text-sm">Manage users, roles & tools</p>
                    </div>
                    <Users className="h-8 w-8 text-blue-600" />
                  </div>
                </div>
              )}

              <div className="glass-card p-6 card-hover">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-800 mb-2">System Settings</h4>
                    <p className="text-gray-600 text-sm">Configure preferences</p>
                  </div>
                  <Settings className="h-8 w-8 text-blue-600" />
                </div>
              </div>
            </div>
          </div>

          {/* User Information */}
          <div className="glass-card p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-6">Account Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Full Name</label>
                <div className="p-3 bg-gray-50 rounded-lg text-gray-900 font-medium">{user.full_name}</div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Username</label>
                <div className="p-3 bg-gray-50 rounded-lg text-gray-900 font-medium">@{user.username}</div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Email Address</label>
                <div className="p-3 bg-gray-50 rounded-lg text-gray-900 font-medium">{user.email}</div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Account Status</label>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                    user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-gray-700 mb-2">System Roles</label>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex flex-wrap gap-2">
                    {user.roles.map((role) => (
                      <span
                        key={role.id}
                        className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold"
                      >
                        {role.name.charAt(0).toUpperCase() + role.name.slice(1)}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              {userTools.length > 0 && (
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Assigned Tools</label>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex flex-wrap gap-2">
                      {userTools.map((tool) => (
                        <span
                          key={tool.id}
                          className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold"
                        >
                          {tool.display_name}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}