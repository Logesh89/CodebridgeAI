import { useQuery } from '@tanstack/react-query';
import {
  Typography, Card, Table, TableBody, TableCell, TableHead, TableRow, Chip, CircularProgress,
} from '@mui/material';
import { logsApi } from '../services/api';
import { formatDate } from '../utils/formatters';

const levelColors: Record<string, 'default' | 'error' | 'warning' | 'info'> = {
  ERROR: 'error', WARNING: 'warning', INFO: 'info', DEBUG: 'default',
};

export default function LogsPage() {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['logs'],
    queryFn: () => logsApi.list().then((r) => r.data),
    refetchInterval: 15000,
  });

  if (isLoading) return <CircularProgress />;

  return (
    <div>
      <Typography variant="h4" fontWeight={700} mb={3}>System Logs</Typography>
      <Card>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Level</TableCell>
              <TableCell>Module</TableCell>
              <TableCell>Message</TableCell>
              <TableCell>Time</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(logs || []).map((log: { id: string; level: string; module: string; message: string; created_at: string }) => (
              <TableRow key={log.id}>
                <TableCell><Chip label={log.level} color={levelColors[log.level] || 'default'} size="small" /></TableCell>
                <TableCell>{log.module}</TableCell>
                <TableCell sx={{ maxWidth: 400, overflow: 'hidden', textOverflow: 'ellipsis' }}>{log.message}</TableCell>
                <TableCell>{formatDate(log.created_at)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
