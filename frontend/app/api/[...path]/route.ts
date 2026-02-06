// Max timeout for Vercel hobby plan (300 seconds = 5 minutes)
export const maxDuration = 300;

// Detect environment: Vercel uses VERCEL env var, Docker uses API_URL_INTERNAL
const getApiUrl = () => {
    if (process.env.VERCEL) {
        // On Vercel: proxy to Render backend
        return 'https://youtube-notes-c4kf.onrender.com';
    }
    // On Docker: proxy to internal service
    return process.env.API_URL_INTERNAL || 'http://api:8000';
};

export async function POST(
    request: Request,
    { params }: { params: Promise<{ path?: string[] }> }
) {
    const { path } = await params;
    const apiUrl = getApiUrl();
    const endpoint = path?.join('/') || '';

    const body = await request.text();

    try {
        const response = await fetch(`${apiUrl}/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Forwarded-For': request.headers.get('x-forwarded-for') || '',
            },
            body,
        });

        const data = await response.json();
        return Response.json(data, { status: response.status });
    } catch (error: unknown) {
        console.error('API proxy error:', error);
        return Response.json(
            { detail: error instanceof Error ? error.message : 'Proxy error' },
            { status: 502 }
        );
    }
}

export async function GET(
    request: Request,
    { params }: { params: Promise<{ path?: string[] }> }
) {
    const { path } = await params;
    const apiUrl = getApiUrl();
    const endpoint = path?.join('/') || '';

    try {
        const response = await fetch(`${apiUrl}/${endpoint}`, {
            method: 'GET',
            headers: {
                'X-Forwarded-For': request.headers.get('x-forwarded-for') || '',
            },
        });

        const data = await response.json();
        return Response.json(data, { status: response.status });
    } catch (error: unknown) {
        console.error('API proxy error:', error);
        return Response.json(
            { detail: error instanceof Error ? error.message : 'Proxy error' },
            { status: 502 }
        );
    }
}
