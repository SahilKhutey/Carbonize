/**
 * packages/web/src/hooks/useAuth.ts
 */
import { useAuthStore, Role } from "../store/authStore";

export function useAuth() {
  const { user, accessToken, setAuth, logout } = useAuthStore();
  const isAuthenticated = !!accessToken && !!user;

  const hasRole = (allowedRoles: Role[]) => {
    if (!user) return false;
    return allowedRoles.includes(user.role);
  };

  return {
    user,
    isAuthenticated,
    hasRole,
    setAuth,
    logout,
  };
}
