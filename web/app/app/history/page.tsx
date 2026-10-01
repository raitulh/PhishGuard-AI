'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ShieldCheck, RefreshCw, ArrowRight } from 'lucide-react';
import { getScanHistory, ScanHistoryItem } from '../../../lib/api';

export default function HistoryPage() {
    const [scans, setScans] = useState<ScanHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);

    const loadScans = async () => {
        setLoading(true);
        try {
            const data = await getScanHistory();
            setScans(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadScans();
    }, []);

    const getBadgeStyle = (level: string, score: number) => {
        if (score >= 75 || level === 'HIGH_RISK') {
            return { color: 'var(--red)', background: 'rgba(255, 114, 108, 0.1)', border: '1px solid rgba(255, 114, 108, 0.25)' };
        }
        if (score >= 50 || level === 'SUSPICIOUS') {
            return { color: 'var(--amber)', background: 'rgba(243, 201, 105, 0.1)', border: '1px solid rgba(243, 201, 105, 0.25)' };
        }
        if (score >= 25 || level === 'CAUTION') {
            return { color: '#64b5f6', background: 'rgba(100, 181, 246, 0.1)', border: '1px solid rgba(100, 181, 246, 0.25)' };
        }
        return { color: 'var(--cyan)', background: 'rgba(109, 232, 208, 0.1)', border: '1px solid rgba(109, 232, 208, 0.25)' };
    };

    return (
        <main className="app-shell">
            <header className="app-nav">
                <Link href="/" className="brand">PHISH<span>GUARD</span></Link>
                <div style={{ display: 'flex', gap: 12 }}>
                    <Link href="/app" className="button">Dashboard</Link>
                    <Link href="/app/analyze" className="button primary">New analysis</Link>
                </div>
            </header>

            <section className="app-main">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
                    <div>
                        <div className="kicker">WORKSPACE / HISTORY</div>
                        <h1>Threat Scan History</h1>
                        <p>Structured analysis reports and evidence fingerprints stored in your local database.</p>
                    </div>
                    <button onClick={loadScans} disabled={loading} className="button" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
                    </button>
                </div>

                {loading ? (
                    <div className="panel" style={{ padding: 40, textAlign: 'center', color: 'var(--muted)' }}>
                        Loading scan history...
                    </div>
                ) : scans.length === 0 ? (
                    <div className="panel" style={{ padding: 48, textAlign: 'center' }}>
                        <ShieldCheck size={36} style={{ color: 'var(--cyan)', marginBottom: 12 }} />
                        <h3>No scan records found yet</h3>
                        <p style={{ color: 'var(--muted)', margin: '8px 0 20px' }}>Analyze your first suspicious link or email message to see structured records here.</p>
                        <Link href="/app/analyze" className="button primary" style={{ display: 'inline-flex', margin: 'auto' }}>
                            Start first analysis <ArrowRight size={16} />
                        </Link>
                    </div>
                ) : (
                    <div className="panel" style={{ overflow: 'hidden', padding: 0 }}>
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 14 }}>
                                <thead>
                                    <tr style={{ borderBottom: '1px solid var(--line)', background: 'var(--surface2)', color: 'var(--muted)' }}>
                                        <th style={{ padding: '14px 20px' }}>SCAN ID</th>
                                        <th style={{ padding: '14px 20px' }}>TARGET / EVIDENCE</th>
                                        <th style={{ padding: '14px 20px' }}>RISK SCORE</th>
                                        <th style={{ padding: '14px 20px' }}>RISK LEVEL</th>
                                        <th style={{ padding: '14px 20px' }}>CONFIDENCE</th>
                                        <th style={{ padding: '14px 20px' }}>SCANNED AT</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {scans.map((scan) => {
                                        const badgeStyle = getBadgeStyle(scan.risk_level, scan.risk_score);
                                        const dateStr = new Date(scan.created_at).toLocaleString();
                                        return (
                                            <tr key={scan.id} style={{ borderBottom: '1px solid var(--line)', transition: 'background 0.2s' }}>
                                                <td style={{ padding: '16px 20px' }} className="mono">
                                                    <span style={{ color: 'var(--cyan)' }}>{scan.id}</span>
                                                </td>
                                                <td style={{ padding: '16px 20px', maxWidth: 320, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                    <span title={scan.target || scan.input_hash} className="mono" style={{ fontSize: 13 }}>
                                                        {scan.target || scan.input_hash.substring(0, 16) + '...'}
                                                    </span>
                                                </td>
                                                <td style={{ padding: '16px 20px' }}>
                                                    <b style={{ fontSize: 16 }}>{scan.risk_score}</b>
                                                    <span style={{ color: 'var(--muted)', fontSize: 12 }}> / 100</span>
                                                </td>
                                                <td style={{ padding: '16px 20px' }}>
                                                    <span style={{ padding: '4px 10px', borderRadius: 4, fontSize: 12, fontWeight: 600, textTransform: 'uppercase', ...badgeStyle }}>
                                                        {scan.risk_level.replaceAll('_', ' ')}
                                                    </span>
                                                </td>
                                                <td style={{ padding: '16px 20px', color: 'var(--muted)' }}>
                                                    {scan.confidence}
                                                </td>
                                                <td style={{ padding: '16px 20px', color: 'var(--muted)', fontSize: 13 }}>
                                                    {dateStr}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </section>
        </main>
    );
}
