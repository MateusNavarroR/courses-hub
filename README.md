# Courses Hub

Biblioteca pessoal de cursos com catálogo inspirado na Udemy. V1 local, com backend Python sem dependências externas e frontend HTML/CSS/JavaScript.

## Executar

Requer Python 3.11 ou superior.

```bash
python3 server.py
```

Abra http://localhost:8765. Outra porta: `python3 server.py --port 8766`.

## Recursos

- Catálogo com busca e filtros por progresso.
- Player com módulos e aulas ordenados numericamente, reprodução com HTTP Range e retomada da posição.
- Marcação de conclusão e persistência em SQLite.
- Materiais Python e TXT com leitura na interface e download; PDFs e notebooks disponíveis como arquivos.
- Adicionar curso por caminho de pasta local, sem duplicação dos arquivos.
- Selecionar e enviar pasta pelo navegador, com envio em blocos e progresso.
- Layout responsivo em português.

O banco, o progresso e os arquivos enviados ficam em `.data/`, ignorado pelo Git. Cursos adicionados por caminho dependem da permanência dos arquivos na pasta original. O caminho corresponde ao computador que executa o servidor.

## Limites da v1

Servidor apenas em loopback, sem autenticação: para uso local. Antes de implantar em VPS, implementar autenticação, limites de armazenamento, controles de upload e servidor adequado a produção. Uploads interrompidos podem deixar arquivos parciais em `.data/uploads/`; retomar uploads entre sessões, remoção e edição de cursos ainda não estão implementados. Não há importação ZIP/RAR, transcodificação, capas personalizadas ou execução de código. Compatibilidade de vídeo depende dos codecs do navegador. Não modifique o banco com o servidor em uso.

## Verificação

```bash
python3 -m unittest discover -s tests -v
```

Testes de importação por upload, ordenação, materiais, persistência de progresso, reprodução parcial e rejeição de caminhos indevidos.

## Referências

- [LearnHouse](https://github.com/learnhouse/learnhouse): catálogo, estrutura de capítulos e atividades; [migração de conteúdo](https://docs.learnhouse.app/developers/migration).
- [Frappe Learning](https://github.com/frappe/lms): organização de cursos e progresso.
- [CourseLit](https://github.com/codelitdev/courselit): administração de cursos.

Implementação própria; nenhum código desses projetos foi incorporado. Repositório inicialmente privado. Implantação futura planejada no oracle-vps, após definir armazenamento para os vídeos.
