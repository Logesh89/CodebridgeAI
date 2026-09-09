import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box, Drawer, AppBar, Toolbar, Typography, List, ListItemButton,
  ListItemIcon, ListItemText, IconButton, Avatar, Divider, Badge,
} from '@mui/material';
import {
  Dashboard, CloudUpload, AccountTree, History, Assessment,
  Description, Download, Settings, Notifications, AdminPanelSettings,
  Menu as MenuIcon, Brightness4, Brightness7, Logout, Person, Code,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';
import { useAppTheme } from '../contexts/ThemeContext';
import { notificationsApi } from '../services/api';

const DRAWER_WIDTH = 260;

const menuItems = [
  { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
  { text: 'Code Interpreter', icon: <Code />, path: '/interpreter' },
  { text: 'Upload', icon: <CloudUpload />, path: '/upload' },
  { text: 'Pipelines', icon: <AccountTree />, path: '/pipelines' },
  { text: 'History', icon: <History />, path: '/history' },
  { text: 'Reports', icon: <Assessment />, path: '/reports' },
  { text: 'Logs', icon: <Description />, path: '/logs' },
  { text: 'Downloads', icon: <Download />, path: '/downloads' },
  { text: 'Notifications', icon: <Notifications />, path: '/notifications' },
  { text: 'Settings', icon: <Settings />, path: '/settings' },
  { text: 'Admin Panel', icon: <AdminPanelSettings />, path: '/admin' },
];

export default function MainLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const { darkMode, toggleTheme } = useAppTheme();

  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.list().then((r) => r.data).catch(() => []),
    refetchInterval: 10000,
  });

  const notificationsList = Array.isArray(notifications)
    ? notifications
    : (Array.isArray((notifications as any)?.items) ? (notifications as any).items : []);

  const unreadCount = notificationsList.filter((n: { is_read?: boolean }) => !n.is_read).length;
  const isAdmin = user?.role?.toLowerCase() === 'admin';
  const visibleMenuItems = menuItems.filter((item) => item.path !== '/admin' || isAdmin);

  const drawer = (
    <Box>
      <Toolbar sx={{ px: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Box
          component="img"
          src="/itc_infotech_logo.png"
          alt="ITC Infotech Logo"
          sx={{
            height: 34,
            objectFit: 'contain',
            bgcolor: '#ffffff',
            p: 0.5,
            borderRadius: 1,
            boxShadow: 1,
          }}
        />
        <Typography variant="h6" noWrap fontWeight={800} color="primary" sx={{ letterSpacing: 0.5 }}>
          CodeBridge AI
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {visibleMenuItems.map((item) => (
          <ListItemButton
            key={item.text}
            selected={location.pathname === item.path}
            onClick={() => navigate(item.path)}
            sx={{ mx: 1, borderRadius: 1, mb: 0.5 }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItemButton>
        ))}
      </List>
      <Divider />
      <List>
        <ListItemButton onClick={() => navigate('/profile')} sx={{ mx: 1, borderRadius: 1 }}>
          <ListItemIcon><Person /></ListItemIcon>
          <ListItemText primary="Profile" />
        </ListItemButton>
        <ListItemButton onClick={logout} sx={{ mx: 1, borderRadius: 1 }}>
          <ListItemIcon><Logout /></ListItemIcon>
          <ListItemText primary="Logout" />
        </ListItemButton>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (t) => t.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setMobileOpen(!mobileOpen)}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Box sx={{ flexGrow: 1 }} />
          <IconButton color="inherit" onClick={toggleTheme}>
            {darkMode ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
          <IconButton color="inherit" onClick={() => navigate('/notifications')}>
            <Badge badgeContent={unreadCount} color="error">
              <Notifications />
            </Badge>
          </IconButton>
          <IconButton onClick={() => navigate('/profile')} sx={{ ml: 1 }}>
            <Avatar sx={{ bgcolor: 'secondary.main', width: 36, height: 36 }}>
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </Avatar>
          </IconButton>
        </Toolbar>
      </AppBar>
      <Box component="nav" sx={{ width: { sm: DRAWER_WIDTH }, flexShrink: { sm: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{ display: { xs: 'block', sm: 'none' }, '& .MuiDrawer-paper': { width: DRAWER_WIDTH } }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{ display: { xs: 'none', sm: 'block' }, '& .MuiDrawer-paper': { width: DRAWER_WIDTH } }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          mt: 8,
          minHeight: '100vh',
          bgcolor: 'background.default',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}
