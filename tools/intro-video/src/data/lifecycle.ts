/**
 * 5 plugins in lifecycle order — used by Scene 5.
 * v0.10.1: Gate/Discover/Architect/Deliver/Operate · 46 skills total.
 */
import { colors } from '../theme';

export interface LifecycleStage {
  name: string;
  phase: string;
  count: string;
  color: string;
  borderColor?: string;
  flagship?: boolean;
}

export const LIFECYCLE: LifecycleStage[] = [
  {
    name: 'hplan',
    phase: 'Gate',
    count: '8 skills',
    color: colors.hplanRedSoft,
    borderColor: colors.hplanRed,
    flagship: true,
  },
  {
    name: 'discover',
    phase: 'Discover',
    count: '6 skills',
    color: '#6366f1',
  },
  {
    name: 'architect',
    phase: 'Architect',
    count: '7 skills',
    color: '#8b5cf6',
  },
  {
    name: 'deliver',
    phase: 'Deliver',
    count: '13 skills',
    color: '#f59e0b',
  },
  {
    name: 'operate',
    phase: 'Operate',
    count: '12 skills',
    color: '#0ea5e9',
  },
];
