import "./QRCode.css";

export function QRCode() {
  return (
    <div className="qr-code">
      <img alt="QR code" src="/github-qr-code.png" />
      <div className="qr-code-text">
        <h3>Visit us on Github today!</h3>
      </div>
    </div>
  );
}
