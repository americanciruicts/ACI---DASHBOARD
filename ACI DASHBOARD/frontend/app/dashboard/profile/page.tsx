'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { User, clearUserSession } from '@/lib/auth'
import Navbar from '@/components/Navbar'

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('accessToken')
    const userData = localStorage.getItem('user')

    if (!token || !userData) {
      router.push('/login')
      return
    }

    try {
      const parsedUser = JSON.parse(userData)
      setUser(parsedUser)
    } catch (err) {
      clearUserSession()
      router.push('/login')
    }
    
    setIsLoading(false)
  }, [router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} />
      
      <main className="p-6 lg:p-8 bg-white min-h-screen">
        <div className="mb-8">
          <h2 className="text-4xl font-bold text-gray-900 mb-2">User Profile</h2>
          <p className="text-gray-600 text-lg">View and manage your account information</p>
        </div>

        {/* User Information */}
        <div className="glass-card p-6 max-w-4xl">
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
          </div>
        </div>
      </main>
    </div>
  )
}