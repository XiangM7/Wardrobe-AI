import Link from "next/link";

const featureBlocks = [
  {
    title: "Upload your real closet",
    description: "Capture tops, pants, and shoes, then fine-tune every item with color, style, season, fit, and formality tags.",
  },
  {
    title: "Align to your goals",
    description: "Tell Wardrobe AI whether you want to look taller, slimmer, cleaner, or simply feel more comfortable day to day.",
  },
  {
    title: "Get explainable outfit picks",
    description: "See three rule-based combinations from your own items, complete with scores and plain-language reasoning.",
  },
];

export default function LandingPage() {
  return (
    <div className="page-wrap space-y-10 py-10 sm:py-14">
      <section className="panel overflow-hidden">
        <div className="grid gap-10 bg-halo px-6 py-10 sm:px-10 lg:grid-cols-[1.2fr_0.8fr] lg:px-14 lg:py-14">
          <div>
            <span className="eyebrow">Wardrobe Planning MVP</span>
            <h1 className="mt-6 max-w-3xl font-display text-5xl leading-tight text-ink sm:text-6xl">
              Daily outfit recommendations that actually start from your closet.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-muted">
              Build a local style profile, upload a full-body photo, tag your closet, and get top outfit picks for school,
              work, dates, or everyday outings.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/onboarding" className="primary-button">
                Start onboarding
              </Link>
              <Link href="/recommend" className="secondary-button">
                View today outfit
              </Link>
            </div>
          </div>

          <div className="grid gap-4 self-end">
            <div className="panel-muted p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted">MVP flow</p>
              <ol className="mt-4 space-y-3 text-sm leading-7 text-ink">
                <li>1. Create a local user profile</li>
                <li>2. Upload a full-body image and preferences</li>
                <li>3. Add tops, pants, and shoes to your closet</li>
                <li>4. Generate three outfit recommendations for today</li>
              </ol>
            </div>
            <div className="panel-muted bg-[rgba(217,231,223,0.7)] p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted">Built for the MVP</p>
              <p className="mt-3 text-sm leading-7 text-ink">
                FastAPI + SQLite on the backend, Next.js + Tailwind on the frontend, and transparent rule-based scoring for every outfit.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-3">
        {featureBlocks.map((feature) => (
          <article key={feature.title} className="panel p-6">
            <span className="eyebrow">Feature</span>
            <h2 className="mt-5 font-display text-3xl text-ink">{feature.title}</h2>
            <p className="mt-4 text-base leading-7 text-muted">{feature.description}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
