import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box, Typography, Card, CardContent, Grid, Table, TableBody, TableCell,
  TableHead, TableRow, Chip, Button, Select, MenuItem, FormControl, InputLabel,
  Avatar, CircularProgress, Alert, IconButton, Tooltip, Dialog, DialogTitle,
  DialogContent, DialogActions, Stack, Switch, FormControlLabel
} from '@mui/material';
import {
  AdminPanelSettings, Security, SupervisorAccount, Storage, VpnKey,
  Visibility, Edit, Delete, Person
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { dashboardApi, userApi } from '../services/api';
import { formatDate } from '../utils/formatters';

interface UserRecord {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  last_login?: string;
  created_at: string;
}

export default function AdminPanelPage() {
  const { user: currentUser } = useAuth();
  const queryClient = useQueryClient();
  const [roleFilter, setRoleFilter] = useState('');

  // Dialog States
  const [viewUser, setViewUser] = useState<UserRecord | null>(null);
  const [editUser, setEditUser] = useState<UserRecord | null>(null);
  const [deleteUser, setDeleteUser] = useState<UserRecord | null>(null);
  const [editRoleValue, setEditRoleValue] = useState<string>('developer');
  const [editIsActive, setEditIsActive] = useState<boolean>(true);

  const isAdmin = currentUser?.role?.toLowerCase() === 'admin';

  // Fetch Dashboard System Metrics
  const { data: dashboardData } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardApi.getDashboard().then((r) => r.data),
  });

  // Fetch Real Registered Users from Database
  const { data: realUsers, isLoading: usersLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => userApi.list().then((r) => r.data as UserRecord[]),
    enabled: isAdmin,
    refetchInterval: 4000,
  });

  // Role Update Mutation
  const updateRoleMutation = useMutation({
    mutationFn: ({ userId, role, isActive }: { userId: string; role: string; isActive: boolean }) =>
      userApi.updateRole(userId, role, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setEditUser(null);
    },
  });

  // Delete User Mutation
  const deleteUserMutation = useMutation({
    mutationFn: (userId: string) => userApi.delete(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setDeleteUser(null);
    },
  });

  if (!isAdmin) {
    return (
      <Box p={4}>
        <Alert severity="warning" icon={<Security />}>
          Access Denied: Only Admin users can view and manage system administration settings.
        </Alert>
      </Box>
    );
  }

  const handleOpenEdit = (u: UserRecord) => {
    setEditUser(u);
    setEditRoleValue(u.role.toLowerCase());
    setEditIsActive(u.is_active);
  };

  const handleSaveEdit = () => {
    if (!editUser) return;
    updateRoleMutation.mutate({
      userId: editUser.id,
      role: editRoleValue.toUpperCase(),
      isActive: editIsActive,
    });
  };

  const handleConfirmDelete = () => {
    if (!deleteUser) return;
    deleteUserMutation.mutate(deleteUser.id);
  };

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={1.5} mb={3}>
        <AdminPanelSettings color="primary" sx={{ fontSize: 36 }} />
        <Typography variant="h4" fontWeight={700}>System Administration</Typography>
      </Box>

      {/* System Status Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary">Total Registered Users</Typography>
                  <Typography variant="h4" fontWeight={700} mt={1}>
                    {realUsers ? realUsers.length : 0} Users
                  </Typography>
                </Box>
                <SupervisorAccount color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary">Airflow Health</Typography>
                  <Typography variant="h4" fontWeight={700} mt={1} color="success.main">
                    {dashboardData?.airflow_status?.status || 'Active'}
                  </Typography>
                </Box>
                <Storage color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary">Datadog APM</Typography>
                  <Typography variant="h4" fontWeight={700} mt={1} color="info.main">
                    {dashboardData?.datadog_status?.status || 'Connected'}
                  </Typography>
                </Box>
                <VpnKey color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* User Role Management Table */}
      <Card sx={{ mb: 4, borderRadius: 3, boxShadow: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" fontWeight={700}>User Role Management</Typography>
            <FormControl size="small" sx={{ minWidth: 160 }}>
              <InputLabel>Filter Role</InputLabel>
              <Select
                value={roleFilter}
                label="Filter Role"
                onChange={(e) => setRoleFilter(e.target.value)}
              >
                <MenuItem value="">All Roles</MenuItem>
                <MenuItem value="admin">Admin</MenuItem>
                <MenuItem value="developer">Developer</MenuItem>
                <MenuItem value="viewer">Viewer</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {usersLoading ? (
            <Box display="flex" justifyContent="center" p={6}><CircularProgress /></Box>
          ) : (
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 700 }}>User</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Email Address</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Current Role</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Last Activity</TableCell>
                  <TableCell align="center" sx={{ fontWeight: 700 }}>Actions (View / Edit / Delete)</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(realUsers || [])
                  .filter((u) => !roleFilter || u.role.toLowerCase() === roleFilter.toLowerCase())
                  .map((u) => (
                    <TableRow key={u.id} hover>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1.5}>
                          <Avatar sx={{ width: 34, height: 34, bgcolor: u.role.toLowerCase() === 'admin' ? 'primary.main' : 'info.main' }}>
                            {u.full_name ? u.full_name[0].toUpperCase() : u.email[0].toUpperCase()}
                          </Avatar>
                          <Box>
                            <Typography fontWeight={600}>{u.full_name || u.email.split('@')[0]}</Typography>
                            <Typography variant="caption" color="text.secondary">ID: {u.id.substring(0, 8)}...</Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>{u.email}</TableCell>
                      <TableCell>
                        <Chip
                          label={u.role.toUpperCase()}
                          size="small"
                          color={u.role.toLowerCase() === 'admin' ? 'primary' : u.role.toLowerCase() === 'developer' ? 'info' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={u.is_active ? 'Active' : 'Disabled'}
                          size="small"
                          color={u.is_active ? 'success' : 'error'}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{formatDate(u.last_login || u.created_at)}</TableCell>
                      <TableCell align="center">
                        <Stack direction="row" spacing={1} justifyContent="center">
                          {/* VIEW ACTION */}
                          <Tooltip title="View User Details">
                            <IconButton size="small" color="info" onClick={() => setViewUser(u)}>
                              <Visibility fontSize="small" />
                            </IconButton>
                          </Tooltip>

                          {/* EDIT ACTION */}
                          <Tooltip title="Edit Role & Permissions">
                            <IconButton size="small" color="primary" onClick={() => handleOpenEdit(u)}>
                              <Edit fontSize="small" />
                            </IconButton>
                          </Tooltip>

                          {/* DELETE ACTION */}
                          <Tooltip title="Delete User">
                            <IconButton
                              size="small"
                              color="error"
                              disabled={u.id === currentUser?.id}
                              onClick={() => setDeleteUser(u)}
                            >
                              <Delete fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* 1. VIEW USER DIALOG */}
      <Dialog open={!!viewUser} onClose={() => setViewUser(null)} maxWidth="xs" fullWidth>
        <DialogTitle display="flex" alignItems="center" gap={1}>
          <Person color="primary" /> User Details
        </DialogTitle>
        <DialogContent dividers>
          {viewUser && (
            <Stack spacing={1.5}>
              <Box><Typography variant="caption" color="text.secondary">User ID</Typography><Typography variant="body2" fontWeight={600}>{viewUser.id}</Typography></Box>
              <Box><Typography variant="caption" color="text.secondary">Email Address</Typography><Typography variant="body2" fontWeight={600}>{viewUser.email}</Typography></Box>
              <Box><Typography variant="caption" color="text.secondary">Current Role</Typography><Typography variant="body2" fontWeight={600}>{viewUser.role.toUpperCase()}</Typography></Box>
              <Box><Typography variant="caption" color="text.secondary">Account Status</Typography><Typography variant="body2" fontWeight={600}>{viewUser.is_active ? 'Active' : 'Disabled'}</Typography></Box>
              <Box><Typography variant="caption" color="text.secondary">Registered Date</Typography><Typography variant="body2">{formatDate(viewUser.created_at)}</Typography></Box>
              <Box><Typography variant="caption" color="text.secondary">Last Login Activity</Typography><Typography variant="body2">{formatDate(viewUser.last_login)}</Typography></Box>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewUser(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* 2. EDIT USER ROLE DIALOG */}
      <Dialog open={!!editUser} onClose={() => setEditUser(null)} maxWidth="xs" fullWidth>
        <DialogTitle display="flex" alignItems="center" gap={1}>
          <Edit color="primary" /> Edit User Role
        </DialogTitle>
        <DialogContent dividers>
          {editUser && (
            <Stack spacing={2} pt={1}>
              <Typography variant="body2">Updating role for <strong>{editUser.email}</strong></Typography>
              <FormControl fullWidth size="small">
                <InputLabel>Role</InputLabel>
                <Select
                  value={editRoleValue}
                  label="Role"
                  onChange={(e) => setEditRoleValue(e.target.value)}
                >
                  <MenuItem value="admin">ADMIN</MenuItem>
                  <MenuItem value="developer">DEVELOPER</MenuItem>
                  <MenuItem value="viewer">VIEWER</MenuItem>
                </Select>
              </FormControl>
              <FormControlLabel
                control={<Switch checked={editIsActive} onChange={(e) => setEditIsActive(e.target.checked)} />}
                label="Account Active Status"
              />
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditUser(null)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveEdit} disabled={updateRoleMutation.isPending}>
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>

      {/* 3. DELETE USER DIALOG */}
      <Dialog open={!!deleteUser} onClose={() => setDeleteUser(null)} maxWidth="xs" fullWidth>
        <DialogTitle display="flex" alignItems="center" gap={1} color="error.main">
          <Delete color="error" /> Delete User Account
        </DialogTitle>
        <DialogContent dividers>
          {deleteUser && (
            <Typography variant="body2">
              Are you sure you want to permanently delete user <strong>{deleteUser.email}</strong>? This action cannot be undone.
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteUser(null)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleConfirmDelete} disabled={deleteUserMutation.isPending}>
            Delete User
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
