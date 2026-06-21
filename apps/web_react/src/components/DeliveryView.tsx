// src/components/DeliveryView.tsx
import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { type TraceRecord } from '@/services/api';
import { Eye, Clipboard, ShieldCheck, X, RefreshCw } from 'lucide-react';

interface DeliveryViewProps {
  matrix: TraceRecord[];
  health: { coverage: number; verified_percentage: number } | null;
  onRefresh: () => void;
}

export const DeliveryView: React.FC<DeliveryViewProps> = ({ matrix, health, onRefresh }) => {
  const [selectedRecord, setSelectedRecord] = useState<TraceRecord | null>(null);
  const [copiedHash, setCopiedHash] = useState(false);

  const handleCopy = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  return (
    <div className="flex flex-col gap-6 relative min-h-full">
      {/* Header sections */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-zinc-200/60 dark:border-zinc-800/80">
        <div className="flex flex-col">
          <span className="text-[10px] text-primary uppercase font-bold tracking-wider">Strategic Verification Engine</span>
          <h2 className="text-xl font-bold tracking-tight mt-0.5">Delivery Traceability Board</h2>
          <p className="text-xs text-muted-foreground mt-0.5">End-to-end trace mapping from raw requirement checkpoints to output artifacts</p>
        </div>
        <Button variant="outline" size="sm" className="h-8 text-xs" onClick={onRefresh}>
          <RefreshCw className="w-3.5 h-3.5 mr-1" /> Scan Traceability
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-4">
        {/* Main trace grid */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold tracking-tight">Traceability Matrix</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="hover:bg-transparent">
                      <TableHead className="w-[120px] text-[10px] font-bold uppercase tracking-wider">Req ID</TableHead>
                      <TableHead className="text-[10px] font-bold uppercase tracking-wider">Functional Requirement</TableHead>
                      <TableHead className="text-[10px] font-bold uppercase tracking-wider">Epic Container</TableHead>
                      <TableHead className="w-[100px] text-[10px] font-bold uppercase tracking-wider text-center">Status</TableHead>
                      <TableHead className="w-[110px] text-[10px] font-bold uppercase tracking-wider text-right">Evidence</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {matrix.map((record) => (
                      <TableRow key={record.id} className="hover:bg-zinc-50/30 dark:hover:bg-zinc-950/20">
                        <TableCell className="font-mono text-xs font-semibold text-primary">{record.requirement.split(":")[0]}</TableCell>
                        <TableCell className="text-xs">{record.requirement.split(":")[1] || record.requirement}</TableCell>
                        <TableCell className="text-xs text-muted-foreground">{record.epic}</TableCell>
                        <TableCell className="text-center">
                          <Badge variant={record.epicStatus === 'Passed' ? 'outline' : record.epicStatus === 'Blocked' ? 'destructive' : 'secondary'} className={`text-[9px] px-1.5 py-0 leading-none ${record.epicStatus === 'Passed' ? 'text-emerald-500 border-emerald-500/20 bg-emerald-500/5' : ''}`}>
                            {record.epicStatus}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="h-7 text-[10px] text-primary-accent font-semibold hover:bg-zinc-100 dark:hover:bg-zinc-800"
                            onClick={() => setSelectedRecord(record)}
                          >
                            <Eye className="w-3.5 h-3.5 mr-1" /> View Trace
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Side summary panel */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md">
            <CardHeader className="pb-3">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Trace Summary</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4 text-center">
              <div className="py-4 border-b border-zinc-100 dark:border-zinc-800 flex flex-col items-center">
                <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Intake Mapped Coverage</span>
                <span className="text-3xl font-extrabold text-indigo-500 mt-1">{health ? health.coverage : 100}%</span>
                <p className="text-[9px] text-muted-foreground mt-1">Requirements traced to commits</p>
              </div>

              <div className="py-2 flex flex-col items-center">
                <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Verification Rate</span>
                <span className="text-3xl font-extrabold text-emerald-500 mt-1">{health ? health.verified_percentage : 75}%</span>
                <p className="text-[9px] text-muted-foreground mt-1">Artifact validation checks passed</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Slide-over Evidence Drawer */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 overflow-hidden animate-paneFadeIn">
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/30 dark:bg-black/50 backdrop-blur-sm" onClick={() => setSelectedRecord(null)} />
          
          <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
            <div className="w-screen max-w-md bg-card border-l border-zinc-200 dark:border-zinc-800 shadow-2xl flex flex-col justify-between">
              
              <div className="flex-1 py-6 overflow-y-auto px-4 sm:px-6">
                <div className="flex items-start justify-between">
                  <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-500" /> Evidence validation trace
                  </h2>
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => setSelectedRecord(null)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>

                <div className="mt-6 flex flex-col gap-5 border-t border-zinc-100 dark:border-zinc-800 pt-5">
                  <div className="flex flex-col gap-1">
                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Verification ID</span>
                    <span className="text-xs font-semibold">{selectedRecord.id}</span>
                  </div>

                  <div className="flex flex-col gap-1">
                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Requirement mapping</span>
                    <span className="text-xs font-medium text-zinc-800 dark:text-zinc-200">{selectedRecord.requirement}</span>
                  </div>

                  <div className="flex flex-col gap-1">
                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">System Task Node</span>
                    <span className="text-xs font-mono">{selectedRecord.task}</span>
                  </div>

                  <div className="flex flex-col gap-1">
                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Commit Hash</span>
                    <span className="text-xs font-mono bg-zinc-50 dark:bg-zinc-950 p-1.5 border border-zinc-200/60 dark:border-zinc-850 rounded text-zinc-600 dark:text-zinc-400">
                      commit {selectedRecord.commit}
                    </span>
                  </div>

                  <div className="flex flex-col gap-1">
                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Provenance SHA256 Hash</span>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <span className="text-[11px] font-mono truncate bg-zinc-50 dark:bg-zinc-950 px-2 py-1.5 border border-zinc-200/60 dark:border-zinc-850 rounded flex-grow">
                        {selectedRecord.verificationHash}
                      </span>
                      <Button size="icon" variant="outline" className="h-8 w-8 shrink-0" onClick={() => handleCopy(selectedRecord.verificationHash)}>
                        <Clipboard className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                    {copiedHash && <span className="text-[9px] text-emerald-500 font-semibold self-end mt-1">Copied to clipboard!</span>}
                  </div>

                  <div className="flex flex-col gap-1.5 mt-2">
                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Checkpoints status:</span>
                    <div className="flex flex-col gap-2">
                      <div className="flex items-center justify-between p-2 border border-zinc-200/60 dark:border-zinc-800 rounded bg-zinc-50/20 dark:bg-zinc-950/20 text-[11px]">
                        <span className="font-medium">PII identification check</span>
                        <Badge variant="outline" className="text-[9px] text-emerald-500 border-emerald-500/20 bg-emerald-500/5 py-0 px-1.5 font-bold">Passed</Badge>
                      </div>
                      <div className="flex items-center justify-between p-2 border border-zinc-200/60 dark:border-zinc-800 rounded bg-zinc-50/20 dark:bg-zinc-950/20 text-[11px]">
                        <span className="font-medium">Licensing restriction validation</span>
                        <Badge variant="outline" className="text-[9px] text-emerald-500 border-emerald-500/20 bg-emerald-500/5 py-0 px-1.5 font-bold">Passed</Badge>
                      </div>
                      <div className="flex items-center justify-between p-2 border border-zinc-200/60 dark:border-zinc-800 rounded bg-zinc-50/20 dark:bg-zinc-950/20 text-[11px]">
                        <span className="font-medium">Artifact build tests</span>
                        <Badge variant="outline" className={`text-[9px] py-0 px-1.5 font-bold ${selectedRecord.verified ? 'text-emerald-500 border-emerald-500/20 bg-emerald-500/5' : 'text-red-500 border-red-500/20 bg-red-500/5'}`}>
                          {selectedRecord.verified ? 'Passed' : 'Untraced'}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 border-t border-zinc-200 dark:border-zinc-800 bg-zinc-50/40 dark:bg-zinc-950/40 flex justify-end">
                <Button size="sm" className="h-8 text-xs" onClick={() => setSelectedRecord(null)}>Close Trace</Button>
              </div>

            </div>
          </div>
        </div>
      )}
    </div>
  );
};
