import { NextResponse } from 'next/server';
import { execSync } from 'child_process';
import { resolvePython } from '@/lib/python-resolver';

export async function GET() {
  try {
    const pythonPath = resolvePython();

    // Get bot status
    const result = execSync(
      `"${pythonPath}" -c "from auto_trader.bot import CryptoScalperBot; import json; bot=CryptoScalperBot(); print(json.dumps(bot.get_status(), default=str))"`,
      { timeout: 10000, encoding: 'utf-8' }
    );

    const status = JSON.parse(result.trim());
    return NextResponse.json(status);
  } catch (error: any) {
    return NextResponse.json({
      running: false,
      mode: 'unknown',
      error: error.message,
      trading: {
        paper_trading: true,
        daily_stats: { total_trades: 0, wins: 0, losses: 0, net_pnl: 0 },
        active_positions: 0,
        win_rate: '0%',
        mode: 'PAPER',
      },
      scheduler: {
        running: false,
        current_window: null,
      },
    });
  }
}
