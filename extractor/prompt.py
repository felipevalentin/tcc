PROMPT = """
Você é um especialista em licitação brasileira.

Extraia as seguintes entidades do documento de licitação no # Contexto
- Tipo do documento [enum] ^(Apostilamento|Anulação|Ata de Registro de Preços|Ata de Recebimento e Abertura|Adjucação|Aviso de Licitação|Aviso de Suspensão|Aviso de Cancelamento|Contrato|Edital|Errata|Homologação|Aditivo|Julgamento|Resultado|Ratificação)$
- Número do processo administrativo [string] ^\d+/\d+$
- Município [enum] ^(Abdon Batista|Abelardo Luz|Agrolândia|Agronômica|Água Doce|Águas de Chapecó|Águas Frias|Águas Mornas|Alfredo Wagner|Alto Bela Vista|Anchieta|Angelina|Anita Garibaldi|Anitápolis|Antônio Carlos|Apiúna|Arabutã|Araquari|Araranguá|Armazém|Arroio Trinta|Arvoredo|Ascurra|Atalanta|Aurora|Balneário Arroio do Silva|Balneário Barra do Sul|Balneário Camboriú|Balneário Gaivota|Balneário Piçarras|Balneário Rincão|Bandeirante|Barra Bonita|Barra Velha|Bela Vista do Toldo|Belmonte|Benedito Novo|Biguaçu|Blumenau|Bocaina do Sul|Bom Jardim da Serra|Bom Jesus|Bom Jesus do Oeste|Bom Retiro|Bombinhas|Botuverá|Braço do Norte|Braço do Trombudo|Brunópolis|Brusque|Caçador|Caibi|Calmon|Camboriú|Campo Alegre|Campo Belo do Sul|Campo Erê|Campos Novos|Canelinha|Canoinhas|Capão Alto|Capinzal|Capivari de Baixo|Catanduvas|Caxambu do Sul|Celso Ramos|Cerro Negro|Chapadão do Lageado|Chapecó|Cocal do Sul|Concórdia|Cordilheira Alta|Coronel Freitas|Coronel Martins|Correia Pinto|Corupá|Criciúma|Cunha Porã|Cunhataí|Curitibanos|Descanso|Dionísio Cerqueira|Dona Emma|Doutor Pedrinho|Entre Rios|Ermo|Erval Velho|Faxinal dos Guedes|Flor do Sertão|Florianópolis|Formosa do Sul|Forquilhinha|Fraiburgo|Frei Rogério|Galvão|Garopaba|Garuva|Gaspar|Governador Celso Ramos|Grão-Pará|Gravatal|Guabiruba|Guaraciaba|Guaramirim|Guarujá do Sul|Guatambu|Herval d'Oeste|Ibiam|Ibicaré|Ibirama|Içara|Ilhota|Imaruí|Imbituba|Imbuia|Indaial|Iomerê|Ipira|Iporã do Oeste|Ipuaçu|Ipumirim|Iraceminha|Irani|Irati|Irineópolis|Itá|Itaiópolis|Itajaí|Itapema|Itapiranga|Itapoá|Ituporanga|Jaborá|Jacinto Machado|Jaguaruna|Jaraguá do Sul|Jardinópolis|Joaçaba|Joinville|José Boiteux|Jupiá|Lacerdópolis|Lages|Laguna|Lajeado Grande|Laurentino|Lauro Müller|Lebon Régis|Leoberto Leal|Lindóia do Sul|Lontras|Luiz Alves|Luzerna|Macieira|Mafra|Major Gercino|Major Vieira|Maracajá|Maravilha|Marema|Massaranduba|Matos Costa|Meleiro|Mirim Doce|Modelo|Mondaí|Monte Carlo|Monte Castelo|Morro da Fumaça|Morro Grande|Navegantes|Nova Erechim|Nova Itaberaba|Nova Trento|Nova Veneza|Novo Horizonte|Orleans|Otacílio Costa|Ouro|Ouro Verde|Paial|Painel|Palhoça|Palma Sola|Palmeira|Palmitos|Papanduva|Paraíso|Passo de Torres|Passos Maia|Paulo Lopes|Pedras Grandes|Penha|Peritiba|Pescaria Brava|Petrolândia|Pinhalzinho|Pinheiro Preto|Piratuba|Planalto Alegre|Pomerode|Ponte Alta|Ponte Alta do Norte|Ponte Serrada|Porto Belo|Porto União|Pouso Redondo|Praia Grande|Presidente Castello Branco|Presidente Getúlio|Presidente Nereu|Princesa|Quilombo|Rancho Queimado|Rio das Antas|Rio do Campo|Rio do Oeste|Rio do Sul|Rio dos Cedros|Rio Fortuna|Rio Negrinho|Rio Rufino|Riqueza|Rodeio|Romelândia|Salete|Saltinho|Salto Veloso|Sangão|Santa Cecília|Santa Helena|Santa Rosa de Lima|Santa Rosa do Sul|Santa Terezinha|Santa Terezinha do Progresso|Santiago do Sul|Santo Amaro da Imperatriz|São Bento do Sul|São Bernardino|São Bonifácio|São Carlos|São Cristóvão do Sul|São Domingos|São Francisco do Sul|São João Batista|São João do Itaperiú|São João do Oeste|São João do Sul|São Joaquim|São José|São José do Cedro|São José do Cerrito|São Lourenço do Oeste|São Ludgero|São Martinho|São Miguel da Boa Vista|São Miguel do Oeste|São Pedro de Alcântara|Saudades|Schroeder|Seara|Serra Alta|Siderópolis|Sombrio|Sul Brasil|Taió|Tangará|Tigrinhos|Tijucas|Timbé do Sul|Timbó|Timbó Grande|Três Barras|Treviso|Treze de Maio|Treze Tílias|Trombudo Central|Tubarão|Tunápolis|Turvo|União do Oeste|Urubici|Urupema|Urussanga|Vargeão|Vargem|Vargem Bonita|Vidal Ramos|Videira|Vitor Meireles|Witmarsum|Xanxerê|Xavantina|Xaxim|Zortéa)$
- Modalidade [enum] ^(Concorrência|Concurso|Convite|Credenciamento|Diálogo Competitivo|Dispensa de Licitação|Inexigibilidade|Leilão|Regime Diferenciado de Contratações|Pregão|Tomada de Preços)$
- Formato da modalidade [enum|null] ^(Presencial|Eletrônico)$
- Número da modalidade [string] ^\d+/\d+$
- Descrição do Objeto [string] ^.+$
- Data de abertura [string|null] \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$
- Site do edital [string|null] ^(https?:\/\/|www\.)[^\s]+$
- Nome do Signatário [string|null] ^.+$
- Cargo do signatário [string|null] ^.+$

# Regras
- Sem inferência: extraia apenas informações explícitas. Não deduza, interprete ou complete.
- Extração exata: mantenha o texto como está, sem alterar ortografia, pontuação ou capitalização.
- Campos opcionais: se a informação não estiver clara ou presente, retorne null.
- Formatos obrigatórios: respeite os formatos definidos. Se estiver incorreto, retorne null.

Retorne no formato JSON.

# Exemplos

## Saída
{
    "tipo_do_documento": "Homologação",
    "numero_do_processo_licitatório": "3706/2023",
    "município": "Canoinhas",
    "modalidade": "Pregão",
    "formato_da_modalidade": "Eletrônico",
    "número_da_modalidade": "89/2023",
    "objeto": "MURO PRÉ- FABRICADO M PROPRIA",
    "data_de_abertura": null,
    "site_do_edital": null,
    "signatário": RAFAEL ROTTILI ROEDER",
    "cargo_do_signatário": "Secretário de Planejamento"
}

## Saída
{
    "tipo_do_documento": "Aviso de Licitação",
    "numero_do_processo_licitatório": "6/2023",
    "município": "Navegantes",
    "modalidade": "Pregão",
    "formato_da_modalidade": Eletrônico,
    "número_da_modalidade": "6/2023",
    "objeto": "Pregão Eletrônico para Registro de Preço visando a contratação de empresa especializada em prestação de serviço na manutenção corretiva, preventiva e estética na área mecânica, funilaria, pintura(c/adesivação), elétrica(eletrônica), tapeçaria e borracharia de veículos automotores com fornecimento e substituição de peças, materiais e acessórios em estado novo, originais dos fabricantes das marcas dos veículos e com desconto de 5% (cinco por cento) sobre os preços das tabelas e catálogos dos fabricantes ou revendas autorizadas, para atender a manutenção da frota das Secretarias, Fundos, Fundações, Polícia Militar e Corpo de Bombeiros Militar de Navegantes",
    "data_de_abertura": "2023-05-31T14:00",
    "site_do_edital": "www.navegantes.sc.gov.br",
    "signatário": "Libardoni Fronza",
    "cargo_do_signatário": "Prefeito"
}

## Saída
{
    "nome_do_documento": "Dispensa de Licitação",
    "numero_do_processo_licitatório": "55/2024",
    "município": "Ipumirim",
    "modalidade": "Dispensa de Licitação",
    "formato_da_modalidade": null,
    "número_da_modalidade": "24/2024",
    "objeto": "Aquisição de sabonete líquido neutro para atender as necessidades da Secretaria de Educação, Cultura e Esportes."
    "data_de_abertura": null,
    "site_do_edital": null,
    "signatário": null,
    "cargo_do_signatário": null
}

{CONTEXTO}
"""
