import React, { useState, useEffect, useRef } from 'react';

interface SaveStudyModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (studyName: string) => void;
    defaultStudyName: string;
}

export const SaveStudyModal: React.FC<SaveStudyModalProps> = ({ isOpen, onClose, onSave, defaultStudyName }) => {
    const [studyName, setStudyName] = useState(defaultStudyName);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (isOpen) {
            setStudyName(defaultStudyName || 'New Study');
            // Focus the input when the modal opens
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [isOpen, defaultStudyName]);

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                onClose();
            }
        };

        if (isOpen) {
            window.addEventListener('keydown', handleKeyDown);
        }

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [isOpen, onClose]);


    if (!isOpen) {
        return null;
    }

    const handleSave = () => {
        if (studyName.trim() === '') {
            alert("Study name cannot be empty.");
            return;
        }
        onSave(studyName.trim());
        onClose();
    };

    const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            handleSave();
        }
    };
    
    return (
        <div 
            className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 transition-opacity duration-300"
            onClick={onClose}
            aria-modal="true"
            role="dialog"
            aria-labelledby="save-study-title"
        >
            <div 
                className="bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md m-4 border border-gray-700 transform transition-all duration-300 scale-95 opacity-0 animate-fade-in-scale"
                onClick={(e) => e.stopPropagation()} // Prevent closing modal when clicking inside
            >
                <h2 id="save-study-title" className="text-xl font-bold text-white mb-4">Save Study</h2>
                <div>
                    <label htmlFor="study-name-input" className="block text-sm font-medium text-gray-300 mb-2">
                        Enter a name for this study
                    </label>
                    <input
                        ref={inputRef}
                        id="study-name-input"
                        type="text"
                        value={studyName}
                        onChange={(e) => setStudyName(e.target.value)}
                        onKeyDown={handleInputKeyDown}
                        className="w-full bg-gray-900/50 border border-gray-600 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 text-gray-200 p-3 transition"
                    />
                </div>
                <div className="mt-6 flex justify-end space-x-3">
                    <button
                        onClick={onClose}
                        type="button"
                        className="px-4 py-2 border border-gray-600 text-sm font-medium rounded-md text-gray-300 bg-gray-700 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-cyan-500 transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        type="button"
                        className="px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-cyan-600 hover:bg-cyan-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-cyan-500 transition-colors"
                    >
                        Save
                    </button>
                </div>
            </div>
            <style>{`
                @keyframes fade-in-scale {
                    0% {
                        opacity: 0;
                        transform: scale(0.95);
                    }
                    100% {
                        opacity: 1;
                        transform: scale(1);
                    }
                }
                .animate-fade-in-scale {
                    animation: fade-in-scale 0.2s ease-out forwards;
                }
            `}</style>
        </div>
    );
};
