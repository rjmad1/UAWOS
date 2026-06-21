// src/services/api.ts

export interface SystemStatus {
  docker_running: boolean;
  running_containers: Record<string, string>;
  health_summary: {
    total: number;
    green: number;
    yellow: number;
    red: number;
    gray: number;
    strict_percentage: number;
    weighted_percentage: number;
  };
  domains: Record<string, Record<string, string>>;
  alternate_daemons: Record<string, string>;
  git_sync?: {
    status: string;
    message: string;
    last_sync_time_str: string;
  };
}

export interface Outcome {
  id: string;
  title: string;
  metric: string;
  target: number;
  current: number;
  baseline: number;
  progress: number;
}

export interface Plan {
  id: string;
  name: string;
  cost: number;
  duration: number;
  probability: number;
  risk: 'Low' | 'Medium' | 'High';
  recommended: boolean;
  selected: boolean;
}

export interface Task {
  id: string;
  name: string;
  done: boolean;
  evidence: string | null;
  blocked?: boolean;
  blockerMsg?: string;
}

export interface Milestone {
  id: string;
  name: string;
  start: number; // offset in px or %
  width: number;
  blocked: boolean;
  tasks: Task[];
}

export interface Objective {
  id: string;
  title: string;
  category: string;
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  description: string;
  health: number;
  readiness: number;
  sponsor: string;
  owner: string;
  outcomes: Outcome[];
  plans: Plan[];
  milestones: Milestone[];
  learnings: string[];
  status?: 'draft' | 'active' | 'paused' | 'completed' | 'failed' | 'cancelled' | 'archived';
}

export interface TraceRecord {
  id: string;
  requirement: string;
  epic: string;
  epicStatus: 'Passed' | 'Blocked' | 'Untraced';
  task: string;
  commit: string;
  verificationHash: string;
  verified: boolean;
}

export interface ExceptionWaiver {
  id: string;
  policyId: string;
  ruleClause: string;
  justification: string;
  requestor: string;
  date: string;
  status: 'pending' | 'approved' | 'rejected';
}

// Subtle, agnostic default mock data
export const mockObjectives: Record<string, Objective> = {
  "OBJ-101": {
    id: "OBJ-101",
    title: "Deploy Cluster Node Migration",
    category: "Infrastructure",
    priority: "High",
    description: "Organize system configurations, run container migrations, and verify network latency targets to transition client nodes seamlessly.",
    health: 85,
    readiness: 100,
    sponsor: "Infrastructure Sponsor",
    owner: "System Operator Group",
    status: "active",
    outcomes: [
      { id: "OUT-101A", title: "Target Compute Density Met", metric: "Density Ratio", target: 95, current: 40, baseline: 20, progress: 26 },
      { id: "OUT-101B", title: "Connection Latency Stabilized", metric: "Milliseconds", target: 40, current: 40, baseline: 120, progress: 100 },
      { id: "OUT-101C", title: "Policy Isolation Audit Passed", metric: "Checklists Done", target: 10, current: 8, baseline: 0, progress: 80 }
    ],
    plans: [
      { id: "PLN-101", name: "Sequential Node Routing Plan", cost: 14000, duration: 30, probability: 95, risk: "Low", recommended: true, selected: true },
      { id: "PLN-102", name: "Concurrent Bulk Migration Plan", cost: 28000, duration: 15, probability: 70, risk: "High", recommended: false, selected: false }
    ],
    milestones: [
      { id: "M-101", name: "Intake & Discovery", start: 20, width: 120, blocked: false, tasks: [
        { id: "T-101A", name: "Translate system configuration parameters", done: true, evidence: "sys_config_translated.json" },
        { id: "T-101B", name: "Execute schema parsing mapping test", done: false, evidence: null, blocked: true, blockerMsg: "Requires authorized compliance signature token validation." }
      ]},
      { id: "M-102", name: "Migration & Testing", start: 160, width: 80, blocked: false, tasks: [
        { id: "T-102A", name: "Submit node routing tables configurations", done: true, evidence: "routing_conf_receipts.zip" },
        { id: "T-102B", name: "Trigger live latency verification scans", done: true, evidence: "latency_audit_report.json" }
      ]}
    ],
    learnings: [
      "Target host configurations require certified schemas 30 days in advance. Must trigger translations on initialization."
    ]
  },
  "OBJ-201": {
    id: "OBJ-201",
    title: "Reduce Resource Allocation Waste by 15%",
    category: "Operational Efficiency",
    priority: "High",
    description: "Construct proactive scaling triggers and optimize resource caching models to minimize memory run-rate waste.",
    health: 90,
    readiness: 100,
    sponsor: "Department Director",
    owner: "Operations Squad",
    status: "active",
    outcomes: [
      { id: "OUT-201A", title: "Memory Allocation Leak Reduced", metric: "Idle Compute %", target: 5.0, current: 7.2, baseline: 12.0, progress: 68 },
      { id: "OUT-201B", title: "Average Cache Hit Ratio Improved", metric: "Hit Ratio %", target: 92, current: 88, baseline: 75, progress: 76 }
    ],
    plans: [
      { id: "PLN-201", name: "Automated Lifecycle Trigger Routing", cost: 8500, duration: 25, probability: 90, risk: "Medium", recommended: true, selected: true },
      { id: "PLN-202", name: "Static Resource Decommissioning", cost: 12000, duration: 40, probability: 75, risk: "Low", recommended: false, selected: false }
    ],
    milestones: [
      { id: "M-201", name: "Telemetry Mappings Setup", start: 30, width: 140, blocked: false, tasks: [
        { id: "T-201A", name: "Connect system parameters to trace logs", done: true, evidence: "trace_endpoints_mapped.json" },
        { id: "T-201B", name: "Calibrate scaling threshold classification rules", done: true, evidence: "threshold_calibrations.txt" }
      ]},
      { id: "M-202", name: "Targeted Decom Execution", start: 190, width: 100, blocked: false, tasks: [
        { id: "T-202A", name: "Deploy automated cleanup scripts to cluster", done: false, evidence: null },
        { id: "T-202B", name: "Schedule manual allocation review checklists", done: false, evidence: null }
      ]}
    ],
    learnings: [
      "Components undergoing rapid deployment loops exhibit 3x higher leakage risk. Configured local automated cleanups."
    ]
  }
};

export const mockTraceability: TraceRecord[] = [
  { id: "TR-001", requirement: "REQ-01: Auto PII Identification", epic: "EPIC-10: Intake Pipeline", epicStatus: "Passed", task: "T-101A: Mask raw strings", commit: "c0182fa", verificationHash: "sha256-a189f72b", verified: true },
  { id: "TR-002", requirement: "REQ-02: Document Extraction Sandbox", epic: "EPIC-10: Intake Pipeline", epicStatus: "Passed", task: "T-101B: Sandboxed parsing", commit: "a0928f1", verificationHash: "sha256-e91823ab", verified: true },
  { id: "TR-003", requirement: "REQ-03: Cycle Verification Detection", epic: "EPIC-20: Timeline Logic", epicStatus: "Blocked", task: "T-102B: Build DFS check", commit: "f01928a", verificationHash: "sha256-f819a82b", verified: false },
  { id: "TR-004", requirement: "REQ-04: Declarative Policy Check", epic: "EPIC-30: Compliance Gates", epicStatus: "Passed", task: "T-201A: Map policy routes", commit: "9021aef", verificationHash: "sha256-7821ef32", verified: true }
];

export const mockWaivers: ExceptionWaiver[] = [
  { id: "EXC-001", policyId: "POL-SEC-01", ruleClause: `deny_restricted_tool_executions {\n  input.tool == "system_command"\n  not user_authorized\n}`, justification: "Emergency restore of cluster routing configurations requires running sandboxed command shell checks.", requestor: "Operations Monitor", date: "2026-06-22", status: "pending" },
  { id: "EXC-002", policyId: "POL-FIN-02", ruleClause: `deny_budget_overruns {\n  input.cost_spent > input.cost_limit\n}`, justification: "Allocate compute cache buffers to clear queue blocks caused by outbound gateway latencies.", requestor: "Planning Director", date: "2026-06-21", status: "approved" }
];

export const mockSystemStatus: SystemStatus = {
  docker_running: true,
  running_containers: {
    "uawos-postgres": "Up 2 hours",
    "uawos-qdrant": "Up 2 hours",
    "uawos-marquez": "Up 2 hours",
    "uawos-superset": "Up 2 hours",
    "uawos-dependency-track-api": "Up 2 hours",
    "uawos-marker-service": "Up 2 hours"
  },
  health_summary: {
    total: 36,
    green: 31,
    yellow: 4,
    red: 1,
    gray: 0,
    strict_percentage: 86.1,
    weighted_percentage: 91.7
  },
  domains: {
    "Services": {
      "Objective Engine": "GREEN",
      "Discovery Engine": "GREEN",
      "Planning Engine": "GREEN",
      "Governance Engine": "GREEN",
      "Knowledge Engine": "GREEN",
      "Value Engine": "GREEN",
      "Simulation Engine": "GREEN"
    },
    "Agents": {
      "Planner Agent": "GREEN",
      "Orchestrator Agent": "GREEN",
      "Executor Agent": "GREEN",
      "Reviewer Agent": "GREEN",
      "Governor Agent": "GREEN",
      "Learner Agent": "GREEN",
      "Knowledge Manager Agent": "GREEN"
    },
    "APIs": {
      "Outbound Model Gateway": "GREEN",
      "Custom Engine APIs": "GREEN"
    },
    "Infrastructure": {
      "Postgres DB": "GREEN",
      "Qdrant Vector DB": "GREEN",
      "Marquez Lineage": "GREEN",
      "Apache Superset": "GREEN",
      "Dependency-Track API": "GREEN"
    }
  },
  alternate_daemons: {
    "Ollama Local LLM": "GREEN",
    "Core Redis": "GREEN"
  },
  git_sync: {
    status: "GREEN",
    message: "Synchronization complete! Ahead by 0 commits.",
    last_sync_time_str: "2026-06-22 00:30:00"
  }
};

export class APIClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = window.location.origin;
  }

  private getHeaders(token?: string, tenantId?: string) {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
      headers["X-UAWOS-Token"] = token;
    }
    if (tenantId) {
      headers["X-Tenant-ID"] = tenantId;
    }
    return headers;
  }

  async getStatus(): Promise<SystemStatus> {
    try {
      const res = await fetch(`${this.baseUrl}/api/status`);
      if (!res.ok) throw new Error("API response error");
      const data = await res.json();
      // Ensure expected structures exist
      if (!data.health_summary) throw new Error("Invalid schema");
      return data;
    } catch {
      return mockSystemStatus;
    }
  }

  async getObjectives(): Promise<Objective[]> {
    try {
      const res = await fetch(`${this.baseUrl}/api/objective/list`);
      if (!res.ok) throw new Error("API response error");
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      // Map dictionary/list to array
      const list = data.objectives ? Object.values(data.objectives) : Object.values(data);
      return list as Objective[];
    } catch {
      return Object.values(mockObjectives);
    }
  }

  async getTraceability(): Promise<{ matrix: TraceRecord[]; health: any }> {
    try {
      const res = await fetch(`${this.baseUrl}/api/traceability`);
      if (!res.ok) throw new Error("API response error");
      const data = await res.json();
      return {
        matrix: data.matrix || mockTraceability,
        health: data.health || { coverage: 85, verified_percentage: 75 }
      };
    } catch {
      return { matrix: mockTraceability, health: { coverage: 75, verified_percentage: 75 } };
    }
  }

  async submitObjective(text: string, options: { owner: string; sponsor: string; input_type: string }, token?: string, tenantId?: string): Promise<any> {
    try {
      const res = await fetch(`${this.baseUrl}/api/objective/submit`, {
        method: "POST",
        headers: this.getHeaders(token, tenantId),
        body: JSON.stringify({ text, ...options })
      });
      if (!res.ok) throw new Error("Submission failed");
      return await res.json();
    } catch (e: any) {
      // Emulate parsing locally
      return {
        status: "success",
        objective: {
          id: `OBJ-${Math.floor(100 + Math.random() * 900)}`,
          title: text.split("\n")[0].substring(0, 50) || "Ingested Objective",
          description: text,
          priority: "Medium",
          category: "Agnostic Operations",
          health: 70,
          readiness: 70,
          owner: options.owner || "Unassigned Agent",
          sponsor: options.sponsor || "Strategic Sponsor",
          outcomes: [
            { id: `OUT-A-${Math.random()}`, title: "Success Target Reached", metric: "Progress Percentage", target: 100, current: 0, baseline: 0, progress: 0 }
          ],
          plans: [
            { id: `PLN-${Math.random()}`, name: "Automated Path Generation A", cost: 15000, duration: 40, probability: 80, risk: "Medium", recommended: true, selected: true },
            { id: `PLN-${Math.random()}`, name: "Alternative Manual Path B", cost: 20000, duration: 60, probability: 65, risk: "Low", recommended: false, selected: false }
          ],
          milestones: [
            { id: `M-${Math.random()}`, name: "Primary Track Execution", start: 20, width: 150, blocked: false, tasks: [
              { id: `T-${Math.random()}`, name: "Execute preliminary intake checks", done: false, evidence: null }
            ]}
          ],
          learnings: ["Requires outcome calibration during planning cycles."]
        }
      };
    }
  }

  async executeObjectiveAction(objId: string, action: string, updates: any = {}, token?: string, tenantId?: string): Promise<any> {
    try {
      const res = await fetch(`${this.baseUrl}/api/objective/action`, {
        method: "POST",
        headers: this.getHeaders(token, tenantId),
        body: JSON.stringify({ objective_id: objId, action, updates })
      });
      if (!res.ok) throw new Error("Action failed");
      return await res.json();
    } catch {
      return { status: "success", action, objective_id: objId };
    }
  }
}

export const api = new APIClient();
