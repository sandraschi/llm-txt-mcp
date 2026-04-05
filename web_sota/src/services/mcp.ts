export interface MCPToolResponse {
    success: boolean;
    result?: any;
    error?: string;
    details?: string;
}

const BACKEND_URL = 'http://localhost:10837';

export async function callMCPTool(name: string, args: Record<string, any> = {}): Promise<MCPToolResponse> {
    try {
        const response = await fetch(`${BACKEND_URL}/call`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                arguments: args,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            return {
                success: false,
                error: errorData.error || `HTTP error! status: ${response.status}`,
                details: errorData.details
            };
        }

        const data = await response.json();
        return {
            success: true,
            result: data
        };
    } catch (error: any) {
        console.error(`MCP Tool Call Error (${name}):`, error);
        return {
            success: false,
            error: error.message || 'Network error calling MCP backend'
        };
    }
}

export const mcpService = {
    getStatus: () => callMCPTool('get_repo_status'),
    generateLLMsTxt: (path: string, options: any = {}) =>
        callMCPTool('generate_llms_txt', { path, ...options }),
    validateLLMsTxt: (path: string) =>
        callMCPTool('validate_llms_txt', { path }),
    ping: () => fetch(`${BACKEND_URL}/api/v1/health`).then(r => r.json()).catch(() => ({ status: 'error' }))
};
