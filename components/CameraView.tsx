
import React, { useRef, useState, useEffect } from 'react';

interface CameraViewProps {
  onCapture: (base64: string) => void;
  onCancel: () => void;
}

export const CameraView: React.FC<CameraViewProps> = ({ onCapture, onCancel }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let activeStream: MediaStream | null = null;

    async function setupCamera() {
      try {
        // Only request access when the component is mounted (user clicked SCAN)
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { facingMode: 'environment' }, 
          audio: false 
        });
        activeStream = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Camera access error:", err);
        setError("Could not access camera. Please ensure permissions are granted and you are using HTTPS.");
      }
    }
    
    setupCamera();

    // Cleanup: This runs as soon as the component unmounts 
    // (e.g., when moving to ANALYZING or back to IDLE)
    return () => {
      if (activeStream) {
        activeStream.getTracks().forEach(track => {
          track.stop(); // Explicitly stop each track to release the hardware
          console.debug("Camera track stopped:", track.label);
        });
      }
    };
  }, []);

  const handleCapture = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
        onCapture(dataUrl);
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black flex flex-col items-center justify-between p-6">
      <div className="w-full flex justify-between items-center mb-4">
        <button 
          onClick={onCancel}
          className="p-4 bg-gray-800 rounded-full accessible-focus"
          aria-label="Cancel and go back"
        >
          <i className="fa-solid fa-xmark text-2xl"></i>
        </button>
        <h2 className="text-xl font-bold">Align Product in View</h2>
        <div className="w-12"></div>
      </div>

      <div className="relative flex-1 w-full max-w-md rounded-2xl overflow-hidden bg-gray-900 shadow-2xl border border-white/10">
        <video 
          ref={videoRef} 
          autoPlay 
          playsInline 
          muted
          className="w-full h-full object-cover"
        />
        {error && (
          <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center bg-slate-900/90">
            <i className="fa-solid fa-video-slash text-4xl text-red-500 mb-4"></i>
            <p className="text-red-400 font-medium">{error}</p>
          </div>
        )}
      </div>

      <div className="w-full max-w-md mt-8 pb-10">
        <button 
          onClick={handleCapture}
          disabled={!!error}
          className={`w-full py-8 rounded-3xl text-2xl font-extrabold flex items-center justify-center gap-4 accessible-focus shadow-lg active:scale-95 transition-all ${
            error ? 'bg-gray-700 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500'
          }`}
          aria-label="Capture photo for analysis"
        >
          <i className="fa-solid fa-camera text-4xl"></i>
          SCAN PRODUCT
        </button>
        <p className="text-center mt-4 text-gray-400 text-sm">
          The camera will close immediately after scanning.
        </p>
      </div>

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};
