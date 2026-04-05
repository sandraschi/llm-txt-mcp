import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FileSearch, CheckCircle, AlertCircle, Loader2, Play } from "lucide-react";
import { mcpService } from "@/services/mcp";
import { Badge } from "@/components/ui/badge";

export function Generator() {
    const [path, setPath] = useState("D:/Dev/repos/llm-txt-mcp");
    const [isGenerating, setIsGenerating] = useState(false);
    const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
    const [message, setMessage] = useState("");
    const [results, setResults] = useState<any>(null);

    const handleGenerate = async () => {
        setIsGenerating(true);
        setStatus("idle");
        setMessage("Analyzing repository and generating llms.txt...");

        try {
            const response = await mcpService.generateLLMsTxt(path);
            if (response.success) {
                setStatus("success");
                setMessage("llms.txt generated successfully!");
                setResults(response.result);
            } else {
                setStatus("error");
                setMessage(response.error || "Generation failed.");
            }
        } catch (error) {
            setStatus("error");
            setMessage("Failed to connect to MCP server.");
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Project Generator</h2>
                    <p className="text-slate-400">Automated llms.txt creation and optimization</p>
                </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                <Card className="lg:col-span-1 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Configuration</CardTitle>
                        <CardDescription className="text-slate-400">Specify target project path</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">Project Root Path</Label>
                            <Input
                                className="bg-slate-900 border-slate-800 text-slate-100"
                                value={path}
                                onChange={(e) => setPath(e.target.value)}
                                placeholder="e.g. D:/Dev/repos/my-app"
                            />
                        </div>
                        <Button
                            className="w-full bg-blue-600 hover:bg-blue-700"
                            onClick={handleGenerate}
                            disabled={isGenerating || !path}
                        >
                            {isGenerating ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Processing...
                                </>
                            ) : (
                                <>
                                    <Play className="mr-2 h-4 w-4" />
                                    Generate llms.txt
                                </>
                            )}
                        </Button>
                    </CardContent>
                </Card>

                <Card className="lg:col-span-2 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Generation Output</CardTitle>
                        <CardDescription className="text-slate-400">Server response and audit logs</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {status === "idle" && !isGenerating && (
                            <div className="flex flex-col items-center justify-center h-48 border-2 border-dashed border-slate-800 rounded-md text-slate-500">
                                <FileSearch className="h-10 w-10 mb-2 opacity-20" />
                                <p>Ready to analyze project</p>
                            </div>
                        )}

                        {(isGenerating || status !== "idle") && (
                            <div className="space-y-4">
                                <div className={`flex items-center p-4 rounded-md border ${status === "success" ? "bg-emerald-900/10 border-emerald-900/30 text-emerald-400" :
                                        status === "error" ? "bg-red-900/10 border-red-900/30 text-red-400" :
                                            "bg-blue-900/10 border-blue-900/30 text-blue-400"
                                    }`}>
                                    {status === "success" ? <CheckCircle className="h-5 w-5 mr-3" /> :
                                        status === "error" ? <AlertCircle className="h-5 w-5 mr-3" /> :
                                            <Loader2 className="h-5 w-5 mr-3 animate-spin" />}
                                    <span className="text-sm font-medium">{message}</span>
                                </div>

                                {results && (
                                    <div className="rounded-md bg-slate-900 border border-slate-800 p-4 font-mono text-xs overflow-auto max-h-[300px]">
                                        <pre className="text-slate-300">{JSON.stringify(results, null, 2)}</pre>
                                    </div>
                                )}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
