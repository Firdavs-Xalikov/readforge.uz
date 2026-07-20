const fs = require('fs');
const path = require('path');

const filesToCopy = ['index.html', 'login.html', 'admin.html', 'capacitor-runtime.js', 'favicon.svg', '404.html'];
const distDir = path.join(__dirname, 'www');

if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

filesToCopy.forEach(file => {
  const src = path.join(__dirname, file);
  const dest = path.join(distDir, file);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, dest);
    console.log(`Copied ${file} to www/`);
  } else {
    console.warn(`File ${file} not found!`);
  }
});
