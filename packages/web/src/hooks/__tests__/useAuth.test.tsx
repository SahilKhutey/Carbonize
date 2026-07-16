/**
 * packages/web/src/hooks/__tests__/useAuth.test.tsx
 */
import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { useAuth } from "../useAuth";
import { useAuthStore } from "../../store/authStore";

describe("useAuth", () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, accessToken: null, refreshToken: null });
  });

  it("returns isAuthenticated false when no user", () => {
    const { result } = renderHook(() => useAuth());
    expect(result.current.isAuthenticated).toBe(false);
  });

  it("returns isAuthenticated true when logged in", () => {
    act(() => {
      useAuthStore.getState().setAuth(
        { id: "1", name: "Op", email: "op@op.com", role: "operator" },
        "token"
      );
    });
    
    const { result } = renderHook(() => useAuth());
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user?.name).toBe("Op");
  });

  it("hasRole returns correct boolean", () => {
    act(() => {
      useAuthStore.getState().setAuth(
        { id: "1", name: "Op", email: "op@op.com", role: "operator" },
        "token"
      );
    });

    const { result } = renderHook(() => useAuth());
    expect(result.current.hasRole(["operator"])).toBe(true);
    expect(result.current.hasRole(["admin"])).toBe(false);
    expect(result.current.hasRole(["operator", "admin"])).toBe(true);
  });
});
