import type { Route } from "./+types/home";
import Dashboard from "../pages/dashboard";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "intelRead" },
    { name: "description", content: "Welcome to intelRead!" },
  ];
}

export default function Home() {
  return (
    <>
      <Dashboard />

    </>
  );
}
