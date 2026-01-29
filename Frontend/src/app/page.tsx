export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div
        className="text-[clamp(64px,20vw,220px)] font-bold tracking-[0.2em] text-slate-100"
        style={{
          textShadow:
            "0 0 12px rgba(255, 255, 255, 0.75), 0 0 32px rgba(0, 180, 255, 0.7), 0 0 64px rgba(0, 180, 255, 0.6)",
        }}
      >
        SKS
      </div>
    </div>
  );
}
