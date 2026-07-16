/**
 * packages/web/src/components/auth/__tests__/ProtectedRoute.test.tsx
 */
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "../ProtectedRoute";
import { useAuthStore } from "../../../store/authStore";

describe("ProtectedRoute", () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, accessToken: null, refreshToken: null });
  });

  const TestSetup = ({ roles }: { roles?: any[] }) => (
    <MemoryRouter initialEntries={["/protected"]}>
      <Routes>
        <Route path="/login" element={<div>Login Page</div>} />
        <Route path="/unauthorized" element={<div>Unauthorized Page</div>} />
        <Route
          path="/protected"
          element={
            <ProtectedRoute allowedRoles={roles}>
              <div>Protected Content</div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>
  );

  it("redirects to /login if not authenticated", () => {
    render(<TestSetup />);
    expect(screen.getByText("Login Page")).toBeInTheDocument();
    expect(screen.queryByText("Protected Content")).toBeNull();
  });

  it("renders content if authenticated and no roles specified", () => {
    useAuthStore.getState().setAuth(
      { id: "1", name: "User", email: "user@test.com", role: "operator" },
      "token"
    );
    render(<TestSetup />);
    expect(screen.getByText("Protected Content")).toBeInTheDocument();
  });

  it("redirects to /unauthorized if role doesn't match", () => {
    useAuthStore.getState().setAuth(
      { id: "1", name: "User", email: "user@test.com", role: "operator" },
      "token"
    );
    render(<TestSetup roles={["admin"]} />);
    expect(screen.getByText("Unauthorized Page")).toBeInTheDocument();
  });

  it("renders content if role matches", () => {
    useAuthStore.getState().setAuth(
      { id: "1", name: "User", email: "user@test.com", role: "operator" },
      "token"
    );
    render(<TestSetup roles={["operator", "admin"]} />);
    expect(screen.getByText("Protected Content")).toBeInTheDocument();
  });
});
