import { FileText } from 'lucide-react';
import { ComingSoon } from '../../components/ComingSoon';

const ReportsPage = () => (
  <ComingSoon
    title="P&L Report"
    description="Profit & loss reporting with categorized revenue/expense breakdown and CSV export is coming next. The Export button in the header will download from here."
    icon={<FileText size={40} />}
  />
);

export default ReportsPage;
