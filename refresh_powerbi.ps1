# Archivo: refresh_powerbi.ps1

# 1. Función para leer el archivo .env
function Get-EnvVariables {
    $envFile = Join-Path -Path $PSScriptRoot -ChildPath ".env"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match '^([^=]+)=(.*)$') {
                Set-Item -Path "env:\$($matches[1].Trim())" -Value $matches[2].Trim()
            }
        }
    } else {
        Write-Error "El archivo .env no existe en la ruta $envFile"
        exit
    }
}

# 2. Cargar variables
Get-EnvVariables

# 3. Usar las variables del entorno
$user = $env:USER_PBI
$password = $env:PASSWORD_PBI
$workspaceSID = $env:WORKSPACE_SID
$datasetSID = $env:DATASET_SID

Write-Host "[INFO] Conectando a Power BI Service como $user..."

# NOTA: Si vas a usar credenciales reales, considera usar un método de autenticación 
# que no requiera el password en texto plano para mayor seguridad.
$secret_password = ConvertTo-SecureString $password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($user, $secret_password)

Connect-PowerBIServiceAccount -Credential $credential

$ruta = "groups/$workspaceSID/datasets/$datasetSID/refreshes"
$notificacion = @{"notifyOption"="MailOnFailure"}

Invoke-PowerBIRestMethod -Url $ruta -Method Post -Body (ConvertTo-Json $notificacion)

Write-Host "[INFO] Solicitud enviada correctamente."
Disconnect-PowerBIServiceAccount