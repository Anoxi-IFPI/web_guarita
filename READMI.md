# Documentação do Banco de Dados - Sistema de Controle de Chaves

Este documento descreve a estrutura das tabelas do banco de dados do sistema de controle de chaves e acessos via leitor de código de barras, desenvolvido para o IFPI Campus Teresina Zona Sul.

O sistema utiliza PostgreSQL e a arquitetura reflete uma lógica rigorosa de rastreamento: a união entre um **Usuário** e uma **Chave** gera um **Empréstimo** (1 Empréstimo = 1 Chave).

---

## 1. Tabela `Usuario`
Responsável por armazenar o cadastro das pessoas autorizadas a retirar chaves no campus.

| Coluna | Tipo de Dado | Descrição | Regras |
| :--- | :--- | :--- | :--- |
| `id` | `BigInt` | Identificador único do usuário. | Primary Key, Auto-incremento |
| `nome` | `Varchar(100)` | Nome completo da pessoa. | Not Null |
| `matricula` | `Varchar(20)` | Registro institucional (SUAP). | Not Null, Unique (Único) |
| `vinculo` | `Varchar(20)` | Categoria institucional. | Choices: Aluno, Professor, Servidor, Terceirizado |
| `email` | `Varchar` | E-mail de contato. | Not Null |
| `telefone` | `Varchar(15)` | Telefone ou celular. | Not Null |

---

## 2. Tabela `Chave`
Representa o objeto físico monitorado pelo sistema através de etiquetas de código de barras.

| Coluna | Tipo de Dado | Descrição | Regras |
| :--- | :--- | :--- | :--- |
| `id` | `BigInt` | Identificador (usado para gerar o código de barras). | Primary Key, Auto-incremento |
| `nome` | `Varchar(50)` | Etiqueta da chave (Ex: Chave 01).| Not Null |
| `setor` | `Varchar(100)` | Sala ou laboratório de destino.| Not Null |
| `disponivel` | `Boolean` | Controle lógico de disponibilidade.| Padrão: True |

---

## 3. Tabela `Emprestimo`
Tabela transacional que surge do relacionamento direto entre um Usuário e uma Chave, registrando o momento exato em que a posse é transferida.

| Coluna | Tipo de Dado | Descrição | Regras |
| :--- | :--- | :--- | :--- |
| `id` | `BigInt` | Identificador único da transação. | Primary Key, Auto-incremento |
| `usuario_id` | `BigInt` | Quem retirou a chave. | Foreign Key -> `Usuario(id)` |
| `chave_id` | `BigInt` | Qual chave (código de barras) foi lida. | Foreign Key -> `Chave(id)` |
| `data` | `Timestamp` | Data e hora exata da transação. | Preenchimento Automático |
| `status` | `Varchar(10)` | Situação atual do rastreamento. | Choices: NOVO, SOLICITADO, DEVOLVIDO, REPASSADO |

### Notas de Arquitetura:
* A entidade `Emprestimo` surge obrigatoriamente do relacionamento entre `Usuario` e `Chave` (One-to-Many logic aplicada como ForeignKey). Isso garante que cada "bip" no leitor de código de barras gere um log individual e imutável de data e hora para fins de auditoria de segurança e controle de devolução.