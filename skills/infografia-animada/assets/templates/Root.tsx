import "./index.css";
import { Composition } from "remotion";
import { Infografia } from "./infografia/Infografia";

// Adjust id, dimensions, fps and duration to what the user agreed.
// Entrances should finish by roughly 60 percent of durationInFrames.
export const RemotionRoot: React.FC = () => (
  <Composition
    id="Infografia"
    component={Infografia}
    durationInFrames={390}
    fps={30}
    width={960}
    height={1280}
  />
);
