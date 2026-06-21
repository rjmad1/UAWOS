// src/components/KnowledgeView.tsx
import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Search, Network, Info, Link2, BookOpen } from 'lucide-react';

interface KnowledgeNode {
  id: string;
  type: 'Claim' | 'Evidence' | 'Decision';
  label: string;
  confidence: number;
  source: string;
}

export const KnowledgeView: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<KnowledgeNode[]>([
    { id: "CLM-901", type: "Claim", label: "Cluster cache limits require daily baseline resets to prevent allocation lockouts.", confidence: 92, source: "Operations Postmortem" },
    { id: "EVI-902", type: "Evidence", label: "Memory allocation analysis report (latency_audit_report.json)", confidence: 100, source: "System Checkpoint Logs" },
    { id: "CLM-903", type: "Claim", label: "Secondary node transitions encounter connection timeouts if routing tables config is missing.", confidence: 84, source: "Operator Manual" }
  ]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    // Simulate query filtering
    setTimeout(() => {
      const filtered = [
        { id: "CLM-901", type: "Claim", label: `Re-calculated alignment: ${query} matches baseline operational guidelines.`, confidence: 88, source: "Intake Analysis" },
        { id: "EVI-904", type: "Evidence", label: "Historical trace validation records (db_schema_mapped.json)", confidence: 100, source: "Git History log" }
      ] as KnowledgeNode[];
      setResults(filtered);
      setIsSearching(false);
    }, 800);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-zinc-200/60 dark:border-zinc-800/80">
        <div className="flex flex-col">
          <span className="text-[10px] text-primary uppercase font-bold tracking-wider">Organizational memory index</span>
          <h2 className="text-xl font-bold tracking-tight mt-0.5">Knowledge Graph Explorer</h2>
          <p className="text-xs text-muted-foreground mt-0.5">Dense vector and semantic ontology searches across historical outcomes and evidence claims</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Search input and claims list */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold tracking-tight">Semantic Ontology Search</CardTitle>
              <form onSubmit={handleSearch} className="flex gap-2 mt-2">
                <Input
                  placeholder="Enter query (e.g. cluster caching constraints)..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="h-8 text-xs border-zinc-200/60 dark:border-zinc-800/80"
                />
                <Button type="submit" size="sm" className="h-8 text-xs font-semibold" disabled={isSearching}>
                  <Search className="w-3.5 h-3.5 mr-1" /> Search Graph
                </Button>
              </form>
            </CardHeader>
            <CardContent className="p-0">
              {isSearching ? (
                <div className="w-full h-[180px] flex flex-col items-center justify-center gap-3">
                  <BookOpen className="w-6 h-6 animate-pulse text-indigo-500" />
                  <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Querying vector index...</span>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow className="hover:bg-transparent">
                      <TableHead className="w-[100px] text-[10px] font-bold uppercase tracking-wider">Node ID</TableHead>
                      <TableHead className="text-[10px] font-bold uppercase tracking-wider">Claim / Evidence Label</TableHead>
                      <TableHead className="w-[100px] text-[10px] font-bold uppercase tracking-wider text-center">Confidence</TableHead>
                      <TableHead className="text-[10px] font-bold uppercase tracking-wider text-right">Source</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {results.map((node) => (
                      <TableRow key={node.id} className="hover:bg-zinc-50/30 dark:hover:bg-zinc-950/20">
                        <TableCell className="font-mono text-xs font-semibold text-primary flex items-center gap-1">
                          <Link2 className="w-3 h-3 text-zinc-400" />
                          <span>{node.id}</span>
                        </TableCell>
                        <TableCell className="text-xs">{node.label}</TableCell>
                        <TableCell className="text-center">
                          <Badge variant="outline" className={`text-[9px] px-1.5 py-0 ${node.confidence > 90 ? 'text-emerald-500 border-emerald-500/20' : 'text-amber-500 border-amber-500/20'}`}>
                            {node.confidence}%
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground text-right">{node.source}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Ontology structure representation */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md flex-1">
            <CardHeader className="pb-3">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <Network className="w-4 h-4 text-violet-500" /> Ontology Structure
              </CardTitle>
            </CardHeader>
            <CardContent className="flex items-center justify-center p-4">
              <div className="w-full aspect-square max-w-[240px] border border-zinc-200/60 dark:border-zinc-800 rounded-lg p-2 bg-zinc-50/10 dark:bg-zinc-950/10 flex items-center justify-center">
                {/* SVG Graph nodes mapping */}
                <svg className="w-full h-full" viewBox="0 0 200 200">
                  {/* Links */}
                  <line x1="100" y1="100" x2="50" y2="60" stroke="rgba(148,163,184,0.3)" strokeWidth="1" />
                  <line x1="100" y1="100" x2="150" y2="60" stroke="rgba(148,163,184,0.3)" strokeWidth="1" />
                  <line x1="100" y1="100" x2="100" y2="160" stroke="rgba(148,163,184,0.3)" strokeWidth="1" />
                  
                  {/* Nodes */}
                  <circle cx="100" cy="100" r="14" className="fill-primary stroke-2 stroke-background" />
                  <text x="100" y="103" fill="white" fontSize="8" fontWeight="bold" textAnchor="middle">U-State</text>

                  <circle cx="50" cy="60" r="10" className="fill-violet-400 stroke-2 stroke-background" />
                  <text x="50" y="63" fill="white" fontSize="7" fontWeight="bold" textAnchor="middle">CLM</text>

                  <circle cx="150" cy="60" r="10" className="fill-violet-400 stroke-2 stroke-background" />
                  <text x="150" y="63" fill="white" fontSize="7" fontWeight="bold" textAnchor="middle">EVI</text>

                  <circle cx="100" cy="160" r="10" className="fill-emerald-400 stroke-2 stroke-background" />
                  <text x="100" y="163" fill="white" fontSize="7" fontWeight="bold" textAnchor="middle">DEC</text>
                </svg>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
