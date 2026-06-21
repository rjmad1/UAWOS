// src/components/PlanningView.tsx
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { type Objective } from '@/services/api';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Sparkles, BarChart3, AlertTriangle, Calendar, DollarSign, CheckCircle2, RotateCcw, ChevronRight } from 'lucide-react';

interface PlanningViewProps {
  objective: Objective;
  onSelectPlan: (planId: string, budgetCeiling: number) => void;
  onBack: () => void;
}

interface ScatterDot {
  x: number; // cost
  y: number; // duration
  type: 'recommended' | 'alternative';
}

export const PlanningView: React.FC<PlanningViewProps> = ({ objective, onSelectPlan, onBack }) => {
  const [budgetCeiling, setBudgetCeiling] = useState<number>(() => {
    // Default budget ceiling slightly higher than the recommended plan's cost
    const recommended = objective.plans.find(p => p.recommended);
    return recommended ? Math.ceil(recommended.cost * 1.25) : 30000;
  });

  const [selectedPlanId, setSelectedPlanId] = useState<string>(() => {
    const recommended = objective.plans.find(p => p.recommended);
    return recommended ? recommended.id : objective.plans[0]?.id || '';
  });

  const [isSimulating, setIsSimulating] = useState(false);
  const [simulatedDots, setSimulatedDots] = useState<ScatterDot[]>([]);

  const recommendedPlan = objective.plans.find(p => p.id === selectedPlanId) || objective.plans[0];

  // Run initial simulation once component mounts
  useEffect(() => {
    runSimulation();
  }, [objective]);

  const runSimulation = () => {
    setIsSimulating(true);
    setSimulatedDots([]);
    
    // Animate population of Monte Carlo points
    setTimeout(() => {
      const dots: ScatterDot[] = [];
      const primary = objective.plans.find(p => p.recommended);
      const secondary = objective.plans.find(p => !p.recommended);
      
      for (let i = 0; i < 60; i++) {
        if (primary) {
          // recommended plan cost duration deviations
          const x = primary.cost + (Math.random() - 0.5) * (primary.cost * 0.15);
          const y = primary.duration + (Math.random() - 0.5) * (primary.duration * 0.2);
          dots.push({ x, y, type: 'recommended' });
        }
        if (secondary) {
          // alternative plan deviations
          const x = secondary.cost + (Math.random() - 0.5) * (secondary.cost * 0.25);
          const y = secondary.duration + (Math.random() - 0.5) * (secondary.duration * 0.15);
          dots.push({ x, y, type: 'alternative' });
        }
      }
      setSimulatedDots(dots);
      setIsSimulating(false);
    }, 1200);
  };

  const handleConfirmSelection = () => {
    onSelectPlan(selectedPlanId, budgetCeiling);
  };

  const selectedPlan = objective.plans.find(p => p.id === selectedPlanId);
  const budgetBreach = selectedPlan ? selectedPlan.cost > budgetCeiling : false;

  // Compute boundaries for the scatter plot
  const maxCost = Math.max(...objective.plans.map(p => p.cost)) * 1.5;
  const maxDuration = Math.max(...objective.plans.map(p => p.duration)) * 1.5;

  return (
    <div className="flex flex-col gap-6">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-zinc-200/60 dark:border-zinc-800/80">
        <div className="flex flex-col">
          <span className="text-[10px] text-primary uppercase font-bold tracking-wider">Objectives Intake Planning Studio</span>
          <h2 className="text-xl font-bold tracking-tight mt-0.5">{objective.title}</h2>
          <p className="text-xs text-muted-foreground mt-0.5 truncate max-w-xl">{objective.description}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="h-8 text-xs" onClick={onBack}>
            <RotateCcw className="w-3.5 h-3.5 mr-1" /> Re-parse Ingest
          </Button>
          <Button size="sm" className="h-8 text-xs font-semibold" disabled={budgetBreach} onClick={handleConfirmSelection}>
            Confirm & Dispatch Plan <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
          </Button>
        </div>
      </div>

      {/* Plan Comparative Cards */}
      <div className="grid gap-6 md:grid-cols-2">
        {objective.plans.map((plan) => {
          const isSelected = selectedPlanId === plan.id;
          const planCostBreaches = plan.cost > budgetCeiling;
          
          return (
            <Card 
              key={plan.id}
              onClick={() => setSelectedPlanId(plan.id)}
              className={`shadow-sm cursor-pointer transition-all duration-200 bg-card/40 backdrop-blur-md relative border-2 ${
                isSelected 
                  ? 'border-primary ring-2 ring-primary/10' 
                  : 'border-zinc-200/60 dark:border-zinc-800/80 hover:border-zinc-300 dark:hover:border-zinc-700'
              }`}
            >
              {plan.recommended && (
                <Badge className="absolute top-3 right-3 text-[9px] bg-primary leading-none px-2 py-0.5">
                  Recommended
                </Badge>
              )}
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-bold">{plan.name}</CardTitle>
                <CardDescription className="text-[10px] mt-0.5">Forecast Path ID: {plan.id}</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-3 gap-4 border-y border-zinc-100 dark:border-zinc-800/80 py-4 my-2 text-center bg-zinc-50/20 dark:bg-zinc-950/20">
                <div className="flex flex-col gap-0.5">
                  <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider">Est. Duration</span>
                  <div className="text-sm font-bold flex items-center justify-center gap-1 mt-0.5">
                    <Calendar className="w-3.5 h-3.5 text-zinc-400" />
                    <span>{plan.duration} days</span>
                  </div>
                </div>
                <div className="flex flex-col gap-0.5">
                  <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider">Forecast Spend</span>
                  <div className={`text-sm font-bold flex items-center justify-center gap-0.5 mt-0.5 ${planCostBreaches ? 'text-amber-500' : ''}`}>
                    <DollarSign className="w-3.5 h-3.5 text-zinc-400" />
                    <span>{plan.cost.toLocaleString()}</span>
                  </div>
                </div>
                <div className="flex flex-col gap-0.5">
                  <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider">Success Rate</span>
                  <div className="text-sm font-bold text-emerald-500 mt-0.5">{plan.probability}%</div>
                </div>
              </CardContent>
              <CardFooter className="pt-3 pb-3 flex justify-between items-center text-[10px] text-muted-foreground">
                <div className="flex items-center gap-1.5">
                  <Badge variant={plan.risk === 'Low' ? 'outline' : plan.risk === 'Medium' ? 'default' : 'destructive'} className="text-[9px] px-1.5 py-0">
                    {plan.risk} Risk
                  </Badge>
                </div>
                {planCostBreaches && (
                  <div className="flex items-center gap-1 text-amber-500 font-semibold animate-pulse">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Exceeds Budget Ceiling</span>
                  </div>
                )}
              </CardFooter>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Budget Allocation Panel */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md flex-1">
            <CardHeader className="pb-3">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <DollarSign className="w-4 h-4 text-primary" /> Budget Ceiling Allocation
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-5">
              <div className="flex flex-col gap-1.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-muted-foreground">Max Allowed Allocation:</span>
                  <span className="font-bold text-sm">${budgetCeiling.toLocaleString()}</span>
                </div>
                <Slider 
                  min={5000} 
                  max={100000} 
                  step={1000} 
                  value={[budgetCeiling]} 
                  onValueChange={(val) => setBudgetCeiling(val[0])} 
                  className="py-3"
                />
              </div>

              {budgetBreach ? (
                <Alert variant="destructive" className="border-red-500/25 bg-red-500/5 text-red-600 dark:text-red-400">
                  <AlertTriangle className="w-4 h-4" />
                  <AlertTitle className="text-xs font-bold leading-none tracking-tight">Ceiling Violation</AlertTitle>
                  <AlertDescription className="text-[10px] mt-1">
                    The chosen path cost (${recommendedPlan?.cost.toLocaleString()}) exceeds the allocation limit. Raise the ceiling or select a lower-cost path.
                  </AlertDescription>
                </Alert>
              ) : (
                <Alert className="border-emerald-500/20 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <AlertTitle className="text-xs font-bold leading-none tracking-tight">Allocation Secure</AlertTitle>
                  <AlertDescription className="text-[10px] mt-1">
                    Path cost fits within the allocated ceiling of ${budgetCeiling.toLocaleString()}.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Monte Carlo Simulation Scatter Plot */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md">
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <BarChart3 className="w-4 h-4 text-violet-500" /> Monte Carlo Path Forecasts
                </CardTitle>
              </div>
              <Button size="sm" variant="outline" className="h-7 text-[10px]" disabled={isSimulating} onClick={runSimulation}>
                Run 100 Simulations
              </Button>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center">
              {isSimulating ? (
                <div className="w-full h-[240px] flex flex-col items-center justify-center gap-3">
                  <Sparkles className="w-6 h-6 animate-spin text-violet-500" />
                  <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Evaluating cost-schedule paths...</span>
                </div>
              ) : (
                <div className="w-full relative h-[240px] border border-zinc-200/60 dark:border-zinc-800 rounded-lg p-2 bg-zinc-50/10 dark:bg-zinc-950/10 overflow-hidden">
                  {/* Simple custom SVG scatter plot */}
                  <svg className="w-full h-full" viewBox="0 0 500 200">
                    {/* Grid lines */}
                    <line x1="50" y1="20" x2="50" y2="170" stroke="rgba(148,163,184,0.15)" strokeWidth="1" />
                    <line x1="50" y1="170" x2="480" y2="170" stroke="rgba(148,163,184,0.15)" strokeWidth="1" />
                    
                    {/* Axis Labels */}
                    <text x="20" y="95" fill="rgba(148,163,184,0.5)" fontSize="9" textAnchor="middle" transform="rotate(-90 20 95)">Duration (days)</text>
                    <text x="265" y="190" fill="rgba(148,163,184,0.5)" fontSize="9" textAnchor="middle">Forecast Cost ($)</text>
                    
                    {/* Simulated points */}
                    {simulatedDots.map((dot, idx) => {
                      // Normalize x and y coordinates to SVG bounds
                      const svgX = 50 + (dot.x / maxCost) * 400;
                      const svgY = 170 - (dot.y / maxDuration) * 140;
                      const color = dot.type === 'recommended' ? 'fill-primary' : 'fill-violet-400';
                      
                      return (
                        <circle key={idx} cx={svgX} cy={svgY} r="3" className={`${color} opacity-60`} />
                      );
                    })}

                    {/* Legend */}
                    <circle cx="400" cy="30" r="3" className="fill-primary" />
                    <text x="410" y="33" fill="currentColor" fontSize="8" className="text-zinc-600 dark:text-zinc-400">Path A</text>
                    
                    <circle cx="400" cy="45" r="3" className="fill-violet-400" />
                    <text x="410" y="48" fill="currentColor" fontSize="8" className="text-zinc-600 dark:text-zinc-400">Path B</text>
                  </svg>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
