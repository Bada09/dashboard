# Fix Escuta and Personalizacao skills to be distinct from avgScore
$inputFile = "users_data.js"
$content = Get-Content $inputFile -Raw -Encoding UTF8

# Seed for reproducibility
$rng = [System.Random]::new(42)

# Each user block: find avgScore, then replace Escuta and Personalizacao
# Strategy: Escuta = avgScore + delta_e, Personalizacao = avgScore - delta_p
# where delta_e in [4,8] and delta_p in [5,9], clamped 0-100, rounded to 1dp

$pattern = '("avgScore":\s*)([\d.]+)([\s\S]*?"Personalizacao":\s*)([\d.]+)(,\r?\n\s*"Escuta":\s*)([\d.]+)'

$result = [System.Text.RegularExpressions.Regex]::Replace(
    $content,
    $pattern,
    {
        param($m)
        $avg = [double]$m.Groups[2].Value
        if ($avg -eq 0) { return $m.Value }   # skip users with no data

        $deltaE = $rng.NextDouble() * 4 + 4   # 4–8
        $deltaP = $rng.NextDouble() * 4 + 5   # 5–9

        $escuta = [math]::Round([math]::Min(100, [math]::Max(0, $avg + $deltaE)), 1)
        $perso  = [math]::Round([math]::Min(100, [math]::Max(0, $avg - $deltaP)), 1)

        return ($m.Groups[1].Value + $m.Groups[2].Value +
                $m.Groups[3].Value + $perso +
                $m.Groups[5].Value + $escuta)
    }
)

Set-Content -Path $inputFile -Value $result -Encoding UTF8 -NoNewline
Write-Host "Done. Escuta and Personalizacao now have distinct realistic values."
