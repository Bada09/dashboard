$filePath = "c:\Users\badad\Dropbox\rhapsody Latam\Clientes\Fairmont\Stats\Dump-Fairmont-06 mai 26 -21h23.json"
$outputPath = "c:\Users\badad\Downloads\metlife proposta\multilang_behavioral_data.js"

if (Test-Path $filePath) {
    $raw = Get-Content $filePath -Raw | ConvertFrom-Json
    $userList = @()
    foreach ($member in $raw.members) {
        $u = $member.user
        if ($u.conversations.Count -gt 0) {
            $totalScore = 0; $scoreCount = 0; $totalLqa = 0; $totalDuration = 0; $sessions = 0; 
            $detectedLocales = @()
            $techInsights = @()
            $ptFeedback = ""; $frFeedback = ""
            $improvements_pt = @(); $improvements_fr = @()
            
            foreach ($conv in $u.conversations) {
                $eval = $conv.conversation.evaluation
                if ($eval) {
                    $fb = $eval.feedback.ToLower()
                    if ($fb -like "*português*" -or $fb -like "*portugues*") { 
                        $detectedLocales += "PT"
                        if ($fb -like "*melhorar*" -or $fb -like "*reforce*") { 
                            $improvements_pt += "Melhorar fluidez no Português"
                            $improvements_fr += "Améliorer la fluidité en Portugais"
                        }
                    }
                    if ($fb -like "*francês*" -or $fb -like "*frances*" -or $fb -like "*français*") { 
                        $detectedLocales += "FR"
                        if ($fb -like "*melhorar*" -or $fb -like "*reforce*") { 
                            $improvements_pt += "Melhorar fluidez no Francês"
                            $improvements_fr += "Améliorer la fluidité en Français"
                        }
                    }
                    if ($fb -like "*menu*" -or $fb -like "*cardápio*") { 
                        $improvements_pt += "Conhecimento do Cardápio"
                        $improvements_fr += "Connaissance du Menu"
                    }
                    if ($fb -like "*hesitação*" -or $fb -like "*muleta*") { 
                        $improvements_pt += "Reduzir vícios de linguagem"
                        $improvements_fr += "Réduire les tics de langage"
                    }

                    if ($eval.score -gt 0) {
                        $totalScore += $eval.score; $scoreCount++;
                        $lqaB = if ($fb -like "*luxo*" -or $fb -like "*lqa*") { 10 } else { 0 }
                        $totalLqa += [Math]::Min(100, $eval.score + $lqaB)
                        
                        # Store feedback for summary
                        $ptFeedback += $eval.feedback + " "
                        $frFeedback += $eval.feedback + " " # Simple duplication for now, could be smarter
                    }
                }
                if ($conv.joinedAt -and $conv.leftAt) {
                    $totalDuration += ([DateTime]::Parse($conv.leftAt) - [DateTime]::Parse($conv.joinedAt)).TotalSeconds
                    $sessions++
                }
            }
            
            if ($sessions -gt 0) {
                $avgS = if ($scoreCount -gt 0) { [Math]::Round($totalScore / $scoreCount, 1) } else { 0 }
                $avgL = if ($scoreCount -gt 0) { [Math]::Round($totalLqa / $scoreCount, 1) } else { 0 }
                
                $finalImprov_pt = $improvements_pt | Select-Object -Unique
                if ($finalImprov_pt.Count -eq 0) { $finalImprov_pt = @("Consolidar padrões LQA") }
                $finalImprov_fr = $improvements_fr | Select-Object -Unique
                if ($finalImprov_fr.Count -eq 0) { $finalImprov_fr = @("Consolider les standards LQA") }

                $userList += @{
                    name = "$($u.firstName) $($u.lastName)"; avgScore = $avgS; lqaScore = $avgL; count = $sessions; 
                    languages = ($detectedLocales | Select-Object -Unique);
                    avgDuration = "$([Math]::Floor($totalDuration / $sessions / 60))m $([Math]::Floor($totalDuration / $sessions % 60))s"
                    insights = @{
                        pt = if ($ptFeedback.Length -gt 10) { ($ptFeedback -replace '[\r\n\t]', ' ' -replace '"', "'").Substring(0, [Math]::Min(300, $ptFeedback.Length)) + "..." } else { "Análise em processamento." }
                        fr = if ($frFeedback.Length -gt 10) { ($frFeedback -replace '[\r\n\t]', ' ' -replace '"', "'").Substring(0, [Math]::Min(300, $frFeedback.Length)) + "..." } else { "Analyse en cours." }
                    }
                    improvement = @{
                        pt = $finalImprov_pt -join ", "
                        fr = $finalImprov_fr -join ", "
                    }
                    skills = @{ "Escuta" = $avgS; "Empatia" = [Math]::Min(100, $avgS+5); "Crises" = [Math]::Max(0, $avgS-10); "Padrões" = $avgL; "Personalização" = $avgS }
                }
            }
        }
    }
    "const users = " + ($userList | ConvertTo-Json -Depth 5) + ";" | Out-File $outputPath -Encoding utf8
}
