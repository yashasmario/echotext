
import React from 'react';

interface TactileOverlayProps {
  onRepeatSummary: () => void;
  onReadAllergens: () => void;
  onNewScan: () => void;
}

export const TactileOverlay: React.FC<TactileOverlayProps> = ({ 
  onRepeatSummary, 
  onReadAllergens, 
  onNewScan 
}) => {
  return (
    <div className="fixed inset-0 z-40 pointer-events-none grid grid-cols-2 grid-rows-2">
      <button
        onClick={(e) => { e.stopPropagation(); onRepeatSummary(); }}
        className="pointer-events-auto bg-blue-500/5 active:bg-blue-500/20 border-r border-b border-white/10 flex flex-col items-center justify-center p-4 transition-colors accessible-focus"
        aria-label="Repeat product summary"
      >
        <i className="fa-solid fa-volume-high text-3xl mb-2 text-blue-400/50"></i>
        <span className="text-xs font-bold uppercase tracking-tighter text-blue-400/40">Repeat Info</span>
      </button>

      <button
        onClick={(e) => { e.stopPropagation(); onReadAllergens(); }}
        className="pointer-events-auto bg-red-500/5 active:bg-red-500/20 border-b border-white/10 flex flex-col items-center justify-center p-4 transition-colors accessible-focus"
        aria-label="Read allergens"
      >
        <i className="fa-solid fa-skull-crossbones text-3xl mb-2 text-red-400/50"></i>
        <span className="text-xs font-bold uppercase tracking-tighter text-red-400/40">Allergens</span>
      </button>

      <button
        onClick={(e) => { e.stopPropagation(); onNewScan(); }}
        className="pointer-events-auto col-span-2 bg-slate-500/5 active:bg-slate-500/20 flex flex-col items-center justify-center p-4 transition-colors accessible-focus"
        aria-label="Start new scan"
      >
        <i className="fa-solid fa-camera text-4xl mb-2 text-slate-400/50"></i>
        <span className="text-lg font-black uppercase tracking-widest text-slate-400/40">New Scan</span>
      </button>
    </div>
  );
};
