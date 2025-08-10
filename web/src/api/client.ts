import axios from "axios";
import { API_BASE } from "./endpoints";
import { tokenStorage } from "../lib/storage";

export const api = axios.create({
  baseURL: API_BASE,
  withCredentials: false,
});

api.interceptors.request.use((config) => {
  const t = tokenStorage.get();
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

// If you later add refresh flow, handle 401 here.

export default api;
