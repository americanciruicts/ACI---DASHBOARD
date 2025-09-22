const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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
    },
  })

  if (!response.ok) {
    throw new Error('Failed to get users')
  }

  return response.json()
}

export async function getAllRoles(token: string): Promise<Role[]> {
  const response = await fetch(`${API_BASE_URL}/api/roles`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Failed to get roles')
  }

  return response.json()
}

export async function getAllTools(token: string): Promise<Tool[]> {
  const response = await fetch(`${API_BASE_URL}/api/tools`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Failed to get tools')
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