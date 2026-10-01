'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowRight, ShieldCheck, History, Puzzle, LogOut } from 'lucide-react';

interface UserSession {
    name?: string;
    email?: string;
    loggedInAt?: string;
}

export default function Dashboard() {
    const router = useRouter();
    const [user, setUser] = useState<UserSession | null>(null);
    const [scans, setScans] = useState<any[]>([]);

    useEffect(() => {
        const stored = localStorage.getItem('phishguard_user');
        if (stored) {
            try {
                setUser(JSON.parse(stored));
            } catch (e) {
                // ignore parsing error
            }
        }
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/scans`)
            .then(res => res.json())
            .then(data => setScans(Array.isArray(data) ? data : []))
            .catch(() => {});
    }, []);

    const handleSignOut = () => {
        localStorage.removeItem('phishguard_user');
        setUser(null);
        router.push('/');
    };

    const highRiskCount = scans.filter(s => s.risk_level === 'HIGH_RISK' || s.risk_score >= 75).length;

    return (
        <main className="app-shell">
            <header className="app-nav">
                <Link href="/" className="brand">PHISH<span>GUARD</span></Link>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                    {user && (
                        <span className="mono" style={{ fontSize: 13, color: 'var(--cyan)' }}>
                            ● {user.email || user.name}
                        </span>
                    )}
                    <Link href="/app/analyze" className="button primary">
                        Analyze threat
                    </Link>
                    <button onClick={handleSignOut} className="button" title="Sign out" style={{ padding: '8px 12px' }}>
                        <LogOut size={16} />
                    </button>
                </div>
            </header>

            <section className="app-main">
                <div className="kicker">WORKSPACE / OVERVIEW</div>
                <h1>Welcome{user?.name ? `, ${user.name}` : ''}.</h1>
                <p>Run threat analyses, inspect security evidence, and view detection signals across web and browser sessions.</p>

                <div className="cards">
                    <div className="card">
                        <span className="index">TOTAL SCANS</span>
                        <h3 style={{ color: 'var(--cyan)' }}>{scans.length}</h3>
                        <p>Persisted in SQLite database.</p>
                    </div>
                    <div className="card">
                        <span className="index">HIGH RISK DETECTIONS</span>
                        <h3 style={{ color: highRiskCount > 0 ? 'var(--red)' : 'inherit' }}>{highRiskCount}</h3>
                        <p>Flagged by threat intelligence.</p>
                    </div>
                    <div className="card">
                        <span className="index">ACTIVE PROVIDERS</span>
                        <h3>3 Global APIs</h3>
                        <p>VirusTotal, Google Safe Browsing, and URLhaus.</p>
                    </div>
                </div>

                <div style={{ marginTop: 32, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20 }}>
                    <Link href="/app/analyze" className="panel" style={{ padding: 24, display: 'block', transition: 'border-color 0.2s' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                            <ShieldCheck size={24} style={{ color: 'var(--cyan)' }} />
                            <ArrowRight size={18} />
                        </div>
                        <h3>Analyze Threat</h3>
                        <p style={{ color: 'var(--muted)', fontSize: 14, margin: '8px 0 0' }}>Paste any suspicious URL or email text to receive an explainable risk breakdown.</p>
                    </Link>

                    <Link href="/app/history" className="panel" style={{ padding: 24, display: 'block' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                            <History size={24} style={{ color: 'var(--cyan)' }} />
                            <ArrowRight size={18} />
                        </div>
                        <h3>Scan History</h3>
                        <p style={{ color: 'var(--muted)', fontSize: 14, margin: '8px 0 0' }}>Review previous threat scans and evidence fingerprints stored in the local SQLite database.</p>
                    </Link>

                    <Link href="/app/extension" className="panel" style={{ padding: 24, display: 'block' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                            <Puzzle size={24} style={{ color: 'var(--cyan)' }} />
                            <ArrowRight size={18} />
                        </div>
                        <h3>Browser Extension</h3>
                        <p style={{ color: 'var(--muted)', fontSize: 14, margin: '8px 0 0' }}>Install and configure the Chrome/Edge extension companion for live browsing protection.</p>
                    </Link>
                </div>
            </section>
        </main>
    );
}
