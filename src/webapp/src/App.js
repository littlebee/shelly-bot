import { Carousel } from "react-responsive-carousel";
import "react-responsive-carousel/lib/styles/carousel.min.css";

import { VideoFeed } from "./VideoFeed";
import { QRCode } from "./QRCode";

import "./App.css";

function App() {
  return (
    <div className="App">
      <div className="left-column">
        <VideoFeed />
        <QRCode />
      </div>
      <div className="right-column">
        <Carousel
          className="carousel"
          autoPlay={true}
          infiniteLoop={true}
          swipeable={true}
          interval={10000}
          showIndicators={true}
          showArrows={true}
          stopOnHover={false}
        >
          <div className="title">
            <h1>shelly-bot by Bee</h1>
            <p className="byline">
              An experiment to see if I can build a bot that remembers names
              better than my friend Shelly.
            </p>
            <h2>Attribution</h2>
            <ul>
              <li>
                <p>
                  <em>Icarus1uk@thingiverse.com</em> - 3d model for face
                </p>
              </li>
              <li>
                <p>
                  <em>i080457@thingiverse.com</em> - 3d model for neck pan and
                  tilt
                </p>
              </li>
            </ul>
          </div>
          <div>
            <h1>shelly-bot says,</h1>
            <p>Fuck off, I'm working here.</p>
          </div>
        </Carousel>
      </div>
    </div>
  );
}

export default App;
