"use client";

import { useState, useRef } from "react";
import { api } from "@/lib/api";
import { SimulateResponse, ApiError } from "@/lib/types";
import { LOADING_STAGES, LoadingStage } from "@/lib/constants";

type SimulationState =
  | { status: "idle" }
  | { status: "loading"; stage: LoadingStage }
  | { status: "success"; data: SimulateResponse }
  | { status: "error"; message: string; stage: string };

export function useSimulation() {
  const [state, setState] = useState<SimulationState>({ status: "idle" });
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  function clearStageTimer() {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }

  async function run(url: string) {
    setState({ status: "loading", stage: "scraping" });

    // Advance through fake stages every 8s for UX while the single request is in flight
    let stageIndex = 0;
    timerRef.current = setInterval(() => {
      stageIndex = Math.min(stageIndex + 1, LOADING_STAGES.length - 1);
      setState({
        status: "loading",
        stage: LOADING_STAGES[stageIndex].key,
      });
    }, 8000);

    try {
      const data = await api.simulate({ url });
      clearStageTimer();
      setState({ status: "success", data });
    } catch (err) {
      clearStageTimer();
      if (err instanceof ApiError) {
        setState({ status: "error", message: err.message, stage: err.stage });
      } else {
        setState({
          status: "error",
          message: err instanceof Error ? err.message : "Unknown error",
          stage: "unknown",
        });
      }
    }
  }

  function reset() {
    clearStageTimer();
    setState({ status: "idle" });
  }

  return { state, run, reset };
}
