import React from 'react';
import { BasicStats, CapabilityStats } from '../types';
import { Card } from './Card';
import { ChartIcon } from './icons';

interface StatsSummaryProps {
  basicStats: BasicStats;
  capability: CapabilityStats;
}

const StatItem: React.FC<{ label: string; value: string | number | undefined; color?: string }> = ({ label, value, color = 'text-cyan-400' }) => (
  <div className="flex justify-between items-baseline p-3 bg-gray-800 rounded-lg">
    <span className="text-sm text-gray-400">{label}</span>
    <span className={`text-lg font-semibold ${color}`}>{value ?? 'N/A'}</span>
  </div>
);

export const StatsSummary: React.FC<StatsSummaryProps> = ({ basicStats, capability }) => {
  const { count, mean, stdDev, min, max, skewness, kurtosis, pValue } = basicStats;
  const { ppk, cpk, cp, pp } = capability;

  const getCapabilityColor = (value: number | undefined) => {
    if (value === undefined) return 'text-gray-500';
    if (value >= 1.33) return 'text-green-400';
    if (value >= 1.00) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getPValueColor = (value: number | undefined) => {
    if (value === undefined) return 'text-gray-500';
    if (value > 0.05) return 'text-green-400';
    return 'text-red-400';
  };

  return (
    <Card title="Statistical Summary" icon={<ChartIcon />}>
      <div className="space-y-4">
        <div>
          <h4 className="font-semibold text-gray-200 mb-2">Process Capability</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <StatItem label="Cp" value={cp?.toFixed(3)} color={getCapabilityColor(cp)} />
            <StatItem label="Cpk" value={cpk?.toFixed(3)} color={getCapabilityColor(cpk)} />
            <StatItem label="Pp" value={pp?.toFixed(3)} color={getCapabilityColor(pp)} />
            <StatItem label="Ppk" value={ppk?.toFixed(3)} color={getCapabilityColor(ppk)} />
          </div>
        </div>
        <div>
          <h4 className="font-semibold text-gray-200 mb-2">Descriptive Statistics</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <StatItem label="Count" value={count} />
            <StatItem label="Mean" value={mean.toFixed(3)} />
            <StatItem label="Std. Dev." value={stdDev.toFixed(3)} />
            <StatItem label="Min" value={min.toFixed(3)} />
            <StatItem label="Max" value={max.toFixed(3)} />
          </div>
        </div>
        <div>
          <h4 className="font-semibold text-gray-200 mb-2">Normality Statistics</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <StatItem label="Skewness" value={skewness.toFixed(3)} />
            <StatItem label="Kurtosis" value={kurtosis.toFixed(3)} />
             <div className="sm:col-span-2">
                <StatItem label="P-value (Jarque-Bera)" value={pValue < 0.0001 ? '< 0.0001' : pValue.toFixed(4)} color={getPValueColor(pValue)} />
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};