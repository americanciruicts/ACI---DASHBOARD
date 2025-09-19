export interface User {
  id: number
  full_name: string
  username: string
  email: string
  is_active: boolean
  roles: Role[]
  tools: Tool[]
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

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface ApiError {
  detail: string
  message?: string
}

export interface PasswordResetRequest {
  username: string
}

export interface ResetPasswordRequest {
  username: string
  new_password: string
}