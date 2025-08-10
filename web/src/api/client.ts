import axios, { AxiosError } from "axios";
import { API_BASE } from "./endpoints";
import { tokenStorage } from "../lib/storage";
import { refreshToken } from "./auth";

export const api = axios.create({ baseURL: API_BASE, withCredentials: false });

api.interceptors.request.use((config) => {
  const t = tokenStorage.getAccess();
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

let refreshing: Promise<string> | null = null;

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config!;
    const status = error.response?.status;

    // Retry once on 401 if we can refresh
    if (status === 401 && !((original as any)._retry)) {
      (original as any)._retry = true;
      try {
        if (!refreshing) {
          const refresh = tokenStorage.getRefresh();
          if (!refresh) throw new Error("No refresh token");
          refreshing = refreshToken(refresh).then(({ access }) => {
            tokenStorage.setAccess(access);
            return access;
          }).finally(() => { refreshing = null; });
        }
        const newAccess = await refreshing;
        original.headers = original.headers ?? {};
        (original.headers as any).Authorization = `Bearer ${newAccess}`;
        return api(original);
      } catch (e) {
        tokenStorage.clear();
      }
    }
    return Promise.reject(error);
  }
);

export default api;
