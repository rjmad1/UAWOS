// src/components/DashboardView.tsx
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { type SystemStatus } from '@/services/api';
import { Activity, Server, AlertOctagon, Play, Pause, RefreshCw, Cpu, Layers } from 'lucide-react';

interface DashboardViewProps {
  status: SystemStatus | null;
  onRefresh: () => void;
  onKillAgent: (agentName: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ status, onRefresh, onKillAgent }) => {
  if (!status) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">Gathering system health telemetry...</p>
      </div>
    );
  }

  const { health_summary, running_containers, domains, git_sync } = status;
  const healthColorClass = 
    health_summary.strict_percentage > 85 ? 'text-emerald-500' :
    health_summary.strict_percentage > 60 ? 'text-amber-500' : 'text-red-500';

  // Extract active blockers (YELLOW or RED status from domains)
  const blockers: { domain: string; name: string; status: string }[] = [];
  Object.entries(domains).forEach(([domain, items]) => {
    Object.entries(items).forEach(([name, val]) => {
      if (val === 'RED' || val === 'YELLOW') {
        blockers.push({ domain, name, status: val });
      }
    });
  });

  return (
    <div className="flex flex-col gap-6">
      {/* Header telemetry cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/60 backdrop-blur-md">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Strict System Health</CardTitle>
            <Activity className={`w-4 h-4 ${healthColorClass}`} />
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold tracking-tight ${healthColorClass}`}>{health_summary.strict_percentage}%</div>
            <p className="text-xs text-muted-foreground mt-1">Direct unweighted components status</p>
            <Progress value={health_summary.strict_percentage} className="h-1.5 mt-3" />
          </CardContent>
        </Card>

        <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/60 backdrop-blur-md">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Weighted System Health</CardTitle>
            <Layers className="w-4 h-4 text-violet-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold tracking-tight text-violet-500 dark:text-violet-400">{health_summary.weighted_percentage}%</div>
            <p className="text-xs text-muted-foreground mt-1">Weighted capability health rollup</p>
            <Progress value={health_summary.weighted_percentage} className="h-1.5 mt-3" />
          </CardContent>
        </Card>

        <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/60 backdrop-blur-md">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Active Blockers</CardTitle>
            <AlertOctagon className={`w-4 h-4 ${blockers.length > 0 ? 'text-amber-500' : 'text-zinc-400'}`} />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold tracking-tight">{blockers.length}</div>
            <p className="text-xs text-muted-foreground mt-1">Violations & component warnings</p>
            <div className="flex gap-1.5 mt-3.5">
              <Badge variant={blockers.filter(b => b.status === 'RED').length > 0 ? 'destructive' : 'secondary'} className="text-[10px] px-1.5 py-0">
                {blockers.filter(b => b.status === 'RED').length} critical
              </Badge>
              <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                {blockers.filter(b => b.status === 'YELLOW').length} warnings
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/60 backdrop-blur-md">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Real-Time State</CardTitle>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[10px] font-semibold text-emerald-500 uppercase tracking-wider">Live</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-sm font-semibold tracking-tight text-zinc-700 dark:text-zinc-300 mt-1">Server-Sent Events</div>
            <p className="text-xs text-muted-foreground mt-1">{git_sync ? git_sync.message : 'State listener connected'}</p>
            <div className="flex items-center gap-2 mt-4 text-[10px] text-muted-foreground">
              <Server className="w-3.5 h-3.5" />
              <span>BFF Port 8099 Online</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Active Blockers list */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md flex-1">
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-sm font-bold tracking-tight">Active Blocker Alerts</CardTitle>
                <CardDescription className="text-[11px] mt-0.5">Critical policy exceptions</CardDescription>
              </div>
              <Button size="sm" variant="outline" className="h-7 text-[10px]" onClick={onRefresh}>
                <RefreshCw className="w-3 h-3 mr-1" /> Poll Status
              </Button>
            </CardHeader>
            <CardContent className="flex flex-col gap-3 max-h-[350px] overflow-y-auto pr-1">
              {blockers.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center border border-dashed border-zinc-200 dark:border-zinc-800 rounded-lg bg-zinc-50/20 dark:bg-zinc-950/20">
                  <span className="w-6 h-6 rounded-full bg-emerald-100 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold text-xs">✓</span>
                  <p className="text-xs font-semibold text-zinc-700 dark:text-zinc-300 mt-2">All boundaries healthy</p>
                  <p className="text-[10px] text-muted-foreground mt-0.5">No loop anomalies detected</p>
                </div>
              ) : (
                blockers.map((block, idx) => (
                  <Alert key={idx} variant={block.status === 'RED' ? 'destructive' : 'default'} className="border-zinc-200 dark:border-zinc-800 bg-zinc-50/40 dark:bg-zinc-950/40 p-3 flex flex-col gap-1">
                    <div className="flex items-center justify-between w-full">
                      <AlertTitle className="text-xs font-bold leading-none tracking-tight">
                        {block.name}
                      </AlertTitle>
                      <Badge variant={block.status === 'RED' ? 'destructive' : 'outline'} className="text-[9px] px-1.5 py-0 leading-none">
                        {block.status}
                      </Badge>
                    </div>
                    <AlertDescription className="text-[10px] text-muted-foreground">
                      Scope: {block.domain} • Action Required: Review parameters or request waiver override.
                    </AlertDescription>
                  </Alert>
                ))
              )}
            </CardContent>
          </Card>
        </div>

        {/* Workforce Entities and Runaway Loop Controller */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold tracking-tight">Autonomous Execution Entities</CardTitle>
              <CardDescription className="text-[11px] mt-0.5">Workforce capabilities and trust safeguards</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-2">
                {Object.entries(domains.Agents || {}).map(([name, state], idx) => {
                  const isSuspended = state === 'GRAY';
                  return (
                    <div key={idx} className="flex items-center justify-between p-3 rounded-lg border border-zinc-200/60 dark:border-zinc-800 bg-zinc-50/30 dark:bg-zinc-950/30">
                      <div className="flex items-center gap-3">
                        <Cpu className={`w-4 h-4 ${isSuspended ? 'text-zinc-400' : 'text-indigo-500'}`} />
                        <div className="flex flex-col">
                          <span className="text-xs font-semibold">{name}</span>
                          <span className="text-[10px] text-muted-foreground mt-0.5">Trust Score: {isSuspended ? '0.00' : '0.94'} • Autonomy L3</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={state === 'GREEN' ? 'outline' : 'secondary'} className={`text-[9px] px-1.5 py-0 ${state === 'GREEN' ? 'text-emerald-500 border-emerald-500/20 bg-emerald-500/5' : ''}`}>
                          {state === 'GREEN' ? 'Active' : 'Suspended'}
                        </Badge>
                        <Button 
                          size="sm" 
                          variant="ghost" 
                          className="h-6 w-6 p-0 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 text-muted-foreground hover:text-zinc-900"
                          onClick={() => onKillAgent(name)}
                          title={isSuspended ? "Resume Agent" : "Suspend Agent (Kill Switch)"}
                        >
                          {isSuspended ? <Play className="w-3.5 h-3.5 text-emerald-500" /> : <Pause className="w-3.5 h-3.5 text-red-500" />}
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Infrastructure Node Telemetry Grid */}
      <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-bold tracking-tight">System Infrastructure Nodes</CardTitle>
          <CardDescription className="text-[11px] mt-0.5">Docker container statuses and database ports checks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Object.entries(domains.Infrastructure || {}).map(([name, val], idx) => {
              const containerName = name.toLowerCase().replace(/ /g, '-');
              const containerInfo = running_containers[containerName] || running_containers[`uawos-${containerName}`] || 'Container inactive';
              return (
                <div key={idx} className="p-3.5 rounded-lg border border-zinc-200/60 dark:border-zinc-800 bg-zinc-50/20 dark:bg-zinc-950/20 flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-zinc-800 dark:text-zinc-200">{name}</span>
                    <Badge variant="outline" className={`text-[9px] px-1.5 py-0 ${val === 'GREEN' ? 'text-emerald-500 border-emerald-500/20 bg-emerald-500/5' : 'text-red-500 border-red-500/20 bg-red-500/5'}`}>
                      {val === 'GREEN' ? 'Online' : 'Degraded'}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground mt-0.5">
                    <Server className="w-3 h-3" />
                    <span className="truncate">{containerInfo}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
