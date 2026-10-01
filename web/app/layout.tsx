import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = { title: 'PhishGuard | Understand the trap', description: 'Explainable phishing and social-engineering intelligence.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
