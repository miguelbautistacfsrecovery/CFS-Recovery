import "./index.css";
import { Composition, Folder } from "remotion";
import { BrandFilm } from "./BrandFilm";
import { Shot1 } from "./scenes/Shot1";
import { Shot2 } from "./scenes/Shot2";
import { Shot3 } from "./scenes/Shot3";
import { Shot4 } from "./scenes/Shot4";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="BrandFilm"
        component={BrandFilm}
        durationInFrames={720}
        fps={24}
        width={1920}
        height={1080}
      />
      <Folder name="Shots">
        <Composition
          id="Shot1"
          component={Shot1}
          durationInFrames={192}
          fps={24}
          width={1920}
          height={1080}
        />
        <Composition
          id="Shot2"
          component={Shot2}
          durationInFrames={192}
          fps={24}
          width={1920}
          height={1080}
        />
        <Composition
          id="Shot3"
          component={Shot3}
          durationInFrames={192}
          fps={24}
          width={1920}
          height={1080}
        />
        <Composition
          id="Shot4"
          component={Shot4}
          durationInFrames={144}
          fps={24}
          width={1920}
          height={1080}
        />
      </Folder>
    </>
  );
};
