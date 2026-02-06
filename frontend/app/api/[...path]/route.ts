// Unlimited timeout for local development (0 = no limit)
// On Vercel, this would be capped by your plan limits
export const maxDuration = 0;

export async function POST(
    request: Request,
    { params }: { params: Promise<{ path?: string[] }> }
) {
    const { path } = await params;
    const apiUrl = process.env.API_URL_INTERNAL || 'http://api:8000';
    const endpoint = path?.join('/') || '';

    const body = await request.text();

    // 30 minute timeout for very long videos
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30 * 60 * 1000);

    try {
        const response = await fetch(`${apiUrl}/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Forwarded-For': request.headers.get('x-forwarded-for') || '',
            },
            body,
            signal: controller.signal,
        });

        clearTimeout(timeoutId);
        const data = await response.json();
        return Response.json(data, { status: response.status });
    } catch (error: unknown) {
        clearTimeout(timeoutId);
        if (error instanceof Error && error.name === 'AbortError') {
            return Response.json({ detail: 'Request timed out after 30 minutes' }, { status: 504 });
        }
        throw error;
    }
}

export async function GET(
    request: Request,
    { params }: { params: Promise<{ path?: string[] }> }
) {
    const { path } = await params;
    const apiUrl = process.env.API_URL_INTERNAL || 'http://api:8000';
    const endpoint = path?.join('/') || '';

    const response = await fetch(`${apiUrl}/${endpoint}`, {
        method: 'GET',
        headers: {
            'X-Forwarded-For': request.headers.get('x-forwarded-for') || '',
        },
    });

    const data = await response.json();
    return Response.json(data, { status: response.status });
}
