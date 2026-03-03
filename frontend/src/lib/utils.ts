export function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}

export function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function formatDateShort(dateString: string) {
  return new Date(dateString).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function timeAgo(dateString: string) {
  const now = new Date();
  const date = new Date(dateString);
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return "방금 전";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}분 전`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}시간 전`;
  if (seconds < 2592000) return `${Math.floor(seconds / 86400)}일 전`;
  return formatDateShort(dateString);
}

export function truncate(text: string, length: number) {
  if (text.length <= length) return text;
  return text.slice(0, length) + "...";
}

export function getCategoryLabel(category: string | null) {
  switch (category) {
    case "tech":
      return "기술 소개";
    case "troubleshooting":
      return "트러블슈팅";
    case "project":
      return "프로젝트";
    default:
      return "일반";
  }
}

export function getCategoryColor(category: string | null) {
  switch (category) {
    case "tech":
      return "bg-blue-100 text-blue-700";
    case "troubleshooting":
      return "bg-amber-100 text-amber-700";
    case "project":
      return "bg-emerald-100 text-emerald-700";
    default:
      return "bg-gray-100 text-gray-700";
  }
}
