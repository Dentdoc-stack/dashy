import type { NextConfig } from "next";

// Internal backend URL used by the Next.js server-side proxy.
// Never exposed to the browser; the browser always uses relative /api/* paths.
const BACKEND_INTERNAL = process.env.BACKEND_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  reactCompiler: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_INTERNAL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
