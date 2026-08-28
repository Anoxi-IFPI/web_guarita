# Documentação do Banco de Dados - Sistema de Controle de Chaves

Este documento descreve a estrutura das tabelas do banco de dados do sistema de controle de chaves e acessos via RFID, desenvolvido para o IFPI Campus Teresina Zona Sul.

O sistema utiliza PostgreSQL e a arquitetura reflete uma lógica rigorosa de rastreamento: **1 Empréstimo = 1 Chave**.

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
Representa o objeto físico (chave ou tag RFID) que será monitorado pelo sistema.

| Coluna | Tipo de Dado | Descrição | Regras |
| :--- | :--- | :--- | :--- |
| `id` | `BigInt` | Identificador da tag no banco. | Primary Key, Auto-incremento |
| `nome` | `Varchar(50)` | Etiqueta da chave (Ex: Chave 01).| Not Null |
| `setor` | `Varchar(100)` | Sala ou laboratório de destino.| Not Null |
| `disponivel` | `Boolean` | Controle lógico de disponibilidade.| Padrão: True |

---

## 3. Tabela `Emprestimo`
Tabela transacional que conecta um Usuário a uma Chave específica, registrando o momento exato do vínculo.

| Coluna | Tipo de Dado | Descrição | Regras |
| :--- | :--- | :--- | :--- |
| `id` | `BigInt` | Identificador único da transação. | Primary Key, Auto-incremento |
| `usuario_id` | `BigInt` | Quem retirou a chave. | Foreign Key -> `Usuario(id)` |
| `chave_id` | `BigInt` | Qual chave foi retirada. | Foreign Key -> `Chave(id)` |
| `data` | `Timestamp` | Data e hora exata da transação. | Preenchimento Automático |
| `status` | `Varchar(10)` | Situação atual do rastreamento. | Choices: NOVO, SOLICITADO, DEVOLVIDO, REPASSADO |

### Notas de Arquitetura:
* O relacionamento entre `Emprestimo` e `Chave` ocorre de forma direta (One-to-Many logic aplicada como ForeignKey) para garantir que cada leitura no sensor RFID gere um log independente de data e hora para fins de auditoria de segurança.