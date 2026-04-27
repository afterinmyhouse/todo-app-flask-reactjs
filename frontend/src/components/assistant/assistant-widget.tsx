import { useCallback, useEffect, useId, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { MessageCircle, Send, Sparkles, X } from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import {
  type AssistantContext,
  getOpeningMessage,
  getReply,
} from "@/lib/assistant-agent";
import {
  fetchEntitySearch,
  formatEntitySearchResults,
  parseEntitySearchQuery,
} from "@/lib/entity-search";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

type ChatRole = "user" | "assistant";

type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
};

let idCounter = 0;
const nextId = () => `m-${++idCounter}`;

function renderBoldSegments(text: string) {
  const parts = text.split(/\*\*(.+?)\*\*/g);
  return parts.map((part, i) =>
    i % 2 === 1 ? (
      <strong key={i} className="font-semibold text-foreground">
        {part}
      </strong>
    ) : (
      <span key={i}>{part}</span>
    ),
  );
}

export function AssistantWidget() {
  const location = useLocation();
  const { isLoggedIn, token } = useAuthStore();
  const panelId = useId();
  const listRef = useRef<HTMLDivElement>(null);

  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");

  const context: AssistantContext = {
    pathname: location.pathname,
    isAuthenticated: isLoggedIn,
  };

  const seedOpening = useCallback(() => {
    setMessages([
      {
        id: nextId(),
        role: "assistant",
        content: getOpeningMessage(context),
      },
    ]);
  }, [context.isAuthenticated, context.pathname]);

  useEffect(() => {
    if (open && messages.length === 0) {
      seedOpening();
    }
  }, [open, messages.length, seedOpening]);

  useEffect(() => {
    if (open && listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages, open]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    if (open) window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const send = () => {
    const text = draft.trim();
    if (!text) return;
    const userMsg: ChatMessage = { id: nextId(), role: "user", content: text };
    setDraft("");

    const searchQuery = parseEntitySearchQuery(text);
    if (searchQuery) {
      if (!isLoggedIn || !token) {
        setMessages((prev) => [
          ...prev,
          userMsg,
          {
            id: nextId(),
            role: "assistant",
            content:
              "**Search** uses your signed-in session. Sign in from the home page, open the assistant again, then try e.g. `search meeting`.",
          },
        ]);
        return;
      }

      const pendingId = nextId();
      setMessages((prev) => [
        ...prev,
        userMsg,
        {
          id: pendingId,
          role: "assistant",
          content: "Searching your workspace…",
        },
      ]);

      void fetchEntitySearch(searchQuery)
        .then((data) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === pendingId
                ? { ...m, content: formatEntitySearchResults(data) }
                : m,
            ),
          );
        })
        .catch(() => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === pendingId
                ? {
                    ...m,
                    content:
                      "Search could not complete (network or session). Check that the API is running and you are still signed in.",
                  }
                : m,
            ),
          );
        });
      return;
    }

    const answer = getReply(text, context);
    const botMsg: ChatMessage = {
      id: nextId(),
      role: "assistant",
      content: answer,
    };
    setMessages((prev) => [...prev, userMsg, botMsg]);
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col items-end gap-2 sm:bottom-6 sm:right-6">
      {open ? (
        <div
          id={panelId}
          role="dialog"
          aria-label="In-app assistant"
          className={cn(
            "flex h-[min(420px,70vh)] w-[min(100vw-2rem,380px)] flex-col overflow-hidden rounded-lg border bg-background shadow-lg",
          )}
        >
          <div className="flex items-center justify-between border-b bg-muted/40 px-3 py-2">
            <div className="flex items-center gap-2 text-sm font-medium">
              <Sparkles className="size-4 text-primary" aria-hidden />
              Assistant
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="size-8 shrink-0"
              onClick={() => setOpen(false)}
              aria-label="Close assistant"
            >
              <X className="size-4" />
            </Button>
          </div>

          <div
            ref={listRef}
            className="flex-1 space-y-3 overflow-y-auto p-3 text-sm leading-relaxed"
          >
            {messages.map((m) => (
              <div
                key={m.id}
                className={cn(
                  "rounded-md px-3 py-2",
                  m.role === "user"
                    ? "ml-6 bg-primary text-primary-foreground"
                    : "mr-4 bg-muted/80 text-muted-foreground",
                )}
              >
                <p className="whitespace-pre-wrap text-left">
                  {renderBoldSegments(m.content)}
                </p>
              </div>
            ))}
          </div>

          <div className="border-t p-2">
            <div className="flex gap-2">
              <Textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder="Ask or type: search meeting…"
                rows={2}
                className="min-h-[60px] resize-none text-sm"
                aria-label="Message to assistant"
              />
              <Button
                type="button"
                size="icon"
                className="h-[60px] w-11 shrink-0 self-end"
                onClick={send}
                aria-label="Send message"
              >
                <Send className="size-4" />
              </Button>
            </div>
            <p className="mt-2 px-1 text-[10px] leading-tight text-muted-foreground">
              Tips use local rules. Commands starting with “search” or “find” query your
              account on this app’s API with your session token; no third-party LLM.
            </p>
          </div>
        </div>
      ) : null}

      <Button
        type="button"
        size="lg"
        className="h-12 rounded-full px-4 shadow-md"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls={open ? panelId : undefined}
        aria-label={open ? "Close assistant" : "Open assistant"}
      >
        {open ? (
          <X className="size-5" />
        ) : (
          <>
            <MessageCircle className="size-5" />
            <span className="hidden sm:inline">Help</span>
          </>
        )}
      </Button>
    </div>
  );
}
