module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const url = req.url || '';

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

  return res.status(200).json({ status: 'healthy', version: '1.0.0', database: 'healthy' });
};
