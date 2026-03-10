import ReactMarkdown from "react-markdown";

export function LegalMarkdown({ content }: { content: string }) {
  return (
    <div className="space-y-6 [&_a]:text-sky-300 [&_a]:underline [&_a]:underline-offset-4 [&_h1]:scroll-m-20 [&_h1]:text-3xl [&_h1]:font-semibold [&_h1]:tracking-tight [&_h2]:scroll-m-20 [&_h2]:border-b [&_h2]:border-white/10 [&_h2]:pb-2 [&_h2]:text-2xl [&_h2]:font-semibold [&_h3]:scroll-m-20 [&_h3]:text-xl [&_h3]:font-semibold [&_li]:ml-5 [&_li]:list-disc [&_li]:py-1 [&_p]:leading-7 [&_strong]:font-semibold">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}
