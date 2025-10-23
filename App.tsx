import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { DataInput } from './components/DataInput';
import { Dashboard } from './components/Dashboard';
import { SavedStudy, StudyInfo, AnalysisData } from './types';
import { performStatisticalAnalysis } from './services/statisticalAnalysis';
import { ChartIcon, CodeIcon, GithubIcon } from './components/icons';
import { HeaderInfo } from './components/HeaderInfo';
import { SavedStudies } from './components/SavedStudies';
import { SaveStudyModal } from './components/SaveStudyModal';

const App: React.FC = () => {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // State lifted from child components for save/load functionality
  const [dataText, setDataText] = useState<string>('');
  const [lsl, setLsl] = useState<string>('');
  const [usl, setUsl] = useState<string>('');
  const [subgroupSize, setSubgroupSize] = useState<string>('5');
  
  const [studyInfo, setStudyInfo] = useState<StudyInfo>({
    processName: '',
    characteristic: '',
    conductedBy: '',
    studyDate: new Date().toISOString().split('T')[0],
    instrument: '',
    resolution: '',
  });
  
  const [savedStudies, setSavedStudies] = useState<SavedStudy[]>([]);
  const [isSaveModalOpen, setIsSaveModalOpen] = useState<boolean>(false);

  useEffect(() => {
    try {
      const storedStudies = localStorage.getItem('spcSavedStudies');
      if (storedStudies) {
        setSavedStudies(JSON.parse(storedStudies));
      }
    } catch (e) {
      console.error("Failed to load studies from local storage:", e);
    }
  }, []);

  const handleAnalyze = useCallback(() => {
    setIsLoading(true);
    setError(null);
    setAnalysisData(null);

    const parsedData = dataText
      .split(/[\s,;\n]+/)
      .map(s => s.trim())
      .filter(s => s !== '')
      .map(Number)
      .filter(n => !isNaN(n));
    
    const parsedLsl = lsl.trim() === '' ? null : parseFloat(lsl);
    const parsedUsl = usl.trim() === '' ? null : parseFloat(usl);
    const parsedSubgroupSize = subgroupSize.trim() === '' ? null : parseInt(subgroupSize, 10);

    setTimeout(() => {
      try {
        if (parsedData.length < 2) {
          throw new Error("Please provide at least two data points for analysis.");
        }
        const results = performStatisticalAnalysis(parsedData, parsedLsl, parsedUsl, parsedSubgroupSize);
        setAnalysisData({ result: results, lsl: parsedLsl, usl: parsedUsl });
      } catch (e: unknown) {
        if (e instanceof Error) {
          setError(e.message);
        } else {
          setError("An unknown error occurred during analysis.");
        }
      } finally {
        setIsLoading(false);
      }
    }, 500);
  }, [dataText, lsl, usl, subgroupSize]);
  
  const handleSaveStudy = () => {
    if (!analysisData) {
        alert("Please analyze data before saving a study.");
        return;
    }
    setIsSaveModalOpen(true);
  };

  const handleConfirmSave = (studyName: string) => {
    if (!analysisData) {
        console.error("handleConfirmSave called without analysis data.");
        return;
    }

    const newStudy: SavedStudy = {
        id: new Date().toISOString() + Math.random(),
        createdAt: new Date().toISOString(),
        studyName: studyName,
        studyInfo,
        dataText,
        lsl,
        usl,
        subgroupSize,
        analysisData,
    };
    
    try {
        const updatedStudies = [...savedStudies, newStudy];
        setSavedStudies(updatedStudies);
        localStorage.setItem('spcSavedStudies', JSON.stringify(updatedStudies));
        alert(`Study "${studyName}" saved successfully!`);
    } catch (error) {
        console.error("Failed to save study:", error);
        alert("Error: Could not save the study. Local storage might be full.");
    }
  };

  const handleLoadStudy = (studyId: string) => {
    const studyToLoad = savedStudies.find(s => s.id === studyId);
    if (studyToLoad) {
        const fullStudyInfo = {
            processName: '',
            characteristic: '',
            conductedBy: '',
            studyDate: new Date().toISOString().split('T')[0],
            instrument: '',
            resolution: '',
            ...studyToLoad.studyInfo,
        };
        setStudyInfo(fullStudyInfo);
        setDataText(studyToLoad.dataText);
        setLsl(studyToLoad.lsl);
        setUsl(studyToLoad.usl);
        setSubgroupSize(studyToLoad.subgroupSize);
        setAnalysisData(studyToLoad.analysisData);
        setError(null);
        window.scrollTo(0, 0);
    }
  };

  const handleDeleteStudy = (studyId: string) => {
    if (window.confirm("Are you sure you want to delete this study? This action cannot be undone.")) {
        try {
            const updatedStudies = savedStudies.filter(s => s.id !== studyId);
            setSavedStudies(updatedStudies);
            localStorage.setItem('spcSavedStudies', JSON.stringify(updatedStudies));
        } catch (error) {
            console.error("Failed to delete study:", error);
            alert("Error: Could not delete the study.");
        }
    }
  };

  const memoizedDashboard = useMemo(() => {
    return analysisData ? <Dashboard result={analysisData.result} lsl={analysisData.lsl} usl={analysisData.usl} /> : null;
  }, [analysisData]);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-200 font-sans">
      <header className="bg-gray-800/50 backdrop-blur-sm shadow-lg sticky top-0 z-10">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <ChartIcon className="h-8 w-8 text-cyan-400" />
              <h1 className="text-xl font-bold tracking-tight text-white">
                Statistical Process Control Analyzer
              </h1>
            </div>
            <a href="https://github.com/google/aistudio" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
              <GithubIcon className="h-6 w-6" />
            </a>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4 sm:p-6 lg:p-8">
        <HeaderInfo 
            studyInfo={studyInfo}
            onStudyInfoChange={setStudyInfo}
            onSaveStudy={handleSaveStudy}
            isAnalysisDone={!!analysisData}
        />
        <DataInput 
            onAnalyze={handleAnalyze} 
            isLoading={isLoading}
            dataText={dataText}
            lsl={lsl}
            usl={usl}
            subgroupSize={subgroupSize}
            onDataTextChange={setDataText}
            onLslChange={setLsl}
            onUslChange={setUsl}
            onSubgroupSizeChange={setSubgroupSize}
        />
        <SavedStudies
            studies={savedStudies}
            onLoad={handleLoadStudy}
            onDelete={handleDeleteStudy}
        />

        {error && (
          <div className="mt-6 bg-red-900/50 border border-red-700 text-red-300 px-4 py-3 rounded-lg relative" role="alert">
            <strong className="font-bold">Error: </strong>
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {isLoading && (
          <div className="mt-6 flex justify-center items-center space-x-3">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
            <p className="text-lg">Analyzing data...</p>
          </div>
        )}
        
        {memoizedDashboard}
      </main>

       <SaveStudyModal
        isOpen={isSaveModalOpen}
        onClose={() => setIsSaveModalOpen(false)}
        onSave={handleConfirmSave}
        defaultStudyName={studyInfo.processName}
      />

      <footer className="text-center p-4 text-gray-500 text-sm">
        <p>Built for advanced statistical analysis. &copy; {new Date().getFullYear()}</p>
        <p className="flex items-center justify-center gap-2 mt-1">
            <CodeIcon className="w-5 h-5" />
            <span>EditData Soluções Inteligentes</span>
        </p>
      </footer>
    </div>
  );
};

export default App;
