import { NextResponse } from 'next/server';
import { readFileSync, existsSync, readdirSync } from 'fs';
import { join } from 'path';

export async function GET() {
  try {
    // Find the trade log directory
    const possiblePaths = [
      join(process.cwd(), 'data', 'trade_logs'),
      join(process.cwd(), 'auto_trader', '..', 'data', 'trade_logs'),
    ];

    let logDir = '';
    for (const p of possiblePaths) {
      if (existsSync(p)) {
        logDir = p;
        break;
      }
    }

    if (!logDir) {
      return NextResponse.json({ trades: [], message: 'No trade logs found yet' });
    }

    // Read the most recent log file
    const files = readdirSync(logDir)
      .filter(f => f.startsWith('trades_') && f.endsWith('.jsonl'))
      .sort()
      .reverse();

    if (files.length === 0) {
      return NextResponse.json({ trades: [], message: 'No trades recorded yet' });
    }

    const latestFile = join(logDir, files[0]);
    const content = readFileSync(latestFile, 'utf-8');
    const trades = content
      .split('\n')
      .filter(line => line.trim())
      .map(line => JSON.parse(line))
      .reverse()
      .slice(0, 50); // Last 50 trades

    return NextResponse.json({
      trades,
      file: files[0],
      total_in_file: content.split('\n').filter(l => l.trim()).length,
    });
  } catch (error: any) {
    return NextResponse.json(
      { trades: [], error: error.message },
      { status: 500 }
    );
  }
}
