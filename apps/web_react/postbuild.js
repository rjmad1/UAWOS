import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const webDir = path.resolve(__dirname, '../web');
const indexHtml = path.join(webDir, 'index.html');
const dashboardHtml = path.join(webDir, 'uawos_dashboard.html');

if (fs.existsSync(indexHtml)) {
  fs.copyFileSync(indexHtml, dashboardHtml);
  fs.unlinkSync(indexHtml);
  console.log('Successfully copied index.html to uawos_dashboard.html');
} else {
  console.log('index.html not found in build output');
}
