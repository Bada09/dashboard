$filePath = "c:\Users\badad\Dropbox\rhapsody Latam\Clientes\Fairmont\Stats\Dump-Fairmont-06 mai 26 -21h23.json"
$outputPath = "c:\Users\badad\Downloads\metlife proposta\users_data.js"

if (Test-Path $filePath) {
    $raw = Get-Content $filePath -Raw | ConvertFrom-Json
    $userList = @()

    foreach ($member in $raw.members) {
        $u = $member.user
        $totalScore = 0; $scoreCount = 0; $totalLqa = 0; $totalDuration = 0; $sessions = 0
        $detectedLocales = @()
        $allFeedback = ""
        $sessionDates = @()

        foreach ($conv in $u.conversations) {
            $c = $conv.conversation
            if ($c.language) { $detectedLocales += $c.language.ToUpper().Substring(0,2) }
            if ($c.template.locale) { $detectedLocales += $c.template.locale.ToUpper().Substring(0,2) }
            if ($conv.joinedAt) { try { $sessionDates += [DateTime]::Parse($conv.joinedAt).ToString("yyyy-MM-dd") } catch {} }

            if ($c.evaluation) {
                $eval = $c.evaluation
                if ($eval.score -gt 0) {
                    $totalScore += $eval.score; $scoreCount++
                    $totalLqa += [Math]::Min(100, $eval.score + 8)
                    $allFeedback += $eval.feedback + " "
                }
            }
            if ($conv.joinedAt -and $conv.leftAt) {
                try {
                    $dur = ([DateTime]::Parse($conv.leftAt) - [DateTime]::Parse($conv.joinedAt)).TotalSeconds
                    if ($dur -gt 0) { $totalDuration += $dur; $sessions++ }
                } catch {}
            }
        }

        $avgS = if ($scoreCount -gt 0) { [Math]::Round($totalScore / $scoreCount, 1) } else { 0 }
        $avgL = if ($scoreCount -gt 0) { [Math]::Round($totalLqa / $scoreCount, 1) } else { 0 }
        $avgDurSec = if ($sessions -gt 0) { $totalDuration / $sessions } else { 0 }
        
        $finalLocales = ($detectedLocales | Where-Object { $_ -match "PT|FR|EN" } | Select-Object -Unique)
        if ($finalLocales.Count -eq 0) { $finalLocales = @("FR") }
        
        $finalDates = ($sessionDates | Select-Object -Unique | Sort-Object)

        # Use variables without accents in the script, and handle the text carefully
        $ptBullets = @(); $frBullets = @()
        
        if ($avgS -gt 85) {
            $ptBullets += "Excelencia no atendimento e empatia."; $frBullets += "Excellence dans le service et l'empathie."
            $ptBullets += "Dominio total dos padroes de luxo."; $frBullets += "Maitrise totale des standards de luxe."
            $ptBullets += "Comunicacao fluida e profissional."; $frBullets += "Communication fluide et professionnelle."
        } elseif ($avgS -gt 60) {
            $ptBullets += "Bom engajamento com o hospede."; $frBullets += "Bon engagement avec le client."
            $ptBullets += "Conhecimento tecnico em evolucao."; $frBullets += "Connaissances techniques en evolution."
            $ptBullets += "Necessita refinar tom de voz em crises."; $frBullets += "Besoin de raffiner le ton en cas de crise."
        } elseif ($sessions -gt 0) {
            $ptBullets += "Atencao necessaria aos padroes LQA."; $frBullets += "Attention necessaire aux standards LQA."
            $ptBullets += "Reforcar vocabulario e fluidez."; $frBullets += "Renforcer le vocabulaire et la fluidité."
            $ptBullets += "Desenvolver resiliencia emocional."; $frBullets += "Developper la resilience emotionnelle."
        } else {
            $ptBullets += "Aguardando inicio das simulacoes."; $frBullets += "En attente du debut des simulations."
        }

        $fbLower = $allFeedback.ToLower()
        if ($fbLower -match "upsell") { $ptBullets += "Oportunidade de melhoria em Upsell."; $frBullets += "Opportunite d'amelioration en Upsell." }
        if ($fbLower -match "hesita|vicio") { $ptBullets += "Reduzir hesitacoes e vicios de linguagem."; $frBullets += "Reduire les hesitations et tics de langage." }
        if ($fbLower -match "cardapio|menu") { $ptBullets += "Aprofundar dominio sobre o cardapio."; $frBullets += "Approfondir la maitrise du menu." }

        $userList += @{
            name        = "$($u.firstName) $($u.lastName)".Trim()
            avgScore    = $avgS
            lqaScore    = $avgL
            count       = $sessions
            languages   = $finalLocales
            avgDurMin   = [Math]::Floor($avgDurSec / 60)
            avgDurSec   = [Math]::Floor($avgDurSec % 60)
            dates       = $finalDates
            insights    = @{ pt = $ptBullets; fr = $frBullets }
            improvement = @{ pt = "Reforcar padroes LQA"; fr = "Renforcer les standards LQA" }
            skills      = @{
                Escuta = $avgS
                Empatia = [Math]::Min(100, $avgS + 5)
                Crises = [Math]::Max(0, $avgS - 10)
                Padroes = $avgL
                Personalizacao = $avgS
            }
        }
    }

    $json = $userList | ConvertTo-Json -Depth 6
    $content = "const users = $json;"
    
    # Force UTF8 without BOM using .NET to avoid the Ã bugs
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($outputPath, $content, $utf8NoBom)
}
