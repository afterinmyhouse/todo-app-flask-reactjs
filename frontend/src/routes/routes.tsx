import { createBrowserRouter } from "react-router-dom";
import { LandingRoot } from "./landing/root";
import { HomePage } from "./landing/home/page";
import { DashboardRoot } from "./dashboard/root";
import { DashboardHomePage } from "./dashboard/page";
import { DashboardSettingsPage } from "./dashboard/settings/page";
import { DashboardProjectsPage } from "./dashboard/projects/page";
import { DashboardNewProjectPage } from "./dashboard/projects/new/page";
import { DashboardNewProjectWithTasksPage } from "./dashboard/projects/new-with-tasks/page";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingRoot />,
    children: [{ index: true, element: <HomePage /> }],
  },
  {
    path: "/dashboard",
    element: <DashboardRoot />,
    children: [
      { index: true, element: <DashboardHomePage /> },
      { path: "settings", element: <DashboardSettingsPage /> },
      { path: "projects", element: <DashboardProjectsPage /> },
      { path: "projects/new", element: <DashboardNewProjectPage /> },
      {
        path: "projects/new-with-tasks",
        element: <DashboardNewProjectWithTasksPage />,
      },
    ],
  },
]);
