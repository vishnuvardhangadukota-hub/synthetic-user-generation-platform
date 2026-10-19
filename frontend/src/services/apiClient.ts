// ============================================================================
// Centralized API Client
// Handles base URL configuration, headers, error parsing, and PDF blobs
// ============================================================================

export const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  details?: any;

  constructor(message: string, status: number, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorDetail = 'Request failed';
    let details: any = null;

    try {
      const data = await response.json();
      details = data;
      if (typeof data.detail === 'string') {
        errorDetail = data.detail;
      } else if (Array.isArray(data.detail)) {
        // FastAPI validation errors
        errorDetail = data.detail.map((d: any) => `${d.loc?.join('.')}: ${d.msg}`).join(' | ');
      } else if (data.error) {
        errorDetail = data.error;
      } else if (data.message) {
        errorDetail = data.message;
      }
    } catch {
      errorDetail = response.statusText || `HTTP ${response.status}`;
    }

    throw new ApiError(errorDetail, response.status, details);
  }

  // Handle empty responses
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const apiClient = {
  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    return handleResponse<T>(response);
  },

  async post<T>(path: string, body?: any): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async put<T>(path: string, body?: any): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async delete<T>(path: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json',
      },
    });
    return handleResponse<T>(response);
  },

  /**
   * Downloads a binary file (e.g., PDF) as a browser Blob
   */
  async downloadBlob(path: string, defaultFilename: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'GET',
    });

    if (!response.ok) {
      let msg = 'Failed to download report';
      try {
        const errJson = await response.json();
        msg = errJson.detail || errJson.error || msg;
      } catch {
        msg = `${msg} (${response.status})`;
      }
      throw new ApiError(msg, response.status);
    }

    const blob = await response.blob();
    const disposition = response.headers.get('content-disposition');
    let filename = defaultFilename;
    if (disposition) {
      const match = disposition.match(/filename=["']?([^"']+)["']?/);
      if (match && match[1]) {
        filename = match[1];
      }
    }

    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  async checkHealth(): Promise<{ status: string; app_name?: string }> {
    return this.get<{ status: string; app_name?: string }>('/');
  },
};
