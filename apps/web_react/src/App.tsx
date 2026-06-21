// src/App.tsx
import { useState, useEffect } from 'react';
import { DashboardView } from './components/DashboardView';
import { IngestionView } from './components/IngestionView';
import { PlanningView } from './components/PlanningView';
import { RoadmapView } from './components/RoadmapView';
import { DeliveryView } from './components/DeliveryView';
import { GovernanceView } from './components/GovernanceView';
import { TopologyView } from './components/TopologyView';
import { KnowledgeView } from './components/KnowledgeView';
import { 
  api, 
  mockWaivers, 
  type Objective, 
  type SystemStatus, 
  type TraceRecord, 
  type ExceptionWaiver 
} from './services/api';
import { 
  LayoutDashboard, 
  FileInput, 
  Compass, 
  Milestone, 
  FileCheck2, 
  ShieldAlert, 
  Network, 
  BookOpen, 
  Sun, 
  Moon, 
  RefreshCw, 
  User, 
  Key,
  ChevronDown,
  Layers,
  Lock,
  Globe
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger, 
  DropdownMenuLabel, 
  DropdownMenuSeparator 
} from '@/components/ui/dropdown-menu';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription, 
  DialogFooter 
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';

type ViewType = 'dashboard' | 'ingestion' | 'planning' | 'roadmap' | 'delivery' | 'exceptions' | 'architecture' | 'knowledge';

function App() {
  // Navigation & UI States
  const [activeView, setActiveView] = useState<ViewType>('dashboard');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [tenantId, setTenantId] = useState<string>('tenant-primary');
  const [activeRole, setActiveRole] = useState<string>('Developer');
  const [token, setToken] = useState<string>('operator-auth-token-1082');
  const [tokenInput, setTokenInput] = useState<string>('');
  const [authDialogOpen, setAuthDialogOpen] = useState<boolean>(false);
  const [isAuthValid, setIsAuthValid] = useState<boolean>(true);
  const [tokenExpiresMin, setTokenExpiresMin] = useState<number>(45);

  // Business Entity States
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [objectives, setObjectives] = useState<Objective[]>([]);
  const [selectedObjectiveId, setSelectedObjectiveId] = useState<string>('');
  const [traceability, setTraceability] = useState<TraceRecord[]>([]);
  const [traceHealth, setTraceHealth] = useState<{ coverage: number; verified_percentage: number } | null>(null);
  const [waivers, setWaivers] = useState<ExceptionWaiver[]>([]);
  
  // Loading States
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isPolling, setIsPolling] = useState<boolean>(false);

  // Initialize theme
  useEffect(() => {
    const savedTheme = localStorage.getItem('uawos-theme') as 'light' | 'dark' | null;
    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      setTheme('light');
    }
  }, []);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('uawos-theme', theme);
  }, [theme]);

  // Hash Routing Parser
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash;
      if (hash === '#c4-topology') setActiveView('architecture');
      else if (hash === '#delivery') setActiveView('delivery');
      else if (hash === '#ingestion-studio') setActiveView('ingestion');
      else if (hash === '#roadmap-timeline') setActiveView('roadmap');
      else if (hash === '#exceptions') setActiveView('exceptions');
      else if (hash === '#knowledge') setActiveView('knowledge');
      else if (hash === '#dashboard') setActiveView('dashboard');
      else if (hash === '#planning') setActiveView('planning');
    };

    handleHashChange(); // Run on mount
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  // Synchronize hash to activeView
  useEffect(() => {
    let hash = '';
    if (activeView === 'architecture') hash = '#c4-topology';
    else if (activeView === 'delivery') hash = '#delivery';
    else if (activeView === 'ingestion') hash = '#ingestion-studio';
    else if (activeView === 'roadmap') hash = '#roadmap-timeline';
    else if (activeView === 'exceptions') hash = '#exceptions';
    else if (activeView === 'knowledge') hash = '#knowledge';
    else if (activeView === 'dashboard') hash = '#dashboard';
    else if (activeView === 'planning') hash = '#planning';
    
    if (hash && window.location.hash !== hash) {
      window.history.pushState(null, '', hash);
    }
  }, [activeView]);

  // Load Initial Data
  const loadData = async (silent = false) => {
    if (!silent) setIsLoading(true);
    else setIsPolling(true);
    
    try {
      const statusRes = await api.getStatus();
      setStatus(statusRes);

      const objRes = await api.getObjectives();
      setObjectives(objRes);
      
      const traceRes = await api.getTraceability();
      setTraceability(traceRes.matrix);
      setTraceHealth(traceRes.health);
    } catch (e) {
      console.error("Data load failed", e);
    } finally {
      setIsLoading(false);
      setIsPolling(false);
    }
  };

  useEffect(() => {
    // Load once
    loadData();
    // Pre-populate waivers with mock data for local interactive state
    setWaivers(mockWaivers);
  }, [tenantId]);

  // Token credential timer simulation
  useEffect(() => {
    const timer = setInterval(() => {
      setTokenExpiresMin(prev => {
        if (prev <= 1) {
          setIsAuthValid(false);
          return 0;
        }
        return prev - 1;
      });
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  // Set default selected objective if not set
  useEffect(() => {
    if (objectives.length > 0 && !selectedObjectiveId) {
      // Find active first, or default to first
      const activeObj = objectives.find(o => o.status === 'active') || objectives[0];
      setSelectedObjectiveId(activeObj.id);
    }
  }, [objectives, selectedObjectiveId]);

  const selectedObjective = objectives.find(o => o.id === selectedObjectiveId) || objectives[0];

  // Actions
  const handleRefresh = () => {
    loadData(true);
  };

  const handleKillAgent = (agentName: string) => {
    if (!status) return;
    const updatedAgents = { ...status.domains.Agents };
    const currentStatus = updatedAgents[agentName];
    const newStatus = currentStatus === 'GREEN' ? 'GRAY' : 'GREEN';
    updatedAgents[agentName] = newStatus;
    
    // Recalculate health summaries dynamically
    let total = 0;
    let green = 0;
    let gray = 0;
    Object.entries(updatedAgents).forEach(([_, v]) => {
      total++;
      if (v === 'GREEN') green++;
      if (v === 'GRAY') gray++;
    });

    // Roll up other domains
    Object.entries(status.domains).forEach(([dName, dVal]) => {
      if (dName !== 'Agents') {
        Object.values(dVal).forEach(v => {
          total++;
          if (v === 'GREEN') green++;
          if (v === 'GRAY') gray++;
        });
      }
    });

    const strict_percentage = Math.round((green / total) * 1000) / 10;
    const weighted_percentage = Math.round((green / (total - gray)) * 1000) / 10;

    setStatus({
      ...status,
      domains: {
        ...status.domains,
        Agents: updatedAgents
      },
      health_summary: {
        ...status.health_summary,
        green,
        gray,
        strict_percentage,
        weighted_percentage: isNaN(weighted_percentage) ? 100 : weighted_percentage
      }
    });
  };

  const handleIngestionSubmit = async (text: string, options: { owner: string; sponsor: string; input_type: string }) => {
    setIsLoading(true);
    try {
      const res = await api.submitObjective(text, options, token, tenantId);
      if (res && res.objective) {
        const newObj: Objective = res.objective;
        setObjectives(prev => {
          const index = prev.findIndex(o => o.id === newObj.id);
          if (index >= 0) {
            const copy = [...prev];
            copy[index] = newObj;
            return copy;
          }
          return [...prev, newObj];
        });
        setSelectedObjectiveId(newObj.id);
        setActiveView('planning');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectPlan = async (planId: string, budgetCeiling: number) => {
    setIsLoading(true);
    try {
      await api.executeObjectiveAction(selectedObjectiveId, 'select_plan', { plan_id: planId, budget_ceiling: budgetCeiling }, token, tenantId);
      
      // Update local state
      setObjectives(prev => prev.map(obj => {
        if (obj.id === selectedObjectiveId) {
          const updatedPlans = obj.plans.map(p => ({
            ...p,
            selected: p.id === planId
          }));
          return {
            ...obj,
            plans: updatedPlans,
            status: 'active' as const
          };
        }
        return obj;
      }));
      
      setActiveView('roadmap');
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApproveWaiver = async (waiverId: string, signatureToken: string) => {
    setIsLoading(true);
    try {
      await api.executeObjectiveAction(selectedObjectiveId, 'approve_waiver', { waiver_id: waiverId, token: signatureToken }, token, tenantId);
      
      // Update waiver state
      setWaivers(prev => prev.map(w => {
        if (w.id === waiverId) {
          return { ...w, status: 'approved' as const };
        }
        return w;
      }));

      // If EXC-001 is approved, we resolve the blocker on OBJ-101 and clear red/yellow flags in status!
      if (waiverId === 'EXC-001') {
        setObjectives(prev => prev.map(obj => {
          if (obj.id === 'OBJ-101') {
            const updatedMilestones = obj.milestones.map(m => {
              if (m.id === 'M-101') {
                const updatedTasks = m.tasks.map(t => {
                  if (t.id === 'T-101B') {
                    return { ...t, done: true, evidence: 'sys_config_validated.json', blocked: false, blockerMsg: undefined };
                  }
                  return t;
                });
                return { ...m, tasks: updatedTasks };
              }
              return m;
            });
            return { ...obj, milestones: updatedMilestones };
          }
          return obj;
        }));

        // Adjust system status to GREEN
        setStatus(prev => {
          if (!prev) return null;
          const updatedDomains = { ...prev.domains };
          if (updatedDomains.Services) {
            updatedDomains.Services = {
              ...updatedDomains.Services,
              "Objective Engine": "GREEN"
            };
          }
          return {
            ...prev,
            domains: updatedDomains,
            health_summary: {
              ...prev.health_summary,
              strict_percentage: 100,
              weighted_percentage: 100
            }
          };
        });
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRejectWaiver = async (waiverId: string) => {
    setWaivers(prev => prev.map(w => {
      if (w.id === waiverId) {
        return { ...w, status: 'rejected' as const };
      }
      return w;
    }));
  };

  const handleUpdateToken = (e: React.FormEvent) => {
    e.preventDefault();
    if (tokenInput.trim()) {
      setToken(tokenInput.trim());
      setIsAuthValid(true);
      setTokenExpiresMin(60);
      setTokenInput('');
      setAuthDialogOpen(false);
    }
  };

  // Nav configuration
  const navItems = [
    { id: 'dashboard', label: 'Command Center', icon: LayoutDashboard, category: 'Operations' },
    { id: 'ingestion', label: 'Ingestion Studio', icon: FileInput, category: 'Planning' },
    { id: 'planning', label: 'Planning & Simulation', icon: Compass, category: 'Planning' },
    { id: 'roadmap', label: 'Roadmap & Timeline', icon: Milestone, iconRight: null, category: 'Planning' },
    { id: 'delivery', label: 'Delivery Traceability', icon: FileCheck2, category: 'Execution' },
    { id: 'exceptions', label: 'Waiver Exception Queue', icon: ShieldAlert, count: waivers.filter(w => w.status === 'pending').length, category: 'Execution' },
    { id: 'architecture', label: 'System Topology', icon: Network, category: 'Operations' },
    { id: 'knowledge', label: 'Knowledge Explorer', icon: BookOpen, category: 'Operations' },
  ];

  return (
    <div className="flex min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50 transition-colors duration-200">
      
      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-zinc-200/60 dark:border-zinc-800/80 bg-zinc-100/50 dark:bg-zinc-900/60 backdrop-blur-md flex flex-col justify-between shrink-0">
        <div className="flex flex-col gap-6 p-4">
          
          {/* Logo & Header */}
          <div className="flex items-center gap-2 px-2 py-1.5 border-b border-zinc-200 dark:border-zinc-800">
            <Layers className="w-5 h-5 text-indigo-500" />
            <span className="font-extrabold text-sm tracking-wider bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">UAWOS PLATFORM</span>
          </div>

          {/* Workspace Switcher */}
          <div className="flex flex-col gap-1.5">
            <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider px-2">Tenant Workspace</span>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="w-full justify-between h-8 text-[11px] font-semibold border-zinc-200/60 dark:border-zinc-800 bg-card/60">
                  <span className="flex items-center gap-1.5">
                    <Globe className="w-3.5 h-3.5 text-zinc-400" />
                    {tenantId === 'tenant-primary' ? 'Primary Cluster' : tenantId === 'tenant-compliance' ? 'Compliance Vault' : 'Global Operations'}
                  </span>
                  <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 text-xs">
                <DropdownMenuLabel>Switch Workspace</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setTenantId('tenant-primary')}>Primary Cluster</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTenantId('tenant-compliance')}>Compliance Vault</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTenantId('tenant-global')}>Global Operations</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Navigation Items grouped by category */}
          <div className="flex flex-col gap-4 mt-2">
            {['Operations', 'Planning', 'Execution'].map((cat) => {
              const items = navItems.filter(item => item.category === cat);
              return (
                <div key={cat} className="flex flex-col gap-1">
                  <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider px-2 mb-1">{cat}</span>
                  {items.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeView === item.id;
                    return (
                      <Button
                        key={item.id}
                        variant={isActive ? 'secondary' : 'ghost'}
                        size="sm"
                        onClick={() => setActiveView(item.id as ViewType)}
                        className={`w-full justify-between h-8 text-[11px] font-medium px-2.5 transition-all duration-150 ${
                          isActive 
                            ? 'bg-zinc-200/60 dark:bg-zinc-800 text-zinc-950 dark:text-zinc-100 font-bold' 
                            : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-200/30 dark:hover:bg-zinc-800/40'
                        }`}
                      >
                        <span className="flex items-center gap-2">
                          <Icon className={`w-4 h-4 ${isActive ? 'text-primary' : 'text-zinc-400'}`} />
                          <span>{item.label}</span>
                        </span>
                        {item.count !== undefined && item.count > 0 && (
                          <Badge variant="destructive" className="h-4 min-w-4 px-1 rounded-full flex items-center justify-center text-[9px] leading-none">
                            {item.count}
                          </Badge>
                        )}
                      </Button>
                    );
                  })}
                </div>
              );
            })}
          </div>

        </div>

        {/* Sidebar Footer - Active Role and Controls */}
        <div className="p-4 border-t border-zinc-200/60 dark:border-zinc-800/80 bg-zinc-150/40 dark:bg-zinc-950/20 flex flex-col gap-3">
          
          {/* Active Role Selector */}
          <div className="flex flex-col gap-1.5">
            <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider px-2">Assigned Role Scope</span>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="w-full justify-between h-8 text-[11px] font-semibold border-zinc-200/60 dark:border-zinc-800 bg-card/60">
                  <span className="flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-indigo-500" />
                    {activeRole}
                  </span>
                  <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 text-xs">
                <DropdownMenuLabel>Select Active Role</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setActiveRole('Developer')}>Developer</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setActiveRole('Compliance Analyst')}>Compliance Analyst</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setActiveRole('Admin')}>Admin</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setActiveRole('Strategic Administrator')}>Strategic Administrator</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <div className="flex justify-between items-center px-1">
            <span className="text-[10px] text-muted-foreground font-mono">v1.0.8-stable</span>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-muted-foreground hover:text-zinc-950 dark:hover:text-zinc-100"
              onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
              title="Toggle theme mode"
            >
              {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            </Button>
          </div>

        </div>
      </aside>

      {/* Main Workspace Frame */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* Main Header / Top bar */}
        <header className="h-14 border-b border-zinc-200/60 dark:border-zinc-800/80 bg-zinc-50/80 dark:bg-zinc-950/80 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-10 sticky top-0">
          <div className="flex items-center gap-2 text-xs">
            <span className="text-muted-foreground">Workspaces</span>
            <span className="text-zinc-400">/</span>
            <span className="font-semibold text-zinc-700 dark:text-zinc-300">
              {tenantId === 'tenant-primary' ? 'Primary Cluster' : tenantId === 'tenant-compliance' ? 'Compliance Vault' : 'Global Operations'}
            </span>
            <span className="text-zinc-400">/</span>
            <span className="font-bold text-primary capitalize">{activeView}</span>
          </div>

          {/* Top-bar Utilities */}
          <div className="flex items-center gap-3">
            
            {/* Objective quick selector for relevant views */}
            {['planning', 'roadmap'].includes(activeView) && objectives.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Active Objective:</span>
                <Select value={selectedObjectiveId} onValueChange={setSelectedObjectiveId}>
                  <SelectTrigger className="w-[180px] h-7 text-[10px] font-semibold border-zinc-200 dark:border-zinc-800">
                    <SelectValue placeholder="Select Objective" />
                  </SelectTrigger>
                  <SelectContent className="text-[10px]">
                    {objectives.map(o => (
                      <SelectItem key={o.id} value={o.id} className="text-[10px]">{o.id} - {o.title}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {/* Token credentials health banner */}
            <Button
              variant={isAuthValid ? 'outline' : 'destructive'}
              size="sm"
              onClick={() => setAuthDialogOpen(true)}
              className={`h-7 px-2.5 text-[10px] font-bold ${
                isAuthValid 
                  ? 'border-indigo-500/20 text-indigo-600 dark:text-indigo-400 bg-indigo-500/5 hover:bg-indigo-500/10'
                  : 'animate-pulse'
              }`}
            >
              <Key className="w-3.5 h-3.5 mr-1" />
              {isAuthValid ? `Token expires in ${tokenExpiresMin}m` : 'Credentials Expired'}
            </Button>

            {/* Polling/Sync button */}
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-muted-foreground hover:text-zinc-950 dark:hover:text-zinc-100"
              onClick={handleRefresh}
              disabled={isLoading || isPolling}
              title="Synchronize operations"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isPolling ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </header>

        {/* Content Wrapper */}
        <main className="flex-1 overflow-y-auto p-6 bg-zinc-50/50 dark:bg-zinc-950/40">
          
          {isLoading ? (
            <div className="flex flex-col items-center justify-center min-h-[300px] gap-3">
              <RefreshCw className="w-8 h-8 animate-spin text-indigo-500" />
              <p className="text-xs text-muted-foreground uppercase font-bold tracking-wider">Syncing operational models...</p>
            </div>
          ) : (
            <div className="max-w-6xl mx-auto h-full">
              
              {/* Conditional view rendering */}
              {activeView === 'dashboard' && (
                <DashboardView 
                  status={status} 
                  onRefresh={handleRefresh} 
                  onKillAgent={handleKillAgent} 
                />
              )}

              {activeView === 'ingestion' && (
                <IngestionView 
                  onSubmit={handleIngestionSubmit} 
                  isLoading={isLoading} 
                />
              )}

              {activeView === 'planning' && selectedObjective && (
                <PlanningView 
                  objective={selectedObjective} 
                  onSelectPlan={handleSelectPlan} 
                  onBack={() => setActiveView('ingestion')} 
                />
              )}

              {activeView === 'roadmap' && selectedObjective && (
                <RoadmapView 
                  objective={selectedObjective} 
                  onRefresh={handleRefresh} 
                />
              )}

              {activeView === 'delivery' && (
                <DeliveryView 
                  matrix={traceability} 
                  health={traceHealth} 
                  onRefresh={handleRefresh} 
                />
              )}

              {activeView === 'exceptions' && (
                <GovernanceView 
                  waivers={waivers} 
                  activeRole={activeRole} 
                  onApproveWaiver={handleApproveWaiver} 
                  onRejectWaiver={handleRejectWaiver} 
                />
              )}

              {activeView === 'architecture' && (
                <TopologyView />
              )}

              {activeView === 'knowledge' && (
                <KnowledgeView />
              )}

            </div>
          )}
        </main>

      </div>

      {/* Token Authenticator Dialog panel */}
      <Dialog open={authDialogOpen} onOpenChange={setAuthDialogOpen}>
        <DialogContent className="sm:max-w-[400px]">
          <form onSubmit={handleUpdateToken}>
            <DialogHeader>
              <DialogTitle className="text-sm font-bold flex items-center gap-1.5 uppercase tracking-wide">
                <Lock className="w-4 h-4 text-indigo-500" /> Token Authenticator Panel
              </DialogTitle>
              <DialogDescription className="text-xs">
                Update or inspect active authorization scopes and credentials.
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="flex flex-col gap-2">
                <Label htmlFor="current-token" className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Active Credentials Token</Label>
                <div className="p-2 border border-zinc-200 dark:border-zinc-800 rounded bg-zinc-50 dark:bg-zinc-950 text-xs font-mono select-all truncate">
                  {token}
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="token-input" className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Update Token String</Label>
                <Input
                  id="token-input"
                  placeholder="Enter new OAuth/JWT scope token..."
                  value={tokenInput}
                  onChange={(e) => setTokenInput(e.target.value)}
                  className="h-8 text-xs border-zinc-200 dark:border-zinc-800"
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="ghost" size="sm" className="h-8 text-xs" onClick={() => setAuthDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" size="sm" className="h-8 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white" disabled={!tokenInput.trim()}>
                Update Scopes
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

    </div>
  );
}

export default App;
