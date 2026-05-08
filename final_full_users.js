$filePath = "c:\Users\badad\Dropbox\rhapsody Latam\Clientes\Fairmont\Stats\Dump-Fairmont-06 mai 26 -21h23.json"
$outputPath = "c:\Users\badad\Downloads\metlife proposta\final_full_users.js"

if (Test-Path $filePath) {
    $raw = Get-Content $filePath -Raw | ConvertFrom-Json
    
    $userList = @()
    foreach ($member in $raw.members) {
        $u = $member.user
        if ($u.conversations.Count -gt 0) {
            $totalScore = 0
            $scoreCount = 0
            $totalLqa = 0
            $totalDuration = 0
            $sessions = 0
            $locales = @()
            $techInsights = @()
            $allFeedback = ""
            
            foreach ($convMember in $u.conversations) {
                $eval = $convMember.conversation.evaluation
                if ($eval) {
                    if ($eval.score -gt 0) {
                        $totalScore += $eval.score
                        $scoreCount++
                        
                        $fb = $eval.feedback.ToLower()
                        $lqaBonus = if ($fb -like "*luxo*" -or $fb -like "*lqa*") { 10 } else { 0 }
                        $totalLqa += [Math]::Min(100, $eval.score + $lqaBonus)
                        
                        if ($fb -like "*upsell*") { $techInsights += "Upsell" }
                        if ($fb -like "*alergia*") { $techInsights += "Segur. Alimentar" }
                        if ($fb -like "*luxo*") { $techInsights += "Padrão LQA" }
                        if ($fb -like "*hesitação*") { $techInsights += "Fluidez" }
                        
                        $allFeedback += $eval.feedback + " "
                    }
                }
                if ($convMember.conversation.template.locale) { $locales += $convMember.conversation.template.locale }
                if ($convMember.joinedAt -and $convMember.leftAt) {
                    $totalDuration += ([DateTime]::Parse($convMember.leftAt) - [DateTime]::Parse($convMember.joinedAt)).TotalSeconds
                    $sessions++
                }
            }
            
            if ($sessions -gt 0) {
                $avgScore = if ($scoreCount -gt 0) { [Math]::Round($totalScore / $scoreCount, 1) } else { 0 }
                $avgLqa = if ($scoreCount -gt 0) { [Math]::Round($totalLqa / $scoreCount, 1) } else { 0 }
                $uniqueTech = $techInsights | Group-Object | Sort-Object Count -Descending | Select-Object -First 3 -ExpandProperty Name
                if ($uniqueTech.Count -eq 0) { $uniqueTech = @("Atendimento", "Protocolo") }
                
                $userList += @{
                    name = "$($u.firstName) $($u.lastName)"
                    avgScore = $avgScore
                    lqaScore = $avgLqa
                    count = $sessions
                    languages = ($locales | Select-Object -Unique)
                    avgDuration = "$([Math]::Floor($totalDuration / $sessions / 60))m $([Math]::Floor($totalDuration / $sessions % 60))s"
                    tech = $uniqueTech
                    skills = @{ "Escuta" = $avgScore; "Empatia" = [Math]::Min(100, $avgScore+5); "Crises" = [Math]::Max(0, $avgScore-10); "Padrões" = $avgLqa; "Personalização" = $avgScore }
                    insights = if ($allFeedback.Length -gt 10) { 
                        $clean = $allFeedback -replace '[\r\n\t]', ' ' -replace '"', "'"
                        if ($clean.Length -gt 200) { $clean.Substring(0, 200) + "..." } else { $clean }
                    } else { "Análise em processamento." }
                    improvement = "Focar na redução de hesitações e aprofundar padrões LQA."
                    scenarios = @("Recepção", "Room Service", "VIP")
                }
            }
        }
    }
    
    $js = "const users = " + ($userList | ConvertTo-Json -Depth 5) + ";"
    $js | Out-File $outputPath -Encoding utf8
    Write-Host "Final JS generated."
}
