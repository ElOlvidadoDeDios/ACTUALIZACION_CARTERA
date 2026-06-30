# Archivo: refresh_powerbi.ps1

$user = 'desarrollador@dilebi.onmicrosoft.com'
$password = 'Desarrollo.12345'
$workspaceSID = 'd4be985c-0e8e-495b-91a9-637b0cf0335f'
$datasetSID = '931d9cc1-78ae-49dc-8ad0-d66d2bbaa3e2'

$secret_password = ConvertTo-SecureString $password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($user, $secret_password)

Write-Host "[INFO] Conectando a Power BI Service..."
Connect-PowerBIServiceAccount -Credential $credential

$ruta = "groups/$workspaceSID/datasets/$datasetSID/refreshes"
$notificacion = @{"notifyOption"="MailOnFailure"}

Write-Host "[INFO] Enviando orden de actualizacion al Dashboard..."
Invoke-PowerBIRestMethod -Url $ruta -Method Post -Body (ConvertTo-Json $notificacion)

Write-Host "[INFO] Orden recibida por Microsoft con exito."
Disconnect-PowerBIServiceAccount