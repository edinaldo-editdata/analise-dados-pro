import React, { useState, useRef, ChangeEvent, useEffect } from 'react';
import { Card } from './Card';
import { SaveIcon, TrashIcon, UploadIcon } from './icons';
import { StudyInfo } from '../types';

const LogoPlaceholder: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" {...props}>
        <path d="M20,80 L20,20 L80,20 L80,80 Z" stroke="currentColor" strokeWidth="4" fill="none" />
        <circle cx="50" cy="50" r="20" fill="currentColor" />
    </svg>
);

const LOGO_STORAGE_KEY = 'spcAnalyzerLogo';

interface HeaderInfoProps {
    studyInfo: StudyInfo;
    onStudyInfoChange: React.Dispatch<React.SetStateAction<StudyInfo>>;
    onSaveStudy: () => void;
    isAnalysisDone: boolean;
}

export const HeaderInfo: React.FC<HeaderInfoProps> = ({ studyInfo, onStudyInfoChange, onSaveStudy, isAnalysisDone }) => {
    const [logoSrc, setLogoSrc] = useState<string | null>(null);
    const [logoSize, setLogoSize] = useState<number>(80);
    const fileInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        const savedLogo = localStorage.getItem(LOGO_STORAGE_KEY);
        if (savedLogo) {
            setLogoSrc(savedLogo);
        }
    }, []);

    const handleLogoChange = (event: ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                if (typeof e.target?.result === 'string') {
                    setLogoSrc(e.target.result);
                    localStorage.setItem(LOGO_STORAGE_KEY, e.target.result);
                }
            };
            reader.readAsDataURL(file);
        }
    };

    const handleLogoClick = () => {
        fileInputRef.current?.click();
    };

    const handleRemoveLogo = () => {
        setLogoSrc(null);
        localStorage.removeItem(LOGO_STORAGE_KEY);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { id, value } = e.target;
        onStudyInfoChange(prev => ({ ...prev, [id]: value }));
    };

    return (
        <Card title="Study Information" className="mb-6">
            <div className="flex flex-col md:flex-row gap-6 items-start">
                 <div className="flex-shrink-0 flex flex-col items-center w-full md:w-auto md:max-w-[200px]">
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleLogoChange}
                        accept="image/*"
                        className="hidden"
                    />
                    <div
                        onClick={handleLogoClick}
                        className="relative group cursor-pointer border-2 border-dashed border-gray-600 rounded-full p-1 hover:border-cyan-400 transition-colors"
                        style={{ width: `${logoSize}px`, height: `${logoSize}px` }}
                        aria-label="Change company logo"
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && handleLogoClick()}
                    >
                        {logoSrc ? (
                            <img
                                src={logoSrc}
                                alt="Company Logo"
                                className="rounded-full object-cover w-full h-full"
                            />
                        ) : (
                            <LogoPlaceholder className="text-cyan-400 w-full h-full" />
                        )}
                        <div className="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <UploadIcon className="w-6 h-6 text-white" />
                        </div>
                    </div>
                   <p className="mt-2 text-sm text-gray-400 font-semibold">Your Company</p>
                   
                    <div className="w-full mt-4 max-w-[150px]">
                        <label htmlFor="logo-size" className="block text-xs text-center font-medium text-gray-400 mb-1">Logo Size</label>
                        <input
                            type="range"
                            id="logo-size"
                            min="40"
                            max="150"
                            value={logoSize}
                            onChange={(e) => setLogoSize(Number(e.target.value))}
                            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-cyan-400"
                        />
                    </div>
                    {logoSrc && (
                        <button
                            onClick={handleRemoveLogo}
                            className="mt-2 text-xs text-red-400 hover:text-red-300 flex items-center gap-1 transition-colors"
                            aria-label="Remove saved logo"
                        >
                            <TrashIcon className="w-3 h-3" />
                            Remove Logo
                        </button>
                    )}
                </div>

                <div className="flex-grow grid grid-cols-1 sm:grid-cols-3 gap-4 w-full">
                    <div>
                        <label htmlFor="processName" className="block text-sm font-medium text-gray-300">Process Name</label>
                        <input type="text" id="processName" value={studyInfo.processName} onChange={handleInputChange} className="mt-1 block w-full bg-gray-900/50 border border-gray-600 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 p-2" placeholder="e.g., Shaft Turning" />
                    </div>
                    <div>
                        <label htmlFor="characteristic" className="block text-sm font-medium text-gray-300">Characteristic</label>
                        <input type="text" id="characteristic" value={studyInfo.characteristic} onChange={handleInputChange} className="mt-1 block w-full bg-gray-900/50 border border-gray-600 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 p-2" placeholder="e.g., Diameter (mm)" />
                    </div>
                     <div>
                        <label htmlFor="instrument" className="block text-sm font-medium text-gray-300">Instrument Used</label>
                        <input type="text" id="instrument" value={studyInfo.instrument || ''} onChange={handleInputChange} className="mt-1 block w-full bg-gray-900/50 border border-gray-600 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 p-2" placeholder="e.g., Caliper" />
                    </div>
                    <div>
                        <label htmlFor="resolution" className="block text-sm font-medium text-gray-300">Resolution</label>
                        <input type="text" id="resolution" value={studyInfo.resolution || ''} onChange={handleInputChange} className="mt-1 block w-full bg-gray-900/50 border border-gray-600 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 p-2" placeholder="e.g., 0.01 mm" />
                    </div>
                    <div>
                        <label htmlFor="conductedBy" className="block text-sm font-medium text-gray-300">Study Conducted By</label>
                        <input type="text" id="conductedBy" value={studyInfo.conductedBy} onChange={handleInputChange} className="mt-1 block w-full bg-gray-900/50 border border-gray-600 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 p-2" placeholder="e.g., John Doe" />
                    </div>
                    <div>
                        <label htmlFor="studyDate" className="block text-sm font-medium text-gray-300">Date of Study</label>
                        <input type="date" id="studyDate" value={studyInfo.studyDate} onChange={handleInputChange} className="mt-1 block w-full bg-gray-900/50 border border-gray-600 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 p-2" />
                    </div>
                     <div className="sm:col-span-3 mt-2">
                        <button
                            onClick={onSaveStudy}
                            disabled={!isAnalysisDone}
                            className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-indigo-500 disabled:bg-gray-500 disabled:cursor-not-allowed transition-colors"
                            title={!isAnalysisDone ? "Analyze data to enable saving" : "Save this study"}
                        >
                            <SaveIcon className="w-5 h-5 mr-2" />
                            Save Current Study
                        </button>
                    </div>
                </div>
            </div>
        </Card>
    );
};