/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    images: {
        unoptimized: true
    },
    trailingSlash: true,
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod'
    }
}

module.exports = nextConfig
