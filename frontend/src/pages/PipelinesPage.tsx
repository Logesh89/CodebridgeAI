import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, Table, TableBody, TableCell, TableHead, TableRow,
  Chip, IconButton, CircularProgress, Card, TextField, MenuItem,
} from '@mui/material';
import { Visibility, Transform } from '@mui/icons-material';
import { pipelineApi } from '../services/api';
import { formatDate } from '../utils/formatters';

const statusColors: Record<string, 'default' | 'primary' | 'success' | 'error' | 'warning' | 'info'> = {
  pending: 'default', queued: 'info', running: 'primary', converting: 'warning',
  executing: 'warning', validating: 'info', completed: 'success', failed: 'error',
};

export default function PipelinesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState('');

  const { data: pipelines, isLoading } = useQuery({
    queryKey: ['pipelines', statusFilter],
    queryFn: () => pipelineApi.list({ status: statusFilter || undefined }).then((r) => r.data),
    refetchInterval: 3000,
  });

  const convertMutation = useMutation({
    mutationFn: (id: string) => pipelineApi.convert(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['pipelines'] }),
  });

  if (isLoading) return <CircularProgress />;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight={700}>Pipelines</Typography>
        <TextField select size="small" label="Status" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} sx={{ minWidth: 150 }}>
          <MenuItem value="">All</MenuItem>
          {['pending', 'queued', 'running', 'completed', 'failed'].map((s) => (
            <MenuItem key={s} value={s}>{s}</MenuItem>
          ))}
        </TextField>
      </Box>

      <Card>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Path</TableCell>
              <TableCell>Project</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(pipelines || []).map((p: { id: string; name: string; path: string; project?: string; status: string; created_at: string }) => (
              <TableRow key={p.id} hover>
                <TableCell>
                  <Typography
                    fontWeight={600}
                    color="primary.main"
                    sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                    onClick={() => navigate(`/pipelines/${p.id}`)}
                  >
                    {p.name}
                  </Typography>
                </TableCell>
                <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.path}</TableCell>
                <TableCell>{p.project || '-'}</TableCell>
                <TableCell><Chip label={p.status} color={statusColors[p.status] || 'default'} size="small" /></TableCell>
                <TableCell>{formatDate(p.created_at)}</TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => navigate(`/pipelines/${p.id}`)}><Visibility /></IconButton>
                  <IconButton size="small" onClick={() => convertMutation.mutate(p.id)} disabled={convertMutation.isPending}>
                    <Transform />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </Box>
  );
}
