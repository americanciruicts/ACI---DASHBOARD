'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { LogOut, User as UserIcon, Settings, Home, Users, Menu, X, Plus, Edit, Eye, EyeOff, ChevronDown, ChevronRight, ArrowLeftRight } from 'lucide-react'
import { User, Role, Tool, getAllUsers, getAllRoles, getAllTools, createUser, updateUser, isSuperUser, UserCreate, UserUpdate } from '@/lib/auth'

interface UserFormData {
  full_name: string
  username: string
  email: string
  password: string
  role_ids: number[]
  tool_ids: number[]
  is_active: boolean
}

export default function UserManagementPage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [tools, setTools] = useState<Tool[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [toolsExpanded, setToolsExpanded] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [showEditForm, setShowEditForm] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [showPassword, setShowPassword] = useState(false)
  const [formData, setFormData] = useState<UserFormData>({
    full_name: '',
    username: '',
    email: '',
    password: '',
    role_ids: [],
    tool_ids: [],
    is_active: true
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('accessToken')
    const userData = localStorage.getItem('user')

    if (!token) {
      router.push('/login')
      return
    }

    if (userData) {
      const user = JSON.parse(userData)
      setCurrentUser(user)
      
      if (!isSuperUser(user)) {
        router.push('/dashboard')
        return
      }
    }

    fetchData()
  }, [router])

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('accessToken')
      if (!token) return

      const [usersData, rolesData, toolsData] = await Promise.all([
        getAllUsers(token),
        getAllRoles(token),
        getAllTools(token)
      ])

      setUsers(usersData)
      setRoles(rolesData)
      setTools(toolsData)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch data')
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('user')
    router.push('/login')
  }

  const resetForm = () => {
    setFormData({
      full_name: '',
      username: '',
      email: '',
      password: '',
      role_ids: [],
      tool_ids: [],
      is_active: true
    })
    setSelectedUser(null)
    setShowPassword(false)
    setError('')
    setSuccess('')
  }

  const handleCreateUser = () => {
    resetForm()
    setShowCreateForm(true)
  }

  const handleEditUser = (user: User) => {
    setFormData({
      full_name: user.full_name,
      username: user.username,
      email: user.email,
      password: '',
      role_ids: user.roles.map(role => role.id),
      tool_ids: user.tools.map(tool => tool.id),
      is_active: user.is_active
    })
    setSelectedUser(user)
    setShowEditForm(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    try {
      const token = localStorage.getItem('accessToken')
      if (!token) return

      if (showCreateForm) {
        const userData: UserCreate = {
          full_name: formData.full_name,
          username: formData.username,
          email: formData.email,
          password: formData.password,
          role_ids: formData.role_ids,
          tool_ids: formData.tool_ids
        }
        await createUser(token, userData)
        setSuccess('User created successfully')
      } else if (showEditForm && selectedUser) {
        const userData: UserUpdate = {
          full_name: formData.full_name,
          username: formData.username,
          email: formData.email,
          role_ids: formData.role_ids,
          tool_ids: formData.tool_ids,
          is_active: formData.is_active
        }
        if (formData.password) {
          userData.password = formData.password
        }
        await updateUser(token, selectedUser.id, userData)
        setSuccess('User updated successfully')
      }

      await fetchData()
      setShowCreateForm(false)
      setShowEditForm(false)
      resetForm()
    } catch (err: any) {
      setError(err.message || 'Operation failed')
    }
  }

  const handleRoleToggle = (roleId: number) => {
    setFormData(prev => ({
      ...prev,
      role_ids: prev.role_ids.includes(roleId)
        ? prev.role_ids.filter(id => id !== roleId)
        : [...prev.role_ids, roleId]
    }))
  }

  const handleToolToggle = (toolId: number) => {
    setFormData(prev => ({
      ...prev,
      tool_ids: prev.tool_ids.includes(toolId)
        ? prev.tool_ids.filter(id => id !== toolId)
        : [...prev.tool_ids, toolId]
    }))
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center gradient-primary">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    )
  }

  if (!currentUser || !isSuperUser(currentUser)) {
    return null
  }

  const menuItems = [
    { icon: Home, label: 'Dashboard', href: '/dashboard', show: true },
    { icon: Users, label: 'User Management', href: '/dashboard/users', show: isSuperUser(currentUser) },
    { icon: Settings, label: 'Settings', href: '/dashboard/settings', show: true },
  ]

  const userTools = currentUser.tools || []
  const hasSuperUserRole = formData.role_ids.some(roleId => 
    roles.find(role => role.id === roleId)?.name === 'superuser'
  )

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
                <p className="text-sm font-semibold text-gray-900">{currentUser.full_name}</p>
                <p className="text-xs text-gray-500">@{currentUser.username}</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {currentUser.roles.map((role) => (
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
          <div className="flex justify-between items-center mb-8">
            <div>
              <h2 className="text-4xl font-bold text-white mb-2">User Management</h2>
              <p className="text-white/80 text-lg">Manage users, roles, and tool assignments</p>
            </div>
            <button
              onClick={handleCreateUser}
              className="btn-primary flex items-center space-x-2 px-6 py-3 text-lg font-semibold shadow-xl"
            >
              <Plus className="h-5 w-5" />
              <span>Add New User</span>
            </button>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl shadow-lg">
              <p className="font-medium">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 text-green-700 rounded-xl shadow-lg">
              <p className="font-medium">{success}</p>
            </div>
          )}

          {/* Users Table */}
          <div className="glass-card overflow-hidden shadow-2xl">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50/50 backdrop-blur-sm">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                      Full Name
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                      Username
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                      Roles
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white/90 backdrop-blur-sm divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr 
                      key={user.id} 
                      className="hover:bg-blue-50/50 transition-colors cursor-pointer"
                      onClick={() => handleEditUser(user)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-10 h-10 gradient-blue rounded-full flex items-center justify-center">
                            <UserIcon className="h-5 w-5 text-white" />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-semibold text-gray-900">{user.full_name}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                        @{user.username}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-wrap gap-1">
                          {user.roles.map((role) => (
                            <span
                              key={role.id}
                              className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800"
                            >
                              {role.name}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                          user.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleEditUser(user)
                          }}
                          className="text-blue-600 hover:text-blue-900 flex items-center space-x-1 font-semibold"
                        >
                          <Edit className="h-4 w-4" />
                          <span>Edit</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Create/Edit User Modal */}
          {(showCreateForm || showEditForm) && (
            <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm">
              <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                <div className="inline-block align-bottom bg-white/95 backdrop-blur-md rounded-2xl text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full border border-white/20">
                  <form onSubmit={handleSubmit}>
                    <div className="px-6 pt-6 pb-4 sm:p-8 sm:pb-6">
                      <h3 className="text-2xl leading-6 font-bold text-gray-900 mb-6 text-gradient">
                        {showCreateForm ? 'Create New User' : `Edit User: ${selectedUser?.full_name}`}
                      </h3>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-semibold text-gray-700 mb-2">Full Name</label>
                          <input
                            type="text"
                            value={formData.full_name}
                            onChange={(e) => setFormData(prev => ({ ...prev, full_name: e.target.value }))}
                            className="form-input"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-semibold text-gray-700 mb-2">Username</label>
                          <input
                            type="text"
                            value={formData.username}
                            onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                            className="form-input"
                            required
                          />
                        </div>

                        <div className="md:col-span-2">
                          <label className="block text-sm font-semibold text-gray-700 mb-2">Email</label>
                          <input
                            type="email"
                            value={formData.email}
                            onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                            className="form-input"
                            required
                          />
                        </div>

                        <div className="md:col-span-2">
                          <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Password {showEditForm && '(leave blank to keep current)'}
                          </label>
                          <div className="relative">
                            <input
                              type={showPassword ? 'text' : 'password'}
                              value={formData.password}
                              onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                              className="form-input pr-12"
                              required={showCreateForm}
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600"
                            >
                              {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                            </button>
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-semibold text-gray-700 mb-3">Roles</label>
                          <div className="space-y-3 max-h-40 overflow-y-auto p-3 bg-gray-50/50 rounded-lg">
                            {roles.map((role) => (
                              <label key={role.id} className="flex items-center">
                                <input
                                  type="checkbox"
                                  checked={formData.role_ids.includes(role.id)}
                                  onChange={() => handleRoleToggle(role.id)}
                                  className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                                />
                                <span className="ml-3 text-sm font-medium text-gray-900">
                                  {role.name} {role.description && `(${role.description})`}
                                </span>
                              </label>
                            ))}
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-semibold text-gray-700 mb-3">
                            Tool Assignments {hasSuperUserRole && <span className="text-xs text-gray-500">(SuperUsers get all tools automatically)</span>}
                          </label>
                          <div className="space-y-3 max-h-40 overflow-y-auto p-3 bg-gray-50/50 rounded-lg">
                            {tools.map((tool) => (
                              <label key={tool.id} className="flex items-center">
                                <input
                                  type="checkbox"
                                  checked={formData.tool_ids.includes(tool.id)}
                                  onChange={() => handleToolToggle(tool.id)}
                                  disabled={hasSuperUserRole}
                                  className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50 disabled:opacity-50"
                                />
                                <span className="ml-3 text-sm font-medium text-gray-900">
                                  {tool.display_name} {tool.description && `(${tool.description})`}
                                </span>
                              </label>
                            ))}
                          </div>
                        </div>

                        {showEditForm && (
                          <div className="md:col-span-2">
                            <label className="flex items-center">
                              <input
                                type="checkbox"
                                checked={formData.is_active}
                                onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                              />
                              <span className="ml-3 text-sm font-semibold text-gray-900">Active User</span>
                            </label>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="bg-gray-50/50 backdrop-blur-sm px-6 py-4 sm:px-8 sm:flex sm:flex-row-reverse">
                      <button
                        type="submit"
                        className="w-full inline-flex justify-center btn-primary sm:ml-3 sm:w-auto text-base px-6 py-3"
                      >
                        {showCreateForm ? 'Create User' : 'Update User'}
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setShowCreateForm(false)
                          setShowEditForm(false)
                          resetForm()
                        }}
                        className="mt-3 w-full inline-flex justify-center btn-secondary sm:mt-0 sm:ml-3 sm:w-auto text-base px-6 py-3"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}