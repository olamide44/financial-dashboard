import Nav from "./Nav";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen grid grid-rows-[auto_1fr]">
      <Nav />
      <main className="p-4 max-w-7xl mx-auto w-full">{children}</main>
    </div>
  );
}
