// scripts/copy-vendor.js
// ============================================================================================
//                          COPY VENDOR ASSETS (runs automatically after npm install)
// - Copies the browser-ready build of each renderer-facing library from node_modules
//   into src/vendor/, so index.html can load them with plain <script>/<link> tags.
// ============================================================================================
const fs = require('fs');
const path = require('path');

const VENDOR_FILES = [
    { from: 'node_modules/flatpickr/dist/flatpickr.min.js', to: 'src/vendor/flatpickr/flatpickr.min.js' },
    { from: 'node_modules/flatpickr/dist/flatpickr.min.css', to: 'src/vendor/flatpickr/flatpickr.min.css' }
];

VENDOR_FILES.forEach(({ from, to }) => {
    const sourcePath = path.join(__dirname, '..', from);
    const destPath = path.join(__dirname, '..', to);

    if (!fs.existsSync(sourcePath)) {
        console.warn(`[copy-vendor] Skipped (not found): ${from}`);
        return;
    }

    fs.mkdirSync(path.dirname(destPath), { recursive: true });
    fs.copyFileSync(sourcePath, destPath);
    console.log(`[copy-vendor] Copied: ${to}`);
});