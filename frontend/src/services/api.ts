function resolveApiBaseUrl(): string {
  // 1. Build-time Vite environment variable
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim() !== '') {
    const trimmed = envUrl.trim().replace(/\/+$/, '');
    return trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`;
  }

  // 2. Runtime detection: when hosted on Render or remote domain, fallback to live backend
  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    const host = window.location.hostname.toLowerCase();
    const isLocal = host === 'localhost' || host === '127.0.0.1' || host === '0.0.0.0' || host === '::1';
    if (!isLocal) {
      return 'https://edumentor-backend-ma4l.onrender.com/api';
    }
  }

  // 3. Fallback for local development
  return 'http://localhost:8000/api';
}

export const API_BASE_URL = resolveApiBaseUrl();

export function getMediaUrl(path: string): string {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  const origin = API_BASE_URL.replace(/\/api\/?$/, '');
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${origin}${cleanPath}`;
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('edumentor_token');
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  // AbortController with 45s timeout to handle Render cold-starts gracefully
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 45000);

  if (options.signal) {
    options.signal.addEventListener('abort', () => controller.abort());
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      if (response.status === 401 && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/register')) {
        localStorage.removeItem('edumentor_token');
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          window.location.href = '/login';
        }
      }
      let errorMessage = 'An error occurred';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData);
      } catch {
        errorMessage = `HTTP error ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      const timeoutError = new Error(
        'Server request timed out. The backend service may be spinning up from idle on Render free tier. Please try again in a few seconds.'
      );
      console.error(`API Timeout [${endpoint}]:`, timeoutError);
      throw timeoutError;
    }
    if (err.message && err.message.includes('Failed to fetch')) {
      const connectionError = new Error(
        'Unable to connect to EduMentor AI backend. The server may be waking up on Render (free tier cold start) or is temporarily unreachable. Please retry.'
      );
      console.error(`API Connection Error [${endpoint}]:`, connectionError);
      throw connectionError;
    }
    console.error(`API Request Error [${endpoint}]:`, err);
    throw err;
  }
}
