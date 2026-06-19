import { MessageCircle } from 'lucide-react';
import { ComingSoon } from '../../components/ComingSoon';

const WhatsappPage = () => (
  <ComingSoon
    title="WhatsApp"
    description="Conversational access to logging and reports through a WhatsApp business integration."
    icon={<MessageCircle size={40} />}
  />
);

export default WhatsappPage;
