import Link from 'next/link';
import LiveAnalyzer from '../../../components/LiveAnalyzer';
export default function AnalyzePage() { return <main className="app-shell"><header className="app-nav"><Link href="/" className="brand">PHISH<span>GUARD</span></Link><Link href="/" className="button">Back to overview</Link></header><section className="app-main"><div className="kicker">ANALYSIS WORKSPACE / MVP</div><h1>Analyze threat</h1><p>Inspect a suspicious message or URL and receive an evidence-backed risk report. Provider availability is shown in the result.</p><LiveAnalyzer /></section></main> }
