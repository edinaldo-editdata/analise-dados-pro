import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Scatter } from 'recharts';
import { Card } from './Card';
import { ChartIcon } from './icons';
import { ControlChartData } from '../types';

interface RChartProps {
  data: ControlChartData;
  dataPrecision: number;
}

const ruleDescriptions: { [key: string]: string } = {
    rule1: "Rule 1: Points outside control limits.",
    rule2: "Rule 2: 7+ consecutive points on one side of the center line.",
    rule3: "Rule 3: 6+ consecutive points all increasing or all decreasing.",
};

export const RChart: React.FC<RChartProps> = ({ data, dataPrecision }) => {
    const { rPoints, rCL, rUCL, rLCL, rChartSpecialCauses } = data;

    const allSpecialCauseSubgroups = [...new Set(Object.values(rChartSpecialCauses).flat())];
    const highlightedPoints = rPoints.filter(p => allSpecialCauseSubgroups.includes(p.subgroup));
    const hasSpecialCauses = allSpecialCauseSubgroups.length > 0;

    const yMin = Math.min(rLCL, ...rPoints.map(p => p.range));
    const yMax = Math.max(rUCL, ...rPoints.map(p => p.range));
    const range = yMax - yMin;
    const padding = range === 0 ? 1 : range * 0.1;
    const yDomain: [number, number] = [yMin - padding, yMax + padding];

    return (
        <Card title="R-Chart (Range)" icon={<ChartIcon />}>
            <div style={{ width: '100%', height: 300 }}>
                <ResponsiveContainer>
                    <LineChart data={rPoints} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#4A5568" />
                        <XAxis dataKey="subgroup" tick={{ fill: '#A0AEC0' }} label={{ value: 'Subgroup', position: 'insideBottom', offset: -5, fill: '#A0AEC0' }}/>
                        <YAxis 
                            tick={{ fill: '#A0AEC0' }} 
                            domain={yDomain} 
                            allowDataOverflow
                            tickFormatter={(tick) => typeof tick === 'number' ? tick.toFixed(dataPrecision + 1) : tick}
                        />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1A202C', border: '1px solid #2D3748', color: '#CBD5E0' }}
                            labelStyle={{ color: '#E2E8F0' }}
                        />
                        <Legend wrapperStyle={{color: '#E2E8F0'}} />
                        <ReferenceLine y={rUCL} label={{ value: `UCL=${rUCL.toFixed(dataPrecision + 2)}`, fill: '#F56565', position: 'insideTopRight' }} stroke="#F56565" strokeDasharray="3 3" />
                        <ReferenceLine y={rLCL} label={{ value: `LCL=${rLCL.toFixed(dataPrecision + 2)}`, fill: '#F56565', position: 'insideBottomRight' }} stroke="#F56565" strokeDasharray="3 3" />
                        <ReferenceLine y={rCL} label={{ value: `CL=${rCL.toFixed(dataPrecision + 2)}`, fill: '#48BB78' }} stroke="#48BB78" strokeDasharray="3 3" />
                        <Line type="monotone" dataKey="range" stroke="#805AD5" strokeWidth={2} name="Subgroup Range" dot={{ r: 3 }} activeDot={{ r: 6 }} />
                        {/* FIX: Removed invalid `zIndex` prop. The Scatter component is already rendered on top due to its order in the JSX. */}
                        <Scatter data={highlightedPoints} fill="#F6AD55" shape="star" name="Special Cause"/>
                    </LineChart>
                </ResponsiveContainer>
            </div>
            {hasSpecialCauses &&
                <div className="mt-4 p-3 bg-gray-900/50 rounded-lg border border-gray-700">
                    <h4 className="font-semibold text-yellow-300 mb-2 text-sm">Special Cause Analysis (R-Chart)</h4>
                    {Object.entries(rChartSpecialCauses).map(([rule, subgroups]) => (
                        // FIX: Added Array.isArray() as a type guard because TypeScript was inferring `subgroups` as `unknown`.
                        Array.isArray(subgroups) && subgroups.length > 0 &&
                        <p key={rule} className="text-sm text-gray-300">
                           <span className="font-semibold">{ruleDescriptions[rule as keyof typeof ruleDescriptions]}</span> Violated by subgroups: {subgroups.join(', ')}.
                        </p>
                    ))}
                </div>
            }
        </Card>
    );
};
