param([Parameter(Mandatory=$true)][string]$WorkDirectory,
      [Parameter(Mandatory=$true)][string]$PythonExecutable)
$ErrorActionPreference = 'Stop'
& $PythonExecutable (Join-Path $PSScriptRoot 'workflow.py') --project-dir $WorkDirectory gate
if ($LASTEXITCODE -ne 0) { throw 'Primero pide un guion o registra su eleccion del profesional por defecto. No se consulto Google.' }
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$projectRoot = [IO.Path]::GetFullPath($WorkDirectory)
if (-not (Test-Path -LiteralPath $projectRoot -PathType Container)) {
    throw 'La carpeta de trabajo no existe.'
}
$statusPath = Join-Path $projectRoot '.gemini-setup-status.json'
$form = New-Object System.Windows.Forms.Form
$form.Text = 'Configurar Gemini para editar en DaVinci'
$form.Size = New-Object System.Drawing.Size(590, 315)
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$form.Font = New-Object System.Drawing.Font('Segoe UI', 10)

$intro = New-Object System.Windows.Forms.Label
$intro.Location = New-Object System.Drawing.Point(22, 18)
$intro.Size = New-Object System.Drawing.Size(530, 63)
$intro.Text = "Pega tu clave de Google AI Studio. Se comprobara con Google y se guardara en tu variable de usuario GEMINI_API_KEY. La clave no se mostrara en el chat ni se guardara en este proyecto."
$form.Controls.Add($intro)

$inputBox = New-Object System.Windows.Forms.TextBox
$inputBox.Location = New-Object System.Drawing.Point(22, 94)
$inputBox.Size = New-Object System.Drawing.Size(530, 30)
$inputBox.UseSystemPasswordChar = $true
$inputBox.MaxLength = 4096
$form.Controls.Add($inputBox)

$statusLabel = New-Object System.Windows.Forms.Label
$statusLabel.Location = New-Object System.Drawing.Point(22, 139)
$statusLabel.Size = New-Object System.Drawing.Size(530, 58)
$statusLabel.Text = 'Esta comprobacion no envia videos ni activa facturacion.'
$form.Controls.Add($statusLabel)

$saveButton = New-Object System.Windows.Forms.Button
$saveButton.Location = New-Object System.Drawing.Point(260, 211)
$saveButton.Size = New-Object System.Drawing.Size(176, 35)
$saveButton.Text = 'Guardar y comprobar'
$form.Controls.Add($saveButton)

$closeButton = New-Object System.Windows.Forms.Button
$closeButton.Location = New-Object System.Drawing.Point(447, 211)
$closeButton.Size = New-Object System.Drawing.Size(105, 35)
$closeButton.Text = 'Cerrar'
$closeButton.Add_Click({ $form.Close() })
$form.Controls.Add($closeButton)
$form.AcceptButton = $saveButton

$saveButton.Add_Click({
    $apiKey = $inputBox.Text.Trim()
    if ($apiKey.Length -lt 16 -or $apiKey -match '\s') {
        $statusLabel.Text = 'Pega la clave completa, sin espacios ni saltos de linea.'
        return
    }
    $saveButton.Enabled = $false
    $statusLabel.Text = 'Comprobando la clave con Google...'
    $form.Refresh()
    try {
        & $PythonExecutable (Join-Path $PSScriptRoot 'workflow.py') --project-dir $WorkDirectory gate
        if ($LASTEXITCODE -ne 0) { throw 'El guion cambio; confirma su version antes de consultar Google.' }
        $headers = @{ 'x-goog-api-key' = $apiKey }
        $catalog = Invoke-RestMethod -Uri 'https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000' -Headers $headers -TimeoutSec 30
        $modelNames = @($catalog.models | ForEach-Object { $_.name })
        [Environment]::SetEnvironmentVariable('GEMINI_API_KEY', $apiKey, 'User')
        $safeStatus = @{ authenticated = $true; saved = $true; model_names = $modelNames; checked_at = (Get-Date).ToString('o') }
        $safeStatus | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statusPath -Encoding UTF8
        $inputBox.Clear()
        $inputBox.Enabled = $false
        $statusLabel.Text = 'Clave guardada. Google respondio correctamente. Puedes cerrar esta ventana y avisar al asistente.'
        $statusLabel.ForeColor = [System.Drawing.Color]::DarkGreen
        $saveButton.Text = 'Configurado'
    } catch {
        $httpCode = 0
        if ($_.Exception.Response) { $httpCode = [int]$_.Exception.Response.StatusCode }
        $statusLabel.ForeColor = [System.Drawing.Color]::DarkRed
        if ($httpCode -eq 400 -or $httpCode -eq 401 -or $httpCode -eq 403) {
            $statusLabel.Text = "Google no acepto la clave (HTTP $httpCode). Revisa que este activa y habilitada para Gemini. No se guardo."
        } elseif ($httpCode -eq 429) {
            $statusLabel.Text = 'Google indica limite de uso (HTTP 429). No se guardo la clave. Revisa tu cuota en AI Studio.'
        } else {
            $statusLabel.Text = "No se pudo completar la comprobacion (HTTP $httpCode). Revisa tu conexion y vuelve a intentar."
        }
        $saveButton.Enabled = $true
    } finally {
        $apiKey = $null
        $headers = $null
    }
})
$form.Add_Shown({ $inputBox.Focus() })
[void]$form.ShowDialog()
$form.Dispose()
