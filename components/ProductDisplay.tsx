
import React from 'react';
import { ProductAnalysis } from '../types';

interface ProductDisplayProps {
  data: ProductAnalysis;
  onReset: () => void;
}

export const ProductDisplay: React.FC<ProductDisplayProps> = ({ data, onReset }) => {
  const safetyColor = data.isSafeForConsumption ? 'bg-green-900/40 border-green-500' : 'bg-red-900/40 border-red-500';

  return (
    <div className="w-full max-w-2xl mx-auto p-4 space-y-6">
      <header className="space-y-2">
        <h1 className="text-4xl font-black leading-tight">{data.productName}</h1>
        <p className="text-xl text-slate-400 font-medium">{data.brand}</p>
      </header>

      <section className={`p-6 rounded-3xl border-2 ${safetyColor}`}>
        <div className="flex items-center gap-4 mb-3">
          <div className={`p-3 rounded-full ${data.isSafeForConsumption ? 'bg-green-500' : 'bg-red-500'}`}>
            <i className={`fa-solid ${data.isSafeForConsumption ? 'fa-check' : 'fa-triangle-exclamation'} text-2xl text-white`}></i>
          </div>
          <h2 className="text-2xl font-bold">{data.isSafeForConsumption ? 'Safe' : 'Unsafe'}</h2>
        </div>
        <p className="text-lg text-slate-200 leading-relaxed">
          {data.safetyReasoning}
        </p>
      </section>

      <section className="bg-slate-800/50 p-6 rounded-3xl border border-slate-700">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <i className="fa-solid fa-chart-simple text-blue-400"></i> Macros
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <MacroCard label="Cals" value={data.nutritionalInfo.calories} icon="fa-fire" color="text-orange-400" />
          <MacroCard label="Protein" value={data.nutritionalInfo.protein} icon="fa-dumbbell" color="text-green-400" />
          <MacroCard label="Fat" value={data.nutritionalInfo.fat} icon="fa-droplet" color="text-yellow-400" />
          <MacroCard label="Carbs" value={data.nutritionalInfo.carbs} icon="fa-wheat-awn" color="text-blue-400" />
        </div>
      </section>

      {data.allergens.length > 0 && (
        <section className="bg-slate-800/50 p-6 rounded-3xl border border-slate-700">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-red-400">
            <i className="fa-solid fa-triangle-exclamation"></i> Allergens
          </h3>
          <div className="flex flex-wrap gap-2">
            {data.allergens.map((allergen, idx) => (
              <span key={idx} className="px-4 py-1 bg-red-900/30 text-red-300 border border-red-800 rounded-full font-semibold">
                {allergen}
              </span>
            ))}
          </div>
        </section>
      )}
      
      <div className="h-32"></div> {/* Spacer for overlay */}
    </div>
  );
};

const MacroCard = ({ label, value, icon, color }: { label: string, value: string, icon: string, color: string }) => (
  <div className="bg-slate-900/50 p-4 rounded-2xl flex flex-col items-center justify-center text-center border border-slate-700">
    <i className={`fa-solid ${icon} ${color} mb-1`}></i>
    <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">{label}</span>
    <span className="text-lg font-black">{value}</span>
  </div>
);
