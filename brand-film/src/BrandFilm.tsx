import React from "react";
import { Series } from "remotion";
import { FPS } from "./theme";
import { Shot1 } from "./scenes/Shot1";
import { Shot2 } from "./scenes/Shot2";
import { Shot3 } from "./scenes/Shot3";
import { Shot4 } from "./scenes/Shot4";

export const BrandFilm: React.FC = () => {
  return (
    <Series>
      <Series.Sequence durationInFrames={8 * FPS} name="Shot 1 — found at 3:00 am">
        <Shot1 />
      </Series.Sequence>
      <Series.Sequence durationInFrames={8 * FPS} name="Shot 2 — you look fine">
        <Shot2 />
      </Series.Sequence>
      <Series.Sequence durationInFrames={8 * FPS} name="Shot 3 — so much better">
        <Shot3 />
      </Series.Sequence>
      <Series.Sequence durationInFrames={6 * FPS} name="Shot 4 — together">
        <Shot4 />
      </Series.Sequence>
    </Series>
  );
};
