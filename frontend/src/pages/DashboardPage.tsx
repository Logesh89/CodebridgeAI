import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box, Grid, Card, CardContent, Typography, CircularProgress,
  Chip, LinearProgress, Table, TableBody, TableCell, TableHead, TableRow,
} from '@mui/material';
import {
  AccountTree, CheckCircle, Error, PlayArrow, Queue,
  Speed, TrendingUp, TrendingDown, OpenInNew,
} from '@mui/icons-material';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { dashboardApi } from '../services/api';
import { formatDate } from '../utils/formatters';
import AirflowMonitorDialog from '../components/AirflowMonitorDialog';
import DatadogMonitorDialog from '../components/DatadogMonitorDialog';

const COLORS = ['#1565C0', '#00897B', '#F57C00', '#C62828', '#7B1FA2'];

function MetricCard({ title, value, icon, color }: { title: string; value: string | number; icon: React.ReactNode; color: string }) {
  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="body2" color="text.secondary">{title}</Typography>
            <Typography variant="h4" fontWeight={700} mt={1}>{value}</Typography>
          </Box>
          <Box sx={{ bgcolor: `${color}20`, p: 1.5, borderRadius: 2, color }}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const [airflowOpen, setAirflowOpen] = useState(false);
  const [datadogOpen, setDatadogOpen] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardApi.getDashboard().then((r) => r.data),
    refetchInterval: 3000,
  });

  if (isLoading) return <Box display="flex" justifyContent="center" p={8}><CircularProgress /></Box>;
  if (error) return <Typography color="error">Failed to load dashboard</Typography>;

  const statusData = Object.entries(data?.pipeline_status || {}).map(([name, value]) => ({ name, value }));

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} mb={3}>Dashboard</Typography>

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Total Pipelines" value={data?.total_pipelines || 0} icon={<AccountTree />} color="#1565C0" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Converted" value={data?.converted_pipelines || 0} icon={<CheckCircle />} color="#2E7D32" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Failed" value={data?.failed_pipelines || 0} icon={<Error />} color="#C62828" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Running Jobs" value={data?.running_jobs || 0} icon={<PlayArrow />} color="#F57C00" />
        </Grid>
      </Grid>

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Queued Jobs" value={data?.queued_jobs || 0} icon={<Queue />} color="#7B1FA2" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Avg Execution Time" value={`${(data?.average_execution_time_ms || 0).toFixed(0)}ms`} icon={<Speed />} color="#00897B" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Success Rate" value={`${data?.success_rate || 0}%`} icon={<TrendingUp />} color="#2E7D32" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Failure Rate" value={`${data?.failure_rate || 0}%`} icon={<TrendingDown />} color="#C62828" />
        </Grid>
      </Grid>

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>Daily Conversions</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data?.daily_conversions || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#1565C0" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>Pipeline Status</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                    {statusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>System Status</Typography>
              <Box display="flex" gap={2} mb={2}>
                <Chip
                  label={`Airflow: ${data?.airflow_status?.status || 'unknown'}`}
                  color="success"
                  clickable
                  onClick={() => setAirflowOpen(true)}
                  icon={<OpenInNew fontSize="small" />}
                  sx={{ fontWeight: 600, px: 1 }}
                />
                <Chip
                  label={`Datadog: ${data?.datadog_status?.status || 'unknown'}`}
                  color="success"
                  clickable
                  onClick={() => setDatadogOpen(true)}
                  icon={<OpenInNew fontSize="small" />}
                  sx={{ fontWeight: 600, px: 1 }}
                />
              </Box>
              <Typography variant="subtitle2" mb={1}>Real-time Progress</Typography>
              <LinearProgress variant="determinate" value={data?.success_rate || 0} sx={{ mb: 1 }} />
            </CardContent>
          </Card>
        </Grid>

      <AirflowMonitorDialog
        open={airflowOpen}
        onClose={() => setAirflowOpen(false)}
        status={data?.airflow_status?.status}
      />
      <DatadogMonitorDialog
        open={datadogOpen}
        onClose={() => setDatadogOpen(false)}
        status={data?.datadog_status?.status}
      />
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>Recent Activity</Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Pipeline</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Updated</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(data?.recent_activity || []).slice(0, 5).map((item: { id: string; name: string; status: string; updated_at: string }) => (
                    <TableRow key={item.id}>
                      <TableCell>{item.name}</TableCell>
                      <TableCell><Chip label={item.status} size="small" /></TableCell>
                      <TableCell>{formatDate(item.updated_at)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
