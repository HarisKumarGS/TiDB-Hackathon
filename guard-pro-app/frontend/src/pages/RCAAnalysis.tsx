import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDownIcon, ArrowLeftIcon } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

// Mock RCA data
const rcaData = {
  CR001: {
    id: "CR001",
    title: "Database Connection Timeout - Backend API",
    severity: "critical",
    timestamp: "2024-01-15 14:30:25",
    component: "Backend API",
    affectedUsers: 1247,
    duration: "45 minutes",
    status: "investigating",
    
    problemIdentification: {
      summary: "Multiple database connection timeouts causing API failures",
      symptoms: [
        "503 Service Unavailable errors on API endpoints",
        "Database connection pool exhaustion",
        "Increased response latency (>5000ms)",
        "User authentication failures"
      ],
      initialAlert: "High error rate alert triggered at 14:30:25 UTC"
    },
    
    rootCause: {
      primary: "Database connection pool misconfiguration",
      technical: "The connection pool max_connections was set to 10, but concurrent load peaked at 250+ simultaneous connections during traffic spike from marketing campaign.",
      timeline: [
        "14:15 - Marketing campaign launched, traffic increased 400%",
        "14:28 - Connection pool reached capacity",
        "14:30 - First timeout errors began",
        "14:35 - 95% of requests failing"
      ]
    },
    
    contributingFactors: [
      "Lack of connection pool monitoring",
      "No auto-scaling configured for database connections",
      "Marketing campaign launched without infrastructure team notification",
      "Missing circuit breaker pattern implementation"
    ],
    
    correctiveActions: [
      "Increased connection pool max_connections to 100",
      "Implemented connection pool monitoring dashboard",
      "Added auto-scaling for database connections",
      "Deployed circuit breaker pattern for database calls"
    ],
    
    preventiveActions: [
      "Establish cross-team communication for traffic spikes",
      "Implement load testing for all marketing campaigns",
      "Add connection pool alerting at 70% capacity",
      "Create runbook for database scaling procedures"
    ],
    
    codeRecommendations: {
      before: `// database.js
const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 10, // Too low!
  queueLimit: 0
});

// No error handling or retry logic
app.get('/api/users', async (req, res) => {
  const connection = await pool.getConnection();
  const [rows] = await connection.execute('SELECT * FROM users');
  connection.release();
  res.json(rows);
});`,
      
      after: `// database.js
const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 100, // Increased capacity
  queueLimit: 0,
  acquireTimeout: 60000,
  timeout: 60000,
  reconnect: true
});

// Circuit breaker implementation
const circuitBreaker = new CircuitBreaker(executeQuery, {
  timeout: 3000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000
});

// Enhanced error handling with retry logic
app.get('/api/users', async (req, res) => {
  try {
    const rows = await circuitBreaker.fire('SELECT * FROM users');
    res.json(rows);
  } catch (error) {
    logger.error('Database query failed:', error);
    res.status(503).json({ error: 'Service temporarily unavailable' });
  }
});

async function executeQuery(query) {
  const connection = await pool.getConnection();
  try {
    const [rows] = await connection.execute(query);
    return rows;
  } finally {
    connection.release();
  }
}`
    }
  }
};

const severityConfig = {
  critical: { label: "Critical", className: "severity-critical" },
  high: { label: "High", className: "severity-high" },
  medium: { label: "Medium", className: "severity-medium" },
  low: { label: "Low", className: "severity-low" }
};

export default function RCAAnalysis() {
  const { crashId } = useParams();
  const navigate = useNavigate();
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['problem', 'rootcause'])
  );

  const rca = crashId ? rcaData[crashId as keyof typeof rcaData] : null;

  if (!rca) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold">RCA not found</h1>
          <Button onClick={() => navigate('/dashboard')} className="mt-4">
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/dashboard')}
            className="p-2"
          >
            <ArrowLeftIcon className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Root Cause Analysis</h1>
            <p className="text-muted-foreground">Incident ID: {rca.id}</p>
          </div>
        </div>

        {/* Incident Overview */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{rca.title}</CardTitle>
              <Badge className={severityConfig[rca.severity as keyof typeof severityConfig].className}>
                {severityConfig[rca.severity as keyof typeof severityConfig].label}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Occurred:</span>
                <p className="font-medium">{rca.timestamp}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Duration:</span>
                <p className="font-medium">{rca.duration}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Affected Users:</span>
                <p className="font-medium">{rca.affectedUsers.toLocaleString()}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Component:</span>
                <p className="font-medium">{rca.component}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* RCA Sections */}
        <div className="space-y-4">
          {/* Problem Identification */}
          <Collapsible>
            <Card>
              <CollapsibleTrigger 
                className="w-full"
                onClick={() => toggleSection('problem')}
              >
                <CardHeader className="hover:bg-muted/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Problem Identification</CardTitle>
                    <ChevronDownIcon 
                      className={cn(
                        "h-5 w-5 transition-transform duration-200",
                        expandedSections.has('problem') && "rotate-180"
                      )} 
                    />
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2">Summary</h4>
                    <p className="text-sm text-muted-foreground">{rca.problemIdentification.summary}</p>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Symptoms</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {rca.problemIdentification.symptoms.map((symptom, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-red-400 mt-1">•</span>
                          {symptom}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Initial Alert</h4>
                    <p className="text-sm text-muted-foreground">{rca.problemIdentification.initialAlert}</p>
                  </div>
                </CardContent>
              </CollapsibleContent>
            </Card>
          </Collapsible>

          {/* Root Cause */}
          <Collapsible>
            <Card>
              <CollapsibleTrigger 
                className="w-full"
                onClick={() => toggleSection('rootcause')}
              >
                <CardHeader className="hover:bg-muted/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Root Cause Determination</CardTitle>
                    <ChevronDownIcon 
                      className={cn(
                        "h-5 w-5 transition-transform duration-200",
                        expandedSections.has('rootcause') && "rotate-180"
                      )} 
                    />
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2">Primary Cause</h4>
                    <p className="text-sm text-muted-foreground">{rca.rootCause.primary}</p>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Technical Details</h4>
                    <p className="text-sm text-muted-foreground">{rca.rootCause.technical}</p>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Timeline</h4>
                    <div className="space-y-2">
                      {rca.rootCause.timeline.map((event, i) => (
                        <div key={i} className="text-sm text-muted-foreground flex gap-2">
                          <span className="font-mono text-xs bg-muted px-2 py-1 rounded">
                            {event.split(' - ')[0]}
                          </span>
                          <span>{event.split(' - ')[1]}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </CollapsibleContent>
            </Card>
          </Collapsible>

          {/* Contributing Factors */}
          <Collapsible>
            <Card>
              <CollapsibleTrigger 
                className="w-full"
                onClick={() => toggleSection('factors')}
              >
                <CardHeader className="hover:bg-muted/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Contributing Factors</CardTitle>
                    <ChevronDownIcon 
                      className={cn(
                        "h-5 w-5 transition-transform duration-200",
                        expandedSections.has('factors') && "rotate-180"
                      )} 
                    />
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <CardContent>
                  <ul className="space-y-2">
                    {rca.contributingFactors.map((factor, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-amber-400 mt-1">•</span>
                        {factor}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </CollapsibleContent>
            </Card>
          </Collapsible>

          {/* Actions Taken */}
          <Collapsible>
            <Card>
              <CollapsibleTrigger 
                className="w-full"
                onClick={() => toggleSection('actions')}
              >
                <CardHeader className="hover:bg-muted/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Corrective & Preventive Actions</CardTitle>
                    <ChevronDownIcon 
                      className={cn(
                        "h-5 w-5 transition-transform duration-200",
                        expandedSections.has('actions') && "rotate-180"
                      )} 
                    />
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <CardContent className="space-y-6">
                  <div>
                    <h4 className="font-medium mb-3 text-emerald-400">Corrective Actions (Completed)</h4>
                    <ul className="space-y-2">
                      {rca.correctiveActions.map((action, i) => (
                        <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="text-emerald-400 mt-1">✓</span>
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <Separator />
                  <div>
                    <h4 className="font-medium mb-3 text-blue-400">Preventive Actions (Planned)</h4>
                    <ul className="space-y-2">
                      {rca.preventiveActions.map((action, i) => (
                        <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="text-blue-400 mt-1">→</span>
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </CollapsibleContent>
            </Card>
          </Collapsible>

          {/* Code Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Code-Level Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2 text-red-400">Before (Problematic Code)</h4>
                  <div className="diff-removed p-4 rounded-md font-mono text-sm overflow-x-auto">
                    <pre><code>{rca.codeRecommendations.before}</code></pre>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-2 text-emerald-400">After (Recommended Solution)</h4>
                  <div className="diff-added p-4 rounded-md font-mono text-sm overflow-x-auto">
                    <pre><code>{rca.codeRecommendations.after}</code></pre>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}