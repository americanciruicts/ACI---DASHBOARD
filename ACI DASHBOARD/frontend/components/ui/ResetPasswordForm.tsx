'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { Key, Eye, EyeOff, Check, AlertCircle } from 'lucide-react'

export default function ResetPasswordForm() {
  // Your entire ResetPasswordPage code goes here, **exactly as you wrote it**,
  // but change the component name to ResetPasswordForm.

  // ...rest of your code without any changes except name...
  // e.g.:

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [token, setToken] = useState('')
  const [validationErrors, setValidationErrors] = useState<string[]>([])

  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    const tokenParam = searchParams.get('token')
    if (!tokenParam) {
      setError('Invalid reset link. Please request a new password reset.')
    } else {
      setToken(tokenParam)
    }
  }, [searchParams])

  const validatePassword = (password: string): string[] => {
    const errors: string[] = []
    
    if (password.length < 12) {
      errors.push('Password must be at least 12 characters long')
    }
    
    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter')
    }
    
    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter')
    }
    
    if (!/\d/.test(password)) {
      errors.push('Password must contain at least one number')
    }
    
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('Password must contain at least one special character')
    }
    
    return errors
  }

  const handlePasswordChange = (newPassword: string) => {
    setPassword(newPassword)
    setValidationErrors(validatePassword(newPassword))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!token) {
      setError('Invalid reset link')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    const passwordErrors = validatePassword(password)
    if (passwordErrors.length > 0) {
      setError('Please fix the password requirements below')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await fetch('/api/v1/users/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          token,
          new_password: password
        })
      })

      if (response.ok) {
        setSuccess(true)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to reset password')
      }
    } catch (error) {
      setError('Network error occurred. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Check className="h-10 w-10 text-green-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Password Reset Successful!</h1>
            <p className="text-gray-600 mb-6">
              Your password has been successfully reset. You can now log in with your new password.
            </p>
            <Link
              href="/login"
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium inline-block text-center"
            >
              Go to Login
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <div className="w-32 h-32 relative p-3 bg-white rounded-2xl shadow-lg ring-4 ring-blue-100 mx-auto mb-6">
            <Image 
              src="/logo.jpg" 
              alt="ACI DASHBOARD" 
              fill 
              sizes="(max-width: 1024px) 128px, 128px"
              className="object-contain"
            />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Reset Your Password</h1>
          <p className="text-gray-600">
            Enter your new password below to complete the reset process.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              New Password
            </label>
            <div className="relative">
              <Key className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => handlePasswordChange(e.target.value)}
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your new password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
            
            {/* Password Requirements */}
            {password && (
              <div className="mt-3 space-y-2">
                <p className="text-sm font-medium text-gray-700">Password Requirements:</p>
                <div className="space-y-1">
                  {[
                    { requirement: 'At least 12 characters', test: password.length >= 12 },
                    { requirement: 'One uppercase letter', test: /[A-Z]/.test(password) },
                    { requirement: 'One lowercase letter', test: /[a-z]/.test(password) },
                    { requirement: 'One number', test: /\d/.test(password) },
                    { requirement: 'One special character', test: /[!@#$%^&*(),.?":{}|<>]/.test(password) }
                  ].map((item, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${item.test ? 'bg-green-500' : 'bg-gray-300'}`} />
                      <span className={`text-sm ${item.test ? 'text-green-600' : 'text-gray-500'}`}>
                        {item.requirement}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
              Confirm New Password
            </label>
            <div className="relative">
              <Key className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                id="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Confirm your new password"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
            
            {confirmPassword && password !== confirmPassword && (
              <p className="mt-2 text-sm text-red-600">Passwords do not match</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading || !token || validationErrors.length > 0 || password !== confirmPassword}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Resetting Password...' : 'Reset Password'}
          </button>

          <div className="text-center">
            <Link
              href="/login"
              className="text-blue-600 hover:text-blue-700 transition-colors font-medium"
            >
              Back to Login
            </Link>
          </div>
        </form>

        <div className="mt-8 pt-6 border-t border-gray-200 text-center">
          <p className="text-sm text-gray-500">
            Need help?{' '}
            <Link href="/forgot-password" className="text-blue-600 hover:text-blue-700 font-medium">
              Request new reset link
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}