/**
 * Lightweight contextual “agent” for in-app guidance.
 *
 * Privacy: all logic runs in the browser. No messages are sent to external
 * LLM APIs or logged to the backend. Do not pass secrets, tokens, or passwords
 * into this layer.
 */

export type AssistantContext = {
  pathname: string;
  isAuthenticated: boolean;
};

const normalize = (s: string) => s.trim().toLowerCase();

/** Opening line when the user opens the assistant, based on route + auth. */
export function getOpeningMessage(ctx: AssistantContext): string {
  const { pathname, isAuthenticated } = ctx;

  if (!isAuthenticated) {
    if (pathname === "/") {
      return "Welcome! I can explain how to sign in or create an account—ask me anything about using this app. I run entirely in your browser and never send your chats to a server.";
    }
    return "You are on a public page. Use **Sign in** or **Create account** from the home screen to reach your dashboard.";
  }

  if (pathname === "/dashboard" || pathname === "/dashboard/") {
    return "You are on the **Dashboard**. Use tags to filter tasks, or add tasks with the **New task** action. Try asking: “How do tags work?”";
  }
  if (pathname.startsWith("/dashboard/projects/new-with-tasks")) {
    return "You are creating a **project with initial tasks** (up to 50). Task titles in one request must be unique. Ask: “What if a tag is missing?”";
  }
  if (pathname.startsWith("/dashboard/projects/new")) {
    return "You are on **New project**. After creating a project, you can add tasks from the dashboard. Ask about projects vs tasks if unsure.";
  }
  if (pathname.startsWith("/dashboard/projects")) {
    return "This is your **Projects** list. Open a project from here or start a new one. I can summarize the difference between a single project and “project with tasks”.";
  }
  if (pathname.startsWith("/dashboard/settings")) {
    return "**Settings** is where you manage your account. I cannot change passwords or tokens—use the controls on this page.";
  }

  return "I am your in-app guide. Ask about **tasks**, **tags**, **projects**, or **sign-in**. I only use rules on your device—no cloud AI.";
}

/**
 * Rule-based reply from the user message and current route.
 * Intentionally conservative: no medical/legal claims, no data exfiltration.
 */
export function getReply(userMessage: string, ctx: AssistantContext): string {
  const q = normalize(userMessage);
  if (!q) {
    return "Type a question or keyword (for example: **tasks**, **projects**, **tags**).";
  }

  if (
    q.includes("password") ||
    q.includes("token") ||
    q.includes("jwt") ||
    q.includes("secret")
  ) {
    return "For security, **never paste passwords or JWT tokens** into this chat. Use the official sign-in form only. Your session token is stored locally by the app; sign out from settings when finished on a shared device.";
  }

  if (q.includes("tag")) {
    return "**Tags** label tasks. On the dashboard, pick a tag to filter the task list, or clear the filter to see everything. Tags are created when you assign them to a task.";
  }

  if (q.includes("task")) {
    return "**Tasks** live on the dashboard. You can create, edit, delete, and change status (pending / in progress / completed). Tasks can reference one tag for organization.";
  }

  if (q.includes("project")) {
    return "**Projects** group work at a higher level. You can create a project alone, or use **New project with tasks** to seed many tasks in one step (duplicate titles in that form are rejected).";
  }

  if (q.includes("sign") || q.includes("login") || q.includes("register") || q.includes("account")) {
    if (!ctx.isAuthenticated) {
      return "Use **Sign in** with your email and password, or **Create account** if you are new. After success you will be redirected to the dashboard.";
    }
    return "You are already signed in. Account changes are under **Settings**. To switch users, sign out from the navigation menu first.";
  }

  if (q.includes("where") || q.includes("help") || q.includes("how")) {
    return getOpeningMessage(ctx);
  }

  return "I match simple keywords about **tasks**, **tags**, **projects**, and **sign-in**. Rephrase your question, or tell me which screen you are on—I also show a route-specific tip when you open this panel.";
}
