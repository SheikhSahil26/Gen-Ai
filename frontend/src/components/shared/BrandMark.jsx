export function BrandMark({ small = false }) {
  return <span className={`brand-mark${small ? " brand-mark-small" : ""}`} aria-hidden="true"><i/><i/><i/><i/></span>
}
