"use client";

import { apiFetch } from "./api";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  institution_id: string;
  institution_name: string;
}

const DEMO_EMAIL = "admin@beu.edu.az";
const DEMO_PASSWORD = "demo123";

export async function login(email: string, password: string) {
  const data = await apiFetch<{
    access_token: string;
    refresh_token: string;
  }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);
  return data;
}

export async function autoLoginDemo(): Promise<boolean> {
  try {
    await login(DEMO_EMAIL, DEMO_PASSWORD);
    return true;
  } catch {
    return false;
  }
}

export async function getMe(): Promise<User> {
  return apiFetch<User>("/auth/me");
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/dashboard";
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("access_token");
}
