/**
 * packages/web/src/store/authStore.ts
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Role = "operator" | "engineer" | "manager" | "admin";

export interface User {
  id: string;
  email: string;
  name: string;
  role: Role;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;

  setAuth: (user: User, accessToken: string, refreshToken?: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,

      setAuth: (user, accessToken, refreshToken) =>
        set((state) => ({
          ...state,
          user,
          accessToken,
          ...(refreshToken ? { refreshToken } : {}),
        })),

      logout: () => set({ user: null, accessToken: null, refreshToken: null }),
    }),
    {
      name: "auth-storage",
    }
  )
);
