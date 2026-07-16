/**
 * packages/web/src/components/auth/__tests__/LoginPage.test.tsx
 */
import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { BrowserRouter } from "react-router-dom";
import { LoginPage } from "../LoginPage";
import { useAuthStore } from "../../../store/authStore";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("LoginPage", () => {
  const renderLogin = () =>
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

  it("renders email and password inputs", () => {
    renderLogin();
    expect(screen.getByPlaceholderText(/name@company.com/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/••••••••/i)).toBeInTheDocument();
  });

  it("shows error if password is too short", async () => {
    renderLogin();
    
    fireEvent.change(screen.getByPlaceholderText(/name@company.com/i), {
      target: { value: "test@operator.com" },
    });
    fireEvent.change(screen.getByPlaceholderText(/••••••••/i), {
      target: { value: "123" },
    });

    const submitBtn = screen.getByRole("button", { name: /sign in/i });
    
    await act(async () => {
      fireEvent.click(submitBtn);
      // Wait for mock API delay
      await new Promise(r => setTimeout(r, 850));
    });

    expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument();
  });

  it("logs in successfully and navigates", async () => {
    renderLogin();
    
    fireEvent.change(screen.getByPlaceholderText(/name@company.com/i), {
      target: { value: "test@operator.com" },
    });
    fireEvent.change(screen.getByPlaceholderText(/••••••••/i), {
      target: { value: "password123" },
    });

    const submitBtn = screen.getByRole("button", { name: /sign in/i });
    
    await act(async () => {
      fireEvent.click(submitBtn);
      // Wait for mock API delay
      await new Promise(r => setTimeout(r, 850));
    });

    // Check authStore is updated
    expect(useAuthStore.getState().user?.role).toBe("operator");
    // Check navigation
    expect(mockNavigate).toHaveBeenCalledWith("/operator/live", { replace: true });
  });
});
