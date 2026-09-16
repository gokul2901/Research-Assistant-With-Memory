import axios, { AxiosError, AxiosInstance, AxiosResponse } from "axios";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60s for batch LLM/Scraping operations
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<{ detail?: string; error?: string; message?: string }>) => {
    let friendlyMessage = "An unexpected error occurred while communicating with the research service.";

    if (error.response) {
      const data = error.response.data;
      if (typeof data === "object" && data !== null) {
        friendlyMessage =
          data.detail ||
          data.message ||
          data.error ||
          `Server returned error (${error.response.status})`;
      } else if (typeof data === "string") {
        friendlyMessage = data;
      }
    } else if (error.request) {
      friendlyMessage =
        "Could not connect to the Research Assistant backend server. Please verify the FastAPI service is running.";
    } else {
      friendlyMessage = error.message;
    }

    const customError = new Error(friendlyMessage);
    (customError as unknown as { status?: number }).status = error.response?.status;
    return Promise.reject(customError);
  }
);

export { API_BASE_URL };
