# 🛡️ Audit Lab - Monitoramento Proativo e Compliance

Este projeto foi desenvolvido como um **Case Prático** para o ecossistema de aprendizado do **NExT - CESAR School** e visa resolver uma das maiores dores do setor de auditoria financeira: a lentidão na detecção de fraudes.

Em vez de depender de relatórios estáticos em planilhas que mostram erros semanas depois do ocorrido, o Audit Lab implementa uma **Arquitetura Orientada a Eventos (Event-Driven)** para capturar, analisar e alertar sobre divergências no milissegundo em que elas ocorrem.

## 🚀 Arquitetura e Tecnologias Utilizadas

O sistema foi construído integrando quatro pilares fundamentais:

* **Banco de Dados (Supabase / PostgreSQL):** Armazenamento seguro dos alertas com **RLS (Row Level Security)**, garantindo que registros críticos não possam ser alterados ou apagados indevidamente.
* **Mensageria e Automação (n8n + Evolution API):** Escuta ativa do banco de dados (Webhooks). Ao detectar uma fraude classificada como "🔴 Crítica", o sistema dispara um alerta instantâneo formatado para o WhatsApp do gestor.
* **Machine Learning Preditivo (Prophet):** O algoritmo analisa a série histórica de perdas financeiras e projeta o risco de volume financeiro em divergência para os próximos 7 dias.
* **Front-End Analítico (Streamlit + Pandas):** Painel web hospedado em nuvem (Oracle Cloud), consumindo dados reais e processando métricas corporativas.

## ⚙️ Como o Fluxo Funciona na Prática

1. Uma divergência financeira (ex: Desvio de Orçamento, Saque não identificado) é registrada no Supabase.
2. O Supabase dispara um Webhook contendo o payload do dado.
3. O **n8n** intercepta o evento, avalia a criticidade e aciona a **Evolution API**.
4. O Auditor recebe um WhatsApp no mesmo instante com os detalhes (Unidade, Valor e Motivo) e um link de acesso rápido.
5. Ao acessar o painel (**Streamlit**), a IA já recalculou a tendência de risco da semana.

---
*Desenvolvido por Arlen Vasconcelos pela Techguia Digital.*
