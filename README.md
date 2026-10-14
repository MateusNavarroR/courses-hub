# Courses Hub

Dashboard de cursos com experiência inspirada na Udemy. Repositório inicialmente privado; implantação planejada no oracle-vps.

## Estado

Pesquisa inicial e escopo proposto. Aplicação ainda não implementada ou implantada. Dois cursos serão cadastrados quando seu formato e localização forem definidos.

## Escopo inicial proposto

- Catálogo com capas, busca e filtros.
- Cadastro de cursos, módulos e aulas.
- Página do curso e player com lista lateral de aulas.
- Progresso de estudo e continuar de onde parou.
- Login e interface responsiva em português.
- Vídeos e materiais fora do Git.

## Projetos pesquisados

| Projeto | Recursos e adequação |
| --- | --- |
| [LearnHouse](https://github.com/learnhouse/learnhouse) | Interface moderna, editor, cursos e dashboard; Next.js e FastAPI, com PostgreSQL e Redis. Candidato para adaptar uma plataforma pronta. Núcleo AGPL-3.0; pagamentos e SSO são Enterprise. |
| [Frappe Learning](https://github.com/frappe/lms) | Cursos, capítulos, aulas, exercícios e certificados; usa Frappe e Vue. Indicado para gestão de ensino mais completa. AGPL-3.0. |
| [CourseLit](https://github.com/codelitdev/courselit) | Criação e venda de cursos, gestão de alunos e integração Stripe; mais orientado a negócios de cursos. [Documentação de hospedagem](https://docs.courselit.app/self-hosting/introduction/). |

Pesquisa realizada em 14/10/2026 a partir dos repositórios e da documentação oficial. Avaliação documental; as plataformas ainda não foram executadas ou comparadas visualmente no servidor.

## Infraestrutura observada

Acesso SSH ao oracle-vps confirmado. Servidor x86_64, Docker disponível, aproximadamente 956 MiB de RAM total e 7,2 GiB de disco livre no momento da inspeção. Precisamos avaliar consumo e armazenamento antes de escolher a plataforma; compatibilidade de implantação ainda não foi validada.

## Direção sugerida

Para uma biblioteca pessoal de dois cursos, considerar uma aplicação enxuta com catálogo, player e progresso. Se a intenção for oferecer cursos a alunos, avaliar primeiro LearnHouse ou Frappe Learning. A escolha depende do formato dos cursos e do público. Nenhuma base foi incorporada ao repositório.

## Pontos a definir

- Uso pessoal ou acesso de outros alunos?
- Cursos em pastas com MP4/PDF, links externos ou conteúdo a produzir?
- Localização e tamanho total dos arquivos.
- Domínio e estratégia de armazenamento.
