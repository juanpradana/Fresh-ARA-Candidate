// @vitest-environment node
import { describe, expect, test } from "vitest";
import config from "../../vite.config";

describe("vite proxy config", () => {
  test("routes /api to backend env target in dev server", () => {
    const expectedTarget = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env?.VITE_API_PROXY_TARGET ?? "http://127.0.0.1:8000";
    const proxy = (config as { server?: { proxy?: Record<string, { target: string }> } }).server?.proxy;
    expect(proxy).toBeDefined();
    expect(proxy?.["/api"]?.target).toBe(expectedTarget);
  });

  test("routes /api to backend env target in preview server", () => {
    const expectedTarget = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env?.VITE_API_PROXY_TARGET ?? "http://127.0.0.1:8000";
    const proxy = (config as { preview?: { proxy?: Record<string, { target: string }> } }).preview?.proxy;
    expect(proxy).toBeDefined();
    expect(proxy?.["/api"]?.target).toBe(expectedTarget);
  });
});
