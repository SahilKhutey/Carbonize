/**
 * packages/web/src/components/auth/LoginPage.tsx
 */
import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { LogIn, KeyRound, Mail, AlertCircle } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import { Role } from "../../store/authStore";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { setAuth } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Where to redirect after login (defaulting to role-based routes if none)
  const from = (location.state as any)?.from?.pathname;

  const getDefaultRoute = (role: Role) => {
    switch (role) {
      case "operator": return "/operator/live";
      case "engineer": return "/twin/plant-alpha"; // default plant for now
      case "manager":
      case "admin":
        return "/executive/dashboard";
      default:
        return "/dashboard";
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = null;
        }
        const message = errorData?.detail || `Authentication failed (Status ${response.status})`;
        throw new Error(message);
      }

      const data = await response.json();

      if (data.status === "mfa_required") {
        setError("MFA is enabled on this account. Complete sign-in using the MFA verification challenge.");
        setLoading(false);
        return;
      }

      if (!data.access_token || !data.user) {
        throw new Error("Invalid response format received from auth server.");
      }

      const userRoles = data.user.roles || [];
      let mappedRole: Role = "engineer";
      if (userRoles.includes("admin")) mappedRole = "admin";
      else if (userRoles.includes("manager")) mappedRole = "manager";
      else if (userRoles.includes("operator")) mappedRole = "operator";

      const mappedUser = {
        id: data.user.id,
        email: data.user.email,
        name: data.user.email.split("@")[0],
        role: mappedRole,
      };

      setAuth(mappedUser, data.access_token, data.refresh_token);
      setLoading(false);
      navigate(from || getDefaultRoute(mappedRole), { replace: true });
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred during login.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 p-6">
      {/* Background decoration */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-900/30 border border-emerald-500/30 mb-4">
            <LogIn className="w-8 h-8 text-emerald-400" />
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">CBMS-Sim</h1>
          <p className="text-slate-400 mt-2">Sign in to your account</p>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-700 p-8 rounded-2xl shadow-2xl">
          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-900/30 border border-red-800/50 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-950/50 border border-slate-700 rounded-lg py-3 pl-10 pr-4 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-shadow"
                  placeholder="name@company.com"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-slate-300">Password</label>
                <a href="#" className="text-xs text-emerald-400 hover:text-emerald-300 hover:underline transition-colors">
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-950/50 border border-slate-700 rounded-lg py-3 pl-10 pr-4 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-shadow"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-3 px-4 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-xs text-slate-500">
              Demo accounts: 
              <span className="font-mono ml-1">op@operator.com</span> or 
              <span className="font-mono ml-1">boss@exec.com</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
