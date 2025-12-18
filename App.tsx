
import React, { useState } from 'react';
import { CameraView } from './components/CameraView';
import { ProductDisplay } from './components/ProductDisplay';
import { VoiceAnnouncer } from './components/VoiceAnnouncer';
import { TactileOverlay } from './components/TactileOverlay';
import { analyzeProductImage } from './services/geminiService';
import { HapticService } from './services/hapticService';
import { AppState, ProductAnalysis } from './types';

const App: React.FC = () => {
  const [state, setState] = useState<AppState>('IDLE');
  const [result, setResult] = useState<ProductAnalysis | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [voiceMsg, setVoiceMsg] = useState<string>('Welcome to EchoText. Tap the large center button to scan.');

  const handleStartScan = () => {
    HapticService.vibrate(20);
    setVoiceMsg('Camera opened. Point your phone at the product. Large scan button is at the bottom.');
    setState('CAPTURING');
  };

  const handleCapture = async (base64: string) => {
    HapticService.capture();
    setState('ANALYZING');
    setVoiceMsg('Analyzing image. Please wait.');
    try {
      const data = await analyzeProductImage(base64);
      setResult(data);
      setState('RESULT');
      
      if (!data.isSafeForConsumption || (data.allergens && data.allergens.length > 0)) {
        HapticService.danger();
      } else {
        HapticService.success();
      }

      const summary = `Found ${data.brand} ${data.productName}. It is ${data.isSafeForConsumption ? 'safe' : 'potentially unsafe'} to consume. ${data.nutritionalInfo.calories} calories.`;
      setVoiceMsg(summary);
    } catch (err) {
      console.error(err);
      HapticService.error();
      setErrorMsg('Failed to analyze product. Please try again.');
      setVoiceMsg('Error analyzing the product. Please try again.');
      setState('ERROR');
    }
  };

  const handleReset = () => {
    HapticService.vibrate(20);
    setResult(null);
    setErrorMsg('');
    setState('IDLE');
    setVoiceMsg('Ready for next scan.');
  };

  const repeatSummary = () => {
    if (result) {
      HapticService.vibrate(10);
      setVoiceMsg(`Repeating: ${result.brand} ${result.productName}. Safety status: ${result.isSafeForConsumption ? 'Safe' : 'Unsafe'}. ${result.safetyReasoning}`);
    }
  };

  const readAllergens = () => {
    if (result) {
      HapticService.vibrate(10);
      const msg = result.allergens.length > 0 
        ? `Contains the following allergens: ${result.allergens.join(', ')}.` 
        : "No allergens identified.";
      setVoiceMsg(msg);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 pb-10 select-none">
      <VoiceAnnouncer message={voiceMsg} trigger={voiceMsg} />

      {state === 'IDLE' && (
        <div className="flex flex-col items-center justify-center min-h-screen px-6 text-center">
          <div className="w-32 h-32 bg-blue-600 rounded-full flex items-center justify-center mb-8 shadow-[0_0_50px_rgba(37,99,235,0.4)]">
            <i className="fa-solid fa-eye text-6xl text-white"></i>
          </div>
          <h1 className="text-5xl font-black mb-4 tracking-tight">EchoText</h1>
          <p className="text-xl text-slate-400 max-w-md mb-12 leading-relaxed font-medium">
            Helping you see through labels. 
          </p>
          
          <button 
            onClick={handleStartScan}
            className="w-full max-w-sm py-12 bg-blue-600 hover:bg-blue-500 rounded-3xl text-3xl font-black shadow-2xl accessible-focus active:scale-95 transition-all flex items-center justify-center gap-4 border-4 border-blue-400"
            aria-label="Scan Product"
          >
            <i className="fa-solid fa-camera"></i>
            SCAN
          </button>
        </div>
      )}

      {state === 'CAPTURING' && (
        <CameraView onCapture={handleCapture} onCancel={handleReset} />
      )}

      {state === 'ANALYZING' && (
        <div className="flex flex-col items-center justify-center min-h-screen p-8 text-center">
          <div className="relative w-24 h-24 mb-10">
            <div className="absolute inset-0 border-4 border-blue-600/30 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
            <i className="fa-solid fa-magnifying-glass absolute inset-0 flex items-center justify-center text-3xl text-blue-400"></i>
          </div>
          <h2 className="text-3xl font-black mb-2">Analyzing...</h2>
          <p className="text-slate-400 text-lg animate-pulse">Checking nutritional facts</p>
        </div>
      )}

      {state === 'RESULT' && result && (
        <div className="relative pt-8 px-4 animate-in fade-in slide-in-from-bottom-8 duration-500">
          <TactileOverlay 
            onRepeatSummary={repeatSummary} 
            onReadAllergens={readAllergens} 
            onNewScan={handleReset} 
          />
          <div className="opacity-80">
            <ProductDisplay data={result} onReset={handleReset} />
          </div>
        </div>
      )}

      {state === 'ERROR' && (
        <div className="flex flex-col items-center justify-center min-h-screen p-8 text-center">
          <div className="w-20 h-20 bg-red-900/30 rounded-full flex items-center justify-center mb-6 border-2 border-red-500">
            <i className="fa-solid fa-circle-exclamation text-4xl text-red-500"></i>
          </div>
          <h2 className="text-3xl font-black mb-4">Scan Failed</h2>
          <button 
            onClick={handleReset}
            className="w-full max-w-xs py-8 bg-slate-800 hover:bg-slate-700 rounded-2xl text-xl font-bold transition-all accessible-focus border-2 border-slate-600"
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  );
};

export default App;
