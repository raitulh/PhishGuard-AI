'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowRight, LoaderCircle } from 'lucide-react';

export default function Signup() {
    const router = useRouter();
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!name.trim() || !email.trim() || !password.trim()) {
            setError('Please fill in all fields.');
            return;
        }

        setLoading(true);

        try {
            const userData = {
                name: name.trim(),
                email: email.trim(),
                loggedInAt: new Date().toISOString(),
                token: 'pg_session_' + Math.random().toString(36).substring(2)
            };
            localStorage.setItem('phishguard_user', JSON.stringify(userData));

            await new Promise(resolve => setTimeout(resolve, 500));
            router.push('/app');
        } catch (err) {
            setError('Could not complete signup. Please try again.');
            setLoading(false);
        }
    };

    return (
        <main className="app-shell">
            <header className="app-nav">
                <Link href="/" className="brand">PHISH<span>GUARD</span></Link>
                <Link href="/" className="button">Back to home</Link>
            </header>
            <section className="app-main" style={{ maxWidth: 560, margin: '40px auto 0' }}>
                <div className="kicker">START WITH PHISHGUARD</div>
                <h1>Protect every click.</h1>
                <p>Create a workspace for explainable threat analysis.</p>

                <form onSubmit={handleSubmit} className="panel" style={{ padding: 28, display: 'grid', gap: 16 }}>
                    {error && (
                        <div style={{ color: 'var(--red)', fontSize: 14, background: 'rgba(255, 114, 108, 0.1)', padding: '10px 14px', borderRadius: 6, border: '1px solid rgba(255, 114, 108, 0.2)' }}>
                            {error}
                        </div>
                    )}
                    <label style={{ display: 'grid', gap: 6, fontSize: 14 }}>
                        <span>Full name</span>
                        <input
                            className="input"
                            required
                            placeholder="Your name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </label>

                    <label style={{ display: 'grid', gap: 6, fontSize: 14 }}>
                        <span>Email address</span>
                        <input
                            className="input"
                            type="email"
                            required
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </label>

                    <label style={{ display: 'grid', gap: 6, fontSize: 14 }}>
                        <span>Password</span>
                        <input
                            className="input"
                            type="password"
                            required
                            placeholder="Create a password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </label>

                    <button type="submit" className="button primary" disabled={loading} style={{ justifyContent: 'center', marginTop: 8 }}>
                        {loading ? (
                            <><LoaderCircle size={16} className="spin" /> Creating account...</>
                        ) : (
                            <>Create account <ArrowRight size={16} /></>
                        )}
                    </button>

                    <div style={{ marginTop: 10, fontSize: 13, color: 'var(--muted)' }}>
                        Already have an account? <Link href="/login" style={{ color: 'var(--cyan)' }}>Sign in</Link>
                    </div>
                </form>
            </section>
        </main>
    );
}
