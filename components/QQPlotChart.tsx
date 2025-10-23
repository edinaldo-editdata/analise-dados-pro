import React from 'react';
import { ComposedChart, Scatter, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card } from './Card';
import { ChartIcon } from './icons';
import { QQPlotDataPoint, BasicStats } from '../types';

interface QQPlotChartProps {
  data: QQPlotDataPoint[];
  basicStats: BasicStats;
}

const getNormalityCommentary = (pValue: number): { text: string; color: string } => {
    const pValueText = pValue < 0.0001 ? '< 0.0001' : pValue.toFixed(4);

    if (pValue > 0.05) {
        return {
            text: `The p-value (${pValueText}) is > 0.05. We cannot reject the null hypothesis; the data appears to be normally distributed.`,
            color: 'text-green-400',
        };
    } else {
        return {
            text: `The p-value (${pValueText}) is <= 0.05. We reject the null hypothesis; the data does not appear to be normally distributed.`,
            color: 'text-red-400',
        };
    }
};

export const QQPlotChart: React.FC<QQPlotChartProps> = ({ data, basicStats }) => {
  const { mean, stdDev, pValue } = basicStats;
  const normalityInfo = getNormalityCommentary(pValue);

  if (data.length === 0) {
    return (
        <Card title="Q-Q Plot (Normality)" icon={<ChartIcon />}>
            <div className="text-center text-gray-400 h-[300px] flex items-center justify-center">
                <p>Not enough data to generate Q-Q Plot.</p>
            </div>
        </Card>
    );
  }

  const minTheoretical = data[0].theoretical;
  const maxTheoretical = data[data.length - 1].theoretical;

  const referenceLineData = [
    { theoretical: minTheoretical, sample: mean + minTheoretical * stdDev },
    { theoretical: maxTheoretical, sample: mean + maxTheoretical * stdDev },
  ];

  return (
    <Card title="Q-Q Plot (Normality)" icon={<ChartIcon />}>
      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer>
          <ComposedChart
            margin={{ top: 20, right: 30, left: 0, bottom: 25 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#4A5568" />
            <XAxis 
                dataKey="theoretical" 
                type="number" 
                domain={['dataMin', 'dataMax']}
                tick={{ fill: '#A0AEC0' }}
                tickFormatter={(tick) => tick.toFixed(2)}
                label={{ value: 'Theoretical Quantiles', position: 'insideBottom', offset: -15, fill: '#A0AEC0' }}
            />
            <YAxis 
                dataKey="sample"
                type="number"
                domain={['dataMin', 'dataMax']}
                tick={{ fill: '#A0AEC0' }}
                tickFormatter={(tick) => typeof tick === 'number' ? tick.toFixed(2) : tick}
                label={{ value: 'Sample Quantiles', angle: -90, position: 'insideLeft', fill: '#A0AEC0', dx: -10 }}
            />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{ backgroundColor: '#1A202C', border: '1px solid #2D3748' }}
              labelStyle={{ color: '#E2E8F0' }}
              formatter={(value: number, name: string) => [value.toFixed(3), name]}
              labelFormatter={(label: number) => `Theoretical: ${label.toFixed(3)}`}
            />
            <Legend wrapperStyle={{color: '#E2E8F0', bottom: 0}} />

            <Scatter name="Data Quantiles" data={data} fill="#2DD4BF" />
            
            <Line 
                dataKey="sample"
                data={referenceLineData} 
                stroke="#F56565" 
                dot={false} 
                strokeWidth={2}
                name="Normal Reference"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
       <div className="mt-4 p-3 bg-gray-900/50 rounded-lg border border-gray-700">
        <h4 className="font-semibold text-gray-300 mb-2 text-sm">Normality Assessment</h4>
        <p className={`text-sm ${normalityInfo.color}`}>
          {normalityInfo.text}
        </p>
      </div>
    </Card>
  );
};