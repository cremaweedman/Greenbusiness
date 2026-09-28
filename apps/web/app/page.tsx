async function getApiHealth() {
  const internalApi = process.env.API_INTERNAL_URL ?? "http://api:8000";
  try {
    const response = await fetch(`${internalApi}/health/live`, { cache: "no-store" });
    return response.ok ? "online" : "degraded";
  } catch {
    return "offline";
  }
}

export default async function Home() {
  const api = await getApiHealth();
  return (
    <main>
      <p className="eyebrow">PHASE 0 · P0-M1</p>
      <h1>GreenBusiness</h1>
      <p>Production foundation is running.</p>
      <div className="status" aria-label={`API status: ${api}`}>
        <span aria-hidden="true" /> API: {api}
      </div>
    </main>
  );
}
