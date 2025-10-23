export interface BasicStats {
  count: number;
  mean: number;
  stdDev: number;
  min: number;
  max: number;
  q1: number;
  median: number;
  q3: number;
  skewness: number;
  kurtosis: number;
  pValue: number;
  dataPrecision: number;
}

export interface CapabilityStats {
  cp?: number;
  cpk?: number;
  pp?: number;
  ppk?: number;
}

export interface HistogramData {
  bins: { x0: number; x1: number; y: number }[];
  normalCurve: { x: number; y: number }[];
}

export interface BoxPlotData {
  min: number;
  q1: number;
  median: number;
  q3: number;
  max: number;
  outliers: number[];
}

export interface SpecialCauses {
    [rule: string]: number[]; // rule name -> array of subgroup indices
}

export interface ControlChartData {
  points: { subgroup: number; mean: number }[];
  cl: number;
  ucl: number;
  lcl: number;
  rPoints: { subgroup: number; range: number }[];
  rCL: number;
  rUCL: number;
  rLCL: number;
  xBarSpecialCauses: SpecialCauses;
  rChartSpecialCauses: SpecialCauses;
}

export interface QQPlotDataPoint {
    theoretical: number;
    sample: number;
}

export interface AnalysisResult {
  basicStats: BasicStats;
  capability: CapabilityStats;
  histogram: HistogramData;
  boxPlot: BoxPlotData;
  controlChart: ControlChartData | null;
  qqPlotData: QQPlotDataPoint[];
}

export interface StudyInfo {
    processName: string;
    characteristic: string;
    conductedBy: string;
    studyDate: string;
    instrument: string;
    resolution: string;
}

export interface AnalysisData {
  result: AnalysisResult;
  lsl: number | null;
  usl: number | null;
}

export interface SavedStudy {
    id: string;
    createdAt: string;
    studyName: string;
    studyInfo: StudyInfo;
    dataText: string;
    lsl: string;
    usl: string;
    subgroupSize: string;
    analysisData: AnalysisData;
}