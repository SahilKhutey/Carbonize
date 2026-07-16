/**
 * packages/web/src/store/__tests__/authStore.test.ts
 */
import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore } from "../authStore";

describe("authStore", () => {
  beforeEach(() => {
    // Reset state before each test
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
    });
  });

  it("initializes with empty state", () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
  });

  it("setAuth updates user and tokens", () => {
    const user = { id: "1", name: "Op", email: "op@operator.com", role: "operator" as const };
    useAuthStore.getState().setAuth(user, "access-123", "refresh-456");
    
    const state = useAuthStore.getState();
    expect(state.user).toEqual(user);
    expect(state.accessToken).toBe("access-123");
    expect(state.refreshToken).toBe("refresh-456");
  });

  it("logout clears state", () => {
    const user = { id: "1", name: "Op", email: "op@operator.com", role: "operator" as const };
    useAuthStore.getState().setAuth(user, "access-123", "refresh-456");
    useAuthStore.getState().logout();
    
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.refreshToken).toBeNull();
  });
});
