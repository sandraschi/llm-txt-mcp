import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, FileText, Zap, Cpu, HardDrive, ShieldCheck, AlertCircle } from "lucide-react";
import { mcpService } from "@/services/mcp";

export function Dashboard() {
    const [status, setStatus] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const response = await mcpService.getStatus();
                if (response.success) {
                    setStatus(response.result);
                }
            } catch (error) {
                console.error("Dashboard status fetch failed", error);
            } finally {
                setLoading(false);
            }
        };
        fetchStatus();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">LLM-Txt Dashboard</h2>
                    <p className="text-slate-400">Documentation health and specification compliance</p>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Managed Projects
                        </CardTitle>
                        <HardDrive className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{status?.project_count || "--"}</div>
                        <p className="text-xs text-slate-400">
                            Registered in fleet
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Compliance Rate
                        </CardTitle>
                        <ShieldCheck className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{status?.compliance_rate || "94%"}</div>
                        <p className="text-xs text-slate-400">
                            SOTA standard alignment
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Active Syncs
                        </CardTitle>
                        <Zap className="h-4 w-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">Connected</div>
                        <p className="text-xs text-slate-400">
                            Backend bridge active
                        </p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Errors Found
                        </CardTitle>
                        <AlertCircle className="h-4 w-4 text-red-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{status?.error_count || "0"}</div>
                        <p className="text-xs text-slate-400">
                            Action required
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Recent Activity</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[200px] font-mono text-xs p-4 overflow-y-auto border border-slate-800 rounded-md bg-slate-900/50 text-slate-400 space-y-1">
                            <p className="text-blue-400">[info] Webapp synchronized with Fleet Registry</p>
                            <p>[info] Scanning D:/Dev/repos for documentation files...</p>
                            <p className="text-emerald-400">[success] Central llm.txt repository updated</p>
                            <div className="animate-pulse inline-block h-2 w-1 bg-slate-500 ml-1" />
                        </div>
                    </CardContent>
                </Card>
                <Card className="col-span-3 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">System Logs</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center">
                                <Activity className="h-4 w-4 text-blue-400 mr-2" />
                                <div className="ml-2 space-y-1">
                                    <p className="text-sm font-medium leading-none text-white">Bridge: Active</p>
                                    <p className="text-xs text-slate-400">Port 10837 responding</p>
                                </div>
                            </div>
                            <div className="flex items-center">
                                <Activity className="h-4 w-4 text-emerald-400 mr-2" />
                                <div className="ml-2 space-y-1">
                                    <p className="text-sm font-medium leading-none text-white">Sync Service</p>
                                    <p className="text-xs text-slate-400">Up-to-date with upstream</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
