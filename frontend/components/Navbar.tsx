'use client'

import { useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Image from 'next/image'
import { LogOut, User as UserIcon, Home, Users, ChevronDown } from 'lucide-react'
import { User, clearUserSession } from '@/lib/auth'

interface NavbarProps {
  user: User
}

export default function Navbar({ user }: NavbarProps) {
  const [userDropdownOpen, setUserDropdownOpen] = useState(false)
  const router = useRouter()
  const pathname = usePathname()

  const handleLogout = () => {
    clearUserSession()
    router.push('/login')
  }

  const isActive = (path: string) => {
    return pathname === path
  }

  const hasUserManagementAccess = user.roles?.some((role: any) => 
    role.name === 'superuser'
  )

  return (
    <div className="w-full bg-white shadow-md border-b border-gray-200 sticky top-0 z-50">
      <div className="flex items-center justify-between h-16 px-6">
        {/* Logo and Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 relative">
            <Image
              src="/logo.jpg"
              alt="ACI DASHBOARD"
              fill
              sizes="48px"
              className="object-contain"
            />
          </div>
          <span className="text-xl font-bold text-gray-900">ACI</span>
        </div>

        {/* Navigation Menu */}
        <nav className="flex items-center space-x-4">
          <button
            onClick={() => router.push('/dashboard')}
            className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg font-semibold transition-all duration-200 border-2 ${
              isActive('/dashboard')
                ? 'bg-blue-600 text-white shadow-lg border-blue-600 transform scale-105'
                : 'text-gray-700 hover:bg-blue-50 hover:text-blue-700 border-transparent hover:border-blue-200 hover:shadow-md active:scale-95'
            }`}
            style={{ outline: 'none', userSelect: 'none' }}
          >
            <Home className="h-5 w-5" />
            <span>Dashboard</span>
          </button>
          
          {hasUserManagementAccess && (
            <button
              onClick={() => router.push('/dashboard/users')}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg font-semibold transition-all duration-200 border-2 ${
                isActive('/dashboard/users')
                  ? 'bg-blue-600 text-white shadow-lg border-blue-600 transform scale-105'
                  : 'text-gray-700 hover:bg-blue-50 hover:text-blue-700 border-transparent hover:border-blue-200 hover:shadow-md active:scale-95'
              }`}
              style={{ outline: 'none', userSelect: 'none' }}
            >
              <Users className="h-5 w-5" />
              <span>User Management</span>
            </button>
          )}
        </nav>

        {/* User Profile Section - Right */}
        <div className="relative">
          <button
            onClick={() => setUserDropdownOpen(!userDropdownOpen)}
            className="flex items-center space-x-3 px-4 py-2.5 rounded-lg hover:bg-blue-50 hover:shadow-md transition-all duration-200 border-2 border-transparent hover:border-blue-200 active:scale-95"
            style={{ outline: 'none', userSelect: 'none' }}
          >
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
              <UserIcon className="h-4 w-4 text-white" />
            </div>
            <div className="flex items-center space-x-2">
              <div className="text-right">
                <p className="text-sm font-semibold text-gray-900">
                  {user.full_name}
                </p>
                <div className="flex flex-wrap gap-1 justify-end">
                  {user.roles?.map((role) => (
                    <span
                      key={role.id}
                      className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-medium"
                    >
                      {role.name === 'superuser' ? 'SUPER USER' : role.name.toUpperCase()}
                    </span>
                  ))}
                </div>
              </div>
              <ChevronDown 
                className={`h-4 w-4 text-gray-500 transform transition-transform duration-200 ${
                  userDropdownOpen ? 'rotate-180' : ''
                }`} 
              />
            </div>
          </button>

          {/* User Dropdown Menu */}
          {userDropdownOpen && (
            <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border-2 border-gray-100 py-3 z-50">
              <div className="px-4 py-3 border-b border-gray-200">
                <p className="text-sm font-semibold text-gray-900">{user.full_name}</p>
                <p className="text-xs text-gray-500">@{user.username}</p>
              </div>
              <button
                onClick={() => {
                  setUserDropdownOpen(false)
                  router.push('/dashboard/profile')
                }}
                className="w-full text-left px-4 py-3 text-sm font-semibold text-gray-700 hover:bg-blue-50 hover:text-blue-700 transition-all duration-200 border-l-4 border-transparent hover:border-blue-500 active:scale-95"
                style={{ outline: 'none', userSelect: 'none' }}
              >
                <div className="flex items-center space-x-2">
                  <UserIcon className="h-4 w-4" />
                  <span>View Profile</span>
                </div>
              </button>
              <button
                onClick={() => {
                  setUserDropdownOpen(false)
                  router.push('/reset-password')
                }}
                className="w-full text-left px-4 py-3 text-sm font-semibold text-gray-700 hover:bg-orange-50 hover:text-orange-700 transition-all duration-200 border-l-4 border-transparent hover:border-orange-500 active:scale-95"
                style={{ outline: 'none', userSelect: 'none' }}
              >
                <div className="flex items-center space-x-2">
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m0 0a2 2 0 012 2m-2-2v6a2 2 0 01-2 2H9a2 2 0 01-2-2V9a2 2 0 012-2m0 0V7a2 2 0 012-2m-2 2h4m-4 0h4" />
                  </svg>
                  <span>Reset Password</span>
                </div>
              </button>
              <div className="border-t border-gray-200 mt-2 pt-2">
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-3 text-sm font-semibold text-red-600 hover:bg-red-50 hover:text-red-700 transition-all duration-200 flex items-center space-x-2 border-l-4 border-transparent hover:border-red-500 active:scale-95"
                  style={{ outline: 'none', userSelect: 'none' }}
                >
                  <LogOut className="h-4 w-4" />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}