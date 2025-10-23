import React, { useCallback, useRef, useState } from 'react';
import { Card } from './Card';
import { UploadIcon } from './icons';
import Papa from 'papaparse';

interface DataInputProps {
  dataText: string;
  lsl: string;
  usl: string;
  subgroupSize: string;
  onDataTextChange: (value: string) => void;
  onLslChange: (value: string) => void;
  onUslChange: (value: string) => void;
  onSubgroupSizeChange: (value: string) => void;
  onAnalyze: () => void;
  isLoading: boolean;
}

export const DataInput: React.FC<DataInputProps> = ({ 
  dataText, lsl, usl, subgroupSize,
  onDataTextChange, onLslChange, onUslChange, onSubgroupSizeChange,
  onAnalyze, isLoading 
}) => {
  const [fileName, setFileName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setFileName(file.name);

      if (file.type === 'text/plain' || file.name.toLowerCase().endsWith('.txt')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const text = e.target?.result;
          if (typeof text === 'string') {
            onDataTextChange(text);
          }
        };
        reader.onerror = () => {
          console.error("Error reading .txt file.");
          alert("Error reading .txt file.");
        };
        reader.readAsText(file);
      } else { // Assume CSV
        Papa.parse(file, {
          complete: (results: any) => {
            const flatData = results.data
              .flat()
              .filter((cell: any) => cell !== null && cell !== undefined && cell.toString().trim() !== '')
              .join('\n');
            onDataTextChange(flatData);
          },
          error: (error: any) => {
            console.error("CSV parsing error:", error);
            alert("Error parsing CSV file.");
          }
        });
      }
    }
  }, [onDataTextChange]);
  
  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <Card title="Data Input & Configuration" className="mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="data-input" className="block text-sm font-medium text-gray-300 mb-2">
            Paste Data (separated by space, comma, semicolon, or new line)
          </label>
          <textarea
            id="data-input"
            rows={10}
            className="w-full bg-gray-900/50 border border-gray-600 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 text-gray-200 p-3 transition"
            placeholder="e.g., 10.2, 10.5, 9.8, 10.1, ..."
            value={dataText}
            onChange={(e) => onDataTextChange(e.target.value)}
          />
           <div className="mt-4 flex space-x-3">
              <input type="file" ref={fileInputRef} onChange={handleFileChange} accept=".csv,.txt" className="hidden" />
              <button onClick={triggerFileSelect} className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-gray-600 text-sm font-medium rounded-md text-gray-300 bg-gray-700 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-cyan-500 transition-colors">
                  <UploadIcon className="w-5 h-5 mr-2" />
                  {fileName ? `File: ${fileName}` : 'Import from CSV/TXT'}
              </button>
          </div>
        </div>
        <div className="space-y-4">
          <div>
            <label htmlFor="lsl" className="block text-sm font-medium text-gray-300">Lower Specification Limit (LSL)</label>
            <input type="number" id="lsl" value={lsl} onChange={(e) => onLslChange(e.target.value)} className="mt-1 block w-full bg-gray-900/50 border border-gray-600 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 p-2" placeholder="Optional" />
          </div>
          <div>
            <label htmlFor="usl" className="block text-sm font-medium text-gray-300">Upper Specification Limit (USL)</label>
            <input type="number" id="usl" value={usl} onChange={(e) => onUslChange(e.target.value)} className="mt-1 block w-full bg-gray-900/50 border border-gray-600 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 p-2" placeholder="Optional" />
          </div>
          <div>
            <label htmlFor="subgroup-size" className="block text-sm font-medium text-gray-300">Subgroup Size (for Control Chart)</label>
            <input type="number" id="subgroup-size" value={subgroupSize} onChange={(e) => onSubgroupSizeChange(e.target.value)} min="2" max="10" className="mt-1 block w-full bg-gray-900/50 border border-gray-600 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 p-2" placeholder="e.g., 5" />
          </div>
        </div>
      </div>
      <div className="mt-6">
        <button
          onClick={onAnalyze}
          disabled={isLoading || dataText.trim() === ''}
          className="w-full inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-cyan-600 hover:bg-cyan-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-cyan-500 disabled:bg-gray-500 disabled:cursor-not-allowed transition-all transform hover:scale-105"
        >
          {isLoading ? 'Analyzing...' : 'Analyze Data'}
        </button>
      </div>
    </Card>
  );
};