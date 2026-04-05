import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Settings as SettingsIcon, Globe, Lock, Cpu } from "lucide-react";

export function Settings() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">System Settings</h2>
                <p className="text-slate-400">Configure global behavior and bridge parameters</p>
            </div>

            <div className="grid gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Globe className="h-5 w-5 text-blue-500" />
                            Bridge Endpoint
                        </CardTitle>
                        <CardDescription className="text-slate-400">Backend MCP server connection string</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">FastMCP HTTP URL</Label>
                            <Input
                                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                                defaultValue="http://localhost:10837"
                            />
                        </div>
                        <Button variant="outline" className="border-slate-800 text-slate-300 hover:bg-slate-800">
                            Verify Connectivity
                        </Button>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Lock className="h-5 w-5 text-purple-500" />
                            Security & Permissions
                        </CardTitle>
                        <CardDescription className="text-slate-400">Manage file system access tokens</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2 text-sm text-slate-400">
                            <p>Current Execution Environment: **Local Trusted**</p>
                            <p>File System Write Access: <span className="text-emerald-500 font-bold">GRANTED</span></p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
