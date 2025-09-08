type Article = {
  id: number;
  title: string;
  description?: string;
  source?: string;
  url: string;
  image_url?: string;
  published_at: string;
  sentiment?: { label?: string; score?: number | null };
};

export default function NewsList({ articles }: { articles: Article[] }) {
  if (!articles?.length) return null;
  return (
    <div className="grid md:grid-cols-2 gap-3">
      {articles.map((a) => (
        <a
          key={a.id}
          href={a.url}
          target="_blank"
          rel="noreferrer"
          className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 hover:bg-slate-800/60 transition"
        >
          <div className="flex gap-3">
            {a.image_url ? (
              <img
                src={a.image_url}
                alt=""
                className="w-24 h-24 object-cover rounded-md border border-slate-800"
              />
            ) : null}
            <div className="flex-1">
              <div className="text-sm font-medium">{a.title}</div>
              <div className="text-xs mt-1 opacity-70 line-clamp-2">
                {a.description || ""}
              </div>
              <div className="text-[11px] mt-2 opacity-60">
                {a.source ? `${a.source} • ` : ""}
                {new Date(a.published_at).toLocaleString()}
                {a.sentiment?.label ? (
                  <span className="ml-2 px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700">
                    {a.sentiment.label}
                    {typeof a.sentiment.score === "number"
                      ? ` (${(a.sentiment.score * 100).toFixed(0)}%)`
                      : ""}
                  </span>
                ) : null}
              </div>
            </div>
          </div>
        </a>
      ))}
    </div>
  );
}
