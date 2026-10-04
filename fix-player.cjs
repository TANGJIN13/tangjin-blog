const fs = require('fs');
const path = 'src/components/MusicPlayer.astro';
let content = fs.readFileSync(path, 'utf8');

// Fix: {tracks.length} 首 → {tracks.length + ' 首'} to avoid Astro parser confusion
content = content.replace('{tracks.length} 首', "{tracks.length + ' 首'}");

fs.writeFileSync(path, content, 'utf8');
console.log('Fixed tracks.length template');

// Verify build
const { execSync } = require('child_process');
try {
  execSync('pnpm build', { cwd: '..', stdio: 'pipe', timeout: 120000 });
  console.log('Build OK');
} catch (e) {
  const output = e.stdout?.toString() + e.stderr?.toString();
  const err = output?.match(/Error[^\n]*/g);
  console.log('Build FAILED:', err ? err[0] : 'unknown');
}
