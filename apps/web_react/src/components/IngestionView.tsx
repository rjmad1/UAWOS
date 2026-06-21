// src/components/IngestionView.tsx
import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Eye, ShieldAlert, Sparkles, CheckCircle, ListTodo, FileText, ArrowRight } from 'lucide-react';

interface IngestionViewProps {
  onSubmit: (text: string, options: { owner: string; sponsor: string; input_type: string }) => void;
  isLoading: boolean;
}

export const IngestionView: React.FC<IngestionViewProps> = ({ onSubmit, isLoading }) => {
  const [text, setText] = useState('');
  const [owner, setOwner] = useState('System Operations Group');
  const [sponsor, setSponsor] = useState('Strategic Sponsor');
  const [inputType, setInputType] = useState('text');
  
  // Local state for PII and critique simulations
  const [isPIIMasked, setIsPIIMasked] = useState(false);
  const [maskedText, setMaskedText] = useState('');
  const [piiFound, setPiiFound] = useState<string[]>([]);
  const [readinessScore, setReadinessScore] = useState<number | null>(null);

  const handleMaskPII = () => {
    if (!text.trim()) return;
    
    // Simulate PII identification
    const found: string[] = [];
    let processed = text;
    
    // Pattern mock checks
    if (text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/)) {
      found.push("Email Address");
      processed = processed.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, "[MASKED_EMAIL]");
    }
    if (text.match(/\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/)) {
      found.push("Credit Card/Identifier Number");
      processed = processed.replace(/\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/g, "[MASKED_ID]");
    }
    if (text.match(/\b\d{3}-\d{2}-\d{4}\b/)) {
      found.push("Personal SSN/Tax ID");
      processed = processed.replace(/\b\d{3}-\d{2}-\d{4}\b/g, "[MASKED_TAX_ID]");
    }
    if (text.toLowerCase().includes("secret") || text.toLowerCase().includes("api_key")) {
      found.push("System Credentials/Secrets");
      processed = processed.replace(/(api_key|secret|password)\s*[:=]\s*[a-zA-Z0-9_]+/gi, "$1: [MASKED_SECRET]");
    }

    if (found.length === 0) {
      found.push("No explicit identifiers found. System checks complete.");
      setMaskedText(text);
    } else {
      setMaskedText(processed);
    }
    
    setPiiFound(found);
    setIsPIIMasked(true);
    
    // Compute mockup critique score based on content length
    const score = Math.min(45 + Math.floor(processed.length / 15), 98);
    setReadinessScore(score);
  };

  const handleClear = () => {
    setText('');
    setIsPIIMasked(false);
    setMaskedText('');
    setPiiFound([]);
    setReadinessScore(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSubmit(isPIIMasked ? maskedText : text, { owner, sponsor, input_type: inputType });
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Input Panel */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md flex-1">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold tracking-tight">Specification Text Intake</CardTitle>
              <CardDescription className="text-[11px] mt-0.5">Paste unstructured system operational intents or notes</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <Textarea
                placeholder="Example: Define cluster node configurations. Ensure failover latency remains under 40 milliseconds and latency logs copy back to verification database. Access requires active operator scopes."
                className="min-h-[220px] text-xs font-normal border-zinc-200/60 dark:border-zinc-800/80 focus-visible:ring-primary/20"
                value={text}
                onChange={(e) => {
                  setText(e.target.value);
                  if (isPIIMasked) setIsPIIMasked(false);
                }}
              />
              
              <div className="flex flex-wrap gap-2.5 justify-between items-center">
                <div className="flex items-center gap-2">
                  <Select value={inputType} onValueChange={setInputType}>
                    <SelectTrigger className="w-[130px] h-8 text-[11px] border-zinc-200/60 dark:border-zinc-800/80">
                      <SelectValue placeholder="Input Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="text" className="text-[11px]">Plain Text</SelectItem>
                      <SelectItem value="document" className="text-[11px]">PRD Document</SelectItem>
                      <SelectItem value="transcript" className="text-[11px]">Meeting Transcript</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex gap-2">
                  {text && (
                    <Button type="button" variant="ghost" size="sm" className="h-8 text-xs text-muted-foreground hover:text-zinc-950 dark:hover:text-zinc-100" onClick={handleClear}>
                      Clear
                    </Button>
                  )}
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    className="h-8 text-xs font-semibold"
                    disabled={!text.trim() || isLoading}
                    onClick={handleMaskPII}
                  >
                    <ShieldAlert className="w-3.5 h-3.5 mr-1" /> Mask PII & Critique
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {isPIIMasked && (
            <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md animate-paneFadeIn">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <Eye className="w-3.5 h-3.5" /> Masked Telemetry Preview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="p-3 rounded-lg bg-zinc-50/50 dark:bg-zinc-950/50 border border-zinc-200/60 dark:border-zinc-800 text-[11px] font-mono text-zinc-600 dark:text-zinc-400 whitespace-pre-wrap max-h-[160px] overflow-y-auto">
                  {maskedText}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Critique and Options Panel */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md flex flex-col justify-between">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold tracking-tight">Intake Governance Details</CardTitle>
              <CardDescription className="text-[11px] mt-0.5">Configure ownership scope parameters</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <Label htmlFor="owner" className="text-[11px] text-muted-foreground uppercase font-bold tracking-wide">Workforce Owner Group</Label>
                <Input
                  id="owner"
                  value={owner}
                  onChange={(e) => setOwner(e.target.value)}
                  className="h-8 text-xs border-zinc-200/60 dark:border-zinc-800/80"
                />
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="sponsor" className="text-[11px] text-muted-foreground uppercase font-bold tracking-wide">Strategic Sponsor</Label>
                <Input
                  id="sponsor"
                  value={sponsor}
                  onChange={(e) => setSponsor(e.target.value)}
                  className="h-8 text-xs border-zinc-200/60 dark:border-zinc-800/80"
                />
              </div>

              {isPIIMasked && readinessScore !== null && (
                <div className="flex flex-col gap-3 mt-2 border-t border-zinc-200/60 dark:border-zinc-800/80 pt-4 animate-paneFadeIn">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-zinc-700 dark:text-zinc-300">Intake Readiness Score</span>
                    <span className={`font-bold ${readinessScore > 75 ? 'text-emerald-500' : 'text-amber-500'}`}>{readinessScore}%</span>
                  </div>
                  <Progress value={readinessScore} className="h-1.5" />
                  
                  <div className="flex flex-col gap-1.5 mt-1">
                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">PII Assessment logs:</span>
                    <div className="flex flex-col gap-1">
                      {piiFound.map((item, idx) => (
                        <div key={idx} className="flex items-center gap-1.5 text-[10px]">
                          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                          <span className="text-zinc-700 dark:text-zinc-300">{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
            
            <CardFooter className="pt-3 border-t border-zinc-200/60 dark:border-zinc-800/80 mt-4">
              <Button
                type="submit"
                className="w-full text-xs font-semibold h-8"
                disabled={!text.trim() || isLoading}
              >
                {isLoading ? (
                  <>
                    <Sparkles className="w-3.5 h-3.5 mr-1.5 animate-spin" /> Analyzing Intent...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5 mr-1.5" /> Compile & Generate Plan <ArrowRight className="w-3.5 h-3.5 ml-1" />
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </form>
  );
};
