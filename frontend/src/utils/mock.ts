export const mockUser = {
  id: '1',
  name: 'Test User',
  email: 'test@example.com',
}

export const mockOrgs = [
  { id: '1', name: 'Acme Corp', description: 'Main organization', ownerId: '1' },
  { id: '2', name: 'Side Project', description: 'Personal projects', ownerId: '1' },
]

export const mockMembers = [
  { userId: '1', userName: 'Test User', userEmail: 'test@example.com', role: 'admin' },
  { userId: '2', userName: 'Jane Doe', userEmail: 'jane@example.com', role: 'member' },
]

export const mockInvitation = {
  id: '1',
  orgId: '1',
  orgName: 'Acme Corp',
  email: 'test@example.com',
  role: 'member',
}
