import axios, { AxiosError, type AxiosResponse } from "axios";

interface ApiErrorPayload {
  detail?: string;
  message?: string;
}

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorPayload>) => {
    const fallbackMessage = "The platform API request failed.";
    const apiMessage = error.response?.data?.detail ?? error.response?.data?.message;
    return Promise.reject(new Error(apiMessage ?? error.message ?? fallbackMessage));
  },
);

export async function unwrap<T>(request: Promise<AxiosResponse<T>>): Promise<T> {
  const response = await request;
  return response.data;
}
