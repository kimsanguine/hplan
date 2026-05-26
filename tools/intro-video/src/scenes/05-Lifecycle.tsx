import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';
import { colors, fonts } from '../theme';
import { PluginBox } from '../components/PluginBox';
import { BigStat } from '../components/BigStat';
import { LIFECYCLE } from '../data/lifecycle';

/**
 * Scene 5 — Lifecycle reveal (55-63s, 240 frames).
 * 7 plugin boxes appear sequentially with arrows, then big stats fade in.
 * v0.7: operate plugin added; stat targets updated to 7/50/18.
 */
export const SceneLifecycle: React.FC = () => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: 'clamp' });

  // Each box appears every 12 frames (0.4s)
  const boxAppearFrames = LIFECYCLE.map((_, i) => 15 + i * 14);
  // Arrows appear between consecutive boxes
  const arrowAppearFrames = LIFECYCLE.slice(0, -1).map((_, i) => 22 + i * 14);

  // Stats appear after all boxes are in (~ frame 110)
  const statsAppearAt = 130;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        fontFamily: fonts.display,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 60,
        opacity: fadeIn,
      }}
    >
      <div
        style={{
          fontSize: 16,
          color: colors.veryDim,
          letterSpacing: 3,
          textTransform: 'uppercase',
          marginBottom: 32,
        }}
      >
        PM 라이프사이클 전체 — hplan marketplace
      </div>

      {/* Lifecycle row with arrows */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          marginBottom: 56,
        }}
      >
        {LIFECYCLE.map((stage, idx) => (
          <React.Fragment key={stage.name}>
            <PluginBox
              appearAt={boxAppearFrames[idx]}
              name={stage.name}
              phase={stage.phase}
              count={stage.count}
              color={stage.color}
              borderColor={stage.borderColor}
              flagship={stage.flagship}
              width={150}
              height={120}
            />
            {idx < LIFECYCLE.length - 1 && (
              <Arrow appearAt={arrowAppearFrames[idx]} />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Big stats row */}
      <div
        style={{
          display: 'flex',
          gap: 96,
          alignItems: 'flex-end',
        }}
      >
        <BigStat appearAt={statsAppearAt} target={5} label="plugins" fontSize={80} />
        <BigStat appearAt={statsAppearAt + 12} target={46} label="skills" fontSize={80} color={colors.skillTag} />
        <BigStat appearAt={statsAppearAt + 24} target={9} label="commands" fontSize={80} color={colors.arrow} />
      </div>
    </AbsoluteFill>
  );
};

const Arrow: React.FC<{ appearAt: number }> = ({ appearAt }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [appearAt, appearAt + 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div
      style={{
        color: colors.veryDim,
        fontSize: 24,
        opacity,
      }}
    >
      →
    </div>
  );
};
