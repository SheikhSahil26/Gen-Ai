export function isAwaitingCheckoutApproval(message = "") {
  return /(would you like me to (proceed|place)|reply [“\"']?(yes|confirm)|please confirm (this|your) order|awaiting_confirmation)/i.test(message)
}
