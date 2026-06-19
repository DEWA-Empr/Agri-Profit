import { MessageSquare } from 'lucide-react';
import { ComingSoon } from '../../components/ComingSoon';

const UssdPage = () => (
  <ComingSoon
    title="USSD / SMS"
    description="Low-bandwidth access so farmers can log activities and check figures from any phone, without the app."
    icon={<MessageSquare size={40} />}
  />
);

export default UssdPage;
