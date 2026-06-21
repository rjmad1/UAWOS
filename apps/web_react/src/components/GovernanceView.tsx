// src/components/GovernanceView.tsx
import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ExceptionWaiver } from '@/services/api';
import { ShieldAlert, CheckCircle2, Lock, Unlock, FileCheck, CircleCheck, Info, XCircle } from 'lucide-react';

interface GovernanceViewProps {
  waivers: ExceptionWaiver[];
  activeRole: string;
  onApproveWaiver: (id: string, token: string) => void;
  onRejectWaiver: (id: string) => void;
}

export const GovernanceView: React.FC<GovernanceViewProps> = ({ waivers, activeRole, onApproveWaiver, onRejectWaiver }) => {
  const [selectedId, setSelectedId] = useState<string>(() => waivers[0]?.id || '');
  const [signatureToken, setSignatureToken] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  const selectedWaiver = waivers.find(w => w.id === selectedId) || waivers[0];

  // Separation of Duties check: Prohibits role Developer or Compliance from approving
  const isAuthorizedRole = activeRole === 'Admin' || activeRole === 'Strategic Administrator';

  const handleApprove = (e: React.FormEvent) => {
    e.preventDefault();
    if (!signatureToken.trim()) {
      setValidationError("Override signature token is required.");
      return;
    }
    if (signatureToken.length < 6) {
      setValidationError("Signature token must be at least 6 characters.");
      return;
    }
    setValidationError(null);
    onApproveWaiver(selectedWaiver.id, signatureToken);
    setSignatureToken('');
  };

  const handleReject = () => {
    onRejectWaiver(selectedWaiver.id);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-zinc-200/60 dark:border-zinc-800/80">
        <div className="flex flex-col">
          <span className="text-[10px] text-primary uppercase font-bold tracking-wider">Stateless Compliance Control plane</span>
          <h2 className="text-xl font-bold tracking-tight mt-0.5">Governance Exception & Waiver Queue</h2>
          <p className="text-xs text-muted-foreground mt-0.5">Authoritative overrides management and Separation of Duties policy audits</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Exception list sidebar */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md flex-1">
            <CardHeader className="pb-3">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Exception Queue</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              {waivers.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center border border-dashed border-zinc-200 dark:border-zinc-800 rounded-lg bg-zinc-50/20 dark:bg-zinc-950/20">
                  <span className="w-6 h-6 rounded-full bg-emerald-100 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold text-xs">✓</span>
                  <p className="text-xs font-semibold text-zinc-700 dark:text-zinc-300 mt-2">Queue is clean</p>
                  <p className="text-[10px] text-muted-foreground mt-0.5">No waivers pending</p>
                </div>
              ) : (
                waivers.map((w) => (
                  <div
                    key={w.id}
                    onClick={() => {
                      setSelectedId(w.id);
                      setValidationError(null);
                    }}
                    className={`p-3 rounded-lg border cursor-pointer transition-all duration-150 flex flex-col gap-1.5 ${
                      selectedId === w.id
                        ? 'border-primary bg-primary/5'
                        : 'border-zinc-200/60 dark:border-zinc-800/80 bg-zinc-50/20 dark:bg-zinc-950/20 hover:border-zinc-300'
                    }`}
                  >
                    <div className="flex justify-between items-center text-xs font-bold">
                      <span className="text-primary">{w.id}</span>
                      <Badge variant={w.status === 'approved' ? 'outline' : w.status === 'rejected' ? 'destructive' : 'secondary'} className={`text-[9px] px-1.5 py-0 leading-none ${w.status === 'approved' ? 'text-emerald-500 border-emerald-500/20 bg-emerald-500/5' : ''}`}>
                        {w.status}
                      </Badge>
                    </div>
                    <div className="text-[10px] text-muted-foreground truncate font-medium">Policy: {w.policyId}</div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>

        {/* Waiver Details and Signing Panel */}
        {selectedWaiver && (
          <div className="lg:col-span-2 flex flex-col gap-6 animate-paneFadeIn">
            <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md">
              <CardHeader className="pb-3 flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-sm font-bold tracking-tight">Waiver Request Detail ({selectedWaiver.id})</CardTitle>
                  <CardDescription className="text-[10px] mt-0.5">Requested by {selectedWaiver.requestor} on {selectedWaiver.date}</CardDescription>
                </div>
                <Badge variant="outline" className="text-[10px] font-mono">{selectedWaiver.policyId}</Badge>
              </CardHeader>
              <CardContent className="flex flex-col gap-4">
                {/* OPA Policy frame */}
                <div className="flex flex-col gap-2">
                  <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider flex items-center gap-1">
                    <Info className="w-3.5 h-3.5" /> Violated Declarative Policy Clause
                  </span>
                  <pre className="p-3 rounded-lg border border-zinc-200/60 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50 text-[11px] font-mono text-zinc-600 dark:text-zinc-400 overflow-x-auto whitespace-pre-wrap">
                    {selectedWaiver.ruleClause}
                  </pre>
                </div>

                <div className="flex flex-col gap-1.5 border-t border-zinc-100 dark:border-zinc-850 pt-3">
                  <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Justification Statement</span>
                  <p className="text-xs text-zinc-800 dark:text-zinc-200 leading-relaxed font-medium bg-zinc-50/20 dark:bg-zinc-950/10 p-3 border border-zinc-200/50 dark:border-zinc-800 rounded-lg">
                    {selectedWaiver.justification}
                  </p>
                </div>

                {/* Separation of Duties feedback */}
                {!isAuthorizedRole && selectedWaiver.status === 'pending' && (
                  <Alert variant="destructive" className="border-amber-500/25 bg-amber-500/5 text-amber-600 dark:text-amber-400 mt-2">
                    <Lock className="w-4 h-4 text-amber-500" />
                    <AlertTitle className="text-xs font-bold leading-none tracking-tight">Separation of Duties Warning</AlertTitle>
                    <AlertDescription className="text-[10px] mt-1">
                      Waiver override approval locked. Proposing role ({activeRole}) is not authorized. Secondary sign-off requires Admin or Strategic Administrator credentials.
                    </AlertDescription>
                  </Alert>
                )}

                {selectedWaiver.status === 'approved' && (
                  <Alert className="border-emerald-500/20 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400 mt-2">
                    <CircleCheck className="w-4 h-4 text-emerald-500" />
                    <AlertTitle className="text-xs font-bold leading-none tracking-tight">Waiver Signed</AlertTitle>
                    <AlertDescription className="text-[10px] mt-1">
                      This exception has been authorized by an administrator. Paused tasks have resumed.
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>

              {selectedWaiver.status === 'pending' && (
                <CardFooter className="pt-4 border-t border-zinc-200 dark:border-zinc-800/80 bg-zinc-50/20 dark:bg-zinc-950/20 flex flex-col items-stretch gap-4 rounded-b-lg">
                  {isAuthorizedRole ? (
                    <form onSubmit={handleApprove} className="flex flex-col gap-3 w-full">
                      <div className="flex flex-col gap-2">
                        <Label htmlFor="sig-token" className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Override Signature Token</Label>
                        <div className="flex gap-2">
                          <Input
                            id="sig-token"
                            placeholder="Enter signature authorization token..."
                            value={signatureToken}
                            onChange={(e) => setSignatureToken(e.target.value)}
                            className="h-8 text-xs border-zinc-200/60 dark:border-zinc-800/80 focus-visible:ring-emerald-500/20"
                          />
                          <Button type="submit" size="sm" className="h-8 text-xs bg-emerald-600 hover:bg-emerald-500 text-white shrink-0">
                            <Unlock className="w-3.5 h-3.5 mr-1" /> Approve Waiver
                          </Button>
                        </div>
                        {validationError && <span className="text-[10px] text-red-500 font-semibold">{validationError}</span>}
                      </div>
                    </form>
                  ) : (
                    <div className="flex justify-end gap-2 w-full">
                      <Button size="sm" variant="outline" className="h-8 text-xs shrink-0" disabled>
                        <Lock className="w-3.5 h-3.5 mr-1" /> Override Locked
                      </Button>
                    </div>
                  )}
                </CardFooter>
              )}
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};
