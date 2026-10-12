export function formatMoney(value, currency = "INR") {
  const amount = Number(value || 0)
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(Number.isFinite(amount) ? amount : 0)
}

export function formatDate(value) {
  if (!value) return "Date unavailable"
  const date = new Date(value.replace(" ", "T"))
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat("en-IN", { dateStyle: "medium" }).format(date)
}

export function humanize(value = "") {
  return value.replaceAll("_", " ").replace(/\b\w/g, character => character.toUpperCase())
}
