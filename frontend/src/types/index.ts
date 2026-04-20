export interface User {
  id: string
  name: string
  email: string
  createdAt?: string
}

export interface Org {
  id: string
  name: string
  description?: string
  ownerId: string
  createdAt?: string
}

export interface OrgMember {
  userId: string
  userName: string
  userEmail: string
  role: string
  joinedAt?: string
}
