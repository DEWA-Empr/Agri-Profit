import { reportsService } from '../../lib/apiClient';

// Triggers a browser download of the P&L CSV. The endpoint sets a
// Content-Disposition attachment header; the anchor click saves the file.
export function downloadPnlCsv(): void {
  const a = document.createElement('a');
  a.href = reportsService.pnlCsvUrl();
  a.download = 'agriprofit_pnl_report.csv';
  document.body.appendChild(a);
  a.click();
  a.remove();
}
