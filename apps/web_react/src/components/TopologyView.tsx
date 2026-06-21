// src/components/TopologyView.tsx
import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Terminal, Network } from 'lucide-react';

interface TopologyNode {
  id: string;
  name: string;
  type: 'container' | 'service' | 'gateway';
  status: 'GREEN' | 'YELLOW' | 'RED';
  port: number;
  logs: string[];
}

export const TopologyView: React.FC = () => {
  const [selectedNodeId, setSelectedNodeId] = useState<string>("postgres");

  const nodes: Record<string, TopologyNode> = {
    postgres: {
      id: "postgres",
      name: "PostgreSQL Database",
      type: "container",
      status: "GREEN",
      port: 5435,
      logs: [
        "[2026-06-22 00:01:00] LOG: database system is ready to accept connections",
        "[2026-06-22 00:05:22] LOG: connection received: host=127.0.0.1 port=58102",
        "[2026-06-22 00:05:23] LOG: execute <unnamed>: SELECT * FROM objective_state WHERE id = $1",
        "[2026-06-22 00:10:45] LOG: checkpoint starting: time"
      ]
    },
    opa: {
      id: "opa",
      name: "Open Policy Agent (OPA)",
      type: "container",
      status: "GREEN",
      port: 8181,
      logs: [
        "[2026-06-22 00:01:10] {\"level\":\"info\",\"msg\":\"Starting policy evaluator engine\"}",
        "[2026-06-22 00:06:12] {\"level\":\"info\",\"msg\":\"Evaluated policy rule: deny_restricted_tool_executions\",\"decision\":false}",
        "[2026-06-22 00:08:44] {\"level\":\"warning\",\"msg\":\"Policy override exception waiver requested: EXC-001\"}",
        "[2026-06-22 00:08:50] {\"level\":\"info\",\"msg\":\"Override authorized, updating FGA permissions state\"}"
      ]
    },
    ollama: {
      id: "ollama",
      name: "Ollama Gateway",
      type: "gateway",
      status: "GREEN",
      port: 11434,
      logs: [
        "[2026-06-22 00:01:05] Starting local inference gateway on port 11434...",
        "[2026-06-22 00:02:14] POST /api/generate 200 OK (elapsed: 1400ms) model=tinyllama",
        "[2026-06-22 00:04:45] POST /api/embeddings 200 OK (elapsed: 320ms) tokens=120",
        "[2026-06-22 00:11:02] POST /api/generate 200 OK (elapsed: 2200ms) model=tinyllama"
      ]
    },
    marquez: {
      id: "marquez",
      name: "Marquez Lineage",
      type: "service",
      status: "GREEN",
      port: 5000,
      logs: [
        "[2026-06-22 00:01:15] OpenLineage listener active on port 5000",
        "[2026-06-22 00:03:22] POST /api/v1/lineage: received dataset schema update",
        "[2026-06-22 00:05:44] GET /api/v1/jobs/OBJ-101/lineage 200 OK",
        "[2026-06-22 00:09:12] POST /api/v1/lineage: mapped execution node output c0182fa"
      ]
    },
    marker: {
      id: "marker",
      name: "Marker Service Sandbox",
      type: "container",
      status: "GREEN",
      port: 8000,
      logs: [
        "[2026-06-22 00:01:20] Marker document parser listening on port 8000 (Isolated Network Sandbox)",
        "[2026-06-22 00:04:12] POST /parse_file: parsing uploaded document job_id=job_1082",
        "[2026-06-22 00:04:15] LOG: completed parsing job_id=job_1082 (size: 1.2MB, text length: 45000 chars)",
        "[2026-06-22 00:04:16] Cleaned cache output, isolated sandbox context refreshed"
      ]
    }
  };

  const selectedNode = nodes[selectedNodeId] || nodes.postgres;

  return (
    <div className="flex flex-col gap-6">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-zinc-200/60 dark:border-zinc-800/80">
        <div className="flex flex-col">
          <span className="text-[10px] text-primary uppercase font-bold tracking-wider">C4 Architecture monitor</span>
          <h2 className="text-xl font-bold tracking-tight mt-0.5">Component Topology Viewer</h2>
          <p className="text-xs text-muted-foreground mt-0.5">Interactive container networking structure and live system log streams</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* SVG Node topology canvas */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md flex-1 min-h-[350px]">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold tracking-tight flex items-center gap-1.5">
                <Network className="w-4 h-4 text-primary" /> Topology Diagram
              </CardTitle>
            </CardHeader>
            <CardContent className="flex items-center justify-center p-6">
              <div className="w-full max-w-[500px] aspect-video border border-zinc-200/60 dark:border-zinc-800/80 rounded-lg bg-zinc-50/10 dark:bg-zinc-950/10 relative p-4 flex items-center justify-center">
                <svg className="w-full h-full" viewBox="0 0 500 250">
                  {/* Connection links */}
                  <line x1="250" y1="50" x2="100" y2="120" stroke="currentColor" strokeWidth="1.5" className="text-zinc-200 dark:text-zinc-800" />
                  <line x1="250" y1="50" x2="250" y2="120" stroke="currentColor" strokeWidth="1.5" className="text-zinc-200 dark:text-zinc-800" />
                  <line x1="250" y1="50" x2="400" y2="120" stroke="currentColor" strokeWidth="1.5" className="text-zinc-200 dark:text-zinc-800" />
                  <line x1="100" y1="120" x2="175" y2="200" stroke="currentColor" strokeWidth="1.5" className="text-zinc-200 dark:text-zinc-800" />
                  <line x1="250" y1="120" x2="175" y2="200" stroke="currentColor" strokeWidth="1.5" className="text-zinc-200 dark:text-zinc-800" />
                  
                  {/* Nodes */}
                  {/* Controller API Gateway */}
                  <g className="cursor-pointer" onClick={() => setSelectedNodeId("ollama")}>
                    <rect x="200" y="25" rx="6" ry="6" width="100" height="40" className={`stroke-2 ${selectedNodeId === 'ollama' ? 'fill-primary/20 stroke-primary' : 'fill-card stroke-zinc-200 dark:stroke-zinc-800'}`} />
                    <text x="250" y="48" textAnchor="middle" fill="currentColor" fontSize="9" fontWeight="bold" className="text-zinc-800 dark:text-zinc-200">Gateway Router</text>
                  </g>

                  {/* OPA Policy */}
                  <g className="cursor-pointer" onClick={() => setSelectedNodeId("opa")}>
                    <rect x="50" y="105" rx="6" ry="6" width="100" height="40" className={`stroke-2 ${selectedNodeId === 'opa' ? 'fill-primary/20 stroke-primary' : 'fill-card stroke-zinc-200 dark:stroke-zinc-800'}`} />
                    <text x="100" y="128" textAnchor="middle" fill="currentColor" fontSize="9" fontWeight="bold" className="text-zinc-800 dark:text-zinc-200">OPA Policy</text>
                  </g>

                  {/* Marquez Lineage */}
                  <g className="cursor-pointer" onClick={() => setSelectedNodeId("marquez")}>
                    <rect x="200" y="105" rx="6" ry="6" width="100" height="40" className={`stroke-2 ${selectedNodeId === 'marquez' ? 'fill-primary/20 stroke-primary' : 'fill-card stroke-zinc-200 dark:stroke-zinc-800'}`} />
                    <text x="250" y="128" textAnchor="middle" fill="currentColor" fontSize="9" fontWeight="bold" className="text-zinc-800 dark:text-zinc-200">Marquez Lineage</text>
                  </g>

                  {/* Marker Sandbox */}
                  <g className="cursor-pointer" onClick={() => setSelectedNodeId("marker")}>
                    <rect x="350" y="105" rx="6" ry="6" width="100" height="40" className={`stroke-2 ${selectedNodeId === 'marker' ? 'fill-primary/20 stroke-primary' : 'fill-card stroke-zinc-200 dark:stroke-zinc-800'}`} />
                    <text x="400" y="128" textAnchor="middle" fill="currentColor" fontSize="9" fontWeight="bold" className="text-zinc-800 dark:text-zinc-200">Marker Sandbox</text>
                  </g>

                  {/* PostgreSQL Database */}
                  <g className="cursor-pointer" onClick={() => setSelectedNodeId("postgres")}>
                    <rect x="125" y="185" rx="6" ry="6" width="100" height="40" className={`stroke-2 ${selectedNodeId === 'postgres' ? 'fill-primary/20 stroke-primary' : 'fill-card stroke-zinc-200 dark:stroke-zinc-800'}`} />
                    <text x="175" y="208" textAnchor="middle" fill="currentColor" fontSize="9" fontWeight="bold" className="text-zinc-800 dark:text-zinc-200">PostgreSQL DB</text>
                  </g>
                </svg>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Monospace log console */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <Card className="shadow-sm border-zinc-200/60 dark:border-zinc-800/80 bg-card/40 backdrop-blur-md flex flex-col h-full justify-between">
            <CardHeader className="pb-3">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <Terminal className="w-4 h-4 text-violet-500" /> Log Console Output
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1">
              <div className="p-3 rounded-lg border border-zinc-200/60 dark:border-zinc-800 bg-zinc-950 font-mono text-[10px] text-emerald-400 overflow-y-auto min-h-[180px] max-h-[220px] flex flex-col gap-2">
                <div className="text-zinc-500 pb-1 border-b border-zinc-900">// Active Node: {selectedNode.name} • Port: {selectedNode.port}</div>
                {selectedNode.logs.map((log, idx) => (
                  <div key={idx} className="leading-relaxed whitespace-pre-wrap">{log}</div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
