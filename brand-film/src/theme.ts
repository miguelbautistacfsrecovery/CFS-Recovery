import { Easing, staticFile } from "remotion";
import { loadFont } from "@remotion/fonts";

loadFont({
  family: "Montserrat",
  url: staticFile("Montserrat-Medium.woff2"),
  weight: "500",
});

export const FONT = "Montserrat";

export const COLORS = {
  bg: "#FAF9F6",
  ink: "#2C2C2A",
  grey: "#ABA69D",
  greySoft: "#E5E2DB",
  cyan: "#00AEEF",
};

// 1.5pt at editorial print scale, held constant across every element.
export const STROKE = 3;

export const FPS = 24;

// Slow, deliberate ease in/out. No bounce, no overshoot.
export const EASE = Easing.bezier(0.55, 0, 0.25, 1);
