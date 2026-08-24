import * as React from "react";
import { CheckCircle2, XCircle, Info, X } from "lucide-react";
import { cn } from "@/lib/utils";

type ToastVariant = "success" | "error" | "info";

interface Toast {
  id: string;
  title: string;
  description?: string;
  variant: ToastVariant;
}

interface ToastContextValue {
  toast: (t: Omit<Toast, "id">) => void;
}

const ToastContext = React.createContext<ToastContextValue | undefined>(undefined);

const VARIANT_STYLES: Record<ToastVariant, { icon: React.ReactNode; className: string }> = {
  success: { icon: <CheckCircle2 className="h-5 w-5 text-emerald-600" />, className: "border-emerald-200 bg-emerald-50" },
  error: { icon: <XCircle className="h-5 w-5 text-destructive" />, className: "border-red-200 bg-red-50" },
  info: { icon: <Info className="h-5 w-5 text-primary" />, className: "border-blue-200 bg-blue-50" },
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([]);

  const toast = React.useCallback((t: Omit<Toast, "id">) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { ...t, id }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((item) => item.id !== id));
    }, 4500);
  }, []);

  const dismiss = (id: string) => setToasts((prev) => prev.filter((item) => item.id !== id));

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-[100] flex w-full max-w-sm flex-col gap-2">
        {toasts.map((t) => {
          const style = VARIANT_STYLES[t.variant];
          return (
            <div
              key={t.id}
              className={cn(
                "flex items-start gap-3 rounded-lg border p-4 shadow-lg animate-in slide-in-from-bottom-2 fade-in-0",
                style.className
              )}
            >
              {style.icon}
              <div className="flex-1">
                <p className="text-sm font-medium text-foreground">{t.title}</p>
                {t.description && <p className="mt-0.5 text-xs text-muted-foreground">{t.description}</p>}
              </div>
              <button onClick={() => dismiss(t.id)} className="text-muted-foreground hover:text-foreground">
                <X className="h-4 w-4" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = React.useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within a ToastProvider");
  return ctx;
}
