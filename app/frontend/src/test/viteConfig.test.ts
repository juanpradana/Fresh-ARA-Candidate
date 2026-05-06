// @vitest-environment node
import { describe, expect, test } from "vitest";
import config from "../../vite.config";

describe("vite proxy config", () => {
  test("routes /api to backend 8000", () => {
    const proxy = (config as { server?: { proxy?: Record<string, { target: string }> } }).server?.proxy;
    expect(proxy).toBeDefined();
    expect(proxy?.["/api"]?.target).toBe("http://127.0.0.1:8000");
  });
});
