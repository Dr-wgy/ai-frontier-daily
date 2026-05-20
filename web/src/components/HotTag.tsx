interface HotTagProps {
  hot: string;
  level?: number;
}

export function HotTag({ hot, level }: HotTagProps) {
  if (!hot) return null;
  const tone =
    level === undefined
      ? "from-orange-500 to-rose-500"
      : level >= 0.9
        ? "from-rose-500 to-red-600"
        : level >= 0.8
          ? "from-orange-500 to-rose-500"
          : "from-amber-400 to-orange-500";
  return (
    <span
      className={`inline-flex items-center rounded-full bg-gradient-to-r ${tone} px-2 py-0.5 text-xs font-medium text-white shadow-sm`}
      aria-label={`热度 ${hot}`}
    >
      {hot}
    </span>
  );
}
