export type RiskLevel = 'LOW_OBSERVED_RISK' | 'CAUTION' | 'SUSPICIOUS' | 'HIGH_RISK';
export type AnalysisResult = {
    scan_id: string;
    risk_score: number;
    risk_level: RiskLevel;
    confidence: string;
    summary: string;
    red_flags: { title: string; severity: string; evidence: string }[];
    recommendation: string[];
    provider_status: Record<string, string>;
    url_analysis: Record<string, unknown>;
    evidence: { source: string; signal: string; severity: string; weight: number; evidence: string }[];
};

export type ScanHistoryItem = {
    id: string;
    input_hash: string;
    target?: string;
    risk_score: number;
    risk_level: RiskLevel;
    confidence: string;
    created_at: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function analyzeThreat(input: { text?: string; url?: string }): Promise<AnalysisResult> {
    const response = await fetch(`${API_URL}/api/v1/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input)
    });
    if (!response.ok) throw new Error(response.status === 429 ? 'Rate limit reached. Try again shortly.' : 'Analysis service is unavailable.');
    return response.json();
}

export async function getScanHistory(): Promise<ScanHistoryItem[]> {
    try {
        const response = await fetch(`${API_URL}/api/v1/scans`, { cache: 'no-store' });
        if (!response.ok) return [];
        return response.json();
    } catch {
        return [];
    }
}
