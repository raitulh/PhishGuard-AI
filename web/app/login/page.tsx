'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowRight, LoaderCircle, Shield } from 'lucide-react';

export default function Login() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!email.trim() || !password.trim()) {
            setError('Please enter both email and password.');
            return;
        }

        setLoading(true);

        try {
            // Store user session in localStorage for client-side state
            const userData = {
                email: email.trim(),
                name: email.split('@')[0],
                loggedInAt: new Date().toISOString(),
                token: 'pg_session_' + Math.random().toString(36).substring(2)
            };
            localStorage.setItem('phishguard_user', JSON.stringify(userData));

            // Short timeout for realistic UX
            await new Promise(resolve => setTimeout(resolve, 500));
            router.push('/app');
        } catch (err) {
            setError('An error occurred during sign in. Please try again.');
            setLoading(false);
        }
    };

    return (
        <main className="app-shell">
            <header className="app-nav">
                <Link href="/" className="brand">PHISH<span>GUARD</span></Link>
                <Link href="/" className="button">Back to home</Link>
            </header>
            <section className="app-main" style={{ maxWidth: 520, margin: '40px auto 0' }}>
                <div className="kicker">PHISHGUARD ACCESS</div>
                <h1>Welcome back.</h1>
                <p>Sign in to review analysis history and connect your workspace.</p>

                <form onSubmit={handleSubmit} className="panel" style={{ padding: 28, display: 'grid', gap: 16 }}>
                    {error && (
                        <div style={{ color: 'var(--red)', fontSize: 14, background: 'rgba(255, 114, 108, 0.1)', padding: '10px 14px', borderRadius: 6, border: '1px solid rgba(255, 114, 108, 0.2)' }}>
                            {error}
                        </div>
                    )}
                    <label style={{ display: 'grid', gap: 6, fontSize: 14 }}>
                        <span>Email address</span>
                        <input
                            className="input"
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="you@example.com"
                            autoComplete="email"
                        />
                    </label>

                    <label style={{ display: 'grid', gap: 6, fontSize: 14 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Password</span>
                            <Link href="/forgot-password" style={{ color: 'var(--cyan)', fontSize: 13 }}>Forgot?</Link>
                        </div>
                        <input
                            className="input"
                            type="password"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            autoComplete="current-password"
                        />
                    </label>

                    <button type="submit" className="button primary" disabled={loading} style={{ justifyContent: 'center', marginTop: 8 }}>
                        {loading ? (
                            <><LoaderCircle size={16} className="spin" /> Signing in...</>
                        ) : (
                            <>Sign in <ArrowRight size={16} /></>
                        )}
                    </button>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 10, fontSize: 13, color: 'var(--muted)' }}>
                        <span>Don't have an account? <Link href="/signup" style={{ color: 'var(--cyan)' }}>Create account</Link></span>
                    </div>
                </form>
            </section>
        </main>
    );
}
