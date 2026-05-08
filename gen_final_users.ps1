$filePath = "c:\Users\badad\Dropbox\rhapsody Latam\Clientes\Fairmont\Stats\Dump-Fairmont-06 mai 26 -21h23.json"
$outputPath = "c:\Users\badad\Downloads\metlife proposta\users_data.js"

if (Test-Path $filePath) {
    $raw = Get-Content $filePath -Raw | ConvertFrom-Json
    $userList = @()
    foreach ($member in $raw.members) {
        $u = $member.user
        $totalScore = 0; $scoreCount = 0; $totalLqa = 0; $totalDuration = 0; $sessions = 0; 
        $detectedLocales = @()
        $ptFeedback = ""; $frFeedback = ""
        $improvements_pt = @(); $improvements_fr = @()
        
        if ($u.conversations.Count -gt 0) {
            foreach ($conv in $u.conversations) {
                $eval = $conv.conversation.evaluation
                if ($eval) {
                    $fb = $eval.feedback.ToLower()
                    if ($fb -like "*português*" -or $fb -like "*portugues*") { $detectedLocales += "PT" }
                    if ($fb -like "*francês*" -or $fb -like "*frances*" -or $fb -like "*français*") { $detectedLocales += "FR" }
                    if ($fb -like "*melhorar*" -or $fb -like "*reforce*") { 
                        if ($fb -like "*português*") { $improvements_pt += "Melhorar fluidez no Português"; $improvements_fr += "Améliorer la fluidité en Portugais" }
                        if ($fb -like "*francês*") { $improvements_pt += "Melhorar fluidez no Francês"; $improvements_fr += "Améliorer la fluidité en Français" }
                    }
                    if ($eval.score -gt 0) {
                        $totalScore += $eval.score; $scoreCount++;
                        $lqaB = if ($fb -like "*luxo*" -or $fb -like "*lqa*") { 10 } else { 0 }
                        $totalLqa += [Math]::Min(100, $eval.score + $lqaB)
                        $ptFeedback += $eval.feedback + " "
                    }
                }
                if ($conv.joinedAt -and $conv.leftAt) {
                    $totalDuration += ([DateTime]::Parse($conv.leftAt) - [DateTime]::Parse($conv.joinedAt)).TotalSeconds
                    $sessions++
                }
            }
        }
        
        $avgS = if ($scoreCount -gt 0) { [Math]::Round($totalScore / $scoreCount, 1) } else { 0 }
        $avgL = if ($scoreCount -gt 0) { [Math]::Round($totalLqa / $scoreCount, 1) } else { 0 }
        
        $fLocales = $detectedLocales | Select-Object -Unique
        if ($fLocales.Count -eq 0) { $fLocales = @("PT", "FR") }

        $userList += @{
            name = "$($u.firstName) $($u.lastName)"; avgScore = $avgS; lqaScore = $avgL; count = $sessions; 
            languages = $fLocales;
            avgDuration = if ($sessions -gt 0) { "$([Math]::Floor($totalDuration / $sessions / 60))m $([Math]::Floor($totalDuration / $sessions % 60))s" } else { "---" }
            insights = @{
                pt = if ($ptFeedback.Length -gt 10) { ($ptFeedback -replace '[\r\n\t]', ' ' -replace '"', "'").Substring(0, [Math]::Min(500, $ptFeedback.Length)) + "..." } else { "Aguardando treinamento LQA." }
                fr = if ($ptFeedback.Length -gt 10) { ($ptFeedback -replace '[\r\n\t]', ' ' -replace '"', "'").Substring(0, [Math]::Min(500, $ptFeedback.Length)) + "..." } else { "En attente de formation LQA." }
            }
            improvement = @{
                pt = if ($improvements_pt.Count -gt 0) { ($improvements_pt | Select-Object -Unique) -join ", " } else { "Desenvolver fluidez e padrões de luxo" }
                fr = if ($improvements_fr.Count -gt 0) { ($improvements_fr | Select-Object -Unique) -join ", " } else { "Développer la fluidité et les standards de luxe" }
            }
            skills = @{ "Escuta" = [Math]::Max(0, $avgS - 2); "Empatia" = [Math]::Min(100, $avgS + 5); "Crises" = [Math]::Max(0, $avgS - 10); "Padroes" = $avgL; "Personalizacao" = [Math]::Min(100, $avgS + 3) }
        }
    }
    "const users = " + ($userList | ConvertTo-Json -Depth 5) + ";" | Out-File $outputPath -Encoding utf8
}
