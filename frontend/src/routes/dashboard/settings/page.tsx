import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useSEO } from "@/hooks/useSEO";
import { useAuthStore } from "@/stores/auth-store";
import { useMemo } from "react";
import { useNavigate } from "react-router-dom";

export const DashboardSettingsPage = () => {
  useSEO("Settings | TodoApp");

  const navigate = useNavigate();
  const { token, logout } = useAuthStore();

  const apiBaseUrl = useMemo(
    () => import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000",
    [],
  );

  const tokenPreview = useMemo(() => {
    if (!token) return "Not signed in";
    if (token.length <= 24) return token;
    return `${token.slice(0, 12)}…${token.slice(-12)}`;
  }, [token]);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const handleClearSession = () => {
    // Zustand persist uses the storage key "session"
    localStorage.removeItem("session");
    logout();
    navigate("/");
  };

  return (
    <div className="max-w-3xl mx-auto">
      <header className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your session and view runtime configuration.
        </p>
      </header>

      <div className="grid gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Session</CardTitle>
            <CardDescription>
              Your login state is stored locally for convenience.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-2 text-sm">
            <div className="flex items-center justify-between gap-4">
              <span className="text-muted-foreground">Token</span>
              <code className="truncate">{tokenPreview}</code>
            </div>
          </CardContent>
          <CardFooter className="flex flex-wrap gap-2 justify-end">
            <Button variant="outline" onClick={handleClearSession}>
              Clear local session
            </Button>
            <Button onClick={handleLogout}>Logout</Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>API</CardTitle>
            <CardDescription>
              Frontend talks to the backend using this base URL.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-sm">
            <div className="flex items-center justify-between gap-4">
              <span className="text-muted-foreground">Base URL</span>
              <code className="truncate">{apiBaseUrl}</code>
            </div>
          </CardContent>
          <CardFooter className="justify-end">
            <Button
              variant="outline"
              onClick={() => window.open(`${apiBaseUrl}/docs`, "_blank")}
            >
              Open API docs
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

