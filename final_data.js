const users = [
    {
        "avgScore":  42.7,
        "skills":  {
                       "PadrÃµes":  42.7,
                       "Crises":  33,
                       "Empatia":  48,
                       "PersonalizaÃ§Ã£o":  42.7,
                       "Escuta":  42.7
                   },
        "count":  6,
        "scenarios":  [
                          "Geral"
                      ],
        "improvement":  "Focar em padrÃµes LQA.",
        "name":  "Fernando Godoy",
        "lqaScore":  42.7,
        "languages":  "FR",
        "tech":  [
                     "Fluidez",
                     "Segur. Alimentar"
                 ],
        "avgDuration":  "2m 44s",
        "insights":  "Aqui estÃ¡ o debriefing da nossa interaÃ§Ã£o. ---  ðŸŒŸPontos fortes da intervenÃ§Ã£o   VocÃª demonstrou uma postura atenciosa ao se dirigir repetidamente ao cliente pelo nome, o que ajuda a criar uma..."
    },
    {
        "avgScore":  45.7,
        "skills":  {
                       "PadrÃµes":  50.3,
                       "Crises":  36,
                       "Empatia":  51,
                       "PersonalizaÃ§Ã£o":  45.7,
                       "Escuta":  45.7
                   },
        "count":  18,
        "scenarios":  [
                          "Geral"
                      ],
        "improvement":  "Focar em padrÃµes LQA.",
        "name":  "Tabajara Dias",
        "lqaScore":  50.3,
        "languages":  "FR",
        "tech":  [
                     "PadrÃ£o LQA",
                     "Fluidez",
                     "Segur. Alimentar"
                 ],
        "avgDuration":  "3m 38s",
        "insights":  "Voici le debriefing de notre conversation.  Jâ€™ai interprÃ©tÃ© le rÃ´le de Pedro, un entrepreneur brÃ©silien de cinquante-trois ans, rÃ©sidant Ã  SÃ£o Paulo, habituÃ© Ã  un niveau de luxe Ã©levÃ© et ..."
    },
    {
        "avgScore":  66.4,
        "skills":  {
                       "PadrÃµes":  67.9,
                       "Crises":  56,
                       "Empatia":  71,
                       "PersonalizaÃ§Ã£o":  66.4,
                       "Escuta":  66.4
                   },
        "count":  8,
        "scenarios":  [
                          "Geral"
                      ],
        "improvement":  "Focar em padrÃµes LQA.",
        "name":  "Lucas Lopes",
        "lqaScore":  67.9,
        "languages":  "FR",
        "tech":  [
                     "Segur. Alimentar",
                     "PadrÃ£o LQA",
                     "Fluidez"
                 ],
        "avgDuration":  "3m 38s",
        "insights":  "Aqui estÃ¡ o debriefing da nossa interaÃ§Ã£o. ________________________________________ Pontos fortes da intervenÃ§Ã£o   VocÃª conduziu a chamada com clareza e profissionalismo, iniciando com uma sauda..."
    },
    {
        "avgScore":  59.6,
        "skills":  {
                       "PadrÃµes":  62.4,
                       "Crises":  50,
                       "Empatia":  65,
                       "PersonalizaÃ§Ã£o":  59.6,
                       "Escuta":  59.6
                   },
        "count":  14,
        "scenarios":  [
                          "Geral"
                      ],
        "improvement":  "Focar em padrÃµes LQA.",
        "name":  "Gabrielli Mattos",
        "lqaScore":  62.4,
        "languages":  "FR",
        "tech":  [
                     "PadrÃ£o LQA",
                     "Fluidez",
                     "Segur. Alimentar"
                 ],
        "avgDuration":  "5m 46s",
        "insights":  "Aqui estÃ¡ o debriefing da nossa troca.  --- ðŸŒŸPontos fortes   VocÃª demonstrou clareza e objetividade ao comunicar o status do problema, explicando de forma simples as etapas que seriam seguidas co..."
    },
    {
        "avgScore":  44.1,
        "skills":  {
                       "PadrÃµes":  44.4,
                       "Crises":  34,
                       "Empatia":  49,
                       "PersonalizaÃ§Ã£o":  44.1,
                       "Escuta":  44.1
                   },
        "count":  127,
        "scenarios":  [
                          "Geral"
                      ],
        "improvement":  "Focar em padrÃµes LQA.",
        "name":  "Sophie GÃ©raud",
        "lqaScore":  44.4,
        "languages":  "FR",
        "tech":  [
                     "PadrÃ£o LQA",
                     "Fluidez",
                     "Segur. Alimentar"
                 ],
        "avgDuration":  "25m 29s",
        "insights":  " â€œVoici le dÃ©briefing de notre Ã©change.â€ Jâ€™ai jouÃ© le persona neuf â€” David, le financier new-yorkais.  {{Points forts de lâ€™intervention}} Tu as ouvert lâ€™appel rapidement et proposÃ© des..."
    },
    {
        "avgScore":  73.9,
        "skills":  {
                       "PadrÃµes":  73.9,
                       "Crises":  64,
                       "Empatia":  79,
                       "PersonalizaÃ§Ã£o":  73.9,
                       "Escuta":  73.9
                   },
        "count":  7,
        "scenarios":  [
                          "Geral"
                      ],
        "improvement":  "Focar em padrÃµes LQA.",
        "name":  "Neube Brigagao",
        "lqaScore":  73.9,
        "languages":  "FR",
        "tech":  [
                     "Fluidez",
                     "Segur. Alimentar"
                 ],
        "avgDuration":  "4m 57s",
        "insights":  "Aqui estÃ¡ o debriefing da nossa interaÃ§Ã£o. ________________________________________ Pontos fortes da intervenÃ§Ã£o   VocÃª iniciou a chamada de forma clara e educada, demonstrando prontidÃ£o para a..."
    },
    {
        "avgScore":  78.5,
        "skills":  {
                       "PadrÃµes":  78.5,
                       "Crises":  68,
                       "Empatia":  84,
                       "PersonalizaÃ§Ã£o":  78.5,
                       "Escuta":  78.5
                   },
        "count":  2,
        "scenarios":  [
                          "Geral"
                      ],
        "improvement":  "Focar em padrÃµes LQA.",
        "name":  "Matheus Barcelos",
        "lqaScore":  78.5,
        "languages":  "FR",
        "tech":  [
                     "Protocolo"
                 ],
        "avgDuration":  "8m 6s",
        "insights":  "Aqui estÃ¡ o debriefing da nossa conversa. Eu interpretei o papel de Pedro, um empresÃ¡rio de cinquenta e trÃªs anos, residente em SÃ£o Paulo, da categoria socioeconÃ´mica alta, viajando com sua espos..."
    },
    {
        "avgScore":  81.2,
        "skills":  {
                       "PadrÃµes":  81.2,
                       "Crises":  71,
                       "Empatia":  86,
                       "PersonalizaÃ§Ã£o":  81.2,
                       "Escuta":  81.2
                   },
        "count":  4,
        "scenarios":  [
                          "Geral"
                      ],
        "improvement":  "Focar em padrÃµes LQA.",
        "name":  "Enzo Hidde",
        "lqaScore":  81.2,
        "languages":  "FR",
        "tech":  "Fluidez",
        "avgDuration":  "12m 40s",
        "insights":  "Here is the debriefing of our conversation. I interpreted the role of Jean-Baptiste, a fifty-six-year-old CEO from Paris, belonging to a high socioeconomic category, traveling with his wife. Your perf..."
    },
    {
        "avgScore":  75,
        "skills":  {
                       "PadrÃµes":  75,
                       "Crises":  65,
                       "Empatia":  80,
                       "PersonalizaÃ§Ã£o":  75,
                       "Escuta":  75
                   },
        "count":  2,
        "scenarios":  [
                          "Geral"
                      ],
        "improvement":  "Focar em padrÃµes LQA.",
        "name":  "Patricia Eckhard",
        "lqaScore":  75,
        "languages":  "FR",
        "tech":  "Fluidez",
        "avgDuration":  "4m 47s",
        "insights":  "Aqui estÃ¡ o debriefing da nossa interaÃ§Ã£o. Ponto forte da intervenÃ§Ã£o   VocÃª iniciou o atendimento utilizando o nome do cliente, o que personaliza a recepÃ§Ã£o. Demonstrou prontidÃ£o ao lidar co..."
    },
    {
        "avgScore":  78,
        "skills":  {
                       "PadrÃµes":  78,
                       "Crises":  68,
                       "Empatia":  83,
                       "PersonalizaÃ§Ã£o":  78,
                       "Escuta":  78
                   },
        "count":  1,
        "scenarios":  [
                          "Geral"
                      ],
        "improvement":  "Focar em padrÃµes LQA.",
        "name":  "Jesse Henriques",
        "lqaScore":  78,
        "languages":  "FR",
        "tech":  [
                     "Protocolo"
                 ],
        "avgDuration":  "16m 23s",
        "insights":  "Aqui estÃ¡ o debriefing da nossa conversa. Eu interpretei o papel de Pedro, o empresÃ¡rio que tudo exige, com cinquenta e trÃªs anos, residente em SÃ£o Paulo, classe socioeconÃ´mica alta, e dois convi..."
    },
    {
        "avgScore":  55.6,
        "skills":  {
                       "PadrÃµes":  59.3,
                       "Crises":  46,
                       "Empatia":  61,
                       "PersonalizaÃ§Ã£o":  55.6,
                       "Escuta":  55.6
                   },
        "count":  28,
        "scenarios":  [
                          "Geral"
                      ],
        "improvement":  "Focar em padrÃµes LQA.",
        "name":  "Philippe de Langlais",
        "lqaScore":  59.3,
        "languages":  "FR",
        "tech":  [
                     "Fluidez",
                     "PadrÃ£o LQA",
                     "Segur. Alimentar"
                 ],
        "avgDuration":  "3m 36s",
        "insights":  "Aqui estÃ¡ o debriefing da nossa conversa. Eu interpretei o papel de Pedro, o empresÃ¡rio que tudo exige, com cinquenta e trÃªs anos, residente em SÃ£o Paulo, categoria socioeconÃ´mica alta, para dois..."
    }
];
