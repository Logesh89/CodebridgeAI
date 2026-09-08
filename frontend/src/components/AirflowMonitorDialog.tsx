import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, Box,
  Chip, Grid, Card, CardContent, Table, TableBody, TableCell, TableHead, TableRow
} from '@mui/material';
import { OpenInNew, CheckCircle, AccountTree } from '@mui/icons-material';

interface AirflowMonitorProps {
  open: boolean;
  onClose: () => void;
  status?: string;
}

export default function AirflowMonitorDialog({ open, onClose, status = 'healthy' }: AirflowMonitorProps) {
  const airflowUrl = 'http://localhost:8080';

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle display="flex" justifyContent="space-between" alignItems="center">
        <Box display="flex" alignItems="center" gap={1.5}>
          <AccountTree color="primary" />
          <Typography variant="h6" fontWeight={700}>Apache Airflow Monitor</Typography>
        </Box>
        <Chip
          icon={<CheckCircle />}
          label={status.toUpperCase()}
          color="success"
          size="small"
        />
      </DialogTitle>

      <DialogContent dividers>
        <Grid container spacing={2} mb={3}>
          <Grid item xs={12} sm={4}>
            <Card variant="outlined">
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Typography variant="caption" color="text.secondary">Cluster Status</Typography>
                <Typography variant="h6" color="success.main" fontWeight={700}>Operational</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card variant="outlined">
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Typography variant="caption" color="text.secondary">Active DAGs</Typography>
                <Typography variant="h6" fontWeight={700}>snaplogic_pipeline_dag</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card variant="outlined">
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Typography variant="caption" color="text.secondary">Scheduler Health</Typography>
                <Typography variant="h6" color="success.main" fontWeight={700}>100% Heartbeat</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Typography variant="subtitle1" fontWeight={700} mb={1}>
          Orchestrated Conversion DAG Tasks
        </Typography>
        <Table size="small" sx={{ mb: 2 }}>
          <TableHead>
            <TableRow>
              <TableCell>Task ID</TableCell>
              <TableCell>Operator</TableCell>
              <TableCell>Trigger State</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell>fetch_snaplogic_json</TableCell>
              <TableCell>PythonOperator</TableCell>
              <TableCell><Chip label="success" color="success" size="small" /></TableCell>
            </TableRow>
            <TableRow>
              <TableCell>ai_convert_to_python</TableCell>
              <TableCell>PythonOperator</TableCell>
              <TableCell><Chip label="success" color="success" size="small" /></TableCell>
            </TableRow>
            <TableRow>
              <TableCell>execute_and_validate</TableCell>
              <TableCell>PythonOperator</TableCell>
              <TableCell><Chip label="success" color="success" size="small" /></TableCell>
            </TableRow>
          </TableBody>
        </Table>

        <Box bgcolor="action.hover" p={2} borderRadius={2} display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="subtitle2" fontWeight={600}>Airflow Web UI URL</Typography>
            <Typography variant="body2" color="text.secondary">{airflowUrl}</Typography>
          </Box>
          <Button
            variant="contained"
            endIcon={<OpenInNew />}
            href={airflowUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            Open Airflow Dashboard
          </Button>
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}
