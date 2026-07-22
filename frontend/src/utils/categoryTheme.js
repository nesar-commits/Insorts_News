export const CATEGORY_GRADIENTS = {
  general: 'from-slate-600 to-slate-800',
  world: 'from-blue-600 to-indigo-800',
  technology: 'from-indigo-500 to-violet-800',
  business: 'from-emerald-600 to-teal-800',
  sports: 'from-orange-500 to-rose-700',
  entertainment: 'from-fuchsia-600 to-purple-800',
  health: 'from-rose-500 to-pink-800',
  science: 'from-cyan-600 to-blue-800',
}

export function getCategoryGradient(slug) {
  return CATEGORY_GRADIENTS[slug] || CATEGORY_GRADIENTS.general
}
