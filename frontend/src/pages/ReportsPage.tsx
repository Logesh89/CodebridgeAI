import { useQuery } from '@tanstack/react-query';
import {
  Typography, Card, Table, TableBody, TableCell, TableHead, TableRow, Chip, CircularProgress, Button,
} from '@mui/material';
import { Download } from '@mui/icons-material';
import { reportsApi, downloadApi } from '../services/api';
import { formatDate } from '../utils/formatters';

export default function ReportsPage() {
  const { data: reports, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportsApi.list().then((r) => r.data),
  });

  if (isLoading) return <CircularProgress />;

  return (
    <div>
      <Typography variant="h4" fontWeight={700} mb={3}>Validation Reports</Typography>
      <Card>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Pipeline ID</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="right">Download</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(reports || []).map((r: { id: string; pipeline_id: string; status: string; created_at: string }) => (
              <TableRow key={r.id}>
                <TableCell>{r.pipeline_id}</TableCell>
                <TableCell><Chip label={r.status} color={r.status === 'passed' ? 'success' : 'error'} size="small" /></TableCell>
                <TableCell>{formatDate(r.created_at)}</TableCell>
                <TableCell align="right">
                  <Button size="small" startIcon={<Download />} href={downloadApi.getUrl(r.id)} target="_blank">Report</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
