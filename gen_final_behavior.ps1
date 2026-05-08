$filePath = "c:\Users\badad\Dropbox\rhapsody Latam\Clientes\Fairmont\Stats\Dump-Fairmont-06 mai 26 -21h23.json"
$outputPath = "c:\Users\badad\Downloads\metlife proposta\final_behavioral_data.js"

if (Test-Path $filePath) {
    $raw = Get-Content $filePath -Raw | ConvertFrom-Json
    $userList = @()
    foreach ($member in $raw.members) {
        $u = $member.user
        if ($u.conversations.Count -gt 0) {
            $totalScore = 0; $scoreCount = 0; $totalLqa = 0; $totalDuration = 0; $sessions = 0; 
            $detectedLocales = @()
            $techInsights = @()
            $allFeedback = ""
            $scenarios = @()
            
            foreach ($conv in $u.conversations) {
                $eval = $conv.conversation.evaluation
                $template = $conv.conversation.template
                
                # Base locale from template
                if ($template.locale) { $detectedLocales += $template.locale }
                
                if ($eval) {
                    $fb = $eval.feedback.ToLower()
                    # Detect additional languages from feedback
                    if ($fb -like "*português*" -or $fb -like "*portugues*") { $detectedLocales += "PT-BR" }
                    if ($fb -like "*francês*" -or $fb -like "*frances*" -or $fb -like "*français*") { $detectedLocales += "FR" }
                    if ($fb -like "*inglês*" -or $fb -like "*ingles*" -or $fb -like "*english*") { $detectedLocales += "EN" }
                    
                    if ($eval.score -gt 0) {
                        $totalScore += $eval.score; $scoreCount++;
                        $lqaB = if ($fb -like "*luxo*" -or $fb -like "*lqa*") { 10 } else { 0 }
                        $totalLqa += [Math]::Min(100, $eval.score + $lqaB)
                        
                        if ($fb -like "*upsell*") { $techInsights += "Upsell" }
                        if ($fb -like "*alergia*") { $techInsights += "Segur. Alimentar" }
                        if ($fb -like "*luxo*") { $techInsights += "Padrão LQA" }
                        if ($fb -like "*hesitação*") { $techInsights += "Fluidez" }
                        
                        $allFeedback += $eval.feedback + " "
                    }
                }
                
                if ($template.name) { $scenarios += $template.name }
                if ($conv.joinedAt -and $conv.leftAt) {
                    $totalDuration += ([DateTime]::Parse($conv.leftAt) - [DateTime]::Parse($conv.joinedAt)).TotalSeconds
                    $sessions++
                }
            }
            
            if ($sessions -gt 0) {
                $avgS = if ($scoreCount -gt 0) { [Math]::Round($totalScore / $scoreCount, 1) } else { 0 }
                $avgL = if ($scoreCount -gt 0) { [Math]::Round($totalLqa / $scoreCount, 1) } else { 0 }
                
                # Cleanup locales
                $finalLocales = @()
                foreach($loc in ($detectedLocales | Select-Object -Unique)) {
                    if ($loc -like "FR*") { $finalLocales += "FR" }
                    elseif ($loc -like "PT*") { $finalLocales += "PT" }
                    elseif ($loc -like "EN*") { $finalLocales += "EN" }
                    else { $finalLocales += $loc }
                }
                $finalLocales = $finalLocales | Select-Object -Unique

                $summary = if ($allFeedback.Length -gt 20) { 
                    $clean = $allFeedback -replace '[\r\n\t]', ' ' -replace '"', "'"
                    if ($clean.Length -gt 400) { $clean.Substring(0, 400) + "..." } else { $clean }
                } else { "Resumo em processamento." }

                $userList += @{
                    name = "$($u.firstName) $($u.lastName)"; avgScore = $avgS; lqaScore = $avgL; count = $sessions; 
                    languages = $finalLocales; scenarios = ($scenarios | Select-Object -Unique | Select-Object -First 3)
                    avgDuration = "$([Math]::Floor($totalDuration / $sessions / 60))m $([Math]::Floor($totalDuration / $sessions % 60))s"
                    tech = ($techInsights | Group-Object | Sort-Object Count -Descending | Select-Object -First 3 -ExpandProperty Name)
                    insights = $summary
                    improvement = "Trabalhar a fluidez verbal e aderência aos processos LQA.";
                    skills = @{ "Escuta" = $avgS; "Empatia" = [Math]::Min(100, $avgS+5); "Crises" = [Math]::Max(0, $avgS-10); "Padrões" = $avgL; "Personalização" = $avgS }
                }
            }
        }
    }
    "const users = " + ($userList | ConvertTo-Json -Depth 5) + ";" | Out-File $outputPath -Encoding utf8
}
