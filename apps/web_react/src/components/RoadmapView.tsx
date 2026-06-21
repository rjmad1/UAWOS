// src/components/RoadmapView.tsx
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Milestone, Objective } from '@/services/api';
import { Calendar, AlertTriangle, CheckCircle, HelpCircle, Layers, Sliders } from 'lucide-react';

interface RoadmapViewProps {
  objective: Objective;
  onRefresh: () => void;
}

interface TimelineMilestone {
  id: string;
  name: string;
  start: number; // offset in % (0 - 100)
  duration: number; // duration in % (10 - 50)
  dependencies: string[];
}

export const RoadmapView: React.FC<RoadmapViewProps> = ({ objective }) => {
  const [milestones, setMilestones] = useState<TimelineMilestone[]>([
    { id: "M1", name: "Intake & Discovery (M1)", start: 10, duration: 25, dependencies: [] },
    { id: "M2", name: "Schema Translation (M2)", start: 40, duration: 20, dependencies: ["M1"] },
    { id: "M3", name: "Simulations Model (M3)", start: 65, duration: 15, dependencies: ["M2"] },
    { id: "M4", name: "Waiver Orchestration (M4)", start: 82, duration: 15, dependencies: ["M3"] }
  ]);

  const [hasCircularConstraint, setHasCircularConstraint] = useState(false);
  const [cycleConflict, setCycleConflict] = useState<string | null>(null);

  useEffect(() => {
    runCycleDetection();
  }, [milestones, hasCircularConstraint]);

  const runCycleDetection = () => {
    // Build adjacency list
    const adjList: Record<string, string[]> = {};
    milestones.forEach(m => {
      adjList[m.id] = [...m.dependencies];
    });

    if (hasCircularConstraint) {
      // Simulate introducing a cycle: M1 depends on M4
      adjList["M1"].push("M4");
    }

    // DFS Cycle Detection Algorithm
    const visited: Record<string, 'unvisited' | 'visiting' | 'visited'> = {};
    milestones.forEach(m => {
      visited[m.id] = 'unvisited';
    });

    let detectedCycle = false;
    let cyclePath: string[] = [];

    const dfs = (nodeId: string, path: string[]): boolean => {
      visited[nodeId] = 'visiting';
      const neighbors = adjList[nodeId] || [];
      
      for (const neighbor of neighbors) {
        if (visited[neighbor] === 'visiting') {
          // Cycle found!
          const cycleStartIdx = path.indexOf(neighbor);
          cyclePath = [...path.slice(cycleStartIdx), nodeId, neighbor];
          detectedCycle = true;
          return true;
        }
        if (visited[neighbor] === 'unvisited') {
          if (dfs(neighbor, [...path, nodeId])) {
            return true;
          }
        }
      }
      visited[nodeId] = 'visited';
      return false;
    };

    for (const m of milestones) {
      if (visited[m.id] === 'unvisited') {
        if (dfs(m.id, [])) {
          break;
        }
      }
    }

    if (detectedCycle) {
      setCycleConflict(`Dependency loop detected: ${cyclePath.join(" → ")}`);
    } else {
      setCycleConflict(null);
    }
  };

  const handleSliderChange = (id: string, field: 'start' | 'duration', value: number) => {
    setMilestones(prev => 
      prev.map(m => m.id === id ? { ...m, [field]: value } : m)
    );
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header telemetry */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-zinc-200/60 dark:border-zinc-800/80">
        <div className="flex flex-col">
          <span className="text-[10px] text-primary uppercase font-bold tracking-wider">Operational roadmap engine</span>
          <h2 className="text-xl font-bold tracking-tight mt-0.5">Timeline & Gantt Tracks</h2>
          <p className="text-xs text-muted-foreground mt-0.5">Milestones sequence offsets and dependency cycle detection</p>
        </div>
      </div>

      {cycleConflict ? (
        <Alert variant="destructive" className="border-red-500/25 bg-red-500/5 text-red-600 dark:text-red-400 animate-pulse">
          <AlertTriangle className="w-4 h-4" />
          <AlertTitle className="text-xs font-bold leading-none tracking-tight">System Loop Conflict</AlertTitle>
          <AlertDescription className="text-[10px] mt-1">
            {cycleConflict}. Execution paused automatically. Drag offsets or disable cyclic triggers to clear.
          </AlertDescription>
        </Alert>
      ) : (
        <Alert className="border-emerald-500/20 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400">
          <CheckCircle className="w-4 h-4 text-emerald-500" />
          <AlertTitle className="text-xs font-bold leading-none tracking-tight">Timeline Consistent</AlertTitle>
          <AlertDescription className="text-[10px] mt-1">
            Zero circular dependencies detected across 4 active milestones tracks.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Gantt Lane display */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold tracking-tight">Roadmap Track Canvas</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="border border-zinc-200/60 dark:border-zinc-800/80 rounded-lg overflow-hidden bg-zinc-50/10 dark:bg-zinc-950/10 relative p-4">
                {/* Timeline axis header */}
                <div className="flex justify-between text-[8px] text-muted-foreground uppercase tracking-widest font-bold pb-2 border-b border-zinc-200/60 dark:border-zinc-800/80 mb-2">
                  <span>Day 0</span>
                  <span>Day 30</span>
                  <span>Day 60</span>
                  <span>Day 90</span>
                  <span>Day 120</span>
                </div>

                <div className="flex flex-col gap-3 min-h-[180px] relative">
                  {milestones.map((m) => {
                    const isM1CycleNode = hasCircularConstraint && (m.id === "M1" || m.id === "M4");
                    const barColor = cycleConflict && (isM1CycleNode || m.dependencies.length > 0 && cycleConflict.includes(m.id))
                      ? 'bg-red-500 dark:bg-red-600 shadow-[0_0_8px_rgba(239,68,68,0.3)]' 
                      : 'bg-indigo-500 dark:bg-indigo-600 shadow-[0_0_8px_rgba(99,102,241,0.2)]';
                    
                    return (
                      <div key={m.id} className="flex items-center h-10 border-b border-zinc-100/50 dark:border-zinc-800/30 relative">
                        <div className="w-[140px] text-[10px] font-semibold text-zinc-700 dark:text-zinc-300 truncate flex-shrink-0">
                          {m.name}
                        </div>
                        <div className="flex-grow h-full relative">
                          <div 
                            className={`absolute h-5 rounded-full ${barColor} text-[9px] font-bold text-white flex items-center justify-center transition-all duration-300`}
                            style={{ 
                              left: `${m.start}%`, 
                              width: `${m.duration}%`,
                              top: '25%'
                            }}
                          >
                            <span>{m.id}</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Offset controls and cycle trigger */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md">
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <Sliders className="w-4 h-4 text-primary" /> Offset Adjustment Controls
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="flex flex-col gap-5">
              <div className="flex items-center justify-between p-3 rounded-lg border border-zinc-200/60 dark:border-zinc-800 bg-zinc-50/20 dark:bg-zinc-950/20">
                <div className="flex flex-col gap-0.5">
                  <Label htmlFor="circular-conflict" className="text-[11px] font-bold">Inject Circular Constraint</Label>
                  <span className="text-[9px] text-muted-foreground">M1 depends on M4 (cycles)</span>
                </div>
                <Switch 
                  id="circular-conflict"
                  checked={hasCircularConstraint} 
                  onCheckedChange={setHasCircularConstraint}
                />
              </div>

              {milestones.map((m) => (
                <div key={m.id} className="flex flex-col gap-2 p-3 rounded-lg border border-zinc-200/60 dark:border-zinc-800">
                  <div className="flex justify-between items-center text-[10px] font-bold text-zinc-700 dark:text-zinc-300">
                    <span>{m.name}</span>
                    <span>Start: Day {Math.floor(m.start * 1.2)}</span>
                  </div>
                  <Slider 
                    min={0} 
                    max={80} 
                    step={1} 
                    value={[m.start]} 
                    onValueChange={(val) => handleSliderChange(m.id, 'start', val[0])}
                    className="py-1"
                  />
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
