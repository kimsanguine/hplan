import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring } from 'remotion';
import { colors, fonts, FPS } from '../theme';

/** v0.8 Core — Scene 8 — Stage 0 CTA (79-84s, 150 frames). */
export const V8CStage0: React.FC = () => {
  const frame = useCurrentFrame();
  const titleSp = spring({ frame: frame - 0, fps: FPS, config: { mass: 0.6, damping: 14 }, from: 0, to: 1 });
  const stageOp = interpolate(frame, [40, 80], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const repoOp = interpolate(frame, [90, 130], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: fonts.display,
        textAlign: 'center',
      }}
    >
      <div
        style={{
          fontSize: 64,
          fontWeight: 700,
          color: colors.text,
          opacity: titleSp,
          transform: `scale(${titleSp})`,
          letterSpacing: '-0.03em',
        }}
      >
        hplan ={' '}
        <span style={{ color: colors.hplanRed }}>WHETHER Gate</span>
      </div>

      <div
        style={{
          marginTop: 24,
          fontSize: 26,
          color: colors.dim,
          opacity: stageOp,
          letterSpacing: '-0.01em',
        }}
      >
        제품을 만들기 전에, 먼저 만들어도 되는지 검증하는 단계
      </div>

      <div
        style={{
          marginTop: 48,
          fontSize: 22,
          color: colors.veryDim,
          fontFamily: fonts.mono,
          opacity: repoOp,
        }}
      >
        habix.ai/products/hplan
      </div>
    </AbsoluteFill>
  );
};
