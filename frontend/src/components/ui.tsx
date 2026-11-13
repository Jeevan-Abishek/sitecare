export function Button({ children, loading = false, className = "", ...props }: any) {
  return (
    <button
      disabled={loading}
      className={`inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-navy-900 text-white hover:bg-navy-800 disabled:opacity-60 disabled:pointer-events-none transition-colors ${className}`}
      {...props}
    >
      {loading ? "Working..." : children}
    </button>
  );
}
