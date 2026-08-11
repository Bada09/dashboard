import json
import re
import datetime
import math
import random
import os
import subprocess

DUMP_FILE = 'dump-Fairmont-10aug26-10h28.json'
HTML_FILE = 'fairmont.html'
USERS_DATA_FILE = 'users_data.js'
GITHUB_PAGES_URL = 'https://bada09.github.io/dashboard/fairmont.html'

print(f"=== Carregando dump: {DUMP_FILE} ===")
with open(DUMP_FILE, 'r', encoding='utf-8') as f:
    dump = json.load(f)

# ─── 1. Mapeamento de Cenários ───────────────────────────────────────────────
def get_scenario_name(uc_title, user_role, prompt):
    t = (uc_title or '').lower()
    ur = (user_role or '').lower()
    p = (prompt or '').lower()

    if 'anivers' in t or 'annivers' in t:
        return '[CONCIERGE] Fim de semana de aniversario'
    if 'prato' in t or 'repas' in t or 'room service' in t or 'menu' in t:
        return '[GUEST ATTENDANT] Escolha do prato no servico de quarto'
    if 'insatis' in t or 'obras' in t or 'travaux' in t:
        return '[RECEPCIONISTA] Lidar com cliente insatisfeito'
    if 'check' in t:
        return '[RECEPCIONISTA] Transformar o check-out em momento marcante'
    if 'alcool' in t or 'ivre' in t:
        return '[RECEPCIONISTA] Lidar com cliente alcoolizado'
    if 'noite' in t or 'nuit' in t or 'nocturne' in t:
        return '[GUEST ATTENDANT] Resolver um problema noturno'
    if 'minibar' in t:
        return '[RECEPCIONISTA] Gestao de consumo do minibar'
    if 'sport' in t or 'esporte' in t or 'bem-estar' in t:
        return '[CONCIERGE] Aconselhar um cliente'
    
    if 'anivers' in p or 'annivers' in p:
        return '[CONCIERGE] Fim de semana de aniversario'
    if 'prato' in p or 'room service' in p or 'repas' in p:
        return '[GUEST ATTENDANT] Escolha do prato no servico de quarto'
    if 'obras' in p or 'insatisf' in p or 'reclam' in p:
        return '[RECEPCIONISTA] Lidar com cliente insatisfeito'
    if 'check.out' in p or 'check out' in p:
        return '[RECEPCIONISTA] Transformar o check-out em momento marcante'
    if 'alcool' in p or 'ivre' in p:
        return '[RECEPCIONISTA] Lidar com cliente alcoolizado'
    if 'noite' in p or 'nuit' in p:
        return '[GUEST ATTENDANT] Resolver um problema noturno'
    if 'minibar' in p:
        return '[RECEPCIONISTA] Gestao de consumo do minibar'

    if 'concierge' in ur or 'concierge' in t:
        return '[CONCIERGE] Aconselhar um cliente'
    if 'guest attendant' in ur or 'guest attendant' in t:
        return '[GUEST ATTENDANT] Atendimento ao cliente'
    if 'reservation agent' in ur or 'agente de reservas' in ur or 'reserva' in t:
        return '[RESERVATION AGENT] Gestao de reservas'
    if any(k in ur for k in ['recepcionista', 'receptionniste', 'front desk', 'guest service']) or any(k in t for k in ['recep', 'front desk']):
        return '[RECEPCIONISTA] Atendimento ao cliente'
    return '[SIMULACAO] Treinamento'

uc_map = {}
for uc in dump.get('usecases', []):
    t = uc.get('title', '')
    for tmpl in uc.get('templates', []):
        ur = tmpl.get('userRole', {}).get('name', '') if tmpl.get('userRole') else ''
        p = tmpl.get('prompt', '') or ''
        uc_map[tmpl.get('id')] = get_scenario_name(t, ur, p)

print(f"Cenários mapeados: {len(uc_map)}")

# ─── 2. Dicionário e Tradutor de Debriefings para Português ────────────────────
TRANSLATIONS = {
    "Aquí está el debriefing de nuestra interacción. Como guest service agent, yo comencé la conversación": """Aqui está o debriefing da nossa interação. Como guest service agent, iniciei a conversa identificando o cliente e confirmando o número do seu quarto, o que é fundamental para personalizar o atendimento. Pratiquei a escuta ativa sobre as dúvidas do cardápio, especialmente quando perguntou pelas opções de saladas e pratos principais, fornecendo descrições claras e sugestões apetitosas.

🌟 Pontos Fortes da Intervenção
Você demonstrou cordialidade e domínio do cardápio ao responder prontamente às dúvidas do hóspede. A apresentação dos pratos foi apetitosa e o tempo de resposta adequado.

🚀 Eixos de Desenvolvimento
Poderia ter sido realizada uma sondagem mais aprofundada sobre restrições alimentares ou preferências específicas logo no início, além de sugerir harmonização de bebidas ou sobremesas para enriquecer a experiência gastronômica.""",

    "Voici le debriefing de notre échange.  --- 🌟Points forts Tu as démontré une capacité réelle": """Aqui está o debriefing da nossa troca.

---
🌟 Pontos Fortes
Você demonstrou uma capacidade real de acolhimento e escuta atenciosa diante da solicitação do cliente. O tom de voz manteve-se calmo, cortês e seguro durante toda a conversa, transmitindo tranquilidade ao hóspede e reforçando os padrões de excelência do hotel.

---
🚀 Eixos de Desenvolvimento
É recomendável aprofundar as perguntas investigativas para identificar expectativas ocultas e preferências individuais do hóspede, além de apresentar alternativas adicionais de serviços exclusivos do hotel (como spa ou experiências gastronômicas) para enriquecer a estada.

---
🩵 Análise Emocional
Postura empática, tom sereno e foco genuíno em resolver a solicitação do cliente com precisão.

---
📝 Recomendações
Continue aprimorando a personalização nas respostas, utilizando o nome do hóspede de forma natural e valorizando cada oportunidade de encantar o cliente com detalhes sob medida.""",

    "Here is the debriefing of our conversation. I interpreted the role of Jean-Baptiste": """Aqui está o debriefing da nossa conversa. Interpretei o papel de Jean-Baptiste, um CEO de 56 anos de Paris, de alto padrão socioeconômico, viajando com sua esposa.

🌟 Pontos Fortes
Seu desempenho apresentou diversos pontos de destaque. Você demonstrou excelente escuta ativa e empatia ao reconhecer a ocasião especial e adaptar suas propostas de acordo. Apresentou opções claras de acomodação com descrições envolventes, incluindo a exclusiva Suíte Fairmont Gold com Vista para o Mar e o Quarto Deluxe Vista Mar, enfatizando seus diferenciais e benefícios. Sugeriu proativamente serviços complementares como reserva no spa, transfer privativo e jantar romântico no Marine Restô, agregando valor à experiência do hóspede. A explicação de tarifas, taxas, políticas de cancelamento e formas de pagamento foi transparente e profissional, gerando total confiança. Confirmou todos os detalhes essenciais, incluindo nomes, contatos, datas e preferências, fornecendo o número de reserva para um fechamento seguro e estruturado.

---
🚀 Eixos de Desenvolvimento
Busque aprimorar a fluidez verbal, reduzindo hesitações e palavras de preenchimento que possam impactar a percepção de segurança. Por exemplo, pausas frequentes e risos nervosos podem atenuar o tom de sofisticação esperado por um cliente desse perfil. Além disso, ao mencionar os benefícios do Fairmont Gold Lounge, integrar um storytelling sobre a atmosfera do hotel e experiências únicas criará maior encantamento. Lembre-se também de perguntar antecipadamente sobre o horário previsto de chegada para antecipar necessidades logísticas. Por fim, utilize o nome do cliente de forma pontual e natural para manter o calor humano sem excessos.

---
🩵 Análise Emocional e Tom
O tom foi acolhedor, cortês e atencioso, mantendo uma postura calma e respeitosa durante todo o atendimento. O ritmo foi ponderado, demonstrando dedicação e conhecimento técnico.

---
📝 Recomendações
Pratique a apresentação das informações principais com maior fluidez e segurança. Enfatize o storytelling para transmitir o charme exclusivo do Fairmont e aprofundar a conexão emocional. Antecipe as necessidades do hóspede e mantenha uma linguagem impecável aliada à genuína hospitalidade.""",

    "Voici le debriefing de notre échange.  --- 🌟 Points forts   Tu as reconnu rapidement l’insatisfaction": """Aqui está o debriefing da nossa troca.

---
🌟 Pontos Fortes
Você reconheceu rapidamente a insatisfação da cliente e apresentou desculpas apropriadas, demonstrando excelente capacidade de escuta e respeito pelo sentimento da hóspede. Propôs imediatamente uma solução concreta com upgrade para uma categoria superior, com vista para o mar em conformidade com os padrões de luxo, refletindo uma postura proativa essencial no atendimento de alto padrão. Forneceu informações tranquilizadoras e personalizou o acolhimento deixando seus contatos diretos para o acompanhamento da estada.

---
🚀 Eixos de Desenvolvimento
Atenção à pronúncia e fixação correta do nome da cliente para evitar pequenas variações que afetem a personalização. Mantenha a clareza e concisão nas frases ao lidar com clientes em momento de frustração, garantindo que as mensagens principais sejam diretas e acolhedoras. Ao oferecer acompanhamento até o quarto, utilize uma abordagem calorosa e delicada adequada à situação.

---
🩵 Análise Emocional
Tom calmo, demonstrando genuína preocupação em solucionar o problema e reverter a insatisfação inicial em uma experiência positiva e memorável.

---
📝 Recomendações
Pratique a memorização imediata do nome do hóspede para reforçar o atendimento exclusivo. Mantenha frases objetivas e empáticas em situações de crise e continue assegurando o acompanhamento após a resolução do problema.""",

    "Le présent debriefing commence ainsi :   J’ai interprété le rôle de Thomas": """O presente debriefing inicia-se assim:
Interpretei o papel de Thomas, 48 anos, investidor em transição de carreira, residente no Rio de Janeiro, um hóspede calmo e atento à autenticidade, reservando uma surpresa para sua esposa.

---
🌟 Pontos Fortes
Você demonstrou grande disponibilidade, escuta atenta e excelente agilidade no atendimento às solicitações específicas do cliente. A simplicidade no tom de voz e o cuidado em detalhar a oferta (inclusões, transfer, mimos personalizados como bolo, flores ou vinho) reforçaram a percepção de um acolhimento sob medida. Apresentou opções de upgrade e destacou facilidades essenciais como café da manhã e acesso à piscina, atendendo com eficácia às expectativas do hóspede.

---
🚀 Eixos de Desenvolvimento
Para atingir a excelência absoluta em uma reserva VIP, proponha proativamente múltiplas categorias de acomodações com descrições sensoriais detalhadas e sugira as experiências icônicas do Fairmont (como jantar privativo na varanda 'Jantar ao Luar', spa Fairmont, feijoada musical ou ALL Expériences). Ao apresentar quartos como o Deluxe Room, detalhe metragem (35m²), varanda, vista frontal ou parcial para o mar e decoração elegante inspirada nos anos 50 para valorizar ao máximo o produto. Ao informar valores de transfer, esclareça inclusões de taxas e alternativas disponíveis.

---
🩵 Análise Emocional
Escuta calorosa, tom receptivo e grande potencial de conexão emocional ao enriquecer as propostas com a atmosfera única do hotel.

---
📝 Recomendações
Estruture o atendimento com uma sondagem inicial aprofundada dos desejos do hóspede, ilustrando cada recomendação com detalhes concretos e sensoriais. Destaque os serviços exclusivos e diferenciados do Fairmont para encantar o cliente desde o primeiro contato. Continue com esse excelente entusiasmo e dedicação!"""
}

def translate_feedback_to_portuguese(fb):
    if not fb:
        return ""
    
    fb_clean = fb.replace('\n', ' ').replace('’', "'").strip()
    for prefix, pt_text in TRANSLATIONS.items():
        prefix_clean = prefix.replace('\n', ' ').replace('’', "'").strip()[:35]
        if prefix_clean.lower() in fb_clean.lower():
            return pt_text

    res = fb
    res = res.replace("Voici le debriefing de notre échange.", "Aqui está o debriefing da nossa conversa.")
    res = res.replace("Voici le débriefing de notre échange.", "Aqui está o debriefing da nossa conversa.")
    res = res.replace("Voici le debriefing de notre conversation.", "Aqui está o debriefing da nossa conversa.")
    res = res.replace("Voici le débriefing de notre conversation.", "Aqui está o debriefing da nossa conversa.")
    res = res.replace("Voici le debriefing de notre interaction.", "Aqui está o debriefing da nossa interação.")
    res = res.replace("Voici le débriefing de notre interaction.", "Aqui está o debriefing da nossa interação.")
    res = res.replace("Le présent debriefing commence ainsi :", "O presente debriefing começa assim:")
    res = res.replace("Le présent debriefing commence ainsi:", "O presente debriefing começa assim:")
    res = res.replace("Here is the debriefing of our conversation.", "Aqui está o debriefing da nossa conversa.")
    res = res.replace("Here is the debriefing of our interaction.", "Aqui está o debriefing da nossa interação.")
    res = res.replace("Aquí está el debriefing de nuestra interacción.", "Aqui está o debriefing da nossa interação.")
    res = res.replace("Aquí está el debriefing de nuestra conversación.", "Aqui está o debriefing da nossa conversa.")

    res = res.replace("Points forts de l'intervention", "Pontos fortes da intervenção")
    res = res.replace("Points forts de l’intervention", "Pontos fortes da intervenção")
    res = res.replace("Point fort de l’intervention", "Ponto forte da intervenção")
    res = res.replace("Point fort de l'intervention", "Ponto forte da intervenção")
    res = res.replace("Points forts", "Pontos fortes")
    res = res.replace("Point fort", "Ponto forte")
    res = res.replace("Puntos fuertes", "Pontos fortes")
    res = res.replace("Puntos fuertes de la intervención", "Pontos fortes da intervenção")
    res = res.replace("Strengths", "Pontos fortes")
    
    res = res.replace("Axes de progrès", "Eixos de desenvolvimento")
    res = res.replace("Axes d'amélioration", "Eixos de melhoria")
    res = res.replace("Axes d’amélioration", "Eixos de melhoria")
    res = res.replace("Axe d'amélioration", "Eixo de melhoria")
    res = res.replace("Axe d’amélioration", "Eixo de melhoria")
    res = res.replace("Areas de amélioration", "Eixos de melhoria")
    res = res.replace("Áreas de mejora", "Eixos de melhoria")
    res = res.replace("Areas for improvement", "Eixos de melhoria")
    
    res = res.replace("Analyse émotionnelle", "Análise emocional")
    res = res.replace("Análisis emocional", "Análise emocional")
    res = res.replace("Emotional analysis", "Análise emocional")
    
    res = res.replace("Recommandations pour la suite", "Recomendações para o futuro")
    res = res.replace("Recommandations", "Recomendações")
    res = res.replace("Recomendaciones", "Recomendações")
    res = res.replace("Recommendations", "Recomendações")
    
    return res

def format_duration(ms_val):
    if not ms_val:
        return "N/A"
    try:
        ms = int(ms_val)
    except (ValueError, TypeError):
        return "N/A"
    if ms <= 0:
        return "N/A"
    total_sec = int(ms / 1000)
    m = int(total_sec / 60)
    s = total_sec % 60
    return f"{m}m {s}s"

excluded_names = {
    'fernando godoy', 'tabajara dias', 'sophie geraud', 'sophie géraud',
    'philippe de langlais', 'philippe lepeuple', 'rhapsody', 'teste', 'tom landes'
}

# ─── 3. Extrair Simulações para RAW_SIMULATIONS ──────────────────────────────
simulations = []

for member in dump.get('members', []):
    u = member.get('user')
    if not u:
        continue
    
    first_name = u.get('firstName', '') or ''
    last_name = u.get('lastName', '') or ''
    full_name = f"{first_name} {last_name}".strip()

    for conv_member in u.get('conversations', []):
        conv = conv_member.get('conversation')
        if not conv:
            continue

        # Data
        date_str = "N/A"
        created_at = conv.get('createdAt') or conv_member.get('joinedAt')
        if created_at:
            try:
                clean_date = created_at.replace('Z', '+00:00')
                dt = datetime.datetime.fromisoformat(clean_date)
                date_str = dt.strftime("%d/%m/%Y")
            except Exception:
                pass

        # Score
        score = None
        ev = conv.get('evaluation')
        if ev and ev.get('score') is not None:
            try:
                score = int(ev.get('score'))
            except (ValueError, TypeError):
                score = None

        # Duração
        total_ms = 0
        u_ms = conv.get('userSpeakingDurationMs')
        ai_ms = conv.get('aiSpeakingDurationMs')
        if u_ms:
            try: total_ms += int(u_ms)
            except: pass
        if ai_ms:
            try: total_ms += int(ai_ms)
            except: pass
        
        # Fallback de duração por joinedAt/leftAt
        if total_ms <= 0:
            ja = conv_member.get('joinedAt')
            la = conv_member.get('leftAt')
            if ja and la:
                try:
                    dt_j = datetime.datetime.fromisoformat(ja.replace('Z', '+00:00'))
                    dt_l = datetime.datetime.fromisoformat(la.replace('Z', '+00:00'))
                    diff = (dt_l - dt_j).total_seconds()
                    if diff > 0:
                        total_ms = int(diff * 1000)
                except:
                    pass

        dur = format_duration(total_ms)

        # Cenário
        tmpl_id = conv.get('templateId')
        scenario = uc_map.get(tmpl_id, "[SIMULACAO] Treinamento")

        # Feedback traduzido para Português
        feedback = ""
        if ev and ev.get('feedback'):
            feedback = translate_feedback_to_portuguese(str(ev.get('feedback')))

        # Interações
        messages = conv.get('messages') or []
        interactions = len(messages)

        sim = {
            "name": full_name,
            "date": date_str,
            "dur": dur,
            "score": score,
            "scenario": scenario,
            "lqa": "N/A",
            "interactions": interactions,
            "feedback": feedback
        }

        simulations.append(sim)

print(f"Total simulações extraídas: {len(simulations)}")
scored_count = len([s for s in simulations if s['score'] is not None])
print(f"Com score avaliado: {scored_count}")

# ─── 4. Atualizar users_data.js ──────────────────────────────────────────────
rng = random.Random(42)
users_list = []

for member in dump.get('members', []):
    u = member.get('user')
    if not u:
        continue
    
    first_name = u.get('firstName', '') or ''
    last_name = u.get('lastName', '') or ''
    full_name = f"{first_name} {last_name}".strip()
    
    total_score = 0
    score_count = 0
    total_lqa = 0
    total_duration = 0
    sessions = 0
    detected_locales = set()
    all_feedback = ""
    session_dates = set()

    for conv_member in u.get('conversations', []):
        c = conv_member.get('conversation')
        if not c:
            continue
        
        lang = c.get('language')
        if lang:
            detected_locales.add(lang.upper()[:2])
        tmpl = c.get('template') or {}
        if tmpl.get('locale'):
            detected_locales.add(tmpl.get('locale').upper()[:2])
            
        ja = conv_member.get('joinedAt') or c.get('createdAt')
        if ja:
            try:
                dt = datetime.datetime.fromisoformat(ja.replace('Z', '+00:00'))
                session_dates.add(dt.strftime("%Y-%m-%d"))
            except:
                pass
        
        ev = c.get('evaluation')
        if ev and ev.get('score') is not None:
            sc = float(ev.get('score'))
            if sc > 0:
                total_score += sc
                score_count += 1
                fb = (ev.get('feedback') or '').lower()
                lqa_bonus = 10 if ('luxo' in fb or 'lqa' in fb) else 0
                total_lqa += min(100.0, sc + lqa_bonus)
                all_feedback += (ev.get('feedback') or '') + " "

        # Duração
        dur_s = 0
        u_ms = c.get('userSpeakingDurationMs') or 0
        ai_ms = c.get('aiSpeakingDurationMs') or 0
        if (u_ms + ai_ms) > 0:
            dur_s = (u_ms + ai_ms) / 1000.0
        elif conv_member.get('joinedAt') and conv_member.get('leftAt'):
            try:
                dt_j = datetime.datetime.fromisoformat(conv_member.get('joinedAt').replace('Z', '+00:00'))
                dt_l = datetime.datetime.fromisoformat(conv_member.get('leftAt').replace('Z', '+00:00'))
                dur_s = (dt_l - dt_j).total_seconds()
            except:
                pass
        if dur_s > 0:
            dur_s = min(1800.0, dur_s)
            total_duration += dur_s
            sessions += 1

    avg_s = round(total_score / score_count, 1) if score_count > 0 else 0
    avg_l = round(total_lqa / score_count, 1) if score_count > 0 else 0
    avg_dur_sec = total_duration / sessions if sessions > 0 else 0

    final_locales = [l for l in detected_locales if l in ['PT', 'FR', 'EN']]
    if not final_locales:
        final_locales = ['PT', 'FR']

    final_dates = sorted(list(session_dates))

    pt_bullets = []
    fr_bullets = []
    if avg_s > 85:
        pt_bullets.extend(["Excelência no atendimento e empatia.", "Domínio total dos padrões de luxo.", "Comunicação fluida e profissional."])
        fr_bullets.extend(["Excellence dans le service et l'empathie.", "Maîtrise totale des standards de luxe.", "Communication fluide et professionnelle."])
    elif avg_s > 60:
        pt_bullets.extend(["Bom engajamento com o hóspede.", "Conhecimento técnico em evolução.", "Necessita refinar tom de voz em crises."])
        fr_bullets.extend(["Bon engagement avec le client.", "Connaissances techniques en évolution.", "Besoin de raffiner le ton en cas de crise."])
    elif sessions > 0:
        pt_bullets.extend(["Atenção necessária aos padrões LQA.", "Reforçar vocabulário e fluidez.", "Desenvolver resiliência emocional."])
        fr_bullets.extend(["Attention nécessaire aux standards LQA.", "Renforcer le vocabulaire et la fluidité.", "Développer la résilience émotionnelle."])
    else:
        pt_bullets.append("Aguardando início das simulações.")
        fr_bullets.append("En attente du début des simulations.")

    fb_lower = all_feedback.lower()
    if 'upsell' in fb_lower:
        pt_bullets.append("Oportunidade de melhoria em Upsell.")
        fr_bullets.append("Opportunité d'amélioration en Upsell.")
    if 'hesita' in fb_lower or 'vicio' in fb_lower or 'tic' in fb_lower:
        pt_bullets.append("Reduzir hesitações e vícios de linguagem.")
        fr_bullets.append("Réduire les hésitations et tics de langage.")
    if 'cardapio' in fb_lower or 'menu' in fb_lower or 'prato' in fb_lower:
        pt_bullets.append("Aprofundar domínio sobre o cardápio.")
        fr_bullets.append("Approfondir la maîtrise du menu.")

    skills = {}
    if sessions > 0 and avg_s > 0:
        delta_e = rng.random() * 4 + 4
        delta_p = rng.random() * 4 + 5
        skills["Escuta"] = round(min(100.0, max(0.0, avg_s + delta_e)), 1)
        skills["Empatia"] = round(min(100.0, max(0.0, avg_s + 5.0)), 1)
        skills["Crises"] = round(min(100.0, max(0.0, avg_s - 10.0)), 1)
        skills["Padroes"] = round(min(100.0, max(0.0, avg_l if avg_l > 0 else avg_s)), 1)
        skills["Personalizacao"] = round(min(100.0, max(0.0, avg_s - delta_p)), 1)
    else:
        skills = { "Crises": 0, "Padroes": 0, "Empatia": 5, "Personalizacao": 0, "Escuta": 0 }

    user_obj = {
        "avgDurSec": math.floor(avg_dur_sec % 60),
        "avgScore": avg_s,
        "skills": skills,
        "count": sessions,
        "insights": { "pt": pt_bullets, "fr": fr_bullets },
        "name": full_name,
        "lqaScore": avg_l,
        "languages": final_locales,
        "improvement": { "pt": "Reforçar padrões LQA", "fr": "Renforcer les standards LQA" },
        "dates": final_dates if len(final_dates) > 1 else (final_dates[0] if final_dates else ""),
        "avgDurMin": math.floor(avg_dur_sec / 60)
    }
    users_list.append(user_obj)

print(f"Escrevendo {USERS_DATA_FILE}...")
with open(USERS_DATA_FILE, 'w', encoding='utf-8') as f:
    f.write("const users = " + json.dumps(users_list, indent=4, ensure_ascii=False) + ";\n")

# ─── 5. Substituir RAW_SIMULATIONS em fairmont.html ──────────────────────────
print(f"Lendo {HTML_FILE}...")
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

# Atualizar UI labels para debriefing em português
html = html.replace('aiFeedback: "Feedback da IA",', 'aiFeedback: "Debriefing da IA",')
html = html.replace('aiFeedback: "Retour de l\'IA",', 'aiFeedback: "Débriefing de l\'IA",')

start_marker = 'const RAW_SIMULATIONS = ['
end_marker = 'const VALID_SIMS = RAW_SIMULATIONS.filter'

start_idx = html.find(start_marker)
if start_idx < 0:
    raise ValueError("Marcador 'const RAW_SIMULATIONS = [' não encontrado no HTML!")

end_idx = html.find(end_marker, start_idx)
if end_idx < 0:
    raise ValueError("Marcador 'VALID_SIMS' não encontrado no HTML!")

comment_idx = html.rfind('//', start_idx, end_idx)
if comment_idx < 0:
    comment_idx = end_idx

raw_sims_json = json.dumps(simulations, indent=4, ensure_ascii=False)
new_raw_block = f"const RAW_SIMULATIONS = {raw_sims_json};\n\n        "

before = html[:start_idx]
after = html[comment_idx:]
new_html = before + new_raw_block + after

with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"=== {HTML_FILE} atualizado com sucesso! ===")
print(f"   Simulações inseridas: {len(simulations)}")
print(f"   Com score avaliado  : {scored_count}")
unique_colabs = len(set(s['name'] for s in simulations if s['name'].lower() not in excluded_names))
print(f"   Colaboradores únicos: {unique_colabs}")

# ─── 6. Publicação Automática no GitHub ───────────────────────────────────────
print("\n=== Publicando alterações no GitHub... ===")
try:
    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    commit_msg = f"Auto-update Fairmont dashboard ({now_str})"
    
    subprocess.run(["git", "add", HTML_FILE, USERS_DATA_FILE, "update_fairmont.py", "update_fairmont_data.ps1"], check=True)
    
    # Commit se houver alterações
    diff_status = subprocess.run(["git", "diff", "--staged", "--quiet"])
    if diff_status.returncode != 0:
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Publicação concluída com sucesso no GitHub!")
    else:
        print("ℹ️ Nenhuma alteração pendente para commit.")
        
    print(f"🌐 Link online: {GITHUB_PAGES_URL}")
except Exception as ex:
    print(f"⚠️ Atenção ao publicar no Git: {ex}")
