import { useState, useEffect } from "react";

import "./VideoFeed.css";

const AI_IP_ADDR = "10.69.0.2:5000";

export function VideoFeed() {
  const [rand, setRand] = useState(0);
  const [errorMsg, setErrorMessage] = useState(null);
  useEffect(() => {
    setInterval(() => {
      setRand(Math.random());
      // setErrorMessage(null);
    }, 15000);
  }, []);

  const handleError = (e) => {
    console.log("got error from image load", e);
    setErrorMessage(`Unable to get video feed from ${AI_IP_ADDR}`);
  };

  const feedUrl = `http://${AI_IP_ADDR}/video_feed?rand=${rand}`;
  return (
    <div className="video-feed">
      {errorMsg ? (
        <h5>{errorMsg}</h5>
      ) : (
        <img alt="video feed" src={feedUrl} onError={handleError} />
      )}
    </div>
  );
}
