$files = @(
    'evidence_vault/01fbc234-5c79-435e-b395-08931df843f3_download.jpg',
    'evidence_vault/ca803220-3c3a-414e-a427-941c57a4dfab_download.jpg',
    'evidence_vault/2ec2a6e2-3218-4b3b-8688-9d31a9d7d9d9_3000.webp'
)

$results = @()

foreach ($f in $files) {
    if (Test-Path $f) {
        $body = @{case_id='test'; file_path=$f} | ConvertTo-Json
        try {
            $resp = Invoke-WebRequest -Uri 'http://localhost:8000/api/vision/analyze' -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing
            $json = $resp.Content | ConvertFrom-Json
            
            $results += [PSCustomObject]@{
                FileName = Split-Path $f -Leaf
                Probability = $json.ganProbability
                NoiseLevel = $json.noiseLevel
                DL_Score = $json.metadata.dl_score
                Color_Score = $json.metadata.color_score
                Texture_Score = $json.metadata.texture_score
                Noise_Score = $json.metadata.noise_scale_score
            }
        } catch {
            Write-Host "Error processing $f : $_"
        }
    } else {
        Write-Host "File not found: $f"
    }
}

$results | Format-Table -AutoSize
