import React from 'react';
import { Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart, Line, ReferenceLine, Label } from 'recharts';
import { Card } from './Card';
import { ChartIcon } from './icons';
import { HistogramData, BasicStats } from '../types';

interface HistogramChartProps {
  histogramData: HistogramData;
  basicStats: BasicStats;
  lsl: number | null;
  usl: number | null;
}

export const HistogramChart: React.FC<HistogramChartProps> = ({ histogramData, basicStats, lsl, usl }) => {
    const { mean, stdDev } = basicStats;

    const chartData = histogramData.bins.map(bin => ({
        x: (bin.x0 + bin.x1) / 2,
        count: bin.y,
        rangeLabel: `${bin.x0.toFixed(2)} - ${bin.x1.toFixed(2)}`
    }));
    
    const allXValues = [
        ...histogramData.bins.flatMap(b => [b.x0, b.x1]), 
        ...(lsl !== null ? [lsl] : []),
        ...(usl !== null ? [usl] : []),
        ...(stdDev > 0 ? [mean - 3.5 * stdDev, mean + 3.5 * stdDev] : [mean - 1, mean + 1])
    ];
    const xDomain: [number, number] = [Math.min(...allXValues), Math.max(...allXValues)];

    return (
        <Card title="Data Distribution Histogram" icon={<ChartIcon />}>
            <div style={{ width: '100%', height: 350 }}>
                <ResponsiveContainer>
                    <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 25 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#4A5568" />
                        <XAxis 
                            dataKey="x" 
                            type="number"
                            domain={xDomain}
                            tick={{ fill: '#A0AEC0' }} 
                            tickFormatter={(tick) => tick.toFixed(2)}
                            label={{ value: 'Value', position: 'insideBottom', offset: -15, fill: '#A0AEC0' }}
                        />
                        <YAxis yAxisId="left" allowDecimals={false} tick={{ fill: '#A0AEC0' }} label={{ value: 'Frequency', angle: -90, position: 'insideLeft', fill: '#A0AEC0', dx: -10 }}/>
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1A202C', border: '1px solid #2D3748' }}
                            labelStyle={{ color: '#E2E8F0' }}
                            formatter={(value: number, name: string, props: any) => [value, `Count (${props.payload.rangeLabel})`]}
                            labelFormatter={(label: number) => `Value: ${label.toFixed(3)}`}
                        />
                        <Legend wrapperStyle={{color: '#E2E8F0', bottom: 0}} />
                        
                        <Bar yAxisId="left" dataKey="count" fill="#2DD4BF" name="Frequency" barSize={20} />
                        
                        <Line
                            yAxisId="left"
                            type="monotone"
                            data={histogramData.normalCurve}
                            dataKey="y"
                            stroke="#F6AD55"
                            dot={false}
                            strokeWidth={2}
                            name="Normal Distribution"
                        />
                        
                        {lsl !== null && (
                             <ReferenceLine yAxisId="left" x={lsl} stroke="#F56565" strokeWidth={2}>
                                <Label value={`LSL: ${lsl}`} position="top" fill="#F56565" />
                             </ReferenceLine>
                        )}
                        {usl !== null && (
                             <ReferenceLine yAxisId="left" x={usl} stroke="#F56565" strokeWidth={2}>
                                <Label value={`USL: ${usl}`} position="top" fill="#F56565" />
                            </ReferenceLine>
                        )}

                        <ReferenceLine yAxisId="left" x={mean} stroke="#48BB78" strokeWidth={2}>
                            <Label value={`Mean: ${mean.toFixed(3)}`} position="top" fill="#48BB78" />
                        </ReferenceLine>

                        {[-3, -2, -1, 1, 2, 3].map(sigma => (
                            stdDev > 0 && <ReferenceLine
                                key={sigma}
                                yAxisId="left"
                                x={mean + sigma * stdDev}
                                stroke="#4299E1"
                                strokeDasharray="3 3"
                                strokeWidth={1}
                            >
                                <Label value={`${sigma > 0 ? '+' : ''}${sigma}σ`} position="insideTop" dy={-10} fill="#4299E1" fontSize="10"/>
                            </ReferenceLine>
                        ))}
                    </ComposedChart>
                </ResponsiveContainer>
            </div>
        </Card>
    );
};