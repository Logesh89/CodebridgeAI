import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, Box,
  Chip, Grid, Card, CardContent, Table, TableBody, TableCell, TableHead, TableRow
} from '@mui/material';
import { OpenInNew, CheckCircle, Analytics } from '@mui/icons-material';

interface DatadogMonitorProps {
  open: boolean;
  onClose: () => void;
  status?: string;
}

export default function DatadogMonitorDialog({ open, onClose, status = 'connected' }: DatadogMonitorProps) {
  const datadogUrl = 'https://app.datadoghq.com';

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle display="flex" justifyContent="space-between" alignItems="center">
        <Box display="flex" alignItems="center" gap={1.5}>
          <Analytics color="primary" />
          <Typography variant="h6" fontWeight={700}>Datadog APM & Telemetry Monitor</Typography>
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
                <Typography variant="caption" color="text.secondary">APM Tracing</Typography>
                <Typography variant="h6" color="success.main" fontWeight={700}>Enabled (dd-trace)</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card variant="outlined">
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Typography variant="caption" color="text.secondary">Logs Injection</Typography>
                <Typography variant="h6" color="success.main" fontWeight={700}>Active</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card variant="outlined">
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Typography variant="caption" color="text.secondary">Service Name</Typography>
                <Typography variant="h6" fontWeight={700}>snaplogic-platform</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Typography variant="subtitle1" fontWeight={700} mb={1}>
          Real-time APM & Telemetry Traces
        </Typography>
        <Table size="small" sx={{ mb: 2 }}>
          <TableHead>
            <TableRow>
              <TableCell>Service Span</TableCell>
              <TableCell>Resource</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell>fastapi.request</TableCell>
              <TableCell>POST /api/v1/excel/upload</TableCell>
              <TableCell>42ms</TableCell>
              <TableCell><Chip label="200 OK" color="success" size="small" /></TableCell>
            </TableRow>
            <TableRow>
              <TableCell>ai.conversion.openai</TableCell>
              <TableCell>gpt-4o-mini completion</TableCell>
              <TableCell>1.2s</TableCell>
              <TableCell><Chip label="200 OK" color="success" size="small" /></TableCell>
            </TableRow>
            <TableRow>
              <TableCell>execution.pandas.validate</TableCell>
              <TableCell>compare_outputs()</TableCell>
              <TableCell>18ms</TableCell>
              <TableCell><Chip label="200 OK" color="success" size="small" /></TableCell>
            </TableRow>
          </TableBody>
        </Table>

        <Box bgcolor="action.hover" p={2} borderRadius={2} display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="subtitle2" fontWeight={600}>Datadog Cloud Portal URL</Typography>
            <Typography variant="body2" color="text.secondary">{datadogUrl}</Typography>
          </Box>
          <Button
            variant="contained"
            endIcon={<OpenInNew />}
            href={datadogUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            Open Datadog Dashboard
          </Button>
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}
