export interface User {
  id: string
  name: string
  email: string
  avatar: string | null
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

export interface Org {
  id: string
  name: string
  owner_id: string
  created_at: string
  updated_at: string
}

export interface OrgMember {
  id: string
  org_id: string
  user_id: string
  role: string
  joined_at: string
  user_email: string | null
  user_name: string | null
}

export interface Invitation {
  id: string
  org_id: string
  email: string
  role: string
  token: string
  expires_at: string
  status: string
  created_at: string
}

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
