import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.API_URL_INTERNAL || 'http://api:8000/:path*', // Proxy to Backend
      },
    ];
  },
};

export default nextConfig;
