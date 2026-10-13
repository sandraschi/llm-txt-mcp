# Per-repo fleet start config for llm-txt-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'llm-txt-mcp'
    BackendPort  = 10837
    FrontendPort = 10836
    HealthPath   = '/api/v1/health'
    WebRoot      = 'web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'llm_txt_mcp.server:app'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '10837' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
