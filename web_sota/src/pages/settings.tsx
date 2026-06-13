import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Settings as SettingsIcon, Globe, Lock, Cpu } from "lucide-react";

function LLMSettings() {
    const [providers, setProviders] = useState<Record<string, {name:string}[]>>({});
    const [selectedProvider, setSelectedProvider] = useState("ollama");
    const [selectedModel, setSelectedModel] = useState("");
    const [status, setStatus] = useState<"loading"|"ready"|"error">("loading");
    useEffect(() => {
        fetch("/api/llm/providers").then(r => r.json()).then(d => {
            setProviders(d);
            const savedP = localStorage.getItem("llm_provider") || "ollama";
            const savedM = localStorage.getItem("llm_model") || "";
            setSelectedProvider(savedP);
            const models = d[savedP === "ollama" ? "ollama" : "lm_studio"] || [];
            setSelectedModel(savedM && models.some((m:{name:string}) => m.name === savedM) ? savedM : (models[0]?.name || ""));
            setStatus(models.length > 0 ? "ready" : "error");
        }).catch(() => {
            setProviders({ ollama: [{name:"llama3.2:3b"}] });
            setSelectedModel(localStorage.getItem("llm_model") || "llama3.2:3b");
            setStatus("ready");
        });
    }, []);
    const save = (p:string, m:string) => { localStorage.setItem("llm_provider", p); localStorage.setItem("llm_model", m); };
    const models = providers[selectedProvider === "ollama" ? "ollama" : "lm_studio"] || [];
    return (
        <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4 space-y-3">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-slate-200">Local LLM</h3>
                <span className={`inline-flex items-center gap-1.5 text-xs ${status === "ready" ? "text-emerald-400" : "text-amber-400"}`}>
                    <span className={`h-2 w-2 rounded-full ${status === "ready" ? "bg-emerald-400" : "bg-amber-400"}`} />
                    {status === "ready" ? "connected" : "probing"}
                </span>
            </div>
            <select className="h-9 w-full rounded-md border border-slate-700 bg-slate-900 px-3 text-sm text-slate-200"
                value={selectedProvider} onChange={(e) => { setSelectedProvider(e.target.value); save(e.target.value, ""); }}>
                <option value="ollama">Ollama</option>
                <option value="lm_studio">LM Studio</option>
            </select>
            <select className="h-9 w-full rounded-md border border-slate-700 bg-slate-900 px-3 text-sm text-slate-200"
                value={selectedModel} onChange={(e) => { setSelectedModel(e.target.value); save(selectedProvider, e.target.value); }}>
                {models.map((m) => <option key={m.name} value={m.name}>{m.name}</option>)}
            </select>
            <p className="text-xs text-slate-500">Used by AI tools. Saved to browser storage.</p>
        </div>
    );
}

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

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Cpu className="h-5 w-5 text-teal-500" />
                            LLM Provider
                        </CardTitle>
                        <CardDescription className="text-slate-400">Local model endpoint configuration</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <LLMSettings />
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
