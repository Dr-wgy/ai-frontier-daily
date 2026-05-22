interface HotTagProps {
  hot: string;
  level?: number;
}

export function HotTag({ hot, level }: HotTagProps) {
  if (!hot) return null;
  const tone =
    level === undefined
      ? "from-amber-400 to-orange-500"
      : level >= 0.9
        ? "from-rose-400 to-red-500"
        : level >= 0.8
          ? "from-amber-400 to-orange-500"
          : "from-amber-300 to-amber-500";
  return (
    <span
      className={`inline-flex items-center rounded-full bg-gradient-to-r ${tone} px-1.5 py-px text-[10px] font-medium text-black`}
      aria-label={`热度 ${hot}`}
    >
      {hot}
    </span>
  );
}
