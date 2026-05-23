import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring } from 'remotion';
import { colors, fonts, typography, FPS } from '../theme';

const STAGES = [
  { name: 'hplan', sub: 'gate', count: 8, c: 'hplanRed' as const },
  { name: 'discover', sub: '', count: 7, c: 'skillTag' as const },
  { name: 'architect', sub: '', count: 8, c: 'skillTag' as const },
  { name: 'deliver', sub: '', count: 32, c: 'trackBlue' as const },
  { name: 'operate', sub: '', count: 17, c: 'skillTag' as const },
];

/** v0.8 Demo — Scene 5 — Lifecycle (45-60s, 450 frames). */
export const V8DLifecycle: React.FC = () => {
  const frame = useCurrentFrame();
  const titleOp = interpolate(frame, [10, 40], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const fadeOut = interpolate(frame, [430, 450], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: fonts.display,
        opacity: fadeOut,
      }}
    >
      <div style={{ fontSize: typography.titleSize, fontWeight: 300, color: colors.text, opacity: titleOp, marginBottom: 48, letterSpacing: '-0.02em' }}>
        5-plugin lifecycle · 72 skills
      </div>

      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap', justifyContent: 'center', maxWidth: 1700 }}>
        {STAGES.map((s, i) => {
          const appear = 60 + i * 25;
          const sp = spring({ frame: frame - appear, fps: FPS, config: { mass: 0.5, damping: 14 }, from: 0, to: 1 });
          return (
            <React.Fragment key={s.name}>
              <div
                style={{
                  opacity: sp,
                  transform: `scale(${sp})`,
                  padding: '10px 16px',
                  border: `1.5px solid ${colors[s.c]}`,
                  borderRadius: 6,
                  textAlign: 'center',
                  minWidth: 110,
                  backgroundColor: 'transparent',
                }}
              >
                <div style={{ fontSize: 18, fontWeight: 600, color: colors[s.c] }}>
                  {s.name}
                </div>
                {s.sub && (
                  <div style={{ fontSize: 11, color: colors[s.c], fontFamily: fonts.mono, marginTop: 1, opacity: 0.7 }}>
                    {s.sub}
                  </div>
                )}
                <div style={{ fontSize: 12, color: colors.dim, fontFamily: fonts.mono, marginTop: 2 }}>
                  {s.count} skills
                </div>
              </div>
              {i < STAGES.length - 1 && <span style={{ color: colors.veryDim, opacity: sp }}>→</span>}
            </React.Fragment>
          );
        })}
      </div>

      <div style={{ marginTop: 48, fontSize: typography.bodySize, color: colors.dim, opacity: interpolate(frame, [320, 360], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }), letterSpacing: '-0.01em' }}>
        v0.9 · hplan → discover → architect → deliver → operate
      </div>
    </AbsoluteFill>
  );
};
