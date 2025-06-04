// app/(main)/layout.tsx
import Sidebar from "../components/Sidebar";
import Providers from "../providers";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <Providers>
      <div className="flex h-screen w-screen">
        <aside className="w-[25%] min-w-[200px] max-w-[280px] border-r bg-gray-50">
          <Sidebar />
        </aside>
        <main className="w-[75%] p-8 overflow-auto">{children}</main>
      </div>
    </Providers>
  );
}
