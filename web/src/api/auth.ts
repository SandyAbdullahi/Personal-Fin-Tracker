import api from "./client";

const OBTAIN = import.meta.env.VITE_JWT_OBTAIN as string;
const REFRESH = import.meta.env.VITE_JWT_REFRESH as string;

export type Tokens = { access: string; refresh: string };

const USERNAME_FIELD = import.meta.env.VITE_JWT_USERNAME_FIELD || "username";

export async function login(identifier: string, password: string) {
  const payload: Record<string, string> = { password };
  payload[USERNAME_FIELD] = identifier; // <-- key is email or username
  const { data } = await api.post(OBTAIN, payload);
  return data;
}

export async function refreshToken(refresh: string): Promise<{ access: string }> {
  const { data } = await api.post(REFRESH, { refresh });
  return data; // { access }
}
