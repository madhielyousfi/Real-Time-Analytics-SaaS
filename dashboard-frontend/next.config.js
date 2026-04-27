/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8001/api/:path*',
      },
      {
        source: '/track/:path*',
        destination: 'http://localhost:8001/track/:path*',
      },
      {
        source: '/health',
        destination: 'http://localhost:8001/health',
      },
    ];
  },
};

module.exports = nextConfig;