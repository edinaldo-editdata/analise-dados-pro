import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from 'recharts';
import { Card } from './Card';
import { ChartIcon } from './icons';
import { BoxPlotData } from '../types';

interface BoxPlotChartProps {
  data: BoxPlotData;
}

export const BoxPlotChart: React.FC<BoxPlotChartProps> = ({ data }) => {
  const { min, q1, median, q3, max } = data;

  const plotData = [
    {
      x: 'Data',
      y: [min, q1, median, q3, max]
    }
  ];
  
  const range = max - min;
  const padding = range === 0 ? 1 : range * 0.15;
  const yDomain: [number, number] = [min - padding, max + padding];
  
  // Custom rendering logic requires manual scaling. This ensures the drawn elements
  // match the Y-axis domain provided to the chart.
  const chartHeight = 300;
  const margin = { top: 20, bottom: 20 };
  const plotHeight = chartHeight - margin.top - margin.bottom;
  const domainRange = yDomain[1] - yDomain[0];

  const scaleY = (value: number) => {
    if (domainRange === 0) {
      return margin.top + plotHeight / 2;
    }
    return margin.top + (1 - (value - yDomain[0]) / domainRange) * plotHeight;
  };

  const yQ1 = scaleY(q1);
  const yQ3 = scaleY(q3);
  const boxHeight = Math.abs(yQ1 - yQ3);

  return (
    <Card title="Box Plot" icon={<ChartIcon />}>
      <div style={{ width: '100%', height: chartHeight }}>
        <ResponsiveContainer>
          <ScatterChart
            margin={margin}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#4A5568" />
            <XAxis dataKey="x" tick={{ fill: '#A0AEC0' }} />
            <YAxis 
              type="number" 
              domain={yDomain} 
              tick={{ fill: '#A0AEC0' }} 
              allowDataOverflow 
              tickFormatter={(tick) => typeof tick === 'number' ? tick.toFixed(2) : tick} 
            />
            <ZAxis dataKey="y" range={[100, 100]} />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              wrapperStyle={{ zIndex: 100 }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                    const values = payload[0].payload.y;
                    return (
                        <div className="p-3 bg-gray-800 border border-gray-600 rounded-lg shadow-lg text-gray-200">
                            <p>Max: {values[4].toFixed(3)}</p>
                            <p>Q3: {values[3].toFixed(3)}</p>
                            <p>Median: {values[2].toFixed(3)}</p>
                            <p>Q1: {values[1].toFixed(3)}</p>
                            <p>Min: {values[0].toFixed(3)}</p>
                        </div>
                    );
                }
                return null;
            }}
            />
            <Scatter data={plotData} fill="#2DD4BF" />
             {/* Custom rendering for box plot components scaled to the chart coordinates */}
            <g>
                {/* Box */}
                <rect x="35%" y={yQ3} width="30%" height={boxHeight} stroke="#2DD4BF" fill="#2DD4BF" fillOpacity={0.3} />
                {/* Median line */}
                <line x1="35%" y1={scaleY(median)} x2="65%" y2={scaleY(median)} stroke="#F6AD55" strokeWidth={2} />
                {/* Top whisker */}
                <line x1="50%" y1={yQ3} x2="50%" y2={scaleY(max)} stroke="#A0AEC0" />
                <line x1="40%" y1={scaleY(max)} x2="60%" y2={scaleY(max)} stroke="#A0AEC0" />
                {/* Bottom whisker */}
                <line x1="50%" y1={yQ1} x2="50%" y2={scaleY(min)} stroke="#A0AEC0" />
                <line x1="40%" y1={scaleY(min)} x2="60%" y2={scaleY(min)} stroke="#A0AEC0" />
            </g>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};