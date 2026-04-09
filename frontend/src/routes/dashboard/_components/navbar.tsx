import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth-store";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";

export const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const isDashboard = location.pathname === "/dashboard";
  const isSettings = location.pathname.startsWith("/dashboard/settings");

  return (
    <header className="fixed top-0 left-0 w-full bg-background z-50 border-b">
      <nav className="flex items-center justify-between h-16 cs-container">
        <div className="flex items-center gap-6">
          <Link to="/dashboard" className="font-bold text-lg">
            TodoApp
          </Link>
          <div className="hidden sm:flex items-center gap-2 text-sm">
            <Link
              to="/dashboard"
              className={cn(
                "px-2 py-1 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors",
                isDashboard && "bg-accent text-accent-foreground",
              )}
            >
              Dashboard
            </Link>
            <Link
              to="/dashboard/settings"
              className={cn(
                "px-2 py-1 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors",
                isSettings && "bg-accent text-accent-foreground",
              )}
            >
              Settings
            </Link>
          </div>
        </div>

        <Button
          className="font-medium"
          size="sm"
          variant="outline"
          onClick={handleLogout}
        >
          Logout
        </Button>
      </nav>
    </header>
  );
};
