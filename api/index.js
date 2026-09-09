module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const url = req.url || '';

  // Auth endpoints
  if (url.includes('/auth/google')) {
    return res.status(200).json({
      access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo_token_12345',
      refresh_token: 'demo_refresh_token_12345',
      token_type: 'bearer',
      expires_in: 604800,
    });
  }

  if (url.includes('/auth/login')) {
    let email = 'udayrise7666@gmail.com';
    if (req.body && req.body.email) email = req.body.email;
    return res.status(200).json({
      message: 'OTP sent to your email (Demo Mode: 123456)',
      email: email,
      otp_code: '123456',
    });
  }

  if (url.includes('/auth/verify-otp')) {
    return res.status(200).json({
      access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo_token_12345',
      refresh_token: 'demo_refresh_token_12345',
      token_type: 'bearer',
      expires_in: 604800,
    });
  }

  if (url.includes('/auth/me')) {
    return res.status(200).json({
      id: '11111111-1111-1111-1111-111111111111',
      email: 'udayrise7666@gmail.com',
      role: 'ADMIN',
      is_active: true,
      is_verified: true,
    });
  }

  // Dashboard metrics
  if (url.includes('/dashboard')) {
    return res.status(200).json({
      total_pipelines: 12,
      converted_pipelines: 10,
      failed_pipelines: 2,
      running_jobs: 0,
      queued_jobs: 0,
      average_execution_time_ms: 145,
      success_rate: 83.3,
      failure_rate: 16.7,
      daily_conversions: [
        { date: '2026-09-03', count: 2 },
        { date: '2026-09-04', count: 3 },
        { date: '2026-09-05', count: 1 },
        { date: '2026-09-06', count: 4 },
        { date: '2026-09-07', count: 2 },
        { date: '2026-09-08', count: 5 },
      ],
      pipeline_status: { Converted: 10, Failed: 2 },
      recent_activity: [
        { id: '1', name: 'Employee_Salary_Calculation.json', status: 'completed', updated_at: '2026-09-08T16:00:00Z' },
        { id: '2', name: 'Filter_Active_Records.json', status: 'completed', updated_at: '2026-09-08T16:18:00Z' },
      ],
      airflow_status: { status: 'healthy' },
      datadog_status: { status: 'healthy' },
    });
  }

  // List endpoints returning arrays
  if (url.includes('/notifications') || url.includes('/pipelines') || url.includes('/history') || url.includes('/reports') || url.includes('/logs') || url.includes('/downloads') || url.includes('/interpreter/history')) {
    return res.status(200).json([]);
  }

  return res.status(200).json({ status: 'healthy', version: '1.0.0', database: 'healthy' });
};
