import { formatDistanceToNowStrict } from 'date-fns'

export function timeAgo(dateString) {
  try {
    return formatDistanceToNowStrict(new Date(dateString), { addSuffix: true })
  } catch {
    return ''
  }
}
