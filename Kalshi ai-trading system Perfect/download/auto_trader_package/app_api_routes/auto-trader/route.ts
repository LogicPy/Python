import { NextResponse } from 'next/server';
import { execSync } from 'child_process';
import { resolvePython } from '@/lib/python-resolver';

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const action = body.action || 'start';

    const pythonPath = resolvePython();

    if (action === 'start') {
      const symbols = body.symbols || 'BTC,ETH,XRP';
      const liveFlag = body.live ? '--live' : '';
      const cmd = `"${pythonPath}" -m auto_trader.bot --symbols ${symbols} ${liveFlag}`;
      try {
        execSync(cmd, { timeout: 5000, detached: true });
      } catch {
        // Bot runs as daemon — timeout is expected
      }
      return NextResponse.json({ status: 'started', mode: body.live ? 'live' : 'paper' });
    }

    if (action === 'stop') {
      try {
        execSync('pkill -f "auto_trader.bot"', { timeout: 3000 });
      } catch {
        // Process might not be running
      }
      return NextResponse.json({ status: 'stopped' });
    }

    if (action === 'status') {
      const pythonPath = resolvePython();
      try {
        const result = execSync(
          `"${pythonPath}" -c "from auto_trader.bot import CryptoScalperBot; import json; bot=CryptoScalperBot(); print(json.dumps(bot.get_status(), default=str))"`,
          { timeout: 10000, encoding: 'utf-8' }
        );
        return NextResponse.json(JSON.parse(result.trim()));
      } catch {
        return NextResponse.json({ status: 'unknown', running: false });
      }
    }

    return NextResponse.json({ error: 'Unknown action' }, { status: 400 });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Auto-trader operation failed' },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const pythonPath = resolvePython();
    const result = execSync(
      `"${pythonPath}" -c "from auto_trader.bot import CryptoScalperBot; import json; bot=CryptoScalperBot(); print(json.dumps(bot.get_status(), default=str))"`,
      { timeout: 10000, encoding: 'utf-8' }
    );
    return NextResponse.json(JSON.parse(result.trim()));
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message, running: false },
      { status: 500 }
    );
  }
}
