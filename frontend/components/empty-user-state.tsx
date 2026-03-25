import Link from "next/link";

type EmptyUserStateProps = {
  title: string;
  description: string;
};

export function EmptyUserState({ title, description }: EmptyUserStateProps) {
  return (
    <section className="panel page-wrap max-w-3xl px-6 py-10 text-center">
      <span className="eyebrow">Set Up First</span>
      <h1 className="mt-5 font-display text-4xl text-ink">{title}</h1>
      <p className="mx-auto mt-4 max-w-2xl text-base leading-7 text-muted">{description}</p>
      <div className="mt-8">
        <Link href="/onboarding" className="primary-button">
          Create local profile
        </Link>
      </div>
    </section>
  );
}
