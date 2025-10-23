import React from 'react';
import { Card } from './Card';
import { SavedStudy } from '../types';
import { FolderOpenIcon, TrashIcon } from './icons';

interface SavedStudiesProps {
    studies: SavedStudy[];
    onLoad: (studyId: string) => void;
    onDelete: (studyId: string) => void;
}

export const SavedStudies: React.FC<SavedStudiesProps> = ({ studies, onLoad, onDelete }) => {
    if (studies.length === 0) {
        return null;
    }

    return (
        <Card title="Saved Studies" className="my-6">
            <div className="space-y-3 max-h-60 overflow-y-auto pr-2">
                {studies.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()).map(study => {
                    const studyDisplayName = study.studyName || study.studyInfo.processName || 'Untitled Study';
                    return (
                        <div key={study.id} className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg border border-gray-700 hover:border-cyan-500 transition-colors">
                            <div>
                                <p className="font-semibold text-white">{studyDisplayName}</p>
                                <p className="text-xs text-gray-400">
                                    Saved on: {new Date(study.createdAt).toLocaleString()}
                                </p>
                                {study.studyInfo.instrument && (
                                    <p className="text-xs text-gray-500 mt-1">
                                        Instrument: {study.studyInfo.instrument}
                                    </p>
                                )}
                            </div>
                            <div className="flex items-center space-x-2">
                                <button
                                    onClick={() => onLoad(study.id)}
                                    className="p-2 text-gray-300 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors"
                                    aria-label={`Load study ${studyDisplayName}`}
                                    title={`Load study: ${studyDisplayName}`}
                                >
                                    <FolderOpenIcon className="w-5 h-5" />
                                </button>
                                <button
                                    onClick={() => onDelete(study.id)}
                                    className="p-2 text-red-400 bg-gray-700 hover:bg-red-900/50 rounded-md transition-colors"
                                    aria-label={`Delete study ${studyDisplayName}`}
                                    title={`Delete study: ${studyDisplayName}`}
                                >
                                    <TrashIcon className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    )
                })}
            </div>
        </Card>
    );
};