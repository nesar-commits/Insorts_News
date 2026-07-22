import {
  Newspaper,
  Globe,
  Cpu,
  Briefcase,
  Trophy,
  Film,
  HeartPulse,
  FlaskConical,
  LayoutGrid,
} from 'lucide-react'

const ICON_MAP = {
  newspaper: Newspaper,
  globe: Globe,
  cpu: Cpu,
  briefcase: Briefcase,
  trophy: Trophy,
  film: Film,
  'heart-pulse': HeartPulse,
  'flask-conical': FlaskConical,
}

export function getCategoryIcon(iconKey) {
  return ICON_MAP[iconKey] || LayoutGrid
}
