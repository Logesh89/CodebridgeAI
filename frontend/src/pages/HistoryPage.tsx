import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, Card, Table, TableBody, TableCell, TableHead, TableRow,
  Chip, IconButton, CircularProgress, Alert
} from '@mui/material';
import { Visibility, History } from '@mui/icons-material';
import { pipelineApi } from '../services/api';
import { formatDate } from '../utils/formatters';

const statusColors: Record<string, 'default' | 'primary' | 'success' | 'error' | 'warning' | 'info'> = {
  pending: 'default', queued: 'info', running: 'primary', converting: 'warning',
  executing: 'warning', validating: 'info', completed: 'success', failed: 'error',
};

export default function HistoryPage() {
  const navigate = useNavigate();
  const { data: pipelines, isLoading } = useQuery({
    queryKey: ['pipelines-history'],
    queryFn: () => pipelineApi.list().then((r) => r.data),
  });

  if (isLoading) {
    return <Box display="flex" justifyContent="center" p={8}><CircularProgress /></Box>;
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={1.5} mb={3}>
        <History color="primary" sx={{ fontSize: 36 }} />
        <Typography variant="h4" fontWeight={700}>Pipeline Conversion History</Typography>
      </Box>

      {(!pipelines || pipelines.length === 0) ? (
        <Alert severity="info">No conversion execution history recorded yet.</Alert>
      ) : (
        <Card>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Pipeline Name</TableCell>
                <TableCell>Pipeline Path</TableCell>
                <TableCell>Project</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Generated Python File</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell align="right">View</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {pipelines.map((p: {
                id: string;
                name: string;
                path: string;
                project?: string;
                status: string;
                python_file_path?: string;
                updated_at: string;
              }) => (
                <TableRow key={p.id} hover>
                  <TableCell sx={{ fontWeight: 600 }}>{p.name}</TableCell>
                  <TableCell sx={{ maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.path}</TableCell>
                  <TableCell>{p.project || '-'}</TableCell>
                  <TableCell>
                    <Chip label={p.status} color={statusColors[p.status] || 'default'} size="small" />
                  </TableCell>
                  <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {p.python_file_path || 'Pending'}
                  </TableCell>
                  <TableCell>{formatDate(p.updated_at)}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" color="primary" onClick={() => navigate(`/pipelines/${p.id}`)}>
                      <Visibility />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}
    </Box>
  );
}
