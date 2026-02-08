const esbuild = require('esbuild');

const production = process.argv.includes('--production');
const watch = process.argv.includes('--watch');

/**
 * @type {import('esbuild').BuildOptions}
 */
const commonOptions = {
  entryPoints: [
    'src/popup.ts',
    'src/content.ts',
    'src/background.ts'
  ],
  bundle: true,
  outdir: 'dist',
  minify: production,
  sourcemap: !production,
  target: ['chrome100'],
  platform: 'browser',
};

const fs = require('fs');
const path = require('path');

async function copyFile(src, dest) {
  await fs.promises.copyFile(src, dest);
}

async function copyDir(src, dest) {
  await fs.promises.mkdir(dest, { recursive: true });
  const entries = await fs.promises.readdir(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      await copyDir(srcPath, destPath);
    } else {
      await copyFile(srcPath, destPath);
    }
  }
}

async function main() {
  const ctx = await esbuild.context(commonOptions);

  if (watch) {
    await ctx.watch();
    console.log('Watching...');
  } else {
    await ctx.rebuild();
    await ctx.dispose();
    
    // Copy static assets
    console.log('Copying static assets...');
    await copyFile('manifest.json', 'dist/manifest.json');
    await copyFile('popup.html', 'dist/popup.html');
    await copyFile('popup.css', 'dist/popup.css');
    if (fs.existsSync('icons')) {
        await copyDir('icons', 'dist/icons');
    }
    
    console.log('Build complete');
  }
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
