import { fetchCurrentUser } from "@/services/api/auth";
import { useAuthStore } from "@/stores/auth-store";
import { useSEO } from "@/hooks/useSEO";
import { AxiosError } from "axios";
import { useEffect } from "react";
import { Navigate, Outlet, useNavigate } from "react-router-dom";
import { Navbar } from "./_components/navbar";
import { Toaster } from "sonner";

export const DashboardRoot = () => {
  const navigate = useNavigate();
  const { isLoggedIn, token, logout } = useAuthStore();

  if (!isLoggedIn) {
    return <Navigate to="/" />;
  }

  useEffect(() => {
    if (!token) return;
    fetchCurrentUser().catch((err) => {
      const status = err instanceof AxiosError ? err.response?.status : undefined;
      if (status === 401) {
        logout();
        navigate("/", { replace: true });
      }
    });
  }, [token, logout, navigate]);

  useSEO("Dashboard | TodoApp");

  return (
    <>
      <Navbar />
      <main className="mt-16 bg-muted/50 min-h-[calc(100vh-4rem)]">
        <section className="cs-section">
          <div className="cs-container">
            <Outlet />
          </div>
        </section>
      </main>
      <Toaster position="top-center" richColors />
    </>
  );
};
