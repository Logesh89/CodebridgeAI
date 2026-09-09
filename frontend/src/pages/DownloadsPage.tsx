import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box, Typography, Card, Table, TableBody, TableCell, TableHead, TableRow,
  Chip, Button, TextField, InputAdornment, CircularProgress, Alert
} from '@mui/material';
import { Download, Search, Description, Code } from '@mui/icons-material';
import { reportsApi, pipelineApi, downloadApi } from '../services/api';

interface DownloadableItem {
  id: string;
  name: string;
  type: 'python' | 'report' | 'json';
  category: 'completed' | 'failed' | 'reports';
  date: string;
  downloadUrl: string;
}

export default function DownloadsPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const { data: pipelines, isLoading: isLoadingPipelines } = useQuery({
    queryKey: ['pipelines'],
    queryFn: () => pipelineApi.list().then((r) => r.data).catch(() => []),
  });

  const { data: reports, isLoading: isLoadingReports } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportsApi.list().then((r) => r.data).catch(() => []),
  });

  if (isLoadingPipelines || isLoadingReports) {
    return <Box display="flex" justifyContent="center" p={8}><CircularProgress /></Box>;
  }

  const items: DownloadableItem[] = [];

  const pipelineList = Array.isArray(pipelines) ? pipelines : (Array.isArray((pipelines as any)?.items) ? (pipelines as any).items : []);
  const reportList = Array.isArray(reports) ? reports : (Array.isArray((reports as any)?.items) ? (reports as any).items : []);

  pipelineList.forEach((p: { id: string; name: string; python_file_path?: string; status: string; updated_at: string }) => {
    if (p.python_file_path) {
      items.push({
        id: p.id,
        name: `${p.name}.py`,
        type: 'python',
        category: p.status === 'completed' ? 'completed' : 'failed',
        date: p.updated_at,
        downloadUrl: downloadApi.getUrl(p.id),
      });
    }
  });

  reportList.forEach((r: { id: string; pipeline_id: string; status: string; created_at: string }) => {
    items.push({
      id: r.id,
      name: `validation_report_${r.id.slice(0, 8)}.html`,
      type: 'report',
      category: 'reports',
      date: r.created_at,
      downloadUrl: downloadApi.getUrl(r.id),
    });
  });

  const filteredItems = items.filter((item) =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight={700}>Download Center</Typography>
        <TextField
          size="small"
          placeholder="Search files..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
          sx={{ width: 280 }}
        />
      </Box>

      {filteredItems.length === 0 ? (
        <Alert severity="info">No downloadable files matching your search criteria.</Alert>
      ) : (
        <Card>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Artifact Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Generated Date</TableCell>
                <TableCell align="right">Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredItems.map((item) => (
                <TableRow key={item.id}>
                  <TableCell sx={{ fontWeight: 600 }}>{item.name}</TableCell>
                  <TableCell>
                    <Chip
                      icon={item.type === 'python' ? <Code /> : <Description />}
                      label={item.type.toUpperCase()}
                      size="small"
                      color={item.type === 'python' ? 'primary' : 'secondary'}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={item.category.toUpperCase()}
                      size="small"
                      variant="outlined"
                      color={item.category === 'completed' ? 'success' : item.category === 'failed' ? 'error' : 'default'}
                    />
                  </TableCell>
                  <TableCell>{new Date(item.date).toLocaleDateString()}</TableCell>
                  <TableCell align="right">
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<Download />}
                      href={item.downloadUrl}
                      download
                    >
                      Download
                    </Button>
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
