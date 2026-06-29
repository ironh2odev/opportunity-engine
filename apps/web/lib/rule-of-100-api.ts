import type {
  ApprovalRecord,
  DailyAction,
  DailyActionStatus,
  DailyRollup,
  RuleOf100Plan,
} from "@aoe/shared-types";

export interface ApiError {
  message: string;
  status: number;
}

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Fields whose values are ActionChannel enum keys (snake_case), not plain object field names.
// Do not recursively transform inside these fields.
const ENUM_KEYED_FIELDS = new Set(["allocation", "by_channel", "byChannel"]);

function toCamel(s: string): string {
  return s.replace(/_([a-z])/g, (_, c: string) => c.toUpperCase());
}

function transformKeys<T>(value: unknown, skipChildren = false): T {
  if (Array.isArray(value)) {
    return value.map((item) => transformKeys(item, skipChildren)) as unknown as T;
  }
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([k, v]) => {
        const newKey = toCamel(k);
        const childSkip = skipChildren || ENUM_KEYED_FIELDS.has(k) || ENUM_KEYED_FIELDS.has(newKey);
        return [newKey, transformKeys(v, childSkip)];
      }),
    ) as T;
  }
  return value as T;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data: unknown = await res.json();
  if (!res.ok) {
    const err = data as { detail?: string };
    const apiErr: ApiError = {
      message: err.detail ?? `Request failed (${res.status})`,
      status: res.status,
    };
    throw apiErr;
  }
  return transformKeys<T>(data);
}

export const ruleOf100Api = {
  getPlan(): Promise<RuleOf100Plan> {
    return apiFetch<RuleOf100Plan>("/rule-of-100/today-plan");
  },

  getActions(date?: string): Promise<DailyAction[]> {
    const query = date ? `?date=${encodeURIComponent(date)}` : "";
    return apiFetch<DailyAction[]>(`/rule-of-100/actions${query}`);
  },

  getRollup(): Promise<DailyRollup> {
    return apiFetch<DailyRollup>("/rule-of-100/rollup");
  },

  approveAction(actionId: string): Promise<ApprovalRecord> {
    return apiFetch<ApprovalRecord>(
      `/rule-of-100/actions/${encodeURIComponent(actionId)}/approve`,
      {
        method: "POST",
        body: JSON.stringify({
          approved_by: "human.operator",
          note: "Approved for manual execution. No auto-send or auto-apply.",
        }),
      },
    );
  },

  completeAction(actionId: string): Promise<DailyAction> {
    return apiFetch<DailyAction>(
      `/rule-of-100/actions/${encodeURIComponent(actionId)}/complete`,
      { method: "POST" },
    );
  },

  updateStatus(actionId: string, status: DailyActionStatus): Promise<DailyAction> {
    return apiFetch<DailyAction>(
      `/rule-of-100/actions/${encodeURIComponent(actionId)}/status`,
      {
        method: "PATCH",
        body: JSON.stringify({ status }),
      },
    );
  },
};
