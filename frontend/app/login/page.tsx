'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Eye, EyeOff, Shield, Lock, Mail } from 'lucide-react'
import Image from 'next/image'
import { loginUser } from '@/lib/auth'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const response = await loginUser(username, password)
      localStorage.setItem('accessToken', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen gradient-primary flex items-center justify-center p-4">
      <div className="glass-card w-full max-w-md p-8 space-y-8 shadow-2xl">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 relative p-2 bg-white rounded-2xl shadow-lg">
              <Image
                src="/logo.jpg"
                alt="ACI DASHBOARD"
                fill
                className="object-contain rounded-lg"
                priority
              />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gradient mb-3">ACI DASHBOARD</h1>
          <p className="text-gray-600 text-lg font-medium">Enterprise Access Portal</p>
          <div className="flex items-center justify-center space-x-2 mt-3">
            <Shield className="h-4 w-4 text-blue-600" />
            <span className="text-sm text-gray-500">Secure Authentication Required</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-semibold text-gray-700 mb-3">
              Username
            </label>
            <div className="relative">
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="form-input pl-12"
                placeholder="Enter your username"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Mail className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-3">
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="form-input pl-12 pr-12"
                placeholder="Enter your password"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center bg-red-50/80 backdrop-blur-sm p-3 rounded-lg border border-red-200/50 shadow-sm">
              <p className="font-medium">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full btn-primary text-lg py-4 font-semibold shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {isLoading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Authenticating...</span>
              </div>
            ) : (
              'Sign In to Dashboard'
            )}
          </button>
        </form>

        <div className="text-center space-y-4">
          <div className="border-t border-gray-200/50 pt-4">
            <p className="text-xs text-gray-500 mb-3">Need assistance?</p>
            <div className="flex justify-center space-x-6">
              <button className="text-blue-600 hover:text-blue-700 text-sm font-medium transition duration-200 hover:underline">
                Forgot Password?
              </button>
              <button className="text-blue-600 hover:text-blue-700 text-sm font-medium transition duration-200 hover:underline">
                Reset Password
              </button>
            </div>
          </div>
        </div>

        {/* Demo Credentials */}
        <div className="bg-blue-50/80 backdrop-blur-sm p-4 rounded-lg border border-blue-200/50">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">Demo Accounts:</h4>
          <div className="space-y-1 text-xs text-blue-800">
            <p><strong>SuperUser:</strong> tony967 / AhFnrAASWN0a</p>
            <p><strong>Manager:</strong> max463 / CCiYxAAxyR0z</p>
            <p><strong>User (Compare Tool Only):</strong> pratiksha649 / hUDcvxtL26I9</p>
          </div>
        </div>
      </div>
    </div>
  )
}