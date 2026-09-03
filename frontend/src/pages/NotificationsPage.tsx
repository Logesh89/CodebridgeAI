import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Typography, Card, List, ListItem, ListItemText, IconButton, Chip, CircularProgress,
} from '@mui/material';
import { MarkEmailRead } from '@mui/icons-material';
import { notificationsApi } from '../services/api';

import { formatDate } from '../utils/formatters';

export default function NotificationsPage() {
  const queryClient = useQueryClient();
  const { data: notifications, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.list().then((r) => r.data),
    refetchInterval: 5000,
  });

  const markRead = useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  });

  if (isLoading) return <CircularProgress />;

  return (
    <div>
      <Typography variant="h4" fontWeight={700} mb={3}>Notifications</Typography>
      <Card>
        <List>
          {(notifications || []).map((n: { id: string; title: string; message: string; notification_type: string; is_read: boolean; created_at: string }) => (
            <ListItem
              key={n.id}
              secondaryAction={
                !n.is_read && (
                  <IconButton onClick={() => markRead.mutate(n.id)}><MarkEmailRead /></IconButton>
                )
              }
            >
              <ListItemText
                primary={<>{n.title} {!n.is_read && <Chip label="New" size="small" color="primary" sx={{ ml: 1 }} />}</>}
                secondary={`${n.message} — ${formatDate(n.created_at)}`}
              />
            </ListItem>
          ))}
        </List>
      </Card>
    </div>
  );
}
