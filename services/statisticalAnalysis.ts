import { AnalysisResult, BasicStats, BoxPlotData, CapabilityStats, ControlChartData, HistogramData, QQPlotDataPoint, SpecialCauses } from '../types';

// Constants for X-bar chart (subgroup sizes 2-10)
const A2_FACTORS: { [key: number]: number } = {
    2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483,
    7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308,
};

// Constants for R-chart (subgroup sizes 2-10)
const D3_FACTORS: { [key: number]: number } = {
    2: 0, 3: 0, 4: 0, 5: 0, 6: 0,
    7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223,
};
const D4_FACTORS: { [key: number]: number } = {
    2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004,
    7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777,
};

// d2 constants for estimating within-subgroup standard deviation from R-bar
const D2_FACTORS: { [key: number]: number } = {
    2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534,
    7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078,
};


const calculateMean = (data: number[]): number => {
    if (data.length === 0) return 0;
    return data.reduce((a, b) => a + b, 0) / data.length;
};

const calculateStdDev = (data: number[], mean?: number): number => {
    if (data.length < 2) return 0;
    const m = mean ?? calculateMean(data);
    const variance = data.reduce((sq, n) => sq + Math.pow(n - m, 2), 0) / (data.length - 1);
    return Math.sqrt(variance);
};

const calculateSkewness = (data: number[], mean: number, stdDev: number): number => {
    if (stdDev === 0) return 0;
    const n = data.length;
    const thirdMoment = data.reduce((sum, val) => sum + Math.pow(val - mean, 3), 0) / n;
    return thirdMoment / Math.pow(stdDev, 3);
};

const calculateKurtosis = (data: number[], mean: number, stdDev: number): number => {
    if (stdDev === 0) return 0;
    const n = data.length;
    const fourthMoment = data.reduce((sum, val) => sum + Math.pow(val - mean, 4), 0) / n;
    return fourthMoment / Math.pow(stdDev, 4);
};

const calculateDataPrecision = (data: number[]): number => {
    let maxPrecision = 0;
    for (const num of data) {
        if (Math.floor(num) === num) continue;
        const s = String(num);
        if (s.includes('.')) {
            const precision = s.split('.')[1].length;
            if (precision > maxPrecision) {
                maxPrecision = precision;
            }
        }
    }
    return maxPrecision;
};


const calculateBasicStats = (data: number[]): BasicStats => {
    const sortedData = [...data].sort((a, b) => a - b);
    const count = data.length;
    const mean = calculateMean(data);
    const stdDev = calculateStdDev(data, mean);
    const min = sortedData[0];
    const max = sortedData[count - 1];

    const q1Index = Math.floor(count / 4);
    const medianIndex = Math.floor(count / 2);
    const q3Index = Math.floor(3 * count / 4);

    const q1 = sortedData[q1Index];
    const median = count % 2 === 0 ? (sortedData[medianIndex - 1] + sortedData[medianIndex]) / 2 : sortedData[medianIndex];
    const q3 = sortedData[q3Index];

    const skewness = calculateSkewness(data, mean, stdDev);
    const kurtosis = calculateKurtosis(data, mean, stdDev);
    const dataPrecision = calculateDataPrecision(data);

    // Jarque-Bera normality test
    const n = data.length;
    const excessKurtosis = kurtosis - 3;
    const jb_statistic = (n / 6) * (Math.pow(skewness, 2) + Math.pow(excessKurtosis, 2) / 4);
    const pValue = Math.exp(-jb_statistic / 2);


    return { count, mean, stdDev, min, max, q1, median, q3, skewness, kurtosis, pValue, dataPrecision };
};

const getSubgroups = (data: number[], subgroupSize: number): number[][] => {
    const subgroups: number[][] = [];
    if (subgroupSize < 2) return subgroups;
    for (let i = 0; i < data.length; i += subgroupSize) {
        const subgroup = data.slice(i, i + subgroupSize);
        if (subgroup.length === subgroupSize) {
            subgroups.push(subgroup);
        }
    }
    return subgroups;
};

const calculateCapability = (
    data: number[],
    stats: BasicStats,
    lsl: number | null,
    usl: number | null,
    subgroupSize: number | null
): CapabilityStats => {
    const { mean, stdDev: stdDevOverall } = stats;
    const result: CapabilityStats = {};

    if (lsl === null || usl === null) {
        return result;
    }

    if (stdDevOverall > 0) {
        const tolerance = usl - lsl;
        result.pp = tolerance / (6 * stdDevOverall);
        const ppu = (usl - mean) / (3 * stdDevOverall);
        const ppl = (mean - lsl) / (3 * stdDevOverall);
        result.ppk = Math.min(ppu, ppl);
    }

    if (subgroupSize && subgroupSize >= 2 && D2_FACTORS[subgroupSize]) {
        const subgroups = getSubgroups(data, subgroupSize);
        if (subgroups.length >= 2) {
            const subgroupRanges = subgroups.map(sg => Math.max(...sg) - Math.min(...sg));
            const rBar = calculateMean(subgroupRanges);
            const d2 = D2_FACTORS[subgroupSize];
            const stdDevWithin = (d2 > 0) ? (rBar / d2) : null;
            
            if (stdDevWithin !== null && stdDevWithin > 0) {
                const tolerance = usl - lsl;
                result.cp = tolerance / (6 * stdDevWithin);
                const cpu = (usl - mean) / (3 * stdDevWithin);
                const cpl = (mean - lsl) / (3 * stdDevWithin);
                result.cpk = Math.min(cpu, cpl);
            }
        }
    }

    return result;
};


const calculateHistogram = (data: number[], stats: BasicStats, lsl: number | null, usl: number | null): HistogramData => {
    const { count, min, max, mean, stdDev } = stats;
    
    if (max === min) {
        const bins = [{ x0: min - 0.5, x1: min + 0.5, y: count }];
        return { bins, normalCurve: [] };
    }

    const numBins = Math.ceil(1 + 3.322 * Math.log10(count));
    const binWidth = (max - min) / numBins;

    const bins = Array.from({ length: numBins }, (_, i) => ({
        x0: min + i * binWidth,
        x1: min + (i + 1) * binWidth,
        y: 0,
    }));
    
    data.forEach(d => {
        let binIndex = Math.floor((d - min) / binWidth);
        if(binIndex === numBins) binIndex--;
        if(bins[binIndex]) {
            bins[binIndex].y++;
        }
    });

    const normalCurve = [];
    if (stdDev > 0) {
        const allRelevantPoints = [min, max];
        if (lsl !== null) allRelevantPoints.push(lsl);
        if (usl !== null) allRelevantPoints.push(usl);
        allRelevantPoints.push(mean - 4 * stdDev, mean + 4 * stdDev);

        const curveMin = Math.min(...allRelevantPoints);
        const curveMax = Math.max(...allRelevantPoints);
        const step = (curveMax - curveMin) / 100;

        for (let i = 0; i <= 100; i++) {
            const x = curveMin + i * step;
            const exponent = -0.5 * Math.pow((x - mean) / stdDev, 2);
            const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(exponent);
            normalCurve.push({x, y});
        }
    }
    
    const maxBinCount = Math.max(0, ...bins.map(b => b.y));
    const maxNormalY = Math.max(1, ...normalCurve.map(p => p.y));
    const scaledNormalCurve = normalCurve.map(p => ({...p, y: (p.y / maxNormalY) * maxBinCount }));


    return { bins, normalCurve: scaledNormalCurve };
};

const calculateBoxPlot = (stats: BasicStats): BoxPlotData => {
    const { min, max, q1, median, q3 } = stats;
    const iqr = q3 - q1;
    const lowerWhisker = Math.max(min, q1 - 1.5 * iqr);
    const upperWhisker = Math.min(max, q3 + 1.5 * iqr);
        
    return { min: lowerWhisker, q1, median, q3, max: upperWhisker, outliers: [] };
};

interface ChartPoint { subgroup: number; value: number; }

const detectSpecialCauses = (points: ChartPoint[], cl: number, ucl: number, lcl: number): SpecialCauses => {
    const causes: SpecialCauses = { rule1: [], rule2: [], rule3: [] };
    const n = points.length;

    // Rule 1: Point outside control limits
    points.forEach(p => {
        if (p.value > ucl || p.value < lcl) {
            causes.rule1.push(p.subgroup);
        }
    });

    // Rule 2: 7+ consecutive points on one side of CL
    if (n >= 7) {
        for (let i = 0; i <= n - 7; i++) {
            const sevenPoints = points.slice(i, i + 7);
            const allAbove = sevenPoints.every(p => p.value > cl);
            const allBelow = sevenPoints.every(p => p.value < cl);
            if (allAbove || allBelow) {
                sevenPoints.forEach(p => causes.rule2.push(p.subgroup));
                i += 6; // Move to the end of the detected sequence
            }
        }
    }
    
    // Rule 3: 6+ consecutive points trending up or down
    if (n >= 6) {
        for (let i = 0; i <= n - 6; i++) {
            const sixPoints = points.slice(i, i + 6);
            let isIncreasing = true;
            let isDecreasing = true;
            for (let j = 1; j < 6; j++) {
                if (sixPoints[j].value <= sixPoints[j-1].value) isIncreasing = false;
                if (sixPoints[j].value >= sixPoints[j-1].value) isDecreasing = false;
            }
            if (isIncreasing || isDecreasing) {
                sixPoints.forEach(p => causes.rule3.push(p.subgroup));
                i += 5; // Move to the end of the detected sequence
            }
        }
    }

    // Make subgroup numbers unique per rule and sort them
    for (const rule in causes) {
        causes[rule] = [...new Set(causes[rule])].sort((a,b) => a-b);
    }

    return causes;
}


const calculateControlChart = (data: number[], subgroupSize: number | null): ControlChartData | null => {
    if (!subgroupSize || subgroupSize < 2 || !A2_FACTORS[subgroupSize]) {
        return null;
    }
    
    const subgroups = getSubgroups(data, subgroupSize);
    if (subgroups.length < 2) return null;

    const subgroupMeans = subgroups.map(sg => calculateMean(sg));
    const subgroupRanges = subgroups.map(sg => Math.max(...sg) - Math.min(...sg));

    const cl = calculateMean(subgroupMeans);
    const rBar = calculateMean(subgroupRanges);
    const a2 = A2_FACTORS[subgroupSize];
    const ucl = cl + a2 * rBar;
    const lcl = cl - a2 * rBar;
    const points = subgroupMeans.map((mean, i) => ({ subgroup: i + 1, mean }));

    const d3 = D3_FACTORS[subgroupSize];
    const d4 = D4_FACTORS[subgroupSize];
    const rCL = rBar;
    const rUCL = d4 * rBar;
    const rLCL = d3 * rBar;
    const rPoints = subgroupRanges.map((range, i) => ({ subgroup: i + 1, range }));

    const xBarChartPoints: ChartPoint[] = points.map(p => ({ subgroup: p.subgroup, value: p.mean }));
    const rChartPoints: ChartPoint[] = rPoints.map(p => ({ subgroup: p.subgroup, value: p.range }));

    const xBarSpecialCauses = detectSpecialCauses(xBarChartPoints, cl, ucl, lcl);
    const rChartSpecialCauses = detectSpecialCauses(rChartPoints, rCL, rUCL, rLCL);

    return { points, cl, ucl, lcl, rPoints, rCL, rUCL, rLCL, xBarSpecialCauses, rChartSpecialCauses };
};

// Function to calculate the inverse of the standard normal CDF (probit function)
function probit(p: number): number {
    if (p <= 0 || p >= 1) return NaN;
    const a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00];
    const b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01];
    const c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00];
    const d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00];
    let q = p - 0.5;
    let r, x;
    if (Math.abs(q) < 0.42) {
        r = q * q;
        x = q * (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
    } else {
        r = p < 0.5 ? p : 1 - p;
        r = Math.log(-Math.log(r));
        x = c[0];
        for (let i = 1; i < c.length; i++) x = c[i] + x * r;
        x = x / (d[0] + r * (d[1] + r * (d[2] + r * d[3])));
        if (p < 0.5) x = -x;
    }
    return x;
}

const calculateQQPlotData = (data: number[]): QQPlotDataPoint[] => {
    const sortedData = [...data].sort((a, b) => a - b);
    const n = sortedData.length;
    if (n === 0) return [];

    return sortedData.map((sample, i) => {
        const p = (i + 1 - 0.5) / n;
        const theoretical = probit(p);
        return { sample, theoretical };
    });
};

export const performStatisticalAnalysis = (data: number[], lsl: number | null, usl: number | null, subgroupSize: number | null): AnalysisResult => {
    const basicStats = calculateBasicStats(data);
    const capability = calculateCapability(data, basicStats, lsl, usl, subgroupSize);
    const histogram = calculateHistogram(data, basicStats, lsl, usl);
    const boxPlot = calculateBoxPlot(basicStats);
    const controlChart = calculateControlChart(data, subgroupSize);
    const qqPlotData = calculateQQPlotData(data);

    return {
        basicStats,
        capability,
        histogram,
        boxPlot,
        controlChart,
        qqPlotData
    };
};