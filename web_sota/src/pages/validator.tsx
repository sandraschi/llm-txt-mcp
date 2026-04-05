import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ShieldCheck, AlertTriangle, Loader2, Search } from "lucide-react";
import { mcpService } from "@/services/mcp";

export function Validator() {
    const [path, setPath] = useState("D:/Dev/repos/llm-txt-mcp/llms.txt");
    const [isValidating, setIsValidating] = useState(false);
    const [results, setResults] = useState<any>(null);

    const handleValidate = async () => {
        setIsValidating(true);
        try {
            const response = await mcpService.validateLLMsTxt(path);
            setResults(response.result);
        } catch (error) {
            console.error("Validation failed", error);
        } finally {
            setIsValidating(false);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Specification Validator</h2>
                <p className="text-slate-400">Ensure compliance with the llms.txt standard</p>
            </div>

            <div className="grid gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Validation Target</CardTitle>
                        <CardDescription className="text-slate-400">Enter path to llms.txt or the project root</CardDescription>
                    </CardHeader>
                    <CardContent className="flex gap-4">
                        <div className="flex-1 space-y-2">
                            <Input
                                className="bg-slate-900 border-slate-800 text-slate-100"
                                value={path}
                                onChange={(e) => setPath(e.target.value)}
                                placeholder="D:/path/to/project/llms.txt"
                            />
                        </div>
                        <Button
                            className="bg-purple-600 hover:bg-purple-700"
                            onClick={handleValidate}
                            disabled={isValidating || !path}
                        >
                            {isValidating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4 mr-2" />}
                            Validate
                        </Button>
                    </CardContent>
                </Card>

                {results && (
                    <Card className={`border-slate-800 bg-slate-950/50 ${results.valid ? "border-emerald-900/30" : "border-red-900/30"}`}>
                        <CardHeader className="flex flex-row items-center gap-4">
                            <div className={`p-2 rounded-full ${results.valid ? "bg-emerald-900/20 text-emerald-400" : "bg-red-900/20 text-red-400"}`}>
                                {results.valid ? <ShieldCheck className="h-6 w-6" /> : <AlertTriangle className="h-6 w-6" />}
                            </div>
                            <div>
                                <CardTitle className="text-white">
                                    {results.valid ? "Standard Compliant" : "Validation Errors Found"}
                                </CardTitle>
                                <CardDescription className="text-slate-400">
                                    {results.valid ? "This file follows the SOTA llms.txt specification." : "Correct the following issues to ensure interoperability."}
                                </CardDescription>
                            </div>
                        </CardHeader>
                        <CardContent>
                            {!results.valid && results.errors && (
                                <ul className="space-y-2">
                                    {results.errors.map((err: string, i: number) => (
                                        <li key={i} className="flex items-start gap-2 text-sm text-red-400">
                                            <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-red-500 shrink-0" />
                                            {err}
                                        </li>
                                    ))}
                                </ul>
                            )}
                            {results.valid && (
                                <div className="text-sm text-emerald-400">
                                    All structure, required fields, and links are valid.
                                </div>
                            )}
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
