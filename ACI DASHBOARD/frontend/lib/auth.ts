// Use server IP for network access from all PCs
const API_BASE_URL = 'http://192.168.1.95:2005'

// Security configuration for ACI Standards compliance
const SECURITY_CONFIG = {
  TOKEN_EXPIRY_BUFFER: 5 * 60 * 1000, // 5 minutes before expiry
  MAX_LOGIN_ATTEMPTS: 100,
  LOGIN_ATTEMPT_WINDOW: 15 * 60 * 1000, // 15 minutes
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30 minutes
}

// Security utilities
class SecurityUtils {
  static sanitizeInput(input: string): string {
    // Remove potentially dangerous characters
    return input.replace(/[<>\"';\\]/g, '').trim()
  }

  static isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const expirationTime = payload.exp * 1000
      return Date.now() > (expirationTime - SECURITY_CONFIG.TOKEN_EXPIRY_BUFFER)
    } catch {
      return true
    }
  }

  static validateEmail(email: string): boolean {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    return emailRegex.test(email) && email.length <= 254
  }

  static logSecurityEvent(event: string, details?: any) {
    console.log(`SECURITY_EVENT: ${event}`, details)
    // In production, this should send to a security monitoring system
  }
}

// Debug function to test API connectivity
export async function testApiConnection(): Promise<{ success: boolean, url: string, error?: string }> {
  const url = `${API_BASE_URL}/health`
  try {
    const response = await fetch(url)
    return { 
      success: response.ok, 
      url,
      error: response.ok ? undefined : `${response.status} ${response.statusText}`
    }
  } catch (error: any) {
    return { success: false, url, error: error.message }
  }
}

export interface Role {
  id: number
  name: string
  description?: string
}

export interface Tool {
  id: number
  name: string
  display_name: string
  description?: string
  route: string
  icon: string
  is_active: boolean
}

export interface User {
  id: number
  full_name: string
  username: string
  email: string
  password?: string  // Optional for display purposes only
  is_active: boolean
  roles: Role[]
  tools: Tool[]
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface UserCreate {
  full_name: string
  username: string
  email: string
  password: string
  role_ids: number[]
  tool_ids?: number[]
}

export interface UserUpdate {
  full_name?: string
  username?: string
  email?: string
  password?: string
  role_ids?: number[]
  tool_ids?: number[]
  is_active?: boolean
}

export async function loginUser(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Login failed')
  }

  return response.json()
}

export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Failed to get user information')
  }

  return response.json()
}

export async function getAllUsers(token: string): Promise<User[]> {
  const response = await fetch(`${API_BASE_URL}/api/users`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Failed to get users: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

export async function getAllRoles(token: string): Promise<Role[]> {
  const response = await fetch(`${API_BASE_URL}/api/roles`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Failed to get roles: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

export async function getAllTools(token: string): Promise<Tool[]> {
  const response = await fetch(`${API_BASE_URL}/api/tools`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Failed to get tools: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

export async function createUser(token: string, userData: UserCreate): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/users`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(userData),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create user')
  }

  return response.json()
}

export async function updateUser(token: string, userId: number, userData: UserUpdate): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(userData),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update user')
  }

  return response.json()
}

export function hasRole(user: User, roleName: string): boolean {
  return user.roles.some(role => role.name === roleName)
}

export function isSuperUser(user: User): boolean {
  return hasRole(user, 'superuser')
}

export function validatePasswordStrength(password: string): { isValid: boolean; errors: string[] } {
  const errors: string[] = []
  
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long')
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
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

export async function resetPasswordWithCurrentPassword(username: string, currentPassword: string, newPassword: string): Promise<{message: string}> {
  try {
    // First authenticate the user to get their token
    const loginResponse = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username,
        password: currentPassword
      }),
    })

    if (!loginResponse.ok) {
      throw new Error('Invalid username or current password')
    }

    const loginData = await loginResponse.json()
    const token = loginData.access_token
    const userId = loginData.user.id

    // Now update the user's password
    const updateResponse = await fetch(`${API_BASE_URL}/api/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        password: newPassword
      }),
    })

    if (!updateResponse.ok) {
      const error = await updateResponse.json()
      throw new Error(error.detail || 'Failed to reset password')
    }

    return { message: 'Password reset successfully' }
  } catch (error: any) {
    throw new Error(error.message || 'Failed to reset password')
  }
}

export async function deleteUser(token: string, userId: number): Promise<{message: string}> {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete user')
  }

  return response.json()
}

export function clearUserSession(): void {
  // Clear all localStorage items related to user session
  localStorage.removeItem('accessToken')
  localStorage.removeItem('user')
  localStorage.removeItem('userSettings')
  
  // Clear any other potential session items
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('lastLogin')
  localStorage.removeItem('currentUser')
  
  // Clear sessionStorage completely
  if (typeof window !== 'undefined') {
    sessionStorage.clear()
    
    // Force a small delay to ensure cleanup is complete
    setTimeout(() => {
      console.log('Session cleared completely')
    }, 100)
  }
}

export function validateSession(): { isValid: boolean, user: User | null, token: string | null } {
  try {
    const token = localStorage.getItem('accessToken')
    const userData = localStorage.getItem('user')
    const lastLogin = localStorage.getItem('lastLogin')
    
    if (!token || !userData) {
      return { isValid: false, user: null, token: null }
    }
    
    const user = JSON.parse(userData)
    const loginTime = lastLogin ? new Date(lastLogin) : null
    const now = new Date()
    
    // Check if session is older than 30 minutes (token expiry)
    if (loginTime && (now.getTime() - loginTime.getTime()) > 30 * 60 * 1000) {
      console.warn('Session may have expired')
      return { isValid: false, user: null, token: null }
    }
    
    return { isValid: true, user, token }
  } catch (error) {
    console.error('Session validation failed:', error)
    return { isValid: false, user: null, token: null }
  }
}