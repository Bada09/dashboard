$filePath = "c:\Users\badad\Dropbox\rhapsody Latam\Clientes\Fairmont\Stats\Dump-Fairmont-06 mai 26 -21h23.json"
$outputPath = "c:\Users\badad\Downloads\metlife proposta\final_data.js"

if (Test-Path $filePath) {
    $raw = Get-Content $filePath -Raw | ConvertFrom-Json
    $userList = @()
    foreach ($member in $raw.members) {
        $u = $member.user
        if ($u.conversations.Count -gt 0) {
            $totalScore = 0; $scoreCount = 0; $totalLqa = 0; $totalDuration = 0; $sessions = 0; $locales = @(); $techInsights = @(); $allFeedback = ""
            foreach ($conv in $u.conversations) {
                $eval = $conv.conversation.evaluation
                if ($eval -and $eval.score -gt 0) {
                    $totalScore += $eval.score; $scoreCount++;
                    $fb = $eval.feedback.ToLower()
                    $lqaB = if ($fb -like "*luxo*" -or $fb -like "*lqa*") { 10 } else { 0 }
                    $totalLqa += [Math]::Min(100, $eval.score + $lqaB)
                    if ($fb -like "*upsell*") { $techInsights += "Upsell" }
                    if ($fb -like "*alergia*") { $techInsights += "Segur. Alimentar" }
                    if ($fb -like "*luxo*") { $techInsights += "Padrão LQA" }
                    if ($fb -like "*hesitação*") { $techInsights += "Fluidez" }
                    $allFeedback += $eval.feedback + " "
                }
                if ($conv.conversation.template.locale) { $locales += $conv.conversation.template.locale }
                if ($conv.joinedAt -and $conv.leftAt) {
                    $totalDuration += ([DateTime]::Parse($conv.leftAt) - [DateTime]::Parse($conv.joinedAt)).TotalSeconds
                    $sessions++
                }
            }
            if ($sessions -gt 0) {
                $avgS = if ($scoreCount -gt 0) { [Math]::Round($totalScore / $scoreCount, 1) } else { 0 }
                $avgL = if ($scoreCount -gt 0) { [Math]::Round($totalLqa / $scoreCount, 1) } else { 0 }
                $uniqueT = $techInsights | Group-Object | Sort-Object Count -Descending | Select-Object -First 3 -ExpandProperty Name
                if ($uniqueT.Count -eq 0) { $uniqueT = @("Protocolo") }
                $userList += @{
                    name = "$($u.firstName) $($u.lastName)"; avgScore = $avgS; lqaScore = $avgL; count = $sessions; languages = ($locales | Select-Object -Unique)
                    avgDuration = "$([Math]::Floor($totalDuration / $sessions / 60))m $([Math]::Floor($totalDuration / $sessions % 60))s"
                    tech = $uniqueT; insights = if ($allFeedback.Length -gt 10) { ($allFeedback -replace '[\r\n\t]', ' ' -replace '"', "'").Substring(0, [Math]::Min(200, $allFeedback.Length)) + "..." } else { "---" }
                    improvement = "Focar em padrões LQA."; scenarios = @("Geral")
                    skills = @{ "Escuta" = [Math]::Max(0, $avgS - 2); "Empatia" = [Math]::Min(100, $avgS + 5); "Crises" = [Math]::Max(0, $avgS - 10); "Padroes" = $avgL; "Personalizacao" = [Math]::Min(100, $avgS + 3) }
                }
            }
        }
    }
    "const users = " + ($userList | ConvertTo-Json -Depth 5) + ";" | Out-File $outputPath -Encoding utf8
}
