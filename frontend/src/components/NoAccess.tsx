import { Lock } from 'lucide-react';
import { EmptyState } from './EmptyState';
import { colors } from '../styles/theme';

// The panel shown where a signed-in user's ROLE does not admit the data.
//
// Built on EmptyState so a refusal reads like every other non-result surface in
// the app rather than like an error. It is not an error: the user is signed in,
// the request worked, and the answer is "not for this role".
//
// THE COPY DELIBERATELY NAMES NOBODY AND NOTHING. It does not print the
// permission the server wanted, the role the caller holds, or the status code —
// those describe the implementation, and the person reading this cannot act on
// them. It says who can change it (the farm owner), which is the only next step
// available to a worker who genuinely needs the screen.
interface NoAccessProps {
  /** What was withheld, in the farm's language — "the farm's financial figures". */
  what?: string;
  /** Bare inside a panel that already draws its own card. */
  bare?: boolean;
}

export const NoAccess = ({ what = 'this information', bare = false }: NoAccessProps) => (
  <EmptyState
    bare={bare}
    icon={<Lock size={22} color={colors.primary} />}
    title="You don't have permission to view this"
    description={`Your role on this farm does not include access to ${what}. Ask the farm owner if you need it.`}
  />
);
