import { useEffect, useState, type CSSProperties } from 'react';
import { Link2, Plus, Copy, Check, Ban, ShieldCheck } from 'lucide-react';
import { shareService } from '../../lib/apiClient';
import type { ShareLink, ShareLinkMinted } from '../../types/domain';
import { colors } from '../../styles/theme';

// Owner-side management of investor/lender share links: mint a revocable,
// read-only link and revoke it. The raw token is shown exactly once (at mint) —
// only its hash is stored server-side — so we surface it in a one-time banner
// with a copy button and a "won't be shown again" warning.
const shareUrl = (token: string) => `${window.location.origin}/investor/${token}`;

const InvestorsPage = () => {
  const [links, setLinks] = useState<ShareLink[]>([]);
  const [loading, setLoading] = useState(true);
  const [label, setLabel] = useState('');
  const [minting, setMinting] = useState(false);
  const [justMinted, setJustMinted] = useState<ShareLinkMinted | null>(null);
  const [copied, setCopied] = useState(false);

  const load = () => {
    shareService.listLinks()
      .then((res) => setLinks(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleMint = async () => {
    setMinting(true);
    try {
      const { data } = await shareService.createLink(label.trim() || undefined);
      setJustMinted(data);
      setCopied(false);
      setLabel('');
      load();
    } catch (err) {
      console.error(err);
    } finally {
      setMinting(false);
    }
  };

  const handleRevoke = async (id: number) => {
    try {
      await shareService.revokeLink(id);
      // If we just minted this one, clear its one-time banner too.
      setJustMinted((m) => (m && m.id === id ? null : m));
      load();
    } catch (err) {
      console.error(err);
    }
  };

  const copy = (token: string) => {
    navigator.clipboard?.writeText(shareUrl(token)).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const card: CSSProperties = { background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '18px' };
  const th: CSSProperties = { textAlign: 'left', fontSize: '10px', fontWeight: 700, letterSpacing: '0.05em', color: colors.textMuted, textTransform: 'uppercase', padding: '10px 12px', borderBottom: `0.5px solid ${colors.border}` };
  const td: CSSProperties = { fontSize: '12px', color: colors.textBody, padding: '11px 12px', borderBottom: `0.5px solid ${colors.dividerLight}` };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      {/* Mint */}
      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <ShieldCheck size={16} color={colors.primaryDark} />
          <h3 style={{ fontSize: '13px', fontWeight: 700, color: colors.text }}>Share a read-only report</h3>
        </div>
        <p style={{ fontSize: '11px', color: colors.textMuted, marginBottom: '14px' }}>
          Give a bank or investor a link to your P&amp;L and yield summary — read-only, no account, and revocable any time.
        </p>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="Label (optional), e.g. First Bank"
            style={{ flex: 1, padding: '9px 12px', borderRadius: '8px', border: `1px solid ${colors.borderInput}`, fontSize: '12px' }}
          />
          <button
            onClick={handleMint}
            disabled={minting}
            style={{ display: 'flex', alignItems: 'center', gap: '7px', background: colors.primaryDark, color: colors.onPrimary, padding: '9px 16px', borderRadius: '8px', border: 'none', fontSize: '12px', fontWeight: 600, cursor: minting ? 'default' : 'pointer', opacity: minting ? 0.7 : 1 }}
          >
            <Plus size={14} /> {minting ? 'Creating…' : 'Create link'}
          </button>
        </div>

        {justMinted && (
          <div style={{ marginTop: '14px', background: colors.primarySurface, border: `0.5px solid ${colors.primaryBorderTint}`, borderRadius: '10px', padding: '12px 14px' }}>
            <p style={{ fontSize: '11px', fontWeight: 700, color: colors.primaryDark, marginBottom: '8px' }}>
              Link created — copy it now. For your security it won’t be shown again.
            </p>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <code style={{ flex: 1, fontSize: '11px', color: colors.textBody, background: colors.surface, border: `0.5px solid ${colors.border}`, borderRadius: '7px', padding: '8px 10px', overflowX: 'auto', whiteSpace: 'nowrap' }}>
                {shareUrl(justMinted.token)}
              </code>
              <button
                onClick={() => copy(justMinted.token)}
                style={{ display: 'flex', alignItems: 'center', gap: '6px', background: colors.surface, color: colors.primaryDark, padding: '8px 12px', borderRadius: '7px', border: `0.5px solid ${colors.borderInput}`, fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}
              >
                {copied ? <><Check size={13} /> Copied</> : <><Copy size={13} /> Copy</>}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Existing links */}
      <div style={{ background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '14px 16px', borderBottom: `0.5px solid ${colors.border}` }}>
          <Link2 size={15} color={colors.textMuted} />
          <h3 style={{ fontSize: '12px', fontWeight: 700, color: colors.text }}>Your share links</h3>
        </div>
        {loading ? (
          <p style={{ fontSize: '12px', color: colors.textMuted, padding: '16px' }}>Loading…</p>
        ) : links.length === 0 ? (
          <p style={{ fontSize: '12px', color: colors.textMuted, padding: '16px' }}>No share links yet. Create one above to grant read-only access.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={th}>Label</th>
                <th style={th}>Created</th>
                <th style={th}>Status</th>
                <th style={{ ...th, textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {links.map((l) => (
                <tr key={l.id}>
                  <td style={{ ...td, fontWeight: 600 }}>{l.label || <span style={{ color: colors.textFaint }}>Untitled</span>}</td>
                  <td style={td}>{new Date(l.created_at).toLocaleDateString()}</td>
                  <td style={td}>
                    <span style={{ fontSize: '10px', fontWeight: 700, padding: '3px 8px', borderRadius: '10px', color: l.revoked ? colors.danger : colors.primaryDark, background: l.revoked ? 'rgba(192,57,43,0.08)' : colors.primarySurface }}>
                      {l.revoked ? 'Revoked' : 'Active'}
                    </span>
                  </td>
                  <td style={{ ...td, textAlign: 'right' }}>
                    {!l.revoked && (
                      <button
                        onClick={() => handleRevoke(l.id)}
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: colors.surface, color: colors.danger, padding: '6px 11px', borderRadius: '7px', border: `0.5px solid ${colors.borderInput}`, fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}
                      >
                        <Ban size={13} /> Revoke
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default InvestorsPage;
