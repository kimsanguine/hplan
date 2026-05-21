import React from 'react';
import { Composition } from 'remotion';
import { HplanIntro16x9 } from './compositions/HplanIntro16x9';
import { HplanIntro1x1 } from './compositions/HplanIntro1x1';
import { HplanIntro9x16 } from './compositions/HplanIntro9x16';
import { HplanV8Editorial } from './compositions/HplanV8Editorial';
import { HplanV8Demo } from './compositions/HplanV8Demo';
import { HplanV8Core } from './compositions/HplanV8Core';
import { HplanV8CoreTrack } from './compositions/HplanV8CoreTrack';
import { FPS, TOTAL_FRAMES, V8E_TOTAL, V8D_TOTAL, V8C_TOTAL, V8CT_TOTAL } from './theme';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="HplanIntro16x9"
        component={HplanIntro16x9}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1920}
        height={1080}
      />
      <Composition
        id="HplanIntro1x1"
        component={HplanIntro1x1}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1080}
        height={1080}
      />
      <Composition
        id="HplanIntro9x16"
        component={HplanIntro9x16}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1080}
        height={1920}
      />
      {/* v0.8 Editorial — 60s, 메시지 위주 */}
      <Composition
        id="HplanV8Editorial"
        component={HplanV8Editorial}
        durationInFrames={V8E_TOTAL}
        fps={FPS}
        width={1920}
        height={1080}
      />
      {/* v0.8 Demo — 90s, 시스템·데모 위주 */}
      <Composition
        id="HplanV8Demo"
        component={HplanV8Demo}
        durationInFrames={V8D_TOTAL}
        fps={FPS}
        width={1920}
        height={1080}
      />
      {/* v0.8 Core — 84s, hplan 본질 (Build Gate · WHETHER vs HOW) 위주 */}
      <Composition
        id="HplanV8Core"
        component={HplanV8Core}
        durationInFrames={V8C_TOTAL}
        fps={FPS}
        width={1920}
        height={1080}
      />
      {/* v0.8 Core + Track — 99s, Core 위에 track 만들기-중 가드레일 추가 */}
      <Composition
        id="HplanV8CoreTrack"
        component={HplanV8CoreTrack}
        durationInFrames={V8CT_TOTAL}
        fps={FPS}
        width={1920}
        height={1080}
      />
      {/* v0.9 Core — 5-plugin lifecycle */}
      <Composition
        id="HplanV9Core"
        component={HplanV8CoreTrack}
        durationInFrames={V8CT_TOTAL}
        fps={FPS}
        width={1920}
        height={1080}
      />
    </>
  );
};
