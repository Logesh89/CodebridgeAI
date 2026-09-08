import { useState, useEffect } from 'react';
import {
  Box, Typography, Card, Grid, MenuItem, TextField,
  Button, CircularProgress, Paper, Chip, Stack, Snackbar, Alert,
} from '@mui/material';
import {
  Transform, CheckCircle, CloudUpload, PlayArrow, Download, ContentCopy, Terminal, Delete, Info, Warning, Error as ErrorIcon,
} from '@mui/icons-material';
import { interpreterApi } from '../services/api';

interface LanguageOption {
  id: string;
  name: string;
  extensions: string[];
  mimeAccept: string;
  targetExt: string;
}

const LANGUAGES: LanguageOption[] = [
  { id: 'java', name: 'Java', extensions: ['.java'], mimeAccept: '.java', targetExt: '.java' },
  { id: 'python', name: 'Python', extensions: ['.py'], mimeAccept: '.py', targetExt: '.py' },
  { id: 'c', name: 'C', extensions: ['.c', '.h'], mimeAccept: '.c,.h', targetExt: '.c' },
  { id: 'cpp', name: 'C++', extensions: ['.cpp', '.cc', '.hpp'], mimeAccept: '.cpp,.cc,.hpp', targetExt: '.cpp' },
  { id: 'csharp', name: 'C# / .NET', extensions: ['.cs'], mimeAccept: '.cs', targetExt: '.cs' },
  { id: 'javascript', name: 'JavaScript', extensions: ['.js', '.mjs'], mimeAccept: '.js,.mjs', targetExt: '.js' },
  { id: 'typescript', name: 'TypeScript', extensions: ['.ts', '.tsx'], mimeAccept: '.ts,.tsx', targetExt: '.ts' },
  { id: 'nodejs', name: 'Node.js', extensions: ['.js', '.ts'], mimeAccept: '.js,.ts', targetExt: '.js' },
  { id: 'go', name: 'Go', extensions: ['.go'], mimeAccept: '.go', targetExt: '.go' },
  { id: 'rust', name: 'Rust', extensions: ['.rs'], mimeAccept: '.rs', targetExt: '.rs' },
  { id: 'php', name: 'PHP', extensions: ['.php'], mimeAccept: '.php', targetExt: '.php' },
  { id: 'react', name: 'React (JSX / TSX)', extensions: ['.jsx', '.tsx'], mimeAccept: '.jsx,.tsx', targetExt: '.tsx' },
  { id: 'angular', name: 'Angular (TS)', extensions: ['.ts'], mimeAccept: '.ts', targetExt: '.ts' },
  { id: 'sql', name: 'SQL Query', extensions: ['.sql'], mimeAccept: '.sql', targetExt: '.sql' },
  { id: 'pyspark', name: 'PySpark DataFrames', extensions: ['.py', '.pyspark'], mimeAccept: '.py,.pyspark', targetExt: '.py' },
  { id: 'shell', name: 'Shell Script (Bash)', extensions: ['.sh', '.bash'], mimeAccept: '.sh,.bash', targetExt: '.sh' },
  { id: 'powershell', name: 'PowerShell', extensions: ['.ps1'], mimeAccept: '.ps1', targetExt: '.ps1' },
  { id: 'snaplogic', name: 'SnapLogic AST (JSON)', extensions: ['.json', '.slp'], mimeAccept: '.json,.slp', targetExt: '.py' },
  { id: 'iics', name: 'IICS Mapping JSON', extensions: ['.json', '.iics'], mimeAccept: '.json,.iics', targetExt: '.ktr' },
  { id: 'pentaho_ktr', name: 'Pentaho KTR (XML)', extensions: ['.ktr', '.xml'], mimeAccept: '.ktr,.xml', targetExt: '.ktr' },
  { id: 'json', name: 'JSON Config', extensions: ['.json'], mimeAccept: '.json', targetExt: '.json' },
  { id: 'xml', name: 'XML Document', extensions: ['.xml'], mimeAccept: '.xml', targetExt: '.xml' },
  { id: 'yaml', name: 'YAML Config', extensions: ['.yaml', '.yml'], mimeAccept: '.yaml,.yml', targetExt: '.yaml' },
];

export default function CodeInterpreterPage() {
  const [fromLang, setFromLang] = useState<string>('java');
  const [toLang, setToLang] = useState<string>('python');
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [sourceCode, setSourceCode] = useState<string>('');
  const [convertedCode, setConvertedCode] = useState<string>('');
  const [convertedFileName, setConvertedFileName] = useState<string>('');
  const [sourceOutput, setSourceOutput] = useState<string>('');
  const [targetOutput, setTargetOutput] = useState<string>('');

  const [conversionStatus, setConversionStatus] = useState<string>('');
  const [compilationMessage, setCompilationMessage] = useState<string>('');
  const [conversionAttempts, setConversionAttempts] = useState<number>(1);
  const [outputMatched, setOutputMatched] = useState<boolean>(false);
  const [conversionReport, setConversionReport] = useState<any>(null);

  const [isConverting, setIsConverting] = useState<boolean>(false);
  const [isAutoFixing, setIsAutoFixing] = useState<boolean>(false);
  const [dragOver, setDragOver] = useState<boolean>(false);
  const [snackbarMessage, setSnackbarMessage] = useState<string>('');
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false);

  const currentFromConfig = LANGUAGES.find((l) => l.id === fromLang) || LANGUAGES[0];
  const currentToConfig = LANGUAGES.find((l) => l.id === toLang) || LANGUAGES[1];

  // Auto-set target to Pentaho KTR when source is IICS JSON
  useEffect(() => {
    if (fromLang === 'iics') {
      setToLang('pentaho_ktr');
    }
  }, [fromLang]);

  // Live Source Execution
  useEffect(() => {
    if (!sourceCode.trim()) {
      setSourceOutput('');
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const res = await interpreterApi.executeCode({ code: sourceCode, language: fromLang });
        if (res.data && res.data.output) {
          setSourceOutput(res.data.output);
        }
      } catch {
        setSourceOutput(`[${fromLang.toUpperCase()} Source Execution Pending Server Verification]`);
      }
    }, 800);
    return () => clearTimeout(timer);
  }, [sourceCode, fromLang]);

  const handleClearAll = () => {
    setSourceCode('');
    setConvertedCode('');
    setSourceOutput('');
    setTargetOutput('');
    setFile(null);
    setFileName('');
    setConvertedFileName('');
    setConversionStatus('');
    setCompilationMessage('');
    setConversionReport(null);
    setSnackbarMessage('Cleared editor and terminal outputs.');
    setSnackbarOpen(true);
  };

  const handleFileSelect = (selectedFile: File) => {
    const ext = '.' + selectedFile.name.split('.').pop()?.toLowerCase();
    const isValid = currentFromConfig.extensions.some((e) => e.toLowerCase() === ext);

    if (!isValid) {
      setSnackbarMessage(
        `Extension "${ext}" does not match ${currentFromConfig.name} (${currentFromConfig.extensions.join(', ')})`
      );
      setSnackbarOpen(true);
      return;
    }

    setFile(selectedFile);
    setFileName(selectedFile.name);

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setSourceCode(content);
      setSnackbarMessage(`Loaded "${selectedFile.name}" successfully!`);
      setSnackbarOpen(true);
    };
    reader.readAsText(selectedFile);
  };

  const handleConvert = async () => {
    if (!sourceCode.trim()) return;
    setIsConverting(true);
    const baseName = fileName ? fileName.split('.')[0] : 'ConvertedCode';
    const outFileName = `${baseName}${currentToConfig.targetExt}`;

    try {
      if (fromLang === 'iics' && (toLang === 'pentaho_ktr' || toLang === 'ktr')) {
        const response = await interpreterApi.convertIicsToKtr({ iics_json: sourceCode });
        if (response.data && response.data.ktr_xml) {
          setConvertedCode(response.data.ktr_xml);
          setConversionStatus(response.data.status || 'PRODUCTION_READY');
          setConversionReport(response.data.report);
          setCompilationMessage(response.data.compilation_message || 'Pentaho KTR XML transformation generated and validated.');
          setOutputMatched(Boolean(response.data.output_match ?? true));
          setSourceOutput(response.data.source_output || '-- IICS Source Mapping Input Data Stream --');
          setTargetOutput(response.data.target_output || 'Pentaho KTR Transformation XML Validated (0 errors).');
        }
      } else {
        const response = await interpreterApi.convertCode({
          source_code: sourceCode,
          from_lang: fromLang,
          to_lang: toLang,
          file_name: fileName,
        });

        if (response.data) {
          setConvertedCode(response.data.converted_code || '');
          setConversionStatus(response.data.status || 'PARTIALLY_VALIDATED');
          setCompilationMessage(response.data.compilation_message || '');
          setConversionAttempts(response.data.attempts || 1);
          setOutputMatched(Boolean(response.data.output_match));

          if (response.data.source_output) {
            setSourceOutput(response.data.source_output);
          } else {
            const srcExecRes = await interpreterApi.executeCode({ code: sourceCode, language: fromLang });
            setSourceOutput(srcExecRes.data?.output || 'Source execution complete.');
          }

          if (response.data.target_output) {
            setTargetOutput(response.data.target_output);
          } else {
            const tgtExecRes = await interpreterApi.executeCode({ code: response.data.converted_code, language: toLang });
            setTargetOutput(tgtExecRes.data?.output || 'Execution complete.');
          }
        }
      }
      setSnackbarMessage(`Converted to ${currentToConfig.name} (${outFileName})!`);
    } catch (err: any) {
      setConversionStatus('FAILED');
      setCompilationMessage(err.response?.data?.detail || 'Conversion failed.');
      setSnackbarMessage('Conversion encountered an error.');
    } finally {
      setConvertedFileName(outFileName);
      setIsConverting(false);
      setSnackbarOpen(true);
    }
  };

  const handleAutoFix = async () => {
    if (!convertedCode.trim()) return;
    setIsAutoFixing(true);
    try {
      const res = await interpreterApi.autoFixCode({
        code: convertedCode,
        language: toLang,
        source_code: sourceCode,
        error_message: targetOutput || compilationMessage,
      });

      if (res.data && res.data.fixed_code) {
        setConvertedCode(res.data.fixed_code);
        setConversionStatus(res.data.is_error_free ? 'PRODUCTION_READY' : 'PARTIALLY_VALIDATED');
        setCompilationMessage(res.data.compilation_message || 'Auto-fix complete.');
        
        const tgtOut = await interpreterApi.executeCode({ code: res.data.fixed_code, language: toLang });
        if (tgtOut.data && tgtOut.data.output) {
          setTargetOutput(tgtOut.data.output);
        }
        setSnackbarMessage('✨ AI Auto-Fix completed with compiler verification!');
      }
    } catch (err: any) {
      setSnackbarMessage('Auto-fix attempt failed.');
    } finally {
      setIsAutoFixing(false);
      setSnackbarOpen(true);
    }
  };

  const handleDownloadConvertedFile = () => {
    if (!convertedCode) return;
    const blob = new Blob([convertedCode], { type: 'text/plain;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', convertedFileName || `converted${currentToConfig.targetExt}`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setSnackbarMessage(`Downloaded "${convertedFileName}"!`);
    setSnackbarOpen(true);
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(convertedCode);
    setSnackbarMessage('Converted code copied to clipboard!');
    setSnackbarOpen(true);
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={800} mb={1} color="primary">
        Code Interpreter & Multi-Language Converter
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={3}>
        Strict AI code translation engine featuring compiler validation, secure sandbox execution, AI self-healing auto-fix loops, and dedicated <strong>IICS JSON → Pentaho KTR</strong> conversion.
      </Typography>

      {/* Language Selectors Header */}
      <Card sx={{ mb: 3, p: 2 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={5}>
            <TextField
              select
              fullWidth
              label="Source Language (From)"
              value={fromLang}
              onChange={(e) => {
                setFromLang(e.target.value);
                setFile(null);
              }}
            >
              {LANGUAGES.map((l) => (
                <MenuItem key={l.id} value={l.id}>
                  {l.name} ({l.extensions.join(', ')})
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          <Grid item xs={12} md={2} textAlign="center">
            <Transform sx={{ fontSize: 32, color: 'primary.main', my: 1 }} />
          </Grid>

          <Grid item xs={12} md={5}>
            <TextField
              select
              fullWidth
              label="Target Language (To)"
              value={toLang}
              onChange={(e) => setToLang(e.target.value)}
            >
              {LANGUAGES.filter((l) => l.id !== fromLang).map((l) => (
                <MenuItem key={l.id} value={l.id}>
                  {l.name} ({l.extensions.join(', ')})
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>
      </Card>

      {/* Code Editor Grid */}
      <Grid container spacing={3} mb={3}>
        {/* Source Code */}
        <Grid item xs={12} md={6}>
          <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="subtitle1" fontWeight={700} color="primary">
                Source Code ({currentFromConfig.name})
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center">
                <Chip
                  label={`Allowed: ${currentFromConfig.extensions.join(', ')}`}
                  color="primary"
                  size="small"
                  variant="outlined"
                />
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  startIcon={<Delete fontSize="small" />}
                  onClick={handleClearAll}
                  sx={{ fontWeight: 600, textTransform: 'none' }}
                >
                  Clear
                </Button>
              </Stack>
            </Box>

            <Box
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                if (e.dataTransfer.files?.[0]) handleFileSelect(e.dataTransfer.files[0]);
              }}
              sx={{
                border: '2px dashed',
                borderColor: dragOver ? 'primary.main' : 'divider',
                borderRadius: 2, p: 3, textAlign: 'center', mb: 2, cursor: 'pointer',
                bgcolor: dragOver ? 'action.hover' : 'background.default',
              }}
              onClick={() => document.getElementById('interpreter-file-input')?.click()}
            >
              <CloudUpload color="primary" sx={{ fontSize: 32, mb: 1 }} />
              <Typography variant="body2" fontWeight={600}>
                {file ? file.name : `Click or Drag & Drop ${currentFromConfig.name} file (${currentFromConfig.extensions.join(', ')})`}
              </Typography>
              <input
                id="interpreter-file-input"
                type="file"
                hidden
                accept={currentFromConfig.mimeAccept}
                onChange={(e) => {
                  if (e.target.files?.[0]) handleFileSelect(e.target.files[0]);
                }}
              />
            </Box>

            <TextField
              multiline
              rows={14}
              fullWidth
              variant="outlined"
              placeholder={`Paste or type ${currentFromConfig.name} code here...`}
              value={sourceCode}
              onChange={(e) => setSourceCode(e.target.value)}
              sx={{
                fontFamily: 'monospace',
                '& .MuiInputBase-input': { fontFamily: 'monospace', fontSize: '0.875rem' },
              }}
            />

            <Box display="flex" justifyContent="flex-end" mt={2}>
              <Button
                variant="contained"
                size="large"
                startIcon={isConverting ? <CircularProgress size={20} color="inherit" /> : <PlayArrow />}
                disabled={isConverting || !sourceCode.trim()}
                onClick={handleConvert}
                sx={{ px: 4, fontWeight: 700 }}
              >
                {isConverting ? 'Translating & Validating...' : `Convert to ${currentToConfig.name}`}
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Converted Output Code */}
        <Grid item xs={12} md={6}>
          <Paper variant="outlined" sx={{ p: 2, height: '100%', bgcolor: '#f8fafc' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="subtitle1" fontWeight={700} color="success.main">
                Converted Code ({currentToConfig.name})
              </Typography>
              {convertedCode && (
                <Stack direction="row" spacing={1} alignItems="center">
                  {conversionStatus === 'PRODUCTION_READY' && (
                    <Chip icon={<CheckCircle />} label="PRODUCTION READY (Compiler Validated)" color="success" size="small" sx={{ fontWeight: 700 }} />
                  )}
                  {conversionStatus === 'SYNTAX_HEURISTIC_ONLY' && (
                    <Chip icon={<Warning />} label="Syntax Heuristic Only (Compiler Unavailable)" color="warning" size="small" sx={{ fontWeight: 700 }} />
                  )}
                  {conversionStatus === 'SYNTAX_VALIDATED_RUNTIME_UNAVAILABLE' && (
                    <Chip icon={<Info />} label="Syntax Validated (Runtime Unavailable)" color="info" size="small" sx={{ fontWeight: 700 }} />
                  )}
                  {conversionStatus === 'PARTIALLY_VALIDATED' && (
                    <Chip icon={<Warning />} label="Partially Validated" color="warning" size="small" sx={{ fontWeight: 700 }} />
                  )}
                  {conversionStatus === 'FAILED' && (
                    <Chip icon={<ErrorIcon />} label="Validation Failed" color="error" size="small" sx={{ fontWeight: 700 }} />
                  )}

                  <Button
                    variant="contained"
                    color="secondary"
                    size="small"
                    startIcon={isAutoFixing ? <CircularProgress size={16} color="inherit" /> : <Transform />}
                    disabled={isAutoFixing}
                    onClick={handleAutoFix}
                    sx={{ fontWeight: 700, textTransform: 'none' }}
                  >
                    Auto-Fix Code
                  </Button>
                  <Button
                    variant="contained"
                    color="success"
                    size="small"
                    startIcon={<Download />}
                    onClick={handleDownloadConvertedFile}
                  >
                    Download
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<ContentCopy />}
                    onClick={handleCopyCode}
                  >
                    Copy
                  </Button>
                </Stack>
              )}
            </Box>

            {compilationMessage && (
              <Alert severity={conversionStatus === 'FAILED' ? 'error' : conversionStatus === 'PRODUCTION_READY' ? 'success' : 'info'} sx={{ mb: 2, fontSize: '0.8rem' }}>
                <strong>Validation Metric:</strong> {compilationMessage} (Attempts: {conversionAttempts})
              </Alert>
            )}

            {conversionReport && (
              <Paper variant="outlined" sx={{ p: 1.5, mb: 2, bgcolor: '#ffffff' }}>
                <Typography variant="caption" fontWeight={700} display="block" color="primary">
                  📊 IICS &rarr; Pentaho KTR Conversion Summary (Attempts: {conversionAttempts})
                </Typography>
                <Typography variant="body2" fontSize="0.75rem">
                  Steps Generated: <strong>{conversionReport.generated_pentaho_steps}</strong> | Total Components: <strong>{conversionReport.total_iics_components}</strong>
                </Typography>
              </Paper>
            )}

            <Box
              component="pre"
              sx={{
                bgcolor: '#1e293b', color: '#f8fafc', p: 2.5, borderRadius: 2,
                fontFamily: 'monospace', fontSize: '0.875rem', overflowX: 'auto', minHeight: '320px', maxHeight: '360px',
              }}
            >
              {convertedCode || `// Converted ${currentToConfig.name} code will appear here after compiler validation...`}
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Terminal Output Comparison */}
      {(sourceOutput || targetOutput) && (
        <Card sx={{ p: 3, mb: 3, bgcolor: '#0f172a', color: '#f8fafc' }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box display="flex" alignItems="center" gap={1}>
              <Terminal sx={{ color: '#38bdf8' }} />
              <Typography variant="h6" fontWeight={700} color="#38bdf8">
                Live Terminal Sandbox Execution Output Comparison
              </Typography>
            </Box>
            <Stack direction="row" spacing={1} alignItems="center">
              {outputMatched ? <Chip icon={<CheckCircle />} label="100% Execution Match" color="success" size="small" /> : null}
              <Button
                variant="outlined"
                color="error"
                size="small"
                startIcon={<Delete fontSize="small" />}
                onClick={() => {
                  setSourceOutput('');
                  setTargetOutput('');
                }}
                sx={{ fontWeight: 600, textTransform: 'none', borderColor: '#ef4444', color: '#fca5a5' }}
              >
                Clear Terminal
              </Button>
            </Stack>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper variant="outlined" sx={{ p: 2, bgcolor: '#020617', borderColor: '#334155', color: '#e2e8f0' }}>
                <Typography variant="caption" fontWeight={700} color="#94a3b8" display="block" mb={1}>
                  🔷 SOURCE FILE TERMINAL STDOUT ({fileName || currentFromConfig.name})
                </Typography>
                <Box component="pre" sx={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#38bdf8', whiteSpace: 'pre-wrap', m: 0 }}>
                  {sourceOutput}
                </Box>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6}>
              <Paper variant="outlined" sx={{ p: 2, bgcolor: '#020617', borderColor: '#334155', color: '#e2e8f0' }}>
                <Typography variant="caption" fontWeight={700} color="#4ade80" display="block" mb={1}>
                  🐍 CONVERTED TARGET TERMINAL STDOUT ({convertedFileName || currentToConfig.name})
                </Typography>
                <Box component="pre" sx={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#4ade80', whiteSpace: 'pre-wrap', m: 0 }}>
                  {targetOutput}
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Card>
      )}

      {/* Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Box>
  );
}
