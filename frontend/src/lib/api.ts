import { SimulateRequest, SimulateResponse, ApiError } from "./types";

const BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export const api = {
  async simulate(req: SimulateRequest): Promise<SimulateResponse> {
    const res = await fetch(`${BASE_URL}/api/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
      signal: AbortSignal.timeout(90_000),
    });

    if (!res.ok) {
      let detail = "Something went wrong";
      let stage = "unknown";
      try {
        const err = await res.json();
        detail = err.detail?.detail ?? err.detail ?? detail;
        stage = err.detail?.stage ?? stage;
      } catch {}
      throw new ApiError(detail, stage);
    }

    return res.json();
  },
};
