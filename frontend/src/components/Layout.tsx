import Nav from "./Nav";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen grid grid-rows-[auto_1fr] bg-[radial-gradient(1200px_600px_at_80%_-10%,rgba(79,70,229,.12),transparent),radial-gradient(800px_400px_at_-10%_10%,rgba(34,197,94,.08),transparent)]">
      <Nav />
      <main className="container py-6">{children}</main>
    </div>
  );
}
